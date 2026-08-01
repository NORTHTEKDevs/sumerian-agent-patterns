# Phase 4 — Does `<RULING>` mark content boundaries? Full-corpus test

The original release claimed it does (Royal p=0.002, Administrative p=0.005). That claim was withdrawn because its null shuffled every token in the tablet, destroying the local coherence any natural-language text has — beating that null shows nothing about `<RULING>` specifically. The corrected test in §4 of `compression_findings.md` returned a null result, but on only 10–17 adjacent chunk pairs per genre, which cannot settle the question either way.

**This is the properly powered test.** Full corpus (91,606 tablets) instead of a 500-per-genre sample, 10,000 permutations, two independent nulls, effect sizes with bootstrap CIs, and Benjamini–Hochberg correction across genres.

## Method

Statistic: mean shared trigrams between adjacent ruling-delimited chunks.

- **Null A — length permute (primary).** Keep real token order and the exact multiset of chunk lengths; permute only their order, moving the cuts. Preserves chunk-size distribution exactly.
- **Null B — uniform cuts (robustness).** Keep real token order; place the same number of cuts uniformly at random with a minimum chunk length. Fully randomises placement.
- **Null C — token shuffle (discredited).** The null behind the withdrawn claim. Reported only for contrast.

A and B fail in different ways, so their agreement is the robustness check. Null A has a known degeneracy: a tablet whose chunk lengths are all equal produces identical cuts under permutation and contributes no variance. The share of such tablets is reported per genre; null B is immune to it.

## Results

| Genre | Tablets | Pairs | Observed (95% CI) | Null A | Δ_A | p_A (2-sided, BH) | Null B | Δ_B | p_B upper/lower | Null C (discredited) |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|
| Administrative | 1,716 | 2,095 | 1.1881 [0.9747, 1.4258] | 1.5165 | -0.3284 | **0.0006** | 2.8492 | -1.6611 | 1.0 / 0.0001 | 0.0345 |
| Literary | 93 | 248 | 1.1694 [0.6089, 1.9839] | 1.4251 | -0.2558 | **0.27777** | 2.3863 | -1.2169 | 1.0 / 0.0001 | 0.0501 |
| Royal Inscription | 16 | 64 | 1.2812 [0.3125, 2.5625] | 1.5235 | -0.2423 | **0.56534** | 2.8555 | -1.5742 | 1.0 / 0.0001 | 0.0197 |

`Δ` is observed minus null mean. Positive means adjacent ruling-delimited chunks share MORE trigrams than the same text cut elsewhere — i.e. RULING boundaries fall at points of higher local similarity, not lower.

### Degeneracy diagnostic (null A)

| Genre | Tablets with all-equal chunk lengths | Share |
|---|---:|---:|
| Administrative | 20 | 1.2% |
| Literary | 2 | 2.2% |
| Royal Inscription | 0 | 0.0% |

Those tablets cannot move under null A, which biases null A toward the observed value and makes it **conservative** — it understates any real effect. Null B is unaffected, which is why both are reported.

## How to read this

Compare the Null C column to Null A and Null B. The discredited null sits far below both legitimate ones, which is precisely why the original claim looked overwhelming: it was measured against a baseline that no real text could fail to beat.

## Conclusion

**The effect is real, and it runs in the OPPOSITE direction to the withdrawn claim.**

Every genre tested shows a negative Δ under the primary null (Administrative -0.3284, Literary -0.2558, Royal Inscription -0.2423), and the direction is confirmed by the independent null B in all cases. Adjacent ruling-delimited chunks share **fewer** trigrams than the same text cut elsewhere with the same chunk-length profile.

Only **Administrative** has the statistical power to establish it: 2,095 adjacent pairs, Δ = -0.3284, BH-adjusted two-sided p = 0.0006. Literary (248 pairs) and Royal Inscription (64 pairs) show the same direction and a similar effect size but do not reach significance — consistent with an underpowered test of a real effect rather than with absence of one.

**What this means.** The original release claimed `<RULING>`-bounded chunks share *more* material than baseline, and read that as evidence for a logical row boundary. That claim was withdrawn because its null was invalid. The properly powered test finds a significant effect in the reverse direction — which is *also* consistent with `<RULING>` being a genuine content boundary, by the opposite mechanism: an arbitrary cut tends to fall **within** a record, leaving material from the same record on both sides, whereas a real ruling falls **between** records.

**This does not reinstate the original claim.** The direction, the mechanism, and the reasoning are all different, and the original analysis remains withdrawn. What is new is an independent, adequately powered result that happens to support the same design intuition the withdrawn claim was reaching for.

### Threats to validity

- **Mechanism is not established.** This test shows *that* aligned cuts lower cross-boundary trigram overlap; it does not demonstrate *why*. The record-boundary explanation above is a hypothesis consistent with the data, not a result. A direct test would need record-level annotation the corpus does not carry.
- **Effect size is modest.** Δ = −0.33 shared trigrams per adjacent pair against an observed mean of 1.19 — roughly a 22% reduction. It is statistically robust, not large.
- **Null B overstates the magnitude.** It produces more uniform chunk lengths than reality, and shared-trigram counts grow with chunk size, so part of Δ_B is a size effect rather than placement. Null A preserves the length multiset exactly and is the one to cite. They are reported together because they agree on direction while differing on magnitude, which is the informative pattern.
- **Genre coverage is thin.** Only Administrative is well-powered, and the corpus is 92%+ administrative, so this is substantially a finding about Ur III administrative practice rather than about Sumerian scribal convention generally.
- **`<RULING>` is a transcription artifact as much as a physical one.** It reflects modern editorial judgement about where a scribe drew a line, mediated by the corpus's transliteration conventions. Systematic editorial bias in placing those marks would be indistinguishable from the effect measured here.
- **Not peer-reviewed, and not adjudicated by an Assyriologist.**
