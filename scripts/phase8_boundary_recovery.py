"""
Phase 8: Can the boundary objective RECOVER the scribal rulings it was derived from?

WHY THIS EXISTS
---------------
Phase 4 showed that real `<RULING>` boundaries sit at points of LOW cross-boundary trigram overlap
(full corpus, two nulls, BH p = 0.0006). Phase 6 showed record-closing formulae are enriched
immediately before rulings (position-controlled, 6.3x for szu ba-ti). Both are association tests.

This phase asks the predictive question: given a tablet's line sequence WITHOUT its rulings, can an
unsupervised objective put the boundaries back where the scribe drew them? That converts
"boundaries have property X" into "property X suffices to FIND boundaries" -- a strictly stronger,
and directly actionable, claim: it is exactly the label-free chunking problem in agent memory / RAG.

HONEST LINEAGE
--------------
Cutting at similarity minima is a TextTiling-family objective (Hearst 1997); exact optimisation by
search over cut positions echoes DP segmentation (Utiyama & Isahara 2001). The novelty here is NOT
the objective -- it is the ground truth: physically drawn record boundaries from ~4,000 years ago,
and the corpus-derived closer signal (Phase 6) used as a second, independent boundary cue.

DESIGN
------
Units are LINES (parsed exactly as Phase 6). Ground truth: the set of line indices after which a
<RULING> occurs. K (number of segments) is GIVEN to every method -- the standard "known K"
evaluation in text segmentation, which isolates boundary PLACEMENT from boundary COUNT estimation.

Methods (all place K-1 cuts):
  equal        -- equally spaced cuts (the fixed-size-chunking baseline used everywhere in RAG)
  random       -- uniform random cuts, averaged over N_RANDOM draws (chance floor)
  overlap_min  -- minimise total shared trigrams between adjacent segments (exact search when the
                  combination count permits, hill-climbing from `equal` otherwise; counts reported)
  closer       -- cut after the K-1 lines best matching the Phase-6-validated closers
                  (szu ba-ti, kiszib3); ties broken by line order. Uses NO similarity signal.
  hybrid       -- overlap_min score minus a fixed bonus (LAMBDA=1 shared trigram) for each cut
                  placed after a closer line. LAMBDA is fixed a priori, not tuned.

Metrics: exact boundary F1, tolerance-1 F1, Pk (Beeferman et al. 1999), WindowDiff (Pevzner &
Hearst 2002). Lower Pk/WindowDiff is better. Window size k = max(2, round(mean true segment
length / 2)) per tablet, the standard convention. Paired sign tests (binomial) against `equal`.

The same pipeline then runs on a MODERN corpus with known boundaries -- the markdown documents of
this repository, section boundaries at `## ` headings, heading lines removed so the objective
cannot read the marker -- as the agent-memory transfer demonstration.
"""
from __future__ import annotations

import sys

import itertools
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


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
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20260802
N_RANDOM = 200
MAX_EXACT_COMBOS = 200_000
LAMBDA = 1.0                     # fixed a priori; not tuned
MIN_SEG_TOKENS = 4               # mirrors Phase 4's MIN_CHUNK: a segment must be able to hold a
                                 # trigram. Without this the raw-overlap objective has a degenerate
                                 # optimum -- shave off a <3-token segment, whose trigram set is
                                 # empty, so its overlap with anything is zero. The first run of
                                 # this script hit exactly that (F1-exact 0.009, BELOW random);
                                 # the constraint was added in response and is noted in the report.
MIN_LINES = 6
MAX_LINES = 120                  # cap for tractability; skipped tablets are counted
STRUCTURAL_LINE = re.compile(r"^<[A-Z_]+>$")

CLOSER_RES = [re.compile(r"\bšu\s+ba-ti\b"), re.compile(r"\bkišib(?:₃)?\b")]


# ----------------------------------------------------------------- parsing

