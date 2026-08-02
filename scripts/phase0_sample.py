"""
Phase 0: Load SumTablets corpus, persist to parquet, build stratified samples.

Outputs:
  data/sumtablets.parquet       full corpus
  data/sample_500.parquet       500/genre stratified sample (5 target genres)
  data/sample_long50.parquet    50 long-form (>500 cuneiform glyphs) per genre
  data/genre_distribution.csv   full corpus genre × period counts
"""
from __future__ import annotations

import sys

import re
from pathlib import Path

import pandas as pd
from datasets import load_dataset

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
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

TARGET_GENRES = ["Administrative", "Literary", "Lexical", "Royal Inscription", "Letter"]
# Adaptive long-form threshold per genre — Letters/Lexical are inherently short.
# Use absolute >500 where the genre supports it, otherwise top-quartile by glyph count.
LONG_MIN = 500
SPECIAL_TOKENS = {"<SURFACE>", "<COLUMN>", "<BLANK_SPACE>", "<RULING>", "<unk>"}
TOKEN_RE = re.compile(r"<[A-Z_]+>")
CUNEIFORM_RANGE = range(0x12000, 0x12480)  # Unicode Cuneiform block


def cuneiform_glyph_count(s: str) -> int:
    if not isinstance(s, str):
        return 0
    stripped = TOKEN_RE.sub("", s)
    return sum(1 for ch in stripped if ord(ch) in CUNEIFORM_RANGE)


def main() -> None:
    parquet_path = DATA / "sumtablets.parquet"
    if parquet_path.exists():
        print(f"[load] reusing cached parquet: {parquet_path}")
        df = pd.read_parquet(parquet_path)
    else:
        print("[load] downloading SumTablets (train+validation+test) ...")
        frames = []
        for split in ("train", "validation", "test"):
            ds = load_dataset("colesimmons/sumtablets", split=split)
            frames.append(ds.to_pandas().assign(split=split))
        df = pd.concat(frames, ignore_index=True)
        df.to_parquet(parquet_path, index=False)
        print(f"[load] persisted {len(df):,} rows to {parquet_path}")

    print(f"[shape] rows={len(df):,}  cols={list(df.columns)}")

    df["glyph_count"] = df["glyphs"].map(cuneiform_glyph_count)

    # Genre normalization: take the first label if comma-separated; trim whitespace.
    df["genre_primary"] = (
        df["genre"].fillna("Unknown").astype(str).str.split(",").str[0].str.strip()
    )

    dist = (
        df.groupby(["genre_primary", "period"], dropna=False)
        .size()
        .reset_index(name="n")
        .sort_values("n", ascending=False)
    )
    dist.to_csv(DATA / "genre_distribution.csv", index=False)
    print(f"[dist] top-10 genre×period:\n{dist.head(10).to_string(index=False)}")

    rng = 42
    samples = []
    for g in TARGET_GENRES:
        sub = df[df["genre_primary"] == g]
        if len(sub) == 0:
            print(f"[warn] no rows for genre={g!r} — skipping")
            continue
        n = min(500, len(sub))
        samples.append(sub.sample(n=n, random_state=rng))
        print(f"[sample] {g}: pulled {n} of {len(sub):,}")

    sample_500 = pd.concat(samples, ignore_index=True)
    sample_500.to_parquet(DATA / "sample_500.parquet", index=False)
    print(f"[save] sample_500.parquet rows={len(sample_500):,}")

    long_samples = []
    for g in TARGET_GENRES:
        genre_rows = df[df["genre_primary"] == g]
        if len(genre_rows) == 0:
            print(f"[warn] no rows for long-form genre={g!r}")
            continue
        # Try absolute threshold first; fall back to top-quartile if too few.
        sub = genre_rows[genre_rows["glyph_count"] > LONG_MIN]
        threshold_used = LONG_MIN
        if len(sub) < 25:
            q75 = genre_rows["glyph_count"].quantile(0.75)
            sub = genre_rows[genre_rows["glyph_count"] >= q75]
            threshold_used = f"top-quartile (>= {q75:.0f})"
        n = min(50, len(sub))
        long_samples.append(sub.sample(n=n, random_state=rng))
        print(f"[sample-long] {g}: pulled {n} of {len(sub):,} (threshold={threshold_used})")

    if long_samples:
        sample_long = pd.concat(long_samples, ignore_index=True)
        sample_long.to_parquet(DATA / "sample_long50.parquet", index=False)
        print(f"[save] sample_long50.parquet rows={len(sample_long):,}")


if __name__ == "__main__":
    main()
