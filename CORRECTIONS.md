# Corrections

A running, dated log of claims this repository has retracted or materially revised. Newest first.

Nothing is removed from the record. Superseded claims stay visible with the reason they failed, so anyone who read or cited an earlier version can see exactly what changed.

---

## 2026-08-05 — WITHDRAWN: "the fixed-size reversal is explained by record-length dispersion"

**Affected:** PAPER v1.4 abstract and §6.6 (published in v0.6.0), which retracted "fixed-size is
worse than random" and proposed record-length dispersion as the mechanism for why the result
reversed between tablets and commit streams.

**Status: the proposed mechanism is withdrawn.** The reversal itself stands; our explanation of
it does not. A pre-registered test (Phase 13) measured the equal-vs-random Pk gap against
record-length CV across six corpora with real boundaries. Prediction: gap increases with CV.
Result: Spearman rho = −0.029, exact permutation p = 1.0. Two corpora with *high* CV (express
1.755, prettier 1.478) show fixed-size clearly *better* than random. What survives is a
corpus-family regularity — both tablet genres show equal ≥ random, all four commit corpora the
opposite — whose cause we leave open rather than proposing a second untested mechanism.

This is the first correction of a correction in this log: the v0.6.0 rescope was itself too
confident about *why*. (An earlier wording here also miscounted a post-hoc observation — the
similarity-algorithm reversal — among the pre-registered failures; the accurate tally of failed
pre-registered criteria at this entry's date is M2, M4, U3, D1. T1 — embeddings-beat-random on
raw agent traces — also failed the same day, for an unrelated root cause: a live, growing trace
corpus, documented in Phase 14, not anything to do with dispersion. It is listed here only for
tally completeness.) A metric caveat verified after review: express's equal-beats-random reversal
is decisive under paired Pk but a coin flip under paired WindowDiff; the corpus-family claim
therefore rests on git/git (replicates under both metrics) and prettier, with express
Pk-supported only.
See [`outputs/phase13_dispersion.md`](outputs/phase13_dispersion.md).

---

## 2026-08-01 — RESOLVED: the RULING question, answered at full corpus scale

The RULING claim was withdrawn on 2026-07-31 (below) for using an invalid null, and the corrected test returned a null result — but on only 10–17 adjacent chunk pairs per genre, which cannot settle the question in either direction. **A withdrawal on an underpowered test is not an answer, so the question was reopened and tested properly.**

`scripts/phase4_ruling_fullcorpus.py` runs it on the full corpus rather than a 500-per-genre sample: 2,095 adjacent pairs for Administrative instead of 17 (a 123× increase), 10,000 permutations, two independent nulls, bootstrap CIs, and Benjamini–Hochberg correction across genres.

**Result: there is a significant effect, and it runs in the opposite direction to the original claim.**

| Genre | Pairs | Observed | Null A (length permute) | Δ | BH p (2-sided) |
|---|---:|---:|---:|---:|---:|
| Administrative | 2,095 | 1.1881 | 1.5165 | **−0.328** | **0.0006** |
| Literary | 248 | 1.1694 | 1.4251 | −0.256 | 0.278 |
| Royal Inscription | 64 | 1.2812 | 1.5235 | −0.242 | 0.565 |

Adjacent ruling-delimited chunks share **fewer** trigrams than the same text cut elsewhere with an identical chunk-length profile. All three genres show the same direction and comparable effect sizes; only Administrative has the power to establish it. The independent uniform-cuts null agrees on direction in every case.

**Why this is not a reinstatement of the original claim.** The original asserted that ruling-bounded chunks share *more* material, and inferred a logical row boundary from that. The sign is wrong, the mechanism is different, and the original analysis remains withdrawn. The new result is consistent with `<RULING>` being a genuine content boundary by the *reverse* mechanism — an arbitrary cut tends to fall within a record, leaving related material on both sides, whereas a real ruling falls between records. Arriving at a defensible conclusion the original analysis was reaching for does not retroactively make that analysis correct.