def parse_tablet(text: str) -> tuple[list[str], set[int]]:
    """Lines + set of interior boundary indices (boundary after line i)."""
    lines, bounds = [], set()
    for raw in str(text).split("\n"):
        s = raw.strip()
        if not s:
            continue
        if s == "<RULING>":
            if lines:
                bounds.add(len(lines) - 1)
            continue
        if STRUCTURAL_LINE.match(s):
            continue
        lines.append(s)
    return lines, {b for b in bounds if b < len(lines) - 1}


def line_tokens(line: str) -> list[str]:
    return line.split()


# ----------------------------------------------------------------- objective

class Tablet:
    def __init__(self, lines: list[str], truth: set[int]):
        self.lines = lines
        self.tok = [line_tokens(l) for l in lines]
        self.truth = sorted(truth)
        self.n = len(lines)
        self.K = len(truth) + 1
        self._span_cache: dict[tuple[int, int], frozenset] = {}
        self.closer_score = [1 if any(rx.search(l) for rx in CLOSER_RES) else 0 for l in lines]
        self.has_closer = any(self.closer_score)
        cum = [0]
        for t_ in self.tok:
            cum.append(cum[-1] + len(t_))
        self.cum = cum               # tokens in lines[a..b] = cum[b+1]-cum[a]

    def feasible(self, cuts: tuple[int, ...]) -> bool:
        edges = [-1, *cuts, self.n - 1]
        return all(self.cum[edges[i + 1] + 1] - self.cum[edges[i] + 1] >= MIN_SEG_TOKENS
                   for i in range(len(edges) - 1))

    def span_tris(self, a: int, b: int) -> frozenset:
        """Trigram set of lines[a..b] inclusive."""
        key = (a, b)
        got = self._span_cache.get(key)
        if got is None:
            toks = [t for i in range(a, b + 1) for t in self.tok[i]]
            got = frozenset(zip(toks, toks[1:], toks[2:]))
            self._span_cache[key] = got
        return got

    def cost(self, cuts: tuple[int, ...], closer_bonus: float = 0.0) -> float:
        """Total adjacent-segment shared trigrams, minus bonus per closer-aligned cut."""
        edges = [-1, *cuts, self.n - 1]
        total = 0.0
        for i in range(len(edges) - 2):
            a = self.span_tris(edges[i] + 1, edges[i + 1])
            b = self.span_tris(edges[i + 1] + 1, edges[i + 2])
            total += len(a & b)
        if closer_bonus:
            total -= closer_bonus * sum(self.closer_score[c] for c in cuts)
        return total


def solve_overlap(t: Tablet, closer_bonus: float = 0.0) -> tuple[tuple[int, ...], str]:
    """Place K-1 cuts minimising cost. Exact when tractable, else hill-climb from equal."""
    m = t.K - 1
    positions = list(range(t.n - 1))
    n_combos = math.comb(len(positions), m)
    if n_combos <= MAX_EXACT_COMBOS:
        best, best_c = None, float("inf")
        for cuts in itertools.combinations(positions, m):
            if not t.feasible(cuts):
                continue
            c = t.cost(cuts, closer_bonus)
            if c < best_c:
                best, best_c = cuts, c
        if best is not None:
            return best, "exact"
        return equal_cuts(t.n, t.K), "fallback"
    # hill-climb: move one cut at a time to any free position until no improvement
    cuts = list(equal_cuts(t.n, t.K))
    cur = t.cost(tuple(cuts), closer_bonus)
    improved = True
    while improved:
        improved = False
        for i in range(m):
            for p in positions:
                if p in cuts:
                    continue
                trial = sorted(cuts[:i] + [p] + cuts[i + 1:])
                if not t.feasible(tuple(trial)):
                    continue
                c = t.cost(tuple(trial), closer_bonus)
                if c < cur - 1e-9:
                    cuts, cur, improved = trial, c, True
    return tuple(cuts), "greedy"


def equal_cuts(n: int, K: int) -> tuple[int, ...]:
    return tuple(sorted({min(n - 2, max(0, round((i + 1) * n / K) - 1)) for i in range(K - 1)}))


