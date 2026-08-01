# Notes for Reviewers

Thank you for looking at this. This document points you straight at the weakest parts rather than making you find them. If you only have an hour, work top to bottom and stop whenever you like — the list is ordered by where a serious problem is most likely to remain.

## What this repo is, stated plainly

A reproducible pipeline that mines a cuneiform corpus for recurring bureaucratic patterns, plus an argument that those patterns map usefully onto multi-agent software design, plus one engineering benchmark.

It is **not** an Assyriology contribution. The corpus observations are, as far as I know, unsurprising to a specialist — Sumerian administrative practice as a proto-information-system is well-trodden ground in the field and in popular essays. The intended contribution is the *pipeline* and the *mapping*, and the honest framing of how much each claim can bear.

The claim-by-claim evidence table is in the README under **Claims and Evidence Strength**. Please attack that table first: if a claim is graded too generously, that is the most damaging error the repo can have.

## Where I would attack it first

1. **The withdrawn RULING-parity claim** ([CORRECTIONS.md](CORRECTIONS.md)). A self-audit found the original positive result was an artifact of a null hypothesis that shuffled all tokens, destroying the local structure any natural text has. Under a null that permutes only boundary placement, the effect vanishes. **Please check that the replacement null is itself correct** — it holds real token order and the exact multiset of chunk lengths fixed and permutes only where cuts fall (`ruling_parity` in `scripts/phase3_compression.py`). If that control is also flawed, I want to know before this goes anywhere.

2. **Whether the same error class survives elsewhere.** The compression-Δ statistic (§2) uses the *same* token-shuffle baseline that broke §4. I argue it is legitimate there because the claim is only "more structured than random token order" rather than a claim about any specific structural feature. That argument deserves scrutiny — it is the most likely place a second instance of the same mistake is hiding.

3. **ELS statistical power** (§3). At 1,000 permutations the minimum attainable p is ~0.001, roughly 10× the Bonferroni threshold of 0.000101. The scan therefore cannot return a Bonferroni-significant result by construction. The original "0 of 495 Bonferroni-significant" framing overstated this; it now reports 3 nominal hits against ~5 expected by chance. Is that reframing sufficient, or should the permutation count simply be raised to ~10,000?

4. **Sample size and selection.** 500 tablets per genre from a corpus that is 92%+ administrative, so several genres are near-exhaustively sampled (Lexical n=69, all of them) while Administrative is sampled at well under 1%. The RULING analysis rests on 10–17 adjacent-chunk pairs in some genres. Are the per-genre comparisons meaningful at all given this imbalance?

5. **Multiple comparisons across the whole repo.** Bonferroni is applied within the ELS scan (495 tests). It is *not* applied across the full set of hypotheses the repo entertains — probes, Zipf fits, compression deltas, parity. With enough probes something will look interesting. I do not have a principled correction for this and would welcome a recommendation.

6. **Regex probe validity.** Every frequency in Phase 1 depends on hand-written regexes over transliterated text (`PROBES` in `scripts/phase1_templates.py`). Transliteration conventions vary, sign readings are contested, and a probe like `\bmu\b` for year-formulae will catch unrelated uses of `mu`. **I have not validated these against a specialist's judgment.** The 25.4% and 74.2% figures are the most-cited numbers in the repo and rest entirely on this. If you have Assyriological background, this is where your time is worth the most.

7. **The mapping itself.** Does "Sumerian scribes used seals, therefore agent writes should carry signed envelopes" survive as anything more than an analogy? The benchmark shows a sealed log answers audit queries an anonymous one cannot — but that is close to true by definition, since the anonymous log lacks the fields being queried. Is the benchmark demonstrating anything beyond its own construction? I think it demonstrates the *cost* side honestly (+59% bytes, +37 tokens) while the capability side is definitional, and the README now says so. Push on that.

## Reproducing it

Full instructions in the README under **How to Reproduce**. Roughly 8 minutes end to end, no API keys, no GPU:

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/phase0_sample.py
python scripts/phase1_templates.py
python scripts/phase3_compression.py
git diff --stat outputs/     # expected: empty
```

Verified end to end from a clean clone on Python 3.14.2 / numpy 2.5.1 / pandas 3.0.5. `outputs/templates.json` and `outputs/phase3_raw.json` regenerate byte-identical. If `git diff` is not empty on your machine, that is a genuine reproducibility failure and I want the issue.

## What would change my mind

- Any demonstration that the boundary-permutation null is also wrong.
- A specialist showing the regex probes systematically over- or under-count.
- An argument that the compression-Δ statistic inherits the §4 problem.
- Evidence that the agent-design mapping is post-hoc rationalization — that these primitives were arrived at from modern practice and retrofitted onto tablets. I believe the templates were mined first and mapped second, and the pipeline ordering supports that, but I cannot prove my own process to you.

## What I am asking for

Blunt assessment of whether the claim/evidence table is honest, and whether anything here is worth writing up formally. A "this is a nicely packaged blog post, not a paper" verdict is a useful answer and will not offend me.
