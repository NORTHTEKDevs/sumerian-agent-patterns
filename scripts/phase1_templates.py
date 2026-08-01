"""
Phase 1: Structural pattern extraction → outputs/templates.json

Approach:
  - Mine `transliteration` (semantic Sumerian morphemes) for opening/body/closing templates.
  - Use `glyph_names` for raw structural marker counts (SURFACE/COLUMN/RULING/BLANK_SPACE).
  - For each genre: top-N distinctive bigrams + trigrams via genre log-odds.
  - Hand-coded regex probes for known bureaucratic primitives (kišib, iti, mu, šu-nigin, etc.).
  - Every claim cites concrete tablet IDs.

Output:
  outputs/templates.json with templates[] = {
    genre, template_name, pattern, semantic_role, frequency,
    example_tablet_ids[], notes
  }
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

STRUCTURAL_TOKENS = ["<SURFACE>", "<COLUMN>", "<RULING>", "<BLANK_SPACE>", "<unk>"]

# Hand-coded regex probes for known Sumerian bureaucratic primitives.
# Each tuple: (template_name, regex_on_transliteration, semantic_role)
#
# KNOWN LIMITATIONS -- these have had NO specialist (Assyriological) review, and
# they produce the most-cited numbers in this repository. Audited 2026-07-31:
#
#   king_title   OVER-COUNTS BADLY. `\blugal\b` matches `lugal-...` as an element
#                of a PERSONAL NAME. In the Administrative sample 54% of matches
#                are personal names and only ~12% are plausibly the title "king",
#                so the reported 48.6% is not a rate of royal titles. Left in place
#                rather than silently patched: separating name from title needs
#                disambiguation regex cannot do. Do not cite this figure.
#
#   year_formula OVER-COUNTS MILDLY. `-` is a regex word boundary, so `\bmu\b`
#                matches inside `mu-DU` (delivery), `mu-ni` ("its name"), and
#                verbal prefixes. ~62% of matches are plausibly year formulae.
#                Tablet-level impact is small: a stricter probe gives 70.6% vs
#                the 74.2% reported, because a tablet with a spurious `mu-`
#                usually carries a real year formula too.
#
#   divine_name / temple_e2 / excess_diri carry the same class of risk and have
#                not been quantified. `e₂` is "house/household" generally, not
#                specifically "temple"; `diri` has senses beyond "excess".
#
# Spot-checked as exact: seal_of_PN (25.4% of Administrative),
# speak_to_him (58.8% of Letters). See CORRECTIONS.md.
PROBES: list[tuple[str, str, str]] = [
    ("seal_of_PN",         r"\bkišib(?:₃)?\b[^\n]{0,40}",               "identity / authentication"),
    ("month_marker",       r"\biti[\s\-][^\n]{0,30}",                    "temporal index (month)"),
    ("year_formula",       r"\bmu\b(?:[\s\-][^\n]{0,80})",               "temporal index (year-name)"),
    ("year_following",     r"\bmu\s+us₂-sa\b[^\n]{0,80}",                "derived year-name (relative date)"),
    ("received_by",        r"\bšu\s+ba-ti\b",                            "transaction confirmation"),
    ("via_witness",        r"\bg[iì]r[iì]?(?:₃)?[\s\-][^\n]{0,40}",      "intermediary / courier"),
    ("witness_eye",        r"\bigi[\s\-][^\n]{0,40}-š[èe]₃\b",           "witness presence (before X)"),
    ("total_audit",        r"\bšu-nigin₂?\b[^\n]{0,40}",                 "ledger total / audit line"),
    ("deficit_la2ia3",     r"\bla₂-ia₃\b[^\n]{0,40}",                    "deficit / arrears"),
    ("excess_diri",        r"\bdiri\b[^\n]{0,40}",                       "excess / surplus"),
    ("debit_zi_ga",        r"\bzi-ga\b[^\n]{0,40}",                      "expenditure / debit"),
    ("credit_mu_DU",       r"\bmu-DU\b[^\n]{0,40}",                      "delivery / credit"),
    ("son_of_PN",          r"\bdumu\b[\s\-][^\n]{0,40}",                 "filiation / lineage"),
    ("man_of_god",         r"\blu₂\{d\}[^\n]{0,30}",                     "personal name with divine theophoric"),
    ("divine_name",        r"\{d\}[a-zA-Z₀-₉\-]+",                       "divine determinative"),
    ("place_name",         r"\{ki\}",                                    "place determinative"),
    ("commodity_qty",      r"\d+\([a-zA-Z₀-₉]+\)\s+[a-zA-Z₀-₉\-{}]+",   "quantity + commodity (transaction line)"),
    ("king_title",         r"\blugal\b[^\n]{0,40}",                      "title: king"),
    ("ensi_title",         r"\bensi₂\b[^\n]{0,40}",                      "title: governor"),
    ("nita_kalag_ga",      r"\bnita\s+kalag-ga\b",                       "royal epithet: mighty male"),
    ("speak_to_him",       r"\bu₃-na-a-du₁₁\b",                          "letter address formula (RPC header)"),
    ("speak_to_PN_say",    r"\bu₃-na-de₃-tah\b",                         "letter speech act extension"),
    ("god_dedication",     r"\bnam-(ti|ki|en|lugal)\b",                  "dedicatory formula"),
    ("temple_e2",          r"\be₂[\s\-][^\n]{0,40}",                     "temple/household reference"),
]

NGRAM_MIN_FREQ_PER_GENRE = 5
TOP_NGRAMS_PER_GENRE = 30


def line_split(text: str) -> list[str]:
    return [ln.strip() for ln in str(text).split("\n") if ln.strip()]


def is_structural_marker(line: str) -> bool:
    return any(tok in line for tok in STRUCTURAL_TOKENS)


def tokenize_morphemes(line: str) -> list[str]:
    """Split a transliteration line into morpheme-like tokens.
    We keep multi-morpheme words intact (separated by '-') because they carry
    more semantic punch than individual morphemes for template detection.
    Strips numerical (n) markers like (diš), (geš₂) since those are syntactic noise.
    """
    if not line or is_structural_marker(line):
        return []
    line = re.sub(r"\d+\([a-zA-Z₀-₉]+\)", "<N>", line)
    return [t for t in line.split() if t and t != "<unk>"]


def all_ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def structural_stats(df: pd.DataFrame) -> dict:
    out = {}
    for g, sub in df.groupby("genre_primary"):
        n = len(sub)
        joined = "\n".join(sub["glyph_names"].astype(str))
        marker_counts = {tok: joined.count(tok) for tok in STRUCTURAL_TOKENS}
        # average lines (any kind) per tablet
        line_counts = sub["glyph_names"].astype(str).map(lambda s: len(s.split("\n")))
        # average glyphs between RULINGs (only meaningful if RULINGs exist)
        ruling_chunks = []
        for s in sub["glyph_names"].astype(str):
            chunks = re.split(r"<RULING>", s)
            for c in chunks:
                gc = sum(1 for ch in c if 0x12000 <= ord(ch) < 0x12480)
                if gc > 0:
                    ruling_chunks.append(gc)
        out[g] = {
            "n_tablets": int(n),
            "marker_counts": marker_counts,
            "marker_per_tablet": {k: round(v / n, 3) for k, v in marker_counts.items()},
            "mean_lines_per_tablet": round(float(line_counts.mean()), 2),
            "mean_glyphs_between_rulings": (
                round(sum(ruling_chunks) / len(ruling_chunks), 2) if ruling_chunks else None
            ),
            "ruling_chunk_count": len(ruling_chunks),
        }
    return out


def position_templates(df: pd.DataFrame, k_open: int = 3, k_close: int = 3) -> dict:
    """Per-genre top opening- and closing-line patterns (ignoring structural markers)."""
    out: dict[str, dict] = {}
    for g, sub in df.groupby("genre_primary"):
        opens = Counter()
        closes = Counter()
        opens_examples: dict[tuple, list[str]] = defaultdict(list)
        closes_examples: dict[tuple, list[str]] = defaultdict(list)
        for tid, txt in zip(sub["id"], sub["transliteration"].astype(str)):
            lines = [ln for ln in line_split(txt) if not is_structural_marker(ln)]
            if not lines:
                continue
            # collapse to morpheme tuples; use first-token-only as a coarse template
            open_sig = tuple(tokenize_morphemes(lines[0])[:3])
            close_sig = tuple(tokenize_morphemes(lines[-1])[:3])
            if open_sig:
                opens[open_sig] += 1
                if len(opens_examples[open_sig]) < 5:
                    opens_examples[open_sig].append(tid)
            if close_sig and close_sig != open_sig:
                closes[close_sig] += 1
                if len(closes_examples[close_sig]) < 5:
                    closes_examples[close_sig].append(tid)
        out[g] = {
            "top_openings": [
                {"signature": list(k), "count": v, "examples": opens_examples[k]}
                for k, v in opens.most_common(15)
            ],
            "top_closings": [
                {"signature": list(k), "count": v, "examples": closes_examples[k]}
                for k, v in closes.most_common(15)
            ],
        }
    return out


def distinctive_ngrams(df: pd.DataFrame, n: int) -> dict:
    """Per-genre log-odds-distinctive n-grams (vs all other genres)."""
    counts_per_genre: dict[str, Counter] = {}
    examples_per_genre: dict[str, dict[tuple, list[str]]] = {}
    for g, sub in df.groupby("genre_primary"):
        c = Counter()
        ex: dict[tuple, list[str]] = defaultdict(list)
        for tid, txt in zip(sub["id"], sub["transliteration"].astype(str)):
            for ln in line_split(txt):
                if is_structural_marker(ln):
                    continue
                toks = tokenize_morphemes(ln)
                for ng in all_ngrams(toks, n):
                    c[ng] += 1
                    if len(ex[ng]) < 5:
                        ex[ng].append(tid)
        counts_per_genre[g] = c
        examples_per_genre[g] = ex

    totals_per_genre = {g: sum(c.values()) for g, c in counts_per_genre.items()}

    out: dict[str, list[dict]] = {}
    for g, c in counts_per_genre.items():
        scored = []
        for ng, freq in c.items():
            if freq < NGRAM_MIN_FREQ_PER_GENRE:
                continue
            other_freq = sum(counts_per_genre[og].get(ng, 0) for og in counts_per_genre if og != g)
            other_total = sum(totals_per_genre[og] for og in totals_per_genre if og != g) or 1
            p_in = freq / max(totals_per_genre[g], 1)
            p_out = (other_freq + 1) / (other_total + 1)
            score = math.log(p_in / p_out)
            scored.append((ng, freq, other_freq, score))
        scored.sort(key=lambda x: x[3], reverse=True)
        out[g] = [
            {
                "ngram": list(ng),
                "freq_in_genre": int(f),
                "freq_in_other_genres": int(of),
                "log_odds": round(s, 3),
                "examples": examples_per_genre[g][ng],
            }
            for ng, f, of, s in scored[:TOP_NGRAMS_PER_GENRE]
        ]
    return out


def probe_hits(df: pd.DataFrame) -> list[dict]:
    """Run hand-coded probes for known bureaucratic primitives."""
    rows = []
    for g, sub in df.groupby("genre_primary"):
        n_tab = len(sub)
        for name, pat, role in PROBES:
            rx = re.compile(pat)
            tablet_hits = 0
            total_matches = 0
            examples: list[str] = []
            for tid, txt in zip(sub["id"], sub["transliteration"].astype(str)):
                m = rx.findall(txt)
                if m:
                    tablet_hits += 1
                    total_matches += len(m)
                    if len(examples) < 5:
                        examples.append(tid)
            if tablet_hits == 0:
                continue
            rows.append({
                "genre": g,
                "template_name": name,
                "pattern": pat,
                "semantic_role": role,
                "tablets_with_hit": tablet_hits,
                "tablet_coverage_pct": round(100 * tablet_hits / n_tab, 1),
                "total_matches": total_matches,
                "matches_per_tablet": round(total_matches / n_tab, 2),
                "example_tablet_ids": examples,
            })
    return rows


def main() -> None:
    df = pd.read_parquet(DATA / "sample_500.parquet")
    long_df = pd.read_parquet(DATA / "sample_long50.parquet")

    print(f"[load] sample_500 rows={len(df):,}  long50 rows={len(long_df):,}")

    structural = structural_stats(df)
    print("[done] structural stats")

    pos_templates = position_templates(df)
    print("[done] position templates")

    bigrams = distinctive_ngrams(df, 2)
    trigrams = distinctive_ngrams(df, 3)
    print("[done] distinctive n-grams (2 + 3)")

    probes = probe_hits(df)
    print(f"[done] probe hits — {len(probes)} (genre, template) rows")

    # Long-form supplementary: column/ruling density on top-quartile tablets.
    long_structural = structural_stats(long_df)
    print("[done] long-form structural stats")

    # Build the canonical templates[] list — combine probe hits + top distinctive n-grams.
    templates: list[dict] = []

    # 1. Probe-derived (high-confidence, semantically labeled).
    for r in probes:
        templates.append({
            "genre": r["genre"],
            "template_name": r["template_name"],
            "glyph_pattern": r["pattern"],
            "semantic_role": r["semantic_role"],
            "frequency": r["tablets_with_hit"],
            "tablet_coverage_pct": r["tablet_coverage_pct"],
            "matches_per_tablet": r["matches_per_tablet"],
            "example_tablet_ids": r["example_tablet_ids"],
            "source": "regex_probe",
        })

    # 2. Distinctive bigrams & trigrams per genre — top-10 each (the "discovered" templates).
    for g, items in bigrams.items():
        for i, it in enumerate(items[:10]):
            templates.append({
                "genre": g,
                "template_name": f"distinctive_bigram_{i+1}",
                "glyph_pattern": " ".join(it["ngram"]),
                "semantic_role": "discovered template (high genre log-odds)",
                "frequency": it["freq_in_genre"],
                "log_odds_vs_other_genres": it["log_odds"],
                "example_tablet_ids": it["examples"],
                "source": "distinctive_ngram",
            })
    for g, items in trigrams.items():
        for i, it in enumerate(items[:10]):
            templates.append({
                "genre": g,
                "template_name": f"distinctive_trigram_{i+1}",
                "glyph_pattern": " ".join(it["ngram"]),
                "semantic_role": "discovered template (high genre log-odds)",
                "frequency": it["freq_in_genre"],
                "log_odds_vs_other_genres": it["log_odds"],
                "example_tablet_ids": it["examples"],
                "source": "distinctive_ngram",
            })

    # 3. Position templates as named openers/closers.
    for g, pt in pos_templates.items():
        for i, it in enumerate(pt["top_openings"][:5]):
            templates.append({
                "genre": g,
                "template_name": f"opener_{i+1}",
                "glyph_pattern": " ".join(it["signature"]),
                "semantic_role": "opening-line template",
                "frequency": it["count"],
                "example_tablet_ids": it["examples"],
                "source": "position_template",
            })
        for i, it in enumerate(pt["top_closings"][:5]):
            templates.append({
                "genre": g,
                "template_name": f"closer_{i+1}",
                "glyph_pattern": " ".join(it["signature"]),
                "semantic_role": "closing-line template",
                "frequency": it["count"],
                "example_tablet_ids": it["examples"],
                "source": "position_template",
            })

    # 4. Structural-separator "templates" — describe the SURFACE/COLUMN/RULING role per genre.
    for g, s in structural.items():
        templates.append({
            "genre": g,
            "template_name": "structural_separators",
            "glyph_pattern": "<SURFACE> | <COLUMN> | <RULING> | <BLANK_SPACE>",
            "semantic_role": "physical-to-logical segmentation markers",
            "frequency": s["n_tablets"],
            "marker_per_tablet": s["marker_per_tablet"],
            "mean_lines_per_tablet": s["mean_lines_per_tablet"],
            "mean_glyphs_between_rulings": s["mean_glyphs_between_rulings"],
            "source": "structural_stats",
        })

    payload = {
        "meta": {
            "sample_size": int(len(df)),
            "long_form_size": int(len(long_df)),
            "genres": sorted(df["genre_primary"].unique().tolist()),
            "method": "transliteration n-grams + hand-coded probes + structural marker counts",
            "ngram_min_freq_per_genre": NGRAM_MIN_FREQ_PER_GENRE,
        },
        "structural_stats_per_genre": structural,
        "long_form_structural_stats_per_genre": long_structural,
        "position_templates_per_genre": pos_templates,
        "distinctive_bigrams_per_genre": bigrams,
        "distinctive_trigrams_per_genre": trigrams,
        "probe_hits": probes,
        "templates": templates,
    }

    out_path = OUT / "templates.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[save] {out_path}  templates={len(templates)}")

    # Quick stdout summary so the user can sanity-check.
    print("\n=== STRUCTURAL MARKER PER TABLET (sample) ===")
    for g, s in structural.items():
        print(f"  {g:18s} markers/tablet={s['marker_per_tablet']}")
    print("\n=== TOP PROBE HITS BY (genre, template) ===")
    top = sorted(probes, key=lambda r: -r["tablet_coverage_pct"])[:30]
    for r in top:
        print(f"  {r['genre']:18s} {r['template_name']:22s} {r['tablet_coverage_pct']:5.1f}% n={r['tablets_with_hit']}")


if __name__ == "__main__":
    main()
