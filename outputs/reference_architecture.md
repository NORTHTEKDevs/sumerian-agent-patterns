# Sumerian × Modern Agent Patterns — Reference Architecture

**Source corpus:** SumTablets (Simmons, Diehl Martinez, Jurafsky — ML4AL 2024). 91,606 tablets, 6.97M cuneiform glyphs. Stratified sample of 2,069 tablets (500/genre × 4, plus all 69 Lexical) drives the patterns below; 197 long-form tablets supply structural-marker statistics.

**Status of claims:** Each subsystem cites either (a) a Phase-1 template hit with tablet IDs, or (b) a Phase-3 statistic. Speculative metaphors are flagged inline.

**Code shapes:** pseudocode given in Python and Rust. Both are illustrative — adapt to your runtime's existing identity / storage / event primitives.

> ⚠️ **CORRECTION NOTICE (2026-07-31).** This is a hand-authored design document written against
> the repository's original findings. **Two of those findings were subsequently withdrawn** after a
> self-audit — the RULING-parity result (wrong null hypothesis) and the Zipf-as-DSL result
> (stream-length artifact) — and **5 of 10 regex probes were found to match a different lexeme than
> their label claims.** Passages below that rest on the withdrawn results are marked inline. The
> document is preserved rather than rewritten so the record of what was claimed stays visible.
> **Read [`../CORRECTIONS.md`](../CORRECTIONS.md) and [`probe_validation.md`](probe_validation.md)
> before relying on anything here.**



---

## 1. Reference Architecture

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

Three transverse subsystems span the agents:

- **Memory layer** (§2) — multi-resolution context segmentation, derived from `<SURFACE>` / `<COLUMN>` / `<RULING>`.
- **Identity/provenance** (§3) — kišib seal model.
- **Taxonomy** (§4) — lexical-list canonicalization.
- **Transaction ledger** (§5) — append-only commodity transactions with audit closure.

---

## 2. Memory Layer — Multi-Resolution Context (SURFACE / COLUMN / RULING)

### Empirical basis (Phase 1 + Phase 3)

| Genre | `<SURFACE>` / tab | `<COLUMN>` / tab | `<RULING>` / tab | RULING parity Δ | RULING parity p |
|---|---:|---:|---:|---:|---:|
| Administrative | 2.25 | 0.44 | 0.04 | +0.171 | 0.005 |
| Royal Inscription | 1.76 | 0.59 | 0.02 | +0.497 | 0.002 |
| Literary | 1.33 | 0.40 | 0.58 | +0.715 | 0.014 |
| Lexical | 1.38 | 0.48 | 0.29 | +0.507 | 0.031 |
| Letter | 2.14 | 0.12 | 0.02 | n/a | n/a |

~~The parity test shows that `<RULING>`-bounded chunks share trigrams with their neighbors at rates 30–500× the shuffled baseline. **`<RULING>` is provably a logical row separator, not a visual hint.**~~

> **WITHDRAWN (2026-07-31).** The 30–500× figure and the p-values in the table above came from a null
> that shuffled all of a tablet's tokens, destroying the local coherence any natural-language text has.
> Under a null that holds token order and chunk lengths fixed and permutes **only where the cuts fall**,
> the effect disappears in every genre (p = 0.78 Admin, 0.91 Literary, 0.27 Lexical, 1.00 Royal), with
> observed values *at or below* the null. **There is no statistical evidence that `<RULING>` marks content
> boundaries.** The `<SURFACE>` / `<COLUMN>` / `<RULING>` marker-density columns in the table are simple
> counts and remain valid; only the parity Δ and p columns are withdrawn. The three-tier memory design
> below is therefore an **untested design proposal**, not a corpus finding. See `../CORRECTIONS.md`.

### Architecture: three-tier context window

