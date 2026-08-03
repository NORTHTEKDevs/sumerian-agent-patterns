# Clay as Ground Truth: Testing Text-Chunking Signals Against 4,000-Year-Old Record Boundaries

**Kristian Baer** (Northtek) · Draft v1.0, 2026-08-02 · Not peer-reviewed
**Repository:** https://github.com/NORTHTEKDevs/sumerian-agent-patterns (all numbers regenerate from the pipeline; CI enforces prose–data agreement)

---

## Abstract

Chunking — deciding where one unit of memory ends and the next begins — is a load-bearing but
weakly evaluated step in retrieval-augmented generation and agent memory: published chunking work
evaluates downstream task metrics and, to our knowledge, never boundary placement itself. We
evaluate boundary-placement signals against an unusual ground truth: the ruling lines that Ur III
scribes (c. 2100–2000 BCE) physically drew between records on administrative tablets, preserved as
structural annotation in the SumTablets corpus (91,606 tablets). Unlike the annotator-judged
boundaries used in text-segmentation benchmarks, these boundaries are causally prior to any modern
judgment — a scribe drew them, for record-keeping reasons, four millennia before the evaluation
was conceived. We establish three results. (1) *Association:* ruling boundaries sit at points of
significantly lower cross-boundary trigram overlap than length-matched alternative cuts (2,095
adjacent pairs, 10,000 permutations, two independent nulls, BH-corrected p = 0.0006), and
record-closing formulae are strongly enriched in the line before a ruling (received-formula
*šu ba-ti* 6.3×, seal-formula *kišib₃* 2.5×, position-controlled p = 0.0001), while date formulae
— which close tablets, not entries — are depleted. (2) *Recovery:* association does not imply
recoverability. A global similarity-minimisation objective (the TextTiling-family signal
underlying modern "semantic chunking") fails to locate record boundaries, performing at or below
chance (Pk 0.454 vs. random 0.405); the sparse closing-formula cue, where present, nearly solves
the task (Pk 0.208 vs. 0.405). The pattern reverses on narrative text, where similarity carries
modest signal and closers are absent. (3) *Measurement:* the regex probes that identify these
formulae were themselves validated against expert lemmatisation (Oracc ePSD2, 3.6M tokens);
a naive royal-title probe turns out to match personal names 41% of the time, quantifying a
failure mode directly relevant to regex-based evaluation of agent systems. We argue the
practical implication for agent memory is that record-structured content — logs, tool traces,
transaction histories — should be chunked on structural end-markers, not embedding-similarity
valleys, and that chunking methods should be evaluated with boundary-recovery metrics, which the
RAG literature currently does not use. The project's full audit trail, including two claims
withdrawn during self-review and the controls that killed them, ships with the repository and is
enforced by CI.

---

## 1. Introduction

Every retrieval-augmented and memory-equipped agent system must decide where one retrievable unit
ends and the next begins. The decision is consequential — chunk boundaries determine what can be
retrieved atomically — yet it is usually made by convention (fixed token windows), by markup
(markdown headers), or by embedding-similarity heuristics ("semantic chunking"), and it is
evaluated, when evaluated at all, only through downstream task metrics. A recent taxonomy of
chunking strategies [Chunking-Taxonomy-2026] evaluates entirely via retrieval metrics; we found no
RAG-chunking publication that measures boundary placement against ground truth with the standard
segmentation metrics (Pk, WindowDiff).

One reason is that trustworthy boundary ground truth is scarce. Text-segmentation benchmarks
derive boundaries from annotator judgment (topic shifts), document structure created by the same
kind of author who writes the text (Wikipedia section headers [Koshorek-2018]), or artificial
concatenation of unrelated documents [Choi-2000]. In each case the ground truth is entangled with
modern textual convention, and in the concatenation case it is trivially easy.

