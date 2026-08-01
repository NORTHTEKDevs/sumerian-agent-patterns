# Phase 3 — Compression & Structural Redundancy Findings
Sample: 2,069 tablets, 5 genres. Shuffles: 1000 for ELS, 20 for compression, 200 for RULING parity.
All claims below cite tablet-corpus-scale stream statistics — individual tablet IDs are in `templates.json`.

---

## 1. Zipfian Glyph-Name Distribution
Classic Zipf predicts exponent s ≈ 1.0 with high R². Deviations indicate either a restricted vocabulary (s > 1, rapid rank falloff, typical of formulaic genres) or a flatter distribution (s < 1, broader vocabulary use, typical of narrative).

| Genre | Stream length | Distinct tokens | Zipf s | R² |
|---|---:|---:|---:|---:|
| Administrative | 32,493 | 962 | 1.746 | 0.9326 |
| Literary | 154,005 | 3,176 | 1.68 | 0.9399 |
| Lexical | 2,508 | 426 | 1.114 | 0.9234 |
| Royal Inscription | 33,015 | 900 | 1.737 | 0.9433 |
| Letter | 18,664 | 780 | 1.607 | 0.9506 |

**Interpretation:** Genres with s substantially > 1 have a *small, high-reuse core vocabulary* — they behave like a DSL with reserved keywords, not a natural language. Administrative and Royal Inscription are the strongest candidates; Literary should be closer to natural-language s ≈ 1.0.

---

## 2. Compression Redundancy (zlib)
`raw_ratio` is compression ratio on the real stream; `shuffled_baseline_ratio` compresses the same tokens in random order. Their difference isolates *structural* redundancy (patterns, not just skewed token frequencies).

| Genre | Raw ratio | Shuffled ratio | Δ (structural) | Stream length |
|---|---:|---:|---:|---:|
| Administrative | 0.215 | 0.3025 | **0.0875** | 32,493 |
| Literary | 0.2632 | 0.3291 | **0.0658** | 154,005 |
| Lexical | 0.3432 | 0.3899 | **0.0467** | 2,508 |
| Royal Inscription | 0.2111 | 0.3102 | **0.0991** | 33,015 |
| Letter | 0.2485 | 0.3234 | **0.0748** | 18,664 |

**Interpretation:** A positive Δ means the actual stream has structural regularities (templates, fixed formulas) beyond what random token order would predict. This is the corpus's 'error-correction overhead' in information-theoretic terms.

---

## 3. Equidistant Letter Sequence (ELS) Scan, Skips 2–100
For each skip k, we decimate the genre stream (take every k-th token) and count how many distinct tokens appear ≥3× in the decimation. Null distribution: 1000 random token permutations, same decimation. z = (observed − null_mean) / null_std.

**Significance criterion:** Bonferroni-corrected p < 0.01/99 ≈ 0.000101 per (genre, skip). This is deliberately strict because with 99 skips × 5 genres = 495 tests, spurious hits are expected.

**Resolution caveat — state this before citing the null.** With 1000 permutations the smallest attainable p-value is 1/(1000+1) ≈ 0.00100, which is about 10× *larger* than the Bonferroni threshold above. This test therefore **cannot** return a Bonferroni-significant result no matter what the data look like; ~9,900 permutations would be needed. The '0 of 495' headline is consequently guaranteed by construction and should not be read as a powered rejection.

The result that *is* informative is the uncorrected one: across 495 tests at a nominal p < 0.01 you would expect ≈5 hits by chance, and that is roughly what appears. No skip, prime or otherwise, stands out above chance expectation. That is genuine evidence against hidden periodic encoding — it is simply weaker, and differently framed, than a Bonferroni claim.

### Administrative
- Total skips tested: 99; skips with p < 0.01: 1; Bonferroni-significant: **0** (of which prime-interval: 0).

*No Bonferroni-significant skips.*


