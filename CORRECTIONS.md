# Corrections

A running, dated log of claims this repository has retracted or materially revised. Newest first.

Nothing is removed from the record. Superseded claims stay visible with the reason they failed, so anyone who read or cited an earlier version can see exactly what changed.

---

## 2026-07-31 — WITHDRAWN: "`<RULING>` is a validated logical row separator"

**Affected:** README artifact #4, README implication #2, `outputs/compression_findings.md` §4, and the Findings table row "`<RULING>` is a logical row separator (not visual)".

**Original claim.** Adjacent ruling-delimited chunks share trigrams 30–500× more than a shuffled baseline (Royal Inscription p=0.002, Administrative p=0.005), establishing that the physical `<RULING>` mark corresponds to a logical row boundary — and, by extension, motivating a three-tier SURFACE/COLUMN/RULING agent-memory design.

**Status: withdrawn.** There is no statistical evidence in this corpus sample that `<RULING>` marks content boundaries.

### What went wrong

Two independent defects, one fatal.

**1. The null hypothesis was wrong (fatal).** The test compared observed cross-boundary trigram sharing against a null built by *pooling the tablet's tokens, shuffling them, and re-cutting at the same lengths*. That null destroys all local structure in the text. Beating it demonstrates only that Sumerian is locally coherent — a property of any natural language, and one that says nothing about `<RULING>` in particular. Any arbitrary chunking of any real text beats that null.

The null that actually isolates the question holds the real token order *and* the exact multiset of chunk lengths fixed, and permutes only **where the cuts fall**. Under that null the effect vanishes:

| Genre | Pairs | Observed | Token-shuffle null (wrong) | Boundary-permute null (correct) | p (correct) |
|---|---:|---:|---:|---:|---:|
| Administrative | 17 | 0.176 | 0.004 | 0.343 | 0.781 |
| Literary | 108 | 0.731 | 0.018 | 0.889 | 0.905 |
| Lexical | 13 | 0.538 | 0.037 | 0.430 | 0.274 |
| Royal Inscription | 10 | 0.500 | 0.001 | 0.500 | 1.000 |

The wrong null sits ~100× below the right one. Observed values land *at or below* the correct null in every genre — the opposite of the reported direction.

**2. The p-value was computed against the wrong distribution.** It measured the fraction of *individual* null chunk-pairs whose value met or exceeded the observed **mean**, rather than building a null distribution *of the mean* (one value per permutation). Because shared-trigram counts are integers and heavily zero-inflated, the reported p-value reduced exactly to "the fraction of shuffled pairs sharing at least one trigram" — a different quantity from the one being claimed. In this instance it happened to land near the correctly computed value (0.005 vs 0.005 for Administrative), so it was not what produced the false positive, but it was wrong and is fixed.

Both are corrected in `scripts/phase3_compression.py::ruling_parity`, which now reports both nulls side by side, uses a permutation distribution of the mean, and applies the standard `(r+1)/(n+1)` correction so p is never exactly 0.

### What this does *not* say

A null result on 10–17 adjacent-chunk pairs is weak evidence in either direction. This does not establish that `<RULING>` is meaningless — the marks are plainly deliberate, physically drawn by scribes, and the three nested structural levels are real features of the artifact. It establishes only that **this test does not support the claim that was made from it**, and that the sample here is too small to settle the question either way. Testing it properly would need the full corpus rather than a 500-tablet-per-genre sample, and a boundary-placement null from the outset.

### Knock-on effects

- The three-tier SURFACE → COLUMN → RULING memory design is now presented as an **untested design proposal**, not a corpus finding.
- Anything in `outputs/FULL_IDEAS.md`, `outputs/summary.md`, or `outputs/reference_architecture.md` that leans on RULING-as-validated-row-boundary inherits this retraction. Those are hand-authored design documents and have not been individually rewritten; treat RULING-derived claims in them as proposals.

### What is unaffected

- **§1 Zipf** (Admin s=1.746, Royal s=1.737, Lexical s=1.114) — descriptive statistics, unchanged.
- **§2 Compression Δ** — descriptive, unchanged. Note it uses the same token-shuffle baseline, but its claim is only "more structured than random token order", which is what that baseline legitimately tests.
- **§3 ELS null result** (0 of 495 Bonferroni-significant) — this was always a correct permutation test: one null value per shuffle, compared against the observed statistic. Audited and unchanged. Being a null result, it is also the claim least at risk from this class of error.
- **Phase 1 probe frequencies** (`kišib₃` 25.4%, year-formula 74.2%, `u₃-na-a-du₁₁` 58.8%) — raw regex counts over the sample, no inference involved.
- **The `kishib3` benchmark** (5/5 vs 0/5 capability, +59% bytes, +37 tokens/write) — an engineering measurement, no statistics.

### How it was found

A reproducibility audit re-ran the full pipeline from a clean clone, then examined how each reported p-value was computed. The RULING-parity p-value was traced to a comparison against the pooled distribution of individual null pairs; investigating that led to examining the null itself. The alternative control was implemented independently and run at 500 permutations before the change was made to the pipeline.

---

## Reporting a problem

If you find an error, open an issue. Claims that survive adversarial checking are worth more than claims that were never checked, and a corrected repo is more useful than a confident one. Independent reproduction of any Phase 3 statistic is especially welcome — see the "Verifying your run matched" section of the README.
