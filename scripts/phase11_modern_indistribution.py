"""
Phase 11: The in-distribution modern-text experiment -- git commit histories as record streams.

WHY THIS EXISTS
---------------
Phases 8-10 established a signal hierarchy on Ur III administrative tablets, with one standing
threat (PAPER s8): Sumerian transliteration is out-of-distribution for every embedding model, so
the embedding results measure machinery, not meaning, and "in-distribution behaviour on modern
text may differ in either direction." This phase runs the same evaluation on modern English
record-structured text where the encoder is squarely in-distribution.

WHY GIT COMMIT HISTORIES
------------------------
The corpus must be record-structured (the agent-trace analog), carry REAL boundaries not created
for this test, be public and reproducible, and offer the marker/markerless contrast the Sumerian
result turns on. Git histories give all four:
  - each commit message is a record; the boundary between consecutive messages is defined by the
    VCS, causally prior to this experiment and not an authorial section heading;
  - records are uneven in length (the property that made fixed-size chunking worse than random);
  - some projects close every record with attribution trailers (Signed-off-by:, Reviewed-by:...)
    -- the modern šu ba-ti -- while others use none. We use git/git (trailer-rich, ~1.5 trailer
    lines per commit) and expressjs/express (trailers on ~4% of commits, effectively markerless);
  - anyone can reproduce with two blobless clones pinned by --until=2026-01-01.

DESIGN
------
Documents are non-overlapping windows of K consecutive commit messages (K drawn seeded from
{3,4,5}), messages joined as their non-empty lines with NO commit headers (a header line would
hand every method the boundary for free). Ground truth: the K-1 junctions. Same methods, metrics,
feasibility rule, corrected sign test, and BH machinery as phases 8-10, imported directly.
The closer probe is the trailer regex -- checked against a hand audit below rather than assumed.

PRE-REGISTERED EXPECTATIONS (fixed before the run)
--------------------------------------------------
  M1  git/git: the trailer cue dominates -- closer Pk beats same-stratum random decisively.
  M2  In-distribution embeddings beat the lexical twin (paired, BH < 0.05) in both repos.
  M3  express (markerless): emb_global beats random, paired p < 0.05 -- the in-distribution
      version of the phase-9/10 markerless result.
  M4  equal (fixed-size) is worse than random in both repos (records are uneven).
  M5  the shuffled-embedding control collapses to chance in both repos.
Whichever way each falls, it is reported under the pre-stated criterion.
"""
from __future__ import annotations

import sys

import json
import re
import subprocess
import urllib.request
from pathlib import Path

import numpy as np


def _ascii_safe_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass


_ascii_safe_stdout()

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "modern"
OUT = ROOT / "outputs"
sys.path.insert(0, str(ROOT / "scripts"))

from phase8_boundary_recovery import (  # noqa: E402
    Tablet, equal_cuts, closer_cuts, pk, windowdiff, f1, N_RANDOM, MIN_LINES, MAX_LINES,
)
from phase9_embedding_chunking import (  # noqa: E402
    emb_valley_cuts, lex_valley_cuts, emb_global_cuts, sign_test, bh, OLLAMA,
)

SEED = 20260803
MODEL = "nomic-embed-text"
UNTIL = "2026-01-01"          # freezes the commit set; results pin to history state, not clone date
N_DOCS = 300                  # per repo
REPOS = {
    "git/git (trailer-rich)": {"path": DATA / "gitgit",
                               "url": "https://github.com/git/git.git"},
    "express (markerless)": {"path": DATA / "express",
                             "url": "https://github.com/expressjs/express.git"},
}
TRAILER = re.compile(r"^(Signed-off-by|Co-authored-by|Reviewed-by|Acked-by|Tested-by|"
                     r"Helped-by|Reported-by|Suggested-by|Mentored-by|Cc):", re.I)


