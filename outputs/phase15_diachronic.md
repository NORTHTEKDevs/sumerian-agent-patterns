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

**S2 permutation test** (ED IIIb vs Ur III, year-name placement entropy, length-stratified, 5,000 permutations): Δ = 0.1392 bits (positive = Ur III more disciplined), p_upper = 0.57289, p_lower = 0.42731.

## Pre-registered verdicts

| Criterion | Held? | Detail |
|---|:---:|---|
| S1 — sealing prevalence rises monotonically ED IIIa → Ur III | **YES** | rho = 1.0, exact p = 0.00833 |
| S2 — year-name placement tightens (entropy falls) by Ur III | **NO** | Δ = 0.1392 bits, p = 0.57289 |
| S3 — full-envelope rate peaks in Ur III | **YES** | Early Dynastic IIIa: 0.0%, Early Dynastic IIIb: 0.0%, Old Akkadian: 0.1%, Lagash II: 0.3%, Ur III: 24.2% |

## What this speaks to, and the four caveats that bound it

**The historiographic stake.** Steinkeller's canonical account treats Ur III under Shulgi as a sharp bureaucratic break — standardized bookkeeping, the bala system, a fixed formula repertoire — while Selz argues many 'Shulgi reforms' have Early Dynastic forerunners, a continuity thesis. A quantitative formula-standardization trajectory speaks directly to gradual-accretion vs. sharp-discontinuity, and to our knowledge (novelty sweep, 2026-08-06) no quantitative diachronic study of administrative-formula standardization across these periods exists. Closest neighbours: Nissen/Damerow/Englund on proto-cuneiform (earlier period), Tsouparopoulou's sealing database (one practice, one site, one period), BDTNS corpus statistics (Ur III only).

**Caveat 1 — surviving record, not practice.** Different city archives dominate different centuries (Girsu early, Drehem/Umma for Ur III), and SumTablets carries no provenance field to stratify on. These are trajectories of the surviving, transliterated record. **Caveat 2 — measurement is textual, not physical.** Our seal figure counts kišib₃ TEXT clauses (25.4% in Ur III), not physical seal impressions (BDTNS reports ~35.7% of Ur III tablets physically sealed); the two measure different things and both can be right. **Caveat 3 — formula spelling itself evolves.** A period where the receipt function was written with a different formula than šu ba-ti will read as low prevalence; part phenomenon (the format changed), part probe limitation — undivided here. **Caveat 4 — low placement entropy alone proves nothing.** Fixed tablet layout can hold positional entropy low in every period for reasons unrelated to standardization (cf. arXiv:2608.02999 on the non-specificity of such measures); only the length-stratified DIACHRONIC DELTA (S2) is claimed, never a single period's entropy in isolation.