**What it does not establish.** The mechanism. This shows *that* aligned cuts lower cross-boundary overlap, not *why*; the record-boundary reading is a hypothesis consistent with the data, and testing it directly would need record-level annotation the corpus does not carry. The effect is modest (~22% reduction against a mean of 1.19). Full threats-to-validity list in [`outputs/phase4_ruling_fullcorpus.md`](outputs/phase4_ruling_fullcorpus.md), including that `<RULING>` reflects modern editorial judgement as much as scribal practice.

---

## 2026-08-01 — REPLACED: the Zipf claim, refitted by the standard method

The Zipf-as-DSL claim was withdrawn (below) as a stream-length artifact produced by a biased estimator. `scripts/phase5_powerlaw.py` now answers the underlying question the way Clauset, Shalizi & Newman (2009) prescribe: x_min chosen by KS minimisation, α by discrete MLE, goodness of fit by parametric bootstrap, and a Vuong likelihood-ratio test against a lognormal alternative — all at a common stream length.

| Genre | α (MLE) | x_min | GoF p | Power law ruled out? | Vuong p |
|---|---:|---:|---:|:---:|---:|
| Administrative | 1.983 | 3 | 0.136 | no | 0.505 |
| Literary | 1.923 | 2 | 0.149 | no | 0.456 |
| Lexical | 1.736 | 2 | 0.003 | **YES** | 0.964 |
| Royal Inscription | 1.867 | 3 | 0.104 | no | 0.524 |
| Letter | 1.851 | 3 | 0.245 | no | 0.178 |

Three conclusions. **(1)** The original spread was an artifact: 1.114–1.746 by OLS at native lengths becomes 1.736–1.983 by MLE at equal length — a band 0.247 wide instead of 0.632. **(2)** A power law is ruled out for Lexical and not ruled out elsewhere. **(3)** Vuong's test cannot distinguish a power law from a lognormal for *any* genre, so **no genre here should be described as power-law distributed.** The defensible statement is that these distributions are heavy-tailed with α ≈ 1.7–2.0 and this method cannot identify the family.

Note that in the goodness-of-fit column a *large* p means the power law is not ruled out — the opposite of the usual convention, and a common source of error when citing power-law fits.

---

## 2026-07-31 — PROBE AUDIT: 5 of 10 audited probes must not be cited; two implications restated

A precision audit of the Phase 1 regex probes now runs as part of the pipeline (`scripts/phase1b_probe_validation.py` → [`outputs/probe_validation.md`](outputs/probe_validation.md)). Phase 1 only ever measured how often a probe *matched*; it never asked whether the matches meant what the probe's label claimed. They frequently do not.

### Probes that must not be cited

| Probe | Claimed role | Precision | What it is actually matching |
|---|---|---:|---|
| `god_dedication` | dedicatory formula | **6%** | `nam-lugal` = "kingship" and `nam-en` = "lordship" — abstract nouns, not dedications. Only `nam-ti` ("life", 10 of 182 matches) is dedicatory. |
| `excess_diri` | excess / surplus | **19%** | `diri` before a month name marks an **intercalary month**, not a ledger surplus. |
| `year_formula` | year-name | **34%** | `-` is a regex word boundary, so `\bmu\b` matches the verbal prefixes `mu-na-`, `mu-un-`, `mu-ni-` (48.6% of matches) plus `mu-kuₓ(DU)` "delivery". |
| `witness_eye` | witness clause | **41%** | `igi-ni-še₃` / `igi-zu-še₃` = "before him / before you" (pronominal), and `igi-nim` = "upper, northern" — a different lexeme entirely. |
| `king_title` | title: king | **42%** | Mostly `lugal-` as an element of a **personal name**. Even genuine hits are ambiguous: in Ur III administrative context `lugal` commonly means "owner, master", not "the king". |

### Probes that validate

`received_by` (`šu ba-ti`) 100%, `speak_to_him` (`u₃-na-a-du₁₁`) 100%, `total_audit` (`šu-nigin₂`) 100%, `seal_of_PN` (`kišib₃`) 96%, `son_of_PN` (`dumu`) 95%. The README headline figures rest on this group.

### A probe that never fires

`credit_mu_DU` searches for `mu-DU`, but the corpus writes this sign sequence as `mu-kuₓ(DU)` — **60 occurrences that the probe never sees.** `phase1_templates.py` does `if tablet_hits == 0: continue`, so a probe matching nothing vanishes from `templates.json` with no warning. The "delivery / credit" primitive was therefore never actually measured, despite appearing in the probe list.

