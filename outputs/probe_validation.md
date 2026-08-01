# Probe Validation — do the Phase 1 regexes mean what their labels say?

Phase 1 reports how often each probe **matches**. This report asks whether those matches **mean** what the probe's label claims. Every headline frequency in the README rests on the answer.

> **Epistemic status.** The discriminators below encode standard dictionary values applied by a **non-specialist**. They are deliberately conservative — a match is only counted FALSE where the surface form makes an alternative reading unambiguous. **These are lower bounds on the error rate, and are not a substitute for review by an Assyriologist.** See `REVIEWERS.md`.

Precision = TRUE / (TRUE + FALSE); UNCLEAR is excluded and reported separately.

## Summary

| Probe | Claimed role | Matches | Precision | UNCLEAR | Verdict |
|---|---|---:|---:|---:|---|
| `year_formula` | temporal index (year-name) | 5,088 | 34% | 715 | **DO NOT CITE** |
| `king_title` | title: king | 2,666 | 42% | 870 | **DO NOT CITE** |
| `god_dedication` | dedicatory formula | 182 | 6% | 0 | **DO NOT CITE** |
| `witness_eye` | witness presence (before X) | 92 | 41% | 5 | **DO NOT CITE** |
| `son_of_PN` | filiation / lineage | 1,302 | 95% | 236 | usable with caveat |
| `excess_diri` | excess / surplus | 62 | 19% | 46 | **DO NOT CITE** |
| `seal_of_PN` | identity / authentication | 301 | 96% | 37 | **reliable** |
| `received_by` | transaction confirmation | 120 | 100% | 0 | **reliable** |
| `speak_to_him` | letter address formula | 297 | 100% | 0 | **reliable** |
| `total_audit` | ledger total / audit line | 22 | 100% | 0 | **reliable** |

## Per-probe detail

### `year_formula` — claimed role: temporal index (year-name)

Regex: `\bmu\b(?:[\s\-][^\n]{0,80})`  
Matches: 5,088 — TRUE 1,485 / FALSE 2,888 / UNCLEAR 715

| Verdict | Interpretation of the matched form | n |
|---|---|---:|
| FALSE | verbal prefix (mu-na-, mu-un-, mu-ni-, ...) | 2,498 |
| TRUE | mu + royal/event name (year-name) | 1,360 |
| UNCLEAR | unclassified by the discriminators | 715 |
| FALSE | line-break / structural-token artifact | 189 |
| FALSE | mu-bi / mu-ni = 'its/his name' | 141 |
| TRUE | mu us₂-sa + event (derived year-name) | 125 |
| FALSE | mu-kuₓ(DU) = delivery, a different lexeme | 60 |

### `king_title` — claimed role: title: king

Regex: `\blugal\b[^\n]{0,40}`  
Matches: 2,666 — TRUE 750 / FALSE 1,046 / UNCLEAR 870

| Verdict | Interpretation of the matched form | n |
|---|---|---:|
| FALSE | lugal- as element of a PERSONAL NAME | 1,046 |
| TRUE | lugal + GN/epithet (king of X, mighty king) | 750 |
| UNCLEAR | bare 'lugal' (king, or 'owner/master' in admin context) | 447 |
| UNCLEAR | unclassified by the discriminators | 423 |

### `god_dedication` — claimed role: dedicatory formula

Regex: `\bnam-(ti|ki|en|lugal)\b`  
Matches: 182 — TRUE 10 / FALSE 172 / UNCLEAR 0

| Verdict | Interpretation of the matched form | n |
|---|---|---:|
| FALSE | nam-lugal = 'KINGSHIP', an abstract noun | 132 |
| FALSE | nam-en = 'en-ship/lordship', an abstract noun | 40 |
| TRUE | nam-ti = 'life' (used in 'for the life of' dedications) | 10 |

### `witness_eye` — claimed role: witness presence (before X)

Regex: `\bigi[\s\-][^\n]{0,40}-š[èe]₃\b`  
Matches: 92 — TRUE 36 / FALSE 51 / UNCLEAR 5

| Verdict | Interpretation of the matched form | n |
|---|---|---:|
| FALSE | igi-ni/zu/bi/mu-še₃ = 'before him/you/it' (pronominal) | 38 |
| TRUE | igi + PN/DN + -še₃ (genuine witness clause) | 36 |
| FALSE | igi-nim = 'upper/northern', a different lexeme | 10 |
| UNCLEAR | unclassified by the discriminators | 5 |
| FALSE | igi + numeral = accounting expression, not a witness | 3 |

