"""
Phase 13: The dispersion curve -- turning a retraction into a quantitative claim.

WHY THIS EXISTS
---------------
Phase 11 retracted "fixed-size chunking is worse than random" as a general claim: it held on
Ur III tablets and reversed on commit streams. The rescope proposed a mechanism -- the result is
a fact about RECORD-LENGTH DISPERSION, not about fixed-size chunking. That mechanism is testable:
across corpora, the equal-vs-random Pk gap should be a monotone function of how uneven the
records are. Two data points suggested it; this phase measures the curve.

DESIGN
------
Six corpora spanning the dispersion range, each with real record boundaries:
  - Administrative tablets, Literary tablets (Sumerian rulings; phases 8-10)
  - git/git, express, curl/curl, prettier/prettier commit windows (VCS boundaries; phase 11
    machinery, two repos newly cloned for this phase, pinned --until=2026-01-01)

Per corpus: record-length dispersion = coefficient of variation (CV = sd/mean) of per-record
token counts, pooled over evaluation documents; and the known-K equal-vs-random Pk gap
(gap > 0 means fixed-size is WORSE than random). Association tested with Spearman rank
correlation across corpora (exact p for n = 6) plus, per corpus, the same paired sign test used
throughout. Known-K keeps this comparable with phases 8-11 and isolates placement from count.

PRE-REGISTERED EXPECTATIONS
---------------------------
  D1  The equal-vs-random Pk gap increases with record-length CV (Spearman rho > 0), with the
      sign of the gap flipping somewhere between the commit corpora (uniform) and the tablets
      (uneven).
  D2  No numeric threshold is pre-committed; the location of the flip is reported descriptively.
Whichever way D1 falls, it is reported as fixed.
"""
from __future__ import annotations

import sys

import itertools
import json
import math
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
    Tablet, sumerian_tablets, equal_cuts, pk, N_RANDOM,
)
from phase9_embedding_chunking import sign_test  # noqa: E402
from phase11_modern_indistribution import commit_messages, build_documents  # noqa: E402

SEED = 20260805
MODERN = {
    "git/git commits": (DATA / "modern" / "gitgit", "https://github.com/git/git.git"),
    "express commits": (DATA / "modern" / "express", "https://github.com/expressjs/express.git"),
    "curl/curl commits": (DATA / "modern" / "curl", "https://github.com/curl/curl.git"),
    "prettier commits": (DATA / "modern" / "prettier", "https://github.com/prettier/prettier.git"),
}


def record_token_lengths(t: Tablet) -> list[int]:
    edges = [-1, *t.truth, t.n - 1]
    return [t.cum[edges[k + 1] + 1] - t.cum[edges[k] + 1] for k in range(len(edges) - 1)]


