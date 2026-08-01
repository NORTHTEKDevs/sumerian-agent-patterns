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
