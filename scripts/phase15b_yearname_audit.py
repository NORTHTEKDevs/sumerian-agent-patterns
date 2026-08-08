"""
Phase 15b: Precision audit of the STRICT year-name probe -- the audit phase 15's gate demanded.

The strict variant (\\bmu\\s+(?:us2-sa\\s+)?(?!<)\\S) was used in phases 6/8/15 but never itself
audited; only the loose form (34%, DO-NOT-CITE) and the bare lexeme (70.6%) were. The gate named
one unexcluded false-positive class: oath formulae (mu lugal-bi in-pad3, 'swore by the name of
the king'). GRADUATION THRESHOLD, FIXED BEFORE THE RUN: >= 95% precision (the gold-probe
convention) lifts phase 15's provisional flag on year-name results; below it, they stay
provisional or are withdrawn.

Method: phase-1b-style discriminators over every strict-probe match in the Administrative
corpus, buckets fixed a priori. Conservative: FALSE only where the surface form is unambiguous.
  TRUE   -- mu us2-sa ... (derived year-name); mu + royal name/divine determinative + regnal
            event verb (ba-hul destroyed, ba-du3 built, ba-hun installed, ba-dim2 fashioned,
            ba-a-r / mu-...-a year-of patterns); mu + en/ensi2 + ba-hun; mu + GN + ba-hul
  FALSE  -- oath: pad3/in-pad3 within the match window; 'mu lugal' followed by -bi/-be2 + oath
            verb; mu ...-sze3 purpose clause ('for the sake of') where followed by verbal form
  UNCLEAR-- everything else (excluded from precision, reported)
Plus an ePSD2 cross-check on the oath class specifically: among Ur III tablets where the strict
probe fires, how often does the fired line contain pad3 (oath) -- an independent bound on the
oath contamination rate.
"""
from __future__ import annotations

import sys

import json
import re
from pathlib import Path

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

STRICT = re.compile(r"\bmu\s+(?:us₂-sa\s+)?(?!<)([^\n]{0,80})")
THRESHOLD = 0.95

TRUE_PATTERNS = [
    (re.compile(r"^us₂-sa\b"), "mu us₂-sa (derived year-name)"),
    (re.compile(r"ba-hul"), "GN destroyed (year-event)"),
    (re.compile(r"ba-du₃|ba-dim₂|ba-du₈|ba-a-du₃"), "built/fashioned (year-event)"),
    (re.compile(r"ba-hun"), "priest/official installed (year-event)"),
    (re.compile(r"^\{d\}[^\s]+\s+lugal"), "royal name + lugal (regnal year)"),
    (re.compile(r"^en\s.+ba-hun|^en-[^\s]+\s+ba-hun"), "en installed (year-event)"),
    (re.compile(r"si-mu-ru-um|ki-maš|an-ša-an|ur-bi₂-lum|šimurum|ša-aš-ru"), "campaign toponym (year-event)"),
    (re.compile(r"bad₃\s"), "wall built (year-event)"),
    (re.compile(r"^ma₂\s.+ba-ab-du₈"), "boat caulked (year-event)"),
    (re.compile(r"^e₂\s.+ba-du₃"), "temple built (year-event)"),
    (re.compile(r"^ha-ar-ši|^hu-ur₅-ti"), "campaign toponym (year-event)"),
    # -- iteration 2 additions (2026-08-07), from iteration 1's UNCLEAR decode. Tri-criteria
    #    fixed before this run: (a) precision >= 95%, (b) worst-case >= 75%, (c) ePSD2
    #    standalone-'mu' year-share >= 90%. All three or no graduation.
    (re.compile(r"maš₂?-e\s+i₃-pa₃"), "en chosen by omen (year-event)"),
    (re.compile(r"^\{d\}(šu-\{d\}suen|šu\{d\}suen|amar-\{d\}suen|i-bi₂-\{d\}suen|šul-gi|ur-\{d\}namma)"),
     "royal name (year formula, possibly line-split)"),
    (re.compile(r"^en\s+\{d\}"), "en of deity (year-event, possibly line-split)"),
]
FALSE_PATTERNS = [
    (re.compile(r"^\d+\("), "duration count (mu + numeral = 'N years')"),
    (re.compile(r"pad₃|in-pad|ba-pad"), "oath formula (swore by the name)"),
    (re.compile(r"^lugal-bi\b|^lugal-be₂\b"), "oath: by its king"),
    (re.compile(r"-še₃\s+\S+\s*$"), "purpose clause (-še₃)"),
]