This paper uses a ground truth with a different epistemic status. Ur III administrative tablets
(c. 2100–2000 BCE) carry horizontal ruling lines that scribes physically drew between records —
transaction entries in receipts, accounts, and ledgers. These are preserved as `$ ruling`
annotations in the Oracc transliteration standard and passed through as `<RULING>` tokens in the
SumTablets corpus [Simmons-2024]. A ruling on clay is not an annotator's post-hoc linguistic
judgment: it was incised by the document's author, for operational record-keeping reasons,
roughly four thousand years before anyone proposed to evaluate a chunking algorithm against it.
To our knowledge — supported by a targeted literature sweep (§2.3) — no prior work has used a
physical scribal mark as linear-segmentation ground truth in any ancient-document tradition, and
no prior work has statistically tested where cuneiform rulings fall relative to the text's
structure.

We ask three questions in sequence:

1. **Association.** Do ruling boundaries have measurable textual correlates — lower
   cross-boundary lexical overlap, characteristic preceding formulae? (§5)
2. **Recovery.** Do those correlates *suffice to find* the boundaries? This is the question a
   chunking algorithm cares about, and it is strictly harder. (§6)
3. **Measurement validity.** Are the lexical probes used to detect formulae actually measuring
   what their labels claim? We validate them against expert lemmatisation and report the failure
   modes. (§4)

The answers are, respectively: *yes, robustly; only the sparse formulaic cue suffices —
the similarity signal, though statistically real, is too weak to localise boundaries in
record-structured text; and only after correction* — a naive probe for "king" turns out to match
personal names 41% of the time.

**Provenance of this work, stated up front.** This project's original release claimed two
statistical findings that did not survive our own audit: a ruling-boundary parity result built on
an invalid null hypothesis (the corrected test initially returned a null result, and a properly
powered version then found a significant effect in the *opposite* direction), and a
Zipf-exponent genre comparison that was a stream-length artifact. Both retractions, the controls
that established them, and the CI machinery that keeps retracted claims coupled to their
corrections are part of the repository ([CORRECTIONS.md](CORRECTIONS.md)). We consider the audit
trail a contribution rather than an embarrassment, and hostile readers are invited to start there.

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
Fragkou-2004]. We claim no algorithmic novelty. Cue-phrase features for segmentation are also
established [Beeferman-1999, Passonneau-Litman]; our closing-formula cue is a corpus-derived,
statistically validated instance of that 25-year-old idea. Supervised neural segmentation
[Koshorek-2018, Lukasik-2020, Ghinassi-2024] is out of scope: our interest is what *unsupervised*
signals the boundaries carry. Evaluation uses Pk [Beeferman-1999] and WindowDiff [Pevzner-2002],
with their known pitfalls discussed in §8.

### 2.2 Chunking for RAG and agent memory

Current practice spans fixed/recursive splitting, header- and syntax-aware splitting (opening-
marker driven), embedding-similarity breakpoint "semantic chunking" (a local, greedy descendant of
TextTiling), late chunking [Gunther-2024], proposition-based retrieval units [Chen-2023], LLM-driven
segmentation [LumberChunker-2024], and contextual retrieval [Anthropic-2024]. Two gaps matter
here. First, published chunking evaluations use downstream retrieval/QA metrics exclusively; we
found none reporting boundary-recovery metrics against ground truth. Second, structure-aware
splitters are almost entirely *opening*-marker driven (headers, `def`/`class`); closing-marker
signals appear only incidentally. Agent-memory systems (MemGPT/Letta, Mem0, Zep/Graphiti) make no
published claims about boundary placement. Our contribution to this literature is a boundary-level
evaluation methodology with an unusually clean ground truth, and evidence that for
record-structured text the closing-marker cue dominates the similarity cue — not a competing
chunker.

### 2.3 Computational cuneiform studies

SumTablets [Simmons-2024] provides 91,606 tablets as parallel glyph/transliteration sequences with
structural tokens (`<SURFACE>`, `<COLUMN>`, `<RULING>`) passed through from Oracc ATF `$`-line
markup. Prior Ur III computational work includes the MTAAC pipeline [PagePerron-2017], Sumerian MT
[Punia-2020], and Sumerian NER [Luo-2015, Wang-2022] — the NER literature independently documents
personal-name/lexeme ambiguity as a hard, error-prone problem, which is precisely the failure our
probe audit quantifies (§4). On rulings, the ATF standard treats them as scribal sectioning
devices, and image-side work detects them physically [Dencker-2020], but we found no prior work
that statistically locates ruling placement relative to textual structure, and no use of rulings
(or any physical mark, in any tradition) as linear-segmentation ground truth. The lemmatised
ePSD2 Ur III corpus used for probe validation is credited to Veldhuis, Tinney, and ePSD2
contributors (CC BY-SA) [ePSD2].

