# Phase 15b — Precision audit of the strict year-name probe

Graduation threshold fixed before the run: >= 95% precision (TRUE vs TRUE+FALSE, conservative discriminators, FALSE only where unambiguous) lifts phase 15's provisional flag; the worst-case bound (every UNCLEAR counted FALSE) must also stay above 75%.

Matches audited: **79,993** across 59,053 administrative tablets.

| Verdict | n | share |
|---|---:|---:|
| TRUE (year-name context) | 50,221 | 62.8% |
| FALSE (oath / purpose clause) | 8,624 | 10.8% |
| UNCLEAR | 21,148 | 26.4% |

**Precision (excl. UNCLEAR): 85.3%** · worst-case (all UNCLEAR as FALSE): 62.8% · oath-class contamination: 1 matches (0.00% of all matches) — the gate's named false-positive class is measured, not assumed.

**Independent ePSD2 criterion (c):** standalone `mu` tokens in the expert lemmatisation: 74,328 total, 66,517 with guide-word 'year' = **89.5%** (required >= 90%): NOT MET.

## Verdict: **NOT GRADUATED** (iteration 2; tri-criteria fixed pre-run)

Phase 15's year-name-dependent results remain provisional. The bucket tables below say what the probe is actually matching.

### Top TRUE buckets

| Pattern | n |
|---|---:|
| GN destroyed (year-event) | 17,422 |
| royal name + lugal (regnal year) | 11,134 |
| priest/official installed (year-event) | 7,969 |
| built/fashioned (year-event) | 6,532 |
| en chosen by omen (year-event) | 1,957 |
| boat caulked (year-event) | 1,666 |
| campaign toponym (year-event) | 1,515 |
| en of deity (year-event, possibly line-split) | 798 |

### Top FALSE buckets

| Pattern | n |
|---|---:|
| duration count (mu + numeral = 'N years') | 8,241 |
| oath: by its king | 222 |
| purpose clause (-še₃) | 160 |
| oath formula (swore by the name) | 1 |

### Top UNCLEAR buckets

| Pattern | n |
|---|---:|
| šu ba-ti | 1,219 |
| maškim | 929 |
| i₃-dab₅ | 594 |
| dub-sar | 405 |
| ma₂-dara₃-abzu ba-ab-du₈ | 326 |
| aga₃-us₂-e-ne-še₃ | 269 |
| sukkal | 200 |
| en eridu{ki} | 197 |
| si-ma-num₂{ki} | 185 |
| ... | 179 |
| hu-hu-nu-ri{ki} | 143 |
| engar | 116 |
| amar{d}suen lugal | 114 |
| šu{d}suen lugal | 113 |
| {d}i-bi₂ | 112 |

Conservative by construction: FALSE requires an unambiguous oath/purpose surface form, so the reported precision is not inflated by charitable UNCLEAR handling — UNCLEAR is excluded from the headline and bounded by the worst-case figure.
