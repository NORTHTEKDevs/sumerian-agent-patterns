# Sumerian Agent Patterns

**Empirical mining of the SumTablets cuneiform corpus (91,606 tablets, 6.97M glyphs) for software-design primitives applicable to modern multi-agent AI systems.**

> Sumerian scribes ran a multi-agent bureaucracy 4,000 years ago. Their clay tablets carry sealed envelopes, named time periods, periodic audits, RPC headers, and witness sets — the same primitives modern agent systems are reinventing. This repo statistically validates which patterns are real (with p-values and cited tablet IDs) and translates them into agent-framework code shapes.

**Who this is for:**
- Multi-agent / LLM agent framework developers (LangGraph, AutoGen, CrewAI, custom runtimes)
- Researchers in agentic AI, cognitive architectures, distributed systems
- Anyone designing memory layers, identity/auth subsystems, or audit logs for AI agents
- Cuneiform / Assyriology researchers curious about cross-disciplinary applications

---

## Why You Should Care (Findings → Actions)

Three concrete things you can build differently after reading this:

### 1. Wrap every agent write in a sealed envelope

**Finding.** 25.4% of administrative tablets carry `kišib₃` (seal of so-and-so), 74.2% are dated by year, and witness clauses (`igi PN-šè`) are common. No important write is anonymous, undated, or unattributed. Tablets P101440, P132611, P117793, P145759.

**Action.** Make every state-changing call in your agent runtime carry `(payload, by_seal, witnesses, period)`. Audit becomes a property of the envelope, not a separate concern bolted on per agent. Replay across any time window becomes trivial.

### 2. Tier your agent memory as session → topic → row

**Finding.** Sumerian tablets have three layers of structure: physical surface (obverse/reverse), logical column, atomic row marked by `<RULING>`. We statistically confirmed `<RULING>` is a real row separator: adjacent ruling-bounded chunks share trigrams 30–500× more than shuffled baselines (Royal Inscription p=0.002, Administrative p=0.005).

**Action.** Replace flat agent memory with three tiers: SURFACE (session) → COLUMN (topic) → RULING (row). Reads return the smallest tier that satisfies the query — never drag back the whole session when one row answers.

### 3. Replace silent token/cost rollups with periodic signed audits

**Finding.** Administrative tablets close with `šu-nigin₂` (sum-total) — a periodic reconciliation. Shortfalls and excesses are named explicitly: `la₂-ia₃` (deficit owed by named person), `diri` (excess). Nothing drifts silently.

**Action.** For any ledger-shaped agent state (token usage, tool-call counts, cost tracking, evidence accumulation), close periods at fixed intervals with a signed audit. Deficits and excesses must be named and attributed to a counterparty.

**Plus a defensive null result:** A 99-skip × 5-genre × 1,000-shuffle ELS scan found zero hidden codes (0 of 495 Bonferroni-significant tests). Useful prior art if anyone tries to sell you "Sumerian secret-code AI."

> **Want more?** `outputs/summary.md` ranks the top 10 ideas by leverage. `outputs/FULL_IDEAS.md` lists ~158 across 16 categories. `outputs/reference_architecture.md` has full code shapes in Python and Rust.

---

## Architecture Overview

```
                     ┌────────────────────────────────────────┐
                     │           RoyalDecreeAgent             │
                     │  (policy/version registry, broadcasts) │
                     └────────────────┬───────────────────────┘
                                      │ subscribes
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌────────────────┐         ┌────────────────────┐        ┌─────────────────────┐
│ TempleLedger   │ ──uses──▶ CommodityLedgerLine │        │ AddressedMessage    │
│ Agent          │         │ Agent (stateless)   │        │ Agent (RPC-on-clay) │
└──────┬─────────┘         └─────────┬──────────┘         └─────────┬───────────┘
       │ writes                      │ canonicalizes                │ delivers
       ▼                             ▼                              ▼
┌────────────────┐         ┌─────────────────────┐         ┌──────────────────┐
│ SealAuthority  │◀────────│ LexicalOntology     │         │ RitualSequence   │
│ Agent          │         │ Agent (taxonomy)    │         │ Agent (workflow) │
└──────┬─────────┘         └─────────────────────┘         └──────────────────┘
       │ identity                                                  ▲
       ▼                                                           │
┌────────────────┐                                          ┌──────┴───────────┐
│ ScribalSchool  │                                          │ YearNameRegistry │
│ Agent          │                                          │ Agent (time)     │
└────────────────┘                                          └──────────────────┘
```

Nine named agent primitives. Three transverse subsystems: memory tiers, identity/provenance, taxonomy. See `outputs/reference_architecture.md` for the full design with Python + Rust code shapes.

---

## Concrete Example — One Tablet, Decomposed

**Tablet P101440 (Ur III administrative, 39 cuneiform glyphs):**