| Tier | Sumerian analog | Runtime role | Boundary marker | Typical content |
|---|---|---|---|---|
| **L1 — Frame** | `<SURFACE>` (obverse / reverse / edge) | Conversation / session window | Hard reset; new task or new actor | Per-task scratchpad, short-term tool results |
| **L2 — Section** | `<COLUMN>` | Topical sub-context within a frame | Soft reset; topic switch within same task | One subroutine, one tool chain, one prompt+response cycle |
| **L3 — Row** | `<RULING>` | Atomic typed record | None — every record is one row | A single transaction, fact, or schema entry |

### Pseudocode — Python

```python
from dataclasses import dataclass, field
from enum import Enum

class SegmentKind(Enum):
    SURFACE = "surface"   # L1 — frame
    COLUMN  = "column"    # L2 — section
    RULING  = "ruling"    # L3 — row

@dataclass(frozen=True)
class Row:
    text: str
    fields: dict           # canonicalized via LexicalOntologyAgent
    written_by: str        # principal_id from SealAuthorityAgent
    period_id: str         # from YearNameRegistryAgent

@dataclass
class Section:
    topic: str
    rows: list[Row] = field(default_factory=list)

@dataclass
class Frame:
    actor: str
    sections: list[Section] = field(default_factory=list)
    parent_frame_id: str | None = None  # frames can nest like obverse/reverse pairs

class TabletMemory:
    """Multi-resolution memory store. Reads return the smallest enclosing tier."""
    def __init__(self) -> None:
        self.frames: list[Frame] = []

    def open_frame(self, actor: str, parent: str | None = None) -> Frame:
        f = Frame(actor=actor, parent_frame_id=parent)
        self.frames.append(f); return f

    def open_section(self, frame: Frame, topic: str) -> Section:
        s = Section(topic=topic); frame.sections.append(s); return s

    def write_row(self, section: Section, row: Row) -> None:
        section.rows.append(row)

    def read(self, query: str, max_tier: SegmentKind = SegmentKind.RULING) -> list[Row]:
        """Return only the rows that match — never bubble up an entire SURFACE
        when one RULING suffices. This is the multi-resolution win."""
        ...
```

### Pseudocode — Rust

```rust
pub enum SegmentKind { Surface, Column, Ruling }

pub struct Row {
    pub text: String,
    pub fields: serde_json::Value,
    pub written_by: PrincipalId,
    pub period_id: PeriodId,
}

pub struct Section { pub topic: String, pub rows: Vec<Row> }
pub struct Frame   { pub actor: ActorId, pub sections: Vec<Section>, pub parent: Option<FrameId> }

pub struct TabletMemory { pub frames: Vec<Frame> }

impl TabletMemory {
    pub fn open_frame(&mut self, actor: ActorId, parent: Option<FrameId>) -> FrameId { /* ... */ }
    pub fn open_section(&mut self, f: FrameId, topic: &str) -> SectionId { /* ... */ }
    pub fn write_row(&mut self, s: SectionId, row: Row) -> RowId { /* ... */ }
    pub fn read_smallest(&self, q: &Query) -> Vec<&Row> { /* return min enclosing scope */ }
}
```

### Why this matters

Most agent-runtime memory is flat. Adding L1/L2/L3 tiers with explicit boundary markers lets a workload observer route reads at the **tightest tier** that satisfies the query — never pulling a full session when a single row answers.

---

## 3. Identity & Provenance — Seal Authority Subsystem

### Empirical basis

- `kišib₃` (seal of) appears in **25.4 %** of Administrative tablets in the sample (probe `seal_of_PN`, n=127). Tablets: P101440, P132611, P117793, P145759.
- `dumu PN` (son of PN) — the filiation primitive — appears in 37 % of Admin tablets and 43.4 % of Royal Inscriptions.
- `igi PN-šè` witness clauses ground transactions in named live observers.

These three together form a **directed authority graph**: principals have parents (lineage), seals (active credentials), and witnesses (live attestation at the moment of action).

### Design

```
Principal ──parent──▶ Principal     (filiation, append-only)
Principal ──holds──▶  Seal          (mintable, revocable)
Seal      ──signs──▶  Transaction   (every write is signed)
Witness   ──attests──▶ Transaction  (set of live seals at write-time)
```

### Pseudocode — Python