Top-5 by z-score (for reference — not necessarily significant after correction):

| Skip | Prime? | Observed | Null mean | z | p |
|---:|:---:|---:|---:|---:|---:|
| 21 |  | 147 | 133.824 | 2.739 | 0.00599 |
| 31 | Y | 114 | 105.379 | 1.915 | 0.03497 |
| 14 |  | 174 | 164.566 | 1.895 | 0.03996 |
| 44 |  | 89 | 82.577 | 1.478 | 0.08691 |
| 28 |  | 119 | 112.712 | 1.421 | 0.09291 |

### Literary
- Total skips tested: 99; skips with p < 0.01: 1; Bonferroni-significant: **0** (of which prime-interval: 0).

*No Bonferroni-significant skips.*


Top-5 by z-score (for reference — not necessarily significant after correction):

| Skip | Prime? | Observed | Null mean | z | p |
|---:|:---:|---:|---:|---:|---:|
| 98 |  | 134 | 122.075 | 2.515 | 0.00799 |
| 69 |  | 159 | 149.389 | 1.842 | 0.04396 |
| 57 |  | 176 | 166.159 | 1.785 | 0.05395 |
| 19 | Y | 314 | 301.366 | 1.774 | 0.04695 |
| 65 |  | 164 | 154.563 | 1.771 | 0.05794 |

### Lexical
- Total skips tested: 99; skips with p < 0.01: 0; Bonferroni-significant: **0** (of which prime-interval: 0).

*No Bonferroni-significant skips.*


Top-5 by z-score (for reference — not necessarily significant after correction):

| Skip | Prime? | Observed | Null mean | z | p |
|---:|:---:|---:|---:|---:|---:|
| 79 | Y | 2 | 0.419 | 2.5 | 0.06294 |
| 9 |  | 38 | 31.747 | 2.094 | 0.02897 |
| 71 | Y | 2 | 0.56 | 2.085 | 0.08991 |
| 44 |  | 4 | 1.826 | 1.976 | 0.06693 |
| 43 | Y | 4 | 1.927 | 1.765 | 0.0959 |

### Royal Inscription
- Total skips tested: 99; skips with p < 0.01: 0; Bonferroni-significant: **0** (of which prime-interval: 0).

*No Bonferroni-significant skips.*


Top-5 by z-score (for reference — not necessarily significant after correction):

| Skip | Prime? | Observed | Null mean | z | p |
|---:|:---:|---:|---:|---:|---:|
| 76 |  | 56 | 48.412 | 2.217 | 0.02398 |
| 63 |  | 64 | 57.204 | 1.904 | 0.03996 |
| 48 |  | 78 | 71.515 | 1.697 | 0.04795 |
| 36 |  | 95 | 88.093 | 1.687 | 0.05295 |
| 20 |  | 136 | 128.233 | 1.682 | 0.06094 |

### Letter
- Total skips tested: 99; skips with p < 0.01: 1; Bonferroni-significant: **0** (of which prime-interval: 0).

*No Bonferroni-significant skips.*


Top-5 by z-score (for reference — not necessarily significant after correction):

| Skip | Prime? | Observed | Null mean | z | p |
|---:|:---:|---:|---:|---:|---:|
| 33 |  | 66 | 55.067 | 3.146 | 0.002 |
| 44 |  | 51 | 43.761 | 2.296 | 0.01698 |
| 77 |  | 31 | 25.672 | 2.006 | 0.03796 |
| 22 |  | 83 | 75.469 | 1.889 | 0.04396 |
| 21 |  | 84 | 77.856 | 1.476 | 0.07992 |

**Honest interpretation of ELS findings:**
After Bonferroni correction, no skip in [2, 100] shows a non-random ELS signal for any genre. This is the correct null result to expect absent true encoding.

In either case we reject mystical readings — the corpus's periodicities are adequately explained by (a) recurring template formulas and (b) average tablet length when multiple tablets are concatenated in the stream.