```
<SURFACE>
la₂-ia₃ 1(aš) gun₂ 5(u) 5(diš) ma-na siki du                  ← deficit line + commodity quantities
<unk> 5(gešʾu) 4(geš₂) 7(diš) a₂ geme₂ u₄ 1(diš)-še₃            ← labor accounting
kišib₃ {d}šul-gi-i₃-li₂                                         ← seal of Shulgi-ili
<SURFACE>
<BLANK_SPACE>
iti ezem-me-ki-gal₂                                             ← month: festival of Mekigal
mu us₂-sa ki-maš{ki} ba-...                                     ← year after the destruction of Kimaš
```

**The same tablet, decomposed into modern primitives:**

```python
WriteEnvelope(
  payload = LedgerEntry(
    lines = [
      Line(qty=Rational(1,1), unit="gun₂", commodity="siki", instrument="deficit"),  # la₂-ia₃
      Line(qty="5(gešʾu) 4(geš₂) 7(diš)", unit="labor-day", commodity="female-worker"),
    ],
  ),
  by_seal      = SealId("shulgi-ili-001"),         # kišib₃ {d}šul-gi-i₃-li₂
  witnesses    = [],                                # none recorded on this tablet
  period_id    = PeriodRegistry.resolve(
    name="iti ezem-me-ki-gal₂",
    year=YearName(derived_from="ki-maš destruction year", offset="us₂-sa"),  # mu us₂-sa
  ),
)
```

This is what every line in `outputs/templates.json` is doing — taking a real tablet's structural pattern and showing the modern primitive it implies.

---

## Glossary — Sumerian Terms Used

| Term | Literal | Modern equivalent |
|---|---|---|
| `kišib₃` (PN) | seal of [person name] | Cryptographic signature / write attribution |
| `mu` X | year of X | Named time period (event-named, not numeric) |
| `mu us₂-sa` X | year after the year of X | Relative time reference resolved at write-time |
| `iti` X | month of X | Calendar month sub-period |
| `šu-nigin₂` | sum-total | Periodic audit / signed reconciliation |
| `la₂-ia₃` | deficit | Named outstanding obligation (never silent) |
| `diri` | excess | Named surplus requiring disposition |
| `igi` PN-šè | before [person] | Witness clause — live attestation at write-time |
| `dumu` PN | son of [person] | Filiation edge in principal/identity graph |
| `u₃-na-a-du₁₁` | speak to him | Letter address formula — RPC envelope opener |
| `dub-ba-ni` | his tablet | Reference to a prior message (thread-id) |
| `lugal` | king | Top-tier role in authority graph |
| `ensi₂` | governor | Region-scoped authority role |
| `niga 4(diš)-kam` | grade-4 grain-fed | Numbered quality tier on a commodity (SLA tier) |
| `<SURFACE>` | physical face of tablet | L1 — Frame / session boundary |
| `<COLUMN>` | column on a surface | L2 — Section / topic boundary |
| `<RULING>` | drawn dividing line | L3 — Row / atomic record boundary |
| `<BLANK_SPACE>` | intentional gap | Semantic whitespace — preserve, don't trim |

---

## Findings (Detail)

The numbers behind the implications above. All claims here are reproducible from `scripts/phase3_compression.py` with seed=42.

| Finding | Statistic | Genre / Coverage |
|---|---|---|
| Admin tablets are a domain-specific language | Zipf exponent s = 1.746 (R²=0.93) | Administrative |
| Royal Inscription is the most-templated genre | Compression-Δ = +0.099 vs shuffled baseline | Royal Inscription |
| Lexical lists are closest to natural language | Zipf s = 1.114 (R²=0.92) | Lexical |
| Letters are short single-purpose RPCs | Lowest marker density (0.02 RULING/tab) | Letter |
| `<RULING>` is a logical row separator (not visual) | p = 0.002 (Royal), p = 0.005 (Admin) for cross-ruling trigram parity | Royal, Admin |
| No hidden encodings in the corpus | 0 of 495 ELS tests Bonferroni-significant | All genres |
| Seal-of-PN clauses are pervasive | 25.4% of Admin tablets | Administrative |
| Year-formulas are universal envelopes | 74.2% Admin, 65% Letter, 62.4% Royal | Across genres |
| Letters are addressed RPCs | `u₃-na-a-du₁₁` in 58.8% of Letters | Letter |

Full statistics with shuffled-baseline controls in `outputs/compression_findings.md`. Per-tablet pattern citations in `outputs/templates.json`.

---

## Repository Layout

