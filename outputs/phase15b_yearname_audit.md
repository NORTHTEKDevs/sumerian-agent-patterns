# Phase 15b — Precision audit of the strict year-name probe

Graduation threshold fixed before the run: >= 95% precision (TRUE vs TRUE+FALSE, conservative discriminators, FALSE only where unambiguous) lifts phase 15's provisional flag; the worst-case bound (every UNCLEAR counted FALSE) must also stay above 75%.

Matches audited: **79,993** across 59,053 administrative tablets.

| Verdict | n | share |
|---|---:|---:|
| TRUE (year-name context) | 46,953 | 58.7% |
| FALSE (oath / purpose clause) | 388 | 0.5% |
| UNCLEAR | 32,652 | 40.8% |

**Precision (excl. UNCLEAR): 99.2%** · worst-case (all UNCLEAR as FALSE): 58.7% · oath-class contamination: 1 matches (0.00% of all matches) — the gate's named false-positive class is measured, not assumed.

## Verdict: **NOT GRADUATED**

Phase 15's year-name-dependent results remain provisional. The bucket tables below say what the probe is actually matching.

### Top TRUE buckets

| Pattern | n |
|---|---:|
| GN destroyed (year-event) | 17,430 |
| royal name + lugal (regnal year) | 11,134 |
| priest/official installed (year-event) | 7,970 |
| built/fashioned (year-event) | 6,536 |
| boat caulked (year-event) | 1,666 |
| campaign toponym (year-event) | 1,516 |
| wall built (year-event) | 360 |
| mu us₂-sa (derived year-name) | 341 |

### Top FALSE buckets

| Pattern | n |
|---|---:|
| oath: by its king | 222 |
| purpose clause (-še₃) | 165 |
| oath formula (swore by the name) | 1 |

### Top UNCLEAR buckets

| Pattern | n |
|---|---:|
| šu ba-ti | 1,219 |
| 2(aš) | 1,095 |
| maškim | 929 |
| 1(aš) | 840 |
| 3(aš) | 663 |
| i₃-dab₅ | 594 |
| en {d}nanna maš-e i₃-pa₃ | 490 |
| en {d}inana unu{ki} maš₂-e i₃-pa₃ | 407 |
| dub-sar | 405 |
| ma₂-dara₃-abzu ba-ab-du₈ | 326 |
| {d}šu{d}suen | 309 |
| aga₃-us₂-e-ne-še₃ | 269 |
| en {d}inana unu{ki}ga maš₂-e i₃-pa | 231 |
| sukkal | 200 |
| en eridu{ki} | 197 |

Conservative by construction: FALSE requires an unambiguous oath/purpose surface form, so the reported precision is not inflated by charitable UNCLEAR handling — UNCLEAR is excluded from the headline and bounded by the worst-case figure.