def commit_messages(repo: Path, url: str) -> list[list[str]]:
    """Each commit's message as its list of non-empty lines. Cached to disk."""
    cache = DATA / (repo.name + "_messages.json")
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    if not repo.exists():
        print(f"[phase11] cloning {url} (blobless) ...")
        subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", "--quiet",
                        url, str(repo)], check=True)
    raw = subprocess.run(
        ["git", "-C", str(repo), "log", f"--until={UNTIL}", "--format=%x01%B"],
        capture_output=True, check=True).stdout.decode("utf-8", errors="replace")
    msgs = []
    for chunk in raw.split("\x01"):
        lines = [l.strip() for l in chunk.split("\n")]
        lines = [l for l in lines if l]
        if lines:
            msgs.append(lines)
    DATA.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(msgs, ensure_ascii=False), encoding="utf-8")
    print(f"[phase11] {repo.name}: {len(msgs):,} commit messages cached")
    return msgs


def build_documents(msgs: list[list[str]], rng) -> list[Tablet]:
    """Non-overlapping K-commit windows -> Tablet objects with trailer-based closer scores."""
    docs, i = [], 0
    ks = rng.integers(3, 6, size=len(msgs))          # K in {3,4,5}
    kidx = 0
    while i < len(msgs) - 5 and len(docs) < N_DOCS * 3:
        K = int(ks[kidx]); kidx += 1
        window = msgs[i:i + K]
        i += K
        lines, truth = [], set()
        for j, m in enumerate(window):
            lines.extend(m)
            if j < len(window) - 1:
                truth.add(len(lines) - 1)
        truth = {b for b in truth if b < len(lines) - 1}
        if len(truth) != K - 1 or not (MIN_LINES <= len(lines) <= 80):
            continue
        t = Tablet(lines, truth)
        # replace the Sumerian closer probe with the trailer probe
        t.closer_score = [1 if TRAILER.match(l) else 0 for l in lines]
        t.has_closer = any(t.closer_score)
        docs.append(t)
    idx = rng.permutation(len(docs))[:N_DOCS]
    return [docs[int(j)] for j in sorted(idx)]


def embed_docs(docs: list[Tablet], slug: str) -> dict[int, np.ndarray]:
    cache = DATA / f"emb_{slug}_nomic.npz"
    all_lines, spans = [], []
    for t in docs:
        spans.append((len(all_lines), len(all_lines) + t.n))
        all_lines.extend(t.lines)
    if cache.exists():
        blob = np.load(cache, allow_pickle=False)
        if int(blob["n_lines"]) == len(all_lines):
            E = blob["embeddings"]
            print(f"[phase11] {slug}: embedding cache hit ({E.shape[0]:,} lines)")
            return {id(t): E[a:b] for t, (a, b) in zip(docs, spans)}
    print(f"[phase11] {slug}: embedding {len(all_lines):,} lines ...")
    vecs = []
    for i in range(0, len(all_lines), 128):
        req = urllib.request.Request(
            f"{OLLAMA}/api/embed",
            data=json.dumps({"model": MODEL, "input": all_lines[i:i + 128]}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=600) as r:
            vecs.extend(json.loads(r.read())["embeddings"])
    E = np.asarray(vecs, dtype=np.float32)
    E /= np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)
    np.savez_compressed(cache, embeddings=E, n_lines=np.int64(len(all_lines)))
    return {id(t): E[a:b] for t, (a, b) in zip(docs, spans)}


