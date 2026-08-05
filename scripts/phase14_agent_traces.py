"""
Phase 14: Real agent traces -- the corpus this whole project has been an analogy for.

WHY THIS EXISTS
---------------
Sections 6-7 of PAPER.md argue from tablets and commit streams to agent memory. This phase closes
the loop on the actual object: tool-call traces from real agent sessions (Claude Code transcript
JSONL). Ground truth: the boundary between consecutive tool interactions, defined by the
transcript structure, causally prior to this test. PAPER s8 flagged commit windows as
"same-project, same-era, gentler than a real agent trace"; these are the real traces.

BRING YOUR OWN DATA
-------------------
Transcripts are private. This script therefore ships as a BYO-data experiment: point it at your
own transcript directory (default: ~/.claude/projects). The repository publishes only AGGREGATE
metrics from the author's local sessions; no transcript content is written to any output file,
and the script asserts that before saving. Embeddings are computed by a LOCAL model (Ollama),
so trace text never leaves the machine.

RECORDS AND RENDERING
---------------------
A record = one tool interaction: the tool_use call (name + input rendered as text lines) followed
by its tool_result content (text lines, truncated per record). Documents = windows of K
consecutive interactions from one session (K in {3,4,5}, seeded), rendered WITHOUT any structural
wrapper, so nothing hands a method the boundary. Two conditions:

  raw         -- traces as they are. Modern agent traces carry no closing formula; this is the
                 markerless condition, for real this time.
  engineered  -- identical documents plus one delimiter line appended to every record
                 ("=== end-of-tool-result ==="). The s7 advice, applied. The closer method's
                 success here is BY CONSTRUCTION and is labelled a demonstration, not a finding;
                 the informative quantity is the size of the gap it opens over every post-hoc
                 method on the same documents.

PRE-REGISTERED EXPECTATIONS
---------------------------
  T1  raw condition: at least one embedding method beats random (paired, BH < 0.05). Genuinely
      uncertain -- tool outputs are heterogeneous (code, logs, prose) and adjacent interactions
      often share vocabulary heavily.
  T2  engineered condition: the delimiter closes the problem (closer Pk < 0.1) -- a demonstration
      by construction, pre-labelled as such.
  T3  the equal-vs-random sign matches the phase 13 dispersion curve's prediction for the
      measured record-length CV of the traces (predicted: CV > ~1 -> equal worse than random;
      CV < ~0.8 -> equal better; in between, no prediction).
Whichever way each falls, it is reported as fixed.
"""
from __future__ import annotations

import sys

import argparse
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
    Tablet, equal_cuts, closer_cuts, pk, f1, N_RANDOM,
)
from phase9_embedding_chunking import (  # noqa: E402
    emb_valley_cuts, lex_valley_cuts, emb_global_cuts, sign_test, bh, OLLAMA,
)
from phase12_unknown_k import marker_cuts_unknown_k  # noqa: E402

SEED = 20260805
MODEL = "nomic-embed-text"
DELIM = "=== end-of-tool-result ==="
MAX_DOCS = 200
MAX_LINES_PER_RECORD = 12
MIN_DOC_LINES, MAX_DOC_LINES = 8, 80
import re  # noqa: E402
DELIM_RE = re.compile(re.escape(DELIM))


# ------------------------------------------------------------- trace parsing

def tool_interactions(session_file: Path) -> list[list[str]]:
    """Each tool interaction rendered as text lines: tool name/input, then result content."""
    records: list[list[str]] = []
    pending: dict[str, list[str]] = {}
    try:
        lines = session_file.read_text(encoding="utf-8", errors="replace").split("\n")
    except OSError:
        return []
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            ev = json.loads(raw)
        except json.JSONDecodeError:
            continue
        msg = ev.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                head = [str(block.get("name", "tool"))]
                inp = block.get("input") or {}
                if isinstance(inp, dict):
                    for k, v in list(inp.items())[:4]:
                        for ln in str(v).split("\n")[:3]:
                            ln = ln.strip()
                            if ln:
                                head.append(f"{k}: {ln}"[:200])
                pending[str(block.get("id"))] = head
            elif block.get("type") == "tool_result":
                head = pending.pop(str(block.get("tool_use_id")), ["tool"])
                body = block.get("content")
                text = ""
                if isinstance(body, str):
                    text = body
                elif isinstance(body, list):
                    text = "\n".join(str(b.get("text", "")) for b in body if isinstance(b, dict))
                rec = list(head)
                for ln in text.split("\n"):
                    ln = ln.strip()
                    if ln:
                        rec.append(ln[:200])
                    if len(rec) >= MAX_LINES_PER_RECORD:
                        break
                if len(rec) >= 2:
                    records.append(rec)
    return records