def closer_cuts(t: Tablet) -> tuple[int, ...]:
    """Cut after closer-matching lines. If the tablet has no closer line at all, fall back to
    equal spacing -- otherwise the index-order tie-break silently piles the cuts at the start of
    the tablet, and the aggregate score measures that accident rather than the closers."""
    m = t.K - 1
    if not t.has_closer:
        return equal_cuts(t.n, t.K)
    scored = [i for i in range(t.n - 1) if t.closer_score[i]]
    if len(scored) >= m:
        return tuple(sorted(scored[:m]))
    rest = [c for c in equal_cuts(t.n, t.K) if c not in scored]
    return tuple(sorted(scored + rest[:m - len(scored)]))


# ----------------------------------------------------------------- metrics

def _seg_ids(n: int, cuts: set[int]) -> list[int]:
    ids, cur = [], 0
    for i in range(n):
        ids.append(cur)
        if i in cuts:
            cur += 1
    return ids


def pk(n: int, ref: set[int], hyp: set[int]) -> float:
    """Hand-implemented from Beeferman, Berger & Lafferty (1999): fraction of position pairs
    (i, i+k) on which reference and hypothesis disagree about same-segment membership, k = half
    the mean reference segment length. NOTE: uses the paper's N-k window count; NLTK's
    implementation uses N-k+1, so NLTK reproductions will differ in the third decimal. This is
    deliberate fidelity to the published formula, not a bug."""
    seg_lens = np.diff([-1, *sorted(ref), n - 1])
    k = max(2, round(float(np.mean(seg_lens)) / 2))
    r, h = _seg_ids(n, ref), _seg_ids(n, hyp)
    errs = tot = 0
    for i in range(n - k):
        tot += 1
        if (r[i] == r[i + k]) != (h[i] == h[i + k]):
            errs += 1
    return errs / tot if tot else 0.0


def windowdiff(n: int, ref: set[int], hyp: set[int]) -> float:
    """Hand-implemented from Pevzner & Hearst (2002): fraction of windows in which the reference
    and hypothesis boundary COUNTS differ. Same N-k window convention as pk() above."""
    seg_lens = np.diff([-1, *sorted(ref), n - 1])
    k = max(2, round(float(np.mean(seg_lens)) / 2))
    errs = tot = 0
    for i in range(n - k):
        tot += 1
        rb = sum(1 for b in ref if i <= b < i + k)
        hb = sum(1 for b in hyp if i <= b < i + k)
        if rb != hb:
            errs += 1
    return errs / tot if tot else 0.0


def f1(ref: set[int], hyp: set[int], tol: int = 0) -> float:
    if not ref or not hyp:
        return 0.0
    matched_r, used_h = 0, set()
    for b in ref:
        for h in hyp:
            if h not in used_h and abs(h - b) <= tol:
                matched_r += 1
                used_h.add(h)
                break
    prec = len(used_h) / len(hyp)
    rec = matched_r / len(ref)
    return 2 * prec * rec / (prec + rec) if prec + rec else 0.0


# ----------------------------------------------------------------- evaluation

