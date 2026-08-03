# Clay as Ground Truth: Testing Text-Chunking Signals Against 4,000-Year-Old Record Boundaries

**Kristian Baer** (Northtek) · Draft v1.1, 2026-08-02 · Not peer-reviewed
**Repository:** https://github.com/NORTHTEKDevs/sumerian-agent-patterns (all numbers regenerate from the pipeline; CI enforces prose–data agreement)

> Draft v1.1 incorporates the findings of a five-reviewer adversarial gate run on v1.0 before any
> external circulation. The issues it caught — including a sign-test implementation that was not
> genuinely two-sided, a transfer demo that ingested its own output file, and an abstract that
> advised against a method never actually tested — are catalogued in §9 and in the commit history.

---

## Abstract

Chunking — deciding where one unit of memory ends and the next begins — is a load-bearing but
weakly evaluated step in retrieval-augmented generation and agent memory: to our knowledge,
published chunking work evaluates downstream task metrics and never boundary placement itself. We
evaluate boundary-placement signals against an unusual ground truth: the ruling lines that Ur III
scribes (c. 2100–2000 BCE) physically drew between records on administrative tablets, preserved
as structural annotation in the SumTablets corpus (91,606 tablets). Unlike the annotator-judged
boundaries used in text-segmentation benchmarks, these boundaries are causally prior to any
modern judgment. We establish three results. (1) *Association:* ruling boundaries sit at points
of significantly lower cross-boundary trigram overlap than length-matched alternative cuts (2,095
adjacent pairs, 10,000 permutations, two independent nulls, BH-corrected p = 0.0006), and
record-closing formulae are strongly enriched in the line before a ruling (*šu ba-ti* "received"
6.31×, *kišib₃* seal 2.52×, position-controlled p = 0.0001). (2) *Recovery:* association does not
imply recoverability. A global **lexical** similarity-minimisation objective — exact trigram
overlap, the TextTiling-family signal from which embedding-based "semantic chunking" descends;
embedding-based chunkers themselves were **not** tested here — fails to locate record boundaries,
losing the per-tablet comparison to random cuts 550/1,165 (BH p < 10⁻⁴). The sparse
closing-formula cue, on the 27% of tablets where it exists, nearly solves the task: Pk 0.208
versus 0.408 for random cuts *on those same tablets*. On the majority of tablets, which carry no
marker, boundary placement remains unsolved. (3) *Measurement:* the regex probes identifying
these formulae were validated against expert lemmatisation (Oracc ePSD2, 3.6M tokens); a naive
royal-title probe matches personal names 41% of the time, quantifying a failure mode directly
relevant to regex-scored evaluation of agent systems. We argue the practical implication for
agent memory is that record-structured content should be chunked on structural end-markers where
they exist — the lexical-cohesion signal alone was insufficient here — and that chunking methods
should be evaluated with boundary-recovery metrics, which the RAG literature currently lacks. The
project's full audit trail, including two withdrawn claims and the reviewer-caught defects of
this paper's own first draft, ships with the repository and is enforced by CI.

---

## 1. Introduction

Every retrieval-augmented and memory-equipped agent system must decide where one retrievable unit
ends and the next begins. The decision is consequential, yet it is usually made by convention
(fixed token windows), by markup (markdown headers), or by embedding-similarity heuristics
("semantic chunking"), and evaluated, when evaluated at all, only through downstream task
metrics. A recent taxonomy of chunking strategies [Chunking-Taxonomy-2026] evaluates entirely via
retrieval metrics; we found no RAG-chunking publication that measures boundary placement against
ground truth with the standard segmentation metrics (Pk, WindowDiff).

One reason is that trustworthy boundary ground truth is scarce. Text-segmentation benchmarks
derive boundaries from annotator judgment, from document structure created by the same kind of
author who writes the text (Wikipedia section headers [Koshorek-2018]), or from artificial
concatenation of unrelated documents [Choi-2000].

