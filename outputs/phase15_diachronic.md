# Phase 15 — Six hundred years of format standardization

The corpus spans c. 2600–2000 BCE. The gold-validated bureaucratic formulae are, functionally, elements of a document format; this phase measures how that format standardized across five administrative periods — prevalence, placement discipline (position-decile entropy; a formula that always sits in the same relative slot has low entropy — that is operationally what 'a format' means), and the full-envelope rate (seal AND date on one tablet). Administrative genre only; length-stratified permutation null for the entropy test; Ur III capped at 5,000 tablets (seeded) for entropy so mass alone cannot drive stratification.

| Period | n | Seal % (95% CI) | Year-name % | Full envelope % | Year-name placement entropy (bits) |
|---|---:|---:|---:|---:|---:|
| Early Dynastic IIIa | 789 | 0.1 (0.0–0.7) | 0.5 | 0.0 | 2.585 |
| Early Dynastic IIIb | 3,331 | 0.4 (0.3–0.7) | 10.6 | 0.0 | 2.79 |
| Old Akkadian | 4,987 | 0.5 (0.4–0.8) | 10.3 | 0.1 | 2.0648 |
| Lagash II | 625 | 1.4 (0.8–2.7) | 20.0 | 0.3 | 1.8034 |
| Ur III | 75,792 | 26.5 (26.2–26.8) | 73.2 | 24.2 | 2.6508 |
| Old Babylonian *(descriptive, small n)* | 130 | 1.5 (0.4–5.4) | 85.4 | 1.5 | nan |

## Probe status — read before the year-name columns

`seal (kišib₃)` and `receipt (šu ba-ti)` are gold-audited (100%/99.8% lexeme precision vs Oracc). **The strict year-name variant used here has never itself been precision-audited**: the loose `\bmu\b` probe scored 34% (DO-NOT-CITE) and the bare-lexeme Oracc check (70.6%) certifies the word, not the formula. A known unexcluded false-positive class is the oath formula (`mu lugal-bi in-pad₃`, 'swore by the name of the king'), which passes a whitespace-based regex. **Every year-name-dependent result below (the year column, S2, S3) is therefore PROVISIONAL pending a dedicated audit of this variant**; the seal-based S1 result does not share this contingency. Caught at the adversarial gate; an earlier draft called all three probes gold, which was wrong.

**S2 permutation test** (ED IIIb vs Ur III, year-name placement entropy, length-stratified, 5,000 permutations): Δ = 0.1392 bits (positive = Ur III more disciplined), p_upper = 0.57289, p_lower = 0.42731.

**Occurrence-matched robustness check** — small-sample entropy bias runs LOW, and ED IIIb has ~8x fewer occurrences, a bias direction that favours the null above, so the comparison is repeated with Ur III subsampled to ED IIIb's 547 occurrences (1,000 draws): ED IIIb 2.79 bits vs Ur III 2.6392 at matched n; matched Δ = 0.1507 bits (95% CI 0.043 to 0.2636). The matched-n CI excludes zero — a small real tightening signal the pre-registered test did not detect. Discipline: the pre-registered stratified test remains the S2 verdict (failed); the matched-n result is a post-hoc observation, flagged for future pre-registration, and is itself contingent on the unaudited year-name probe.

## Pre-registered verdicts

| Criterion | Held? | Detail |
|---|:---:|---|
| S1 — sealing prevalence rises monotonically ED IIIa → Ur III | **YES** | rho = 1.0, exact p = 0.00833 |
| S2 — year-name placement tightens (entropy falls) by Ur III | **NO** | Δ = 0.1392 bits, p = 0.57289 |
| S3 — full-envelope rate peaks in Ur III | **YES** | Early Dynastic IIIa: 0.0%, Early Dynastic IIIb: 0.0%, Old Akkadian: 0.1%, Lagash II: 0.3%, Ur III: 24.2% |

**S1 disclosure.** With five points, ANY strictly increasing sequence yields the same exact p = 1/120; the certified content is the ordering alone. The four early periods' Wilson CIs mutually overlap — their internal ordering is not distinguishable from noise. The load-bearing contrast is Ur III against all earlier periods, which no CI overlap threatens.

## What this speaks to, and the caveats that bound it

**The historiographic stake, stated symmetrically.** Steinkeller's canonical account treats Ur III under Shulgi as a sharp bureaucratic break; Selz argues many reforms have Early Dynastic forerunners. This study contributes ONE quantitative datapoint on ONE textual practice to a dispute that spans many practices — it does not adjudicate it. Read symmetrically, the data cut both ways: seal-CLAUSE adoption looks like sharp discontinuity (Steinkeller-compatible), while placement conventions show no detectable Ur III tightening under the pre-registered test (continuity-compatible). To our knowledge (novelty sweep, 2026-08-06) no quantitative diachronic study of administrative-formula standardization across these periods exists; closest neighbours: Nissen/Damerow/Englund on proto-cuneiform, Tsouparopoulou's sealing database (one practice, one site, one period), BDTNS corpus statistics (Ur III only).

**Caveat 1 — surviving record, not practice.** Different city archives dominate different centuries (Girsu early, Drehem/Umma for Ur III), and SumTablets carries no provenance field to stratify on. These are trajectories of the surviving, transliterated record. **Caveat 2 — measurement is textual, not physical.** Our seal figure counts kišib₃ TEXT clauses, not physical seal impressions; literature-circulating BDTNS-derived figures put physical sealing substantially higher (roughly a third of Ur III tablets) — a figure we have NOT verified at source and flag rather than cite with false precision. The two measure different things and both can be right. **Caveat 3 — formula spelling itself evolves.** A period where the receipt function was written with a different formula than šu ba-ti will read as low prevalence; part phenomenon (the format changed), part probe limitation — undivided here. **Caveat 4 — entropy levels are non-specific AND, here, high.** Both periods sit near the uniform ceiling (2.79 and 2.65 of a 3.32-bit maximum): at decile resolution NO strong slot convention existed in either period, so no claim of 'already conventional' placement is available from this data (an earlier draft made that claim; withdrawn at the gate). Single-period entropy is additionally non-specific in principle (arXiv:2608.02999); only the diachronic delta was tested.
