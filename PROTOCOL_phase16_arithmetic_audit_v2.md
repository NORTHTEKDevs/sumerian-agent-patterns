# Pre-registered protocol v2 — Phase 16 arithmetic audit (supersedes v1's exclusion rules only)

**Status: PROTOCOL ONLY, committed 2026-08-07 after v1's kill criteria fired.** Estimand and
hypotheses A1-A3 are UNCHANGED from v1 (PROTOCOL_phase16_arithmetic_audit.md); only the rules
v1's attrition accounting proved incompatible with the corpus change, with rationale.

## Changes from v1, with rationale
1. **Rule 2 (damage) becomes per-SECTION:** v1's whole-tablet damage exclusion eliminated 79%
   of candidates (533/671). v2 requires only that the ITEM BLOCK (lines between the first
   counted line and the total line) and the TOTAL LINE are free of damage markers; damage in
   headers, date lines, or seal lines does not exclude.
2. **Rule 1 gains subtotal support:** tablets with multiple šu-nigin₂ lines are verifiable
   per-SECTION (each total checked against the items above it, back to the previous total).
3. **The validation gate is unchanged (>= 98% on COUNTED groups, 100 tablets)** but the second-
   annotator alignment must be repaired first: v1's 75% reflected ePSD2 tokenisation-window
   misses as much as classifier error; v2 requires a disagreement post-mortem distinguishing
   classifier error from annotator-alignment error before the gate verdict counts.
4. Kill criteria unchanged: gate failure after two iterations, or < 150 verifiable sections.

*Runs in a later session against this text. Deviations go to CORRECTIONS.md.*
