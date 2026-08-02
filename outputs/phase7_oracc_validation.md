# Phase 7 — Probe validation against Oracc's expert lemmatisation

Phase 1b audited the regex probes using discriminators I wrote. Conservative, but one non-specialist's judgement. **This replaces that judgement with published Assyriological work.**

[Oracc](http://oracc.museum.upenn.edu) distributes the ePSD2 Ur III administrative corpus with every token carrying an expert-assigned citation form (`cf`), guide word (`gw`) and part of speech (`pos`). `pos` separates **PN** (personal name) from **N** (common noun) — precisely the distinction no regex can make, and the one that broke `king_title`.

For each probe, its head lexeme is looked up across the whole Ur III corpus and the expert annotation is tallied. The accept rule for each probe is deliberately generous, so these figures are an **upper bound** on probe quality.

## Results

| Probe | Head | Claimed role | Oracc occurrences | **Precision vs Oracc** | POS mix |
|---|---|---|---:|---:|---|
| `king_title` | `lugal` | title: king | 73,749 | **58.0%** | N 42,861, PN 30,381, u 340 |
| `year_formula` | `mu` | temporal index (year-name) | 94,309 | **70.6%** | N 83,151, V/t 4,684, V/i 3,578 |
| `witness_eye` | `igi` | witness presence | 7,213 | **71.5%** | N 5,634, PN 1,446, FN 60 |
| `excess_diri` | `diri` | excess / surplus | 3,687 | **94.3%** | V/i 3,658, PN 14, X 9 |
| `son_of_PN` | `dumu` | filiation / lineage | 53,359 | **95.4%** | N 53,199, X 72, PN 41 |
| `ensi_title` | `ensi` | title: governor | 9,379 | **98.6%** | N 9,322, PN 48, u 4 |
| `received_by` | `ba-ti` | transaction confirmation | 14,452 | **99.8%** | V/i 14,426, PN 20, N 4 |
| `seal_of_PN` | `kišib` | identity / authentication | 30,044 | **100.0%** | N 30,030, X 10, PN 2 |
| `total_audit` | `šu-niŋin` | ledger total | 0 | — | not attested |

## What Oracc says each head token actually is

### `king_title` — head `lugal`, claimed *title: king*

A PN tag means the match is a personal-name element, not the title.

| Citation form | Guide word | POS | n | Counts as correct |
|---|---|---|---:|:---:|
| lugal | king | N | 42,746 | yes |
| Lugalemahe | 0 | PN | 2,216 | **no** |
| Lugalezem | 0 | PN | 1,802 | **no** |
| Lugalkugzu | 0 | PN | 1,705 | **no** |
| Lugalmagure | 0 | PN | 1,292 | **no** |
| Lugalazida | 0 | PN | 1,154 | **no** |
| Lugalkugani | 0 | PN | 1,133 | **no** |
| Lugalniŋlagare | 0 | PN | 1,067 | **no** |

### `seal_of_PN` — head `kišib`, claimed *identity / authentication*

| Citation form | Guide word | POS | n | Counts as correct |
|---|---|---|---:|:---:|
| kišib | seal | N | 30,003 | yes |
| kišibla | wrist | N | 26 | yes |
| — | — | X | 10 | **no** |
| — | — | u | 2 | **no** |
| Kišib₃.NE | 00 | PN | 1 | **no** |
| dub | tablet | N | 1 | **no** |
| Kišib₃.ur.nin.geš.zi.da | 00 | PN | 1 | **no** |

### `son_of_PN` — head `dumu`, claimed *filiation / lineage*

dumu-zi (the deity Dumuzi) should surface as DN, not as 'child'.

| Citation form | Guide word | POS | n | Counts as correct |
|---|---|---|---:|:---:|
| dumu | child | N | 50,881 | yes |
| dumumunus | daughter | N | 819 | **no** |
| dumunita | son | N | 660 | **no** |
| dumudaba | worker₂ | N | 353 | **no** |
| dumugugur | worker | N | 216 | **no** |
| dumudaba | worker₁ | N | 136 | **no** |
| dumugir | citizen | N | 133 | **no** |
| — | — | X | 72 | **no** |

### `witness_eye` — head `igi`, claimed *witness presence*

igi also means 'eye/front'; the witness reading needs the igi PN-še₃ frame.

| Citation form | Guide word | POS | n | Counts as correct |
|---|---|---|---:|:---:|
| igi | face | N | 2,901 | yes |
| igi | eye | N | 2,254 | yes |
| igikarag | delivery | N | 261 | **no** |
| Igi.e₂.mah | 00 | PN | 130 | **no** |
| IgiŠarak | 0 | PN | 128 | **no** |
| Igianakezu | 0 | PN | 108 | **no** |
| Igisagsag | 0 | PN | 98 | **no** |
| igiduh | seer | N | 89 | **no** |

### `year_formula` — head `mu`, claimed *temporal index (year-name)*

mu is also 'name', and mu- is a verbal prefix.

| Citation form | Guide word | POS | n | Counts as correct |
|---|---|---|---:|:---:|
| mu | year | N | 66,614 | yes |
| mu.DU | delivery | N | 8,266 | **no** |
| mu | name | N | 7,955 | **no** |
| du | build | V/t | 3,687 | **no** |
| hulu | bad | V/i | 3,082 | **no** |
| Mušudu | 1 | MN | 1,035 | **no** |
| Muriqtidnim | 1 | ON | 832 | **no** |
| dim | create | V/t | 733 | **no** |

### `excess_diri` — head `diri`, claimed *excess / surplus*

diri also marks an intercalary month.

| Citation form | Guide word | POS | n | Counts as correct |
|---|---|---|---:|:---:|
| dirig | exceed | V/i | 3,476 | yes |
| dirig | float | V/i | 182 | **no** |
| Watartum | 0 | PN | 14 | **no** |
| — | — | X | 9 | **no** |
| — | — | u | 3 | **no** |
| Watartum | 1 | DN | 2 | **no** |
| Diri.tar | 00 | FN | 1 | **no** |

### `received_by` — head `ba-ti`, claimed *transaction confirmation*

šu ba-ti is a fixed receipt formula.

| Citation form | Guide word | POS | n | Counts as correct |
|---|---|---|---:|:---:|
| teŋ | near | V/i | 14,426 | yes |
| Ba.ti.ti | 00 | PN | 11 | **no** |
| batiʾum | container | N | 4 | **no** |
| Ba.ti.la | 00 | PN | 3 | **no** |
| Ba.ti.um.ma | 00 | PN | 2 | **no** |
| Ba.ti.mu | 00 | PN | 2 | **no** |
| — | — | u | 1 | **no** |
| Ba.ti.ir | 00 | PN | 1 | **no** |

### `ensi_title` — head `ensi`, claimed *title: governor*

| Citation form | Guide word | POS | n | Counts as correct |
|---|---|---|---:|:---:|
| ensik | ruler | N | 9,250 | yes |
| ensikgal | steward | N | 59 | **no** |
| Ensi₂ | 00 | PN | 46 | **no** |
| ensi | interpreter | N | 13 | **no** |
| — | — | u | 4 | **no** |
| — | — | X | 4 | **no** |
| Ensi₂.aš | 00 | PN | 1 | **no** |
| Ensi₂.GAN₂.en.ki | 00 | FN | 1 | **no** |

## Synthesis — how this compares to my own audit (Phase 1b)

| Probe | Phase 1b (my discriminators) | Phase 7 (Oracc gold) | Agreement |
|---|---:|---:|---|
| `seal_of_PN` | 96% | **100.0%** | confirmed |
| `received_by` | 100% | **99.8%** | confirmed |
| `son_of_PN` | 95% | **95.4%** | confirmed |
| `king_title` | 42% | **58.0%** | same verdict, different magnitude |
| `witness_eye` | 41% | **71.5%** | **I was too harsh** |
| `year_formula` | 34% | **70.6%** | **I was too harsh** |
| `excess_diri` | 19% | **94.3%** | **I was wrong** |

### The two audits measure different things, and that is the point

Oracc answers *is this token the lexeme the probe names?* Phase 1b answered *is this match the grammatical construction the probe claims?* Those come apart:

- **`year_formula`** — Oracc says 70.6% of `mu` tokens are the year lexeme, but the probe claims a year *formula* (`mu` + event name). A token can correctly be the year-lexeme and still not sit in a year formula, so Phase 1b's stricter 34% is not refuted — it answers the narrower question.
- **`witness_eye`** — Oracc says 71.5% are the `igi` lexeme (*eye/face*). The witness reading needs the `igi PN-še₃` frame, which token-level annotation does not check.
- **`excess_diri`** — here I was simply **wrong**. Oracc lemmatises 94.3% as `dirig` *exceed*, the sense the probe claims. My intercalary-month objection was misplaced: an intercalary month is named with that same lexeme, so the token identification was right all along.

### What is now settled

**`king_title` is broken, confirmed by expert annotation.** Of 73,749 occurrences Oracc tags **30,381 (41%) as PN — personal names** — against 42,861 as the common noun *king*. The probe reports 48.6% of administrative tablets carrying a royal title; a large share of that is people named Lugal-something. This is the failure mode no regex can avoid, and the clearest argument for annotation over pattern-matching.

**Four probes are validated at 95–100% against gold annotation**: `seal_of_PN`, `received_by`, `ensi_title`, `son_of_PN`. Every headline frequency in this repository rests on that group — the reassuring half of this result.

**My own audit was systematically too harsh on three probes.** Worth stating plainly: a conservative hand-built discriminator over-flags, and without gold annotation there was no way to know by how much. Phase 1b remains the right tool for construction-level validity and the wrong tool for lexeme identity.

**Unresolved:** `total_audit` — the head token as written here did not match any Oracc form, so no gold comparison was obtained. This is a limitation of the lookup, not evidence about the probe.

## Source and license

Oracc ePSD2 `admin/ur3`, CC BY-SA. Cite ePSD2 alongside this repository if you use these figures. Oracc is not affiliated with this work and has not reviewed it.