def evaluate(tablets: list[Tablet], rng) -> dict:
    methods = ["equal", "random", "closer", "overlap_min", "hybrid"]
    acc = {m: {"pk": [], "wd": [], "f1": [], "f1_tol1": []} for m in methods}
    solver_kind = {"exact": 0, "greedy": 0, "fallback": 0}

    for t in tablets:
        ref = set(t.truth)
        hyps: dict[str, set[int]] = {}
        hyps["equal"] = set(equal_cuts(t.n, t.K))
        hyps["closer"] = set(closer_cuts(t))
        cuts, kind = solve_overlap(t)
        solver_kind[kind] += 1
        hyps["overlap_min"] = set(cuts)
        hcuts, _ = solve_overlap(t, closer_bonus=LAMBDA)
        hyps["hybrid"] = set(hcuts)

        for m in ("equal", "closer", "overlap_min", "hybrid"):
            h = hyps[m]
            acc[m]["pk"].append(pk(t.n, ref, h))
            acc[m]["wd"].append(windowdiff(t.n, ref, h))
            acc[m]["f1"].append(f1(ref, h, 0))
            acc[m]["f1_tol1"].append(f1(ref, h, 1))

        rnd = {"pk": [], "wd": [], "f1": [], "f1_tol1": []}
        for _ in range(N_RANDOM):
            h = set(rng.choice(t.n - 1, size=t.K - 1, replace=False).tolist())
            rnd["pk"].append(pk(t.n, ref, h))
            rnd["wd"].append(windowdiff(t.n, ref, h))
            rnd["f1"].append(f1(ref, h, 0))
            rnd["f1_tol1"].append(f1(ref, h, 1))
        for key in rnd:
            acc["random"][key].append(float(np.mean(rnd[key])))

    def sign_test(a: list[float], b: list[float]) -> float:
        """Genuinely two-sided binomial sign test: p = 2 * min(P(X <= w), P(X >= w)) under
        X ~ Bin(n, 1/2), ties dropped, capped at 1.

        An earlier version summed only the upper tail from the observed win count and doubled
        it, which is correct when wins > n/2 but saturates at 1.0 whenever wins <= n/2 -- so a
        method LOSING 0/20 would have reported p = 1.0 instead of significant. Caught in
        adversarial review; fixed and disclosed here."""
        wins = sum(1 for x, y in zip(a, b) if x < y)
        ties = sum(1 for x, y in zip(a, b) if x == y)
        n = len(a) - ties
        if n == 0:
            return 1.0
        from math import comb
        upper = sum(comb(n, i) for i in range(wins, n + 1)) / 2 ** n
        lower = sum(comb(n, i) for i in range(0, wins + 1)) / 2 ** n
        return float(min(1.0, 2 * min(upper, lower)))

    def bh(pvals: list[float]) -> list[float]:
        """Benjamini-Hochberg adjusted p-values."""
        m = len(pvals)
        order = sorted(range(m), key=lambda i: pvals[i])
        adj = [0.0] * m
        prev = 1.0
        for rank in range(m - 1, -1, -1):
            i = order[rank]
            prev = min(prev, pvals[i] * m / (rank + 1))
            adj[i] = prev
        return adj

    summary = {}
    for m in methods:
        summary[m] = {k: round(float(np.mean(v)), 4) for k, v in acc[m].items()}
    tests = {}
    for m in ("overlap_min", "closer", "hybrid"):
        for base in ("equal", "random"):
            tests[f"{m}_vs_{base}"] = {
                "pk_sign_p": round(sign_test(acc[m]["pk"], acc[base]["pk"]), 5),
                "wins_pk": sum(1 for x, y in zip(acc[m]["pk"], acc[base]["pk"]) if x < y),
                "losses_pk": sum(1 for x, y in zip(acc[m]["pk"], acc[base]["pk"]) if x > y),
            }
    # BH across ALL paired tests in this corpus -- the genre-reversal claim rests on these,
    # so they get the same multiple-comparison discipline as the Phase 4 result.
    names = list(tests)
    adjusted = bh([tests[k]["pk_sign_p"] for k in names])
    for k, a_ in zip(names, adjusted):
        tests[k]["pk_sign_p_bh"] = round(a_, 5)

    # Same-population baselines for the closer stratum: the quotable stratified number needs
    # comparators computed on the SAME tablets, not the whole-corpus mean.
    strat_base = {}
    for label, sel in (("with_closer_lines", True), ("without_closer_lines", False)):
        idx = [i for i, t in enumerate(tablets) if t.has_closer == sel]
        if idx:
            strat_base[label] = {
                "n": len(idx),
                "closer_pk": round(float(np.mean([acc["closer"]["pk"][i] for i in idx])), 4),
                "random_pk": round(float(np.mean([acc["random"]["pk"][i] for i in idx])), 4),
                "equal_pk": round(float(np.mean([acc["equal"]["pk"][i] for i in idx])), 4),
            }
    return {"n_tablets": len(tablets), "solver": solver_kind, "summary": summary,
            "paired_tests": tests, "closer_stratum": strat_base}