## 3. Corpus and ground truth

We use SumTablets (91,606 tablets; 6,968,581 cuneiform glyphs; corpus totals independently
verified; zero duplicate IDs or transliterations). Analyses are genre-stratified throughout;
"Administrative" below means the ~85k-tablet administrative stratum dominated by Ur III. Ground
truth boundaries are `<RULING>` tokens between transliteration lines. 2,285 tablets carry at
least one ruling; after requiring ≥ 2 usable chunks, the primary analysis set is 1,716–1,783
administrative tablets (per-phase filters documented in the scripts).

**Reliability caveat, stated before any result.** `<RULING>` is inherited Oracc editorial markup
entered by many editors over decades, with no published accuracy figure; SumTablets' authors give
caveats for glyph coverage but none for structural tokens. Editorial inconsistency (rulings
present on the tablet but not transcribed, or vice versa) is therefore a real threat (§8). Two
observations bound it: omissions *dilute* rather than manufacture the effects we measure (missing
boundaries make nulls harder to beat, not easier), and the mechanism results (§5.2) show ruling
placement is predicted by the semantic content of the preceding line, which unmotivated editorial
noise would not produce.

## 4. Are the probes measuring what they claim? (Phases 1b & 7)

All formula detection here rests on regexes over transliteration. We audited them twice.

**Construction-level audit (Phase 1b).** Hand-built discriminators partition each probe's matches
into TRUE/FALSE/UNCLEAR against its claimed grammatical construction. Five of ten probes fell
below 50% precision and were marked do-not-cite in the data files themselves (`templates.json`
carries machine-readable `_audit_verdict` fields).

**Lexeme-level audit against expert annotation (Phase 7).** Every audited head token was tallied
across the Oracc ePSD2 Ur III corpus (80,181 tablets; 3,604,534 tokens), where each token carries
an expert-assigned citation form, guide word, and part of speech. Results:

| Probe | Claimed | Precision vs. gold | n |
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
people named Lugal-something), not the title "king". No surface pattern can make that distinction;
the Sumerian NER literature independently identifies it as a hard problem [Luo-2015]. The two
audits also *disagree* instructively: the construction-level audit was too harsh on three probes
(e.g. *diri* 19% → 94.3%), because "is this token the lexeme?" and "is this match the claimed
construction?" are different questions. Both are reported; boundary experiments (§5–6) use only
probes ≥ 95% at the lexeme level.

**Why agent researchers should care:** regex and keyword probes are ubiquitous in agent
evaluation ("did the model call the right tool?", "did the answer mention X?"). Here, probes that
looked precise ran at 34–58%, and the errors were invisible without gold annotation. Measured
probe validity should be a reported component of agent evals, not an assumption.

## 5. What properties do real boundaries have? (Phases 4 & 6)

### 5.1 Boundaries sit at similarity minima — measured with the right null

Statistic: mean shared trigrams between adjacent ruling-delimited chunks. The null matters more
than the statistic. A token-shuffle null (destroying all local structure) is *always* beaten by
real text and supported this project's original — withdrawn — claim. The correct primary null
permutes the order of the observed chunk lengths, moving only cut *positions* while preserving
the chunk-size distribution; an independent uniform-cuts null varies placement freely.

Full corpus, 10,000 permutations, bootstrap CIs, BH correction across genres:

| Genre | Pairs | Observed | Length-permute null | Δ | BH p (2-sided) |
|---|---:|---:|---:|---:|---:|
| Administrative | 2,095 | 1.188 | 1.517 | **−0.328** | **0.0006** |
| Literary | 248 | 1.169 | 1.425 | −0.256 | 0.278 |
| Royal | 64 | 1.281 | 1.524 | −0.242 | 0.565 |

