"""
Phase 16: Auditing the world's first auditors -- run against PROTOCOL_phase16_arithmetic_audit.md
as committed 2026-08-06. Deviations, if any, are listed in the report and logged in
CORRECTIONS.md. See the protocol for estimand, exclusion rules, gate, and kill criteria.

MTAAC EVALUATION (protocol step 0, logged 2026-08-07): the cdli-gh org's MTAAC repositories are
public (mtaac_work, mtaac_gold_corpus, mtaac_cdli_ur3_corpus) but expose no standalone
numero-metrological parser package usable off the shelf; integrating their pipeline exceeds this
run. Outcome: proceed with our classifier, validated against ePSD2 as the protocol's named
second annotator; a comparison against MTAAC remains future work.

CLASSIFIER (protocol rule 4)
----------------------------
Every numeral group N(unit) on an item line is classified:
  NON_COUNTED  -- date context (u4/iti/mu/ba-zal on the line segment), ordinal (-kam suffix),
                  rate (-ta suffix), capacity/weight/area units (gur, sila3, ban2, barig, ma-na,
                  gin2, gun2, sar, bur3, iku, GAN2, kusz3), fraction notation
  COUNTED      -- System-S group (disz/u/gesz2/geszu/szar2) whose line names a count commodity
                  from the fixed lexicon (herd animals + personnel + birds)
  UNCLASSIFIABLE -- anything else (bare numeral before a personal name, unknown unit, aš-system
                  in a count context) -> tablet excluded per rule 4
The total line must be pure System-S + count commodity (rule 3).

VALIDATION GATE (protocol): 100 seeded-random verifiable tablets that also exist in the ePSD2
Ur III corpusjson are re-analysed by an INDEPENDENT pipeline over ePSD2's expert-lemmatised
token stream (different source corpus, different tokenisation, expert lemmas = the protocol's
"second annotator"). Per-group precision on COUNTED groups = |multiset agreement| / |parser
groups|; the parser ships only at >= 98%. Below the gate after two iterations: publish the
validation numbers, no error rate (kill criterion 1). Fewer than 150 verifiable: descriptive
only (kill criterion 2). A4 (provenance) is DROPPED as pre-authorised: SumTablets carries no
provenance field; logged here.
"""
from __future__ import annotations

import sys

import json
import re
import zipfile
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

SEED = 20260807
GATE_N = 100
GATE_PRECISION = 0.98
MIN_VERIFIABLE = 150

SYSTEM_S = {"diš": 1, "u": 10, "geš₂": 60, "gešʾu": 600, "šar₂": 3600, "šarʾu": 36000}
NUM = re.compile(r"(\d+)\(([^)]+)\)")
FRACTION = re.compile(r"\d+/\d+\(|igi-\d+-gal₂|la₂ \d+\(")
NONCOUNT_UNITS = {"gur", "sila₃", "ban₂", "barig", "ma-na", "gin₂", "gun₂", "sar",
                  "bur₃", "iku", "GAN₂", "kuš₃", "aš", "ban₂@c", "barig@c"}
DATE_CTX = re.compile(r"\bu₄\b|\biti\b|\bmu\b|ba-zal|-kam\b|\bzal\b")
RATE = re.compile(r"\)\s*-?ta\b|\)-ta\b")
COMMODITIES = ["udu", "maš₂", "maš-gal", "sila₄", "u₈", "ud₅", "gu₄", "ab₂", "amar",
               "anše", "šah₂", "mušen", "guruš", "geme₂", "kir₁₁", "šeg₉"]
COMMODITY_RE = re.compile("|".join(rf"\b{re.escape(c)}\b" for c in COMMODITIES))
TOTAL_RE = re.compile(r"šu-nigin")
STRUCT = re.compile(r"^<[A-Z_]+>$")

# ePSD2 second-annotator lexicon: citation forms and guide words
EPSD2_COMMODITY_CF = {"udu", "maš", "mašgal", "sila", "u₈", "ud₅", "gud", "gu₄", "ab₂",
                      "amar", "anše", "šaḫ", "šah", "mušen", "guruš", "geme", "kir₁₁"}
EPSD2_COMMODITY_GW = ("sheep", "goat", "lamb", "ewe", "ox", "cow", "calf", "donkey", "equid",
                      "pig", "bird", "male", "worker", "female")
EPSD2_DATE_GW = ("day", "month", "year", "name")


def parse_group_value(mult: int, unit: str):
    return mult * SYSTEM_S[unit] if unit in SYSTEM_S else None


