# Phase 12 — Unknown K: methods must decide how many cuts, not just where

Phases 8–11 gave every method the true segment count (the standard known-K evaluation, flagged in PAPER §8 as a generosity). Here the oracle is removed. `marker_K` cuts after every marker run and thereby *estimates K from the markers*; `emb_thresh`/`lex_thresh` cut where a document's own gap scores exceed mean + 0.5·sd (the sign-flipped analogue of TextTiling's original criterion, fixed a priori); `length_prior` cuts every L lines with L learned as the median record length on a held-out half of each corpus. `oracle_random` and `oracle_equal` keep the true K and are labelled as the oracle references they are. Boundary-count error is reported directly (K MAE / bias).

## Administrative tablets

858 evaluation documents (held-out split) · length prior L = 6

| Method | Pk ↓ | WindowDiff ↓ | K MAE | K bias |
|---|---:|---:|---:|---:|
| oracle_random *(oracle K)* | 0.407 | 0.409 | 0.0 | +0.0 |
| oracle_equal *(oracle K)* | 0.440 | 0.441 | 0.0 | +0.0 |
| marker_K | 0.270 | 0.271 | 1.04 | -0.909 |
| emb_thresh | 0.518 | 0.601 | 3.682 | +3.677 |
| lex_thresh | 0.312 | 0.323 | 1.903 | -0.5 |
| length_prior | 0.445 | 0.458 | 1.231 | +1.079 |

| Comparison | wins/losses | sign p | BH |
|---|---:|---:|---:|
| marker K vs oracle random | 798/60 | 0.0 | 0.0 |
| emb thresh vs oracle random | 256/602 | 0.0 | 0.0 |
| lex thresh vs oracle random | 810/48 | 0.0 | 0.0 |
| length prior vs oracle random | 341/517 | 0.0 | 0.0 |

Marker-bearing stratum (224): marker_K Pk **0.2111** vs oracle-random 0.4106 (172/52, p = 0.0), K MAE 0.326.

## git/git (trailer-rich)

150 evaluation documents (held-out split) · length prior L = 8

| Method | Pk ↓ | WindowDiff ↓ | K MAE | K bias |
|---|---:|---:|---:|---:|
| oracle_random *(oracle K)* | 0.463 | 0.481 | 0.0 | +0.0 |
| oracle_equal *(oracle K)* | 0.420 | 0.426 | 0.0 | +0.0 |
| marker_K | 0.120 | 0.129 | 0.96 | -0.853 |
| emb_thresh | 0.473 | 0.700 | 9.813 | +9.8 |
| lex_thresh | 0.400 | 0.410 | 3.26 | -2.393 |
| length_prior | 0.512 | 0.532 | 2.08 | +1.693 |

| Comparison | wins/losses | sign p | BH |
|---|---:|---:|---:|
| marker K vs oracle random | 147/3 | 0.0 | 0.0 |
| emb thresh vs oracle random | 63/87 | 0.06003 | 0.06003 |
| lex thresh vs oracle random | 141/9 | 0.0 | 0.0 |
| length prior vs oracle random | 48/102 | 1e-05 | 1e-05 |

Marker-bearing stratum (132): marker_K Pk **0.0801** vs oracle-random 0.4626 (132/0, p = 0.0), K MAE 0.697.

## express (markerless)

150 evaluation documents (held-out split) · length prior L = 2

| Method | Pk ↓ | WindowDiff ↓ | K MAE | K bias |
|---|---:|---:|---:|---:|
| oracle_random *(oracle K)* | 0.243 | 0.545 | 0.0 | +0.0 |
| oracle_equal *(oracle K)* | 0.180 | 0.505 | 0.0 | +0.0 |
| marker_K | 0.786 | 0.791 | 3.34 | -3.327 |
| emb_thresh | 0.470 | 0.654 | 1.567 | -1.233 |
| lex_thresh | 0.750 | 0.779 | 3.26 | -2.993 |
| length_prior | 0.186 | 0.494 | 1.173 | -0.36 |

| Comparison | wins/losses | sign p | BH |
|---|---:|---:|---:|
| marker K vs oracle random | 15/135 | 0.0 | 0.0 |
| emb thresh vs oracle random | 40/107 | 0.0 | 0.0 |
| lex thresh vs oracle random | 14/134 | 0.0 | 0.0 |
| length prior vs oracle random | 106/14 | 0.0 | 0.0 |

## Pre-registered verdicts

| Criterion | Held? |
|---|:---:|
| U1 — markers beat all non-marker methods AND estimate K with MAE < 1 (marker-rich corpora) | **YES** |
| U2 — known-K→unknown-K degradation quantified for valley methods (see tables vs phases 9/11) | **YES** |
| U3 — markerless corpus: no unknown-K method beats oracle-K random | **NO** |

**Criterion disclosure (U1).** As pre-registered, U1 said 'MAE < 1' without specifying aggregate or stratum. The verdict uses the marker-bearing stratum (the population the claim concerns; tablets 0.326, git/git 0.697). Under the literal aggregate reading the tablet corpus narrowly fails (MAE 1.04, driven by markerless tablets where the method emits zero cuts). Both readings are reported; the ambiguity was ours and is disclosed rather than resolved silently in our favour. A related population mismatch, same treatment: the U1 Pk comparison sets the stratified marker Pk against competitors' aggregate Pk (per-method stratified competitor numbers are not computed); the aggregate-vs-aggregate comparison in the main table shows the same ordering, which is why the verdict stands, but the cleaner stratified-vs-stratified design is noted for any replication.

The headline consequence, if U1 held: under unknown K the marker cue's advantage *widens*, because markers answer the question every other method now has to guess — how many records there are. Engineered delimiters supply count and placement in one mechanism.
