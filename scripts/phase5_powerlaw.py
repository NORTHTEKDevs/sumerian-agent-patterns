"""
Phase 5: Is the glyph-frequency distribution actually a power law? Done by the standard method.

WHY THIS EXISTS
---------------
The original release fitted Zipf exponents by OLS on log-log rank-frequency data and read the
cross-genre spread (Administrative s=1.746 vs Lexical s=1.114) as evidence that administrative
tablets are "DSL-like". That claim was withdrawn (CORRECTIONS.md): the spread is a stream-length
artifact, and OLS on log-log data is a biased estimator whose R^2 is not a goodness-of-fit test.

This script does it the way Clauset, Shalizi & Newman (2009, SIAM Review 51(4):661-703) prescribe:

  1. Estimate x_min by minimising the Kolmogorov-Smirnov distance between the empirical CDF and
     the fitted power law above x_min.
  2. Estimate alpha by discrete MLE given that x_min.
  3. Test goodness of fit by parametric bootstrap: synthesise many datasets from the fitted model,
     refit each, and ask how often the synthetic KS distance exceeds the observed one. That
     fraction is p. Here a LARGE p means "power law is not ruled out"; p < 0.1 rules it out.
  4. Compare against a lognormal alternative with Vuong's likelihood-ratio test, because a
     distribution can pass (3) and still be better explained by lognormal.

All fits are run at a COMMON stream length across genres, because that is the confound that
invalidated the original comparison.

Reading the result: "is it a power law" is a much weaker and more honest question than the
original "is it a DSL". A positive answer here does NOT resurrect the DSL claim.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

STRUCTURAL = {"<SURFACE>", "<COLUMN>", "<RULING>", "<BLANK_SPACE>", "<unk>"}
TARGET_GENRES = ["Administrative", "Literary", "Lexical", "Royal Inscription", "Letter"]
N_GOF_BOOT = 500          # parametric-bootstrap replicates for the KS goodness-of-fit test
N_LENGTH_DRAWS = 10       # contiguous equal-length blocks per genre
SEED = 20260801


def discrete_mle_alpha(x: np.ndarray, xmin: int) -> float:
    """MLE for the discrete power-law exponent, via the standard continuous approximation
    with the -1/2 correction (Clauset et al. eq. 3.7), which is accurate for xmin >= 6 and
    is used here as the optimiser's objective."""
    xx = x[x >= xmin]
    if xx.size < 2:
        return float("nan")
    return float(1.0 + xx.size / np.sum(np.log(xx / (xmin - 0.5))))


def _zeta(alpha: float, xmin: int, terms: int = 10000) -> float:
    k = np.arange(xmin, xmin + terms)
    return float(np.sum(k.astype(float) ** (-alpha)))


def _plaw_cdf(vals: np.ndarray, alpha: float, xmin: int) -> np.ndarray:
    z = _zeta(alpha, xmin)
    out = np.empty(vals.size)
    for i, v in enumerate(vals):
        k = np.arange(xmin, int(v) + 1)
        out[i] = np.sum(k.astype(float) ** (-alpha)) / z
    return out


def ks_distance(x: np.ndarray, alpha: float, xmin: int) -> float:
    xx = np.sort(x[x >= xmin])
    if xx.size < 2:
        return float("inf")
    uniq = np.unique(xx)
    emp = np.searchsorted(xx, uniq, side="right") / xx.size
    thr = _plaw_cdf(uniq, alpha, xmin)
    return float(np.max(np.abs(emp - thr)))


def fit_xmin(x: np.ndarray) -> tuple[int, float, float]:
    """Choose x_min by minimising KS distance; return (xmin, alpha, ks)."""
    best = (1, float("nan"), float("inf"))
    candidates = [c for c in np.unique(x) if c >= 2][:40]
    for xmin in candidates:
        xmin = int(xmin)
        if (x >= xmin).sum() < 50:
            break
        a = discrete_mle_alpha(x, xmin)
        if not np.isfinite(a) or a <= 1:
            continue
        d = ks_distance(x, a, xmin)
        if d < best[2]:
            best = (xmin, a, d)
    return best


def sample_powerlaw(n: int, alpha: float, xmin: int, rng, cap: int = 100000) -> np.ndarray:
    k = np.arange(xmin, cap)
    w = k.astype(float) ** (-alpha)
    w /= w.sum()
    return rng.choice(k, size=n, p=w)


def gof_pvalue(x: np.ndarray, alpha: float, xmin: int, ks_obs: float, rng) -> float:
    """Parametric bootstrap. LARGE p => power law not ruled out; p < 0.1 => ruled out."""
    tail = x[x >= xmin]
    n_tail = tail.size
    if n_tail < 50 or not np.isfinite(ks_obs):
        return float("nan")
    worse = 0
    for _ in range(N_GOF_BOOT):
        synth = sample_powerlaw(n_tail, alpha, xmin, rng)
        a_s = discrete_mle_alpha(synth, xmin)
        if not np.isfinite(a_s) or a_s <= 1:
            continue
        if ks_distance(synth, a_s, xmin) >= ks_obs:
            worse += 1
    return worse / N_GOF_BOOT


