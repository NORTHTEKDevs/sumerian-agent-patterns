# Sumerian Agent Patterns

**Empirical mining of the SumTablets cuneiform corpus (91,606 tablets, 6.97M glyphs) for software-design primitives applicable to modern multi-agent AI systems.**

> **The full research writeup is [PAPER.md](PAPER.md)** — abstract through threats-to-validity, every number CI-coupled to the generated data. **Start with [FINDINGS.md](FINDINGS.md)** — every claim this repo makes, ranked by strength, with the evidence and the limits of each. Then [CORRECTIONS.md](CORRECTIONS.md) for what was withdrawn and why.

> **Read [CORRECTIONS.md](CORRECTIONS.md) for the full retraction record.** A self-audit on 2026-07-31 withdrew two headline statistical findings — RULING-parity (wrong null hypothesis) and Zipf-as-DSL (stream-length artifact) — and a probe-precision audit found that **5 of 10 audited regex probes match a different lexeme than their label claims** and must not be cited. What survives: the compression-redundancy contrast (verified against a length control), the ELS null result, four precision-validated probe frequencies, and the engineering benchmark. Every claim is tagged with its evidence strength, and every correction is reproducible from the pipeline rather than asserted — see [`outputs/probe_validation.md`](outputs/probe_validation.md).

> Sumerian scribes ran a large administrative bureaucracy 4,000 years ago. Their clay tablets carry seal attributions, named time periods, sum-totals, and letter address formulae — recognisable ancestors of primitives modern agent systems are reinventing. This repo mines that corpus for those patterns, reports each with a measured precision and prevalence, and translates them into agent-framework code shapes. **Two statistical findings and five regex probes did not survive audit and are documented as withdrawn.** What carries weight: four precision-validated frequencies, one genre contrast verified against a length control, one null result, and an engineering benchmark.

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
| 3 | **Power-law analysis done properly** (Zipf-as-DSL withdrawn; replaced by a correct fit) | [`outputs/phase5_powerlaw.md`](outputs/phase5_powerlaw.md) | Clauset–Shalizi–Newman MLE + KS + Vuong: α ≈ 1.74–1.98 at equal length, power law ruled out for Lexical, indistinguishable from lognormal everywhere |
| 4 | **RULING boundaries — full-corpus result** (original claim withdrawn; effect re-established in the *opposite* direction) | [`outputs/phase4_ruling_fullcorpus.md`](outputs/phase4_ruling_fullcorpus.md) | 2,095 adjacent pairs, 10,000 permutations, two nulls: adjacent ruling-delimited chunks share **fewer** trigrams than alternative cuts (Δ=−0.33, BH p=0.0006) |
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
| `kišib₃` (seal) on 25.4% of Administrative tablets; year-names on 70.2%; `u₃-na-a-du₁₁` in 58.8% of Letters; `šu ba-ti` on 15.2% | Regex counts over a 2,069-tablet sample, **precision-audited** | **Solid** — descriptive | These four probes validate at 96–100% precision ([`probe_validation.md`](outputs/probe_validation.md)). Other probes in `templates.json` do **not** — see the row below. |
| Token-frequency distributions are heavy-tailed, α ≈ 1.74–1.98; power law ruled out for Lexical only; indistinguishable from lognormal everywhere | Clauset–Shalizi–Newman: KS-fitted x_min, discrete MLE, parametric-bootstrap GoF, Vuong test | **Moderate** — descriptive | The honest ceiling for this question. **No genre should be called power-law distributed.** [`phase5`](outputs/phase5_powerlaw.md) |
| ~~Administrative and Royal are more formulaic than Lexical (Zipf s 1.75 / 1.74 vs 1.11)~~ | OLS fit on log-log rank-frequency | **WITHDRAWN** | Stream-length artifact; at equal length under a correct estimator the spread collapses from 0.632 to 0.247. See [CORRECTIONS.md](CORRECTIONS.md). |
| Genres differ in structural redundancy; Royal Inscription and Administrative rank highest, Lexical lowest (Δ +0.05 to +0.10) | zlib ratio, real vs token-shuffled, **verified against an equal-length control** | **Moderate–solid** — descriptive | The strongest surviving positive statistic here. The token-shuffle baseline is legitimate for this particular claim, which is only "more structured than random token order". Unlike Zipf, the genre ranking survives equal-length contiguous blocks. Still not a test of any specific structural hypothesis. |
| No hidden periodic encoding in the corpus | ELS scan, 99 skips × 5 genres × 1,000 permutations | **Moderate** — null result | 3 nominal hits (p<0.01) vs ~5 expected by chance. **Underpowered for the Bonferroni threshold it originally claimed** — see §3 resolution caveat. Reads as "no signal above chance", not as a proof of absence. |
| Sealed envelopes answer 5/5 audit queries; anonymous logs 0/5, at +59% bytes / +37 tokens / +7µs per write | Executed benchmark, 100k writes | **Solid** — engineering measurement | Not a statistical claim. The 0/5 is definitional (an anonymous log lacks the fields), so it demonstrates a design consequence, not a discovery. Latencies are hardware-dependent. |
| `<RULING>` marks fall where cross-boundary trigram overlap is **lower** (Administrative, Δ=−0.33) | Full-corpus permutation test, 2,095 pairs, 10,000 perms, 2 independent nulls, BH-corrected | **Strong** — inferential | BH-adjusted two-sided p=0.0006; both nulls agree on direction; degeneracy affects 1.2% of tablets and biases against detection. Mechanism NOT established. [`phase4`](outputs/phase4_ruling_fullcorpus.md) |
| ~~`<RULING>` chunks share MORE trigrams than baseline (the original claim)~~ | Permutation test vs token-shuffle null | **WITHDRAWN** | Wrong null, and the corrected test finds the opposite sign. See [CORRECTIONS.md](CORRECTIONS.md). |
| Frequencies for `king_title`, `year_formula` (loose), `witness_eye`, `god_dedication`, `excess_diri` in `templates.json` | Regex counts | **DO NOT CITE** | Precision 6–42%. These probes match a different lexeme than their label claims (`nam-lugal` = "kingship" not a dedication; `igi-zu-še₃` = "before you" not a witness; `lugal-` mostly a personal-name element). Quantified in [`probe_validation.md`](outputs/probe_validation.md). |
| The 9 named agent primitives | Hand-authored mapping from templates | **Design proposal** | Grounded in cited tablet IDs, but the mapping from a Sumerian formula to an agent contract is an argument, not a measurement. `primitives.json` tags each as `validated` or `speculative` — that flag refers to whether the *pattern* was observed, never to whether the agent design works. |
| Three-tier SURFACE → COLUMN → RULING memory | — | **Untested proposal, now with indirect support** | The withdrawn claim is not its basis. The full-corpus result (row 1) is consistent with ruling-aligned chunking being meaningful, but no agent system was built or evaluated here. |
| The reference architecture, `FULL_IDEAS.md`, `summary.md` | Hand-authored | **Ideation** | No evidence claimed. Not generated by any script. |

