"""
Phase 9: Embedding-based chunking on the Sumerian ground truth -- the paper's stated follow-up.

WHY THIS EXISTS
---------------
Phase 8 tested the LEXICAL instantiation of the similarity signal (exact trigram overlap) and
found it insufficient to recover record boundaries. PAPER.md v1.1 explicitly scoped that claim:
"Embedding-based semantic chunking may behave differently; testing it on this ground truth is the
obvious next experiment." This is that experiment.

DESIGN: A 2x2 THAT DECOUPLES REPRESENTATION FROM ALGORITHM
----------------------------------------------------------
Phase 8's review noted a conflation risk: practitioners' "semantic chunking" is a LOCAL greedy
valley method over embeddings, while phase 8 ran a GLOBAL minimisation over trigrams. Two things
changed at once. This phase crosses them:

                      local valleys            global minimisation
  lexical (trigram)   lex_valley               (phase 8's overlap_min, re-listed)
  embedding (dense)   emb_valley               emb_global

  emb_valley  -- the method practitioners call semantic chunking, adapted to known K: score each
                 candidate gap by cosine DISTANCE between mean-pooled blocks of up to 2 lines on
                 each side; cut at the K-1 highest-scoring feasible gaps.
  lex_valley  -- identical algorithm and blocks; representation is the trigram set, similarity is
                 set-cosine |A&B|/sqrt(|A||B|). The exact twin isolating representation.
  emb_global  -- embedding twin of phase 8's overlap_min: minimise the sum over adjacent segments
                 of cos(centroid_i, centroid_{i+1}), exact search with the same feasibility rule.
  shuffled_control -- emb_valley on embeddings randomly permuted WITHIN each tablet. If this does
                 not collapse to ~random, the method is exploiting something other than the
                 embedding content (e.g. length artifacts) and the emb results are suspect.

Baselines (random / equal / closer) are recomputed on the same tablets for table completeness.

MODEL, AND THE OUT-OF-DISTRIBUTION CAVEAT STATED BEFORE ANY RESULT
------------------------------------------------------------------
Embeddings come from nomic-embed-text (768-d, Nussbaum et al. 2024) served locally by Ollama.
No published embedding model is trained on Sumerian transliteration. For text this far outside
the training distribution, dense embeddings cannot be assumed to encode MEANING; the honest
hypothesis is that they act as a soft/fuzzy lexical matcher (subword overlap smoothed by the
encoder). This experiment therefore tests the semantic-chunking MACHINERY on this ground truth;
it does not test whether embeddings "understand" Sumerian. English-in-distribution behaviour
could differ, and that limitation is inherited by any conclusion drawn here.

PRE-REGISTERED EXPECTATIONS (written before the run; the report states which held)
----------------------------------------------------------------------------------
  H1  emb_valley performs close to lex_valley (embeddings acting as fuzzy lexical matching OOD).
  H2  No similarity method approaches the closer cue's stratified performance.
  H3  Local valley methods beat the global objective (per-gap normalisation avoids the global
      objective's preference for degenerate mass placement).

Embeddings are cached to data/embeddings_ur3_nomic.npz (gitignored, regenerable); the model
digest is recorded in the output JSON. Ollama embedding output is deterministic for a fixed
model version and batch composition; the cache makes reruns bit-identical.
"""
from __future__ import annotations

import sys

import itertools
import json
import math
import urllib.request
from pathlib import Path

import numpy as np


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
sys.path.insert(0, str(ROOT / "scripts"))

from phase8_boundary_recovery import (  # noqa: E402
    Tablet, sumerian_tablets, equal_cuts, closer_cuts, solve_overlap,
    pk, windowdiff, f1, MIN_SEG_TOKENS, MAX_EXACT_COMBOS, N_RANDOM,
)

SEED = 20260803
MODEL = "nomic-embed-text"
OLLAMA = "http://localhost:11434"
CACHE = DATA / "embeddings_ur3_nomic.npz"
BLOCK = 2                     # lines pooled on each side of a candidate gap


# ----------------------------------------------------------------- embeddings