```python
@dataclass(frozen=True)
class Principal:
    id: str
    role: str              # ensi, lugal, dub-sar (scribe), kurušda (fattener), ...
    parent_id: str | None  # dumu-of edge

@dataclass(frozen=True)
class Seal:
    id: str
    principal_id: str
    public_key: bytes
    valid_from: int
    valid_to: int | None   # None = active; set on revocation

class SealAuthority:
    def mint(self, principal: Principal, public_key: bytes) -> Seal: ...
    def revoke(self, seal_id: str, by: str, reason: str) -> None: ...
    def verify(self, seal_id: str, payload: bytes, sig: bytes) -> bool: ...
    def authorized_for(self, seal_id: str, role: str) -> bool: ...

    def witness_set_valid(self, seal_ids: list[str], at: int) -> bool:
        return all(s.valid_from <= at and (s.valid_to is None or at < s.valid_to)
                   for s in (self.get(sid) for sid in seal_ids))
```

### Pseudocode — Rust

```rust
pub struct SealAuthority { /* graph store */ }

impl SealAuthority {
    pub fn mint(&mut self, p: PrincipalId, pubkey: PublicKey) -> SealId { /* ... */ }
    pub fn revoke(&mut self, s: SealId, by: PrincipalId, reason: String) -> Result<()> { /* ... */ }
    pub fn verify(&self, s: SealId, payload: &[u8], sig: &Signature) -> bool { /* ... */ }
    pub fn authorized_for(&self, s: SealId, role: &str) -> bool { /* ... */ }
}
```

### Why this matters

Multi-agent systems routinely treat agent identity as a string. The Sumerian model treats it as **a graph of principals plus a mutable set of credentials with explicit revocation**. An agent runtime can adopt this directly: every agent action carries `(principal_id, seal_id, witness_set)`, and the authority service is a separate, single-responsibility primitive — no inline auth scattered across handlers.

---

## 4. Taxonomy / Ontology Subsystem

### Empirical basis (and its limit)

Lexical lists are the world's first formal ontologies. In our sample only **69** Lexical tablets exist (P411777, P480569 are the long-form examples), so the architecture below relies on Assyriological consensus more than on quantitative findings — flagged as **speculative-from-prior-art** in `primitives.json`.

What our data *does* show: Lexical tablets have the highest `<COLUMN>` density (0.48/tab) and high `<RULING>` density (0.29/tab) — the column/row layout of an explicit type catalog.

### Design

```
Category (DAG; multiple parents allowed)
   │
   ├── canonical_id ──synonyms──▶ surface_form[]
   │
   └── attestations[] ──cite──▶ tablet_id[]   # provenance for the canonical entry
```

### Pseudocode — Python

```python
@dataclass
class Category:
    id: str
    parents: list[str]    # DAG, not tree
    label: str
    version: int

@dataclass
class CanonicalTerm:
    id: str
    category_id: str
    surface_forms: set[str]
    attestations: list[str]   # tablet IDs from corpus or future writes

class LexicalOntology:
    def resolve(self, surface: str, context_genre: str | None = None) -> list[CanonicalTerm]:
        """Returns candidates — caller MUST disambiguate before writing."""
        ...
    def add_synonym(self, canonical_id: str, surface: str, attestation: str) -> None: ...
    def unify(self, ids: list[str], by_seal: str, witnesses: list[str]) -> str:
        """Merge duplicates only with a signed transaction. Never silent."""
        ...
```

### Why this matters

LLM agents routinely conflate distinct entities because they share a string. An agent runtime can adopt the lexical-list model: a versioned canonical taxonomy that **other agents pin to**, with explicit, signed `unify` events when two ids are merged. No silent normalization.

---

## 5. Transaction / Ledger Subsystem

### Empirical basis

Distinctive Administrative trigrams (Phase 1 log-odds):

- `2(diš) gin₂ naga` (2 shekels of soda) — 91 occurrences
- `gin₂ i₃ 2(diš)` (shekel of oil, 2) — 90
- `sila₃ kaš 2(diš)` (liter of beer, 2) — 63
- `sila₃ ninda 5(diš)` (liter of bread, 5) — 63