def build_trace_documents(transcripts_dir: Path, rng) -> list[Tablet]:
    """FROZEN CORPUS: the transcript directory is LIVE -- the author's sessions grow while the
    experiment is being developed (including the session developing this very script), so two
    runs hours apart see different corpora and produce different numbers despite a fixed seed.
    Caught when a rerun shifted CV 0.667 -> 0.726. The parsed documents are therefore frozen to
    a local cache on first run; delete data/traces_frozen.json to re-snapshot. The cache stays
    on-machine (gitignored) -- freezing changes reproducibility-in-time, not privacy."""
    frozen = DATA / "traces_frozen.json"
    if frozen.exists():
        payload = json.loads(frozen.read_text(encoding="utf-8"))
        return [Tablet(d["lines"], set(d["truth"])) for d in payload]

    files = sorted(transcripts_dir.rglob("*.jsonl"))
    rng.shuffle(files)
    docs: list[Tablet] = []
    for f in files:
        if len(docs) >= MAX_DOCS:
            break
        recs = tool_interactions(f)
        i = 0
        while i + 3 <= len(recs) and len(docs) < MAX_DOCS:
            K = int(rng.integers(3, 6))
            window = recs[i:i + K]
            i += K
            if len(window) < 3:
                break
            lines, truth = [], set()
            for j, r in enumerate(window):
                lines.extend(r)
                if j < len(window) - 1:
                    truth.add(len(lines) - 1)
            truth = {b for b in truth if b < len(lines) - 1}
            if len(truth) != len(window) - 1 or not (MIN_DOC_LINES <= len(lines) <= MAX_DOC_LINES):
                continue
            docs.append(Tablet(lines, truth))
    frozen.write_text(json.dumps([{"lines": t.lines, "truth": sorted(t.truth)} for t in docs],
                                 ensure_ascii=False), encoding="utf-8")
    return docs


def engineer(docs: list[Tablet]) -> list[Tablet]:
    """Same documents with one delimiter line appended to every record."""
    out = []
    for t in docs:
        edges = [-1, *sorted(t.truth), t.n - 1]
        lines, truth = [], set()
        for k in range(len(edges) - 1):
            seg = t.lines[edges[k] + 1: edges[k + 1] + 1]
            lines.extend(seg)
            lines.append(DELIM)
            if k < len(edges) - 2:
                truth.add(len(lines) - 1)
        t2 = Tablet(lines, truth)
        t2.closer_score = [1 if DELIM_RE.fullmatch(l) else 0 for l in lines]
        t2.has_closer = True
        out.append(t2)
    return out


# ------------------------------------------------------------- embeddings

def embed(docs: list[Tablet], cache: Path) -> dict[int, np.ndarray]:
    all_lines, spans = [], []
    for t in docs:
        spans.append((len(all_lines), len(all_lines) + t.n))
        all_lines.extend(t.lines)
    if cache.exists():
        blob = np.load(cache, allow_pickle=False)
        if int(blob["n_lines"]) == len(all_lines):
            E = blob["embeddings"]
            return {id(t): E[a:b] for t, (a, b) in zip(docs, spans)}
    print(f"[phase14] embedding {len(all_lines):,} lines locally ({MODEL}) ...")
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


# ------------------------------------------------------------- evaluation

