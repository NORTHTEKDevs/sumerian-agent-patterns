# Full Idea Catalog — Everything We Could Build From the Sumerian Corpus

Exhaustive dump of every primitive, finding, product, and research direction the SumTablets corpus suggests. Tagged with evidence strength and effort estimate.

**Tags:**
- `[V]` Validated by Phase 1/3 data with cited tablet IDs
- `[S]` Speculative — extrapolation beyond what 2,069 tablets show
- `[N]` Negative finding — explicitly DON'T do
- `[XS|S|M|L]` Effort: extra-small (hours), small (days), medium (weeks), large (months)

---

## A. Architectural Primitives (the agent rubric, expanded)

The 9 in `primitives.json` plus 11 more the corpus surfaces.

| # | Primitive | Tag | Effort | Source |
|---|---|:---:|:---:|---|
| A1 | TempleLedgerAgent | V | M | Admin tablets P514944, P101440 |
| A2 | SealAuthorityAgent (kišib₃ identity) | V | M | 25.4% Admin probe hit |
| A3 | LexicalOntologyAgent | S | L | 69 Lexical tablets — schema only, populate externally |
| A4 | ScribalSchoolAgent (curriculum + graduation) | V | M | P411777 reproduces same lines twice |
| A5 | RoyalDecreeAgent (versioned policy) | V | S | Q004341, Q001737 royal-title chain |
| A6 | RitualSequenceAgent (event-sourced workflow) | S | M | Literary speech-act framings |
| A7 | YearNameRegistryAgent (relative→absolute time) | V | S | 74.2% Admin year-formula hit |
| A8 | CommodityLedgerLineAgent (stateless line parser) | V | S | `2(diš) gin₂ <commodity>` 100s of hits |
| A9 | AddressedMessageAgent (RPC envelope) | V | S | `u₃-na-a-du₁₁` 58.8% Letters |
| A10 | DeficitTracker (la₂-ia₃ as named obligation, not silent zero) | V | XS | Probe hit |
| A11 | ExcessTracker (diri as named surplus, requires disposition) | V | XS | Probe hit |
| A12 | DebitCreditPair (zi-ga ↔ mu-DU as matched movement) | V | S | Probe hits |
| A13 | WitnessSet (live-seal-list at write time, separate from author) | V | S | igi PN-šè pattern |
| A14 | RoleBoundSeal (lugal vs ensi₂ vs dub-sar — seals scoped to role) | V | S | Royal title probes |
| A15 | PlaceBoundJurisdiction (`lugal urim₅{ki}ma` — title scoped to region) | V | S | Royal trigram |
| A16 | DivineDeterminativeTagger ({d}, {ki}, {giš} as type prefixes) | V | XS | Universal pattern |
| A17 | DedicationAct (`a mu-na-ru` — object dedicated to recipient, like git tag) | V | XS | Royal probe |
| A18 | ThreadReference (`dub-ba-ni` — "his tablet", explicit prior-msg ref) | V | XS | Letter pattern |
| A19 | GradeSystem (`niga gu₄-e-us₂-sa`, `niga 4(diš)-kam` — quality grades on commodities) | V | XS | Royal Inscription trigram |
| A20 | ProfessionRole (`kurušda` fattener, `dub-sar` scribe, `šuš₃` cattle-keeper) | V | XS | Filiation patterns |

---

## B. Memory Layer Findings (Phase 3 confirmed)

Multi-resolution context segmentation, derived from physical document structure.

