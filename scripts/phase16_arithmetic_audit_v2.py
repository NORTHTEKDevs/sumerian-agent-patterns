"""
Phase 16 v2: the arithmetic audit re-run against PROTOCOL_phase16_arithmetic_audit_v2.md as
committed 2026-08-07 (which supersedes v1's exclusion rules ONLY; estimand and hypotheses
unchanged from PROTOCOL_phase16_arithmetic_audit.md). Deviations, if any, go to CORRECTIONS.md.

WHAT v2 CHANGES (per the committed text)
----------------------------------------
- Unit of verifiability is the SECTION: each šu-nigin₂ line is checked against the item lines
  above it, back to the previous total (rule 1 subtotal support).
- Rule 2 damage exclusion is per-section: only the ITEM BLOCK (first counted line .. total line)
  and the TOTAL LINE must be damage-free; damage in headers/date/seal lines does not exclude.
- The validation gate is unchanged (>= 98% on COUNTED groups, 100 tablets) but the second-
  annotator alignment must be repaired first, with a disagreement post-mortem distinguishing
  classifier error from annotator-alignment error before the gate verdict counts.
- Kill criteria unchanged: gate failure after two iterations, or < 150 verifiable SECTIONS.

CLASSIFIER: UNCHANGED from the v1 run (iteration 1 keeps the committed classifier verbatim;
the gate + post-mortem, not pre-run edits, are the sanctioned mechanism for classifier changes).

ATTRIBUTION ORDER for per-section attrition (documented so the accounting is deterministic):
  2a. damage marker on the total line                      -> rule 2
  3.  total line not pure System-S + lexicon commodity     -> rule 3
  2b. damage marker in the item block (first counted line
      through the line before the total)                   -> rule 2
  4.  unclassifiable numeral group anywhere in the section
      item region                                          -> rule 4
  5.  fewer than 2 counted item lines                      -> rule 5
A section is VERIFIABLE only if it passes all five; the pass/fail SET is order-independent,
only the attrition attribution depends on this order.

SECOND ANNOTATOR (repaired, per v2 gate clause). v1's ePSD2 extraction had three alignment
defects, found in the v1 post-mortem material and fixed here BEFORE any verdict:
  (a) unordered tree walk (stack over dict.values() + reverse) - token order not guaranteed;
      v2 walks the CDL structure in document order and reconstructs LINES at line-start nodes;
  (b) commodity search window of 2 tokens after the numeral - modifiers (niga "fattened", ...)
      eclipsed the commodity; v2 classifies the whole reconstructed line by expert lemmas;
  (c) lexicon misses: ePSD2 citation forms use ŋ (ŋuruš, not guruš) so every personnel group
      was dropped, and fraction forms like 1/2(diš) parsed as 2(diš)=2; both fixed.
Round 2 (after the round-1 disagreement post-mortem, all six disagreeing groups adjudicated
as annotator-alignment error by hand inspection of the expert lemmas - see POSTMORTEM below):
  (d) the round-1 fraction guard matched "igi-" as a substring and ate lines whose personal
      name starts igi-zu-... ; narrowed to the igi-N-gal₂ fraction pattern proper;
  (e) two herd-animal compounds lemmatised under citation forms outside the lexicon
      (maš₂-sag = mašsaŋ "leader" i.e. lead goat; gu₄-ab₂-ba = gudabak "bull"); the citation
      forms were added exactly as ePSD2 writes them;
  (f) minus-notation lines (la₂ / la₂-ia₃) now skipped on the annotator side, symmetric with
      the parser's FRACTION exclusion, instead of misparsing "2(u) la₂ 1(diš)" (=19) as 20+1.
The repairs touch only annotator COVERAGE (ordering, guards, lemma rendering). The
classification judgment - what counts as a commodity, a date, a unit - stays ePSD2's own
expert lemmatisation throughout, so the annotator remains independent.
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

SEED = 20260808
GATE_N = 100
GATE_PRECISION = 0.98
MIN_VERIFIABLE_SECTIONS = 150

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
DAMAGE = ("<unk>", "...")

# Post-hoc sensitivity ONLY (not part of the committed pipeline): a generous personnel/status
# lexicon extension, to bound how much of the rule-3/rule-5 attrition is lexicon choice.
SENSITIVITY_EXTRA = ["aga₃-us₂", "erin₂", "dumu", "lu₂", "munus", "nita₂"]
COMMODITY_RE_WIDE = re.compile(
    "|".join(rf"\b{re.escape(c)}\b" for c in COMMODITIES + SENSITIVITY_EXTRA))


def classify_line(line: str, commodity_re=COMMODITY_RE):
    """v1 classifier, verbatim (commodity_re parameterised only for the sensitivity bound)."""
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
        return ("total", vals) if commodity_re.search(line) else ("unclassifiable", [])
    if DATE_CTX.search(line) or RATE.search(line):
        return ("noncounted", [])
    if commodity_re.search(line):
        return ("counted", vals)
    return ("unclassifiable", [])


def tablet_sections(text: str):
    lines = [l.strip() for l in str(text).split("\n")
             if l.strip() and not STRUCT.match(l.strip())]
    tot = [i for i, l in enumerate(lines) if TOTAL_RE.search(l)]
    out, prev = [], -1
    for ti in tot:
        out.append((lines[prev + 1:ti], lines[ti]))
        prev = ti
    return out


def _damaged(line: str) -> bool:
    return any(d in line for d in DAMAGE)


def verify_section(item_lines, total_line, attrition, decomp, commodity_re=COMMODITY_RE):
    """Apply v2 rules in the documented attribution order. Returns dict or None."""
    if _damaged(total_line):                                        # 2a
        attrition["rule2_damage"] += 1
        return None
    kind, tvals = classify_line(total_line, commodity_re)           # 3
    if kind != "total" or not tvals:
        groups = NUM.findall(total_line)
        units = [u for _, u in groups]
        if not groups:
            decomp["rule3_no_numeral"] += 1
        elif any(u in NONCOUNT_UNITS for u in units):
            decomp["rule3_capacity_or_weight"] += 1
        elif not all(u in SYSTEM_S for u in units):
            decomp["rule3_other_number_system"] += 1
        else:
            decomp["rule3_no_lexicon_commodity"] += 1
        attrition["rule3_total_line"] += 1
        return None
    kinds = [classify_line(l, commodity_re) for l in item_lines]
    counted_idx = [i for i, (k, _) in enumerate(kinds) if k == "counted"]
    if counted_idx:                                                 # 2b
        block = item_lines[counted_idx[0]:]
        if any(_damaged(l) for l in block):
            attrition["rule2_damage"] += 1
            return None
    if any(k == "unclassifiable" for k, _ in kinds):                # 4
        attrition["rule4_unclassifiable"] += 1
        return None
    if len(counted_idx) < 2:                                        # 5
        n_numeral_lines = sum(1 for k, _ in kinds if k != "none")
        if not item_lines:
            decomp["rule5_empty_item_region"] += 1
        elif n_numeral_lines == 0:
            decomp["rule5_no_numeral_lines"] += 1                   # implicit name-list sections
        elif len(counted_idx) == 0:
            decomp["rule5_all_numerals_noncounted"] += 1
        else:
            decomp["rule5_exactly_one_counted"] += 1
        attrition["rule5_too_few_items"] += 1
        return None
    items = [v for (k, vals) in kinds if k == "counted" for v in vals]
    counted_lines = [item_lines[i] for i in counted_idx]
    lead_damage = any(_damaged(l) for l in item_lines[:counted_idx[0]])
    return {"claimed": sum(tvals), "item_sum": sum(items), "items": items,
            "n_items": len(counted_idx), "counted_lines": counted_lines,
            "lead_damage": lead_damage,
            "match": sum(tvals) == sum(items)}


# ---------------- repaired ePSD2 second annotator

EPSD2_COMMODITY_CF = {"udu", "maš", "mašgal", "sila", "u₈", "ud₅", "gud", "ab", "amar",
                      "anše", "šaḫ", "šah", "mušen", "ŋuruš", "geme", "kir", "šeg",
                      "mašsaŋ", "gudabak", "udunita", "u"}
EPSD2_COMMODITY_GW = ("sheep", "goat", "lamb", "ewe", "ox", "cow", "calf", "donkey", "equid",
                      "pig", "bird", "worker", "female", "ram", "kid", "nanny", "billy",
                      "sow", "piglet", "laborer", "bull")
EPSD2_DATE_GW = ("day", "month", "year")
EPSD2_MINUS_CF = {"lal", "laʾu"}          # la₂ minus notation / la₂-ia₃ arrears
FRACTION_FORM = re.compile(r"igi-\d|\d+/\d+\(")


def epsd2_lines(zf: zipfile.ZipFile, pnum: str):
    """Reconstruct lines in document order from the CDL tree: list of token lists, each token
    (form, cf, gw). Returns None if the tablet is not in the ePSD2 Ur III corpus."""
    try:
        doc = json.loads(zf.read(f"epsd2/admin/ur3/corpusjson/{pnum}.json"))
    except KeyError:
        return None
    lines: list[list[tuple[str, str, str]]] = []

    def walk(node):
        if isinstance(node, list):
            for v in node:
                walk(v)
            return
        if not isinstance(node, dict):
            return
        if node.get("node") == "d" and node.get("type") == "line-start":
            lines.append([])
        elif node.get("node") == "l":
            f = node.get("f") or {}
            if f.get("form"):
                if not lines:
                    lines.append([])
                lines[-1].append((str(f["form"]), str(f.get("cf") or ""),
                                  str(f.get("gw") or "")))
        walk(node.get("cdl", []))

    walk(doc.get("cdl", []))
    return [l for l in lines if l]


def epsd2_counted_groups(lines):
    """Line-level COUNTED extraction from expert lemmas. A line's System-S numeral groups are
    COUNTED iff the line has a commodity lemma and is not a total / date / metrological /
    ordinal / rate / fraction line. Group granularity matches the parser (one value per
    N(unit) group)."""
    vals = []
    for toks in lines:
        forms = [t[0] for t in toks]
        gws = [t[2].lower() for t in toks]
        cfs = [t[1] for t in toks]
        if any(f.startswith("šu-nigin") or c == "šunigin" or g == "total"
               for f, c, g in zip(forms, cfs, gws)):
            continue
        if any(g == "unit" for g in gws):                     # gur/sila₃/gin₂/... metrological
            continue
        if any(g in EPSD2_DATE_GW for g in gws):
            continue
        if any(FRACTION_FORM.search(f) for f in forms):       # fractions (igi-N-gal₂, N/M)
            continue
        if any(c in EPSD2_MINUS_CF for c in cfs):             # la₂ minus / la₂-ia₃ arrears
            continue
        if any(f.endswith("-kam") or f.endswith("-ta") for f in forms):
            continue
        has_commodity = any(
            c in EPSD2_COMMODITY_CF or any(w in g for w in EPSD2_COMMODITY_GW)
            for c, g in zip(cfs, gws))
        if not has_commodity:
            continue
        for f in forms:
            groups = NUM.findall(f)
            if groups and all(u in SYSTEM_S for _, u in groups):
                vals.extend(int(m) * SYSTEM_S[u] for m, u in groups)
    return vals


# Post-mortem classifications of the ROUND-1 gate disagreements (v2 gate clause: classifier
# error vs annotator-alignment error), adjudicated by hand inspection of the ePSD2 expert
# lemmas; encoded here so regeneration is deterministic. All six disagreeing groups were
# annotator-alignment errors; zero classifier errors were found in the matched sample.
POSTMORTEM: dict[str, dict] = {
    "P205369": {"class": "annotator-alignment",
                "note": "maš₂-sag (lead goat) lemmatised cf=mašsaŋ gw='leader', outside the "
                        "round-1 annotator lexicon; all three maš₂-sag item lines dropped. "
                        "Parser classification correct."},
    "P515662": {"class": "annotator-alignment",
                "note": "gu₄-ab₂-ba (breed bull) lemmatised cf=gudabak gw='bull'; 'bull' "
                        "absent from the round-1 gw list. Parser classification correct."},
    "P207923": {"class": "annotator-alignment",
                "note": "round-1 fraction guard matched 'igi-' as substring and ate the line "
                        "'1(geš₂) guruš nu-banda₃ igi-zu-bar-ra' (igi-zu-bar-ra is a personal "
                        "name, pos=PN). Parser classification correct."},
}
ROUND1 = {"groups_parser": 242, "groups_agree": 236, "precision": 0.9752,
          "n_disagreeing_tablets": 3}


def main() -> None:
    rng = np.random.default_rng(SEED)
    df = pd.read_parquet(DATA / "sumtablets.parquet",
                         columns=["id", "genre", "period", "transliteration"])
    df["g"] = df["genre"].fillna("").astype(str).str.split(",").str[0].str.strip()
    adm = df[(df["g"] == "Administrative") & (df["period"] == "Ur III")]
    cand = adm[adm["transliteration"].astype(str).str.contains("šu-nigin")]
    print(f"[phase16v2] Ur III admin tablets with a total line: {len(cand):,}")

    attrition = {"rule2_damage": 0, "rule3_total_line": 0,
                 "rule4_unclassifiable": 0, "rule5_too_few_items": 0}
    decomp = {"rule3_no_numeral": 0, "rule3_capacity_or_weight": 0,
              "rule3_other_number_system": 0, "rule3_no_lexicon_commodity": 0,
              "rule5_empty_item_region": 0, "rule5_no_numeral_lines": 0,
              "rule5_all_numerals_noncounted": 0, "rule5_exactly_one_counted": 0}
    n_sections = 0
    verifiable: dict[str, list[dict]] = {}
    sealed_tablets: set[str] = set()
    for _, row in cand.iterrows():
        raw = str(row["transliteration"])
        if re.search(r"\bkišib(?:₃)?\b", raw):
            sealed_tablets.add(row["id"])
        for item_lines, total_line in tablet_sections(raw):
            n_sections += 1
            r = verify_section(item_lines, total_line, attrition, decomp)
            if r is not None:
                verifiable.setdefault(row["id"], []).append(r)
    n_ver = sum(len(v) for v in verifiable.values())
    n_ver_tabs = len(verifiable)
    print(f"[phase16v2] sections: {n_sections:,}  verifiable: {n_ver} "
          f"(on {n_ver_tabs} tablets)  attrition: {attrition}")

    kill2 = n_ver < MIN_VERIFIABLE_SECTIONS

    # Sensitivity bound (post-hoc, labeled): generous lexicon extension.
    attr_w = {k: 0 for k in attrition}
    dec_w = {k: 0 for k in decomp}
    n_ver_wide = 0
    for _, row in cand.iterrows():
        for item_lines, total_line in tablet_sections(str(row["transliteration"])):
            if verify_section(item_lines, total_line, attr_w, dec_w,
                              COMMODITY_RE_WIDE) is not None:
                n_ver_wide += 1
    print(f"[phase16v2] sensitivity (lexicon + {SENSITIVITY_EXTRA}): "
          f"{n_ver_wide} verifiable sections")

    # ---------------- repaired second annotator over the verifiable tablets (descriptive:
    # the committed gate requires a 100-tablet sample, unreachable here)
    zpath = DATA / "oracc" / "epsd2-admin-ur3.zip"
    gate = {"attempted": 0, "epsd2_matched": 0, "groups_parser": 0, "groups_agree": 0}
    disagreements = []
    if zpath.exists():
        zf = zipfile.ZipFile(zpath)
        ids = sorted(verifiable)
        rng.shuffle(ids)
        for pnum in ids:
            if gate["epsd2_matched"] >= GATE_N:
                break
            gate["attempted"] += 1
            lines = epsd2_lines(zf, pnum)
            if lines is None:
                continue
            gate["epsd2_matched"] += 1
            ours = sorted(v for sec in verifiable[pnum] for v in sec["items"])
            theirs = sorted(epsd2_counted_groups(lines))
            pool = list(theirs)
            agree, missing = 0, []
            for v in ours:
                if v in pool:
                    pool.remove(v)
                    agree += 1
                else:
                    missing.append(v)
            gate["groups_parser"] += len(ours)
            gate["groups_agree"] += agree
            if missing:
                disagreements.append({
                    "id": pnum, "missing_from_epsd2": missing,
                    "parser": ours, "epsd2": theirs,
                    "parser_counted_lines": [l for sec in verifiable[pnum]
                                             for l in sec["counted_lines"]],
                    "epsd2_lines": [" ".join(t[0] for t in l) for l in lines]})
        precision = gate["groups_agree"] / gate["groups_parser"] if gate["groups_parser"] else 0.0
    else:
        precision = 0.0
        print("[phase16v2] FATAL: ePSD2 zip missing; second annotator cannot run")
    gate["precision"] = round(precision, 4)
    print(f"[phase16v2] second annotator: {gate['epsd2_matched']} tablets, "
          f"{gate['groups_agree']}/{gate['groups_parser']} groups agree "
          f"-> {precision:.4f} (descriptive; gate needs {GATE_N} tablets)")

    (OUT / "phase16_v2_gate_disagreements.json").write_text(
        json.dumps(disagreements, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------- descriptive section table (kill 2 => no estimand, no hypothesis tests)
    sec_rows = []
    for pnum in sorted(verifiable):
        for j, sec in enumerate(verifiable[pnum], 1):
            sec_rows.append({"id": pnum, "section": j, "claimed": sec["claimed"],
                             "item_sum": sec["item_sum"], "n_items": sec["n_items"],
                             "match": sec["match"], "lead_damage": sec["lead_damage"],
                             "sealed_tablet": pnum in sealed_tablets})
    n_mismatch = sum(1 for r in sec_rows if not r["match"])
    n_lead = sum(1 for r in sec_rows if r["lead_damage"])
    mismatch_lead = sum(1 for r in sec_rows if not r["match"] and r["lead_damage"])

    payload = {
        "config": {"seed": SEED, "protocol": "PROTOCOL_phase16_arithmetic_audit_v2.md",
                   "unit": "section", "gate_n": GATE_N,
                   "gate_precision_required": GATE_PRECISION,
                   "min_verifiable_sections": MIN_VERIFIABLE_SECTIONS,
                   "classifier": "v1 verbatim (iteration 1)",
                   "sensitivity_extra_lexicon": SENSITIVITY_EXTRA},
        "n_candidates": int(len(cand)), "n_sections": n_sections,
        "attrition_by_rule": attrition, "attrition_decomposition": decomp,
        "n_verifiable_sections": n_ver, "n_verifiable_tablets": n_ver_tabs,
        "kill2_fired": bool(kill2),
        "sensitivity_wide_lexicon": {"n_verifiable_sections": n_ver_wide,
                                     "still_below_150": bool(n_ver_wide < 150)},
        "second_annotator_round1": ROUND1,
        "second_annotator_round2": gate,
        "postmortem": {k: v["class"] for k, v in POSTMORTEM.items()},
        "postmortem_verdict": "all round-1 disagreements annotator-alignment; "
                              "0 classifier errors in matched sample",
        "n_disagreeing_tablets_round2": len(disagreements),
        "sections_descriptive": sec_rows,
        "descriptive_counts": {"mismatch_sections": n_mismatch,
                               "lead_damage_sections": n_lead,
                               "mismatch_and_lead_damage": mismatch_lead},
        "verdicts": {"kill2_fewer_than_150_sections": bool(kill2),
                     "error_rate_published": False,
                     "hypothesis_tests_run": False},
    }

    md = [
        "# Phase 16 v2 — the arithmetic audit under per-section rules (run against protocol v2)\n\n",
        "Protocol: [PROTOCOL_phase16_arithmetic_audit_v2.md](../PROTOCOL_phase16_arithmetic_audit_v2.md), "
        "committed 2026-08-07 after v1's kill criteria fired; estimand and hypotheses unchanged "
        "from v1, exclusion rules per-section with subtotal support. Classifier: v1 verbatim "
        "(iteration 1). Unit of verifiability: the SECTION.\n\n",
        f"Candidates: **{len(cand):,} tablets**, containing **{n_sections:,} total-line "
        f"sections**. Verifiable under the v2 rules: **{n_ver} sections on {n_ver_tabs} "
        f"tablets**.\n\n",
        "## Verdict first: kill criterion 2 fires again, for a different and more "
        "interesting reason\n\n",
        f"**{n_ver} verifiable sections < 150 → no error rate, no hypothesis tests (A1–A3 not "
        "evaluated). The study retires under v2 as it did under v1.** But the attrition moved: "
        "v1 died of damage exclusion (79% of tablets); v2's per-section damage rule works — "
        f"damage now removes only {attrition['rule2_damage']} of {n_sections:,} sections "
        f"({100 * attrition['rule2_damage'] / n_sections:.0f}%). What kills v2 is the corpus "
        "itself:\n\n",
        f"- **Rule 3 removes {attrition['rule3_total_line']:,} sections "
        f"({100 * attrition['rule3_total_line'] / n_sections:.0f}%)**: "
        f"{decomp['rule3_capacity_or_weight']:,} totals are grain/capacity/weight metrology "
        "(gur/sila₃/gin₂ systems — outside the committed System-S head-count scope), "
        f"{decomp['rule3_no_lexicon_commodity']:,} System-S totals name no lexicon commodity "
        "on the total line (bare grand totals; status words like la₂-ia₃ 'deficit', zi-ga "
        "'expended', gub-ba 'stationed'; personnel terms outside the fixed lexicon such as "
        f"aga₃-us₂, erin₂), {decomp['rule3_no_numeral']:,} have no readable numeral, "
        f"{decomp['rule3_other_number_system']:,} use other number systems (šargal, eše₃, "
        "DIŠ/AŠ sign-value variants).\n",
        f"- **Rule 5 removes {attrition['rule5_too_few_items']:,} of the remaining sections**: "
        f"{decomp['rule5_no_numeral_lines']:,} sections total an item region with NO numeral "
        "lines at all — one-name-per-line personnel/delivery lists whose counts are implicit "
        f"(one head per line); {decomp['rule5_all_numerals_noncounted']:,} have numerals only "
        f"in date/rate context; {decomp['rule5_exactly_one_counted']:,} have exactly one "
        f"counted line; {decomp['rule5_empty_item_region']:,} are empty regions (grand totals "
        "directly after subtotals).\n",
        f"- Rule 4 (unclassifiable groups) removes {attrition['rule4_unclassifiable']:,}.\n\n",
        "**The structural finding: Ur III head-count totals mostly do not total explicit "
        "numeral item lines.** In order of magnitude: they are grain/capacity totals outside "
        "the head-count scope, System-S totals whose commodity or status word sits outside "
        "the fixed lexicon or off the total line, grand totals over subtotal regions with no "
        "items of their own, and implicit one-name-per-line lists. Explicit item-arithmetic "
        "sections — where a total can be checked against parseable addends — are rare in "
        "this corpus regardless of damage handling. v1's conclusion ('damage makes this "
        "impossible') was wrong about the binding constraint; v2 shows that fixing damage "
        "handling exposes a deeper scarcity.\n\n",
        f"**Robustness of the kill:** a deliberately generous post-hoc lexicon extension "
        f"({', '.join(SENSITIVITY_EXTRA)}) raises verifiable sections only to "
        f"**{n_ver_wide}** — still far below 150. The kill is not a lexicon artifact.\n\n",
        "## Second annotator, repaired (v2 obligation), descriptive only\n\n",
        "**Round 1** fixed three v1 alignment defects before any comparison: unordered CDL "
        "walk (token order not guaranteed), a 2-token commodity window that modifiers like "
        "niga 'fattened' eclipsed, and lexicon misses (ePSD2 writes ŋuruš with ŋ, so every "
        "personnel group dropped; fraction forms like 1/2(diš) parsed as 2). Round-1 result: "
        f"**{ROUND1['groups_agree']}/{ROUND1['groups_parser']} COUNTED groups agree "
        f"({100 * ROUND1['precision']:.1f}%)** over the verifiable tablets present in ePSD2 — "
        "against v1's 75%, which is thereby demonstrated to have been mostly annotator-"
        "alignment failure, not classifier failure.\n\n",
        "**Post-mortem (the v2 precondition for any gate verdict): every round-1 "
        f"disagreement — {ROUND1['groups_parser'] - ROUND1['groups_agree']} groups on "
        f"{ROUND1['n_disagreeing_tablets']} tablets — was adjudicated by hand against the "
        "expert lemmas as ANNOTATOR-ALIGNMENT error; zero classifier errors were found.**\n\n",
    ]
    for pid, pm in POSTMORTEM.items():
        md.append(f"- **{pid}** ({pm['class']}): {pm['note']}\n")
    md += [
        "\nRound 2 repaired those coverage gaps (citation forms added exactly as ePSD2 "
        "writes them: mašsaŋ, gudabak; fraction guard narrowed to igi-N-gal₂; la₂ minus-"
        "notation lines skipped symmetric with the parser). The classification judgment "
        "itself — what is a commodity, a date, a unit — remains ePSD2's expert lemmatisation "
        "throughout, so the annotator stays independent. Round-2 result over the "
        f"{gate['epsd2_matched']} matched tablets: **{gate['groups_agree']}/"
        f"{gate['groups_parser']} COUNTED groups agree ({100 * precision:.1f}%)**"
        + (f", {len(disagreements)} tablets still disagreeing (raw dump in "
           f"`phase16_v2_gate_disagreements.json`)" if disagreements else "")
        + ". This is DESCRIPTIVE: the committed gate requires a "
        f"{GATE_N}-tablet sample and only {n_ver_tabs} verifiable tablets exist, so no gate "
        "verdict is issued or counted.\n\n",
    ]
    md += [
        "## The 32-section descriptive record (NOT an error rate)\n\n",
        f"Among the {n_ver} verifiable sections, **{n_mismatch} raw total-vs-sum "
        f"disagreements**. These are UNVALIDATED parser disagreements, not scribal errors: "
        "the gate never ran at protocol scale, the classifier's line-level date suppression "
        "drops counted groups on mixed lines (the same `\\bmu\\b` overreach class the phase "
        "15b year-name audit quantified), and "
        f"{n_lead} sections have damage above their first counted line (possible destroyed "
        f"items; {mismatch_lead} of the disagreeing sections are in that set). The "
        "suppression mechanism is verified, not suspected: P515662's two 'mismatches' "
        "reconcile EXACTLY once its age-graded cattle lines (`8(diš) ab₂ mu 3(aš)` = eight "
        "3-year-old cows, suppressed because `mu` reads as date context) are restored — "
        "39 counted + 37 suppressed = 76 claimed, and 41 + 33 = 74. The scribes were right "
        "both times; the parser manufactured both disagreements.\n\n",
        "| Tablet | Sec | Total claims | Items sum | Counted lines | Match | Lead damage | Sealed tablet |\n"
        "|---|---:|---:|---:|---:|---|---|---|\n",
    ]
    for r in sec_rows:
        md.append(f"| {r['id']} | {r['section']} | {r['claimed']} | {r['item_sum']} | "
                  f"{r['n_items']} | {'yes' if r['match'] else 'NO'} | "
                  f"{'yes' if r['lead_damage'] else ''} | "
                  f"{'yes' if r['sealed_tablet'] else ''} |\n")
    md += [
        "\n## Status of the study\n\n",
        "Two committed protocols, two kills, two different binding constraints — v1: damage "
        "notation density; v2: the scarcity of explicit item-arithmetic in head-count "
        "sections. A v3 would need a different estimand (e.g. grain metrology with full "
        "capacity-system arithmetic, or implicit name-list counting), i.e. a new study, not "
        "a rules patch. Per both protocols, the attrition and validation accounting above "
        "IS the publishable output.\n",
    ]

    (OUT / "phase16_arithmetic_audit_v2.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "phase16_arithmetic_audit_v2.md").write_text("".join(md), encoding="utf-8")
    print(f"[save] {OUT / 'phase16_arithmetic_audit_v2.md'}")


if __name__ == "__main__":
    main()