**The honest summary:** this repo's defensible contributions are (a) a reproducible corpus-mining pipeline, (b) descriptive statistics on genre formulaicity, (c) a null result on hidden encodings, (d) an engineering benchmark for provenance-carrying write logs, and (e) a documented worked example of a null-hypothesis error and its correction. The mapping from cuneiform to agent design is an argument offered for its generative value, not a validated result — and the one place that mapping was given inferential backing, the backing did not survive audit.

---

## Why You Should Care (Findings → Actions)

Three concrete things you can build differently after reading this:

### 1. Wrap every agent write in a sealed envelope

**Finding, restated after audit.** 25.4% of administrative tablets carry `kišib₃` (seal of so-and-so) and 70.2% are dated by year-name. Both probes validate cleanly (`seal_of_PN` 96% precision, and the 70.2% is the *strict* year probe — see [`outputs/probe_validation.md`](outputs/probe_validation.md)). Sealed administrative example: **P101440**. Letters attribute differently — via `u₃-na-a-du₁₁` plus a closing scribe-and-filiation signature (`dub-sar`, `dumu` PN) rather than a seal: **P132611, P117793, P145759**.

**Two claims previously made here are withdrawn.** (a) *"Witness clauses (`igi PN-šè`) are common"* — they are not: genuine non-pronominal witness clauses appear on **0.4%** of administrative tablets, and 52% of that probe's raw matches are pronominal forms like `igi-zu-še₃` ("before you") that are not witness clauses at all. (b) *"No important write is anonymous, undated, or unattributed"* — **23.2%** of administrative tablets in this sample carry neither seal, year-name, nor witness, and ~75% carry no seal clause. Sealing is a strong minority practice, not a universal rule.

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

