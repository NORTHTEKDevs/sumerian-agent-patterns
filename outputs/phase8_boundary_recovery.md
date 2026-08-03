# Phase 8 — Recovering scribal boundaries without seeing them

Phases 4 and 6 established two *properties* of `<RULING>` boundaries: adjacent chunks share fewer trigrams than alternative cuts, and record-closing formulae precede them. This phase asks the strictly stronger predictive question: **do those properties suffice to put the boundaries back?** Each method receives a tablet's line sequence with rulings removed and the true number of segments K, and must place K−1 cuts. This is exactly the label-free chunking problem in agent memory and RAG.

**Lineage stated plainly:** cutting at similarity minima is a TextTiling-family objective (Hearst 1997); exact search over cut positions echoes DP segmentation (Utiyama & Isahara 2001). The contribution is the ground truth — physically drawn record boundaries — and the corpus-derived closer signal as an independent cue, not the objective itself.

Metrics: Pk (Beeferman et al. 1999) and WindowDiff (Pevzner & Hearst 2002), **lower is better**; boundary F1 exact and ±1 line. `random` is the mean of 200 uniform draws. Paired sign tests (two-sided) compare methods per document against both `equal` and `random`, BH-corrected within corpus.

## Administrative

1,717 documents · solver: 1,694 exact, 22 hill-climb, 1 infeasible-fallback

| Method | Pk ↓ | WindowDiff ↓ | F1 exact ↑ | F1 ±1 ↑ |
|---|---:|---:|---:|---:|
| random | 0.405 | 0.407 | 0.097 | 0.269 |
| equal | 0.438 | 0.440 | 0.080 | 0.301 |
| closer | 0.371 | 0.373 | 0.194 | 0.400 |
| overlap_min | 0.454 | 0.456 | 0.018 | 0.061 |
| hybrid | 0.395 | 0.397 | 0.125 | 0.205 |
**Stratified, same-population comparison** — the only fair way to read the closer result: on the 467 documents that contain a closer line, closer Pk = **0.2076** vs random **0.4082** and equal **0.4532** *on those same documents*. On the 1,250 documents with no closer line, the method falls back to equal spacing (Pk 0.4319) and the marker signal simply does not exist — boundary placement there remains unsolved.


| Comparison | wins / losses (Pk) | sign p (two-sided) | BH-adjusted |
|---|---:|---:|---:|
| overlap min vs equal | 756 / 660 | 0.01156 | 0.01387 |
| overlap min vs random | 550 / 1165 | 0.0 | 0.0 |
| closer vs equal | 311 / 62 | 0.0 | 0.0 |
| closer vs random | 815 / 901 | 0.04015 | 0.04015 |
| hybrid vs equal | 844 / 557 | 0.0 | 0.0 |
| hybrid vs random | 757 / 960 | 0.0 | 0.0 |

BH adjustment is across all paired tests within this corpus. The sign test is the corrected two-sided version (an earlier release's implementation saturated at p=1 for methods that LOST most comparisons; see the function docstring).

## Literary

91 documents · solver: 75 exact, 7 hill-climb, 9 infeasible-fallback

| Method | Pk ↓ | WindowDiff ↓ | F1 exact ↑ | F1 ±1 ↑ |
|---|---:|---:|---:|---:|
| random | 0.374 | 0.406 | 0.143 | 0.290 |
| equal | 0.373 | 0.403 | 0.208 | 0.361 |
| closer | 0.369 | 0.400 | 0.203 | 0.367 |
| overlap_min | 0.347 | 0.380 | 0.111 | 0.223 |
| hybrid | 0.349 | 0.383 | 0.115 | 0.242 |
**Stratified, same-population comparison** — the only fair way to read the closer result: on the 5 documents that contain a closer line, closer Pk = **0.3983** vs random **0.4314** and equal **0.4586** *on those same documents*. On the 86 documents with no closer line, the method falls back to equal spacing (Pk 0.3678) and the marker signal simply does not exist — boundary placement there remains unsolved.


| Comparison | wins / losses (Pk) | sign p (two-sided) | BH-adjusted |
|---|---:|---:|---:|
| overlap min vs equal | 44 / 24 | 0.02053 | 0.10674 |
| overlap min vs random | 53 / 37 | 0.11334 | 0.17001 |
| closer vs equal | 1 / 1 | 1.0 | 1.0 |
| closer vs random | 36 / 54 | 0.07255 | 0.1451 |
| hybrid vs equal | 42 / 24 | 0.03558 | 0.10674 |
| hybrid vs random | 52 / 38 | 0.17024 | 0.20429 |

BH adjustment is across all paired tests within this corpus. The sign test is the corrected two-sided version (an earlier release's implementation saturated at p=1 for methods that LOST most comparisons; see the function docstring).

## Markdown (this repo, modern transfer demo)

2 documents · solver: 0 exact, 2 hill-climb, 0 infeasible-fallback

| Method | Pk ↓ | WindowDiff ↓ | F1 exact ↑ | F1 ±1 ↑ |
|---|---:|---:|---:|---:|
| random | 0.471 | 0.501 | 0.103 | 0.259 |
| equal | 0.565 | 0.591 | 0.125 | 0.225 |
| closer | 0.500 | 0.515 | 0.062 | 0.287 |
| overlap_min | 0.535 | 0.575 | 0.125 | 0.225 |
| hybrid | 0.505 | 0.520 | 0.062 | 0.287 |
**Stratified, same-population comparison** — the only fair way to read the closer result: on the 1 documents that contain a closer line, closer Pk = **0.3939** vs random **0.4632** and equal **0.5253** *on those same documents*. On the 1 documents with no closer line, the method falls back to equal spacing (Pk 0.6053) and the marker signal simply does not exist — boundary placement there remains unsolved.


| Comparison | wins / losses (Pk) | sign p (two-sided) | BH-adjusted |
|---|---:|---:|---:|
| overlap min vs equal | 1 / 0 | 1.0 | 1.0 |
| overlap min vs random | 0 / 2 | 0.5 | 1.0 |
| closer vs equal | 1 / 0 | 1.0 | 1.0 |
| closer vs random | 1 / 1 | 1.0 | 1.0 |
| hybrid vs equal | 1 / 0 | 1.0 | 1.0 |
| hybrid vs random | 1 / 1 | 1.0 | 1.0 |

BH adjustment is across all paired tests within this corpus. The sign test is the corrected two-sided version (an earlier release's implementation saturated at p=1 for methods that LOST most comparisons; see the function docstring).

