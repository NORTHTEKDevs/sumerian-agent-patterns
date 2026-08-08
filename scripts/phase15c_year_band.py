"""
Phase 15c: Band re-measurement of the phase-15 year-name trajectory.

Phase 15b (two iterations, tri-criteria fixed pre-run) left the strict year-name probe NOT
GRADUATED: precision 85.3% excluding UNCLEAR, with duration counts (`mu N(aš)` = 'N years')
alone contaminating 10.8% of all matches. Phase 15's year-dependent results are therefore
provisional. This phase asks the remaining answerable question: does the SHAPE of the year
trajectory survive the measured contamination?

METHOD. Re-measure per-period prevalence as a BAND, using phase 15b's committed classifier
verbatim (imported, not copied — FALSE checked before TRUE before UNCLEAR, same regexes):
  lower bound  -- share of tablets with >= 1 TRUE match (contamination stripped)
  upper bound  -- share of tablets with >= 1 TRUE-or-UNCLEAR match (maximal inclusion)
  point        -- share with >= 1 match of any class (must equal phase 15's published rate;
                  asserted against outputs/phase15_diachronic.json, a deviation fails the run)
Phase-15 line semantics reproduced exactly: structural markers stripped, tablets with fewer
than 4 lines never fire, matching is per line.

SUPPORT CRITERIA, FIXED HERE BEFORE THE RUN (a trajectory claim "survives the band" only if):
  B1  Ur III jump:   rate(Ur III) > rate(Lagash II) on BOTH bounds; STRONG form additionally
                     requires lower(Ur III) > upper(Lagash II) (band separation).
  B2  Rise into OB:  rate(OB) > rate(Ur III) on BOTH bounds; STRONG form lower(OB) > upper(Ur III).
  B3  Envelope peak: envelope(Ur III) > every earlier period on BOTH bounds (S3's shape).
  B4  Step stability: every adjacent-period step keeps its sign on both bounds.
This is a post-hoc characterization of provisional results, not a graduation: whatever
survives remains probe-contingent until a probe passes its audit. What FAILS the band is
withdrawn as a shape claim.
"""
from __future__ import annotations

import sys

import json
import math
import re
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase15b_yearname_audit import FALSE_PATTERNS, STRICT, TRUE_PATTERNS  # noqa: E402


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

PERIODS = ["Early Dynastic IIIa", "Early Dynastic IIIb", "Old Akkadian", "Lagash II",
           "Ur III", "Old Babylonian"]
SEAL = re.compile(r"\bkišib(?:₃)?\b")
STRUCT = re.compile(r"^<[A-Z_]+>$")


def tablet_lines(text: str) -> list[str]:
    return [l.strip() for l in str(text).split("\n") if l.strip() and not STRUCT.match(l.strip())]


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    z = 1.96
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def classify_tablet(text: str):
    """Return (any_match, any_true, any_true_or_unclear, sealed) under phase-15 semantics."""
    lines = tablet_lines(text)
    sealed = any(SEAL.search(l) for l in lines)
    if len(lines) < 4:                      # phase 15's positions() floor: never fires
        return (False, False, False, sealed)
    any_m = any_t = any_tu = False
    for line in lines:
        for m in STRICT.finditer(line):
            tail = m.group(1).strip()
            if not tail:
                continue
            any_m = True
            verdict = None
            for rx, _ in FALSE_PATTERNS:
                if rx.search(tail):
                    verdict = "FALSE"
                    break
            if verdict is None:
                for rx, _ in TRUE_PATTERNS:
                    if rx.search(tail):
                        verdict = "TRUE"
                        break
            if verdict is None:
                verdict = "UNCLEAR"
            if verdict == "TRUE":
                any_t = any_tu = True
            elif verdict == "UNCLEAR":
                any_tu = True
    return (any_m, any_t, any_tu, sealed)