This paper uses a ground truth with a different epistemic status. Ur III administrative tablets
carry horizontal ruling lines that scribes physically drew between records — transaction entries
in receipts, accounts, and ledgers. These are preserved as `$ ruling` annotations in the Oracc
transliteration standard and passed through as `<RULING>` tokens in SumTablets [Simmons-2024]. A
ruling on clay is not an annotator's post-hoc linguistic judgment: it was incised by the
document's author, for operational reasons, four millennia before anyone proposed to evaluate a
chunking algorithm against it. Within computational cuneiform studies, no prior work statistically
tests where rulings fall relative to textual structure (§2.3); more broadly, our segmentation-
literature sweep found no use of a physical scribal mark as linear-segmentation ground truth in
other traditions either — the closest analogue, Greek papyrological *paragraphos* marks, has been
studied only as an image-detection problem — though we state this as the result of a bounded
search, not a proof of absence.

We ask three questions in sequence: **association** (do ruling boundaries have measurable textual
correlates? §5), **recovery** (do those correlates suffice to *find* the boundaries? §6), and
**measurement validity** (are the probes used to detect formulae measuring what their labels
claim? §4).

**Provenance of this work, stated up front.** This project's original release claimed two
statistical findings that did not survive our own audit: a ruling-boundary parity result built on
an invalid null (the corrected, properly powered test then found the effect *reversed*), and a
Zipf-exponent genre comparison that was a stream-length artifact. Both retractions, the controls
that established them, and the CI machinery that keeps retracted claims coupled to their
corrections are part of the repository ([CORRECTIONS.md](CORRECTIONS.md)). The first draft of
this very paper then failed its own adversarial review gate in five places (§9). We consider the
audit trail a contribution rather than an embarrassment, and hostile readers are invited to start
there.

## 2. Related work

### 2.1 Text segmentation

Cutting at lexical-cohesion minima originates with TextTiling [Hearst-1994, Hearst-1997], which
scores cohesion between adjacent blocks and places boundaries at score valleys. Successors include
C99 [Choi-2000], statistical dynamic-programming segmentation [Utiyama-2001, Fragkou-2004],
minimum-cut segmentation with known K [Malioutov-2006], and Bayesian segmentation
[Eisenstein-2008]. Our similarity objective — place K−1 cuts to minimise total adjacent-segment
trigram overlap — is squarely in this family: the *signal* is TextTiling's, the known-K global
optimisation is closest to [Malioutov-2006], and because our cost couples adjacent segment pairs
it is a second-order variant of the first-order per-segment DP costs of [Utiyama-2001,
Fragkou-2004]. We claim no algorithmic novelty. Cue-phrase features for segmentation are equally
established [Beeferman-1999, Passonneau-Litman]; our closing-formula cue is a corpus-derived,
statistically validated instance of that 25-year-old idea. Supervised neural segmentation
[Koshorek-2018, Lukasik-2020, Ghinassi-2024] is out of scope: our interest is what *unsupervised*
signals the boundaries carry. Evaluation uses Pk [Beeferman-1999] and WindowDiff [Pevzner-2002];
our implementations are hand-written from the published formulas (N−k window convention — NLTK
uses N−k+1, so library reproductions will differ in the third decimal), and their pitfalls are
discussed in §8.

### 2.2 Chunking for RAG and agent memory

Current practice spans fixed/recursive splitting, header- and syntax-aware splitting (opening-
marker driven), embedding-similarity breakpoint "semantic chunking" (a local, greedy descendant of
TextTiling), late chunking [Gunther-2024], proposition-based retrieval units [Chen-2023],
LLM-driven segmentation [LumberChunker-2024], and contextual retrieval [Anthropic-2024]. Two gaps
matter here, both stated to our knowledge after a targeted sweep: published chunking evaluations
use downstream retrieval/QA metrics exclusively, with none reporting boundary-recovery metrics
against ground truth; and structure-aware splitters are almost entirely *opening*-marker driven,
with closing-marker signals appearing only incidentally. Agent-memory systems (MemGPT/Letta,
Mem0, Zep/Graphiti) make no published claims about boundary placement. Our contribution to this
literature is a boundary-level evaluation methodology with an unusually clean ground truth — not
a competing chunker, and not a test of embedding-based semantic chunking, which we did not run.