All have the structure `<qty>(<unit>) <commodity>` — the canonical typed transaction line. Administrative has the second-highest structural-redundancy Δ (+0.088, second only to Royal Inscription at +0.099), and that ranking does survive an equal-length control.

> **Caveat (2026-07-31).** "It is a **DSL**, with reserved keywords" overstates what the statistic shows.
> The compression Δ establishes only that the real token stream is more redundant than the same tokens in
> random order. "DSL" is an analogy, not a result. The Zipf evidence originally cited for it has been
> withdrawn as a stream-length artifact.

### Design

```
TempleLedger (per actor/department)
   │
   ├── Entry  { ts, lines[], witnessed_by[], seal_id, period_id, parent_audit_id? }
   │
   └── Audit  { period_id, sum_by_commodity, deficit, excess, signed_by_seal_id }

CommodityLedgerLine (stateless)
   parses raw "2(diš) gin₂ i₃" → { qty: 2, unit: gin₂, commodity: i₃ (canonicalized) }
```

### Pseudocode — Python

```python
@dataclass(frozen=True)
class Line:
    qty: tuple[int, int]        # rational — Sumerian uses sexagesimal compounds
    unit_id: str                # canonical from LexicalOntology
    commodity_id: str
    counterparty_id: str | None
    instrument: str             # 'sealed' | 'received' | 'delivered' | 'debited'

@dataclass(frozen=True)
class Entry:
    id: str
    ts: int
    lines: list[Line]
    witnessed_by: list[str]     # seal_ids
    seal_id: str
    period_id: str
    parent_audit_id: str | None = None

class TempleLedger:
    def post(self, entry: Entry) -> None: ...
    def close_period(self, period_id: str, by_seal: str) -> "Audit": ...
    def deficit_for(self, counterparty_id: str) -> dict[str, "Rational"]: ...

class CommodityLedgerLine:  # stateless parser
    @staticmethod
    def parse(raw: str, ontology: LexicalOntology) -> Line: ...
```

### Pseudocode — Rust

```rust
pub struct Line {
    pub qty: Rational,           // num::Rational64 or rug::Rational
    pub unit_id: CanonicalId,
    pub commodity_id: CanonicalId,
    pub counterparty_id: Option<PrincipalId>,
    pub instrument: Instrument,
}

pub struct Entry {
    pub id: EntryId,
    pub ts: Timestamp,
    pub lines: Vec<Line>,
    pub witnessed_by: Vec<SealId>,
    pub seal_id: SealId,
    pub period_id: PeriodId,
    pub parent_audit_id: Option<AuditId>,
}

pub trait Ledger {
    fn post(&mut self, e: Entry) -> Result<()>;
    fn close_period(&mut self, p: PeriodId, by: SealId) -> Result<Audit>;
    fn deficit_for(&self, c: PrincipalId) -> HashMap<CanonicalId, Rational>;
}
```

### Why this matters

LLM agents have no native concept of an *audit*. The Sumerian primitive `šu-nigin₂` (sum-total) is a periodic, signed reconciliation — every period closes with a totals line that anyone can recompute from raw entries. An agent runtime can adopt this for any ledger-like agent state (token accounting, tool-call accounting, cost tracking, evidence ledgers): **periodic signed audits with deficit/excess explicitly named**.

---

## 6. Year-Name Registry (Time Index)

### Empirical basis

`mu` (year) probe hits **74.2 %** of Administrative tablets, 65 % of Letters, 62.4 % of Royal Inscription. The construction `mu us₂-sa <event>` (year-following-the-year-of-X) shows the Sumerians built **derived names that resolve at write-time** — a relative-time reference that becomes an absolute fact once recorded.

### Design

```python
@dataclass(frozen=True)
class Period:
    id: str                # monotonic
    name: str              # "year of the destruction of Kimaš"
    naming_event: str      # what the year is named after
    naming_decree_id: str  # the RoyalDecree that named it
    derived_from: str | None  # the prior period if this is a 'us2-sa' name

class YearNameRegistry:
    def name(self, p: Period) -> None: ...
    def resolve_relative(self, anchor: str, offset: str) -> Period:
        """'us2-sa' → next; 'us2-sa-a-bi' → year after that. Resolves at write-time."""
        ...
```