---

## 4. Cross-RULING Parity — NULL RESULT (supersedes an earlier positive claim)
**Question:** do `<RULING>` marks fall at content boundaries, or could you cut the tablet anywhere and see the same thing?

**Statistic:** mean shared trigrams between adjacent ruling-delimited chunks. The choice of null *is* the entire experiment:

- **`boundary_permute` (primary).** Keep the real token order and the exact multiset of chunk lengths; permute only *where* the cuts fall. Boundary placement is the only thing that varies, so this isolates the actual question.
- **`token_shuffle` (secondary, shown for contrast).** Pool the tablet's tokens, shuffle, re-cut at the same lengths. This destroys *all* local structure, so it tests "is this text locally coherent at all" — true of any natural language, and uninformative about `<RULING>`.

| Genre | Pairs | Observed | Boundary-permute null | Δ | p (primary) | Token-shuffle null | p (secondary) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Administrative | 17 | 0.176 | 0.343 | -0.167 | **0.78109** | 0.004 | 0.00498 |
| Literary | 108 | 0.731 | 0.889 | -0.158 | **0.90547** | 0.018 | 0.00498 |
| Lexical | 13 | 0.538 | 0.43 | 0.108 | **0.27363** | 0.037 | 0.00498 |
| Royal Inscription | 10 | 0.5 | 0.5 | 0.0 | **1.0** | 0.001 | 0.00498 |
| Letter | 1 | 0.0 | 0.55 | -0.55 | n/a (n=1) | 0.015 | n/a (n=1) |

p-values require at least 5 adjacent-chunk pairs. Even where reported, n is small (Administrative 17, Royal Inscription 10) — these samples could not support a strong claim in either direction.

**Result: null.** Under the control that isolates boundary placement, no genre shows adjacent ruling-delimited chunks sharing more trigrams than arbitrarily placed cuts of the same lengths. Observed values sit *at or below* the boundary-permuted null throughout.

**Correction.** An earlier version of this repository reported this test as significant (Royal p=0.002, Administrative p=0.005) and concluded that `<RULING>` is a validated logical row separator. That result came from the `token_shuffle` null, which — as the two columns above show — inflates the effect by roughly 100× because it destroys the local coherence that any natural-language text has. The p-value was also computed against the pooled distribution of *individual* null pairs rather than the null distribution *of the mean*. Both are corrected here. **The claim is withdrawn: we have no statistical evidence that `<RULING>` marks content boundaries.**

This does not show that `<RULING>` is *meaningless* — a null result on a sample this small is weak evidence either way, and the marks plainly correspond to physical lines drawn by scribes. It shows only that this test does not support the claim, and that the three-tier memory design it was cited to justify should be read as an untested design proposal.

---

## 5. Summary — Implications for Agent Runtimes
- **Genre DSLs are real.** Zipf exponents > 1 in Administrative and Royal Inscription indicate keyword-reuse typical of a domain-specific language, not prose. Memory segments in agent runtimes should preserve genre/schema tags so downstream agents can exploit this.
- **Structural redundancy is measurable.** The positive raw-vs-shuffled Δ gives an empirical 'template coverage' score per genre. Memory compression strategies should target high-template genres with template-aware encoders.
- **ELS is a dead end for cuneiform.** As expected. Useful null-result to cite when future ideas try to decode 'hidden patterns'.
- **RULINGs: no evidence either way.** The earlier positive claim was an artifact of the wrong null and is withdrawn (§4). Treat the three-tier SURFACE/COLUMN/RULING memory design as an untested proposal, not a corpus finding.

**On the two surviving positive results.** Both §1 (Zipf) and §2 (compression Δ) are descriptive statistics against a shuffled-token baseline. They establish that these genres are more formulaic than random token order — they do not establish that the corpus is a 'DSL' in any formal sense. That word is an analogy, not a result.
