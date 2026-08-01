# Sumerian Agent Patterns

**Empirical mining of the SumTablets cuneiform corpus (91,606 tablets, 6.97M glyphs) for software-design primitives applicable to modern multi-agent AI systems.**

> **Read [CORRECTIONS.md](CORRECTIONS.md) first.** One headline finding in the original release (RULING-parity, §4) was withdrawn on 2026-07-31 after a self-audit found it was an artifact of the wrong null hypothesis. The corpus statistics, the ELS null result, and the engineering benchmark are unaffected. Every claim below is now tagged with its evidence strength.

> Sumerian scribes ran a multi-agent bureaucracy 4,000 years ago. Their clay tablets carry sealed envelopes, named time periods, periodic audits, RPC headers, and witness sets — the same primitives modern agent systems are reinventing. This repo mines that corpus for those primitives, reports each one with its evidence strength and cited tablet IDs, and translates them into agent-framework code shapes. Descriptive corpus statistics and an engineering benchmark carry the weight; one inferential claim was tested, failed, and is documented as withdrawn.

**Who this is for:**
- Multi-agent / LLM agent framework developers (LangGraph, AutoGen, CrewAI, custom runtimes)
- Researchers in agentic AI, cognitive architectures, distributed systems
- Anyone designing memory layers, identity/auth subsystems, or audit logs for AI agents
- Cuneiform / Assyriology researchers curious about cross-disciplinary applications

---

## Start Here — The Evidence-Backed Artifacts

Of the ~158 ideas in `outputs/FULL_IDEAS.md`, the following **9 first-class artifacts** carry real evidence (statistical results, cited tablet IDs, or measured benchmarks). The rest of the catalog is brainstorm-grade — useful for ideation, but not load-bearing. Start here:

| # | Artifact | Where | What it gives you |
|---|---|---|---|
| 1 | **Empirical method** — a reproducible corpus-mining pipeline with permutation nulls and Bonferroni correction, including the null-choice failure it caught in its own output | `scripts/phase{0,1,3}_*.py` | A pipeline you can re-run on any corpus to extract templates + structure, and a worked lesson in picking the null |
| 2 | **9 named agent primitives** with cited tablet IDs and contracts | `outputs/primitives.json` | Single-responsibility agent designs grounded in real attestations (P/Q tablet IDs) |
| 3 | **Zipf-as-DSL detector finding** (Admin s=1.746, Royal s=1.737, Lexical s=1.114) | `outputs/compression_findings.md` §1 | Empirical method for unsupervised "is-this-a-DSL?" classification of any corpus |
| 4 | **RULING-parity — NULL result** (claim withdrawn 2026-07-31, see [CORRECTIONS.md](CORRECTIONS.md)) | `outputs/compression_findings.md` §4 | A worked example of how the choice of null hypothesis manufactures a finding — and how it was caught |
| 5 | **ELS-null result** — 3 nominal hits at p<0.01 across 495 tests, against ~5 expected by chance | `outputs/compression_findings.md` §3 | Defensive prior art against future numerology / "hidden code" claims on cuneiform |
| 6 | **Reference architecture** — composes the primitives into a multi-agent design with Python + Rust pseudocode | `outputs/reference_architecture.md` | Drop-in design doc you can adapt to any agent runtime |
| 7 | **Quantitative benchmark** — sealed envelope vs anonymous baseline, measured | `benchmarks/RESULTS.md` | Hard numbers (+59% bytes, +37 tokens, +7µs per write) and a 5/5-vs-0/5 capability comparison |
| 8 | **Reference implementation** of `kishib3` (sealed envelope) in 250 LoC stdlib Python | `benchmarks/kishib3.py` | Working code for one of the primitives — clone, adapt, ship |
| 9 | **5 unmined research directions** from data we already have on disk | `outputs/FULL_IDEAS.md` §N (items N1, N4, N5, N9, N12) | Named-person social network (N1), region-scoped authority (N4), votive ledger pattern (N5), multi-tablet narratives (N9), kišib₃ undercount (N12) |

**Honest framing:** the ~158-idea catalog in `FULL_IDEAS.md` is preserved for browsability, but most of it is restatements of these 9 artifacts in different framings, branding gimmicks (Sumerian-named libraries that are the primitives renamed), or ephemera. If you only have 30 minutes, read `outputs/summary.md` + `benchmarks/RESULTS.md`. If you have an hour, add `outputs/reference_architecture.md`.

---

