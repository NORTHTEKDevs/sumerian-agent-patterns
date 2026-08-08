# Phase 16 v2 — the arithmetic audit under per-section rules (run against protocol v2)

Protocol: [PROTOCOL_phase16_arithmetic_audit_v2.md](../PROTOCOL_phase16_arithmetic_audit_v2.md), committed 2026-08-07 after v1's kill criteria fired; estimand and hypotheses unchanged from v1, exclusion rules per-section with subtotal support. Classifier: v1 verbatim (iteration 1). Unit of verifiability: the SECTION.

Candidates: **671 tablets**, containing **1,731 total-line sections**. Verifiable under the v2 rules: **32 sections on 12 tablets**.

## Verdict first: kill criterion 2 fires again, for a different and more interesting reason

**32 verifiable sections < 150 → no error rate, no hypothesis tests (A1–A3 not evaluated). The study retires under v2 as it did under v1.** But the attrition moved: v1 died of damage exclusion (79% of tablets); v2's per-section damage rule works — damage now removes only 375 of 1,731 sections (22%). What kills v2 is the corpus itself:

- **Rule 3 removes 1,079 sections (62%)**: 613 totals are grain/capacity/weight metrology (gur/sila₃/gin₂ systems — outside the committed System-S head-count scope), 403 System-S totals name no lexicon commodity on the total line (bare grand totals; status words like la₂-ia₃ 'deficit', zi-ga 'expended', gub-ba 'stationed'; personnel terms outside the fixed lexicon such as aga₃-us₂, erin₂), 61 have no readable numeral, 2 use other number systems (šargal, eše₃, DIŠ/AŠ sign-value variants).
- **Rule 5 removes 201 of the remaining sections**: 35 sections total an item region with NO numeral lines at all — one-name-per-line personnel/delivery lists whose counts are implicit (one head per line); 13 have numerals only in date/rate context; 4 have exactly one counted line; 149 are empty regions (grand totals directly after subtotals).
- Rule 4 (unclassifiable groups) removes 44.

**The structural finding: Ur III head-count totals mostly do not total explicit numeral item lines.** In order of magnitude: they are grain/capacity totals outside the head-count scope, System-S totals whose commodity or status word sits outside the fixed lexicon or off the total line, grand totals over subtotal regions with no items of their own, and implicit one-name-per-line lists. Explicit item-arithmetic sections — where a total can be checked against parseable addends — are rare in this corpus regardless of damage handling. v1's conclusion ('damage makes this impossible') was wrong about the binding constraint; v2 shows that fixing damage handling exposes a deeper scarcity.

**Robustness of the kill:** a deliberately generous post-hoc lexicon extension (aga₃-us₂, erin₂, dumu, lu₂, munus, nita₂) raises verifiable sections only to **34** — still far below 150. The kill is not a lexicon artifact.

## Second annotator, repaired (v2 obligation), descriptive only

**Round 1** fixed three v1 alignment defects before any comparison: unordered CDL walk (token order not guaranteed), a 2-token commodity window that modifiers like niga 'fattened' eclipsed, and lexicon misses (ePSD2 writes ŋuruš with ŋ, so every personnel group dropped; fraction forms like 1/2(diš) parsed as 2). Round-1 result: **236/242 COUNTED groups agree (97.5%)** over the verifiable tablets present in ePSD2 — against v1's 75%, which is thereby demonstrated to have been mostly annotator-alignment failure, not classifier failure.

**Post-mortem (the v2 precondition for any gate verdict): every round-1 disagreement — 6 groups on 3 tablets — was adjudicated by hand against the expert lemmas as ANNOTATOR-ALIGNMENT error; zero classifier errors were found.**

- **P205369** (annotator-alignment): maš₂-sag (lead goat) lemmatised cf=mašsaŋ gw='leader', outside the round-1 annotator lexicon; all three maš₂-sag item lines dropped. Parser classification correct.
- **P515662** (annotator-alignment): gu₄-ab₂-ba (breed bull) lemmatised cf=gudabak gw='bull'; 'bull' absent from the round-1 gw list. Parser classification correct.
- **P207923** (annotator-alignment): round-1 fraction guard matched 'igi-' as substring and ate the line '1(geš₂) guruš nu-banda₃ igi-zu-bar-ra' (igi-zu-bar-ra is a personal name, pos=PN). Parser classification correct.

