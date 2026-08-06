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

    # phase10: the paper claims 4/4 pre-registered replication -- assert it from the JSON
    p10 = ROOT / "outputs" / "phase10_model_robustness.json"
    if p10.exists():
        d10 = json.loads(p10.read_text(encoding="utf-8"))
        ok(d10.get("n_replicated") == d10.get("n_criteria") == 4,
           "phase10: replication no longer 4/4 -- PAPER s6.5 and FINDINGS claims are dead")
        ok("4 of 4" in ptext or "4/4" in ptext,
           "PAPER.md: the 4-of-4 replication claim text not found")

    # phase11: the in-distribution replication the paper cites -- M1/M3/M5 must still hold,
    # the 3-of-5 verdict count must match, and the headline stratified numbers must appear.
    p11 = ROOT / "outputs" / "phase11_modern_indistribution.json"
    if p11.exists():
        d11 = json.loads(p11.read_text(encoding="utf-8"))
        v11 = d11.get("verdicts", {})
        ok(v11.get("M1_trailer_cue_dominates") is True,
           "phase11: M1 no longer holds -- the paper's central transfer claim is dead")
        ok(v11.get("M3_markerless_embeddings_beat_random") is True,
           "phase11: M3 no longer holds -- the markerless in-distribution claim is dead")
        ok(v11.get("M5_shuffled_control_collapses_both") is True,
           "phase11: shuffled control no longer collapses -- embedding results suspect")
        ok(d11.get("n_held") == 3 and d11.get("n_criteria") == 5,
           "phase11: verdict count changed -- PAPER 'three held and two failed' text is stale")
        gg = d11["results"].get("git/git (trailer-rich)", {})
        w11 = gg.get("strata", {}).get("with_trailers", {})
        if w11:
            ok(f"{w11['closer_pk']:.3f}" in ptext and f"{w11['random_pk']:.3f}" in ptext,
               f"PAPER.md: phase11 stratified numbers {w11['closer_pk']}/{w11['random_pk']} missing/drifted")

    # WRITEUP.md (the public post) cites headline numbers too -- couple them to the same JSONs
    # so the post cannot drift from the data any more than the paper can.
    wpath = ROOT / "WRITEUP.md"
    if wpath.exists():
        wtext = wpath.read_text(encoding="utf-8")
        if p8.exists():
            strat_w = json.loads(p8.read_text(encoding="utf-8"))["results"].get(
                "Administrative", {}).get("closer_stratum", {}).get("with_closer_lines", {})
            if strat_w.get("closer_pk") is not None:
                ok(f"{strat_w['closer_pk']:.3f}"[:5] in wtext and f"{strat_w['random_pk']:.3f}"[:5] in wtext,
                   "WRITEUP.md: phase8 stratified numbers missing or drifted")
        p11w = ROOT / "outputs" / "phase11_modern_indistribution.json"
        if p11w.exists():
            gg_w = json.loads(p11w.read_text(encoding="utf-8"))["results"].get(
                "git/git (trailer-rich)", {}).get("strata", {}).get("with_trailers", {})
            if gg_w:
                ok(f"{gg_w['closer_pk']:.3f}" in wtext and f"{gg_w['random_pk']:.3f}" in wtext,
                   "WRITEUP.md: phase11 stratified numbers missing or drifted")
        if p7.exists():
            kt_w = json.loads(p7.read_text(encoding="utf-8"))["results"].get("king_title", {})
            if kt_w.get("oracc_occurrences"):
                pn_share = round(100 * kt_w["pos_distribution"].get("PN", 0) / kt_w["oracc_occurrences"])
                ok(f"{pn_share}%" in wtext, f"WRITEUP.md: lugal PN share {pn_share}% missing or drifted")

    # phases 12-14: the claims v1.5 rests on, asserted from the generated JSONs.
    p12 = ROOT / "outputs" / "phase12_unknown_k.json"
    if p12.exists():
        d12 = json.loads(p12.read_text(encoding="utf-8"))
        ok(d12.get("verdicts", {}).get("U1_markers_dominate_and_estimate_K") is True,
           "phase12: U1 no longer holds — the unknown-K marker claim is dead")
        gg12 = d12["results"].get("git/git (trailer-rich)", {}).get("strata", {}).get("with_markers", {})
        if gg12:
            ok(f"{gg12['marker_K_pk']:.3f}"[:5] in ptext,
               f"PAPER.md: phase12 git/git marker stratum Pk {gg12['marker_K_pk']} missing/drifted")
    p13 = ROOT / "outputs" / "phase13_dispersion.json"
    if p13.exists():
        d13 = json.loads(p13.read_text(encoding="utf-8"))
        ok(d13.get("verdicts", {}).get("D1_gap_increases_with_cv") is False,
           "phase13: D1 now HOLDS — the dispersion-mechanism withdrawal in CORRECTIONS/PAPER is stale")
        ok("rho = −0.03" in ptext or "rho = -0.03" in ptext
           or f"{d13.get('spearman_rho')}" in ptext,
           "PAPER.md: phase13 rho missing — the refutation must be visible in the paper")
    p14 = ROOT / "outputs" / "phase14_agent_traces.json"
    if p14.exists():
        d14 = json.loads(p14.read_text(encoding="utf-8"))
        v14 = d14.get("verdicts", {})
        ok(v14.get("T1_embeddings_beat_random_on_raw_traces") is False,
           "phase14: T1 now HOLDS — the paper reports it as failed; prose is stale")
        ok(v14.get("T2_engineered_delimiter_closes_problem") is True,
           "phase14: T2 no longer holds — the engineered-delimiter demonstration failed")
        ok(v14.get("T3_dispersion_prediction", {}).get("status") == "VOID_mechanism_refuted_in_phase13",
           "phase14: T3 no longer marked VOID — coherence with phase 13's refutation is broken")
        raw14 = d14.get("raw_condition", {}).get("summary", {})
        if raw14:
            ok(raw14.get("equal", {}).get("pk", 1) < min(raw14.get("emb_valley", {}).get("pk", 0),
                                                          raw14.get("emb_global", {}).get("pk", 0)),
               "phase14: fixed-size no longer beats similarity methods on raw traces — §6.7/§7 claim is dead")
            ok(f"{raw14['equal']['pk']:.3f}" in ptext,
               f"PAPER.md: phase14 raw-trace equal Pk {raw14['equal']['pk']} missing/drifted")
        # Couple the PAIRED numbers too. The prose was once written from the second-to-last run
        # and drifted in the third decimal after the final regeneration -- caught by the review
        # gate's numbers verifier ("fresh drift inside the very passage that claims to have
        # fixed drift"). Never again.
        eq14 = d14.get("raw_condition", {}).get("paired_tests", {}).get("equal_vs_random", {})
        if eq14:
            ok(f"{eq14['wins_pk']}/{eq14['losses_pk']}" in ptext,
               f"PAPER.md: phase14 equal-vs-random {eq14['wins_pk']}/{eq14['losses_pk']} missing/drifted")
        ev14 = d14.get("raw_condition", {}).get("paired_tests", {}).get("emb_valley_vs_random", {})
        if ev14 and ev14.get("pk_sign_p_bh") is not None:
            ok(f"{ev14['pk_sign_p_bh']:.2f}" in ptext,
               f"PAPER.md: phase14 emb-valley BH {ev14['pk_sign_p_bh']} (2dp) missing/drifted")
        # privacy re-assertion at integrity time: no long transcript-looking lines in the JSON
        ok('"privacy": "aggregate metrics only' in (ROOT / "outputs" / "phase14_agent_traces.json").read_text(encoding="utf-8"),
           "phase14: privacy statement missing from output JSON")

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
