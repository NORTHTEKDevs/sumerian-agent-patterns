# Phase 8 — Recovering scribal boundaries without seeing them

Phases 4 and 6 established two *properties* of `<RULING>` boundaries: adjacent chunks share fewer trigrams than alternative cuts, and record-closing formulae precede them. This phase asks the strictly stronger predictive question: **do those properties suffice to put the boundaries back?** Each method receives a tablet's line sequence with rulings removed and the true number of segments K, and must place K−1 cuts. This is exactly the label-free chunking problem in agent memory and RAG.

**Lineage stated plainly:** cutting at similarity minima is a TextTiling-family objective (Hearst 1997); exact search over cut positions echoes DP segmentation (Utiyama & Isahara 2001). The contribution is the ground truth — physically drawn record boundaries — and the corpus-derived closer signal as an independent cue, not the objective itself.

Metrics: Pk (Beeferman et al. 1999) and WindowDiff (Pevzner & Hearst 2002), **lower is better**; boundary F1 exact and ±1 line. `random` is the mean of 200 uniform draws. Paired sign tests compare methods per tablet against `equal`.

## Administrative

1,717 documents · solver: 1,694 exact, 22 hill-climb, 1 infeasible-fallback

| Method | Pk ↓ | WindowDiff ↓ | F1 exact ↑ | F1 ±1 ↑ |
|---|---:|---:|---:|---:|
| random | 0.405 | 0.407 | 0.097 | 0.269 |
| equal | 0.438 | 0.440 | 0.080 | 0.301 |
| closer | 0.371 | 0.373 | 0.194 | 0.400 |
| overlap_min | 0.454 | 0.456 | 0.018 | 0.061 |
| hybrid | 0.395 | 0.397 | 0.125 | 0.205 |
`closer` scope: 467 documents contain a closer line (Pk 0.2076), 1,250 contain none and fall back to equal spacing (Pk 0.4319). The closer signal exists only where closers exist; the stratified numbers are the honest ones.


| Comparison | wins / losses (Pk) | sign-test p |
|---|---:|---:|
| overlap min vs equal | 756 / 660 | 0.01156 |
| closer vs equal | 311 / 62 | 0.0 |
| hybrid vs equal | 844 / 557 | 0.0 |

## Literary

91 documents · solver: 75 exact, 7 hill-climb, 9 infeasible-fallback

| Method | Pk ↓ | WindowDiff ↓ | F1 exact ↑ | F1 ±1 ↑ |
|---|---:|---:|---:|---:|
| random | 0.374 | 0.406 | 0.143 | 0.290 |
| equal | 0.373 | 0.403 | 0.208 | 0.361 |
| closer | 0.369 | 0.400 | 0.203 | 0.367 |
| overlap_min | 0.347 | 0.380 | 0.111 | 0.223 |
| hybrid | 0.349 | 0.383 | 0.115 | 0.242 |
`closer` scope: 5 documents contain a closer line (Pk 0.3983), 86 contain none and fall back to equal spacing (Pk 0.3678). The closer signal exists only where closers exist; the stratified numbers are the honest ones.


| Comparison | wins / losses (Pk) | sign-test p |
|---|---:|---:|
| overlap min vs equal | 44 / 24 | 0.02053 |
| closer vs equal | 1 / 1 | 1.0 |
| hybrid vs equal | 42 / 24 | 0.03558 |

## Markdown (this repo, modern transfer demo)

7 documents · solver: 4 exact, 3 hill-climb, 0 infeasible-fallback

| Method | Pk ↓ | WindowDiff ↓ | F1 exact ↑ | F1 ±1 ↑ |
|---|---:|---:|---:|---:|
| random | 0.450 | 0.480 | 0.086 | 0.219 |
| equal | 0.550 | 0.570 | 0.071 | 0.171 |
| closer | 0.481 | 0.506 | 0.018 | 0.154 |
| overlap_min | 0.381 | 0.426 | 0.107 | 0.183 |
| hybrid | 0.387 | 0.431 | 0.089 | 0.201 |
`closer` scope: 4 documents contain a closer line (Pk 0.4257), 3 contain none and fall back to equal spacing (Pk 0.554). The closer signal exists only where closers exist; the stratified numbers are the honest ones.


| Comparison | wins / losses (Pk) | sign-test p |
|---|---:|---:|
| overlap min vs equal | 6 / 0 | 0.03125 |
| closer vs equal | 3 / 1 | 0.625 |
| hybrid vs equal | 5 / 0 | 0.0625 |

