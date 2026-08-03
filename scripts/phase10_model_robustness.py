"""
Phase 10: Does the Phase 9 embedding result survive a different encoder?

WHY THIS EXISTS
---------------
Phase 9's conclusions rest on ONE embedding model (nomic-embed-text, 137M, monolingual-English
BERT lineage). PAPER.md v1.2 s8 lists "model-family robustness (a second encoder) has not been
run" as an open threat. This closes it with bge-m3 (BAAI, XLM-RoBERTa lineage, multilingual
pretraining, 1024-d) -- architecturally and training-distributionally distinct from nomic. The
multilingual axis is itself informative: if multilingual pretraining transfers better to Latin
transliteration of Sumerian, bge-m3 should IMPROVE on nomic; if the signal is generic subword
geometry, they should tie.

WHAT COUNTS AS REPLICATION (fixed before the run)
-------------------------------------------------
Phase 9's citable conclusions, each tested with the new encoder on the same tablets:
  R1  emb_valley beats lex_valley paired, significant after BH  (the twin comparison)
  R2  emb_global beats random on the MARKERLESS Administrative stratum, BH p < 0.05
  R3  shuffled-embedding control collapses to chance (|Pk - random| < 0.015)
  R4  emb_global mean Pk <= emb_valley mean Pk  (global beats valleys with embeddings)
A conclusion REPLICATES only if its criterion holds verbatim with the new model. Partial or
directional-only agreement is reported as NOT replicated -- no goalpost moving.

Everything else (tablets, metrics, feasibility rule, sign test, BH, seeds) is identical to
Phase 9 by direct import.
"""
from __future__ import annotations

import sys

import json
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
DATA = ROOT / "data"
OUT = ROOT / "outputs"
sys.path.insert(0, str(ROOT / "scripts"))

from phase8_boundary_recovery import (  # noqa: E402
    sumerian_tablets, equal_cuts, closer_cuts, pk, windowdiff, f1, N_RANDOM,
)
from phase9_embedding_chunking import (  # noqa: E402
    emb_valley_cuts, lex_valley_cuts, emb_global_cuts, sign_test, bh, OLLAMA,
)

SEED = 20260803          # same seed as phase 9: identical random baselines per tablet order
MODEL2 = "bge-m3"
CACHE2 = DATA / "embeddings_ur3_bgem3.npz"
P9_JSON = OUT / "phase9_embedding_chunking.json"


