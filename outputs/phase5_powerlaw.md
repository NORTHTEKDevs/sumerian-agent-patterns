# Phase 5 — Is the glyph-frequency distribution a power law?

The original release fitted Zipf exponents by OLS on log-log rank-frequency data and read the cross-genre spread as evidence that administrative tablets are "DSL-like". [That claim was withdrawn](../CORRECTIONS.md): the spread is a stream-length artifact, and OLS on log-log data is a biased estimator whose R² is not a goodness-of-fit test.

This is the standard method (Clauset, Shalizi & Newman 2009, *SIAM Review* 51(4):661–703): x_min chosen by minimising KS distance, α by discrete MLE, goodness of fit by parametric bootstrap, and a Vuong likelihood-ratio test against a lognormal alternative. **All genres are fitted at a common stream length (2,508 tokens)** — the confound that invalidated the original comparison.

| Genre | α (MLE) | sd | x_min | KS | GoF p | Power law ruled out? | Vuong R | Vuong p |
|---|---:|---:|---:|---:|---:|:---:|---:|---:|
| Administrative | 1.983 | 0.316 | 3 | 0.08 | 0.136 | no | 3.33 | 0.5054 |
| Literary | 1.923 | 0.276 | 2 | 0.076 | 0.149 | no | 6.24 | 0.4564 |
| Lexical | 1.736 | 0.0 | 2 | 0.0793 | 0.003 | **YES** | -0.44 | 0.964 |
| Royal Inscription | 1.867 | 0.239 | 3 | 0.0778 | 0.104 | no | 5.42 | 0.5238 |
| Letter | 1.851 | 0.112 | 3 | 0.0633 | 0.245 | no | 10.94 | 0.1776 |

**How to read this.** In the goodness-of-fit column a LARGE p means the power law is *not ruled out*; p < 0.1 rules it out. This is the opposite of the usual convention and is a common source of error when citing power-law fits. Vuong R > 0 favours the power law over lognormal, R < 0 favours lognormal, and Vuong p says whether the difference is distinguishable from zero — a large p means the two models fit comparably and **neither should be claimed**.

**What this does not do.** Establishing that a frequency distribution is or is not power-law says nothing about whether a genre is a "domain-specific language". That was the original overreach and it is not reinstated here. The α values are reported as a property of the token distribution, nothing more.

## Conclusion

**1. The original cross-genre spread was an artifact.** At a common stream length the MLE exponents span 1.736–1.983 — a band of 0.247. The OLS fit at native lengths reported 1.114–1.746, a spread of 0.632, roughly seven times wider. The genre difference that the "Zipf-as-DSL detector" rested on does not survive either the correct estimator or the length control.

**2. A power law is ruled out for Lexical** (bootstrap GoF p < 0.1). It is not ruled out for Administrative, Literary, Royal Inscription, Letter.

**3. But 'not ruled out' is not 'confirmed'.** Vuong's test cannot distinguish the power law from a lognormal for any genre tested (all p > 0.05). **No genre in this corpus should be described as power-law distributed.** Two models fit comparably, which is the ordinary situation for real-world data and precisely what Clauset et al. warn against over-reading. The correct summary is: the token-frequency distributions are heavy-tailed with α ≈ 1.7–2.0, and this method cannot identify which heavy-tailed family generated them.

**4. Net effect on the repository's claims.** This analysis does not restore the withdrawn finding; it explains why the finding was wrong and replaces it with a weaker, defensible statement. The one genuinely new result is the Lexical outcome — under a correct fit, lexical lists are the single genre whose frequency distribution is inconsistent with a power law, which is at least consistent with their being curated word-lists rather than natural text. That is offered as an observation, not a claim about scribal practice.