### 2.3 Computational cuneiform studies

SumTablets [Simmons-2024] provides 91,606 tablets as parallel glyph/transliteration sequences
with structural tokens passed through from Oracc ATF `$`-line markup. Prior Ur III computational
work includes the MTAAC pipeline [PagePerron-2017], Sumerian MT [Punia-2020], and Sumerian NER
[Luo-2015, Wang-2022] — the NER literature independently documents personal-name/lexeme ambiguity
as a hard problem, which is precisely the failure our probe audit quantifies (§4). The ATF
standard treats rulings as scribal sectioning devices, and image-side work detects them
physically [Dencker-2020], but we found no prior work statistically locating ruling placement
relative to textual structure. The lemmatised ePSD2 Ur III corpus used for probe validation is
credited to Veldhuis, Tinney, and ePSD2 contributors (CC BY-SA) [ePSD2].

## 3. Corpus and ground truth

We use SumTablets (91,606 tablets; 6,968,581 cuneiform glyphs; totals independently verified;
zero duplicate IDs or transliterations). Analyses are genre-stratified throughout. Ground-truth
boundaries are `<RULING>` tokens between transliteration lines. 2,285 tablets carry at least one
ruling (this count is emitted by the Phase 8 pipeline as `corpus_prefilter`, not hand-computed);
after per-phase filters (interior boundaries only, minimum lines, a 120-line tractability cap
that excludes 29 tablets — also persisted in the JSON), the primary analysis set is 1,716–1,783
administrative tablets.

**Reliability caveat, stated before any result.** `<RULING>` is inherited Oracc editorial markup
entered by many editors over decades, with no published accuracy figure; SumTablets' authors give
caveats for glyph coverage but none for structural tokens. Editorial inconsistency is therefore a
real threat (§8). Two observations bound it: omissions *dilute* rather than manufacture the
effects we measure, and the mechanism results (§5.2) show ruling placement is predicted by the
semantic content of the preceding line, which unmotivated editorial noise would not produce.

## 4. Are the probes measuring what they claim? (Phases 1b & 7)

All formula detection rests on regexes over transliteration. We audited them twice — first with
hand-built construction-level discriminators (Phase 1b), then against the Oracc ePSD2 Ur III
corpus (80,181 tablets; 3,604,534 tokens), where every token carries an expert-assigned citation
form, guide word, and part of speech (Phase 7):

| Probe | Claimed | Precision vs. gold (lexeme) | n |
|---|---|---:|---:|
| `seal_of_PN` (*kišib₃*) | seal attribution | 100.0% | 30,044 |
| `received_by` (*šu ba-ti*) | receipt formula | 99.8% | 14,452 |
| `ensi_title` (*ensi₂*) | governor title | 98.6% | 9,379 |
| `son_of_PN` (*dumu*) | filiation | 95.4% | 53,359 |
| `excess_diri` (*diri*) | excess | 94.3% | 3,687 |
| `witness_eye` (*igi*) | witness lexeme | 71.5% | 7,213 |
| `year_formula` (*mu*) | year lexeme | 70.6% | 94,309 |
| `king_title` (*lugal*) | royal title | **58.0%** | 73,749 |

The headline failure: **41% of *lugal* occurrences are personal names** (30,381 tagged PN —
people named Lugal-something), not the title "king". No surface pattern can make that
distinction; the Sumerian NER literature independently identifies it as hard [Luo-2015]. The two
audits also *disagree* instructively — the construction-level audit was too harsh on three probes
(e.g. *diri* 19% at construction level vs. 94.3% at lexeme level) because "is this token the
lexeme?" and "is this match the claimed construction?" are different questions. Both audits are
published in full.

