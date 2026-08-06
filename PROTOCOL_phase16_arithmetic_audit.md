# Pre-registered protocol — Phase 16: Auditing the world's first auditors

**Status: PROTOCOL ONLY. Committed before the analysis exists.** This document fixes the
estimand, the exclusion rules, the validation gate, and the hypotheses for a study that has NOT
been run. The pilot numbers below are disclosed as unvalidated parser output and must not be
cited as findings. When the study runs, it runs against this document as committed; deviations
get logged in CORRECTIONS.md like everything else here.

## The question

2,476 administrative tablets in SumTablets carry a `šu-nigin₂` (sum-total) line. Sumerian count
notation is parseable (sexagesimal System S: `1(diš)`=1, `1(u)`=10, `1(geš₂)`=60, `1(gešʾu)`=600,
`1(šar₂)`=3600). Therefore, for a verifiable subset, we can check whether the totals actually
equal the sums of their line items — **the arithmetic error rate of Ur III accounting, measured
at corpus scale**, something we have found no prior quantitative measurement of (novelty sweep
pending; this claim will be re-verified before the study runs).

## Why this is not runnable today

A naive pilot (2026-08-06, spike script in the session record) found only 14 strictly-checkable
tablets and 8 apparent mismatches. Those mismatches are presumed **parser artifacts, not scribal
errors**, until proven otherwise: line items carry numerals that are not counted commodities —
day numbers (`u₄ 2(u)-kam`), ordinals (`-kam`), grade markers, year counts — and the pilot
counter cannot distinguish them. Publishing an "error rate" from that pipeline would repeat the
`king_title` failure (41% personal names) with arithmetic. The study therefore gates on a
validation step, below.

## Estimand

Among VERIFIABLE tablets (defined by the exclusion rules), the share whose stated total does not
equal the sum of parsed line items, with a Wilson 95% CI, decomposed into:
  (a) under-total (total < sum), (b) over-total (total > sum), (c) magnitude distribution of
  discrepancies (off-by-one vs. sign-value slips vs. large).

## Exclusion rules (fixed now)

A tablet is VERIFIABLE only if ALL hold:
1. Exactly one `šu-nigin₂` line (multi-total and subtotal structures: v2, not v1).
2. No damage markers (`<unk>`, `...`) anywhere on the tablet.
3. The total line's numerals are entirely System-S count units, attached to a count commodity
   (herd animals, personnel) from a fixed lexicon.
4. Every numeral group on item lines is classifiable by the classifier (below) as COUNTED or
   NON-COUNTED (dates, ordinals, grades, capacity/weight systems); any unclassifiable group
   excludes the tablet.
5. At least 2 counted item lines.

## The validation gate (the part that makes this credible)

Before any corpus-level number is reported:
- A hand-audit of **100 randomly sampled verifiable tablets** (seeded), where a human (or a
  carefully prompted independent check against the ePSD2 lemmatisation, treated as a second
  annotator) classifies every numeral group. The parser ships only if its per-group
  classification agrees with the hand audit at ≥ 98% precision on COUNTED groups.
- Reported alongside the error rate: the verifiable-subset selection rate and a comparison of
  verifiable vs. non-verifiable tablets on length/period/commodity, so selection bias is visible.
- MTAAC's numero-metrological parser (Pagé-Perron et al. 2017 lineage) to be evaluated first;
  if public and adequate, we validate against it rather than reinventing it.

## Pre-registered hypotheses

  A1  The corpus-level arithmetic error rate among verifiable tablets is below 5%. (Ur III
      accounting is reputed meticulous; this quantifies the reputation.)
  A2  Error rate increases with the number of line items (cognitive load).
  A3  **Sealed tablets (`kišib₃` present) have a lower error rate than unsealed verifiable
      tablets** — named accountability and error, 2000 BCE. Confound controls fixed now:
      compare within commodity-class and item-count strata; report the raw and stratified
      contrast; treat as suggestive unless both agree. (A reviewer sweep on sealing-function
      scholarship is pending and its confound list will be incorporated before the run, with
      any additions logged as amendments here.)
  A4  Error rate does not differ detectably across Ur III provincial archives (provenance not
      in SumTablets metadata; this hypothesis activates only if provenance can be joined from
      CDLI; otherwise it is dropped and the drop logged).

## What would kill the study

- Parser precision below the gate after two iterations: report the failure, publish the
  validation numbers, do not publish an error rate.
- Fewer than 150 verifiable tablets: report descriptively, no hypothesis tests.

*Committed 2026-08-06. Any run happens in a later session, against this text.*
