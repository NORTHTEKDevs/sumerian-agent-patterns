# Phase 11 — In-distribution modern text: git commit histories as record streams

The Sumerian results carried a standing scope limit: every encoder was out-of-distribution. This phase reruns the full evaluation on modern English record streams where the encoder is in-distribution — non-overlapping windows of consecutive commit messages (boundaries defined by the VCS, commit headers stripped so nothing hands the boundary to any method), from two public repositories chosen for the marker contrast: **git/git**, whose convention closes nearly every record with attribution trailers (`Signed-off-by:` — the modern *šu ba-ti*), and **expressjs/express**, effectively markerless. Pinned to `--until=2026-01-01`; reproducible with two blobless clones.

## git/git (trailer-rich)

300 documents · 263 contain trailer lines · solver: {'exact': 272, 'greedy': 28, 'fallback': 0}

| Method | Pk ↓ | F1 ±1 ↑ |
|---|---:|---:|
| random | 0.465 | 0.244 |
| equal | 0.425 | 0.337 |
| closer | 0.267 | 0.508 |
| lex_valley | 0.439 | 0.110 |
| emb_valley | 0.350 | 0.382 |
| emb_global | 0.461 | 0.088 |
| shuffled_control | 0.460 | 0.196 |

| Comparison | wins/losses | sign p | BH |
|---|---:|---:|---:|
| closer vs random | 273/27 | 0.0 | 0.0 |
| lex valley vs random | 156/144 | 0.52544 | 0.70398 |
| emb valley vs random | 230/70 | 0.0 | 0.0 |
| emb global vs random | 145/155 | 0.60341 | 0.70398 |
| emb valley vs lex valley | 199/87 | 0.0 | 0.0 |
| equal vs random | 172/128 | 0.01291 | 0.02259 |
| shuffled control vs random | 149/151 | 0.95397 | 0.95397 |

Trailer-bearing stratum (263): closer 0.2517 vs random 0.4636 (250/13, p = 0.0).

## express (markerless)

300 documents · 32 contain trailer lines · solver: {'exact': 217, 'greedy': 0, 'fallback': 83}

| Method | Pk ↓ | F1 ±1 ↑ |
|---|---:|---:|
| random | 0.246 | 0.804 |
| equal | 0.196 | 0.860 |
| closer | 0.187 | 0.873 |
| lex_valley | 0.254 | 0.763 |
| emb_valley | 0.241 | 0.792 |
| emb_global | 0.232 | 0.812 |
| shuffled_control | 0.255 | 0.765 |

| Comparison | wins/losses | sign p | BH |
|---|---:|---:|---:|
| closer vs random | 198/36 | 0.0 | 0.0 |
| lex valley vs random | 124/121 | 0.89836 | 0.89836 |
| emb valley vs random | 138/110 | 0.08623 | 0.1509 |
| emb global vs random | 144/90 | 0.0005 | 0.00117 |
| emb valley vs lex valley | 70/63 | 0.60305 | 0.70356 |
| equal vs random | 192/42 | 0.0 | 0.0 |
| shuffled control vs random | 132/113 | 0.2501 | 0.35014 |

Trailer-bearing stratum (32): closer 0.247 vs random 0.3494 (21/9, p = 0.04277).

## Pre-registered verdicts

| Criterion | Held? |
|---|:---:|
| M1 — trailer cue dominates in git/git (stratified, p < 0.05) | **YES** |
| M2 — embeddings beat the lexical twin in BOTH repos (BH < 0.05) | **NO** |
| M3 — markerless repo: emb_global beats random (BH < 0.05) | **YES** |
| M4 — fixed-size worse than random in BOTH repos | **NO** |
| M5 — shuffled control collapses in BOTH repos | **YES** |

**3 of 5 pre-registered criteria held.** Each is reported under the criterion as fixed before the run.