Adjacent real chunks share ~22% *fewer* trigrams than length-matched alternative cuts. All genres
agree in direction; only Administrative is powered. Both nulls agree in sign everywhere.

### 5.2 Boundaries follow record-closing formulae — and only those

If a ruling ends a record, the line before it should carry record-*closing* formulae. Using only
gold-validated probes, against a null that permutes ruling positions (and a stricter variant that
permutes only within relative-position deciles, closing the positional co-clustering confound):

| Marker | Enrichment before ruling (position-controlled) | p |
|---|---:|---:|
| *šu ba-ti* "received" | **6.31×** | 0.0001 |
| *kišib₃* seal | **2.52×** | 0.0001 |
| *iti* month | 0.53× (depleted) | — |
| *mu* year-name | 0.28× (depleted) | — |
| letter-opening formula (negative control) | no signal | — |

The signal is *differentiated*, which is what makes it credible: transaction-closers enriched,
tablet-closers (dates) depleted — dates close tablets, not entries, and tablet-final lines are
excluded by design — and an opening formula flat. A philologist may regard the direction as
definitionally expected (*šu ba-ti* closes a transaction by definition); we agree, and frame this
as *quantifying* a definitional expectation — 6.31× with a controlled null — rather than
discovering it. The quantification is what §6 builds on, and it is also evidence against the
editorial-artifact concern: markup applied without regard to content would not reproduce it.

## 6. Do those properties suffice to FIND the boundaries? (Phase 8)

Setup: each tablet's line sequence, rulings removed; every method receives the true number of
segments K and places K−1 cuts (the standard known-K evaluation, isolating placement from count
estimation). Methods: `equal` (fixed-size), `random` (200-draw chance floor), `overlap_min`
(global adjacent-overlap minimisation, exact search for 99% of tablets; minimum-segment
constraint after an initial run exposed the degenerate tiny-segment optimum — documented in the
script), `closer` (cut after gold-validated closer lines; falls back to equal where none exist),
`hybrid` (overlap with fixed closer bonus, λ = 1, untuned). Metrics: Pk, WindowDiff, boundary F1
(exact, ±1). Paired sign tests per tablet.

**Administrative (1,717 tablets):**

| Method | Pk ↓ | WD ↓ | F1 ±1 ↑ |
|---|---:|---:|---:|
| random | 0.405 | 0.407 | 0.269 |
| equal | 0.438 | 0.440 | 0.301 |
| closer | **0.371** | **0.373** | **0.400** |
| overlap_min | 0.454 | 0.456 | 0.061 |
| hybrid | 0.395 | 0.397 | 0.205 |

Stratified honestly: on the 467 tablets containing at least one closer line, `closer` reaches
**Pk 0.208** — approaching solved — while its aggregate includes 1,250 closer-less tablets where
it degrades to equal spacing. Three results deserve emphasis:

1. **Association ≠ recoverability.** The similarity deficit at boundaries is statistically robust
   (§5.1) yet `overlap_min` performs at or *below* chance. A ~22% overlap reduction is far too
   weak to localise boundaries against the combinatorial background. Any argument of the form
   "boundaries correlate with X, therefore chunk on X" should be treated as unproven until X
   demonstrably recovers boundaries.
2. **The sparse discrete cue dominates.** Where a closing formula exists, it nearly pins the
   boundary (Pk 0.208). This is [Beeferman-1999]'s cue-phrase insight, demonstrated on
   four-millennia-old ground truth with a validated cue inventory.
3. **Fixed-size chunking is worse than random** (Pk 0.438 vs. 0.405): real records are uneven, so
   evenly spaced cuts are systematically misaligned. The most common chunking default in
   production RAG is, on this corpus, worse than cutting at random.

