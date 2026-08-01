# Notes for Reviewers

Thank you for looking at this. This document points you straight at the weakest parts rather than making you find them. The list is ordered by where a serious problem is most likely to remain.

## What this repo is, stated plainly

A reproducible pipeline that mines a cuneiform corpus for recurring bureaucratic patterns, an argument that those patterns map usefully onto multi-agent software design, and one engineering benchmark.

It is **not** an Assyriology contribution. The corpus observations are, as far as I know, unsurprising to a specialist — Sumerian administrative practice as a proto-information-system is well-trodden ground. The intended contribution is the *pipeline*, the *mapping*, and honest accounting of how much each claim bears.

**A self-audit on 2026-07-31 withdrew two of the three original statistical findings.** Both are documented in [CORRECTIONS.md](CORRECTIONS.md) with the controls that killed them:

- **RULING-parity** (was Royal p=0.002, Admin p=0.005) — the null shuffled all tokens, which destroys the local coherence any natural text has. Under a null that permutes only boundary *placement*, the effect vanishes in every genre.
- **Zipf-as-DSL** (was Admin s=1.746 vs Lexical s=1.114) — a stream-length artifact. Streams differ ~60× in length; at equal length every genre falls in 1.11–1.21.

What survives: the compression-redundancy ranking (tested against the same length confound and robust to it), the ELS null result, descriptive probe frequencies, and the benchmark. The claim-by-claim table is in the README under **Claims and Evidence Strength** — please attack that table first. If a claim is graded too generously, that is the most damaging error left.

## Where I would attack it first

1. **The regex probes — still the highest value for your time.** Every Phase 1 frequency comes from hand-written regexes over transliterated text (`PROBES` in `scripts/phase1_templates.py`). I have now precision-audited 10 of them (`scripts/phase1b_probe_validation.py` → [`outputs/probe_validation.md`](outputs/probe_validation.md)) and **5 failed badly enough to be marked DO-NOT-CITE**:

   | Probe | Claimed role | Precision | Actually matching |
   |---|---|---:|---|
   | `god_dedication` | dedicatory formula | 6% | `nam-lugal` "kingship", `nam-en` "lordship" — abstract nouns |
   | `excess_diri` | excess / surplus | 19% | `diri` + month = **intercalary month** |
   | `year_formula` | year-name | 34% | verbal prefixes `mu-na-`, `mu-un-`, `mu-ni-` |
   | `witness_eye` | witness clause | 41% | `igi-zu-še₃` "before you"; `igi-nim` "upper/north" |
   | `king_title` | title: king | 42% | `lugal-` as a personal-name element |

   Validating cleanly: `received_by` 100%, `speak_to_him` 100%, `total_audit` 100%, `seal_of_PN` 96%, `son_of_PN` 95%. A sixth probe, `credit_mu_DU`, **never fires at all** — it searches `mu-DU` while the corpus writes `mu-kuₓ(DU)` (60 occurrences), and Phase 1 silently drops zero-hit probes.

   **What I need from you:** my discriminators encode standard dictionary values applied by a non-specialist, and are deliberately conservative, so the reported error rates are *lower bounds*. Are any of my TRUE buckets actually wrong? In particular: (a) is bare `lugal` in Ur III administrative context ever safely "the king" rather than "owner/master"? (b) is my `igi PN-še₃` TRUE bucket really a witness clause, or does it include other uses? (c) does `diri` + quantity reliably mean surplus? Correcting a *false TRUE* matters more than adding a false FALSE, because the TRUE buckets are what the README still cites.

2. **Is the replacement RULING null itself correct?** It holds real token order and the exact multiset of chunk lengths and permutes only where cuts fall (`ruling_parity`). If that control is also flawed, I want to know before this goes anywhere.

3. **Does the compression-Δ result really survive?** It uses the same token-shuffle baseline that broke the RULING claim. I argue it is legitimate *there* because the claim is only "more structured than random token order", and I tested it against the length confound that broke Zipf — the genre ranking holds at equal-length contiguous blocks. That control must use contiguous blocks; scattered-position sampling destroys adjacency and manufactures a collapse. **I made exactly that mistake during the audit and had to redo it**, which is reason enough to check my reasoning rather than trust it.

4. **ELS statistical power.** At 1,000 permutations the minimum attainable p is ~0.001, roughly 10× the Bonferroni threshold of 0.000101 — so the scan cannot return a Bonferroni-significant result by construction. It now reports 3 nominal hits (p<0.01) against ~5 expected by chance. Is that reframing sufficient, or should the permutation count simply go to ~10,000?

5. **Sample size and imbalance.** 500 tablets per genre from a corpus that is 92%+ administrative: Lexical is sampled exhaustively (n=69, all of them) while Administrative is sampled at well under 1%. The RULING analysis rests on 10–17 adjacent-chunk pairs in some genres. Are per-genre comparisons meaningful at all under this imbalance?

6. **Multiple comparisons across the whole repo.** Bonferroni is applied within the ELS scan (495 tests) but *not* across the full set of hypotheses entertained — 24 probes, 5 Zipf fits, 5 compression deltas, 5 parity tests. With enough probes something looks interesting. I have no principled correction for this and would welcome a recommendation.

7. **The mapping itself.** Does "Sumerian scribes used seals, therefore agent writes should carry signed envelopes" survive as more than an analogy? The benchmark shows a sealed log answers audit queries an anonymous one cannot — but that is close to true by construction, since the anonymous log lacks the queried fields. I think it demonstrates the *cost* side honestly (+59% bytes, +37 tokens/write) while the capability side is definitional, and the README now says so. Push on that.

## Reproducing it

Full instructions in the README under **How to Reproduce**. ~8 minutes, no API keys, no GPU:

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/phase0_sample.py
python scripts/phase1_templates.py
python scripts/phase1b_probe_validation.py   # the probe precision audit
python scripts/phase3_compression.py
git diff --stat outputs/     # expected: empty
```

Fastest path to judging this repo: read `outputs/probe_validation.md` (which probe frequencies are citable) and `CORRECTIONS.md` (what was withdrawn and why). Together they are about 10 minutes and cover every claim that has been challenged so far.

Verified end to end from a clean clone on Python 3.14.2 / numpy 2.5.1 / pandas 3.0.5. `outputs/templates.json` and `outputs/phase3_raw.json` regenerate byte-identical. A non-empty `git diff` is a genuine reproducibility failure and I want the issue.

Corpus integrity independently confirmed: 91,606 tablets, 6,968,581 cuneiform glyphs, zero duplicate IDs, zero duplicate transliterations, sampling seeded at `random_state=42`.

## What would change my mind

- A demonstration that the boundary-permutation null is also wrong.
- A specialist showing the regex probes systematically over- or under-count (I already expect this in places).
- An argument that the compression-Δ result inherits either the §1 or §4 problem.
- Evidence that the agent-design mapping is post-hoc rationalization — that the primitives came from modern practice and were retrofitted onto tablets. I believe templates were mined first and mapped second, and the pipeline ordering supports that, but I cannot prove my own process to you.

## What I am asking for

Blunt assessment of whether the claim/evidence table is honest, and whether anything here is worth writing up formally. "This is a nicely packaged blog post, not a paper" is a useful answer and will not offend me.