**Probe usage downstream, stated precisely.** The recovery experiment (§6) uses as boundary cues
only the two probes at ≥ 99% lexeme precision (*kišib₃*, *šu ba-ti*). The mechanism table (§5.2)
additionally *reports* date formulae (*iti*: unaudited at construction level; *mu*: 70.6% at
lexeme level, stricter variant unaudited) — those rows serve as directional context and negative
contrast, and are never used as boundary cues.

**Why agent researchers should care:** regex and keyword probes are ubiquitous in agent
evaluation. Here, probes that looked authoritative measured the wrong thing at rates from 6% to
42% depending on probe and audit level, and the errors were invisible without gold annotation.
Measured probe validity should be a reported component of agent evals, not an assumption.

## 5. What properties do real boundaries have? (Phases 4 & 6)

### 5.1 Boundaries sit at similarity minima — measured with the right null

Statistic: mean shared trigrams between adjacent ruling-delimited chunks. The null matters more
than the statistic: a token-shuffle null (destroying all local structure) is *always* beaten by
real text, and supported this project's original — withdrawn — claim. The correct primary null
permutes the order of the observed chunk lengths, moving only cut positions while preserving the
chunk-size distribution; an independent uniform-cuts null varies placement freely.

Full corpus, 10,000 permutations, bootstrap CIs, BH correction across genres:

| Genre | Pairs | Observed | Length-permute null | Δ | BH p (2-sided) |
|---|---:|---:|---:|---:|---:|
| Administrative | 2,095 | 1.188 | 1.517 | **−0.328** | **0.0006** |
| Literary | 248 | 1.169 | 1.425 | −0.256 | 0.278 |
| Royal | 64 | 1.281 | 1.524 | −0.242 | 0.565 |

Adjacent real chunks share ~22% *fewer* trigrams than length-matched alternative cuts. All genres
agree in direction; only Administrative is powered.

### 5.2 Boundaries follow record-closing formulae — and only those

Against a null that permutes ruling positions within relative-position deciles (closing the
positional co-clustering confound):

| Marker | Enrichment before ruling (position-controlled) | p | Probe audit status |
|---|---:|---:|---|
| *šu ba-ti* "received" | **6.31×** | 0.0001 | 99.8% (gold) |
| *kišib₃* seal | **2.52×** | 0.0001 | 100% (gold) |
| *iti* month | 0.53× (depleted) | — | context row; unaudited construction |
| *mu* year-name | 0.28× (depleted) | — | context row; lexeme 70.6% |
| letter-opening formula (negative control) | no signal | — | 100% (gold) |

The signal is *differentiated*: transaction-closers enriched, tablet-closers (dates) depleted —
dates close tablets, not entries — and an opening formula flat. A philologist may regard the
direction as definitionally expected; we agree, and frame this as *quantifying* a definitional
expectation, not discovering it. The quantification is what §6 builds on, and it also weighs
against the editorial-artifact concern: markup applied without regard to content would not
reproduce it.

## 6. Do those properties suffice to FIND the boundaries? (Phase 8)

Setup: each tablet's line sequence, rulings removed; every method receives the true number of
segments K and places K−1 cuts (known-K evaluation, isolating placement from count estimation).
Methods: `equal` (fixed-size), `random` (200-draw chance floor), `overlap_min` (global
adjacent-trigram-overlap minimisation, exact search for 99% of tablets; a minimum-segment
constraint was added after the first run exposed the degenerate tiny-segment optimum — documented
in the script), `closer` (cut after gold-validated closer lines; falls back to equal where none
exist), `hybrid` (overlap with fixed closer bonus, λ = 1, untuned). Metrics: Pk, WindowDiff,
boundary F1. Paired two-sided sign tests, BH-corrected within each corpus.