## Claims and Evidence Strength

Every substantive claim in this repo, and exactly how much weight it can bear. Read this before citing anything.

| Claim | Evidence type | Strength | Notes |
|---|---|---|---|
| `kišib₃` (seal) appears in 25.4% of Administrative tablets; year-formulae in 74.2%; `u₃-na-a-du₁₁` in 58.8% of Letters | Regex counts over a 2,069-tablet sample | **Solid** — descriptive | No inference. Reproducible exactly. Sensitive to regex design; probes are in `phase1_templates.py` and worth reading before trusting a number. |
| Administrative and Royal Inscription are more formulaic than natural language (Zipf s ≈ 1.75 / 1.74 vs Lexical 1.11) | Zipfian fit, R² 0.92–0.95 | **Solid** — descriptive | "DSL" is an analogy, not a formal claim. A high Zipf exponent means a small high-reuse vocabulary; it does not establish a grammar. |
| Genres carry structural redundancy beyond token frequency (compression Δ +0.05 to +0.10) | zlib ratio, real vs token-shuffled | **Moderate** — descriptive | The token-shuffle baseline is legitimate *here*, because the claim is only "more structured than random token order". Δ magnitudes are not comparable across genres of different lengths. |
| No hidden periodic encoding in the corpus | ELS scan, 99 skips × 5 genres × 1,000 permutations | **Moderate** — null result | 3 nominal hits (p<0.01) vs ~5 expected by chance. **Underpowered for the Bonferroni threshold it originally claimed** — see §3 resolution caveat. Reads as "no signal above chance", not as a proof of absence. |
| Sealed envelopes answer 5/5 audit queries; anonymous logs 0/5, at +59% bytes / +37 tokens / +7µs per write | Executed benchmark, 100k writes | **Solid** — engineering measurement | Not a statistical claim. The 0/5 is definitional (an anonymous log lacks the fields), so it demonstrates a design consequence, not a discovery. Latencies are hardware-dependent. |
| ~~`<RULING>` marks logical row boundaries~~ | Permutation test | **WITHDRAWN** | Artifact of the wrong null. See [CORRECTIONS.md](CORRECTIONS.md). |
| The 9 named agent primitives | Hand-authored mapping from templates | **Design proposal** | Grounded in cited tablet IDs, but the mapping from a Sumerian formula to an agent contract is an argument, not a measurement. `primitives.json` tags each as `validated` or `speculative` — that flag refers to whether the *pattern* was observed, never to whether the agent design works. |
| Three-tier SURFACE → COLUMN → RULING memory | — | **Untested proposal** | Its empirical support was the withdrawn claim above. |
| The reference architecture, `FULL_IDEAS.md`, `summary.md` | Hand-authored | **Ideation** | No evidence claimed. Not generated by any script. |

**The honest summary:** this repo's defensible contributions are (a) a reproducible corpus-mining pipeline, (b) descriptive statistics on genre formulaicity, (c) a null result on hidden encodings, (d) an engineering benchmark for provenance-carrying write logs, and (e) a documented worked example of a null-hypothesis error and its correction. The mapping from cuneiform to agent design is an argument offered for its generative value, not a validated result — and the one place that mapping was given inferential backing, the backing did not survive audit.

---

## Why You Should Care (Findings → Actions)

Three concrete things you can build differently after reading this:

### 1. Wrap every agent write in a sealed envelope

**Finding.** 25.4% of administrative tablets carry `kišib₃` (seal of so-and-so), 74.2% are dated by year, and witness clauses (`igi PN-šè`) are common. No important write is anonymous, undated, or unattributed. Tablets P101440, P132611, P117793, P145759.

**Action.** Make every state-changing call in your agent runtime carry `(payload, by_seal, witnesses, period)`. Audit becomes a property of the envelope, not a separate concern bolted on per agent. Replay across any time window becomes trivial.

**Measured impact** ([benchmarks/RESULTS.md](benchmarks/RESULTS.md)). We built a minimal sealed-envelope library (`benchmarks/kishib3.py`, 250 LoC, stdlib only) and ran 100,000 writes through both it and an anonymous-log baseline:
- **Cost**: +37 tokens / write (estimated), +7 µs latency / write, +59 % bytes at 250-byte payloads (drops to ~14 % at 1 KB payloads, ~1.4 % at 10 KB).
- **Capability**: sealed log answers 5/5 audit queries (who wrote X, all writes by principal, all writes in period, integrity verification, replay-after-cascade-revoke). Anonymous log answers **0 of 5**. The capability gap is total, not partial.
- **The killer query**: replay-as-of after revoking a parent principal. Baseline returns all 50 writes (silent drift). Sealed log returns 0 — every revoked descendant is correctly excluded.