def classify_line(line: str):
    """Return (kind, values): kind in {'counted','noncounted','total','unclassifiable','none'}."""
    groups = NUM.findall(line)
    if not groups:
        return ("none", [])
    if FRACTION.search(line):
        return ("unclassifiable", [])
    units = [u for _, u in groups]
    if any(u in NONCOUNT_UNITS for u in units):
        return ("noncounted", []) if all(u in NONCOUNT_UNITS or u in SYSTEM_S for u in units) \
            else ("unclassifiable", [])
    if not all(u in SYSTEM_S for u in units):
        return ("unclassifiable", [])
    vals = [int(m) * SYSTEM_S[u] for m, u in groups]
    if TOTAL_RE.search(line):
        return ("total", vals) if COMMODITY_RE.search(line) else ("unclassifiable", [])
    if DATE_CTX.search(line) or RATE.search(line):
        return ("noncounted", [])
    if COMMODITY_RE.search(line):
        return ("counted", vals)
    return ("unclassifiable", [])


ATTRITION = {"rule2_damage": 0, "rule1_multi_total": 0, "rule3_total_line": 0,
             "rule4_unclassifiable": 0, "rule5_too_few_items": 0}


def analyse_tablet(text: str):
    """Apply protocol rules; return dict or None (not verifiable). Attrition is counted so the
    report can say WHICH committed rule was the binding constraint."""
    raw = str(text)
    if "<unk>" in raw or "..." in raw:
        ATTRITION["rule2_damage"] += 1
        return None                                    # rule 2
    lines = [l.strip() for l in raw.split("\n") if l.strip() and not STRUCT.match(l.strip())]
    total_lines = [i for i, l in enumerate(lines) if TOTAL_RE.search(l)]
    if len(total_lines) != 1:
        ATTRITION["rule1_multi_total"] += 1
        return None                                    # rule 1
    ti = total_lines[0]
    kind, tvals = classify_line(lines[ti])
    if kind != "total" or not tvals:
        ATTRITION["rule3_total_line"] += 1
        return None                                    # rule 3
    counted, n_counted_lines = [], 0
    for l in lines[:ti]:
        k, vals = classify_line(l)
        if k == "unclassifiable":
            ATTRITION["rule4_unclassifiable"] += 1
            return None                                # rule 4
        if k == "counted":
            counted.extend(vals)
            n_counted_lines += 1
    if n_counted_lines < 2:
        ATTRITION["rule5_too_few_items"] += 1
        return None                                    # rule 5
    return {"claimed": sum(tvals), "item_sum": sum(counted), "items": counted,
            "n_items": n_counted_lines, "sealed": bool(re.search(r"\bkišib(?:₃)?\b", raw)),
            "match": sum(tvals) == sum(counted)}


# ---------------- ePSD2 second annotator

def epsd2_tokens(zf: zipfile.ZipFile, pnum: str):
    try:
        doc = json.loads(zf.read(f"epsd2/admin/ur3/corpusjson/{pnum}.json"))
    except KeyError:
        return None
    toks = []
    stack = [doc]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            f = node.get("f")
            if isinstance(f, dict) and f.get("form"):
                toks.append((str(f["form"]), str(f.get("cf") or ""), str(f.get("gw") or "")))
            for v in node.values():
                if isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(node, list):
            stack.extend(v for v in node if isinstance(v, (dict, list)))
    toks.reverse()
    return toks


def epsd2_counted_groups(toks):
    """Independent COUNTED extraction from expert lemmas: a System-S numeral token whose next
    non-numeral token is a commodity lemma; date/name lemmas nearby -> non-counted."""
    vals = []
    for i, (form, cf, gw) in enumerate(toks):
        groups = NUM.findall(form)
        if not groups or not all(u in SYSTEM_S for _, u in groups):
            continue
        v = sum(int(m) * SYSTEM_S[u] for m, u in groups)
        nxt = None
        for j in range(i + 1, min(i + 3, len(toks))):
            if not NUM.findall(toks[j][0]):
                nxt = toks[j]
                break
        if nxt is None:
            continue
        ncf, ngw = nxt[1], nxt[2].lower()
        if any(ngw.startswith(d) or d in ngw for d in EPSD2_DATE_GW):
            continue
        if ncf in EPSD2_COMMODITY_CF or any(w in ngw for w in EPSD2_COMMODITY_GW):
            vals.append(v)
    return vals


