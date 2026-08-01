# Summary — Top 10 Ideas, Ranked by Novelty × Implementability

> ⚠️ **CORRECTION NOTICE (2026-07-31).** This is a hand-authored design document written against
> the repository's original findings. **Two of those findings were subsequently withdrawn** after a
> self-audit — the RULING-parity result (wrong null hypothesis) and the Zipf-as-DSL result
> (stream-length artifact) — and **5 of 10 regex probes were found to match a different lexeme than
> their label claims.** Passages below that rest on the withdrawn results are marked inline. The
> document is preserved rather than rewritten so the record of what was claimed stays visible.
> **Read [`../CORRECTIONS.md`](../CORRECTIONS.md) and [`probe_validation.md`](probe_validation.md)
> before relying on anything here.**



Scoring: each axis is 1–5. **Score** is the product (max 25). "Implementability" is for a typical modern agent runtime; "novelty" is relative to common multi-agent / LLM frameworks (LangGraph, AutoGen, CrewAI, MS Semantic Kernel).

| # | Idea | Novelty | Impl. | Score | Source |
|---|---|---:|---:|---:|---|
| 1 | Universal sealed write envelope `(payload, seal, witnesses, period)` | 5 | 5 | **25** | §3, §5, §7.1 of `reference_architecture.md` |
| 2 | L1/L2/L3 tiered memory (SURFACE / COLUMN / RULING) — **empirical basis WITHDRAWN, now an untested proposal** | 4 | 5 | ~~20~~ | §2; the Phase 3 RULING-parity result it rested on is withdrawn (`../CORRECTIONS.md`) |
| 3 | Periodic signed audits (`šu-nigin₂`) for token/cost/tool ledgers | 5 | 4 | **20** | §5, probe `total_audit` |
| 4 | Templates-as-types encoder for high-redundancy genres | 5 | 3 | **15** | ~~Phase 3 Zipf s=1.75~~ **withdrawn** — rests instead on the compression-Δ ranking, which survives a length control |
| 5 | Year-name registry: relative refs that resolve + freeze at write-time | 4 | 4 | **16** | §6, probe `year_following` 74% admin |
| 6 | Filiation + revocable seal graph for principal identity | 3 | 4 | **12** | §3, probe `dumu PN` 37% admin |
| 7 | RoyalDecree-style policy registry with explicit supersession | 3 | 5 | **15** | §1 (RoyalDecreeAgent) |
| 8 | LexicalOntology with **signed `unify` events** — no silent entity merges | 4 | 3 | **12** | §4 |
| 9 | ScribalSchool curriculum pipeline for training new agents | 4 | 3 | **12** | primitives.json `ScribalSchoolAgent` |
| 10 | AddressedMessage RPC envelope (`u₃-na-a-du₁₁`) for inter-agent calls | 3 | 5 | **15** | probe `speak_to_him` 58.8% Letters |

---

## Top 3 — Detailed

### 1. Universal sealed write envelope (Score 25)

~~**The pattern.** Every clay tablet ends with `kišib₃ PN` (seal of PN), `iti X` (month), `mu Y` (year), and an optional witness chain (`igi PN-šè`). No write is anonymous, undated, or unattributed. Tablets P101440 and P132611 are textbook examples.~~

> **CORRECTED (2026-07-31).** This overstates the corpus badly. **25.4%** of administrative tablets carry
> `kišib₃`; **70.2%** carry a year-name; genuine witness clauses appear on **0.4%**; and **23.2%** carry
> *none* of the three. "Every clay tablet" and "no write is anonymous" are false. P101440 is a genuine
> sealed example; P132611 is a **Letter** with no seal clause, and was miscited here. The real pattern —
> a quarter of administrative tablets sealed and ~70% year-dated — is still notable, and is what the
> README now claims. See `probe_validation.md` for per-genre prevalence.

**The proposal.** Make this the **kernel-wide invariant for every state-changing call** in your agent runtime:

```rust
struct WriteEnvelope<T> {
    payload: T,
    by_seal: SealId,           // who
    witnesses: Vec<SealId>,    // who else was live at the moment
    period_id: PeriodId,       // when, in registry-resolved terms
}
```

**Why this is high-impact.**
- Auditability becomes a property of the envelope, not a separate concern bolted on per agent.
- Replay across any time window is trivial: collect envelopes, re-verify seals against the authority graph at each `period_id`, recompute audits.
- A failed verification at any point in history is a *single, locatable* event, not a debugging mystery.

**Cost.** Invasive — touches every write path. But the payoff scales with the size of the agent fleet.

---

### 2. Three-tier memory (SURFACE / COLUMN / RULING) (Score 20)

**The pattern.** Sumerian scribes treated tablets as a hierarchical document: physical surface (obverse/reverse) → logical column → atomic row. That three-level physical structure is a real feature of the artifact.

> **WITHDRAWN (2026-07-31).** The sentence that followed — "Phase 3 statistically confirms the row tier:
> adjacent `<RULING>`-bounded chunks share trigrams 30–500× more than shuffled baseline (Royal p=0.002,
> Administrative p=0.005)" — is withdrawn. It came from a null that destroys all local structure. Under a
> boundary-placement null the effect vanishes in every genre. The physical three-level layout is real; the
> claim that `<RULING>` marks *content* boundaries is unsupported. See `../CORRECTIONS.md`.

**The proposal.** Replace flat agent memory with a three-tier store. Reads return the *smallest enclosing tier* that satisfies the query, never the whole frame.

**Why this is high-impact.** Tier-aware reads add **structural pruning** on top of any existing context-compression — orthogonal and stackable.

**Cost.** Medium. Migration requires re-segmenting existing memory, but the segmentation rules are mechanical (paragraph → column, line → row, session → surface).

---

### 3. Periodic signed audits (`šu-nigin₂`) (Score 20)

**The pattern.** Administrative tablets close with `šu-nigin₂` (sum-total) — a periodic reconciliation that anyone can recompute from raw entries. Deviations are named explicitly: `la₂-ia₃` (deficit), `diri` (excess).

**The proposal.** For any ledger-shaped agent state (token usage, tool-call counts, cost tracking, evidence accumulation, eval scores), close periods at fixed intervals with a signed audit. **Deficits and excesses must be named and attributed to a counterparty** — never silently swept.

**Why this is high-impact.** LLM-agent systems routinely accumulate quiet drift in metric tracking. The Sumerian model forces drift to surface as a named, signed event with a counterparty, which makes it actionable instead of mysterious.

**Cost.** Medium. The hard part is defining "period" per ledger; the easy part is computing the audit (you already have the entries).

---

## Honest non-recommendations

- **Skip the ELS / hidden-code idea.** Phase 3 ran a 99-skip × 5-genre × 1000-shuffle ELS scan. Zero Bonferroni-significant skips. There is no hidden encoding to mine, and trying would be a credibility tax.
- **Don't force the literary-as-workflow metaphor.** Literary tablets are mostly hymns/narratives, not ritual procedures. `RitualSequenceAgent` is useful as a generic event-sourced workflow primitive — don't market it as "Sumerian ritual engine."
- **Don't claim full taxonomy from Lexical without external augmentation.** Our 69 Lexical tablets aren't enough to reverse-engineer HAR-ra=hubullu. Build the architectural slot, populate it from CDLI / ePSD2 separately.

---

## Reproducibility

- All scripts are seeded (`random_state=42`, `np.random.default_rng(42)`).
- Re-run order: `phase0_sample.py` → `phase1_templates.py` → `phase3_compression.py`. The architecture documents (`reference_architecture.md`, `primitives.json`) are hand-authored design artifacts that read those outputs.
- Outputs ground every claim in tablet IDs (`P*`, `Q*`) and per-genre statistics. Tablet IDs are resolvable at https://cdli.mpiwg-berlin.mpg.de/ or https://aicuneiform.com/.