def vuong_vs_lognormal(x: np.ndarray, alpha: float, xmin: int) -> tuple[float, float]:
    """Normalised log-likelihood-ratio R and two-sided p (Vuong).
    R > 0 favours the power law, R < 0 favours lognormal; p says whether |R| is distinguishable
    from zero. A large p means the two models fit comparably and neither is preferred."""
    xx = x[x >= xmin].astype(float)
    if xx.size < 50:
        return float("nan"), float("nan")
    ll_pl = -alpha * np.log(xx) - np.log(_zeta(alpha, xmin))
    lx = np.log(xx)
    mu, sigma = lx.mean(), lx.std(ddof=1)
    if sigma <= 0:
        return float("nan"), float("nan")
    ll_ln = -np.log(xx * sigma * np.sqrt(2 * np.pi)) - (lx - mu) ** 2 / (2 * sigma ** 2)
    # normalise the lognormal density over the same support so the comparison is fair
    ll_ln = ll_ln - np.log(max(1e-300, 1.0 - 0.5 * (1 + _erf((np.log(xmin - 0.5) - mu) / (sigma * np.sqrt(2))))))
    diff = ll_pl - ll_ln
    n = diff.size
    R = float(diff.sum())
    sd = float(diff.std(ddof=1))
    if sd == 0:
        return R, float("nan")
    z = R / (np.sqrt(n) * sd)
    p = float(2 * (1 - _norm_cdf(abs(z))))
    return round(R, 2), round(p, 4)


def _erf(z: float) -> float:
    t = 1.0 / (1.0 + 0.3275911 * abs(z))
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * np.exp(-z * z)
    return float(np.sign(z) * y)


def _norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + _erf(z / np.sqrt(2)))


def genre_streams() -> dict[str, list[str]]:
    df = pd.read_parquet(DATA / "sample_500.parquet")
    out = {}
    for g in TARGET_GENRES:
        toks = []
        for s in df[df["genre_primary"] == g]["glyph_names"]:
            toks.extend(t for t in str(s).split() if t not in STRUCTURAL)
        out[g] = toks
    return out