**Finding, corrected after audit — this pattern is real but RARE.** Some administrative tablets close with `šu-nigin₂` (sum-total), and shortfalls are named explicitly with `la₂-ia₃` (deficit owed by a named person). The `šu-nigin₂` and `la₂-ia₃` probes are precise, but the prevalence is far lower than earlier wording implied: **`šu-nigin₂` appears on 2.2% of administrative tablets, `la₂-ia₃` on 3.4%.** The earlier claim that administrative tablets "close with `šu-nigin₂`" and that "nothing drifts silently" described a practice attested on a small minority of tablets as though it were the norm. It is a genuine Sumerian bookkeeping device; it is not characteristic of the corpus. `diri` is **not** usable as an "excess" marker at all — 19% precision, because it frequently marks an *intercalary month*, not a ledger surplus.

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
| `šu-nigin₂` | sum-total | Periodic audit / signed reconciliation *(precise probe, but only 2.2% of Admin tablets)* |
| `la₂-ia₃` | deficit | Named outstanding obligation (never silent) |
| `diri` | excess *(also: intercalary month — the probe for this is 19% precise, do not cite it)* | Named surplus requiring disposition |
| `igi` PN-šè | before [person] | Witness clause *(genuine ones are rare: 0.4% of Admin tablets; the bare `igi-...-še₃` probe mostly catches "before him/you")* |
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
| ~~Admin tablets are a domain-specific language~~ **WITHDRAWN** | Length artifact; at equal stream length every genre sits at s = 1.11–1.21 ([CORRECTIONS.md](CORRECTIONS.md)) | Administrative |
| Royal Inscription is the most-templated genre | Compression-Δ = +0.099 vs shuffled baseline | Royal Inscription |
| ~~Lexical lists are closest to natural language~~ **WITHDRAWN** | Same length artifact — Lexical merely has the shortest stream (2,508 tokens) | Lexical |
| Letters are short single-purpose RPCs | Lowest marker density (0.02 RULING/tab) | Letter |
| ~~`<RULING>` is a logical row separator~~ **WITHDRAWN** | Null under the correct control; the original p-values came from a null that destroys all local structure ([CORRECTIONS.md](CORRECTIONS.md)) | Royal, Admin |
| No hidden encodings in the corpus | 3 of 495 ELS tests nominally p<0.01, vs ~5 expected by chance | All genres |
| Seal-of-PN clauses are a strong minority practice | 25.4% of Admin tablets (probe precision 96%); ~75% carry no seal | Administrative |
| Year-formulae are common in Administrative, less so elsewhere | Strict probe: 70.2% Admin, 45.4% Letter, 41.8% Royal (loose `\bmu\b` probe over-reports these as 74.2 / 73.8 / 62.6 — 53% of its matches are verbal prefixes) | Across genres |
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
│   ├── phase1b_probe_validation.py    precision-audits those probes (which ones are citable)
│   ├── phase4_ruling_fullcorpus.py    the RULING question, full corpus, 2 nulls, 10k permutations
│   ├── phase5_powerlaw.py             power-law fits by the Clauset-Shalizi-Newman method
│   ├── phase6_ruling_mechanism.py     do closers precede rulings? (position-controlled null)
│   ├── phase7_oracc_validation.py     probe precision vs expert lemmatisation (3.6M tokens)
│   ├── phase8_boundary_recovery.py    can the signals RECOVER the boundaries? (Pk/WindowDiff)
│   ├── check_integrity.py             pre-publish gate: links, correction notices, audit stamps
│   └── phase3_compression.py          Zipf, compression, ELS, RULING-parity analysis
├── benchmarks/
│   ├── kishib3.py                     reference sealed-envelope implementation (~250 LoC)
│   ├── baseline_log.py                anonymous-log comparison point (~50 LoC)
│   ├── benchmark.py                   harness — overhead + capability comparison
│   ├── results.json                   raw measurement output
│   └── RESULTS.md                     report with measured numbers and caveats
└── outputs/
    ├── phase4_ruling_fullcorpus.md    full-corpus RULING result
    ├── phase5_powerlaw.md             power-law analysis, done by the standard method
    ├── phase6_ruling_mechanism.md     closer-enrichment mechanism (6.3x, position-controlled)
    ├── phase7_oracc_validation.md     probe precision vs Oracc gold (lugal = 41% personal names)
    ├── phase8_boundary_recovery.md    boundary recovery: markers beat similarity on records
    ├── probe_validation.md            per-probe precision + prevalence -- READ BEFORE CITING
    ├── probe_validation.json          machine-readable probe audit
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

python scripts/phase0_sample.py            # ~2 min  downloads SumTablets, caches parquet, builds samples
python scripts/phase1_templates.py         # ~10 s   writes outputs/templates.json
python scripts/phase1b_probe_validation.py # ~5 s    writes outputs/probe_validation.md  <- READ THIS
python scripts/phase3_compression.py       # ~5 min  writes outputs/compression_findings.md + phase3_raw.json
python scripts/phase4_ruling_fullcorpus.py # ~20 min full-corpus RULING test (10,000 permutations)
python scripts/phase5_powerlaw.py          # ~2 min  Clauset-Shalizi-Newman power-law fits
python scripts/phase6_ruling_mechanism.py  # ~8 min  closer-enrichment mechanism test
python scripts/phase7_oracc_validation.py  # ~4 min  probe validation vs Oracc gold (561MB download)
python scripts/phase8_boundary_recovery.py # ~12 min boundary-recovery experiment (the paper headline)
python scripts/check_integrity.py          # ~1 s    links resolve, corrections present, audit stamps intact
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