### Two README implications restated

**Implication #1 previously asserted "witness clauses (`igi PN-šè`) are common" and "no important write is anonymous, undated, or unattributed."** Both are false in this sample. Genuine non-pronominal witness clauses appear on **0.4%** of administrative tablets. And **23.2%** of administrative tablets carry neither seal, year-name, nor witness, while ~75% carry no seal clause at all. Sealing is a strong minority practice, not a universal rule. The surviving claim — 25.4% sealed, 70.2% year-dated, both precision-validated — is still interesting and is what the section now says.

**Implication #3 previously asserted that administrative tablets "close with `šu-nigin₂`" and that "nothing drifts silently."** `šu-nigin₂` is a precise probe (100%) but appears on only **2.2%** of administrative tablets; `la₂-ia₃` on 3.4%. The pattern is real and genuinely a Sumerian bookkeeping device, but it was described as characteristic of the corpus when it is a small minority practice. Prevalence tables per genre are now in `probe_validation.md`.

**The general lesson, which is now stated in the report itself: attested is not the same as characteristic.** Several claims in this repo moved from "we found this pattern" to "this is how Sumerian bureaucracy worked" without the prevalence check that distinguishes them.

### Epistemic status of this audit

The discriminators encode standard dictionary values applied by a **non-specialist**. They are deliberately conservative — a match is marked FALSE only where the surface form makes an alternative reading unambiguous — so the reported error rates are **lower bounds**. This is not a substitute for review by an Assyriologist, and `REVIEWERS.md` still lists probe validation as the highest-value target for specialist time.

---

## 2026-07-31 — WITHDRAWN: "Administrative and Royal genres are DSL-like (Zipf s ≈ 1.75 vs Lexical 1.11)"

**Affected:** README artifact #3, the Findings table rows "Admin tablets are a domain-specific language" and "Lexical lists are closest to natural language", and `outputs/compression_findings.md` §1.

**Original claim.** Per-genre Zipf exponents (Administrative s=1.746, Royal Inscription s=1.737, Letter s=1.607, Literary s=1.680, Lexical s=1.114, all R² 0.92–0.95) show that administrative and royal genres have a small high-reuse core vocabulary — behaving like a domain-specific language — while lexical lists sit near the natural-language value of s ≈ 1.0.

**Status: withdrawn.** The cross-genre difference is an artifact of how many tokens each genre's stream contains.

### What went wrong

**1. A stream-length confound (fatal).** Zipf exponents estimated this way are strongly sample-size dependent, and these streams differ by ~60×: Literary 154,005 tokens, Royal 33,015, Administrative 32,493, Letter 18,664, Lexical **2,508**. Comparing raw exponents across them compares corpus sizes, not genres. Re-fitting every genre on equal-length blocks:

| Genre | Stream length | s at native length | s at 2,508 tokens | sd |
|---|---:|---:|---:|---:|
| Administrative | 32,493 | 1.746 | **1.187** | 0.019 |
| Literary | 154,005 | 1.680 | **1.187** | 0.045 |
| Lexical | 2,508 | 1.114 | **1.114** | 0.000 |
| Royal Inscription | 33,015 | 1.737 | **1.200** | 0.022 |
| Letter | 18,664 | 1.607 | **1.210** | 0.015 |

A native-length spread of 0.632 collapses to 0.096. Lexical looked like "natural language" only because its stream is the shortest and so had the least opportunity to accumulate a low-frequency tail. Verified under both contiguous-block and random-token subsampling, 25 draws each.

**2. The estimator is unreliable.** `zipf_fit` is ordinary least squares on log-log rank-frequency data. That is a biased estimator of a power-law exponent, and the R² it produces is not a goodness-of-fit test — comparably high R² is routine for lognormal and exponential data (Clauset, Shalizi & Newman 2009, *SIAM Review* 51(4), 661–703). An MLE estimate on the same data disagrees with the OLS estimate in both magnitude and **rank order**, which is the diagnostic symptom.

**3. Sensitivity to arbitrary preprocessing.** Hapax legomena are 34–59% of types depending on genre. Dropping them shifts exponents by up to 0.17 and reverses the direction of some genre comparisons — a result that flips on a preprocessing choice nobody documented is not a finding.