### 2. Tier your agent memory as session → topic → row — *design proposal, not a finding*

**Status.** This section previously claimed statistical confirmation that `<RULING>` is a logical row separator (Royal p=0.002, Admin p=0.005). **That claim is withdrawn.** It came from a null hypothesis that shuffled the tablet's tokens, which destroys all local structure and therefore only shows that Sumerian text is locally coherent — true of any natural language. Under a null that varies *only where the boundaries fall*, the effect disappears entirely in every genre. See [CORRECTIONS.md](CORRECTIONS.md) and `outputs/compression_findings.md` §4.

**What is still true.** Tablets do carry three nested physical structures — surface, column, and ruling-delimited row. That is a description of the artifact, not a statistical result.

**The proposal.** Tiering agent memory as SURFACE (session) → COLUMN (topic) → RULING (row), where reads return the smallest tier that satisfies the query, is a reasonable design. It is offered here as an untested idea. This repo provides no evidence that it works.

### 3. Replace silent token/cost rollups with periodic signed audits

**Finding.** Administrative tablets close with `šu-nigin₂` (sum-total) — a periodic reconciliation. Shortfalls and excesses are named explicitly: `la₂-ia₃` (deficit owed by named person), `diri` (excess). Nothing drifts silently.

**Action.** For any ledger-shaped agent state (token usage, tool-call counts, cost tracking, evidence accumulation), close periods at fixed intervals with a signed audit. Deficits and excesses must be named and attributed to a counterparty.

**Plus a defensive null result:** A 99-skip × 5-genre × 1,000-permutation ELS scan found no periodic encoding — 3 nominally significant hits (p<0.01) across 495 tests, where chance alone predicts ~5. Useful prior art if anyone tries to sell you "Sumerian secret-code AI."

*Stated precisely, because it matters:* at 1,000 permutations the smallest attainable p is ~0.001, which is ~10× the Bonferroni threshold — so this scan **cannot** return a Bonferroni-significant result by construction, and the earlier "0 of 495 Bonferroni-significant" framing overstated its power. The informative comparison is the uncorrected hit rate against chance expectation, above.

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
| ~~`<RULING>` is a logical row separator~~ **WITHDRAWN** | Null under the correct control; the original p-values came from a null that destroys all local structure ([CORRECTIONS.md](CORRECTIONS.md)) | Royal, Admin |
| No hidden encodings in the corpus | 3 of 495 ELS tests nominally p<0.01, vs ~5 expected by chance | All genres |
| Seal-of-PN clauses are pervasive | 25.4% of Admin tablets | Administrative |
| Year-formulas are universal envelopes | 74.2% Admin, 65% Letter, 62.4% Royal | Across genres |
| Letters are addressed RPCs | `u₃-na-a-du₁₁` in 58.8% of Letters | Letter |

Full statistics with shuffled-baseline controls in `outputs/compression_findings.md`. Per-tablet pattern citations in `outputs/templates.json`.

---

## Repository Layout