```
.
├── README.md                          this file
├── LICENSE                            CC BY 4.0 (docs and analysis artifacts)
├── LICENSE-CODE                       MIT (Python scripts)
├── requirements.txt                   Python deps
├── scripts/
│   ├── phase0_sample.py               loads SumTablets, builds stratified samples
│   ├── phase1_templates.py            extracts genre templates and probe hits
│   └── phase3_compression.py          Zipf, compression, ELS, RULING-parity analysis
└── outputs/
    ├── templates.json                 229 templates × {genre, pattern, role, frequency, tablet IDs}
    ├── primitives.json                9 named agent primitives (6 rubric + 3 data-justified)
    ├── compression_findings.md        Phase 3 statistics with p-values
    ├── phase3_raw.json                machine-readable Phase 3 metric rows
    ├── reference_architecture.md      multi-agent reference architecture with code shapes
    ├── summary.md                     top-10 ideas ranked novelty × implementability
    └── FULL_IDEAS.md                  ~158 ideas across 16 categories
```

## How to Reproduce

```bash
pip install -r requirements.txt
python scripts/phase0_sample.py     # downloads SumTablets, persists local parquet, builds samples
python scripts/phase1_templates.py  # writes outputs/templates.json
python scripts/phase3_compression.py  # writes outputs/compression_findings.md + phase3_raw.json
```

All scripts are seeded (`random_state=42`, `np.random.default_rng(42)`) and reproducible end-to-end. Phase 0 downloads ~50 MB of corpus data from HuggingFace on first run, caches it locally as parquet, and reuses on subsequent runs.

`reference_architecture.md`, `summary.md`, `FULL_IDEAS.md`, and `primitives.json` are hand-authored design artifacts that cite outputs from the scripts.

## Methodology

1. **Sample.** Stratified-sample 500 tablets per genre (Administrative, Literary, Lexical, Royal Inscription, Letter) plus up to 50 long-form tablets per genre. Total sample: 2,069 tablets + 197 long-form.
2. **Templates.** For each genre: structural-marker statistics (`<SURFACE>`, `<COLUMN>`, `<RULING>`, `<BLANK_SPACE>`); per-position opening/closing line templates; distinctive bigrams and trigrams via genre log-odds vs other genres; hand-coded regex probes for known bureaucratic primitives (seal-of, year-formula, total/audit, deficit, witness, etc.). Every template carries cited tablet IDs.
3. **Compression and ELS.** Per-genre Zipfian fit; compression-ratio Δ between raw and shuffled token streams; equidistant-letter-sequence (ELS) decimation at skips 2–100 with 1,000 shuffled-baseline controls (Bonferroni-corrected for 495 tests); cross-RULING trigram parity vs within-tablet shuffled baseline.
4. **Mapping.** For each empirical template, propose a named single-responsibility agent primitive with inputs, outputs, state, tools, and guardrails. Distinguish validated-by-data from speculative.

## Honest Limits

- We sampled 2.3% of the corpus. Findings are strong for Ur III administrative tablets and Old Babylonian literary tablets; weaker for everything else.
- The corpus is 92%+ administrative — generalizing about "Sumerian thought" from this sample would be like generalizing about "civilization" from accounting receipts.
- Lexical findings rely on only 69 tablets; the Lexical-list architectural slot is real but the actual taxonomic content needs to come from external sources (CDLI, ePSD2).
- Sumerian seals were physical, witnessed, and socially backed — not cryptographic. The `SealAuthorityAgent` primitive borrows the *shape* (named principals, revocation, witness sets), not the threat model.
- Year-names are political artifacts named after royal acts, not a neutral monotonic clock.
- The general observation "Sumerian admin = proto-information-system" is well-established in popular essays. The contribution here is the *empirical statistical mining* with cited tablet IDs and shuffled-baseline controls — not the metaphor itself.

## Citation

If you find this useful in your own work, please cite the underlying corpus:

> Simmons, C., Diehl Martinez, R., & Jurafsky, D. (2024). *SumTablets: A Transliteration Dataset of Sumerian Tablets.* Workshop on Machine Learning for Ancient Languages (ML4AL), ACL 2024. https://aclanthology.org/2024.ml4al-1.20.pdf

Tablet IDs cited throughout (P-numbers and Q-numbers) are CDLI catalog entries and resolvable at:
- https://cdli.mpiwg-berlin.mpg.de/
- https://aicuneiform.com/

## License

- **Documentation and analysis artifacts** (`outputs/*`, `*.md`): [CC BY 4.0](LICENSE). Use freely with attribution.
- **Python scripts** (`scripts/*`): [MIT](LICENSE-CODE).

## Contributing

Issues and PRs welcome — particularly:
- Cross-validation against CDLI / Oracc / ePSD2
- Extension to Akkadian or other periods
- Counter-examples to any cited template
- Bug fixes in the analysis scripts
- Independent reproduction of Phase 3 statistics

## Acknowledgements

Built on top of the SumTablets corpus (Simmons et al., 2024, CC BY 4.0) and the broader work of the Cuneiform Digital Library Initiative, Oracc, ETCSL, ePSD2, and the cuneiform NLP community.