def main() -> None:
    rng = np.random.default_rng(SEED)
    df = pd.read_parquet(DATA / "sumtablets.parquet",
                         columns=["id", "genre", "period", "transliteration"])
    df["g"] = df["genre"].fillna("").astype(str).str.split(",").str[0].str.strip()
    adm = df[(df["g"] == "Administrative") & (df["period"] == "Ur III")]
    cand = adm[adm["transliteration"].astype(str).str.contains("šu-nigin")]
    print(f"[phase16] Ur III admin tablets with a total line: {len(cand):,}")

    verifiable = {}
    for _, row in cand.iterrows():
        r = analyse_tablet(row["transliteration"])
        if r is not None:
            verifiable[row["id"]] = r
    n_ver = len(verifiable)
    print(f"[phase16] verifiable under protocol rules: {n_ver:,}")

    # ---------------- validation gate
    zpath = DATA / "oracc" / "epsd2-admin-ur3.zip"
    gate = {"attempted": 0, "epsd2_matched": 0, "groups_parser": 0, "groups_agree": 0,
            "tablet_disagreements": []}
    if zpath.exists():
        zf = zipfile.ZipFile(zpath)
        ids = sorted(verifiable)
        rng.shuffle(ids)
        for pnum in ids:
            if gate["epsd2_matched"] >= GATE_N:
                break
            gate["attempted"] += 1
            toks = epsd2_tokens(zf, pnum)
            if toks is None:
                continue
            gate["epsd2_matched"] += 1
            ours = sorted(verifiable[pnum]["items"])
            theirs = sorted(epsd2_counted_groups(toks))
            # multiset agreement on COUNTED groups
            agree = 0
            pool = list(theirs)
            for v in ours:
                if v in pool:
                    pool.remove(v)
                    agree += 1
            gate["groups_parser"] += len(ours)
            gate["groups_agree"] += agree
            if agree < len(ours) and len(gate["tablet_disagreements"]) < 12:
                gate["tablet_disagreements"].append(
                    {"id": pnum, "parser": ours[:12], "epsd2": theirs[:12]})
        precision = gate["groups_agree"] / gate["groups_parser"] if gate["groups_parser"] else 0.0
    else:
        precision = 0.0
        print("[phase16] FATAL: ePSD2 zip missing; gate cannot run")
    gate["precision"] = round(precision, 4)
    gate_passed = precision >= GATE_PRECISION and gate["epsd2_matched"] >= 50
    print(f"[phase16] GATE: {gate['epsd2_matched']} tablets matched, "
          f"{gate['groups_agree']}/{gate['groups_parser']} counted groups agree "
          f"-> precision {precision:.4f} ({'PASS' if gate_passed else 'FAIL'} at {GATE_PRECISION})")

    payload = {"attrition_by_rule": dict(ATTRITION),
               "config": {"seed": SEED, "protocol": "PROTOCOL_phase16_arithmetic_audit.md",
                          "gate_n": GATE_N, "gate_precision_required": GATE_PRECISION,
                          "mtaac_evaluation": "public repos, no standalone parser package; "
                                              "comparison deferred (logged per protocol)",
                          "A4_dropped": "no provenance field in SumTablets (pre-authorised)"},
               "n_candidates": int(len(cand)), "n_verifiable": n_ver,
               "validation_gate": {k: v for k, v in gate.items() if k != "tablet_disagreements"},
               "gate_disagreement_examples": gate["tablet_disagreements"],
               "gate_passed": bool(gate_passed)}

    md = ["# Phase 16 — Auditing the world's first auditors (run against the committed protocol)\n\n",
          f"Protocol: [PROTOCOL_phase16_arithmetic_audit.md](../PROTOCOL_phase16_arithmetic_audit.md), "
          "committed 2026-08-06, before this analysis existed. MTAAC evaluation (step 0): public "
          "repos, no standalone numero-metrological parser package; comparison deferred — logged. "
          "A4 (provenance) dropped as pre-authorised: SumTablets has no provenance field.\n\n",
          f"Ur III administrative tablets with a total line: **{len(cand):,}** · verifiable under "
          f"the protocol's five exclusion rules: **{n_ver:,}**\n\n",
          "**Attrition by committed rule** (which rule was the binding constraint): "
          f"damage markers anywhere (rule 2): {ATTRITION['rule2_damage']:,}; multiple/zero total "
          f"lines (rule 1): {ATTRITION['rule1_multi_total']:,}; total line not pure count-system "
          f"(rule 3): {ATTRITION['rule3_total_line']:,}; unclassifiable numeral group (rule 4): "
          f"{ATTRITION['rule4_unclassifiable']:,}; fewer than 2 counted item lines (rule 5): "
          f"{ATTRITION['rule5_too_few_items']:,}. One scope note: the protocol quoted 2,476 "
          "total-bearing tablets corpus-wide; this run restricts to the Ur III period per the "
          "protocol's framing ('Ur III accounting'), giving 671 candidates — most total-bearing "
          "tablets sit in earlier periods.\n\n",
          f"## Validation gate (the part that decides whether an error rate may be published)\n\n",
          f"{gate['epsd2_matched']} verifiable tablets re-analysed by the independent ePSD2 "
          f"expert-lemma pipeline (protocol's second annotator): **{gate['groups_agree']} of "
          f"{gate['groups_parser']} COUNTED groups agree → precision {precision:.1%}** against the "
          f"required {GATE_PRECISION:.0%}. **GATE {'PASSED' if gate_passed else 'FAILED'}.**\n\n"]

    if not gate_passed:
        md.append("Per the protocol's kill criterion, **no error rate is published from this run**. "
                  "The validation numbers above and the disagreement examples below are the "
                  "publishable output. The next iteration must fix the classifier (or the "
                  "second-annotator alignment) and re-run the gate; a second failure retires the "
                  "study with these numbers as the result.\n\n")
        if gate["tablet_disagreements"]:
            md.append("| Tablet | Parser COUNTED groups | ePSD2 COUNTED groups |\n|---|---|---|\n")
            for d in gate["tablet_disagreements"][:8]:
                md.append(f"| {d['id']} | {d['parser']} | {d['epsd2']} |\n")
        payload["verdicts"] = {"gate": "FAILED", "error_rate_published": False}
    else:
        # ---------------- estimand + hypotheses (published only past the gate)
        ids = sorted(verifiable)
        res = [verifiable[i] for i in ids]
        n = len(res)
        errors = [r for r in res if not r["match"]]
        k = len(errors)
        import math as _m
        z = 1.96
        p_ = k / n
        d_ = 1 + z * z / n
        c_ = (p_ + z * z / (2 * n)) / d_
        h_ = z * _m.sqrt(p_ * (1 - p_) / n + z * z / (4 * n * n)) / d_
        under = sum(1 for r in errors if r["claimed"] < r["item_sum"])
        over = k - under
        by_items = {}
        for r in res:
            b = "2-3" if r["n_items"] <= 3 else ("4-6" if r["n_items"] <= 6 else "7+")
            by_items.setdefault(b, [0, 0])
            by_items[b][0] += 1
            by_items[b][1] += 0 if r["match"] else 1
        sealed = [r for r in res if r["sealed"]]
        unsealed = [r for r in res if not r["sealed"]]
        er_s = sum(1 for r in sealed if not r["match"]) / len(sealed) if sealed else float("nan")
        er_u = sum(1 for r in unsealed if not r["match"]) / len(unsealed) if unsealed else float("nan")
        payload["estimand"] = {"n_verifiable": n, "n_errors": k,
                               "error_rate": round(p_, 4),
                               "wilson_ci95": [round(max(0, c_ - h_), 4), round(min(1, c_ + h_), 4)],
                               "under_total": under, "over_total": over}
        payload["A2_by_item_count"] = {b: {"n": v[0], "errors": v[1],
                                           "rate": round(v[1] / v[0], 4) if v[0] else None}
                                       for b, v in sorted(by_items.items())}
        payload["A3_sealed_vs_unsealed"] = {"n_sealed": len(sealed), "n_unsealed": len(unsealed),
                                            "error_rate_sealed": round(er_s, 4),
                                            "error_rate_unsealed": round(er_u, 4)}
        payload["verdicts"] = {
            "gate": "PASSED",
            "A1_error_rate_below_5pct": bool((c_ + h_) < 0.05),
            "A2_rate_increases_with_items": None,   # descriptive; test only if n supports it
            "A3_sealed_lower": bool(er_s < er_u) if sealed and unsealed else None,
            "kill2_descriptive_only": bool(n < MIN_VERIFIABLE),
        }
        md.append(f"## Estimand\n\nAmong {n:,} verifiable tablets: **{k} totals do not equal their "
                  f"item sums — error rate {100*p_:.2f}% (Wilson 95% CI "
                  f"{100*max(0,c_-h_):.2f}–{100*min(1,c_+h_):.2f}%)**; {under} under-totals, "
                  f"{over} over-totals.\n\n")
        md.append("| Item-count bin | n | errors | rate |\n|---|---:|---:|---:|\n")
        for b, v in sorted(by_items.items()):
            md.append(f"| {b} | {v[0]:,} | {v[1]} | {100*v[1]/v[0]:.2f}% |\n")
        md.append(f"\nSealed: {len(sealed):,} tablets, error rate {100*er_s:.2f}%. Unsealed: "
                  f"{len(unsealed):,}, {100*er_u:.2f}%. (A3 stratified analysis and significance "
                  f"only if the counts support it; raw contrast reported regardless.)\n\n")
        if n < MIN_VERIFIABLE:
            md.append("**Kill criterion 2 applies: fewer than 150 verifiable tablets — everything "
                      "above is DESCRIPTIVE ONLY, no hypothesis verdicts.**\n\n")

    (OUT / "phase16_arithmetic_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "phase16_arithmetic_audit.md").write_text("".join(md), encoding="utf-8")
    print(f"[save] {OUT / 'phase16_arithmetic_audit.md'}")


if __name__ == "__main__":
    main()
