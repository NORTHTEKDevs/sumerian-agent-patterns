# Phase 13 — The dispersion curve: when is fixed-size chunking worse than random?

Phase 11 retracted "fixed-size is worse than random" as a general claim and proposed the mechanism: the result is about **record-length dispersion**. This phase measures the curve across six corpora with real boundaries — two Sumerian genres and four commit-stream corpora spanning message-culture styles. Gap = mean equal Pk − mean random Pk under known K; positive gap means fixed-size is worse than random.

| Corpus | Docs | Records | Record-length CV | equal Pk | random Pk | Gap | equal worse? | sign p |
|---|---:|---:|---:|---:|---:|---:|:---:|---:|
| git/git commits | 300 | 1,177 | 0.902 | 0.429 | 0.465 | -0.0357 | no | 0.27263 |
| curl/curl commits | 300 | 1,210 | 1.143 | 0.448 | 0.462 | -0.0131 | no | 0.29788 |
| Administrative tablets | 1,717 | 3,806 | 1.389 | 0.438 | 0.405 | +0.0327 | yes | 0.0 |
| prettier commits | 300 | 1,251 | 1.478 | 0.233 | 0.335 | -0.1013 | no | 0.0 |
| express commits | 300 | 1,335 | 1.755 | 0.186 | 0.243 | -0.0572 | no | 0.0 |
| Literary tablets | 91 | 326 | 2.086 | 0.373 | 0.372 | +0.0005 | yes | 0.0446 |

**Spearman rank correlation (gap vs. CV): rho = -0.029, exact two-sided p = 1.00000** over 6 corpora.

The gap changes sign **3 time(s)** along the CV ordering — multiple crossings are themselves evidence against any monotone dispersion mechanism: between curl/curl commits (CV 1.143) and Administrative tablets (CV 1.389); between Administrative tablets (CV 1.389) and prettier commits (CV 1.478); between express commits (CV 1.755) and Literary tablets (CV 2.086).

## Pre-registered verdict

- **D1 (gap increases with record-length CV): DID NOT HOLD** (rho = -0.029, p = 1.00000).

With six corpora the correlation has limited power and the exact permutation p is the honest test; the per-corpus paired sign tests carry the within-corpus weight. If D1 held, the practical reading is: measure your records' length CV before choosing fixed-size chunking — above the flip region, cutting at random is literally better than cutting evenly.