**Administrative (1,717 tablets):**

| Method | Pk ↓ | WD ↓ | F1 ±1 ↑ |
|---|---:|---:|---:|
| random | 0.405 | 0.407 | 0.269 |
| equal | 0.438 | 0.440 | 0.301 |
| closer | **0.371** | **0.373** | **0.400** |
| overlap_min | 0.454 | 0.456 | 0.061 |
| hybrid | 0.395 | 0.397 | 0.205 |

Three results, each stated with its honest scope:

1. **The lexical similarity objective fails.** `overlap_min` loses the per-tablet paired
   comparison against random cuts **550 wins / 1,165 losses** (two-sided sign test, BH p < 10⁻⁴)
   and has worse mean Pk (0.454 vs. 0.405). The similarity deficit at boundaries is statistically
   robust (§5.1) yet far too weak to localise boundaries against the combinatorial background.
   One nuance: against `equal` (itself worse than random here), `overlap_min` wins slightly more
   often than it loses (756/660, BH p = 0.014) while having a worse mean — better on the median
   tablet, catastrophically worse on a heavy tail. For a chunking system that tail profile is
   arguably the more damning failure mode. *Scope:* this tests the lexical instantiation of the
   similarity signal; embedding-based chunkers might extract signal trigrams miss and were not
   tested.
2. **The sparse discrete cue nearly solves the task — where it exists.** The honest comparison is
   stratified on the same population: on the **467 tablets (27%) containing a closer line**,
   `closer` reaches **Pk 0.208** vs. **0.408 for random and 0.453 for equal on those same
   tablets**. (The aggregate paired test against random — 815/901, BH p = 0.04 in random's favour
   — is dominated by the 1,250 closer-less tablets where `closer` degrades to equal spacing; we
   report it to preempt selective reading, and cite only the stratified numbers as the finding.)
   This is [Beeferman-1999]'s cue-phrase insight on four-millennia-old ground truth. **On the 73%
   of tablets with no marker, boundary placement remains unsolved** — no method tested here beats
   random there, and we state that as an open problem rather than burying it.
3. **Fixed-size chunking is worse than random** (Pk 0.438 vs. 0.405): real records are uneven, so
   evenly spaced cuts are systematically misaligned. The most common chunking default in
   production RAG is, on this corpus, worse than cutting at random.

**Genre contrast — directional, not significant.** On Literary tablets (91, narrative),
`overlap_min` has better mean Pk than random (0.347 vs. 0.374) and wins the paired test against
`equal` 44/24 — but after BH correction no Literary comparison is significant (all BH p ≥ 0.11).
We therefore describe the reversal — similarity helping on narrative where closers are absent —
as a directional hint requiring a larger narrative corpus, not a finding. A modern markdown demo
remains in the pipeline for illustration but was reduced to **2 documents** after review caught
it ingesting self-referential inputs (including, on rerun, its own output file); at n = 2 it
carries no evidential weight and we cite no numbers from it.

## 7. Implications for agent memory

Agent memory content — tool-call traces, transaction logs, episodic event streams — is
record-structured, not narrative. With the scopes established above:

- **Where structural end-markers exist, chunk on them.** Tool-call terminations, status codes,
  signature/confirmation lines are the modern analogues of *šu ba-ti*; on marker-bearing records
  the cue nearly pinned boundaries while the lexical-cohesion objective performed below chance.
  The advice is conditional by construction: on the majority of our tablets no marker existed and
  nothing tested here worked — for markerless record streams, boundary placement is an open
  problem, and engineered delimiters (making agent traces *carry* explicit closers) may be worth
  more than any post-hoc segmentation.
- **Evaluate chunkers on boundary recovery, not only downstream metrics.** The methodology here —
  known-K placement, Pk/WindowDiff/F1, permutation nulls matched on chunk-length profile,
  stratified same-population baselines — is directly portable, and to our knowledge the RAG
  literature lacks it entirely.