def _embed(texts: list[str]) -> list[list[float]]:
    req = urllib.request.Request(
        f"{OLLAMA}/api/embed",
        data=json.dumps({"model": MODEL2, "input": texts}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())["embeddings"]


def embed_corpus2(by_genre) -> dict[int, np.ndarray]:
    all_lines, spans, order = [], [], []
    for tablets in by_genre.values():
        for t in tablets:
            spans.append((len(all_lines), len(all_lines) + t.n))
            all_lines.extend(t.lines)
            order.append(t)
    if CACHE2.exists():
        blob = np.load(CACHE2, allow_pickle=False)
        if int(blob["n_lines"]) == len(all_lines):
            E = blob["embeddings"]
            print(f"[phase10] cache hit: {E.shape[0]:,} lines")
            return {id(t): E[a:b] for t, (a, b) in zip(order, spans)}
    print(f"[phase10] embedding {len(all_lines):,} lines with {MODEL2} ...")
    vecs = []
    B = 64
    for i in range(0, len(all_lines), B):
        vecs.extend(_embed(all_lines[i:i + B]))
        if (i // B) % 100 == 0:
            print(f"[phase10]   {i:,}/{len(all_lines):,}")
    E = np.asarray(vecs, dtype=np.float32)
    E /= np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)
    np.savez_compressed(CACHE2, embeddings=E, n_lines=np.int64(len(all_lines)))
    print(f"[phase10] cached to {CACHE2}")
    return {id(t): E[a:b] for t, (a, b) in zip(order, spans)}


def main() -> None:
    rng = np.random.default_rng(SEED)
    by_genre, _ = sumerian_tablets()
    emb = embed_corpus2(by_genre)
    p9 = json.loads(P9_JSON.read_text(encoding="utf-8")) if P9_JSON.exists() else None
    results = {}

    for genre, tablets in by_genre.items():
        print(f"[phase10] {genre}: {len(tablets):,} tablets ...")
        methods = ["random", "closer", "lex_valley", "emb_valley", "emb_global", "shuffled_control"]
        acc = {m: {"pk": []} for m in methods}
        for t in tablets:
            ref = set(t.truth)
            E = emb[id(t)]
            hyps = {}
            hyps["closer"] = set(closer_cuts(t))
            hyps["lex_valley"], _ = lex_valley_cuts(t)
            hyps["emb_valley"], _ = emb_valley_cuts(t, E)
            hyps["emb_global"], _ = emb_global_cuts(t, E)
            perm = rng.permutation(E.shape[0])
            hyps["shuffled_control"], _ = emb_valley_cuts(t, E[perm])
            for m in ("closer", "lex_valley", "emb_valley", "emb_global", "shuffled_control"):
                acc[m]["pk"].append(pk(t.n, ref, hyps[m]))
            rnd = []
            for _ in range(N_RANDOM):
                h = set(rng.choice(t.n - 1, size=t.K - 1, replace=False).tolist())
                rnd.append(pk(t.n, ref, h))
            acc["random"]["pk"].append(float(np.mean(rnd)))

        summary = {m: round(float(np.mean(acc[m]["pk"])), 4) for m in methods}
        tests = {}
        pairs = [("emb_valley", "lex_valley"), ("emb_valley", "random"),
                 ("emb_global", "random"), ("shuffled_control", "random")]
        for a_, b_ in pairs:
            tests[f"{a_}_vs_{b_}"] = {
                "pk_sign_p": round(sign_test(acc[a_]["pk"], acc[b_]["pk"]), 5),
                "wins_pk": sum(1 for x, y in zip(acc[a_]["pk"], acc[b_]["pk"]) if x < y),
                "losses_pk": sum(1 for x, y in zip(acc[a_]["pk"], acc[b_]["pk"]) if x > y),
            }
        names = list(tests)
        for k, adj in zip(names, bh([tests[k]["pk_sign_p"] for k in names])):
            tests[k]["pk_sign_p_bh"] = round(adj, 5)

        idx_no = [i for i, t in enumerate(tablets) if not t.has_closer]
        strata = {}
        if len(idx_no) >= 30:
            sub_g = [acc["emb_global"]["pk"][i] for i in idx_no]
            sub_r = [acc["random"]["pk"][i] for i in idx_no]
            strata["without_closer_lines"] = {
                "n": len(idx_no),
                "random_pk": round(float(np.mean(sub_r)), 4),
                "emb_global_pk": round(float(np.mean(sub_g)), 4),
                "emb_global_vs_random": {
                    "pk_sign_p": round(sign_test(sub_g, sub_r), 5),
                    "wins_pk": sum(1 for x, y in zip(sub_g, sub_r) if x < y),
                    "losses_pk": sum(1 for x, y in zip(sub_g, sub_r) if x > y),
                },
            }
        results[genre] = {"n_tablets": len(tablets), "summary": summary,
                          "paired_tests": tests, "marker_strata": strata}
        print(f"    Pk  random={summary['random']:.3f} closer={summary['closer']:.3f} "
              f"lex={summary['lex_valley']:.3f} emb_v={summary['emb_valley']:.3f} "
              f"emb_g={summary['emb_global']:.3f} shuf={summary['shuffled_control']:.3f}")

    # ---- replication verdicts against the fixed criteria
    verdicts = {}
    adm = results.get("Administrative", {})
    if adm:
        s = adm["summary"]
        t_ = adm["paired_tests"]
        twin = t_["emb_valley_vs_lex_valley"]
        verdicts["R1_twin_direction_significant"] = bool(
            twin["wins_pk"] > twin["losses_pk"] and twin["pk_sign_p_bh"] < 0.05)
        no = adm["marker_strata"].get("without_closer_lines", {})
        eg = no.get("emb_global_vs_random", {})
        verdicts["R2_markerless_stratum_significant"] = bool(
            no and no["emb_global_pk"] < no["random_pk"] and eg.get("pk_sign_p", 1.0) < 0.05)
        verdicts["R3_shuffled_control_collapses"] = bool(
            abs(s["shuffled_control"] - s["random"]) < 0.015)
        verdicts["R4_global_beats_valley"] = bool(s["emb_global"] <= s["emb_valley"])
    n_rep = sum(verdicts.values())

    (OUT / "phase10_model_robustness.json").write_text(json.dumps({
        "config": {"seed": SEED, "model": MODEL2, "n_random": N_RANDOM,
                   "criteria_fixed_before_run": True},
        "results": results, "replication_verdicts": verdicts,
        "n_replicated": n_rep, "n_criteria": len(verdicts)},
        indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Phase 10 — Second-encoder robustness of the embedding result\n\n",
          f"Phase 9 used one encoder (nomic-embed-text, monolingual BERT lineage, 137M). This reruns "
          f"the decisive comparisons with **{MODEL2}** (BAAI, XLM-RoBERTa lineage, multilingual "
          "pretraining, 1024-d) — architecturally and training-distributionally distinct. Replication "
          "criteria were fixed in the script header before the run; partial agreement counts as NOT "
          "replicated.\n\n"]
    for genre, r in results.items():
        md.append(f"## {genre}\n\n{r['n_tablets']:,} tablets\n\n")
        md.append("| Method | Pk (bge-m3) | Pk (nomic, phase 9) |\n|---|---:|---:|\n")
        p9g = (p9 or {}).get("results", {}).get(genre, {}).get("summary", {})
        for m in ("random", "closer", "lex_valley", "emb_valley", "emb_global", "shuffled_control"):
            prev = p9g.get(m, {}).get("pk", "—")
            md.append(f"| {m} | {r['summary'][m]:.3f} | {prev} |\n")
        md.append("\n| Comparison | wins/losses | sign p | BH |\n|---|---:|---:|---:|\n")
        for name, tt in r["paired_tests"].items():
            md.append(f"| {name.replace('_',' ')} | {tt['wins_pk']}/{tt['losses_pk']} | "
                      f"{tt['pk_sign_p']} | {tt['pk_sign_p_bh']} |\n")
        no = r["marker_strata"].get("without_closer_lines")
        if no:
            eg = no["emb_global_vs_random"]
            md.append(f"\nMarkerless stratum ({no['n']:,}): emb_global {no['emb_global_pk']} vs random "
                      f"{no['random_pk']} ({eg['wins_pk']}/{eg['losses_pk']}, p = {eg['pk_sign_p']}).\n")
        md.append("\n")
    md.append("## Replication verdicts (criteria fixed before the run)\n\n")
    md.append("| Criterion | Replicated with bge-m3? |\n|---|:---:|\n")
    labels = {
        "R1_twin_direction_significant": "R1 — embeddings beat the lexical twin (paired, BH < 0.05)",
        "R2_markerless_stratum_significant": "R2 — emb_global beats random on the markerless Administrative stratum (p < 0.05)",
        "R3_shuffled_control_collapses": "R3 — shuffled-embedding control collapses to chance",
        "R4_global_beats_valley": "R4 — global objective ≤ valley objective (mean Pk)",
    }
    for k, label in labels.items():
        md.append(f"| {label} | {'**YES**' if verdicts.get(k) else '**NO**'} |\n")
    md.append(f"\n**{n_rep} of {len(verdicts)} criteria replicated.** Whichever way each verdict "
              "fell, it is reported under the pre-stated criterion; no criterion was adjusted after "
              "seeing the data.\n")
    (OUT / "phase10_model_robustness.md").write_text("".join(md), encoding="utf-8")
    print(f"[save] {OUT / 'phase10_model_robustness.md'}")
    print(f"[phase10] replicated {n_rep}/{len(verdicts)}")


if __name__ == "__main__":
    main()
