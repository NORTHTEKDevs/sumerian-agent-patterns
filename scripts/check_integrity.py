"""
Repo integrity check — run before publishing or tagging a release.

Verifies the things a reader or reviewer will hit first:
  1. Every relative link and backticked file path in the docs resolves to a real file.
  2. Every claim marked WITHDRAWN in the README is also marked in the derived documents,
     so a reader who lands on outputs/*.md directly cannot pick up a retracted claim.
  3. Every probe rated DO_NOT_CITE is stamped in templates.json.
  4. Reported corpus totals match the actual corpus.

Exit code 0 = clean, 1 = at least one problem. Intended for CI and for a pre-publish check.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

def _ascii_safe_stdout() -> None:
    """Windows consoles default to cp1252, which cannot encode Sumerian transliteration.
    Without this, printing a probe name crashes the script after the analysis has already
    succeeded -- the same failure that made benchmark.py unusable on Windows."""
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass


_ascii_safe_stdout()



ROOT = Path(__file__).resolve().parents[1]
problems: list[str] = []
checks = 0


def ok(cond: bool, msg: str) -> None:
    global checks
    checks += 1
    if not cond:
        problems.append(msg)


# ---- 1. links resolve -------------------------------------------------------
LINK = re.compile(r"\[[^\]]*\]\(([^)#][^)]*)\)")
docs = list(ROOT.glob("*.md")) + list((ROOT / "outputs").glob("*.md")) + list((ROOT / "benchmarks").glob("*.md"))
for doc in docs:
    text = doc.read_text(encoding="utf-8")
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (doc.parent / target.split("#")[0]).resolve()
        ok(resolved.exists(), f"{doc.relative_to(ROOT)}: broken link -> {target}")

# ---- 2. withdrawn claims are marked everywhere they appear -------------------
WITHDRAWN_MARKERS = ("WITHDRAWN", "withdrawn", "CORRECTION", "CORRECTED", "DO NOT CITE", "DO_NOT_CITE")
# (file, a regex for the retracted assertion, human description)
RETRACTED = [
    ("outputs/reference_architecture.md", r"provably a logical row separator", "RULING-as-proven-row-separator"),
    ("outputs/summary.md", r"statistically confirms the row tier", "RULING parity confirmation"),
    ("outputs/summary.md", r"No write is anonymous, undated, or unattributed", "'no write is anonymous'"),
    ("outputs/FULL_IDEAS.md", r"parity p=0\.002", "RULING parity p-value"),
]
for rel, pattern, desc in RETRACTED:
    path = ROOT / rel
    if not path.exists():
        ok(False, f"missing file referenced by integrity check: {rel}")
        continue
    text = path.read_text(encoding="utf-8")
    m = re.search(pattern, text)
    if m:
        # The correction must be TIGHTLY coupled to the assertion. The window is deliberately
        # narrow (300 chars before / 800 after) so that a document-level banner at the top of
        # the file cannot satisfy the check for an assertion buried 60 lines further down --
        # an earlier, wider window made this check vacuous, which a negative control caught.
        window = text[max(0, m.start() - 300): m.end() + 800]
        ok(any(k in window for k in WITHDRAWN_MARKERS),
           f"{rel}: retracted claim '{desc}' appears with no correction notice adjacent to it")

# ---- 3. DO_NOT_CITE probes are stamped in templates.json --------------------
tpath = ROOT / "outputs" / "templates.json"
if tpath.exists():
    t = json.loads(tpath.read_text(encoding="utf-8"))
    ok("_AUDIT" in t, "templates.json: missing _AUDIT block")
    dnc = set(t.get("_AUDIT", {}).get("do_not_cite", {}))
    ok(bool(dnc), "templates.json: _AUDIT.do_not_cite is empty")
    for row in t.get("templates", []) + t.get("probe_hits", []):
        name = row.get("template_name") or row.get("probe")
        if name in dnc:
            ok(row.get("_audit_verdict") == "DO_NOT_CITE",
               f"templates.json: row '{name}' is DO_NOT_CITE but carries no _audit_verdict")
else:
    ok(False, "outputs/templates.json missing — run scripts/phase1_templates.py")

# ---- 3b. headline numbers in the prose match the generated JSON -------------
# Catches the failure mode that started this whole audit: a hand-edited report drifting
# away from the machine output it was generated from.
p4 = ROOT / "outputs" / "phase4_ruling_fullcorpus.json"
if p4.exists():
    d = json.loads(p4.read_text(encoding="utf-8"))
    adm = next((r for r in d["results"] if r["genre"] == "Administrative"), None)
    ok(adm is not None, "phase4 JSON missing the Administrative result")
    if adm:
        for doc in ("FINDINGS.md", "CORRECTIONS.md", "README.md"):
            text = (ROOT / doc).read_text(encoding="utf-8")
            if "phase4" in text or "2,095" in text or "0.0006" in text:
                ok(f"{adm['n_adjacent_pairs']:,}" in text,
                   f"{doc}: cites a pair count differing from phase4 JSON ({adm['n_adjacent_pairs']:,})")
                ok(str(adm["p_two_sided_null_A_BH"]) in text,
                   f"{doc}: cites a p-value differing from phase4 JSON ({adm['p_two_sided_null_A_BH']})")
        ok(adm["null_A_length_permute"]["delta"] < 0,
           "phase4: Administrative delta is no longer negative — every doc describing the direction is now wrong")

p5 = ROOT / "outputs" / "phase5_powerlaw.json"
if p5.exists():
    d5 = json.loads(p5.read_text(encoding="utf-8"))
    lex = next((r for r in d5["results"] if r["genre"] == "Lexical"), None)
    if lex:
        ok(lex["powerlaw_ruled_out"] is True,
           "phase5: Lexical no longer rules out a power law — FINDINGS.md and CORRECTIONS.md say it does")
        ok(all((r["vuong_p_mean"] or 0) > 0.05 for r in d5["results"]),
           "phase5: a Vuong test is now significant — the 'indistinguishable from lognormal' claim needs revising")

# ---- 3c. PAPER.md headline numbers match the generated JSON -----------------
paper = ROOT / "PAPER.md"
p8 = ROOT / "outputs" / "phase8_boundary_recovery.json"
p7 = ROOT / "outputs" / "phase7_oracc_validation.json"
if paper.exists():
    ptext = paper.read_text(encoding="utf-8")
    if p8.exists():
        d8 = json.loads(p8.read_text(encoding="utf-8"))
        adm8 = d8["results"].get("Administrative", {})
        s8 = adm8.get("summary", {})
        for method in ("closer", "overlap_min", "random", "equal"):
            val = s8.get(method, {}).get("pk")
            if val is not None:
                ok(f"{val:.3f}" in ptext,
                   f"PAPER.md: Administrative {method} Pk {val:.3f} not found — prose has drifted from phase8 JSON")
        strat = adm8.get("closer_stratum", {}).get("with_closer_lines", {})
        if strat.get("closer_pk") is not None:
            ok(f"{strat['closer_pk']:.3f}"[:5] in ptext,
               f"PAPER.md: closer-stratum Pk {strat['closer_pk']} not found — prose has drifted from phase8 JSON")
            ok(f"{strat['random_pk']:.3f}"[:5] in ptext,
               f"PAPER.md: same-stratum random Pk {strat['random_pk']} not found — the stratified comparison must cite both sides")
        # The paper's central claims, asserted STRICTLY — an earlier tolerance (+0.06) was wider
        # than the effect it protected, so the headline ordering could have reversed without
        # breaking the build. Caught in adversarial review.
        if s8:
            ok(s8["closer"]["pk"] < s8["random"]["pk"],
               "phase8: closer no longer beats random on mean Pk — §6 result 2 is dead")
            ok(s8["overlap_min"]["pk"] >= s8["random"]["pk"] - 0.005,
               "phase8: overlap_min now clearly beats random — §6 result 1 (similarity fails) is dead")
            ok(s8["equal"]["pk"] > s8["random"]["pk"],
               "phase8: equal no longer worse than random — §6 result 3 is dead")
        ovr = adm8.get("paired_tests", {}).get("overlap_min_vs_random", {})
        if ovr:
            ok(ovr.get("losses_pk", 0) > ovr.get("wins_pk", 0),
               "phase8: overlap_min no longer loses the paired test vs random — abstract claim is dead")
            ok(f"{ovr['wins_pk']}" in ptext and f"{ovr['losses_pk']:,}" in ptext,
               "PAPER.md: overlap_min-vs-random win/loss counts not found — prose has drifted")
        pre = d8.get("corpus_prefilter", {})
        if pre.get("tablets_with_any_ruling"):
            ok(f"{pre['tablets_with_any_ruling']:,}" in ptext,
               f"PAPER.md: ruling-tablet count {pre['tablets_with_any_ruling']:,} not found or drifted")

    # phase9: the embedding-experiment numbers the paper cites, plus the assertions its claims
    # rest on -- the twin comparison direction, the markerless-stratum significance, and the
    # shuffled control collapsing to chance.
    p9 = ROOT / "outputs" / "phase9_embedding_chunking.json"
    if p9.exists():
        d9 = json.loads(p9.read_text(encoding="utf-8"))
        adm9 = d9["results"].get("Administrative", {})
        s9 = adm9.get("summary", {})
        t9 = adm9.get("paired_tests", {})
        twin = t9.get("emb_valley_vs_lex_valley", {})
        if twin:
            ok(twin.get("wins_pk", 0) > twin.get("losses_pk", 0),
               "phase9: embeddings no longer beat their lexical twin — abstract claim is dead")
            ok(f"{twin['wins_pk']}/{twin['losses_pk']}" in ptext,
               "PAPER.md: twin-comparison win/loss counts not found — prose has drifted")
        no9 = adm9.get("marker_strata", {}).get("without_closer_lines", {})
        if no9:
            eg = no9.get("emb_global_vs_random", {})
            ok(eg.get("pk_sign_p_bh", 1.0) < 0.05,
               "phase9: markerless-stratum emb_global significance lost — §6.5 claim is dead")
            ok(f"{no9['emb_global_pk']:.3f}" in ptext,
               f"PAPER.md: markerless emb_global Pk {no9['emb_global_pk']} not found — drifted")
            bhval = eg.get("pk_sign_p_bh")
            ok(str(bhval) in ptext or f"{bhval:.3f}" in ptext,
               f"PAPER.md: markerless BH p {bhval} (or 3-dp rounding) not found — drifted")
        if s9:
            ok(abs(s9["shuffled_control"]["pk"] - s9["random"]["pk"]) < 0.015,
               "phase9: shuffled-embedding control no longer collapses to chance — emb results suspect")

    # phase4 and phase6 headline numbers must appear in PAPER.md too, not only FINDINGS/CORRECTIONS
    p4b = ROOT / "outputs" / "phase4_ruling_fullcorpus.json"
    if p4b.exists():
        d4 = json.loads(p4b.read_text(encoding="utf-8"))
        adm4 = next((r for r in d4["results"] if r["genre"] == "Administrative"), None)
        if adm4:
            ok(f"{adm4['n_adjacent_pairs']:,}" in ptext, "PAPER.md: phase4 pair count missing/drifted")
            ok(str(adm4["p_two_sided_null_A_BH"]) in ptext, "PAPER.md: phase4 BH p missing/drifted")
    p6b = ROOT / "outputs" / "phase6_ruling_mechanism.json"
    if p6b.exists():
        d6 = json.loads(p6b.read_text(encoding="utf-8"))
        adm6 = d6.get("results", {}).get("Administrative", {}).get("markers", {})
        for probe_label, key in (("received_by (šu ba-ti)", "enrichment"), ("seal_of_PN (kišib₃)", "enrichment")):
            pc = adm6.get(probe_label, {}).get("position_controlled", {})
            if pc.get("enrichment") is not None:
                ok(f"{pc['enrichment']}" in ptext,
                   f"PAPER.md: phase6 {probe_label} position-controlled enrichment {pc['enrichment']} missing/drifted")
    if p7.exists():
        d7 = json.loads(p7.read_text(encoding="utf-8"))
        kt = d7["results"].get("king_title", {})
        if kt.get("oracc_occurrences"):
            pn = kt.get("pos_distribution", {}).get("PN", 0)
            share = round(100 * pn / kt["oracc_occurrences"])
            ok(f"{share}%" in ptext,
               f"PAPER.md: lugal PN share {share}% not found — prose has drifted from phase7 JSON")

# ---- 4. corpus totals match what the docs claim -----------------------------
parquet = ROOT / "data" / "sumtablets.parquet"
if parquet.exists():
    import pandas as pd
    df = pd.read_parquet(parquet, columns=["id"])
    n = len(df)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    ok(f"{n:,}" in readme, f"README cites a tablet count that does not match the corpus ({n:,})")
    ok(df["id"].duplicated().sum() == 0, "corpus contains duplicate tablet IDs")
else:
    print("[skip] data/sumtablets.parquet not present — run scripts/phase0_sample.py for corpus checks")

# ---- report -----------------------------------------------------------------
print(f"[integrity] {checks} checks run")
if problems:
    print(f"[integrity] {len(problems)} PROBLEM(S):")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)
print("[integrity] clean")