- **Validate eval probes.** The 41%-personal-names result is a template for silent probe failure
  in any regex-scored agent benchmark.

We do *not* claim a new chunking algorithm, superiority over any deployed system, or anything
about embedding-based semantic chunking, which was not tested.

## 8. Threats to validity

- **Ground-truth reliability.** `<RULING>` is inherited, unaudited editorial markup (§3). A
  cross-check against an independently curated Ur III database (e.g. BDTNS) or tablet imagery is
  the most valuable external validation and has not been done.
- **Genre scope.** The strong results concern Ur III administrative records. The closer-dominance
  claim is scoped to record-structured text with markers present (27% here); the narrative
  contrast is directional only (§6).
- **Definitional circularity risk.** Closing formulae are, philologically, entry-closers; §5.2
  quantifies rather than discovers. The recovery experiment is the non-circular payload.
- **Metric pitfalls.** Pk penalises misses more than false alarms; both metrics are window-size
  dependent [Pevzner-2002]. We report WindowDiff and F1 alongside, use per-tablet windows at the
  standard half-mean-segment convention, and publish per-document values. Implementations are
  hand-written to the published formulas (§2.1) — NLTK reproductions will differ slightly.
- **Known-K is generous.** All methods receive the true segment count; results are upper bounds
  on placement quality, uniformly across methods.
- **The similarity method tested is lexical, not neural.** Embedding-based semantic chunking may
  behave differently; testing it on this ground truth is the obvious next experiment.
- **Statistical hygiene of this draft.** The v1.0 sign test was not genuinely two-sided (it
  saturated at p = 1 for methods losing most comparisons); v1.1 uses the corrected two-tail form,
  BH-corrects all paired tests within each corpus, and discloses the change in the script
  docstring. All quoted p-values are from the corrected implementation.
- **One analyst; no external replication yet.** No Assyriologist has adjudicated the philology
  beyond published lemmatisation. Reproduction instructions and 100+ CI-enforced integrity checks
  ship with the repository.

## 9. The audit trail as method

Two of this project's original three statistical claims died under self-audit — one from an
invalid null (the corrected, properly powered test then found the effect *reversed*), one as a
stream-length artifact refit with the standard estimator [Clauset-2009]. Five of ten detection
probes were demoted after precision measurement, machine-readably. The first draft of this paper
then went through a five-reviewer adversarial gate, which caught: an abstract recommending
against embedding-similarity chunking when only the lexical signal had been tested; sign-test
statistics attached to comparisons never computed; a sign-test implementation that was not
two-sided; a transfer demo whose input set included the pipeline's own output file; an unsourced
corpus count; and a CI tolerance wide enough to let the paper's central ordering claim silently
reverse. Every one is fixed in v1.1, the CI checks were tightened accordingly, and the defects
are preserved in the commit history rather than amended away. We offer this as a working example
of adversarial self-correction in computational work on historical corpora, where the scarcity of
domain experts makes silent error unusually durable.

## 10. Conclusion

A boundary drawn on clay four thousand years ago turns out to be a demanding, honest referee for
one of the most casually made decisions in modern agent systems. Its verdict, within the scopes
measured here: the lexical-cohesion signal that similarity-based chunking descends from is real
but insufficient for record-structured text; sparse closing markers, where they exist, nearly
solve the problem; fixed-size chunking is worse than random; markerless records remain open; and
the probes used to measure any of this deserve the same audit as the claims they support.

## References