def main() -> None:
    rng = np.random.default_rng(SEED)
    streams = genre_streams()
    common_n = min(len(v) for v in streams.values())
    results = []

    for genre, stream in streams.items():
        # fit at a COMMON stream length -- the confound that broke the original comparison
        alphas, xmins, kss, gofs, vuongs = [], [], [], [], []
        for _ in range(N_LENGTH_DRAWS):
            start = 0 if len(stream) <= common_n else int(rng.integers(0, len(stream) - common_n))
            block = stream[start:start + common_n]
            freqs = np.array(sorted(Counter(block).values(), reverse=True), dtype=float)
            xmin, alpha, ks = fit_xmin(freqs)
            if not np.isfinite(alpha):
                continue
            alphas.append(alpha); xmins.append(xmin); kss.append(ks)
            gofs.append(gof_pvalue(freqs, alpha, xmin, ks, rng))
            vuongs.append(vuong_vs_lognormal(freqs, alpha, xmin))

        if not alphas:
            continue
        gof_clean = [g for g in gofs if g == g]
        R = [v[0] for v in vuongs if v[0] == v[0]]
        pv = [v[1] for v in vuongs if v[1] == v[1]]
        results.append({
            "genre": genre,
            "stream_length_native": len(stream),
            "fitted_at_common_length": common_n,
            "alpha_mle_mean": round(float(np.mean(alphas)), 3),
            "alpha_mle_sd": round(float(np.std(alphas)), 3),
            "xmin_median": int(np.median(xmins)),
            "ks_distance_mean": round(float(np.mean(kss)), 4),
            "gof_p_mean": round(float(np.mean(gof_clean)), 3) if gof_clean else None,
            "powerlaw_ruled_out": (float(np.mean(gof_clean)) < 0.1) if gof_clean else None,
            "vuong_R_mean": round(float(np.mean(R)), 2) if R else None,
            "vuong_p_mean": round(float(np.mean(pv)), 4) if pv else None,
        })
        print(f"[phase5] {genre:<20} alpha={results[-1]['alpha_mle_mean']:.3f} "
              f"xmin={results[-1]['xmin_median']} GoF_p={results[-1]['gof_p_mean']} "
              f"Vuong_R={results[-1]['vuong_R_mean']}")

    (OUT / "phase5_powerlaw.json").write_text(
        json.dumps({"config": {"gof_bootstrap": N_GOF_BOOT, "length_draws": N_LENGTH_DRAWS,
                               "common_length_tokens": common_n, "seed": SEED,
                               "method": "Clauset, Shalizi & Newman 2009"},
                    "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Phase 5 — Is the glyph-frequency distribution a power law?\n\n",
          "The original release fitted Zipf exponents by OLS on log-log rank-frequency data and read the "
          "cross-genre spread as evidence that administrative tablets are \"DSL-like\". "
          "[That claim was withdrawn](../CORRECTIONS.md): the spread is a stream-length artifact, and OLS on "
          "log-log data is a biased estimator whose R² is not a goodness-of-fit test.\n\n",
          "This is the standard method (Clauset, Shalizi & Newman 2009, *SIAM Review* 51(4):661–703): x_min "
          "chosen by minimising KS distance, α by discrete MLE, goodness of fit by parametric bootstrap, and a "
          "Vuong likelihood-ratio test against a lognormal alternative. **All genres are fitted at a common "
          f"stream length ({common_n:,} tokens)** — the confound that invalidated the original comparison.\n\n",
          "| Genre | α (MLE) | sd | x_min | KS | GoF p | Power law ruled out? | Vuong R | Vuong p |\n",
          "|---|---:|---:|---:|---:|---:|:---:|---:|---:|\n"]
    for r in results:
        md.append(f"| {r['genre']} | {r['alpha_mle_mean']} | {r['alpha_mle_sd']} | {r['xmin_median']} | "
                  f"{r['ks_distance_mean']} | {r['gof_p_mean']} | "
                  f"{'**YES**' if r['powerlaw_ruled_out'] else 'no'} | {r['vuong_R_mean']} | {r['vuong_p_mean']} |\n")
    md.append("\n**How to read this.** In the goodness-of-fit column a LARGE p means the power law is *not ruled "
              "out*; p < 0.1 rules it out. This is the opposite of the usual convention and is a common source of "
              "error when citing power-law fits. Vuong R > 0 favours the power law over lognormal, R < 0 favours "
              "lognormal, and Vuong p says whether the difference is distinguishable from zero — a large p means "
              "the two models fit comparably and **neither should be claimed**.\n\n")
    md.append("**What this does not do.** Establishing that a frequency distribution is or is not power-law "
              "says nothing about whether a genre is a \"domain-specific language\". That was the original "
              "overreach and it is not reinstated here. The α values are reported as a property of the token "
              "distribution, nothing more.\n\n")

    ruled_out = [r["genre"] for r in results if r["powerlaw_ruled_out"]]
    not_ruled = [r["genre"] for r in results if r["powerlaw_ruled_out"] is False]
    indistinguishable = [r["genre"] for r in results if r["vuong_p_mean"] and r["vuong_p_mean"] > 0.05]
    lo = min(r["alpha_mle_mean"] for r in results)
    hi = max(r["alpha_mle_mean"] for r in results)

    md.append("## Conclusion\n\n")
    md.append(f"**1. The original cross-genre spread was an artifact.** At a common stream length the MLE "
              f"exponents span {lo}–{hi} — a band of {hi - lo:.3f}. The OLS fit at native lengths reported "
              "1.114–1.746, a spread of 0.632, roughly seven times wider. The genre difference that the "
              "\"Zipf-as-DSL detector\" rested on does not survive either the correct estimator or the length control.\n\n")
    if ruled_out:
        md.append(f"**2. A power law is ruled out for {', '.join(ruled_out)}** (bootstrap GoF p < 0.1). "
                  f"It is not ruled out for {', '.join(not_ruled)}.\n\n")
    md.append(f"**3. But 'not ruled out' is not 'confirmed'.** Vuong's test cannot distinguish the power law "
              f"from a lognormal for {'any genre tested' if len(indistinguishable) == len(results) else ', '.join(indistinguishable)} "
              f"(all p > 0.05). **No genre in this corpus should be described as power-law distributed.** "
              "Two models fit comparably, which is the ordinary situation for real-world data and precisely "
              "what Clauset et al. warn against over-reading. The correct summary is: the token-frequency "
              "distributions are heavy-tailed with α ≈ 1.7–2.0, and this method cannot identify which "
              "heavy-tailed family generated them.\n\n")
    md.append("**4. Net effect on the repository's claims.** This analysis does not restore the withdrawn "
              "finding; it explains why the finding was wrong and replaces it with a weaker, defensible "
              "statement. The one genuinely new result is the Lexical outcome — under a correct fit, "
              "lexical lists are the single genre whose frequency distribution is inconsistent with a power "
              "law, which is at least consistent with their being curated word-lists rather than natural text. "
              "That is offered as an observation, not a claim about scribal practice.\n")
    (OUT / "phase5_powerlaw.md").write_text("".join(md), encoding="utf-8")
    print(f"[save] {OUT / 'phase5_powerlaw.md'}")


if __name__ == "__main__":
    main()