def main() -> None:
    df = pd.read_parquet(DATA / "sumtablets.parquet",
                         columns=["id", "genre", "period", "transliteration"])
    df["g"] = df["genre"].fillna("").astype(str).str.split(",").str[0].str.strip()
    adm = df[df["g"] == "Administrative"]

    published = json.loads((OUT / "phase15_diachronic.json").read_text(encoding="utf-8"))

    results = {}
    for period in PERIODS:
        sub = adm[adm["period"] == period]
        n = len(sub)
        if n == 0:
            continue
        k_point = k_lo = k_hi = env_point = env_lo = env_hi = 0
        for t in sub["transliteration"]:
            any_m, any_t, any_tu, sealed = classify_tablet(t)
            k_point += any_m
            k_lo += any_t
            k_hi += any_tu
            env_point += any_m and sealed
            env_lo += any_t and sealed
            env_hi += any_tu and sealed
        pub_k = published["results"][period]["prevalence"]["year-name (strict mu)"]["k"]
        if k_point != pub_k:
            print(f"[15c] FATAL: point k {k_point} != published {pub_k} for {period} — "
                  "semantics drifted; fix before any band claim")
            sys.exit(1)
        results[period] = {
            "n": n, "k_point": k_point, "k_lower": k_lo, "k_upper": k_hi,
            "rate_point": round(k_point / n, 4),
            "rate_lower": round(k_lo / n, 4), "rate_upper": round(k_hi / n, 4),
            "ci_lower": [round(x, 4) for x in wilson(k_lo, n)],
            "ci_upper": [round(x, 4) for x in wilson(k_hi, n)],
            "envelope_point": round(env_point / n, 4),
            "envelope_lower": round(env_lo / n, 4), "envelope_upper": round(env_hi / n, 4),
        }
        print(f"[15c] {period:<22} n={n:>6,} point={k_point/n:.3f} "
              f"band=[{k_lo/n:.3f}, {k_hi/n:.3f}] env=[{env_lo/n:.4f}, {env_hi/n:.4f}]")

    # ---- support criteria (fixed in the module docstring before the run)
    r = results
    ur3, lag2, ob = r["Ur III"], r["Lagash II"], r["Old Babylonian"]
    earlier = [p for p in PERIODS[:-2]]     # all periods before Ur III
    b1 = ur3["rate_lower"] > lag2["rate_lower"] and ur3["rate_upper"] > lag2["rate_upper"]
    b1_strong = ur3["rate_lower"] > lag2["rate_upper"]
    b2 = ob["rate_lower"] > ur3["rate_lower"] and ob["rate_upper"] > ur3["rate_upper"]
    b2_strong = ob["rate_lower"] > ur3["rate_upper"]
    b3 = all(ur3["envelope_lower"] > r[p]["envelope_lower"]
             and ur3["envelope_upper"] > r[p]["envelope_upper"] for p in earlier)
    steps = {}
    b4 = True
    for a, b in zip(PERIODS, PERIODS[1:]):
        if a not in r or b not in r:
            continue
        s_lo = r[b]["rate_lower"] - r[a]["rate_lower"]
        s_hi = r[b]["rate_upper"] - r[a]["rate_upper"]
        stable = (s_lo > 0) == (s_hi > 0)
        steps[f"{a} -> {b}"] = {"delta_lower": round(s_lo, 4), "delta_upper": round(s_hi, 4),
                                "sign_stable": bool(stable)}
        b4 = b4 and stable

    verdicts = {
        "B1_ur3_jump_survives": bool(b1), "B1_strong_band_separation": bool(b1_strong),
        "B2_rise_into_OB_survives": bool(b2), "B2_strong_band_separation": bool(b2_strong),
        "B3_envelope_peak_survives": bool(b3),
        "B4_all_steps_sign_stable": bool(b4),
    }
    payload = {"config": {"classifier": "phase15b iteration-2, imported verbatim",
                          "semantics": "phase15 line-level, <4-line floor reproduced",
                          "criteria": "B1-B4 fixed in module docstring before the run"},
               "results": results, "adjacent_steps": steps, "verdicts": verdicts}

    md = ["# Phase 15c — Band re-measurement of the year-name trajectory\n\n",
          "Phase 15b left the strict year-name probe NOT GRADUATED (85.3% precision excluding "
          "41% UNCLEAR; duration counts alone = 10.8% of matches), so every phase-15 "
          "year-dependent number is provisional. This phase re-measures the trajectory as a "
          "band — **lower bound: tablets with ≥1 TRUE match; upper bound: ≥1 TRUE-or-UNCLEAR "
          "match** — using 15b's classifier verbatim, under phase 15's exact line semantics "
          "(point rates asserted equal to the published ones at run time). Support criteria "
          "B1–B4 were fixed in the script header before the run. This characterizes "
          "provisional results; it graduates nothing.\n\n",
          "| Period | n | Published (point) | Lower (TRUE-only) | Upper (+UNCLEAR) | "
          "Envelope band |\n|---|---:|---:|---:|---:|---|\n"]
    for p in PERIODS:
        if p not in r:
            continue
        e = r[p]
        md.append(f"| {p} | {e['n']:,} | {100*e['rate_point']:.1f}% | "
                  f"{100*e['rate_lower']:.1f}% | {100*e['rate_upper']:.1f}% | "
                  f"[{100*e['envelope_lower']:.2f}%, {100*e['envelope_upper']:.2f}%] |\n")
    md += ["\n## Verdicts against the pre-stated criteria\n\n",
           f"- **B1 — the Ur III jump survives the band: "
           f"{'YES' if verdicts['B1_ur3_jump_survives'] else 'NO'}**"
           f" (strong band separation, lower(Ur III) > upper(Lagash II): "
           f"{'YES' if verdicts['B1_strong_band_separation'] else 'NO'} — "
           f"{100*ur3['rate_lower']:.1f}% vs {100*lag2['rate_upper']:.1f}%).\n",
           f"- **B2 — the rise into Old Babylonian survives: "
           f"{'YES' if verdicts['B2_rise_into_OB_survives'] else 'NO'}**"
           f" (strong: {'YES' if verdicts['B2_strong_band_separation'] else 'NO'} — "
           f"lower(OB) {100*ob['rate_lower']:.1f}% vs upper(Ur III) "
           f"{100*ur3['rate_upper']:.1f}%). Old Babylonian is descriptive (n=130).\n",
           f"- **B3 — the envelope peak in Ur III survives: "
           f"{'YES' if verdicts['B3_envelope_peak_survives'] else 'NO'}** "
           f"(Ur III envelope band [{100*ur3['envelope_lower']:.2f}%, "
           f"{100*ur3['envelope_upper']:.2f}%] vs every earlier period).\n",
           f"- **B4 — all adjacent steps sign-stable across the band: "
           f"{'YES' if verdicts['B4_all_steps_sign_stable'] else 'NO'}.**\n\n",
           "| Step | Δ lower | Δ upper | sign stable |\n|---|---:|---:|---|\n"]
    for k, v in steps.items():
        md.append(f"| {k} | {100*v['delta_lower']:+.1f}pp | {100*v['delta_upper']:+.1f}pp | "
                  f"{'yes' if v['sign_stable'] else 'NO'} |\n")
    md.append(
        "\n## The period-coverage confound, and why B1 survives it while B2 does not\n\n"
        "15b's TRUE patterns are built from Ur III-era year-name formulae (the royal names "
        "are the Ur III dynasty's; the event verbs are its year-name conventions). The LOWER "
        "bound is therefore a floor, not an estimate, in every non-Ur III period — early and "
        "Old Babylonian year formulae that a specialist would call TRUE land in UNCLEAR. "
        "This cuts differently per verdict:\n\n"
        "- **B1 is conservative despite the confound.** Its strong form compares Ur III's "
        "LOWER bound (understates Ur III) against Lagash II's UPPER bound (overstates "
        "Lagash II — UNCLEAR needs no TRUE-pattern coverage). Both biases run AGAINST the "
        f"jump, and it still holds: {100*ur3['rate_lower']:.1f}% vs "
        f"{100*lag2['rate_upper']:.1f}%. The jump is real under any resolution of UNCLEAR.\n"
        "- **B2 is unadjudicable, not refuted.** The band direction flips across bounds "
        f"(lower: OB {100*ob['rate_lower']:.1f}% < Ur III {100*ur3['rate_lower']:.1f}%; "
        f"upper: {100*ob['rate_upper']:.1f}% > {100*ur3['rate_upper']:.1f}%), and the lower "
        "bound is exactly where the OB coverage gap bites. The rise-into-OB reading stays "
        "descriptive and provisional (n=130); it is not withdrawn as false, it is withdrawn "
        "as a band-supported claim.\n"
        "- B4's only unstable step is Ur III → Old Babylonian, the same confound.\n\n"
        "Whatever survives here remains PROBE-CONTINGENT (the probe itself failed its "
        "audit); what fails here is not asserted as a shape claim. The seal-based results "
        "(S1, the 19x sealing jump) are untouched — they rest on gold-audited probes.\n")

    (OUT / "phase15c_year_band.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "phase15c_year_band.md").write_text("".join(md), encoding="utf-8")
    print(f"[15c] verdicts: {verdicts}")
    print(f"[save] {OUT / 'phase15c_year_band.md'}")


if __name__ == "__main__":
    main()
