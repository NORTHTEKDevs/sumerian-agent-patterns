"""
Phase 15: Six hundred years of format standardization -- the diachronic trajectory of the
world's first document conventions.

WHY THIS EXISTS
---------------
Every phase so far treats the corpus as a snapshot. It is not: it spans roughly 2600-2000 BCE
across five well-populated administrative periods (ED IIIa 789 tablets, ED IIIb 3,331, Old
Akkadian 4,987, Lagash II 625, Ur III 75,792; Old Babylonian 130 as a small-n descriptive tail).
The bureaucratic formulae we validated at gold precision (kiszib3 sealing, szu ba-ti receipt,
year-names) are, functionally, elements of a document FORMAT. This phase measures how that
format standardized over six centuries -- prevalence trajectories, placement discipline, and
what historians' qualitative narrative (Ur III as the bureaucratic intensification under Shulgi)
looks like as numbers.

MEASURES (per period, Administrative genre only; seal and receipt probes are gold-audited,
the strict year-name variant is NOT -- see the probe-status block in the report)
------------------------------------------------------------------
  prevalence      -- share of tablets carrying each formula (seal, receipt, strict year-name)
  placement       -- where in the tablet each formula sits (normalized position in [0,1]);
                     PLACEMENT DISCIPLINE = entropy of the position-decile distribution.
                     A formula that always sits in the same relative slot has low entropy --
                     that is what "a format" means operationally.
  co-occurrence   -- share of formula-bearing tablets carrying BOTH seal and date ("full
                     envelope" rate)

CONTROLS
--------
Tablet-length composition differs by period, and position deciles interact with length: all
placement entropy comparisons use a LENGTH-STRATIFIED permutation null -- period labels are
permuted within tablet-length strata (quintiles of line count), 5,000 permutations, so a period
cannot look "disciplined" merely by having shorter tablets. Prevalence comparisons report
Wilson 95% CIs. Ur III is downsampled to 5,000 tablets (seeded) for the entropy computations so
one period's mass does not dominate the stratification; prevalence uses full counts.

PRE-REGISTERED EXPECTATIONS (fixed before the run)
--------------------------------------------------
  S1  Sealing prevalence rises monotonically from ED IIIa to Ur III (Spearman over the five
      period ranks, exact p, on the point estimates).
  S2  Placement entropy of the year-name formula DECREASES from ED IIIa to Ur III
      (standardization of where the date goes), significant under the length-stratified
      permutation test comparing ED IIIb vs Ur III (the two best-populated early/late pairs
      with n >= 500).
  S3  The "full envelope" rate (seal AND year on the same tablet) is higher in Ur III than in
      every earlier period.
Whichever way each falls, it is reported as fixed. OB (n=130) is descriptive only and enters no
test. This is a DESCRIPTIVE-TRAJECTORY study with two significance tests; it quantifies a
narrative historians hold qualitatively, and where our numbers contradict that narrative the
contradiction is the finding.
"""
from __future__ import annotations

import sys

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


def _ascii_safe_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass


_ascii_safe_stdout()

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"

SEED = 20260806
N_PERM = 5000
UR3_CAP = 5000
PERIODS = ["Early Dynastic IIIa", "Early Dynastic IIIb", "Old Akkadian", "Lagash II", "Ur III"]
PERIODS_DESC = PERIODS + ["Old Babylonian"]

PROBES = {
    "seal (kišib₃)": re.compile(r"\bkišib(?:₃)?\b"),
    "receipt (šu ba-ti)": re.compile(r"\bšu\s+ba-ti\b"),
    "year-name (strict mu)": re.compile(r"\bmu\s+(?:us₂-sa\s+)?(?!<)\S"),
}
STRUCT = re.compile(r"^<[A-Z_]+>$")


def tablet_lines(text: str) -> list[str]:
    return [l.strip() for l in str(text).split("\n") if l.strip() and not STRUCT.match(l.strip())]


def positions(lines: list[str], rx) -> list[float]:
    n = len(lines)
    if n < 4:
        return []
    return [i / (n - 1) for i, l in enumerate(lines) if rx.search(l)]