**Genre reversal.** On Literary tablets (91, narrative), `overlap_min` *does* beat random
(Pk 0.347 vs. 0.374; sign-test p = 0.02) and closers are essentially absent. On a small modern
transfer demo (this repository's own markdown documents, headings removed; 7 documents),
similarity again wins (0.381 vs. 0.450; 6/0 paired wins) — with the caveat that the demo is tiny
and in-domain, and its `closer` column is meaningless there (the only "closer" matches are our own
documents *quoting* the Sumerian formulae, a self-reference we flag rather than hide). The
emerging picture: **the informative boundary signal is genre-dependent — discrete end-markers for
record-structured text, distributional similarity for continuous prose.**

## 7. Implications for agent memory

Agent memory content — tool-call traces, transaction logs, episodic event streams — is
record-structured, not narrative. The results suggest, concretely:

- **Chunk record-structured content on structural end-markers** (tool-call terminations, status
  codes, signature/confirmation lines), not on embedding-similarity valleys. Where such markers
  exist they nearly solve boundary placement; similarity-driven chunking on this content class
  performed at chance despite the underlying signal being statistically real.
- **Evaluate chunkers on boundary recovery, not only downstream metrics.** The methodology here —
  known-K placement, Pk/WindowDiff/F1, permutation nulls matched on chunk-length profile — is
  directly portable, and the RAG literature currently lacks it entirely (§2.2).
- **Validate eval probes.** The 41%-personal-names result is a template for what silent probe
  failure looks like in any regex-scored agent benchmark.

We explicitly do *not* claim a new chunking algorithm, nor superiority over any deployed system;
no head-to-head against RAG chunkers on retrieval benchmarks was run. The contribution is the
ground truth, the evaluation design, and the measured dissociation between association and
recoverability.

## 8. Threats to validity

- **Ground-truth reliability.** `<RULING>` is inherited, unaudited editorial markup (§3). A
  cross-check against an independently curated Ur III database (e.g. BDTNS) or tablet imagery is
  the single most valuable external validation and has not been done.
- **Genre scope.** The strong results concern Ur III administrative records — a maximally
  formulaic genre. The closer-dominance claim is scoped to record-structured text; the literary
  and markdown results are directionally consistent but underpowered (n = 91 and 7).
- **Definitional circularity risk.** Closing formulae are, philologically, entry-closers; their
  enrichment before rulings quantifies rather than discovers. The recovery experiment (§6) is the
  non-circular payload: knowing closers close entries does not by itself tell you they suffice to
  localise boundaries, nor that similarity does not.
- **Metric pitfalls.** Pk penalises misses more than false alarms and both metrics depend on
  window size [Pevzner-2002]; we report WindowDiff and F1 alongside, use per-tablet windows at
  the standard half-mean-segment convention, and publish per-document values in the JSON.
- **Known-K is generous.** All methods receive the true segment count; real chunkers must also
  estimate K. Results are therefore upper bounds on placement quality, uniformly across methods.
- **One analyst.** No independent replication yet; no Assyriologist has adjudicated the
  philology beyond what published lemmatisation provides. Both invitations are open, with
  reproduction instructions and 100+ CI-enforced integrity checks in the repository.

## 9. The audit trail as method

Two of this project's original three statistical claims died under self-audit — one from an
invalid null (the corrected, properly powered test then found the effect *reversed*), one as a
sample-size artifact refit with the standard estimator [Clauset-2009]. Five of ten detection
probes were demoted after precision measurement; the demotions are machine-readable in the data
files. The repository's CI fails if a retracted claim loses its adjacent correction notice or if
prose numbers drift from generated JSON, and every negative control for those checks was itself
validated by deliberate breakage. We offer this as a working example of adversarial
self-correction in computational work on historical corpora, where the scarcity of domain experts
makes silent error especially durable.

## 10. Conclusion

A boundary drawn on clay four thousand years ago turns out to be a demanding, honest referee for
one of the most casually made decisions in modern agent systems. Its verdict: the similarity
signal that "semantic chunking" relies on is real but insufficient for record-structured text,
where sparse closing markers nearly solve the problem; fixed-size chunking is worse than random;
and the probes we use to measure any of this deserve the same audit as the claims they support.

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

*All numbers in this paper regenerate from `scripts/phase*.py`; `scripts/check_integrity.py`
fails CI if this document's headline figures drift from the generated JSON. The corpus is
CC BY 4.0 (SumTablets), the lemmatisation CC BY-SA (Oracc ePSD2); this paper and the analysis
artifacts are CC BY 4.0, the code MIT.*