```
.
├── README.md                          this file
├── CORRECTIONS.md                     dated log of retracted / revised claims -- read first
├── REVIEWERS.md                       where to attack this, for reviewers
├── CITATION.cff                       citation metadata
├── LICENSE                            CC BY 4.0 (docs and analysis artifacts)
├── LICENSE-CODE                       MIT (Python scripts)
├── requirements.txt                   Python deps
├── scripts/
│   ├── phase0_sample.py               loads SumTablets, builds stratified samples
│   ├── phase1_templates.py            extracts genre templates and probe hits
│   └── phase3_compression.py          Zipf, compression, ELS, RULING-parity analysis
├── benchmarks/
│   ├── kishib3.py                     reference sealed-envelope implementation (~250 LoC)
│   ├── baseline_log.py                anonymous-log comparison point (~50 LoC)
│   ├── benchmark.py                   harness — overhead + capability comparison
│   ├── results.json                   raw measurement output
│   └── RESULTS.md                     report with measured numbers and caveats
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

**Requirements:** Python ≥ 3.10. No GPU, no API keys, no HuggingFace account. Total runtime ≈ 8 minutes on a laptop (phase 3 dominates at ~5 min). Disk: 48 MB of parquet in `data/`, plus a HuggingFace `datasets` cache of similar size on first download.

```bash
git clone https://github.com/NORTHTEKDevs/sumerian-agent-patterns.git
cd sumerian-agent-patterns

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/phase0_sample.py       # ~2 min  downloads SumTablets, caches parquet, builds samples
python scripts/phase1_templates.py    # ~10 s   writes outputs/templates.json
python scripts/phase3_compression.py  # ~5 min  writes outputs/compression_findings.md + phase3_raw.json
```

The corpus benchmark is independent of the above — pure stdlib, no dependencies, no corpus:

```bash
cd benchmarks && python benchmark.py   # ~6 s, writes results.json
```

### Verifying your run matched

The committed files in `outputs/` are exactly what these scripts produce. After a full re-run:

```bash
git diff --stat outputs/
```

**Expected: no output.** Anything else is a genuine divergence worth an issue.

What you should see in the console along the way — these are the load-bearing numbers:

| Check | Expected | Where |
|---|---|---|
| Corpus rows loaded | 91,606 | phase 0 |
| Stratified sample | 2,069 tablets + 197 long-form | phase 0 |
| `seal_of_PN` in Administrative | 25.4% (n=127) | phase 1 |
| Zipf s — Admin / Royal / Lexical | 1.746 / 1.737 / 1.114 | phase 3 |
| RULING parity (primary null) | not significant in any genre | phase 3 |
| ELS nominal hits (p<0.01) | **3** of 495, vs ~5 expected by chance | phase 3 |
| Sealed-vs-anonymous audit queries | 5/5 vs 0/5 | benchmark |

### Reproducibility caveats — read before filing an issue

- **`benchmarks/results.json` is not byte-reproducible, by design.** Seal IDs come from `secrets.token_hex`, and absolute latencies are hardware-dependent. The byte/token overheads and the 5/5-vs-0/5 capability result are stable; the µs figures will not match ours.
- **`benchmarks/RESULTS.md` is hand-authored** and is not regenerated by `benchmark.py`. It interprets `results.json`.
- **Determinism depends on your NumPy version.** Phase 3 draws every shuffle from one seeded `np.random.default_rng(42)` consumed sequentially across all four analyses. NumPy does not guarantee `Generator` stream stability across major versions, so a future NumPy could shift the ELS reference tables. It is stable across NumPy 2.x — verified end-to-end on 2.5.1. The ELS null conclusion is not sensitive to this.
- **There is no `phase2` script.** Phase 2 was the hand-authored mapping step from templates to agent primitives; its output is `outputs/primitives.json`. The numbering is historical, not a missing file.
- The pipeline is stage-ordered: phase 1 and phase 3 both read the parquet files that phase 0 writes into the (gitignored) `data/` directory. Run phase 0 first.

**Verified end-to-end on 2026-07-31:** clean clone, fresh venv, Python 3.14.2, Windows 11, `datasets` 5.0.1 / `pandas` 3.0.5 / `numpy` 2.5.1 / `scipy` 1.18.0. `outputs/templates.json` and `outputs/phase3_raw.json` regenerated byte-identical to the committed copies.

`reference_architecture.md`, `summary.md`, `FULL_IDEAS.md`, and `primitives.json` are hand-authored design artifacts that cite outputs from the scripts — they are not regenerated by any script.

## Methodology

1. **Sample.** Stratified-sample 500 tablets per genre (Administrative, Literary, Lexical, Royal Inscription, Letter) plus up to 50 long-form tablets per genre. Total sample: 2,069 tablets + 197 long-form.
2. **Templates.** For each genre: structural-marker statistics (`<SURFACE>`, `<COLUMN>`, `<RULING>`, `<BLANK_SPACE>`); per-position opening/closing line templates; distinctive bigrams and trigrams via genre log-odds vs other genres; hand-coded regex probes for known bureaucratic primitives (seal-of, year-formula, total/audit, deficit, witness, etc.). Every template carries cited tablet IDs.
3. **Compression and ELS.** Per-genre Zipfian fit; compression-ratio Δ between raw and shuffled token streams; equidistant-letter-sequence (ELS) decimation at skips 2–100 with 1,000 shuffled-baseline controls (Bonferroni-corrected for 495 tests); cross-RULING trigram parity against two nulls — a token-shuffle null (retained only to show it is the wrong control) and a boundary-permutation null that holds token order and chunk lengths fixed and varies only where the cuts fall (the primary test).
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