# ----------------------------------------------------------------- corpora

def sumerian_tablets() -> tuple[dict[str, list[Tablet]], dict]:
    df = pd.read_parquet(DATA / "sumtablets.parquet", columns=["id", "genre", "transliteration"])
    df["g"] = df["genre"].fillna("Unknown").astype(str).str.split(",").str[0].str.strip()
    df = df[df["transliteration"].astype(str).str.contains("<RULING>")]
    prefilter = {"tablets_with_any_ruling": int(len(df))}
    out: dict[str, list[Tablet]] = {}
    skipped = 0
    for genre in ["Administrative", "Literary"]:
        rows = []
        for raw in df[df["g"] == genre]["transliteration"]:
            lines, truth = parse_tablet(raw)
            if not truth or len(lines) < MIN_LINES:
                continue
            if len(lines) > MAX_LINES:
                skipped += 1
                continue
            rows.append(Tablet(lines, truth))
        if len(rows) >= 30:
            out[genre] = rows
    prefilter["skipped_over_max_lines"] = skipped
    print(f"[phase8] tablets with any ruling: {prefilter['tablets_with_any_ruling']:,}; "
          f"over {MAX_LINES} lines skipped: {skipped}")
    return out, prefilter


# Fixed allowlist. Earlier versions globbed outputs/*.md, which meant this script INGESTED ITS
# OWN OUTPUT FILE on rerun (phase8_boundary_recovery.md matched the filter) plus other generated
# reports quoting the very numbers under test -- a self-referential feedback loop caught in
# adversarial review. Root-level hand-written documents only. Note these are still in-domain
# (documents about this project, some quoting Sumerian formulae), which is why the demo is
# labelled illustrative and its `closer` column is not meaningful here.
MD_ALLOWLIST = ["README.md", "CORRECTIONS.md", "REVIEWERS.md", "FINDINGS.md"]


def markdown_docs() -> list[Tablet]:
    """Modern transfer demo: recover `## ` section boundaries in this repo's own documents."""
    docs = []
    for path in [ROOT / n for n in MD_ALLOWLIST if (ROOT / n).exists()]:
        raw = path.read_text(encoding="utf-8")
        lines, truth = [], set()
        for line in raw.split("\n"):
            s = line.strip()
            if not s:
                continue
            if s.startswith("## "):
                if lines:
                    truth.add(len(lines) - 1)
                continue                      # heading REMOVED: objective cannot read the marker
            lines.append(s)
        truth = {b for b in truth if b < len(lines) - 1}
        if truth and MIN_LINES <= len(lines) <= MAX_LINES and len(truth) >= 2:
            docs.append(Tablet(lines, truth))
    return docs