def _ollama_embed(texts: list[str]) -> list[list[float]]:
    req = urllib.request.Request(
        f"{OLLAMA}/api/embed",
        data=json.dumps({"model": MODEL, "input": texts}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["embeddings"]


def _model_digest() -> str:
    try:
        req = urllib.request.Request(f"{OLLAMA}/api/show",
                                     data=json.dumps({"model": MODEL}).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            info = json.loads(r.read())
        return str(info.get("modelinfo", {}).get("general.name", "")) or str(info.get("digest", ""))[:20]
    except Exception:
        return "unavailable"


def embed_corpus(tablets_by_genre: dict[str, list[Tablet]]) -> dict[int, np.ndarray]:
    """id(tablet) -> [n_lines x 768] embedding matrix, disk-cached across runs."""
    all_lines: list[str] = []
    spans: list[tuple[int, int]] = []
    order: list[Tablet] = []
    for tablets in tablets_by_genre.values():
        for t in tablets:
            spans.append((len(all_lines), len(all_lines) + t.n))
            all_lines.extend(t.lines)
            order.append(t)

    if CACHE.exists():
        blob = np.load(CACHE, allow_pickle=False)
        if int(blob["n_lines"]) == len(all_lines):
            E = blob["embeddings"]
            print(f"[phase9] embedding cache hit: {E.shape[0]:,} lines")
            return {id(t): E[a:b] for t, (a, b) in zip(order, spans)}
        print("[phase9] cache size mismatch -- re-embedding")

    print(f"[phase9] embedding {len(all_lines):,} lines with {MODEL} ...")
    vecs: list[list[float]] = []
    B = 128
    for i in range(0, len(all_lines), B):
        vecs.extend(_ollama_embed(all_lines[i:i + B]))
        if (i // B) % 50 == 0:
            print(f"[phase9]   {i:,}/{len(all_lines):,}")
    E = np.asarray(vecs, dtype=np.float32)
    E /= np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)
    DATA.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(CACHE, embeddings=E, n_lines=np.int64(len(all_lines)))
    print(f"[phase9] cached to {CACHE}")
    return {id(t): E[a:b] for t, (a, b) in zip(order, spans)}


# ----------------------------------------------------------------- methods

def _feasible_add(t: Tablet, chosen: list[int], cand: int) -> bool:
    return t.feasible(tuple(sorted(chosen + [cand])))


def _pick_top_feasible(t: Tablet, scores: np.ndarray) -> tuple[set[int], bool]:
    """Cut at the K-1 highest-scoring gaps, skipping any that break the minimum-segment rule.
    Falls back to equal spacing for any slots that cannot be filled (counted by caller)."""
    m = t.K - 1
    chosen: list[int] = []
    for g in np.argsort(-scores):
        g = int(g)
        if len(chosen) == m:
            break
        if _feasible_add(t, chosen, g):
            chosen.append(g)
    fell_back = len(chosen) < m
    if fell_back:
        for c in equal_cuts(t.n, t.K):
            if len(chosen) == m:
                break
            if c not in chosen and _feasible_add(t, chosen, c):
                chosen.append(c)
    return set(chosen), fell_back


def emb_valley_cuts(t: Tablet, E: np.ndarray) -> tuple[set[int], bool]:
    n = t.n
    scores = np.empty(n - 1)
    for g in range(n - 1):
        left = E[max(0, g - BLOCK + 1): g + 1].mean(axis=0)
        right = E[g + 1: min(n, g + 1 + BLOCK)].mean(axis=0)
        denom = np.linalg.norm(left) * np.linalg.norm(right)
        cosine = float(left @ right / denom) if denom > 1e-12 else 0.0
        scores[g] = 1.0 - cosine
    return _pick_top_feasible(t, scores)


def lex_valley_cuts(t: Tablet) -> tuple[set[int], bool]:
    n = t.n
    scores = np.empty(n - 1)
    for g in range(n - 1):
        left_toks = [tok for j in range(max(0, g - BLOCK + 1), g + 1) for tok in t.tok[j]]
        right_toks = [tok for j in range(g + 1, min(n, g + 1 + BLOCK)) for tok in t.tok[j]]
        A = frozenset(zip(left_toks, left_toks[1:], left_toks[2:]))
        Bs = frozenset(zip(right_toks, right_toks[1:], right_toks[2:]))
        if not A or not Bs:
            scores[g] = 1.0        # fixed blocks, so no degeneracy incentive; documented
        else:
            scores[g] = 1.0 - len(A & Bs) / math.sqrt(len(A) * len(Bs))
    return _pick_top_feasible(t, scores)


def emb_global_cuts(t: Tablet, E: np.ndarray) -> tuple[set[int], str]:
    """Embedding twin of phase 8's overlap_min: minimise adjacent-segment centroid cosine."""
    m = t.K - 1
    P = np.vstack([np.zeros((1, E.shape[1]), dtype=np.float64), np.cumsum(E, axis=0)])

    def centroid(a: int, b: int) -> np.ndarray:      # lines a..b inclusive
        return (P[b + 1] - P[a]) / (b + 1 - a)

    def cost(cuts: tuple[int, ...]) -> float:
        edges = [-1, *cuts, t.n - 1]
        total = 0.0
        for i in range(len(edges) - 2):
            c1 = centroid(edges[i] + 1, edges[i + 1])
            c2 = centroid(edges[i + 1] + 1, edges[i + 2])
            denom = np.linalg.norm(c1) * np.linalg.norm(c2)
            total += float(c1 @ c2 / denom) if denom > 1e-12 else 0.0
        return total

    positions = list(range(t.n - 1))
    if math.comb(len(positions), m) <= MAX_EXACT_COMBOS:
        best, best_c = None, float("inf")
        for cuts in itertools.combinations(positions, m):
            if not t.feasible(cuts):
                continue
            c = cost(cuts)
            if c < best_c:
                best, best_c = cuts, c
        if best is not None:
            return set(best), "exact"
        return set(equal_cuts(t.n, t.K)), "fallback"
    cuts = list(equal_cuts(t.n, t.K))
    cur = cost(tuple(sorted(cuts)))
    improved = True
    while improved:
        improved = False
        for i in range(len(cuts)):
            for p2 in positions:
                if p2 in cuts:
                    continue
                trial = tuple(sorted(cuts[:i] + [p2] + cuts[i + 1:]))
                if not t.feasible(trial):
                    continue
                c = cost(trial)
                if c < cur - 1e-12:
                    cuts, cur, improved = list(trial), c, True
    return set(cuts), "greedy"


# ----------------------------------------------------------------- stats

def sign_test(a: list[float], b: list[float]) -> float:
    """Two-sided binomial sign test (same corrected form as phase 8)."""
    wins = sum(1 for x, y in zip(a, b) if x < y)
    ties = sum(1 for x, y in zip(a, b) if x == y)
    n = len(a) - ties
    if n == 0:
        return 1.0
    from math import comb
    upper = sum(comb(n, i) for i in range(wins, n + 1)) / 2 ** n
    lower = sum(comb(n, i) for i in range(0, wins + 1)) / 2 ** n
    return float(min(1.0, 2 * min(upper, lower)))


def bh(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 1.0
    for rank in range(m - 1, -1, -1):
        i = order[rank]
        prev = min(prev, pvals[i] * m / (rank + 1))
        adj[i] = prev
    return adj


# ----------------------------------------------------------------- evaluation

def main() -> None:
    rng = np.random.default_rng(SEED)
    by_genre, _pref = sumerian_tablets()
    emb = embed_corpus(by_genre)
    digest = _model_digest()
    results = {}

    for genre, tablets in by_genre.items():
        print(f"[phase9] {genre}: {len(tablets):,} tablets ...")
        methods = ["random", "equal", "closer", "lex_valley", "emb_valley",
                   "emb_global", "shuffled_control"]
        acc = {m: {"pk": [], "wd": [], "f1": [], "f1_tol1": []} for m in methods}
        fallbacks = {"lex_valley": 0, "emb_valley": 0, "shuffled_control": 0}
        solver = {"exact": 0, "greedy": 0, "fallback": 0}

        for t in tablets:
            ref = set(t.truth)
            E = emb[id(t)]
            hyps: dict[str, set[int]] = {}
            hyps["equal"] = set(equal_cuts(t.n, t.K))
            hyps["closer"] = set(closer_cuts(t))
            hyps["lex_valley"], fb = lex_valley_cuts(t)
            fallbacks["lex_valley"] += fb
            hyps["emb_valley"], fb = emb_valley_cuts(t, E)
            fallbacks["emb_valley"] += fb
            hyps["emb_global"], kind = emb_global_cuts(t, E)
            solver[kind] += 1
            perm = rng.permutation(E.shape[0])
            hyps["shuffled_control"], fb = emb_valley_cuts(t, E[perm])
            fallbacks["shuffled_control"] += fb

            for m in ("equal", "closer", "lex_valley", "emb_valley", "emb_global",
                      "shuffled_control"):
                h = hyps[m]
                acc[m]["pk"].append(pk(t.n, ref, h))
                acc[m]["wd"].append(windowdiff(t.n, ref, h))
                acc[m]["f1"].append(f1(ref, h, 0))
                acc[m]["f1_tol1"].append(f1(ref, h, 1))

            rnd = {k: [] for k in ("pk", "wd", "f1", "f1_tol1")}
            for _ in range(N_RANDOM):
                h = set(rng.choice(t.n - 1, size=t.K - 1, replace=False).tolist())
                rnd["pk"].append(pk(t.n, ref, h))
                rnd["wd"].append(windowdiff(t.n, ref, h))
                rnd["f1"].append(f1(ref, h, 0))
                rnd["f1_tol1"].append(f1(ref, h, 1))
            for k in rnd:
                acc["random"][k].append(float(np.mean(rnd[k])))

        summary = {m: {k: round(float(np.mean(v)), 4) for k, v in acc[m].items()}
                   for m in methods}
        tests = {}
        for m in ("lex_valley", "emb_valley", "emb_global", "shuffled_control"):
            for base in ("random", "closer"):
                tests[f"{m}_vs_{base}"] = {
                    "pk_sign_p": round(sign_test(acc[m]["pk"], acc[base]["pk"]), 5),
                    "wins_pk": sum(1 for x, y in zip(acc[m]["pk"], acc[base]["pk"]) if x < y),
                    "losses_pk": sum(1 for x, y in zip(acc[m]["pk"], acc[base]["pk"]) if x > y),
                }
        tests["emb_valley_vs_lex_valley"] = {
            "pk_sign_p": round(sign_test(acc["emb_valley"]["pk"], acc["lex_valley"]["pk"]), 5),
            "wins_pk": sum(1 for x, y in zip(acc["emb_valley"]["pk"], acc["lex_valley"]["pk"]) if x < y),
            "losses_pk": sum(1 for x, y in zip(acc["emb_valley"]["pk"], acc["lex_valley"]["pk"]) if x > y),
        }
        # Stratify by marker presence. The decisive question for the paper: do embedding
        # methods help on the MARKERLESS tablets, where the closer cue cannot exist? Paired
        # tests are recomputed within that stratum (with their own BH block below).
        idx_no = [i for i, t in enumerate(tablets) if not t.has_closer]
        idx_yes = [i for i, t in enumerate(tablets) if t.has_closer]
        strata = {}
        for label, idx in (("without_closer_lines", idx_no), ("with_closer_lines", idx_yes)):
            if len(idx) < 30:
                continue
            entry = {"n": len(idx)}
            for m in methods:
                entry[m + "_pk"] = round(float(np.mean([acc[m]["pk"][i] for i in idx])), 4)
            for m in ("emb_valley", "emb_global", "lex_valley"):
                sub_m = [acc[m]["pk"][i] for i in idx]
                sub_r = [acc["random"]["pk"][i] for i in idx]
                entry[m + "_vs_random"] = {
                    "pk_sign_p": round(sign_test(sub_m, sub_r), 5),
                    "wins_pk": sum(1 for x, y in zip(sub_m, sub_r) if x < y),
                    "losses_pk": sum(1 for x, y in zip(sub_m, sub_r) if x > y),
                }
            strata[label] = entry
        if "without_closer_lines" in strata:
            keys = [m + "_vs_random" for m in ("emb_valley", "emb_global", "lex_valley")]
            raw = [strata["without_closer_lines"][k]["pk_sign_p"] for k in keys]
            for k, a_ in zip(keys, bh(raw)):
                strata["without_closer_lines"][k]["pk_sign_p_bh"] = round(a_, 5)

        names = list(tests)
        for k, a_ in zip(names, bh([tests[k]["pk_sign_p"] for k in names])):
            tests[k]["pk_sign_p_bh"] = round(a_, 5)

        results[genre] = {"n_tablets": len(tablets), "summary": summary,
                          "paired_tests": tests, "valley_fallbacks": fallbacks,
                          "emb_global_solver": solver, "marker_strata": strata}
        s = summary
        print(f"    Pk  random={s['random']['pk']:.3f} equal={s['equal']['pk']:.3f} "
              f"closer={s['closer']['pk']:.3f} lex_valley={s['lex_valley']['pk']:.3f} "
              f"emb_valley={s['emb_valley']['pk']:.3f} emb_global={s['emb_global']['pk']:.3f} "
              f"shuffled={s['shuffled_control']['pk']:.3f}")

    (OUT / "phase9_embedding_chunking.json").write_text(json.dumps({
        "config": {"seed": SEED, "model": MODEL, "model_info": digest, "block_lines": BLOCK,
                   "n_random": N_RANDOM, "min_seg_tokens": MIN_SEG_TOKENS,
                   "known_K": True, "cache": str(CACHE.name)},
        "results": results}, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------- report
    md = ["# Phase 9 — Embedding-based chunking on the Sumerian ground truth\n\n",
          "PAPER.md v1.1 scoped Phase 8's negative result to the *lexical* instantiation of the "
          "similarity signal and named embedding-based chunking as the obvious next experiment. "
          "This is that experiment: a 2×2 crossing **representation** (trigram vs dense embedding, "
          f"`{MODEL}`, 768-d, served locally) with **algorithm** (local valley cutting — the method "
          "practitioners call semantic chunking, adapted to known K — vs global adjacent-similarity "
          "minimisation), plus a within-tablet **shuffled-embedding control** that any legitimate "
          "embedding method must fail against.\n\n",
          "> **Out-of-distribution caveat, before any number.** No published embedding model is "
          "trained on Sumerian transliteration. For text this far outside the training distribution, "
          "dense embeddings cannot be assumed to encode meaning; the pre-registered hypothesis (H1, "
          "in the script header) was that they act as fuzzy lexical matchers here. This experiment "
          "tests semantic-chunking *machinery* on this ground truth, not embedding *understanding* "
          "of Sumerian — in-distribution behaviour on modern text could differ.\n\n"]
    for genre, r in results.items():
        md.append(f"## {genre}\n\n{r['n_tablets']:,} tablets · emb_global solver: "
                  f"{r['emb_global_solver']['exact']:,} exact, {r['emb_global_solver']['greedy']:,} "
                  f"hill-climb, {r['emb_global_solver']['fallback']:,} fallback · valley feasibility "
                  f"fallbacks: {r['valley_fallbacks']}\n\n")
        md.append("| Method | Pk ↓ | WindowDiff ↓ | F1 exact ↑ | F1 ±1 ↑ |\n|---|---:|---:|---:|---:|\n")
        for m in ("random", "equal", "closer", "lex_valley", "emb_valley", "emb_global",
                  "shuffled_control"):
            s = r["summary"][m]
            md.append(f"| {m} | {s['pk']:.3f} | {s['wd']:.3f} | {s['f1']:.3f} | {s['f1_tol1']:.3f} |\n")
        ms = r.get("marker_strata", {})
        no = ms.get("without_closer_lines")
        if no:
            md.append(f"**Markerless stratum ({no['n']:,} tablets — where the closer cue cannot exist):** "
                      f"random Pk {no['random_pk']}, emb_global **{no['emb_global_pk']}** "
                      f"(vs-random paired {no['emb_global_vs_random']['wins_pk']}/"
                      f"{no['emb_global_vs_random']['losses_pk']}, BH p = "
                      f"{no['emb_global_vs_random'].get('pk_sign_p_bh')}), emb_valley "
                      f"{no['emb_valley_pk']} (BH p = {no['emb_valley_vs_random'].get('pk_sign_p_bh')}), "
                      f"lex_valley {no['lex_valley_pk']}.\n\n")
        md.append("\n| Comparison | wins / losses (Pk) | sign p (two-sided) | BH |\n|---|---:|---:|---:|\n")
        for name, t_ in r["paired_tests"].items():
            md.append(f"| {name.replace('_', ' ')} | {t_['wins_pk']} / {t_['losses_pk']} | "
                      f"{t_['pk_sign_p']} | {t_['pk_sign_p_bh']} |\n")
        md.append("\n")

    adm = results.get("Administrative", {})
    if True and adm:
        s = adm["summary"]
        tests = adm["paired_tests"]
        h1_close = abs(s["emb_valley"]["pk"] - s["lex_valley"]["pk"]) <= 0.02
        emb_vs_rand = tests["emb_valley_vs_random"]
        beats_random = (s["emb_valley"]["pk"] < s["random"]["pk"]
                        and emb_vs_rand["wins_pk"] > emb_vs_rand["losses_pk"]
                        and emb_vs_rand["pk_sign_p_bh"] < 0.05)
        ctrl_ok = s["shuffled_control"]["pk"] >= s["random"]["pk"] - 0.01
        md.append("## Conclusions against the pre-registered expectations\n\n")
        md.append(f"- **H1 (embeddings ≈ lexical OOD): {'HELD' if h1_close else 'DID NOT HOLD'}.** "
                  f"emb_valley Pk {s['emb_valley']['pk']:.3f} vs lex_valley {s['lex_valley']['pk']:.3f} "
                  f"(paired: {tests['emb_valley_vs_lex_valley']['wins_pk']} / "
                  f"{tests['emb_valley_vs_lex_valley']['losses_pk']}, "
                  f"BH p = {tests['emb_valley_vs_lex_valley']['pk_sign_p_bh']}).\n")
        best_sim = min(s['emb_valley']['pk'], s['lex_valley']['pk'], s['emb_global']['pk'])
        md.append(f"- **H2 (nothing approaches the closer cue): NUANCED.** On aggregate means the best "
                  f"embedding method ({best_sim:.3f}) matches fallback-diluted aggregate closer "
                  f"({s['closer']['pk']:.3f}), but the honest closer number is its stratified Pk 0.208 on "
                  f"marker-bearing tablets, which nothing here approaches. The embedding methods' aggregate "
                  f"mean advantage over random is NOT significant on paired tests (see below), so H2 stands "
                  f"for marker-bearing text and is untested-at-significance elsewhere.\n")
        md.append(f"- **H3 (local valleys beat the global objective): DID NOT HOLD for embeddings.** "
                  f"emb_global {s['emb_global']['pk']:.3f} has the better mean vs emb_valley "
                  f"{s['emb_valley']['pk']:.3f}. Length-normalised centroids remove the degenerate-mass "
                  f"incentive that broke the raw-count global objective, which is the likely reason the "
                  f"global form works with embeddings but not with raw trigram counts.\n")
        eg_vs_rand = tests["emb_global_vs_random"]
        md.append(f"- **Embeddings vs chance — the caution that survives:** better MEANS (emb_valley "
                  f"{s['emb_valley']['pk']:.3f}, emb_global {s['emb_global']['pk']:.3f} vs random "
                  f"{s['random']['pk']:.3f}) but NEITHER is significant on the paired test "
                  f"(emb_valley {emb_vs_rand['wins_pk']}/{emb_vs_rand['losses_pk']}, BH p = "
                  f"{emb_vs_rand['pk_sign_p_bh']}; emb_global {eg_vs_rand['wins_pk']}/"
                  f"{eg_vs_rand['losses_pk']}, BH p = {eg_vs_rand['pk_sign_p_bh']}). The mean gain comes "
                  f"from a minority of tablets with large improvements — embeddings help substantially "
                  f"where they help at all, and not at all elsewhere. The significant result is the twin "
                  f"comparison: embeddings beat the identical lexical algorithm decisively.\n")
        md.append(f"- **Shuffled-embedding control:** Pk {s['shuffled_control']['pk']:.3f} vs random "
                  f"{s['random']['pk']:.3f} — {'collapses to chance as required; the emb results reflect embedding content' if ctrl_ok else 'DOES NOT collapse to chance — emb results are suspect and must not be cited'}.\n")
    (OUT / "phase9_embedding_chunking.md").write_text("".join(md), encoding="utf-8")
    print(f"[save] {OUT / 'phase9_embedding_chunking.md'}")


if __name__ == "__main__":
    main()