def spearman(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Spearman rho with EXACT permutation p (two-sided) -- n is tiny, so enumerate."""
    n = len(xs)
    rx = np.argsort(np.argsort(xs)).astype(float)
    ry = np.argsort(np.argsort(ys)).astype(float)

    def rho_of(a, b):
        a = a - a.mean(); b = b - b.mean()
        d = float(np.sqrt((a * a).sum() * (b * b).sum()))
        return float((a * b).sum() / d) if d > 0 else 0.0

    obs = rho_of(rx, ry)
    perms = list(itertools.permutations(range(n)))
    count = sum(1 for p_ in perms if abs(rho_of(rx, ry[list(p_)])) >= abs(obs) - 1e-12)
    return obs, count / len(perms)


def main() -> None:
    rng = np.random.default_rng(SEED)
    points = []

    corpora: dict[str, list[Tablet]] = {}
    by_genre, _ = sumerian_tablets()
    corpora["Administrative tablets"] = by_genre["Administrative"]
    corpora["Literary tablets"] = by_genre["Literary"]
    for i, (label, (path, url)) in enumerate(MODERN.items()):
        msgs = commit_messages(path, url)
        # NOTE: stable per-corpus seed by enumeration index. An earlier draft used hash(label),
        # which is randomized per process (PYTHONHASHSEED) -- precisely the irreproducibility
        # class this repository exists to catch.
        corpora[label] = build_documents(msgs, np.random.default_rng(SEED + i))

    for label, docs in corpora.items():
        if len(docs) < 30:
            print(f"[phase13] {label}: only {len(docs)} documents, skipping")
            continue
        rec_lens = [l for t in docs for l in record_token_lengths(t)]
        cv = float(np.std(rec_lens) / np.mean(rec_lens))
        eq_pk, rn_pk = [], []
        for t in docs:
            ref = set(t.truth)
            eq_pk.append(pk(t.n, ref, set(equal_cuts(t.n, t.K))))
            draws = [pk(t.n, ref, set(rng.choice(t.n - 1, size=t.K - 1, replace=False).tolist()))
                     for _ in range(N_RANDOM)]
            rn_pk.append(float(np.mean(draws)))
        gap = float(np.mean(eq_pk) - np.mean(rn_pk))
        p = sign_test(eq_pk, rn_pk)
        points.append({
            "corpus": label, "n_docs": len(docs), "n_records": len(rec_lens),
            "record_len_cv": round(cv, 3),
            "equal_pk": round(float(np.mean(eq_pk)), 4),
            "random_pk": round(float(np.mean(rn_pk)), 4),
            "gap_equal_minus_random": round(gap, 4),
            "equal_worse": bool(gap > 0),
            "paired_sign_p": round(p, 5),
        })
        print(f"[phase13] {label:<26} CV={cv:.3f}  gap={gap:+.4f}  p={p:.5f}")

    xs = [pt["record_len_cv"] for pt in points]
    ys = [pt["gap_equal_minus_random"] for pt in points]
    rho, p_exact = spearman(xs, ys)
    ordered = sorted(points, key=lambda pt: pt["record_len_cv"])
    # ALL sign changes along the CV ordering (an earlier draft kept only the last
    # negative-to-positive transition; the sequence crosses sign more than once, which is
    # itself evidence against a monotone dispersion mechanism). Caught in review.
    flips = []
    for a, b in zip(ordered[:-1], ordered[1:]):
        ga, gb = a["gap_equal_minus_random"], b["gap_equal_minus_random"]
        if (ga <= 0 < gb) or (gb <= 0 < ga):
            flips.append((a["corpus"], a["record_len_cv"], b["corpus"], b["record_len_cv"]))
    flip = flips

    verdicts = {"D1_gap_increases_with_cv": bool(rho > 0 and p_exact < 0.05)}

    (OUT / "phase13_dispersion.json").write_text(json.dumps({
        "config": {"seed": SEED, "n_random": N_RANDOM, "known_K": True,
                   "criteria_fixed_before_run": True},
        "points": points, "spearman_rho": round(rho, 3), "spearman_p_exact": round(p_exact, 5),
        "sign_flip_between": flip, "verdicts": verdicts},
        indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Phase 13 — The dispersion curve: when is fixed-size chunking worse than random?\n\n",
          "Phase 11 retracted \"fixed-size is worse than random\" as a general claim and proposed the "
          "mechanism: the result is about **record-length dispersion**. This phase measures the curve "
          "across six corpora with real boundaries — two Sumerian genres and four commit-stream "
          "corpora spanning message-culture styles. Gap = mean equal Pk − mean random Pk under known "
          "K; positive gap means fixed-size is worse than random.\n\n",
          "| Corpus | Docs | Records | Record-length CV | equal Pk | random Pk | Gap | equal worse? | sign p |\n",
          "|---|---:|---:|---:|---:|---:|---:|:---:|---:|\n"]
    for pt in ordered:
        md.append(f"| {pt['corpus']} | {pt['n_docs']:,} | {pt['n_records']:,} | {pt['record_len_cv']} | "
                  f"{pt['equal_pk']:.3f} | {pt['random_pk']:.3f} | {pt['gap_equal_minus_random']:+.4f} | "
                  f"{'yes' if pt['equal_worse'] else 'no'} | {pt['paired_sign_p']} |\n")
    md.append(f"\n**Spearman rank correlation (gap vs. CV): rho = {rho:.3f}, exact two-sided "
              f"p = {p_exact:.5f}** over {len(points)} corpora.\n\n")
    if flip:
        md.append(f"The gap changes sign **{len(flip)} time(s)** along the CV ordering — multiple "
                  "crossings are themselves evidence against any monotone dispersion mechanism: "
                  + "; ".join(f"between {f[0]} (CV {f[1]}) and {f[2]} (CV {f[3]})" for f in flip)
                  + ".\n\n")
    md.append("## Pre-registered verdict\n\n")
    md.append(f"- **D1 (gap increases with record-length CV): "
              f"{'HELD' if verdicts['D1_gap_increases_with_cv'] else 'DID NOT HOLD'}** "
              f"(rho = {rho:.3f}, p = {p_exact:.5f}).\n\n")
    md.append("With six corpora the correlation has limited power and the exact permutation p is the "
              "honest test; the per-corpus paired sign tests carry the within-corpus weight. If D1 "
              "held, the practical reading is: measure your records' length CV before choosing "
              "fixed-size chunking — above the flip region, cutting at random is literally better "
              "than cutting evenly.\n")
    (OUT / "phase13_dispersion.md").write_text("".join(md), encoding="utf-8")
    print(f"[save] {OUT / 'phase13_dispersion.md'}")
    print(f"[phase13] rho={rho:.3f} p={p_exact:.5f} verdicts={verdicts}")


if __name__ == "__main__":
    main()