- [Anthropic-2024] Introducing Contextual Retrieval. Anthropic engineering blog, 2024. https://www.anthropic.com/news/contextual-retrieval
- [Beeferman-1999] Beeferman, Berger, Lafferty. Statistical Models for Text Segmentation. *Machine Learning* 34:177–210, 1999.
- [Chen-2023] Chen et al. Dense X Retrieval: What Retrieval Granularity Should We Use? arXiv:2312.06648; EMNLP 2024.
- [Choi-2000] Choi. Advances in Domain Independent Linear Text Segmentation. NAACL 2000.
- [Chunking-Taxonomy-2026] Beyond Chunk-Then-Embed: A Comprehensive Taxonomy and Evaluation of Document Chunking Strategies. arXiv:2602.16974.
- [Clauset-2009] Clauset, Shalizi, Newman. Power-law Distributions in Empirical Data. *SIAM Review* 51(4):661–703, 2009.
- [Dencker-2020] Dencker et al. Deep learning of cuneiform sign detection with weak supervision using transliteration alignment. *PLOS ONE*, 2020.
- [Eisenstein-2008] Eisenstein, Barzilay. Bayesian Unsupervised Topic Segmentation. EMNLP 2008.
- [ePSD2] Veldhuis, Tinney, and ePSD2 contributors. epsd2/admin/ur3: Ur III Administrative Texts. Oracc. CC BY-SA. http://oracc.org/epsd2/admin/ur3
- [Fragkou-2004] Fragkou, Petridis, Kehagias. A Dynamic Programming Algorithm for Linear Text Segmentation. *JIIS* 23:179–197, 2004.
- [Ghinassi-2024] Ghinassi, Wang, Newell, Purver. Recent advances in text segmentation. Findings of EMNLP 2024. arXiv:2411.16613.
- [Gunther-2024] Günther et al. Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models. arXiv:2409.04701.
- [Hearst-1994] Hearst. Multi-Paragraph Segmentation of Expository Text. ACL 1994.
- [Hearst-1997] Hearst. TextTiling: Segmenting Text into Multi-paragraph Subtopic Passages. *Computational Linguistics* 23(1):33–64, 1997.
- [Koshorek-2018] Koshorek et al. Text Segmentation as a Supervised Learning Task. NAACL 2018.
- [LumberChunker-2024] Duarte et al. LumberChunker: Long-Form Narrative Document Segmentation. Findings of EMNLP 2024. arXiv:2406.17526.
- [Luo-2015] Luo, Liu et al. Enhancing Sumerian Lemmatization by Unsupervised Named-Entity Recognition. NAACL 2015.
- [Lukasik-2020] Lukasik et al. Text Segmentation by Cross Segment Attention. EMNLP 2020.
- [Malioutov-2006] Malioutov, Barzilay. Minimum Cut Model for Spoken Lecture Segmentation. ACL 2006.
- [PagePerron-2017] Pagé-Perron, Sukhareva, Khait, Chiarcos. Machine Translation and Automated Analysis of the Sumerian Language. SIGHUM/ACL 2017.
- [Passonneau-Litman] Passonneau, Litman. Discourse Segmentation by Human and Automated Means. *Computational Linguistics* 23(1), 1997.
- [Pevzner-2002] Pevzner, Hearst. A Critique and Improvement of an Evaluation Metric for Text Segmentation. *Computational Linguistics* 28(1):19–36, 2002.
- [Punia-2020] Punia et al. Towards the First Machine Translation System for Sumerian Transliterations. COLING 2020.
- [Simmons-2024] Simmons, Diehl Martinez, Jurafsky. SumTablets: A Transliteration Dataset of Sumerian Tablets. ML4AL, ACL 2024.
- [Utiyama-2001] Utiyama, Isahara. A Statistical Model for Domain-Independent Text Segmentation. ACL 2001.
- [Wang-2022] Wang, Liu, Hearne. Few-shot Learning for Sumerian Named Entity Recognition. DeepLo, ACL 2022.

---

*All numbers regenerate from `scripts/phase*.py`; `scripts/check_integrity.py` fails CI if this
document's headline figures drift from the generated JSON. Corpus CC BY 4.0 (SumTablets);
lemmatisation CC BY-SA (Oracc ePSD2); this paper and analysis artifacts CC BY 4.0; code MIT.*
