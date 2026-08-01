"""
Phase 1b: Precision audit of the Phase 1 regex probes → outputs/probe_validation.md

Phase 1 reports how often each probe MATCHES. It never asks whether the matches mean
what the probe's label says. This script asks that, because every headline frequency in
the README rests on it.

Method. For each audited probe, a set of hand-written discriminators partitions its
matches into buckets that are philologically distinguishable by surface form alone --
e.g. `lugal-` followed by a name element is a personal name, `lugal` followed by a
place name is the title "king of X". Each bucket is labelled TRUE (consistent with the
probe's claimed semantic role), FALSE (demonstrably a different lexeme or construction),
or UNCLEAR. Reported precision is TRUE / (TRUE + FALSE), with UNCLEAR excluded and
counted separately.

Epistemic status. The discriminators encode standard dictionary values (ePSD2/CDLI
conventions) applied by a NON-SPECIALIST. They are deliberately conservative: a bucket
is only marked FALSE where the surface form makes the alternative reading unambiguous
(`nam-lugal` = "kingship" cannot be a dedicatory formula; `igi-zu-še₃` = "before you"
cannot be a witness clause naming a person). This is a lower bound on the error rate,
not a substitute for specialist review. See REVIEWERS.md.

Output: outputs/probe_validation.md + outputs/probe_validation.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

# (probe, claimed_role, [(verdict, label, regex_on_the_MATCH_TEXT)])
# Rules are applied in order; first match wins. Anything unmatched falls to the default.
AUDITS: list[tuple[str, str, str, list[tuple[str, str, str]], str]] = [
    (
        "year_formula", r"\bmu\b(?:[\s\-][^\n]{0,80})", "temporal index (year-name)",
        [
            ("FALSE", "verbal prefix (mu-na-, mu-un-, mu-ni-, ...)", r"^mu-(na|un|ni|e|ra|da|ta|ši|a)"),
            ("FALSE", "mu-kuₓ(DU) = delivery, a different lexeme", r"^mu-kuₓ"),
            ("FALSE", "line-break / structural-token artifact", r"^mu\s*<"),
            ("TRUE", "mu us₂-sa + event (derived year-name)", r"^mu\s+us₂-sa\b"),
            ("TRUE", "mu + royal/event name (year-name)", r"^mu\s+\S"),
            ("FALSE", "mu-bi / mu-ni = 'its/his name'", r"^mu-(bi|ni|zu|mu)\b"),
        ],
        "UNCLEAR",
    ),
    (
        "king_title", r"\blugal\b[^\n]{0,40}", "title: king",
        [
            ("TRUE", "lugal + GN/epithet (king of X, mighty king)", r"^lugal\s+(uri|urim|kal-ga|kalag-ga|an[\s\-]ub-da|ki-en-gi|ma-da)"),
            ("FALSE", "lugal- as element of a PERSONAL NAME", r"^lugal-(?!e₂-mah)\S*[a-z]"),
            ("FALSE", "lugal-mu / lugal-a-ni = 'my/his master' (possessed)", r"^lugal-(mu|a-ni|ne)\b"),
            ("UNCLEAR", "bare 'lugal' (king, or 'owner/master' in admin context)", r"^lugal\s*$|^lugal\b(?![\s\-]\S)"),
        ],
        "UNCLEAR",
    ),
    (
        "god_dedication", r"\bnam-(ti|ki|en|lugal)\b", "dedicatory formula",
        [
            ("TRUE", "nam-ti = 'life' (used in 'for the life of' dedications)", r"^ti$"),
            ("FALSE", "nam-lugal = 'KINGSHIP', an abstract noun", r"^lugal$"),
            ("FALSE", "nam-en = 'en-ship/lordship', an abstract noun", r"^en$"),
        ],
        "UNCLEAR",
    ),
    (
        "witness_eye", r"\bigi[\s\-][^\n]{0,40}-š[èe]₃\b", "witness presence (before X)",
        [
            ("FALSE", "igi-ni/zu/bi/mu-še₃ = 'before him/you/it' (pronominal)", r"^igi-(ni|ma|mu|zu|bi)-š[èe]₃"),
            ("FALSE", "igi-nim = 'upper/northern', a different lexeme", r"^igi-nim"),
            ("FALSE", "igi + numeral = accounting expression, not a witness", r"^igi\s+\d"),
            ("TRUE", "igi + PN/DN + -še₃ (genuine witness clause)", r"^igi\s+\S"),
        ],
        "UNCLEAR",
    ),
    (
        "son_of_PN", r"\bdumu\b[\s\-][^\n]{0,40}", "filiation / lineage",
        [
            ("FALSE", "dumu-zi = Dumuzi (divine/personal name)", r"^dumu-zi\b"),
            ("UNCLEAR", "dumu-ni / dumu-munus etc. (possessed / compound)", r"^dumu-(ni|munus|gi|nita)\b"),
            ("TRUE", "dumu + PN (filiation)", r"^dumu\s+\S"),
        ],
        "UNCLEAR",
    ),
    (
        "excess_diri", r"\bdiri\b[^\n]{0,40}", "excess / surplus",
        [
            ("FALSE", "diri + month name = INTERCALARY MONTH, not a ledger surplus", r"^diri\s+(ezem|še-sag|iti|mah)"),
            ("UNCLEAR", "diri-ga / bare diri (verbal 'to exceed', or surplus)", r"^diri(-ga)?\s*$|^diri\.\.\."),
            ("TRUE", "diri + quantity (surplus amount)", r"^diri\s+\d"),
        ],
        "UNCLEAR",
    ),
    (
        "seal_of_PN", r"\bkišib(?:₃)?\b[^\n]{0,40}", "identity / authentication",
        [
            ("FALSE", "kišib₃-bi N = 'its sealed tablets: N' (a count, not an attribution)", r"^kišib₃?-bi\b"),
            ("TRUE", "kišib₃ + PN/title (seal of so-and-so)", r"^kišib₃?\s+\S"),
        ],
        "UNCLEAR",
    ),
    (
        "received_by", r"\bšu\s+ba-ti\b", "transaction confirmation",
        [("TRUE", "šu ba-ti = 'received' (fixed formula)", r"^šu\s+ba-ti$")],
        "UNCLEAR",
    ),
    (
        "speak_to_him", r"\bu₃-na-a-du₁₁\b", "letter address formula",
        [("TRUE", "u₃-na-a-du₁₁ = 'speak to him' (fixed formula)", r"^u₃-na-a-du₁₁$")],
        "UNCLEAR",
    ),
    (
        "total_audit", r"\bšu-nigin₂?\b[^\n]{0,40}", "ledger total / audit line",
        [("TRUE", "šu-nigin₂ = 'sum total'", r"^šu-nigin₂?")],
        "UNCLEAR",
    ),
]

# Probes whose match count is fine but whose TABLET-LEVEL RATE is the thing a reader
# will misread. Reported separately as prevalence, because "attested" != "characteristic".
PREVALENCE = [
    ("seal_of_PN", r"kišib(₃)?", "seal attribution"),
    ("year_formula (strict)", r"\bmu\s+(?:us₂-sa\s+)?(?!<)\S", "year-name dating"),
    ("total_audit", r"šu-nigin₂?", "periodic sum-total"),
    ("deficit_la2ia3", r"la₂-ia₃", "named deficit"),
    ("excess_diri", r"\bdiri\b", "named excess"),
    ("witness_eye (non-pronominal)", r"\bigi\s+(?!(?:ni|ma|mu|zu|bi|nim)-)[^\n]{2,40}-š[èe]₃\b", "witness clause"),
    ("received_by", r"šu\s+ba-ti", "receipt confirmation"),
]


def audit_probe(texts: list[str], pattern: str, rules, default: str) -> dict:
    rx = re.compile(pattern)
    buckets: dict[tuple[str, str], int] = {}
    total = 0
    for t in texts:
        for m in rx.findall(t):
            s = " ".join(str(m).split())
            total += 1
            for verdict, label, rule in rules:
                if re.search(rule, s):
                    buckets[(verdict, label)] = buckets.get((verdict, label), 0) + 1
                    break
            else:
                buckets[(default, "unclassified by the discriminators")] = \
                    buckets.get((default, "unclassified by the discriminators"), 0) + 1
    t_ = sum(v for (vd, _), v in buckets.items() if vd == "TRUE")
    f_ = sum(v for (vd, _), v in buckets.items() if vd == "FALSE")
    u_ = sum(v for (vd, _), v in buckets.items() if vd == "UNCLEAR")
    precision = (t_ / (t_ + f_)) if (t_ + f_) else float("nan")
    return {"total_matches": total, "true": t_, "false": f_, "unclear": u_,
            "precision_excl_unclear": round(precision, 3) if precision == precision else None,
            "buckets": [{"verdict": vd, "label": lb, "n": n} for (vd, lb), n in
                        sorted(buckets.items(), key=lambda kv: -kv[1])]}


def main() -> None:
    df = pd.read_parquet(DATA / "sample_500.parquet")
    texts = df["transliteration"].astype(str).tolist()
    genres = sorted(df["genre_primary"].unique())

    results = {}
    for name, pattern, role, rules, default in AUDITS:
        results[name] = audit_probe(texts, pattern, rules, default) | {"claimed_role": role, "regex": pattern}
        print(f"[audit] {name:<16} precision={results[name]['precision_excl_unclear']}")

    prevalence = {}
    for label, pattern, human in PREVALENCE:
        rx = re.compile(pattern)
        prevalence[label] = {"description": human, "by_genre": {
            g: round(100 * sum(1 for t in df[df["genre_primary"] == g]["transliteration"].astype(str) if rx.search(t))
                     / max((df["genre_primary"] == g).sum(), 1), 1) for g in genres}}

    # Probes that never fire are silently dropped by phase1 -- surface them.
    from phase1_templates import PROBES
    dead = []
    for pname, ppat, _role in PROBES:
        rx = re.compile(ppat)
        if not any(rx.search(t) for t in texts):
            dead.append({"probe": pname, "regex": ppat})

    md = ["# Probe Validation — do the Phase 1 regexes mean what their labels say?\n\n",
          "Phase 1 reports how often each probe **matches**. This report asks whether those matches ",
          "**mean** what the probe's label claims. Every headline frequency in the README rests on the answer.\n\n",
          "> **Epistemic status.** The discriminators below encode standard dictionary values applied by a ",
          "**non-specialist**. They are deliberately conservative — a match is only counted FALSE where the ",
          "surface form makes an alternative reading unambiguous. **These are lower bounds on the error rate, ",
          "and are not a substitute for review by an Assyriologist.** See `REVIEWERS.md`.\n\n",
          "Precision = TRUE / (TRUE + FALSE); UNCLEAR is excluded and reported separately.\n\n",
          "## Summary\n\n| Probe | Claimed role | Matches | Precision | UNCLEAR | Verdict |\n",
          "|---|---|---:|---:|---:|---|\n"]
    for name, r in results.items():
        p = r["precision_excl_unclear"]
        if p is None:
            v = "n/a"
        elif p >= 0.95:
            v = "**reliable**"
        elif p >= 0.75:
            v = "usable with caveat"
        elif p >= 0.5:
            v = "**weak**"
        else:
            v = "**DO NOT CITE**"
        md.append(f"| `{name}` | {r['claimed_role']} | {r['total_matches']:,} | "
                  f"{'—' if p is None else f'{100*p:.0f}%'} | {r['unclear']:,} | {v} |\n")

    md.append("\n## Per-probe detail\n\n")
    for name, r in results.items():
        md.append(f"### `{name}` — claimed role: {r['claimed_role']}\n\n")
        md.append(f"Regex: `{r['regex']}`  \nMatches: {r['total_matches']:,} — "
                  f"TRUE {r['true']:,} / FALSE {r['false']:,} / UNCLEAR {r['unclear']:,}\n\n")
        md.append("| Verdict | Interpretation of the matched form | n |\n|---|---|---:|\n")
        for b in r["buckets"]:
            md.append(f"| {b['verdict']} | {b['label']} | {b['n']:,} |\n")
        md.append("\n")

    if dead:
        md.append("## Probes that never fire\n\n")
        md.append("`phase1_templates.py` skips any probe with zero tablet hits (`if tablet_hits == 0: continue`), "
                  "so a probe whose regex does not match the corpus's transliteration conventions disappears from "
                  "`templates.json` without any warning. These probes produced **no matches at all**:\n\n")
        for d in dead:
            md.append(f"- `{d['probe']}` — regex `{d['regex']}`\n")
        md.append("\n")

    md.append("## Prevalence — attested is not the same as characteristic\n\n")
    md.append("Percentage of tablets **in each genre** carrying each pattern. A pattern can be real, "
              "well-attested, and still be far too rare to describe a genre's normal practice — which is a "
              "different claim from the one a reader takes away from 'administrative tablets close with a sum-total'.\n\n")
    md.append("| Pattern | " + " | ".join(genres) + " |\n|---|" + "---:|" * len(genres) + "\n")
    for label, r in prevalence.items():
        md.append(f"| {label} | " + " | ".join(f"{r['by_genre'][g]}%" for g in genres) + " |\n")
    md.append("\n**Read this table before citing any frequency from `templates.json`.**\n")

    (OUT / "probe_validation.md").write_text("".join(md), encoding="utf-8")
    (OUT / "probe_validation.json").write_text(
        json.dumps({"probes": results, "prevalence": prevalence, "never_fire": dead}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"[save] {OUT / 'probe_validation.md'}")


if __name__ == "__main__":
    main()
