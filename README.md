# Sumerian Agent Patterns

**Empirical mining of the SumTablets cuneiform corpus (91,606 tablets, 6.97M glyphs) for software-design primitives applicable to modern multi-agent AI systems.**

What this is: a statistical and structural analysis of how Sumerian scribes organized information on clay tablets ~4,000 years ago, with the patterns mapped 1:1 to named agent-framework primitives. Every claim cites the tablet IDs that motivated it.

What this isn't: a paper, a product, or a claim that the Sumerians "invented" modern computing. The observation that Sumerian administration is a proto-information-system is well-established. The contribution here is the **empirical mining of the actual corpus** with statistical controls, plus a **named primitive catalog** with cited tablet IDs and code shapes.

## TL;DR Findings

- **Administrative tablets are a domain-specific language.** Per-genre Zipf analysis: Administrative s = 1.746, Royal Inscription s = 1.737 (natural language ≈ 1.0). Compression-Δ vs shuffled baseline is positive in every genre, peaking at +0.099 for Royal Inscription — confirming structural redundancy beyond simple frequency skew.
- **`<RULING>` markers are statistically validated row separators.** Adjacent ruling-bounded chunks share trigrams 30–500× more than shuffled baselines. Royal Inscription p = 0.002, Administrative p = 0.005.
- **No hidden codes.** A 99-skip × 5-genre × 1,000-shuffle ELS scan returned zero Bonferroni-significant hits across 495 tests. The corpus's periodicities are explained by template recurrence, not encoded messages.
- **Bureaucratic primitives are pervasive.** `kišib₃` (seal of) in 25.4% of Administrative tablets, `mu` (year-formula) in 74.2%, `u₃-na-a-du₁₁` ("speak to him") in 58.8% of Letters. These map directly to modern concepts: signed envelopes, named time periods, RPC headers.

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
    └── FULL_IDEAS.md                  ~150 ideas across 16 categories
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