### What is unaffected

The §2 compression-redundancy comparison was tested for the *same* confound rather than assumed safe, and **survives**: at equal-length contiguous blocks the genre ranking is preserved (Royal > Administrative > Literary/Letter > Lexical) with magnitudes of the same order, and genres that swap rank do so within overlapping standard deviations. That control now runs as part of the pipeline. Note the control must use *contiguous* blocks — sampling scattered positions destroys the token adjacency zlib exploits and manufactures a collapse that is not there. An earlier version of this audit made exactly that mistake and had to be redone.

### Doing this properly

MLE fitting with a fitted `x_min`, a Kolmogorov–Smirnov goodness-of-fit statistic, and likelihood-ratio tests against lognormal alternatives — on length-matched samples. None of that is done here. The pipeline now reports the length control and an MLE exponent alongside the OLS fit so the discrepancy is visible rather than buried.

---

## 2026-07-31 — CORRECTED: tablet citations under the seal finding

README implication #1 cited "Tablets P101440, P132611, P117793, P145759" in support of the sentence "25.4% of administrative tablets carry `kišib₃`". Only **P101440** is an administrative tablet containing `kišib₃`. The other three are **Letters** and contain no seal clause; they carry attribution by a different mechanism — the `u₃-na-a-du₁₁` address formula plus a closing scribe signature (`dub-sar`) and filiation (`dumu` PN). All four are genuine corpus tablets and all four are relevant to attribution, but they were cited under a claim three of them do not support. Now cited separately with the mechanism each one actually demonstrates.

Verified: the "Concrete Example" decomposition of P101440 elsewhere in the README is accurate in every element — `la₂-ia₃`, `kišib₃ {d}šul-gi-i₃-li₂`, `iti ezem-me-ki-gal₂`, `mu us₂-sa ki-maš{ki} ba-hul`, `siki`, and `geme₂` are all present in the tablet as transcribed.

---

## 2026-07-31 — REVISED: probe frequencies restated with their over-catch

`year_formula` uses the regex `\bmu\b`, which matches inside `mu-DU` (a delivery/credit term), `mu-ni` ("its name"), and verbal prefixes, because `-` is a regex word boundary. Of 551 matches in the Administrative sample, ~62% are plausibly year formulae and ~19% are clearly not. At the tablet level the effect is small — a stricter probe requiring `mu` followed by a year-name gives **70.6%** against the reported **74.2%** — because tablets carrying a spurious `mu-` usually carry a real year formula too. The README now states ~71% with both figures shown.

A larger problem affects `king_title` (`\blugal\b`, reported at 48.6% of Administrative tablets), which is **not** measuring royal titles: 54% of its matches are `lugal-...` as an element of a *personal name*, and only ~12% are plausibly the title "king". That probe appears in `outputs/templates.json`; it is not among the README headline figures. It is flagged rather than silently repaired, because fixing it properly needs a name-vs-title disambiguation that regex cannot do.

Spot-checked and confirmed exact: `seal_of_PN` 25.4% of Administrative, `speak_to_him` (`u₃-na-a-du₁₁`) 58.8% of Letters. Corpus totals confirmed exact: 91,606 tablets, 6,968,581 cuneiform glyphs, zero duplicate IDs, zero duplicate transliterations.

---

## 2026-07-31 — WITHDRAWN: "`<RULING>` is a validated logical row separator"

**Affected:** README artifact #4, README implication #2, `outputs/compression_findings.md` §4, and the Findings table row "`<RULING>` is a logical row separator (not visual)".

**Original claim.** Adjacent ruling-delimited chunks share trigrams 30–500× more than a shuffled baseline (Royal Inscription p=0.002, Administrative p=0.005), establishing that the physical `<RULING>` mark corresponds to a logical row boundary — and, by extension, motivating a three-tier SURFACE/COLUMN/RULING agent-memory design.

**Status: withdrawn.** There is no statistical evidence in this corpus sample that `<RULING>` marks content boundaries.

### What went wrong

Two independent defects, one fatal.