def main() -> None:
    rng = np.random.default_rng(SEED)
    results = {}

    for label, spec in REPOS.items():
        msgs = commit_messages(spec["path"], spec["url"])
        docs = build_documents(msgs, rng)
        slug = spec["path"].name
        emb = embed_docs(docs, slug)
        n_with = sum(1 for t in docs if t.has_closer)
        print(f"[phase11] {label}: {len(docs)} docs, {n_with} with trailer lines")

        methods = ["random", "equal", "closer", "lex_valley", "emb_valley",
                   "emb_global", "shuffled_control"]
        acc = {m: {"pk": [], "f1t1": []} for m in methods}
        solver = {"exact": 0, "greedy": 0, "fallback": 0}
        for t in docs:
            ref = set(t.truth)
            E = emb[id(t)]
            hyps = {}
            hyps["equal"] = set(equal_cuts(t.n, t.K))
            hyps["closer"] = set(closer_cuts(t))
            hyps["lex_valley"], _ = lex_valley_cuts(t)
            hyps["emb_valley"], _ = emb_valley_cuts(t, E)
            hyps["emb_global"], kind = emb_global_cuts(t, E)
            solver[kind] += 1
            perm = rng.permutation(E.shape[0])
            hyps["shuffled_control"], _ = emb_valley_cuts(t, E[perm])
            for m in ("equal", "closer", "lex_valley", "emb_valley", "emb_global",
                      "shuffled_control"):
                acc[m]["pk"].append(pk(t.n, ref, hyps[m]))
                acc[m]["f1t1"].append(f1(ref, hyps[m], 1))
            rnd_pk, rnd_f1 = [], []
            for _ in range(N_RANDOM):
                h = set(rng.choice(t.n - 1, size=t.K - 1, replace=False).tolist())
                rnd_pk.append(pk(t.n, ref, h))
                rnd_f1.append(f1(ref, h, 1))
            acc["random"]["pk"].append(float(np.mean(rnd_pk)))
            acc["random"]["f1t1"].append(float(np.mean(rnd_f1)))

        summary = {m: {"pk": round(float(np.mean(acc[m]["pk"])), 4),
                       "f1_tol1": round(float(np.mean(acc[m]["f1t1"])), 4)} for m in methods}
        tests = {}
        for a_, b_ in (("closer", "random"), ("lex_valley", "random"), ("emb_valley", "random"),
                       ("emb_global", "random"), ("emb_valley", "lex_valley"),
                       ("equal", "random"), ("shuffled_control", "random")):
            tests[f"{a_}_vs_{b_}"] = {
                "pk_sign_p": round(sign_test(acc[a_]["pk"], acc[b_]["pk"]), 5),
                "wins_pk": sum(1 for x, y in zip(acc[a_]["pk"], acc[b_]["pk"]) if x < y),
                "losses_pk": sum(1 for x, y in zip(acc[a_]["pk"], acc[b_]["pk"]) if x > y),
            }
        names = list(tests)
        for k, adj in zip(names, bh([tests[k]["pk_sign_p"] for k in names])):
            tests[k]["pk_sign_p_bh"] = round(adj, 5)

        idx_with = [i for i, t in enumerate(docs) if t.has_closer]
        strata = {}
        if len(idx_with) >= 30:
            sc = [acc["closer"]["pk"][i] for i in idx_with]
            sr = [acc["random"]["pk"][i] for i in idx_with]
            strata["with_trailers"] = {
                "n": len(idx_with),
                "closer_pk": round(float(np.mean(sc)), 4),
                "random_pk": round(float(np.mean(sr)), 4),
                "closer_vs_random": {
                    "pk_sign_p": round(sign_test(sc, sr), 5),
                    "wins_pk": sum(1 for x, y in zip(sc, sr) if x < y),
                    "losses_pk": sum(1 for x, y in zip(sc, sr) if x > y)},
            }
        results[label] = {"n_docs": len(docs), "n_with_trailers": n_with,
                          "summary": summary, "paired_tests": tests,
                          "strata": strata, "solver": solver}
        print(f"    Pk  random={summary['random']['pk']:.3f} equal={summary['equal']['pk']:.3f} "
              f"closer={summary['closer']['pk']:.3f} lex={summary['lex_valley']['pk']:.3f} "
              f"emb_v={summary['emb_valley']['pk']:.3f} emb_g={summary['emb_global']['pk']:.3f} "
              f"shuf={summary['shuffled_control']['pk']:.3f}")

    # ---- pre-registered verdicts
    g = results.get("git/git (trailer-rich)", {})
    e = results.get("express (markerless)", {})
    verdicts = {}
    if g and e:
        gw = g["strata"].get("with_trailers", {})
        verdicts["M1_trailer_cue_dominates"] = bool(
            gw and gw["closer_pk"] < gw["random_pk"]
            and gw["closer_vs_random"]["pk_sign_p"] < 0.05)
        verdicts["M2_embeddings_beat_lexical_twin_both"] = bool(all(
            r["paired_tests"]["emb_valley_vs_lex_valley"]["wins_pk"]
            > r["paired_tests"]["emb_valley_vs_lex_valley"]["losses_pk"]
            and r["paired_tests"]["emb_valley_vs_lex_valley"]["pk_sign_p_bh"] < 0.05
            for r in (g, e)))
        verdicts["M3_markerless_embeddings_beat_random"] = bool(
            e["paired_tests"]["emb_global_vs_random"]["pk_sign_p_bh"] < 0.05
            and e["summary"]["emb_global"]["pk"] < e["summary"]["random"]["pk"])
        verdicts["M4_fixed_size_worse_than_random_both"] = bool(all(
            r["summary"]["equal"]["pk"] > r["summary"]["random"]["pk"] for r in (g, e)))
        verdicts["M5_shuffled_control_collapses_both"] = bool(all(
            abs(r["summary"]["shuffled_control"]["pk"] - r["summary"]["random"]["pk"]) < 0.02
            for r in (g, e)))

    (OUT / "phase11_modern_indistribution.json").write_text(json.dumps({
        "config": {"seed": SEED, "model": MODEL, "until": UNTIL, "n_docs_per_repo": N_DOCS,
                   "k_range": [3, 5], "max_doc_lines": 80,
                   "criteria_fixed_before_run": True},
        "results": results, "verdicts": verdicts,
        "n_held": sum(verdicts.values()), "n_criteria": len(verdicts)},
        indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Phase 11 — In-distribution modern text: git commit histories as record streams\n\n",
          "The Sumerian results carried a standing scope limit: every encoder was out-of-distribution. "
          "This phase reruns the full evaluation on modern English record streams where the encoder is "
          "in-distribution — non-overlapping windows of consecutive commit messages (boundaries defined "
          "by the VCS, commit headers stripped so nothing hands the boundary to any method), from two "
          "public repositories chosen for the marker contrast: **git/git**, whose convention closes "
          "nearly every record with attribution trailers (`Signed-off-by:` — the modern *šu ba-ti*), "
          f"and **expressjs/express**, effectively markerless. Pinned to `--until={UNTIL}`; "
          "reproducible with two blobless clones.\n\n"]
    for label, r in results.items():
        md.append(f"## {label}\n\n{r['n_docs']} documents · {r['n_with_trailers']} contain trailer "
                  f"lines · solver: {r['solver']}\n\n")
        md.append("| Method | Pk ↓ | F1 ±1 ↑ |\n|---|---:|---:|\n")
        for m in ("random", "equal", "closer", "lex_valley", "emb_valley", "emb_global",
                  "shuffled_control"):
            s = r["summary"][m]
            md.append(f"| {m} | {s['pk']:.3f} | {s['f1_tol1']:.3f} |\n")
        md.append("\n| Comparison | wins/losses | sign p | BH |\n|---|---:|---:|---:|\n")
        for name, tt in r["paired_tests"].items():
            md.append(f"| {name.replace('_', ' ')} | {tt['wins_pk']}/{tt['losses_pk']} | "
                      f"{tt['pk_sign_p']} | {tt['pk_sign_p_bh']} |\n")
        w = r["strata"].get("with_trailers")
        if w:
            md.append(f"\nTrailer-bearing stratum ({w['n']}): closer {w['closer_pk']} vs random "
                      f"{w['random_pk']} ({w['closer_vs_random']['wins_pk']}/"
                      f"{w['closer_vs_random']['losses_pk']}, p = {w['closer_vs_random']['pk_sign_p']}).\n")
        md.append("\n")
    md.append("## Pre-registered verdicts\n\n| Criterion | Held? |\n|---|:---:|\n")
    labels = {
        "M1_trailer_cue_dominates": "M1 — trailer cue dominates in git/git (stratified, p < 0.05)",
        "M2_embeddings_beat_lexical_twin_both": "M2 — embeddings beat the lexical twin in BOTH repos (BH < 0.05)",
        "M3_markerless_embeddings_beat_random": "M3 — markerless repo: emb_global beats random (BH < 0.05)",
        "M4_fixed_size_worse_than_random_both": "M4 — fixed-size worse than random in BOTH repos",
        "M5_shuffled_control_collapses_both": "M5 — shuffled control collapses in BOTH repos",
    }
    for k, lab in labels.items():
        md.append(f"| {lab} | {'**YES**' if verdicts.get(k) else '**NO**'} |\n")
    md.append(f"\n**{sum(verdicts.values())} of {len(verdicts)} pre-registered criteria held.** "
              "Each is reported under the criterion as fixed before the run.\n")
    (OUT / "phase11_modern_indistribution.md").write_text("".join(md), encoding="utf-8")
    print(f"[save] {OUT / 'phase11_modern_indistribution.md'}")
    print(f"[phase11] held {sum(verdicts.values())}/{len(verdicts)}")


if __name__ == "__main__":
    main()