def evaluate(docs, emb, rng, with_closer: bool) -> dict:
    methods = ["random", "equal", "lex_valley", "emb_valley", "emb_global"]
    if with_closer:
        methods += ["closer", "marker_K_unknownK"]
    acc = {m: {"pk": [], "f1t1": []} for m in methods}
    for t in docs:
        ref = set(t.truth)
        E = emb[id(t)]
        hyps = {
            "equal": set(equal_cuts(t.n, t.K)),
            "lex_valley": lex_valley_cuts(t)[0],
            "emb_valley": emb_valley_cuts(t, E)[0],
            "emb_global": emb_global_cuts(t, E)[0],
        }
        if with_closer:
            hyps["closer"] = set(closer_cuts(t))
            hyps["marker_K_unknownK"] = marker_cuts_unknown_k(t)
        for m, h in hyps.items():
            acc[m]["pk"].append(pk(t.n, ref, h))
            acc[m]["f1t1"].append(f1(ref, h, 1))
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
    for m in [x for x in methods if x != "random"]:
        tests[f"{m}_vs_random"] = {
            "pk_sign_p": round(sign_test(acc[m]["pk"], acc["random"]["pk"]), 5),
            "wins_pk": sum(1 for x, y in zip(acc[m]["pk"], acc["random"]["pk"]) if x < y),
            "losses_pk": sum(1 for x, y in zip(acc[m]["pk"], acc["random"]["pk"]) if x > y),
        }
    names = list(tests)
    for k, adj in zip(names, bh([tests[k]["pk_sign_p"] for k in names])):
        tests[k]["pk_sign_p_bh"] = round(adj, 5)
    return {"summary": summary, "paired_tests": tests}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcripts-dir", default=str(Path.home() / ".claude" / "projects"))
    args = ap.parse_args()
    tdir = Path(args.transcripts_dir)
    rng = np.random.default_rng(SEED)

    docs = build_trace_documents(tdir, rng)
    if len(docs) < 50:
        print(f"[phase14] only {len(docs)} documents from {tdir}; need >= 50. "
              "Point --transcripts-dir at a directory of Claude Code session JSONL files.")
        sys.exit(2)
    print(f"[phase14] {len(docs)} raw-trace documents from local sessions")

    rec_lens = []
    for t in docs:
        edges = [-1, *sorted(t.truth), t.n - 1]
        rec_lens.extend(t.cum[edges[k + 1] + 1] - t.cum[edges[k] + 1] for k in range(len(edges) - 1))
    cv = float(np.std(rec_lens) / np.mean(rec_lens))

    emb_raw = embed(docs, DATA / "traces_raw_emb.npz")
    raw = evaluate(docs, emb_raw, rng, with_closer=False)
    eng_docs = engineer(docs)
    emb_eng = embed(eng_docs, DATA / "traces_eng_emb.npz")
    eng = evaluate(eng_docs, emb_eng, rng, with_closer=True)

    # T3 prediction from the phase 13 curve
    if cv > 1.0:
        predicted = "equal_worse"
    elif cv < 0.8:
        predicted = "equal_better"
    else:
        predicted = "no_prediction"
    actual = "equal_worse" if raw["summary"]["equal"]["pk"] > raw["summary"]["random"]["pk"] else "equal_better"

    t1 = any(raw["paired_tests"][f"{m}_vs_random"]["pk_sign_p_bh"] < 0.05
             and raw["summary"][m]["pk"] < raw["summary"]["random"]["pk"]
             for m in ("emb_valley", "emb_global"))
    t2 = eng["summary"]["closer"]["pk"] < 0.1
    verdicts = {
        "T1_embeddings_beat_random_on_raw_traces": bool(t1),
        "T2_engineered_delimiter_closes_problem": bool(t2),
        # T3 is VOID, not held/failed: Phase 13 refuted the mechanism this prediction was drawn
        # from before T3 could be evaluated, so the criterion has no evidential standing either
        # way. Caught in adversarial review; the raw prediction/observation pair is retained.
        "T3_dispersion_prediction": {"record_len_cv": round(cv, 3), "predicted": predicted,
                                     "actual": actual, "status": "VOID_mechanism_refuted_in_phase13"},
    }

    payload = {
        "config": {"seed": SEED, "model": MODEL, "max_docs": MAX_DOCS,
                   "byo_data": True, "criteria_fixed_before_run": True,
                   "privacy": "aggregate metrics only; no transcript content in outputs"},
        "n_docs": len(docs), "record_len_cv": round(cv, 3),
        "raw_condition": raw, "engineered_condition": eng, "verdicts": verdicts,
    }
    blob = json.dumps(payload, indent=2, ensure_ascii=False)
    # privacy assertion over EVERY document and line (an earlier draft checked only the first
    # 50 documents and lines over 20 chars -- narrower than the prose claimed; caught in review)
    for t in docs:
        for line in t.lines:
            if len(line) >= 8:
                assert line not in blob, "transcript content leaked into output"
    (OUT / "phase14_agent_traces.json").write_text(blob, encoding="utf-8")

    md = ["# Phase 14 — Real agent traces (bring your own data)\n\n",
          "The corpus every earlier phase has been an analogy for: tool-call interactions from real "
          "agent sessions, boundaries defined by transcript structure. **Privacy model:** transcripts "
          "never leave the machine (local embedding model), and only aggregate metrics are published; "
          "the script asserts no document line appears in its output. Reproduce on your own sessions "
          "with `--transcripts-dir`.\n\n",
          f"Author's run: **{len(docs)} documents**, record-length CV **{cv:.3f}**.\n\n"]
    for cond, r in (("Raw traces (markerless, as agents emit them today)", raw),
                    ("Engineered condition (one delimiter line appended per record)", eng)):
        md.append(f"## {cond}\n\n| Method | Pk ↓ | F1 ±1 ↑ |\n|---|---:|---:|\n")
        for m, s in r["summary"].items():
            md.append(f"| {m} | {s['pk']:.3f} | {s['f1_tol1']:.3f} |\n")
        md.append("\n| Comparison | wins/losses | sign p | BH |\n|---|---:|---:|---:|\n")
        for name, tt in r["paired_tests"].items():
            md.append(f"| {name.replace('_', ' ')} | {tt['wins_pk']}/{tt['losses_pk']} | "
                      f"{tt['pk_sign_p']} | {tt['pk_sign_p_bh']} |\n")
        md.append("\n")
    v = verdicts
    md.append("## Pre-registered verdicts\n\n")
    md.append(f"- **T1 (some embedding method beats random on raw traces): "
              f"{'HELD' if v['T1_embeddings_beat_random_on_raw_traces'] else 'DID NOT HOLD'}.**\n")
    md.append(f"- **T2 (engineered delimiter closes the problem, closer Pk < 0.1): "
              f"{'HELD' if v['T2_engineered_delimiter_closes_problem'] else 'DID NOT HOLD'}** — "
              "by construction, labelled a demonstration: the informative quantity is the gap it "
              "opens over every post-hoc method on the same documents.\n")
    t3 = v["T3_dispersion_prediction"]
    md.append(f"- **T3 (dispersion curve predicts the fixed-size sign): VOID.** Phase 13 refuted "
              f"the mechanism this prediction was drawn from (rho = −0.03 across six corpora) "
              f"before T3 could be evaluated, so the criterion has no evidential standing in either "
              f"direction. For the record: measured CV {t3['record_len_cv']}, predicted "
              f"{t3['predicted']}, observed {t3['actual']}.\n")
    md.append("\n**Corpus-freezing note.** The first two runs of this script saw different corpora "
              "(CV 0.667 then 0.726) because the transcript directory is live and grew between runs — "
              "including from the session developing this experiment. Documents are now frozen to a "
              "local cache at first parse; the published numbers come from the frozen snapshot.\n")
    (OUT / "phase14_agent_traces.md").write_text("".join(md), encoding="utf-8")
    print(f"[save] {OUT / 'phase14_agent_traces.md'}")
    print(f"[phase14] verdicts: T1={v['T1_embeddings_beat_random_on_raw_traces']} "
          f"T2={v['T2_engineered_delimiter_closes_problem']} T3=VOID (CV={cv:.3f})")


if __name__ == "__main__":
    main()
