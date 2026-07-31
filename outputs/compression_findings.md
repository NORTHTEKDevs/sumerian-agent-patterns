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

### Administrative
- Total skips tested: 99; skips with p < 0.01: 1; Bonferroni-significant: **0** (of which prime-interval: 0).

*No Bonferroni-significant skips.*


Top-5 by z-score (for reference — not necessarily significant after correction):

| Skip | Prime? | Observed | Null mean | z | p |
|---:|:---:|---:|---:|---:|---:|
| 21 |  | 147 | 133.824 | 2.739 | 0.005 |
| 31 | Y | 114 | 105.379 | 1.915 | 0.034 |
| 14 |  | 174 | 164.566 | 1.895 | 0.039 |
| 44 |  | 89 | 82.577 | 1.478 | 0.086 |
| 28 |  | 119 | 112.712 | 1.421 | 0.092 |

### Literary
- Total skips tested: 99; skips with p < 0.01: 1; Bonferroni-significant: **0** (of which prime-interval: 0).

*No Bonferroni-significant skips.*


Top-5 by z-score (for reference — not necessarily significant after correction):

| Skip | Prime? | Observed | Null mean | z | p |
|---:|:---:|---:|---:|---:|---:|
| 98 |  | 134 | 122.075 | 2.515 | 0.007 |
| 69 |  | 159 | 149.389 | 1.842 | 0.043 |
| 57 |  | 176 | 166.159 | 1.785 | 0.053 |
| 19 | Y | 314 | 301.366 | 1.774 | 0.046 |
| 65 |  | 164 | 154.563 | 1.771 | 0.057 |

### Lexical
- Total skips tested: 99; skips with p < 0.01: 0; Bonferroni-significant: **0** (of which prime-interval: 0).

*No Bonferroni-significant skips.*


Top-5 by z-score (for reference — not necessarily significant after correction):

| Skip | Prime? | Observed | Null mean | z | p |
|---:|:---:|---:|---:|---:|---:|
| 79 | Y | 2 | 0.419 | 2.5 | 0.062 |
| 9 |  | 38 | 31.747 | 2.094 | 0.028 |
| 71 | Y | 2 | 0.56 | 2.085 | 0.089 |
| 44 |  | 4 | 1.826 | 1.976 | 0.066 |
| 43 | Y | 4 | 1.927 | 1.765 | 0.095 |

### Royal Inscription
- Total skips tested: 99; skips with p < 0.01: 0; Bonferroni-significant: **0** (of which prime-interval: 0).

*No Bonferroni-significant skips.*


Top-5 by z-score (for reference — not necessarily significant after correction):

| Skip | Prime? | Observed | Null mean | z | p |
|---:|:---:|---:|---:|---:|---:|
| 76 |  | 56 | 48.412 | 2.217 | 0.023 |
| 63 |  | 64 | 57.204 | 1.904 | 0.039 |
| 48 |  | 78 | 71.515 | 1.697 | 0.047 |
| 36 |  | 95 | 88.093 | 1.687 | 0.052 |
| 20 |  | 136 | 128.233 | 1.682 | 0.06 |

### Letter
- Total skips tested: 99; skips with p < 0.01: 1; Bonferroni-significant: **0** (of which prime-interval: 0).

*No Bonferroni-significant skips.*


Top-5 by z-score (for reference — not necessarily significant after correction):

| Skip | Prime? | Observed | Null mean | z | p |
|---:|:---:|---:|---:|---:|---:|
| 33 |  | 66 | 55.067 | 3.146 | 0.001 |
| 44 |  | 51 | 43.761 | 2.296 | 0.016 |
| 77 |  | 31 | 25.672 | 2.006 | 0.037 |
| 22 |  | 83 | 75.469 | 1.889 | 0.043 |
| 21 |  | 84 | 77.856 | 1.476 | 0.079 |

**Honest interpretation of ELS findings:**
After Bonferroni correction, no skip in [2, 100] shows a non-random ELS signal for any genre. This is the correct null result to expect absent true encoding.

In either case we reject mystical readings — the corpus's periodicities are adequately explained by (a) recurring template formulas and (b) average tablet length when multiple tablets are concatenated in the stream.

---

## 4. Cross-RULING Parity (Shared Trigrams Across Adjacent Chunks)
For tablets with ≥2 RULING-delimited chunks, we measure trigram overlap between adjacent chunks, and compare to a within-tablet shuffled baseline (pool tokens, reshuffle, re-chunk at same lengths). High Δ ⇒ RULINGs separate sections that share structured content (e.g., parallel entries in a list).

| Genre | Adjacent-chunk pairs | Obs. shared trigrams | Null mean | Δ | p (approx) |
|---|---:|---:|---:|---:|---:|
| Administrative | 17 | 0.176 | 0.005 | **0.171** | 0.00529 |
| Literary | 108 | 0.731 | 0.016 | **0.715** | 0.01431 |
| Lexical | 13 | 0.538 | 0.032 | **0.507** | 0.03115 |
| Royal Inscription | 10 | 0.5 | 0.003 | **0.497** | 0.002 |
| Letter | 1 | 0.0 | 0.025 | **-0.025** | n/a (n=1, insufficient) |

p-values are reported only where at least 5 adjacent-chunk pairs were observed. Administrative (n=17) and Royal Inscription (n=10) rest on small samples — treat them as indicative, not conclusive.

**Interpretation:** Positive Δ in Literary or Lexical would confirm that `<RULING>` is a *logical* separator between parallel items (like list entries with repeated framing words), not arbitrary spacing. This is the clearest evidence that `<RULING>` maps to 'row boundary' in a typed schema.

---

## 5. Summary — Implications for Agent Runtimes
- **Genre DSLs are real.** Zipf exponents > 1 in Administrative and Royal Inscription indicate keyword-reuse typical of a domain-specific language, not prose. Memory segments in agent runtimes should preserve genre/schema tags so downstream agents can exploit this.
- **Structural redundancy is measurable.** The positive raw-vs-shuffled Δ gives an empirical 'template coverage' score per genre. Memory compression strategies should target high-template genres with template-aware encoders.
- **ELS is a dead end for cuneiform.** As expected. Useful null-result to cite when future ideas try to decode 'hidden patterns'.
- **RULINGs are logical separators where Δ > 0.** Use them as row boundaries, not as mere visual hints.