**1. The null hypothesis was wrong (fatal).** The test compared observed cross-boundary trigram sharing against a null built by *pooling the tablet's tokens, shuffling them, and re-cutting at the same lengths*. That null destroys all local structure in the text. Beating it demonstrates only that Sumerian is locally coherent — a property of any natural language, and one that says nothing about `<RULING>` in particular. Any arbitrary chunking of any real text beats that null.

The null that actually isolates the question holds the real token order *and* the exact multiset of chunk lengths fixed, and permutes only **where the cuts fall**. Under that null the effect vanishes:

| Genre | Pairs | Observed | Token-shuffle null (wrong) | Boundary-permute null (correct) | p (correct) |
|---|---:|---:|---:|---:|---:|
| Administrative | 17 | 0.176 | 0.004 | 0.343 | 0.781 |
| Literary | 108 | 0.731 | 0.018 | 0.889 | 0.905 |
| Lexical | 13 | 0.538 | 0.037 | 0.430 | 0.274 |
| Royal Inscription | 10 | 0.500 | 0.001 | 0.500 | 1.000 |

The wrong null sits ~100× below the right one. Observed values land *at or below* the correct null in every genre — the opposite of the reported direction.

**2. The p-value was computed against the wrong distribution.** It measured the fraction of *individual* null chunk-pairs whose value met or exceeded the observed **mean**, rather than building a null distribution *of the mean* (one value per permutation). Because shared-trigram counts are integers and heavily zero-inflated, the reported p-value reduced exactly to "the fraction of shuffled pairs sharing at least one trigram" — a different quantity from the one being claimed. In this instance it happened to land near the correctly computed value (0.005 vs 0.005 for Administrative), so it was not what produced the false positive, but it was wrong and is fixed.

Both are corrected in `scripts/phase3_compression.py::ruling_parity`, which now reports both nulls side by side, uses a permutation distribution of the mean, and applies the standard `(r+1)/(n+1)` correction so p is never exactly 0.

### What this does *not* say

A null result on 10–17 adjacent-chunk pairs is weak evidence in either direction. This does not establish that `<RULING>` is meaningless — the marks are plainly deliberate, physically drawn by scribes, and the three nested structural levels are real features of the artifact. It establishes only that **this test does not support the claim that was made from it**, and that the sample here is too small to settle the question either way. Testing it properly would need the full corpus rather than a 500-tablet-per-genre sample, and a boundary-placement null from the outset.

### Knock-on effects

- The three-tier SURFACE → COLUMN → RULING memory design is now presented as an **untested design proposal**, not a corpus finding.
- Anything in `outputs/FULL_IDEAS.md`, `outputs/summary.md`, or `outputs/reference_architecture.md` that leans on RULING-as-validated-row-boundary inherits this retraction. Those are hand-authored design documents and have not been individually rewritten; treat RULING-derived claims in them as proposals.

### What is unaffected

- **§1 Zipf** (Admin s=1.746, Royal s=1.737, Lexical s=1.114) — descriptive statistics, unchanged.
- **§2 Compression Δ** — descriptive, unchanged. Note it uses the same token-shuffle baseline, but its claim is only "more structured than random token order", which is what that baseline legitimately tests.
- **§3 ELS null result** (0 of 495 Bonferroni-significant) — this was always a correct permutation test: one null value per shuffle, compared against the observed statistic. Audited and unchanged. Being a null result, it is also the claim least at risk from this class of error.
- **Phase 1 probe frequencies** (`kišib₃` 25.4%, year-formula 74.2%, `u₃-na-a-du₁₁` 58.8%) — raw regex counts over the sample, no inference involved.
- **The `kishib3` benchmark** (5/5 vs 0/5 capability, +59% bytes, +37 tokens/write) — an engineering measurement, no statistics.

### How it was found

A reproducibility audit re-ran the full pipeline from a clean clone, then examined how each reported p-value was computed. The RULING-parity p-value was traced to a comparison against the pooled distribution of individual null pairs; investigating that led to examining the null itself. The alternative control was implemented independently and run at 500 permutations before the change was made to the pipeline.

---

## Reporting a problem

If you find an error, open an issue. Claims that survive adversarial checking are worth more than claims that were never checked, and a corrected repo is more useful than a confident one. Independent reproduction of any Phase 3 statistic is especially welcome — see the "Verifying your run matched" section of the README.