This subsystem and `RoyalDecreeAgent` are tightly coupled — every period name *is* a decree.

---

## 7. Composite Properties

### 7.1 Single-responsibility, sealed, dated

Every write across every subsystem carries the same envelope:

```
{ payload, by_seal_id, witness_set[], period_id }
```

This is the Sumerian invariant. Adopting it uniformly means cross-agent audits become trivial: replay any time window, verify all seals were valid then, recompute the audit totals.

### 7.2 Append-only with explicit revocation

Filiation is append-only. Seals are revocable. Decrees supersede explicitly. Period names are frozen. **Nothing is ever silently rewritten.**

### 7.3 Templates as types

~~Phase 3 shows administrative tablets have Zipf s = 1.75 — they are a typed DSL, not free text.~~ Memory-layer encoders can compress template-heavy genres (admin, royal) at higher ratios than narrative if they're given the schema. The Phase-1 templates are exactly that schema.

> **WITHDRAWN (2026-07-31).** The s = 1.75 cross-genre comparison is a stream-length artifact: the genre
> streams differ ~60× in length, and at equal length every genre falls in 1.11–1.21. The estimator (OLS on
> log-log rank-frequency) is also biased, and its R² is not a goodness-of-fit test. The *compression*
> ranking that motivates the encoder idea does survive a length control, so the design suggestion stands on
> that basis — but not on Zipf. See `../CORRECTIONS.md`.

### 7.4 What does NOT translate

- **ELS / hidden codes**: Phase 3 found zero Bonferroni-significant skips. There is no hidden-message channel in the corpus.
- **Lexical-list internal structure**: our 69-tablet sample is too small to reverse-engineer the formal taxonomic hierarchy. Use the lexical primitive as a structural placeholder only; populate the actual taxonomy from external sources (CDLI, ePSD2).
- **Literary as workflow**: hymns and narratives use ordered speech acts but most lines are descriptive, not procedural. The `RitualSequenceAgent` metaphor works for *event-sourced workflows* generically, not for literal ritual orderings.

---

## 8. Implementation Roadmap

| Phase | Deliverable | Dep | Effort |
|---|---|---|---|
| 1 | `TabletMemory` (L1/L2/L3 tiers) — replace flat memory in your runtime | none | medium |
| 2 | `SealAuthority` (Rust crate) | crypto crate | medium |
| 3 | Universal write envelope `{payload, by_seal, witnesses, period}` enforced runtime-wide | 1 + 2 | small but invasive |
| 4 | `TempleLedger` for token/cost/tool-call accounting with periodic signed audits | 2 | medium |
| 5 | `LexicalOntology` for canonical entity store; backfill from existing memory store | 2 | large |
| 6 | `AddressedMessage` + `RitualSequence` for inter-agent RPC and workflow event-sourcing | 3 | medium |
| 7 | `RoyalDecree` + `YearNameRegistry` for policy/version/time control plane | 2 + 3 | small |

Phases 1–3 are the **foundation** — everything else assumes the universal envelope. Building 4–7 without 1–3 is the same mistake as building inline auth into every handler.

---

## 9. References

- Simmons, Diehl Martinez, Jurafsky (2024). *SumTablets: A Transliteration Dataset of Sumerian Tablets.* ML4AL workshop. CC BY 4.0.
- All cited tablet IDs (P-numbers and Q-numbers) refer to CDLI catalog entries; cross-reference at https://cdli.mpiwg-berlin.mpg.de/ or https://aicuneiform.com/.
- Sample manifests: `data/sample_500.parquet` (2,069 tablets) and `data/sample_long50.parquet` (197 tablets) — regeneratable from `scripts/phase0_sample.py`.
- All numerical claims reproducible from `scripts/phase{0,1,3}_*.py` with seed=42.
