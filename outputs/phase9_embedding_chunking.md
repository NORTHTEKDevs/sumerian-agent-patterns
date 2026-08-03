# Phase 9 — Embedding-based chunking on the Sumerian ground truth

PAPER.md v1.1 scoped Phase 8's negative result to the *lexical* instantiation of the similarity signal and named embedding-based chunking as the obvious next experiment. This is that experiment: a 2×2 crossing **representation** (trigram vs dense embedding, `nomic-embed-text`, 768-d, served locally) with **algorithm** (local valley cutting — the method practitioners call semantic chunking, adapted to known K — vs global adjacent-similarity minimisation), plus a within-tablet **shuffled-embedding control** that any legitimate embedding method must fail against.

> **Out-of-distribution caveat, before any number.** No published embedding model is trained on Sumerian transliteration. For text this far outside the training distribution, dense embeddings cannot be assumed to encode meaning; the pre-registered hypothesis (H1, in the script header) was that they act as fuzzy lexical matchers here. This experiment tests semantic-chunking *machinery* on this ground truth, not embedding *understanding* of Sumerian — in-distribution behaviour on modern text could differ.

## Administrative

1,717 tablets · emb_global solver: 1,694 exact, 22 hill-climb, 1 fallback · valley feasibility fallbacks: {'lex_valley': 1, 'emb_valley': 1, 'shuffled_control': 2}

| Method | Pk ↓ | WindowDiff ↓ | F1 exact ↑ | F1 ±1 ↑ |
|---|---:|---:|---:|---:|
| random | 0.405 | 0.407 | 0.097 | 0.269 |
| equal | 0.438 | 0.440 | 0.080 | 0.301 |
| closer | 0.371 | 0.373 | 0.194 | 0.400 |
| lex_valley | 0.454 | 0.455 | 0.014 | 0.041 |
| emb_valley | 0.381 | 0.384 | 0.117 | 0.302 |
| emb_global | 0.370 | 0.375 | 0.084 | 0.221 |
| shuffled_control | 0.406 | 0.408 | 0.082 | 0.241 |
**Markerless stratum (1,250 tablets — where the closer cue cannot exist):** random Pk 0.4028, emb_global **0.3681** (vs-random paired 662/584, BH p = 0.04367), emb_valley 0.3789 (BH p = 0.75534), lex_valley 0.4525.


| Comparison | wins / losses (Pk) | sign p (two-sided) | BH |
|---|---:|---:|---:|
| lex valley vs random | 559 / 1152 | 0.0 | 0.0 |
| lex valley vs closer | 657 / 835 | 0.0 | 0.0 |
| emb valley vs random | 827 / 884 | 0.17577 | 0.22599 |
| emb valley vs closer | 636 / 625 | 0.77826 | 0.77826 |
| emb global vs random | 872 / 839 | 0.43917 | 0.49407 |
| emb global vs closer | 787 / 713 | 0.05941 | 0.10413 |
| shuffled control vs random | 748 / 965 | 0.0 | 0.0 |
| shuffled control vs closer | 608 / 674 | 0.06942 | 0.10413 |
| emb valley vs lex valley | 717 / 480 | 0.0 | 0.0 |

## Literary

91 tablets · emb_global solver: 75 exact, 7 hill-climb, 9 fallback · valley feasibility fallbacks: {'lex_valley': 9, 'emb_valley': 9, 'shuffled_control': 9}

| Method | Pk ↓ | WindowDiff ↓ | F1 exact ↑ | F1 ±1 ↑ |
|---|---:|---:|---:|---:|
| random | 0.374 | 0.405 | 0.142 | 0.288 |
| equal | 0.373 | 0.403 | 0.208 | 0.361 |
| closer | 0.369 | 0.400 | 0.203 | 0.367 |
| lex_valley | 0.336 | 0.381 | 0.107 | 0.223 |
| emb_valley | 0.347 | 0.383 | 0.175 | 0.368 |
| emb_global | 0.288 | 0.327 | 0.193 | 0.407 |
| shuffled_control | 0.379 | 0.412 | 0.151 | 0.251 |
**Markerless stratum (86 tablets — where the closer cue cannot exist):** random Pk 0.3719, emb_global **0.2858** (vs-random paired 59/26, BH p = 0.00135), emb_valley 0.3367 (BH p = 0.45055), lex_valley 0.3339.


| Comparison | wins / losses (Pk) | sign p (two-sided) | BH |
|---|---:|---:|---:|
| lex valley vs random | 57 / 34 | 0.02058 | 0.06174 |
| lex valley vs closer | 48 / 28 | 0.02863 | 0.06442 |
| emb valley vs random | 49 / 42 | 0.5296 | 0.5958 |
| emb valley vs closer | 38 / 27 | 0.21454 | 0.38617 |
| emb global vs random | 63 / 27 | 0.00019 | 0.00171 |
| emb global vs closer | 51 / 22 | 0.00091 | 0.00409 |
| shuffled control vs random | 40 / 51 | 0.29447 | 0.44032 |
| shuffled control vs closer | 33 / 30 | 0.80131 | 0.80131 |
| emb valley vs lex valley | 31 / 40 | 0.34247 | 0.44032 |

## Conclusions against the pre-registered expectations

- **H1 (embeddings ≈ lexical OOD): DID NOT HOLD.** emb_valley Pk 0.381 vs lex_valley 0.454 (paired: 717 / 480, BH p = 0.0).
- **H2 (nothing approaches the closer cue): NUANCED.** On aggregate means the best embedding method (0.370) matches fallback-diluted aggregate closer (0.371), but the honest closer number is its stratified Pk 0.208 on marker-bearing tablets, which nothing here approaches. The embedding methods' aggregate mean advantage over random is NOT significant on paired tests (see below), so H2 stands for marker-bearing text and is untested-at-significance elsewhere.
- **H3 (local valleys beat the global objective): DID NOT HOLD for embeddings.** emb_global 0.370 has the better mean vs emb_valley 0.381. Length-normalised centroids remove the degenerate-mass incentive that broke the raw-count global objective, which is the likely reason the global form works with embeddings but not with raw trigram counts.
- **Embeddings vs chance — the caution that survives:** better MEANS (emb_valley 0.381, emb_global 0.370 vs random 0.405) but NEITHER is significant on the paired test (emb_valley 827/884, BH p = 0.22599; emb_global 872/839, BH p = 0.49407). The mean gain comes from a minority of tablets with large improvements — embeddings help substantially where they help at all, and not at all elsewhere. The significant result is the twin comparison: embeddings beat the identical lexical algorithm decisively.
- **Shuffled-embedding control:** Pk 0.406 vs random 0.405 — collapses to chance as required; the emb results reflect embedding content.
