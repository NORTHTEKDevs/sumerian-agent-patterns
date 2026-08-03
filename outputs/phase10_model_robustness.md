# Phase 10 — Second-encoder robustness of the embedding result

Phase 9 used one encoder (nomic-embed-text, monolingual BERT lineage, 137M). This reruns the decisive comparisons with **bge-m3** (BAAI, XLM-RoBERTa lineage, multilingual pretraining, 1024-d) — architecturally and training-distributionally distinct. Replication criteria were fixed in the script header before the run; partial agreement counts as NOT replicated.

## Administrative

1,717 tablets

| Method | Pk (bge-m3) | Pk (nomic, phase 9) |
|---|---:|---:|
| random | 0.405 | 0.4045 |
| closer | 0.371 | 0.3709 |
| lex_valley | 0.454 | 0.4537 |
| emb_valley | 0.380 | 0.3808 |
| emb_global | 0.374 | 0.37 |
| shuffled_control | 0.408 | 0.4055 |

| Comparison | wins/losses | sign p | BH |
|---|---:|---:|---:|
| emb valley vs lex valley | 716/460 | 0.0 | 0.0 |
| emb valley vs random | 847/868 | 0.62915 | 0.71697 |
| emb global vs random | 864/848 | 0.71697 | 0.71697 |
| shuffled control vs random | 736/978 | 0.0 | 0.0 |

Markerless stratum (1,250): emb_global 0.3644 vs random 0.4028 (682/565, p = 0.00101).

## Literary

91 tablets

| Method | Pk (bge-m3) | Pk (nomic, phase 9) |
|---|---:|---:|
| random | 0.374 | 0.374 |
| closer | 0.369 | 0.3695 |
| lex_valley | 0.336 | 0.3358 |
| emb_valley | 0.359 | 0.3466 |
| emb_global | 0.276 | 0.2882 |
| shuffled_control | 0.357 | 0.3788 |

| Comparison | wins/losses | sign p | BH |
|---|---:|---:|---:|
| emb valley vs lex valley | 28/41 | 0.14803 | 0.29606 |
| emb valley vs random | 44/47 | 0.83408 | 0.83408 |
| emb global vs random | 66/24 | 1e-05 | 4e-05 |
| shuffled control vs random | 48/43 | 0.67522 | 0.83408 |

Markerless stratum (86): emb_global 0.2745 vs random 0.3719 (62/23, p = 3e-05).

## Replication verdicts (criteria fixed before the run)

| Criterion | Replicated with bge-m3? |
|---|:---:|
| R1 — embeddings beat the lexical twin (paired, BH < 0.05) | **YES** |
| R2 — emb_global beats random on the markerless Administrative stratum (p < 0.05) | **YES** |
| R3 — shuffled-embedding control collapses to chance | **YES** |
| R4 — global objective ≤ valley objective (mean Pk) | **YES** |

**4 of 4 criteria replicated.** Whichever way each verdict fell, it is reported under the pre-stated criterion; no criterion was adjusted after seeing the data.