`python scripts/check_integrity.py` should print `[integrity] clean`. It verifies that every relative link resolves, that every claim marked WITHDRAWN in the README still carries a correction notice *adjacent to it* in the derived documents, that every DO-NOT-CITE probe is stamped in `templates.json`, and that the corpus totals match. It runs in CI on every push. Its checks were validated by deliberately breaking each one and confirming it fails — one check was found vacuous that way and tightened.

What you should see in the console along the way — these are the load-bearing numbers:

| Check | Expected | Where |
|---|---|---|
| Corpus rows loaded | 91,606 | phase 0 |
| Stratified sample | 2,069 tablets + 197 long-form | phase 0 |
| `seal_of_PN` in Administrative | 25.4% (n=127) | phase 1 |
| Probes rated DO-NOT-CITE | 5 of 10 audited | phase 1b |
| Probes that never fire | 1 (`credit_mu_DU`) | phase 1b |
| Zipf s at native length (confounded, see §1) | 1.746 / 1.737 / 1.114 | phase 3 |
| Zipf s at equal length (the real comparison) | all genres 1.11–1.21 | phase 3 |
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
2b. **Probe validation.** Each probe's matches are partitioned by hand-written discriminators into TRUE / FALSE / UNCLEAR against its claimed semantic role, yielding a precision figure and a per-genre prevalence table. Probes below ~50% precision are marked DO-NOT-CITE rather than silently repaired. This step exists because the original release cited probe frequencies that were measuring the wrong lexeme.
3. **Compression and ELS.** Per-genre Zipfian fit (OLS on log-log, reported alongside an MLE exponent and an equal-length control that shows the cross-genre comparison does not survive); compression-ratio Δ between raw and shuffled token streams (with the same equal-length control, which it does survive); equidistant-letter-sequence (ELS) decimation at skips 2–100 against 1,000 permutations, `(r+1)/(n+1)` corrected, Bonferroni threshold reported together with the resolution caveat that the permutation count cannot reach it; cross-RULING trigram parity against two nulls — a token-shuffle null retained only to demonstrate it is the wrong control, and a boundary-permutation null holding token order and chunk lengths fixed and varying only where cuts fall (the primary test).
4. **Mapping.** For each empirical template, propose a named single-responsibility agent primitive with inputs, outputs, state, tools, and guardrails. Distinguish validated-by-data from speculative.

## For Reviewers and Future Readers

If you are evaluating this repo rather than using it, read in this order:

1. **[FINDINGS.md](FINDINGS.md)** — every claim, ranked by strength, with what each does and does not establish.
2. **[CORRECTIONS.md](CORRECTIONS.md)** — everything retracted, with the control that killed it. Two statistical findings and five regex probes.
3. **[outputs/probe_validation.md](outputs/probe_validation.md)** — which frequencies are citable (precision + per-genre prevalence).
4. **[REVIEWERS.md](REVIEWERS.md)** — where I think this is still weakest, and the specific questions I cannot answer myself.

The hand-authored design documents (`outputs/reference_architecture.md`, `outputs/summary.md`, `outputs/FULL_IDEAS.md`) were written against the original findings. They are **preserved rather than rewritten**, with inline correction notices at each retracted passage, so the record of what was claimed stays visible. `scripts/check_integrity.py` enforces that coupling — a retracted claim cannot sit in this repo without its correction beside it.

**Nothing here has been peer-reviewed.** The probe audit was performed by a non-specialist against standard dictionary values and is deliberately conservative, so its error rates are lower bounds.

---

## Honest Limits

- **Two of the three original statistical findings did not survive audit** (RULING-parity, Zipf-as-DSL — see [CORRECTIONS.md](CORRECTIONS.md)). Of what remains, the compression-redundancy ranking is the only positive inferential-flavoured result, and it is a descriptive contrast against random token order rather than a test of a specific structural hypothesis. Treat this repo's statistical contribution as modest.
- **The regex probes have had no specialist review**, and they generate the most-cited numbers here. One (`king_title`) is known to be measuring personal names rather than titles. Others carry the same class of risk and have not been quantified.
- **Multiple comparisons are corrected only within the ELS scan**, not across the ~40 hypotheses the repo entertains in total.
- The Zipf fit uses OLS on log-log rank-frequency data, which is a biased power-law estimator whose R² is not a goodness-of-fit test. It is retained, with an MLE exponent beside it, so the discrepancy is visible — not because it is the right method.
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