### `son_of_PN` — claimed role: filiation / lineage

Regex: `\bdumu\b[\s\-][^\n]{0,40}`  
Matches: 1,302 — TRUE 1,008 / FALSE 58 / UNCLEAR 236

| Verdict | Interpretation of the matched form | n |
|---|---|---:|
| TRUE | dumu + PN (filiation) | 1,008 |
| UNCLEAR | unclassified by the discriminators | 163 |
| UNCLEAR | dumu-ni / dumu-munus etc. (possessed / compound) | 73 |
| FALSE | dumu-zi = Dumuzi (divine/personal name) | 58 |

### `excess_diri` — claimed role: excess / surplus

Regex: `\bdiri\b[^\n]{0,40}`  
Matches: 62 — TRUE 3 / FALSE 13 / UNCLEAR 46

| Verdict | Interpretation of the matched form | n |
|---|---|---:|
| UNCLEAR | unclassified by the discriminators | 24 |
| UNCLEAR | diri-ga / bare diri (verbal 'to exceed', or surplus) | 22 |
| FALSE | diri + month name = INTERCALARY MONTH, not a ledger surplus | 13 |
| TRUE | diri + quantity (surplus amount) | 3 |

### `seal_of_PN` — claimed role: identity / authentication

Regex: `\bkišib(?:₃)?\b[^\n]{0,40}`  
Matches: 301 — TRUE 253 / FALSE 11 / UNCLEAR 37

| Verdict | Interpretation of the matched form | n |
|---|---|---:|
| TRUE | kišib₃ + PN/title (seal of so-and-so) | 253 |
| UNCLEAR | unclassified by the discriminators | 37 |
| FALSE | kišib₃-bi N = 'its sealed tablets: N' (a count, not an attribution) | 11 |

### `received_by` — claimed role: transaction confirmation

Regex: `\bšu\s+ba-ti\b`  
Matches: 120 — TRUE 120 / FALSE 0 / UNCLEAR 0

| Verdict | Interpretation of the matched form | n |
|---|---|---:|
| TRUE | šu ba-ti = 'received' (fixed formula) | 120 |

### `speak_to_him` — claimed role: letter address formula

Regex: `\bu₃-na-a-du₁₁\b`  
Matches: 297 — TRUE 297 / FALSE 0 / UNCLEAR 0

| Verdict | Interpretation of the matched form | n |
|---|---|---:|
| TRUE | u₃-na-a-du₁₁ = 'speak to him' (fixed formula) | 297 |

### `total_audit` — claimed role: ledger total / audit line

Regex: `\bšu-nigin₂?\b[^\n]{0,40}`  
Matches: 22 — TRUE 22 / FALSE 0 / UNCLEAR 0

| Verdict | Interpretation of the matched form | n |
|---|---|---:|
| TRUE | šu-nigin₂ = 'sum total' | 22 |

## Probes that never fire

`phase1_templates.py` skips any probe with zero tablet hits (`if tablet_hits == 0: continue`), so a probe whose regex does not match the corpus's transliteration conventions disappears from `templates.json` without any warning. These probes produced **no matches at all**:

- `credit_mu_DU` — regex `\bmu-DU\b[^\n]{0,40}`

## Prevalence — attested is not the same as characteristic

Percentage of tablets **in each genre** carrying each pattern. A pattern can be real, well-attested, and still be far too rare to describe a genre's normal practice — which is a different claim from the one a reader takes away from 'administrative tablets close with a sum-total'.

| Pattern | Administrative | Letter | Lexical | Literary | Royal Inscription |
|---|---:|---:|---:|---:|---:|
| seal_of_PN | 25.4% | 8.4% | 1.4% | 3.6% | 11.0% |
| year_formula (strict) | 70.2% | 45.4% | 2.9% | 29.8% | 41.8% |
| total_audit | 2.2% | 0.2% | 0.0% | 1.2% | 0.2% |
| deficit_la2ia3 | 3.4% | 1.8% | 1.4% | 0.4% | 0.8% |
| excess_diri | 4.2% | 0.4% | 0.0% | 2.2% | 3.4% |
| witness_eye (non-pronominal) | 0.4% | 0.6% | 0.0% | 3.0% | 1.0% |
| received_by | 15.2% | 2.2% | 0.0% | 0.8% | 5.0% |

**Read this table before citing any frequency from `templates.json`.**
