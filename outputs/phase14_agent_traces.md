# Phase 14 — Real agent traces (bring your own data)

The corpus every earlier phase has been an analogy for: tool-call interactions from real agent sessions, boundaries defined by transcript structure. **Privacy model:** transcripts never leave the machine (local embedding model), and only aggregate metrics are published; the script asserts no document line appears in its output. Reproduce on your own sessions with `--transcripts-dir`.

Author's run: **200 documents**, record-length CV **0.812**.

## Raw traces (markerless, as agents emit them today)

| Method | Pk ↓ | F1 ±1 ↑ |
|---|---:|---:|
| random | 0.471 | 0.313 |
| equal | 0.383 | 0.497 |
| lex_valley | 0.454 | 0.262 |
| emb_valley | 0.463 | 0.343 |
| emb_global | 0.475 | 0.187 |

| Comparison | wins/losses | sign p | BH |
|---|---:|---:|---:|
| equal vs random | 124/76 | 0.00085 | 0.0034 |
| lex valley vs random | 102/98 | 0.83207 | 0.83207 |
| emb valley vs random | 98/102 | 0.83207 | 0.83207 |
| emb global vs random | 91/109 | 0.22925 | 0.4585 |

## Engineered condition (one delimiter line appended per record)

| Method | Pk ↓ | F1 ±1 ↑ |
|---|---:|---:|
| random | 0.471 | 0.272 |
| equal | 0.359 | 0.471 |
| lex_valley | 0.466 | 0.197 |
| emb_valley | 0.431 | 0.388 |
| emb_global | 0.488 | 0.151 |
| closer | 0.000 | 1.000 |
| marker_K_unknownK | 0.000 | 1.000 |

| Comparison | wins/losses | sign p | BH |
|---|---:|---:|---:|
| equal vs random | 132/68 | 1e-05 | 2e-05 |
| lex valley vs random | 91/109 | 0.22925 | 0.22925 |
| emb valley vs random | 117/83 | 0.0194 | 0.0291 |
| emb global vs random | 85/115 | 0.04004 | 0.04805 |
| closer vs random | 200/0 | 0.0 | 0.0 |
| marker K unknownK vs random | 200/0 | 0.0 | 0.0 |

## Pre-registered verdicts

- **T1 (some embedding method beats random on raw traces): DID NOT HOLD.**
- **T2 (engineered delimiter closes the problem, closer Pk < 0.1): HELD** — by construction, labelled a demonstration: the informative quantity is the gap it opens over every post-hoc method on the same documents.
- **T3 (dispersion curve predicts the fixed-size sign): VOID.** Phase 13 refuted the mechanism this prediction was drawn from (rho = −0.03 across six corpora) before T3 could be evaluated, so the criterion has no evidential standing in either direction. For the record: measured CV 0.812, predicted no_prediction, observed equal_better.

**Corpus-freezing note.** The first two runs of this script saw different corpora (CV 0.667 then 0.726) because the transcript directory is live and grew between runs — including from the session developing this experiment. Documents are now frozen to a local cache at first parse; the published numbers come from the frozen snapshot.