Round 2 repaired those coverage gaps (citation forms added exactly as ePSD2 writes them: mašsaŋ, gudabak; fraction guard narrowed to igi-N-gal₂; la₂ minus-notation lines skipped symmetric with the parser). The classification judgment itself — what is a commodity, a date, a unit — remains ePSD2's expert lemmatisation throughout, so the annotator stays independent. Round-2 result over the 12 matched tablets: **242/242 COUNTED groups agree (100.0%)**. This is DESCRIPTIVE: the committed gate requires a 100-tablet sample and only 12 verifiable tablets exist, so no gate verdict is issued or counted.

## The 32-section descriptive record (NOT an error rate)

Among the 32 verifiable sections, **8 raw total-vs-sum disagreements**. These are UNVALIDATED parser disagreements, not scribal errors: the gate never ran at protocol scale, the classifier's line-level date suppression drops counted groups on mixed lines (the same `\bmu\b` overreach class the phase 15b year-name audit quantified), and 4 sections have damage above their first counted line (possible destroyed items; 3 of the disagreeing sections are in that set). The suppression mechanism is verified, not suspected: P515662's two 'mismatches' reconcile EXACTLY once its age-graded cattle lines (`8(diš) ab₂ mu 3(aš)` = eight 3-year-old cows, suppressed because `mu` reads as date context) are restored — 39 counted + 37 suppressed = 76 claimed, and 41 + 33 = 74. The scribes were right both times; the parser manufactured both disagreements.

| Tablet | Sec | Total claims | Items sum | Counted lines | Match | Lead damage | Sealed tablet |
|---|---:|---:|---:|---:|---|---|---|
| P204617 | 1 | 5193 | 5193 | 4 | yes |  |  |
| P204617 | 2 | 1135 | 1135 | 4 | yes |  |  |
| P204617 | 3 | 193 | 193 | 4 | yes |  |  |
| P204617 | 4 | 113 | 113 | 4 | yes |  |  |
| P204617 | 5 | 53 | 53 | 4 | yes |  |  |
| P204617 | 6 | 153 | 153 | 4 | yes |  |  |
| P204617 | 7 | 124 | 124 | 4 | yes |  |  |
| P204617 | 8 | 126 | 126 | 4 | yes |  |  |
| P204617 | 9 | 75 | 75 | 4 | yes |  |  |
| P204617 | 10 | 60 | 60 | 4 | yes |  |  |
| P204617 | 11 | 71 | 71 | 4 | yes |  |  |
| P204617 | 12 | 170 | 170 | 4 | yes |  |  |
| P204617 | 13 | 543 | 543 | 4 | yes |  |  |
| P204617 | 14 | 406 | 406 | 4 | yes |  |  |
| P204617 | 15 | 376 | 376 | 4 | yes |  |  |
| P205369 | 1 | 415 | 415 | 5 | yes |  |  |
| P205369 | 2 | 123 | 123 | 3 | yes |  |  |
| P205369 | 3 | 525 | 525 | 5 | yes | yes |  |
| P205369 | 4 | 540 | 540 | 5 | yes |  |  |
| P205369 | 5 | 120 | 54 | 2 | NO | yes |  |
| P205369 | 6 | 332 | 332 | 4 | yes |  |  |
| P207923 | 1 | 120 | 120 | 2 | yes |  |  |
| P376970 | 1 | 67 | 11 | 2 | NO |  |  |
| P390115 | 1 | 12 | 21 | 4 | NO |  |  |
| P514944 | 1 | 221 | 221 | 5 | yes |  |  |
| P515528 | 1 | 92 | 92 | 3 | yes |  | yes |
| P515662 | 1 | 76 | 39 | 2 | NO |  |  |
| P515662 | 2 | 74 | 41 | 2 | NO | yes |  |
| P516034 | 1 | 32 | 91 | 4 | NO | yes |  |
| P517764 | 1 | 285 | 365 | 4 | NO |  |  |
| P518224 | 1 | 22 | 22 | 4 | yes |  |  |
| P518266 | 1 | 124 | 327 | 15 | NO |  |  |

## Status of the study

Two committed protocols, two kills, two different binding constraints — v1: damage notation density; v2: the scarcity of explicit item-arithmetic in head-count sections. A v3 would need a different estimand (e.g. grain metrology with full capacity-system arithmetic, or implicit name-list counting), i.e. a new study, not a rules patch. Per both protocols, the attrition and validation accounting above IS the publishable output.