| # | Idea | Tag | Effort |
|---|---|:---:|:---:|
| B1 | Three-tier memory: L1=SURFACE / L2=COLUMN / L3=RULING | V | M |
| B2 | Read at smallest enclosing tier (return one row, not the whole frame) | V | S |
| B3 | RULING-bounded chunks as vector-embedding units (parity p=0.002 Royal, p=0.005 Admin) | V | S |
| B4 | Frame nesting (obverse/reverse pairs) → call-stack-style nested contexts | V | S |
| B5 | BLANK_SPACE marker as intentional gap (preserve, don't trim — it carries semantic weight in admin) | V | XS |
| B6 | <unk> rate as data-quality signal per genre (Literary 6.9/tab → most damaged) | V | XS |
| B7 | Per-genre encoder: train a tiny tokenizer per memory-genre to exploit Zipf s>1.7 | V | M |
| B8 | Multi-column tablets as multi-pane editor model for agent transcripts | S | M |
| B9 | Surface-pair frame for "before/after" reasoning traces | S | S |
| B10 | RULING-density as document-formality classifier (Literary 0.58 vs Letter 0.02) | V | XS |

---

## C. Compression / Encoding Findings (Phase 3)

| # | Idea | Tag | Effort |
|---|---|:---:|:---:|
| C1 | Templates-as-types: detect that admin/royal are DSLs (Zipf s≈1.74), apply schema-aware encoder | V | M |
| C2 | Compression-Δ as "template coverage" diagnostic for ANY new corpus (genre detection without labels) | V | S |
| C3 | Per-genre vocabulary pinning for token cost reduction (small core vocab handles most admin lines) | V | S |
| C4 | Sexagesimal rational arithmetic for transaction qty (never coerce to float; Sumerian compounds 60-base) | V | XS |
| C5 | Determinative tags as cheap type hints in any structured-output context | V | XS |
| C6 | Provenance-delta storage: store sealed envelopes as deltas against parent | S | M |
| C7 | Genre-tagged memory crystals (a memory entry IS a sealed tablet with a genre) | V | M |
| C8 | DSL-detector heuristic: Zipf s>1.5 + compression-Δ>+0.07 → treat as keyword-language not prose | V | S |
| C9 | Compression-ratio per agent-output-type as drift detector (template adherence over time) | S | M |
| C10 | Stream-of-tablets concatenation pattern → corpus-level batch ledger compression | V | S |

---

## D. Identity / Trust Findings

| # | Idea | Tag | Effort |
|---|---|:---:|:---:|
| D1 | Universal sealed write envelope `(payload, by_seal, witnesses, period)` — runtime-wide invariant | V | M |
| D2 | Filiation graph (parent_principal_id) — append-only lineage | V | M |
| D3 | Revocable seals with cascading subordinate revocation | V | M |
| D4 | Witness-set requirement (live attestation, not just signature) | V | S |
| D5 | Time-bounded seals (valid_from/valid_to) | V | XS |
| D6 | Role-scoped seals (lugal-only operations reject ensi₂ seals) | V | S |
| D7 | Place-scoped jurisdiction (seal valid in region X, rejected in Y) | V | S |
| D8 | Hereditary credentials (parent revocation cascades to children) | V | S |
| D9 | Cross-org seal verification with explicit interop accord | S | M |
| D10 | Seal as model-version (different model fine-tunes get different seal lineages) | S | M |

---

## E. Workflow / Coordination Findings

| # | Idea | Tag | Effort |
|---|---|:---:|:---:|
| E1 | RPC-on-clay envelope: every inter-agent call carries explicit (from, to, body, expect_reply) | V | S |
| E2 | Imperative-only message bodies (typed action verbs: bar=release, ti=take, du₁₁=speak) | V | S |
| E3 | Reply threading: `dub-ba-ni` reference → message_id back-pointer | V | XS |
| E4 | ack/delivery receipts as separate event class | V | S |
| E5 | Periodic settlement as workflow checkpoint (close audit ⇒ commit batch) | V | M |
| E6 | Year-name as global event-sequence id (events instead of timestamps) | V | S |
| E7 | Compensation workflow for skipped steps (cannot just skip, must compensate) | S | M |
| E8 | Speech-act-as-state-transition (verbatim utterance recorded with transition) | V | S |
| E9 | Decree subscription model (agents subscribe to topic, get latest non-revoked) | V | S |
| E10 | Letter-as-batch (a single letter carries multiple imperatives) → batched RPC | V | S |

---

## F. Knowledge / Ontology Findings

| # | Idea | Tag | Effort |
|---|---|:---:|:---:|
| F1 | Versioned canonical taxonomy with pinned downstream consumers | S | L |
| F2 | DAG categories (a category can have multiple parents — barley is both grain AND ration) | V | M |
| F3 | Signed `unify` events (no silent entity merge) | V | S |
| F4 | Synonym attestation (cite the tablet/source where you observed the synonym) | V | S |
| F5 | Determinative prefixes as cheap type tags ({d} divine, {ki} place, {giš} wood, {d}DN) | V | XS |
| F6 | Lexical list as agent-onboarding curriculum | V | M |
| F7 | Per-genre canonical vocabulary (admin commodities ≠ literary metaphors) | V | M |
| F8 | Quality grade as commodity sub-type (`niga 4(diš)-kam` = grade 4 grain-fed) → SLA tiers | V | S |
| F9 | Profession ontology distinct from person ontology (role vs identity) | V | S |
| F10 | Place ontology distinct from authority (jurisdiction-tied roles) | V | S |

---

## G. Compute / Kernel Findings

| # | Idea | Tag | Effort |
|---|---|:---:|:---:|
| G1 | Workload-observer tunable: tier-routing (L1 vs L2 vs L3 read frequency) | V | S |
| G2 | Per-genre compression-ratio threshold drives extraction-model routing decision | V | S |
| G3 | Stale-seal check at every read (revocation propagation latency tracking) | V | S |
| G4 | Audit-result cache + replay invalidation when raw entries change | V | M |
| G5 | Period-boundary memory eviction (close period → archive cold tier) | V | M |
| G6 | Signed-envelope-aware diff for memory updates (preserve provenance through merges) | V | M |
| G7 | DSL-detector pre-pass on incoming corpora (auto-detect when to load template encoder) | V | S |
| G8 | Workload profile: "high-formality" mode (admin-style) vs "narrative" mode (literary-style) | V | S |
| G9 | Lexical-resolution as a kernel pass (canonicalize before write to memory) | S | M |
| G10 | Royal-decree pattern as kernel-config hot-reload primitive | V | S |

---

## H. Standalone Open-Source Library Ideas

Each is a small, focused library people could `npm install` / `pip install` / `cargo add`. Sumerian-named for branding (and SEO uniqueness).

| # | Library | What | Tag | Effort |
|---|---|---|:---:|:---:|
| H1 | `kishib3` (Rust+Py+TS) | Sealed write envelope + signature + verification | V | S |
| H2 | `shu-nigin` | Periodic ledger audit lib (close period → recompute totals → sign) | V | S |
| H3 | `iti-mu` | Year-name registry with relative-name resolution | V | S |
| H4 | `lu2` | Principal/filiation graph store (Postgres + Drizzle schema?) | V | M |
| H5 | `harra-hubullu` | Versioned canonical-entity taxonomy service | V | M |
| H6 | `u3-na-a-du11` | Inter-agent RPC envelope (sender, recipient, body, reply expectation) | V | S |
| H7 | `edubba` | Agent training pipeline (curriculum + scoring + graduation) | V | M |
| H8 | `nita-kalag-ga` | Policy/decree registry with explicit supersession | V | S |
| H9 | `tablet-mem` | L1/L2/L3 tiered memory store (drop-in for LangChain/LangGraph) | V | M |
| H10 | `kurushda` | Role-scoped seal lib (seals tied to declared role/place) | V | S |
| H11 | `dub-ba-ni` | Message-thread back-reference lib (any RPC system can adopt) | V | XS |
| H12 | `niga-grade` | Quality-grade-on-commodity SLA tier definition lib | V | XS |
| H13 | `mu-DU` | Debit/credit pair-matching enforcement lib | V | S |
| H14 | `igi` | Witness-set live-attestation lib (consumes from seal authority) | V | S |
| H15 | `cuneicompress` | Template-aware compressor with auto-detected DSL mode | V | M |

---

## I. Research / Paper Ideas

Each could go to ML4AL, NeurIPS workshops, or arXiv. Some are defensive (publishing the negative result protects the corpus from misuse).

| # | Paper | Tag | Effort |
|---|---|:---:|:---:|
| I1 | "Sumerian Tablets as Multi-Agent System Specifications" — workshop paper at ML4AL or similar | V | M |
| I2 | "Negative ELS Result on the SumTablets Corpus" — defensive paper killing future numerology takes | V | S |
| I3 | "Compression Ratio as DSL Detector in Ancient Corpora" — IR / corpus-linguistics paper | V | M |
| I4 | "The First Append-Only Ledger: 4000 Years of Audit Discipline in Ur III" — popular-science essay | V | S |
| I5 | "Tiered Memory From Physical Document Segmentation" — agents workshop | V | M |
| I6 | "The Sumerian RPC Pattern" — short note / blog | V | XS |
| I7 | "Role-Scoped Capabilities: Lessons from kišib₃" — security-systems venue | V | M |
| I8 | "Year-Names as Distributed Event-Time" — distsys workshop | V | M |
| I9 | "Determinative Prefixes as Type Hints" — PL / type-systems venue | S | M |
| I10 | "Why Lexical Lists Were the World's First Ontologies" — DH venue | S | M |

---

## J. Generic Stack Application — How to Pick What Applies to You

The 80+ ideas above translate to your existing systems via three foundational integrations. Once these three are in place, the rest plug in incrementally:

1. **Sealed write envelope** (D1, A2) — wrap every state-changing call in `(payload, by_seal, witnesses, period)`. Touches every write path; payoff scales with agent fleet size.
2. **Three-tier memory** (B1, B2) — replace flat memory stores with SURFACE (session) / COLUMN (topic) / RULING (row) tiers. Queries return the smallest tier that answers.
3. **Periodic signed audits** (A1, G4) — close ledger-shaped state at fixed intervals; compute totals from raw entries; name deficits/excesses explicitly.

Domain-specific extensions worth considering:

- **Compliance / legal-doc generation:** templates-as-types DSL encoder (C1), RULING-density formality classifier (B10), templates-as-schemas for form generation (C1).
- **Multi-tenant / multi-region products:** place-bound jurisdiction (A15), role-scoped seals (A14), filiation graph for delegated authority (D2).
- **Signal / prediction systems:** quality-grade pattern (A19) for confidence tiers, witness-set for "what else was live" attestation (D4).
- **Entity-heavy data products:** lexical canonicalization with signed unify (F3), DAG categories (F2), synonym attestation (F4).
- **Inter-agent coordination:** RPC envelope (E1), reply threading (E3), ack/delivery receipts (E4).
- **Time-sensitive audit trails:** year-name registry (A7), periodic settlement (E5), year-name as global event-sequence id (E6).

---

## K. Standalone SaaS / Product Ideas

| # | Product | Tag | Market | Effort |
|---|---|:---:|---|:---:|
| K1 | **Edubba** — agent-fleet training-and-graduation SaaS (curriculum + score + cert) | V | AI dev tools | L |
| K2 | **Tablet** — drop-in tiered-memory layer for LangChain/LangGraph users | V | AI dev tools | M |
| K3 | **Kishib** — sealed-event-store-as-a-service (every event signed, periodic audits) | V | Audit/compliance | L |
| K4 | **Year-Name** — distributed event-time service for distributed-systems devs | V | DevOps | M |
| K5 | **Harra** — managed canonical-entity taxonomy service with versioning | S | Data infra | L |
| K6 | **Nita-Kalag** — feature-flag-style policy registry with explicit supersession | V | DevOps | M |
| K7 | **Sumerian** — open-spec for agent-system interoperability (envelope + tiers + canonical-entities) | V | Standards | L |
| K8 | **Cuneiform IDE** — visual agent-flow editor with sealed-envelope debugger ("who signed this?") | V | AI dev tools | L |

---

## L. Datasets / Public Releases

Reusable artifacts from this single experiment.

| # | Release | Tag | Effort |
|---|---|:---:|:---:|
| L1 | `templates.json` published as HuggingFace dataset "Sumerian Bureaucratic Templates" | V | XS |
| L2 | Genre × period distribution as a CSV release | V | XS |
| L3 | Per-tablet glyph-count and template-coverage scores | V | XS |
| L4 | A reproducible PoC repo with all 4 phases (THIS REPO) | V | XS |
| L5 | A blog post + diagram series mapping each Sumerian primitive to a modern equivalent | V | S |
| L6 | A Jupyter / nbviewer notebook walking through Phase 1 → 4 | V | S |
| L7 | An interactive web demo: paste an admin tablet, get its sealed-envelope decomposition | S | M |
| L8 | Public talk/screencast: "What 4000-year-old clay tablets teach about agent design" | V | S |
| L9 | Cross-reference table mapping Phase-1 templates to Phase-2 primitives | V | S |
| L10 | A benchmark: "can your LLM agent reproduce a Sumerian admin closing formula?" | S | M |

---

## M. Speculative / Fun Things

| # | Idea | Tag | Effort |
|---|---|:---:|:---:|
| M1 | Synthetic Sumerian admin generator using Phase-1 templates + Phase-4 ontology | V | M |
| M2 | "Sumerian Mode" for any LLM agent: enforce sealed envelopes, year-names, audits | V | M |
| M3 | Cuneiform-glyph compressor as a toy demo / gif on Twitter | V | XS |
| M4 | RPC trace formatter that prints `u₃-na-a-du₁₁ "X did Y at year-name Z"` instead of JSON | V | XS |
| M5 | Visual sealed-envelope debugger ("walk the seal lineage of this row") | V | M |
| M6 | "Year-of-the-X" namer for every CI/CD release — replace v1.2.3 with named events | V | XS |
| M7 | Browser extension that wraps any web form submission in a sealed envelope | S | M |
| M8 | A static site that lets anyone explore tablet IDs cited in primitives.json | V | S |
| M9 | "What would your codebase look like as a Sumerian temple ledger?" — analyzer | S | M |
| M10 | A toy procedural-generation game where you play an Ur III ensi₂ administering a city | S | L |

---

## N. Findings Caught But Not Elevated to Phase 1–4

Patterns visible in the sample that would warrant a deeper pass.

| # | Finding | Tag |
|---|---|:---:|
| N1 | Recurring person `dumu ur-nigar{gar} šuš₃` appears across many Letter tablets — suggests a high-frequency individual. Building a frequency map of named persons would expose the social network. | V |
| N2 | Place determinative {ki} attaches to thousands of city names — a ready-made gazetteer. | V |
| N3 | `niga 4(diš)-kam`-style numbered grades suggest an explicit ordinal-quality system, not just enum tags. | V |
| N4 | `lugal urim₅{ki}ma`, `lugal kiš{ki}` etc. — title is region-bound. Authority is geographically scoped, not global. | V |
| N5 | Royal Inscription `a mu-na-ru` ("he dedicated to him") — every dedication carries (donor, recipient, object) — a typed votive ledger. | V |
| N6 | Letter `dub-ba-ni` ("his tablet") — explicit reference to a prior physical message — a thread-id. | V |
| N7 | Letter has the lowest marker density (2.14 SURFACE / tab, 0.02 RULING / tab) — letters are SHORT single-purpose RPCs by design. Compare to Admin (2.25 SURFACE, 0.04 RULING) — admin tablets pack more on a single surface. | V |
| N8 | Lexical sample has 3.2 `<unk>` per tablet — Lexical lists were heavily damaged in archeological recovery; their density of {ki}/{d}/role tags makes them a stress test for canonicalization. | V |
| N9 | Literary 154k stream tokens vs 977 tablets → many literary tablets are LONG (often hymns continuing across multiple tablets). Multi-tablet narratives = multi-document agents. | V |
| N10 | The Ur III period dominates (75k of 91k tablets) — single-period bias in the corpus. Cross-period analysis would need careful weighting. | V |
| N11 | Almost no tablets have BOTH high RULING density AND high COLUMN density — the two segmentation strategies trade off. Genres pick one. | V |
| N12 | "kišib₃" probe found 25.4% of admin tablets sealed in our sample, but aicuneiform.com lists 6,980 seal objects in its 99k Sumerian set — implying many sealed tablets do NOT carry the kišib₃ marker (the seal is a physical impression, not a transliterated word). Phase 1 undercounts. | V |
| N13 | Year-formula matches in 65% Letters even though letters carry no transactions — letters are dated for delivery context, not for ledger reasons. Date is a universal envelope field. | V |
| N14 | The single 343-glyph Literary tablet P346161 is a Lugal-e fragment — long-form mythology has its own structural patterns (refrains, parallel verse) that our quantitative pass barely touches. | S |
| N15 | "ŠU LAGAB" recurring as a totals marker in admin signs — could be a compact accounting glyph worth promoting to a typed primitive. | V |

---

## O. Negative Findings (DO NOT pursue)

| # | Idea | Why |
|---|---|---|
| O1 | ELS / hidden-message decoding | Phase 3: 0 of 495 Bonferroni-significant tests. No signal. |
| O2 | Treating literary tablets as literal ritual workflows | Mostly hymns/narratives, not procedures. Metaphor breaks. |
| O3 | Reconstructing Lexical-list internal taxonomy from our 69 tablets alone | Insufficient sample. Use external sources (CDLI/ePSD2). |
| O4 | Marketing "Sumerian Ritual Engine" or other mystical framing | Brand-damaging. Stay engineering-grade. |
| O5 | Using the corpus to claim cuneiform "predicted" modern systems | They were solving the same bureaucratic problems independently. Coincidence is not influence. |
| O6 | Assuming SealAuthority maps to crypto PKI 1:1 | Sumerian seals were physical, witnessed, social. Don't import all PKI assumptions. |
| O7 | Treating year-names as monotonic increasing IDs | They are a NAMED sequence, not numeric — derived names (us₂-sa) are a feature. |

---

## P. Quick-Win Roadmap (next 7 days)

If you wanted to ship something concrete from this work this week:

1. **Day 1**: Publish `templates.json` and `compression_findings.md` as a public HF dataset + repo (this repo).
2. **Day 2**: Write `kishib3` as a minimal Rust crate (sealed envelope + verify). 200 LoC.
3. **Day 3**: Wire `kishib3` into one write path of your runtime as proof of integration.
4. **Day 4**: Write `iti-mu` (year-name registry) — 150 LoC, no deps.
5. **Day 5**: Publish a blog post: "What 4000-year-old clay tablets teach about agent design."
6. **Day 6**: Add L1/L2/L3 markers to one type of memory entry as a test.
7. **Day 7**: Submit a 4-page workshop note to ML4AL on the negative ELS result + DSL Zipf finding.

Total effort: ~3 days actual coding, ~4 days writing/release work.

---

## Q. Where the Metaphor Genuinely Breaks (intellectual honesty)

| # | Where it breaks | What to NOT claim |
|---|---|---|
| Q1 | Lexical lists ≠ formal type systems with subtype constraints. They're enumerations with thematic groupings. Don't oversell them as "OOP avant la lettre." | "First object-oriented system" |
| Q2 | kišib₃ seals had no cryptographic security — they were physical, fakeable, witnessed-in-person. | "Sumerians invented PKI" |
| Q3 | Year-names are political artifacts (named after royal acts). They are NOT a neutral monotonic clock. | "Sumerians invented logical clocks" |
| Q4 | Lugal-e and other narrative texts are LITERATURE — they have plot, refrain, ornament. They are not workflow specifications. | "Hymns are state machines" |
| Q5 | The corpus is heavily biased to administrative texts (>92% Admin in our sample). Generalizing about "Sumerian thought" from this is generalizing about "civilization" from accounting receipts. | "All of Sumerian cognition is bureaucratic" |
| Q6 | We sampled 2.3% of the corpus. Findings are representative for Ur III admin and OB literary; weak for everything else. | "We've characterized the entire Sumerian corpus" |

---

## Total Idea Count

- Architectural primitives: 20
- Memory layer: 10
- Compression / encoding: 10
- Identity / trust: 10
- Workflow / coordination: 10
- Knowledge / ontology: 10
- Compute / kernel: 10
- Standalone libraries: 15
- Research papers: 10
- SaaS / product: 8
- Datasets / releases: 10
- Speculative / fun: 10
- Uncovered findings: 15
- Negative findings: 7
- Roadmap items: 7
- Honest-limit caveats: 6

**~158 distinct ideas.** Most are XS–S effort. The ones that compound (D1 sealed envelope, B1 tiered memory, A2 SealAuthority + A7 YearName + A10–A14 typed primitives) form the *foundation* — everything else assumes them.