def epsd2_standalone_mu():
    """Criterion (c): guide-word distribution of tokens whose form is exactly 'mu' in the ePSD2
    Ur III expert lemmatisation -- the only surface form the strict probe can fire on."""
    import zipfile
    zpath = DATA / "oracc" / "epsd2-admin-ur3.zip"
    if not zpath.exists():
        return None
    zf = zipfile.ZipFile(zpath)
    year = other = 0
    for name in zf.namelist():
        if not (name.endswith(".json") and "corpusjson" in name):
            continue
        try:
            doc = json.loads(zf.read(name))
        except Exception:
            continue
        stack = [doc]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                f = node.get("f")
                if isinstance(f, dict) and f.get("form") == "mu":
                    if str(f.get("gw") or "").lower().startswith("year"):
                        year += 1
                    else:
                        other += 1
                for v in node.values():
                    if isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(node, list):
                stack.extend(v for v in node if isinstance(v, (dict, list)))
    tot = year + other
    return {"n_standalone_mu": tot, "gw_year": year,
            "year_share": round(year / tot, 4) if tot else None}


def main() -> None:
    df = pd.read_parquet(DATA / "sumtablets.parquet", columns=["id", "genre", "transliteration"])
    df["g"] = df["genre"].fillna("").astype(str).str.split(",").str[0].str.strip()
    adm = df[df["g"] == "Administrative"]

    buckets = {"TRUE": {}, "FALSE": {}, "UNCLEAR": {}}
    n_true = n_false = n_unclear = 0
    oath_lines = 0
    fired_tablets = 0

    for raw in adm["transliteration"]:
        text = str(raw)
        fired = False
        for m in STRICT.finditer(text):
            tail = m.group(1).strip()
            if not tail:
                continue
            fired = True
            verdict, label = None, None
            for rx, lab in FALSE_PATTERNS:
                if rx.search(tail):
                    verdict, label = "FALSE", lab
                    break
            if verdict is None:
                for rx, lab in TRUE_PATTERNS:
                    if rx.search(tail):
                        verdict, label = "TRUE", lab
                        break
            if verdict is None:
                verdict, label = "UNCLEAR", tail[:34]
            buckets[verdict][label] = buckets[verdict].get(label, 0) + 1
            if verdict == "TRUE":
                n_true += 1
            elif verdict == "FALSE":
                n_false += 1
            else:
                n_unclear += 1
            if "pad₃" in tail or "in-pad" in tail:
                oath_lines += 1
        if fired:
            fired_tablets += 1

    total = n_true + n_false + n_unclear
    precision = n_true / (n_true + n_false) if (n_true + n_false) else 0.0
    unclear_share = n_unclear / total if total else 0.0
    # worst-case precision: every UNCLEAR counted as FALSE
    worst = n_true / total if total else 0.0
    ep = epsd2_standalone_mu()
    ep_ok = bool(ep and ep["year_share"] is not None and ep["year_share"] >= 0.90)
    graduated = precision >= THRESHOLD and worst >= 0.75 and ep_ok

    payload = {"total_matches": total, "true": n_true, "false": n_false, "unclear": n_unclear,
               "precision_excl_unclear": round(precision, 4),
               "worst_case_all_unclear_false": round(worst, 4),
               "oath_line_matches": oath_lines,
               "oath_share_of_matches": round(oath_lines / total, 4) if total else None,
               "fired_tablets": fired_tablets,
               "threshold": THRESHOLD, "graduated": bool(graduated),
               "epsd2_standalone_mu": ep, "epsd2_criterion_met": ep_ok,
               "top_true": sorted(buckets["TRUE"].items(), key=lambda kv: -kv[1])[:8],
               "top_false": sorted(buckets["FALSE"].items(), key=lambda kv: -kv[1])[:8],
               "top_unclear": sorted(buckets["UNCLEAR"].items(), key=lambda kv: -kv[1])[:15]}
    (OUT / "phase15b_yearname_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    md = ["# Phase 15b — Precision audit of the strict year-name probe\n\n",
          f"Graduation threshold fixed before the run: >= {THRESHOLD:.0%} precision (TRUE vs "
          "TRUE+FALSE, conservative discriminators, FALSE only where unambiguous) lifts phase 15's "
          "provisional flag; the worst-case bound (every UNCLEAR counted FALSE) must also stay "
          "above 75%.\n\n",
          f"Matches audited: **{total:,}** across {fired_tablets:,} administrative tablets.\n\n",
          f"| Verdict | n | share |\n|---|---:|---:|\n",
          f"| TRUE (year-name context) | {n_true:,} | {n_true/total:.1%} |\n",
          f"| FALSE (oath / purpose clause) | {n_false:,} | {n_false/total:.1%} |\n",
          f"| UNCLEAR | {n_unclear:,} | {unclear_share:.1%} |\n\n",
          f"**Precision (excl. UNCLEAR): {precision:.1%}** · worst-case (all UNCLEAR as FALSE): "
          f"{worst:.1%} · oath-class contamination: {oath_lines:,} matches "
          f"({100*oath_lines/total:.2f}% of all matches) — the gate's named false-positive class "
          "is measured, not assumed.\n\n",
          (f"**Independent ePSD2 criterion (c):** standalone `mu` tokens in the expert "
           f"lemmatisation: {ep['n_standalone_mu']:,} total, {ep['gw_year']:,} with guide-word "
           f"'year' = **{100*ep['year_share']:.1f}%** (required >= 90%): "
           f"{'MET' if ep_ok else 'NOT MET'}.\n\n") if ep else "ePSD2 criterion could not run.\n\n",
          f"## Verdict: **{'GRADUATED' if graduated else 'NOT GRADUATED'}** "
          f"(iteration 2; tri-criteria fixed pre-run)\n\n"]
    if graduated:
        md.append("The strict probe meets the gold-probe convention; phase 15's year-name-dependent "
                  "results (year column, S2, S3) lose their probe-contingency flag. The remaining "
                  "phase-15 caveats (surviving record, formula evolution, entropy non-specificity) "
                  "stand unchanged.\n\n")
    else:
        md.append("Phase 15's year-name-dependent results remain provisional. The bucket tables "
                  "below say what the probe is actually matching.\n\n")
    for v in ("TRUE", "FALSE", "UNCLEAR"):
        md.append(f"### Top {v} buckets\n\n| Pattern | n |\n|---|---:|\n")
        for lab, n_ in payload[f"top_{v.lower()}"]:
            md.append(f"| {lab} | {n_:,} |\n")
        md.append("\n")
    md.append("Conservative by construction: FALSE requires an unambiguous oath/purpose surface "
              "form, so the reported precision is not inflated by charitable UNCLEAR handling — "
              "UNCLEAR is excluded from the headline and bounded by the worst-case figure.\n")
    (OUT / "phase15b_yearname_audit.md").write_text("".join(md), encoding="utf-8")
    print(f"[15b] matches={total:,} TRUE={n_true:,} FALSE={n_false:,} UNCLEAR={n_unclear:,}")
    print(f"[15b] precision={precision:.4f} worst={worst:.4f} oath={oath_lines} "
          f"-> {'GRADUATED' if graduated else 'NOT GRADUATED'}")


if __name__ == "__main__":
    main()