def main() -> None:
    rng = np.random.default_rng(SEED)
    results = {}

    by_genre, prefilter = sumerian_tablets()
    for genre, tablets in by_genre.items():
        print(f"[phase8] {genre}: {len(tablets):,} tablets ...")
        results[genre] = evaluate(tablets, rng)
        s = results[genre]["summary"]
        print(f"    Pk   equal={s['equal']['pk']:.3f} random={s['random']['pk']:.3f} "
              f"closer={s['closer']['pk']:.3f} overlap={s['overlap_min']['pk']:.3f} "
              f"hybrid={s['hybrid']['pk']:.3f}")

    md_docs = markdown_docs()
    if md_docs:
        print(f"[phase8] markdown demo: {len(md_docs)} documents ...")
        results["Markdown (this repo, modern transfer demo)"] = evaluate(md_docs, rng)

    (OUT / "phase8_boundary_recovery.json").write_text(json.dumps({
        "config": {"seed": SEED, "n_random": N_RANDOM, "lambda_hybrid": LAMBDA,
                   "max_exact_combos": MAX_EXACT_COMBOS, "min_lines": MIN_LINES,
                   "max_lines": MAX_LINES, "known_K": True,
                   "markdown_allowlist": MD_ALLOWLIST},
        "corpus_prefilter": prefilter,
        "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Phase 8 — Recovering scribal boundaries without seeing them\n\n",
          "Phases 4 and 6 established two *properties* of `<RULING>` boundaries: adjacent chunks share fewer "
          "trigrams than alternative cuts, and record-closing formulae precede them. This phase asks the strictly "
          "stronger predictive question: **do those properties suffice to put the boundaries back?** Each method "
          "receives a tablet's line sequence with rulings removed and the true number of segments K, and must "
          "place K−1 cuts. This is exactly the label-free chunking problem in agent memory and RAG.\n\n",
          "**Lineage stated plainly:** cutting at similarity minima is a TextTiling-family objective "
          "(Hearst 1997); exact search over cut positions echoes DP segmentation (Utiyama & Isahara 2001). "
          "The contribution is the ground truth — physically drawn record boundaries — and the corpus-derived "
          "closer signal as an independent cue, not the objective itself.\n\n",
          "Metrics: Pk (Beeferman et al. 1999) and WindowDiff (Pevzner & Hearst 2002), **lower is better**; "
          "boundary F1 exact and ±1 line. `random` is the mean of "
          f"{N_RANDOM} uniform draws. Paired sign tests (two-sided) compare methods per document against both `equal` and `random`, BH-corrected within corpus.\n\n"]
    for corpus, r in results.items():
        md.append(f"## {corpus}\n\n{r['n_tablets']:,} documents · solver: {r['solver']['exact']:,} exact, "
                  f"{r['solver']['greedy']:,} hill-climb, {r['solver'].get('fallback', 0):,} infeasible-fallback\n\n")
        md.append("| Method | Pk ↓ | WindowDiff ↓ | F1 exact ↑ | F1 ±1 ↑ |\n|---|---:|---:|---:|---:|\n")
        for m in ("random", "equal", "closer", "overlap_min", "hybrid"):
            s = r["summary"][m]
            md.append(f"| {m} | {s['pk']:.3f} | {s['wd']:.3f} | {s['f1']:.3f} | {s['f1_tol1']:.3f} |\n")
        cs = r.get("closer_stratum", {})
        w = cs.get("with_closer_lines")
        if w:
            wo = cs.get("without_closer_lines", {})
            md.append(f"**Stratified, same-population comparison** — the only fair way to read the closer "
                      f"result: on the {w['n']:,} documents that contain a closer line, closer Pk = "
                      f"**{w['closer_pk']}** vs random **{w['random_pk']}** and equal **{w['equal_pk']}** "
                      f"*on those same documents*. On the {wo.get('n', 0):,} documents with no closer line, "
                      f"the method falls back to equal spacing (Pk {wo.get('closer_pk')}) and the marker "
                      f"signal simply does not exist — boundary placement there remains unsolved.\n\n")
        md.append("\n| Comparison | wins / losses (Pk) | sign p (two-sided) | BH-adjusted |\n|---|---:|---:|---:|\n")
        for name, t in r["paired_tests"].items():
            md.append(f"| {name.replace('_', ' ')} | {t['wins_pk']} / {t['losses_pk']} | "
                      f"{t['pk_sign_p']} | {t.get('pk_sign_p_bh')} |\n")
        md.append("\nBH adjustment is across all paired tests within this corpus. The sign test is the "
                  "corrected two-sided version (an earlier release's implementation saturated at p=1 for "
                  "methods that LOST most comparisons; see the function docstring).\n\n")
    (OUT / "phase8_boundary_recovery.md").write_text("".join(md), encoding="utf-8")
    print(f"[save] {OUT / 'phase8_boundary_recovery.md'}")


if __name__ == "__main__":
    main()