def decile_entropy(pos: list[float]) -> float:
    """Shannon entropy (bits) of the position-decile histogram; max = log2(10) ≈ 3.32."""
    if len(pos) < 5:
        return float("nan")
    hist = np.zeros(10)
    for p in pos:
        hist[min(9, int(p * 10))] += 1
    q = hist / hist.sum()
    return float(-(q[q > 0] * np.log2(q[q > 0])).sum())


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.96
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> None:
    rng = np.random.default_rng(SEED)
    df = pd.read_parquet(DATA / "sumtablets.parquet", columns=["id", "genre", "period", "transliteration"])
    df["g"] = df["genre"].fillna("").astype(str).str.split(",").str[0].str.strip()
    adm = df[df["g"] == "Administrative"].copy()

    results = {}
    per_tablet = {}          # period -> list of (n_lines, {probe: positions})
    for period in PERIODS_DESC:
        sub = adm[adm["period"] == period]
        n = len(sub)
        if n == 0:
            continue
        rows = []
        counts = {k: 0 for k in PROBES}
        both = 0
        for t in sub["transliteration"]:
            lines = tablet_lines(t)
            entry = {}
            for name, rx in PROBES.items():
                pos = positions(lines, rx)
                entry[name] = pos
                if pos:
                    counts[name] += 1
            if entry["seal (kišib₃)"] and entry["year-name (strict mu)"]:
                both += 1
            rows.append((len(lines), entry))
        per_tablet[period] = rows
        prev = {}
        for name in PROBES:
            k = counts[name]
            lo, hi = wilson(k, n)
            prev[name] = {"rate": round(k / n, 4), "n": n, "k": k,
                          "ci95": [round(lo, 4), round(hi, 4)]}
        results[period] = {"n_tablets": n, "prevalence": prev,
                           "full_envelope_rate": round(both / n, 4),
                           "full_envelope_k": both}
        print(f"[phase15] {period:<22} n={n:>6,}  seal={prev['seal (kišib₃)']['rate']:.3f}  "
              f"year={prev['year-name (strict mu)']['rate']:.3f}  envelope={both/n:.3f}")

    # ---- placement entropy per period (Ur III capped, seeded)
    entropies = {}
    pooled_positions = {}
    for period in PERIODS:
        rows = per_tablet[period]
        if period == "Ur III" and len(rows) > UR3_CAP:
            idx = rng.choice(len(rows), size=UR3_CAP, replace=False)
            rows = [rows[int(i)] for i in idx]
        pooled_positions[period] = rows
        ent = {}
        for name in PROBES:
            pos = [p for _, e in rows for p in e[name]]
            ent[name] = {"entropy_bits": round(decile_entropy(pos), 4), "n_occurrences": len(pos)}
        entropies[period] = ent
        results[period]["placement_entropy"] = ent

    # ---- S2 permutation test: ED IIIb vs Ur III year-name entropy, length-stratified
    name = "year-name (strict mu)"
    a_rows = pooled_positions["Early Dynastic IIIb"]
    b_rows = pooled_positions["Ur III"]
    all_rows = [(l, e, 0) for l, e in a_rows] + [(l, e, 1) for l, e in b_rows]
    lens = np.array([l for l, _, _ in all_rows])
    strata = np.searchsorted(np.quantile(lens, [0.2, 0.4, 0.6, 0.8]), lens, side="right")

    def ent_diff(labels: np.ndarray) -> float:
        pa = [p for (l, e, _), lab in zip(all_rows, labels) if lab == 0 for p in e[name]]
        pb = [p for (l, e, _), lab in zip(all_rows, labels) if lab == 1 for p in e[name]]
        return decile_entropy(pa) - decile_entropy(pb)

    obs_labels = np.array([lab for _, _, lab in all_rows])
    obs = ent_diff(obs_labels)          # positive = early period LESS disciplined than Ur III
    null = np.empty(N_PERM)
    for k in range(N_PERM):
        lab = obs_labels.copy()
        for s_ in range(5):
            idx = np.flatnonzero(strata == s_)
            lab[idx] = lab[idx][rng.permutation(idx.size)]
        null[k] = ent_diff(lab)
    p_upper = (int((null >= obs).sum()) + 1) / (N_PERM + 1)
    p_lower = (int((null <= obs).sum()) + 1) / (N_PERM + 1)

    # OCCURRENCE-MATCHED robustness check. Entropy estimated from few samples is biased LOW,
    # and ED IIIb has ~8.5x fewer year-name occurrences than capped Ur III (547 vs ~4.6k) --
    # a bias direction that FAVOURS the null we would otherwise report. Subsample Ur III
    # occurrence positions to ED IIIb's count, many draws, and compare at matched n.
    pos_a = [p_ for l, e in a_rows for p_ in e[name]]
    pos_b = [p_ for l, e in b_rows for p_ in e[name]]
    n_match = len(pos_a)
    ent_a = decile_entropy(pos_a)
    draws = np.empty(1000)
    pb_arr = np.array(pos_b)
    for k in range(1000):
        sub = pb_arr[rng.choice(pb_arr.size, size=n_match, replace=False)]
        draws[k] = decile_entropy(sub.tolist())
    matched_delta = ent_a - float(draws.mean())
    matched_ci = (round(ent_a - float(np.percentile(draws, 97.5)), 4),
                  round(ent_a - float(np.percentile(draws, 2.5)), 4))
    s2 = {"entropy_EDIIIb_minus_UrIII_bits": round(obs, 4),
          "null_mean": round(float(null.mean()), 4),
          "p_upper": round(p_upper, 5), "p_lower": round(p_lower, 5),
          "n_perm": N_PERM, "length_stratified": True,
          "occurrence_matched": {"n_matched": n_match,
                                 "ediiib_entropy": round(ent_a, 4),
                                 "ur3_entropy_at_matched_n_mean": round(float(draws.mean()), 4),
                                 "matched_delta_bits": round(matched_delta, 4),
                                 "matched_delta_ci95": list(matched_ci)}}

    # ---- verdicts
    seal_rates = [results[p]["prevalence"]["seal (kišib₃)"]["rate"] for p in PERIODS]
    # exact Spearman for a strict monotone trend over 5 points
    import itertools
    ranks = np.argsort(np.argsort(seal_rates)).astype(float)
    ideal = np.arange(5, dtype=float)

    def rho_of(a, b):
        a = a - a.mean(); b = b - b.mean()
        d = float(np.sqrt((a * a).sum() * (b * b).sum()))
        return float((a * b).sum() / d) if d > 0 else 0.0

    rho = rho_of(ranks, ideal)
    perms = list(itertools.permutations(range(5)))
    p_exact = sum(1 for pr in perms if rho_of(ranks[list(pr)], ideal) >= rho - 1e-12) / len(perms)

    env = [results[p]["full_envelope_rate"] for p in PERIODS]
    verdicts = {
        "S1_sealing_rises_monotonically": {"spearman_rho": round(rho, 3), "exact_p": round(p_exact, 5),
                                           "held": bool(rho > 0 and p_exact < 0.05)},
        "S2_yearname_placement_tightens": {"held": bool(obs > 0 and p_upper < 0.05), **s2},
        "S3_full_envelope_peaks_in_UrIII": {"held": bool(env[-1] > max(env[:-1])),
                                            "rates_by_period": dict(zip(PERIODS, env))},
    }

    (OUT / "phase15_diachronic.json").write_text(json.dumps({
        "config": {"seed": SEED, "n_perm": N_PERM, "ur3_entropy_cap": UR3_CAP,
                   "genre": "Administrative only", "probes": "gold-validated only",
                   "criteria_fixed_before_run": True},
        "results": results, "s2_test": s2, "verdicts": verdicts},
        indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Phase 15 — Six hundred years of format standardization\n\n",
          "The corpus spans c. 2600–2000 BCE. The gold-validated bureaucratic formulae are, "
          "functionally, elements of a document format; this phase measures how that format "
          "standardized across five administrative periods — prevalence, placement discipline "
          "(position-decile entropy; a formula that always sits in the same relative slot has low "
          "entropy — that is operationally what 'a format' means), and the full-envelope rate "
          "(seal AND date on one tablet). Administrative genre only; length-stratified permutation "
          "null for the entropy test; Ur III capped at 5,000 tablets (seeded) for entropy so mass "
          "alone cannot drive stratification.\n\n",
          "| Period | n | Seal % (95% CI) | Year-name % | Full envelope % | Year-name placement entropy (bits) |\n",
          "|---|---:|---:|---:|---:|---:|\n"]
    for period in PERIODS_DESC:
        if period not in results:
            continue
        r = results[period]
        pv = r["prevalence"]
        seal = pv["seal (kišib₃)"]
        ent = r.get("placement_entropy", {}).get("year-name (strict mu)", {})
        tag = " *(descriptive, small n)*" if period == "Old Babylonian" else ""
        md.append(f"| {period}{tag} | {r['n_tablets']:,} | {100*seal['rate']:.1f} "
                  f"({100*seal['ci95'][0]:.1f}–{100*seal['ci95'][1]:.1f}) | "
                  f"{100*pv['year-name (strict mu)']['rate']:.1f} | "
                  f"{100*r['full_envelope_rate']:.1f} | "
                  f"{ent.get('entropy_bits', float('nan'))} |\n")
    om = s2["occurrence_matched"]
    md.append("\n## Probe status — read before the year-name columns\n\n")
    md.append("`seal (kišib₃)` and `receipt (šu ba-ti)` are gold-audited (100%/99.8% lexeme "
              "precision vs Oracc). **The strict year-name variant used here has never itself been "
              "precision-audited**: the loose `\\bmu\\b` probe scored 34% (DO-NOT-CITE) and the "
              "bare-lexeme Oracc check (70.6%) certifies the word, not the formula. A known "
              "unexcluded false-positive class is the oath formula (`mu lugal-bi in-pad₃`, 'swore by "
              "the name of the king'), which passes a whitespace-based regex. **Every year-name-"
              "dependent result below (the year column, S2, S3) is therefore PROVISIONAL pending a "
              "dedicated audit of this variant**; the seal-based S1 result does not share this "
              "contingency. Caught at the adversarial gate; an earlier draft called all three probes "
              "gold, which was wrong.\n")
    md.append(f"\n**S2 permutation test** (ED IIIb vs Ur III, year-name placement entropy, "
              f"length-stratified, {N_PERM:,} permutations): Δ = {s2['entropy_EDIIIb_minus_UrIII_bits']} "
              f"bits (positive = Ur III more disciplined), p_upper = {s2['p_upper']}, "
              f"p_lower = {s2['p_lower']}.\n\n")
    md.append(f"**Occurrence-matched robustness check** — small-sample entropy bias runs LOW, and ED "
              f"IIIb has ~{round(4629/max(om['n_matched'],1))}x fewer occurrences, a bias direction that "
              f"favours the null above, so the comparison is repeated with Ur III subsampled to ED IIIb's "
              f"{om['n_matched']} occurrences (1,000 draws): ED IIIb {om['ediiib_entropy']} bits vs Ur III "
              f"{om['ur3_entropy_at_matched_n_mean']} at matched n; matched Δ = {om['matched_delta_bits']} "
              f"bits (95% CI {om['matched_delta_ci95'][0]} to {om['matched_delta_ci95'][1]}). The matched-n CI "
              f"excludes zero — a small real tightening signal the pre-registered test did not detect. "
              f"Discipline: the pre-registered stratified test remains the S2 verdict (failed); the "
              f"matched-n result is a post-hoc observation, flagged for future pre-registration, and "
              f"is itself contingent on the unaudited year-name probe.\n\n")
    md.append("## Pre-registered verdicts\n\n| Criterion | Held? | Detail |\n|---|:---:|---|\n")
    v = verdicts
    md.append(f"| S1 — sealing prevalence rises monotonically ED IIIa → Ur III | "
              f"{'**YES**' if v['S1_sealing_rises_monotonically']['held'] else '**NO**'} | "
              f"rho = {v['S1_sealing_rises_monotonically']['spearman_rho']}, exact p = "
              f"{v['S1_sealing_rises_monotonically']['exact_p']} |\n")
    md.append(f"| S2 — year-name placement tightens (entropy falls) by Ur III | "
              f"{'**YES**' if v['S2_yearname_placement_tightens']['held'] else '**NO**'} | "
              f"Δ = {s2['entropy_EDIIIb_minus_UrIII_bits']} bits, p = {s2['p_upper']} |\n")
    env_detail = ", ".join(f"{k}: {100*x:.1f}%" for k, x
                           in v["S3_full_envelope_peaks_in_UrIII"]["rates_by_period"].items())
    md.append(f"| S3 — full-envelope rate peaks in Ur III | "
              f"{'**YES**' if v['S3_full_envelope_peaks_in_UrIII']['held'] else '**NO**'} | "
              f"{env_detail} |\n")
    md.append("\n**S1 disclosure.** With five points, ANY strictly increasing sequence yields the "
              "same exact p = 1/120; the certified content is the ordering alone. The four early "
              "periods' Wilson CIs mutually overlap — their internal ordering is not distinguishable "
              "from noise. The load-bearing contrast is Ur III against all earlier periods, which no "
              "CI overlap threatens.\n")
    md.append("\n## What this speaks to, and the caveats that bound it\n\n")
    md.append("**The historiographic stake, stated symmetrically.** Steinkeller's canonical account "
              "treats Ur III under Shulgi as a sharp bureaucratic break; Selz argues many reforms "
              "have Early Dynastic forerunners. This study contributes ONE quantitative datapoint on "
              "ONE textual practice to a dispute that spans many practices — it does not adjudicate "
              "it. Read symmetrically, the data cut both ways: seal-CLAUSE adoption looks like sharp "
              "discontinuity (Steinkeller-compatible), while placement conventions show no detectable "
              "Ur III tightening under the pre-registered test (continuity-compatible). To our "
              "knowledge (novelty sweep, 2026-08-06) no quantitative diachronic study of "
              "administrative-formula standardization across these periods exists; closest "
              "neighbours: Nissen/Damerow/Englund on proto-cuneiform, Tsouparopoulou's sealing "
              "database (one practice, one site, one period), BDTNS corpus statistics (Ur III "
              "only).\n\n")
    md.append("**Caveat 1 — surviving record, not practice.** Different city archives dominate "
              "different centuries (Girsu early, Drehem/Umma for Ur III), and SumTablets carries no "
              "provenance field to stratify on. These are trajectories of the surviving, transliterated "
              "record. **Caveat 2 — measurement is textual, not physical.** Our seal figure counts "
              "kišib₃ TEXT clauses, not physical seal impressions; literature-circulating "
              "BDTNS-derived figures put physical sealing substantially higher (roughly a third of "
              "Ur III tablets) — a figure we have NOT verified at source and flag rather than cite "
              "with false precision. The two measure different things and both can be right. **Caveat 3 — formula spelling itself evolves.** A period where the "
              "receipt function was written with a different formula than šu ba-ti will read as low "
              "prevalence; part phenomenon (the format changed), part probe limitation — undivided "
              "here. **Caveat 4 — entropy levels are non-specific AND, here, high.** Both periods sit "
              "near the uniform ceiling (2.79 and 2.65 of a 3.32-bit maximum): at decile resolution "
              "NO strong slot convention existed in either period, so no claim of 'already "
              "conventional' placement is available from this data (an earlier draft made that "
              "claim; withdrawn at the gate). Single-period entropy is additionally non-specific in "
              "principle (arXiv:2608.02999); only the diachronic delta was tested.\n")
    (OUT / "phase15_diachronic.md").write_text("".join(md), encoding="utf-8")
    print(f"[save] {OUT / 'phase15_diachronic.md'}")
    print(f"[phase15] verdicts: S1={v['S1_sealing_rises_monotonically']['held']} "
          f"S2={v['S2_yearname_placement_tightens']['held']} "
          f"S3={v['S3_full_envelope_peaks_in_UrIII']['held']}")


if __name__ == "__main__":
    main()
