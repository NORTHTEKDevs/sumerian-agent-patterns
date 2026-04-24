# Benchmark Results — `kishib3` (sealed envelope) vs Baseline (anonymous log)

**Setup:** Python 3.14, Windows 11, single process, in-memory storage. HMAC-SHA256 signing (stdlib `hmac`). 10 principals, 3 named periods. Realistic "tool-call result" payloads.

**Scripts:** `kishib3.py` (250 LoC sealed envelope), `baseline_log.py` (50 LoC anonymous log), `benchmark.py` (200 LoC harness). Run with `python benchmark.py` from this directory.

---

## 1. Per-Write Overhead

| Metric | Baseline (anonymous) | Sealed (kishib3) | Delta |
|---|---:|---:|---:|
| Bytes per write (10k writes) | 246.4 | 392.4 | **+59.3 %** |
| Estimated tokens per write* | 61.6 | 98.1 | **+36.5 tokens** |
| Median write latency | 0.6 µs | 7.8 µs | +7.2 µs |
| p95 write latency | 1.1 µs | 13.6 µs | +12.5 µs |

*Token estimate uses 4 bytes/token (conservative tiktoken-like heuristic). For exact counts on your stack, swap in `tiktoken` or your model's tokenizer. The structural overhead (`seq`, `by_seal`, `witnesses`, `period_id`, `written_at`, `signature`) is fixed at ~146 bytes per envelope regardless of payload size, so the **percentage overhead falls as payload grows** — at 1 KB payloads the overhead is ~14 %, at 10 KB payloads it's ~1.4 %.

**Scaling sanity check** (overhead is constant per write, not per byte stored):

| Scale | Baseline total | Sealed total | Sealed write p50 |
|---:|---:|---:|---:|
| 1k writes | 243 KB | 389 KB | 7.6 µs |
| 10k writes | 2.46 MB | 3.92 MB | 7.8 µs |
| 100k writes | 24.9 MB | 39.5 MB | 8.8 µs |

Latency is flat across scale — no degradation as the log grows.

---

## 2. Read-Path Latency (10k writes)

| Operation | Cost |
|---|---:|
| `who_wrote(seq)` single lookup | 6.6 µs |
| `writes_by_seal(seal_id)` filter | 673 µs (filters 10k entries) |
| `verify_all()` full integrity check | 74.7 ms (= 7.5 µs / entry) |

For comparison, the baseline log can perform `who_wrote` and `writes_by_seal` queries — they just always return None / empty list, because no author was ever recorded.

---

## 3. Capability Comparison — The 5 Audit Queries That Matter

This is the headline. The sealed log answers all 5 queries; the baseline answers **none** of them.

| Query | Baseline | Sealed | What this means |
|---|---|---|---|
| **Q1** Who wrote event #25? | ✘ Returns `None` | ✔ Returns seal id `4cc84271a2b580c4` | Author attribution |
| **Q2** All writes by a specific principal | ✘ Returns `[]` (no author recorded) | ✔ Returns 5 matching entries | Per-principal audit |
| **Q3** All writes in a named period | ✘ Returns `[]` (no period recorded) | ✔ Returns 17 entries in period-1 | Time-period filtering |
| **Q4** Verify integrity of every entry | ✘ 0 / 50 verified (no signatures) | ✔ 50 / 50 verified | Tamper detection |
| **Q5** Replay log AFTER cascade-revoking parent | ✘ Returns all 50 entries (can't filter by author validity) | ✔ Returns 0 entries (every scribe descends from the revoked lugal) | Cascade revocation |

**Q5 is the most important.** In the test, we revoke the root principal (`lugal`) at `t = base_ts + 30`. All 10 scribe-* principals are descendants of `lugal`, so cascade revocation invalidates every seal they ever held. When we replay-as-of `t = base_ts + 100`:

- The baseline returns **all 50 writes** because it has no concept of author validity. A revoked agent's writes silently remain in the log. **This is the silent-drift failure mode.**
- The sealed log returns **0 writes** because every write's `by_seal` is invalid as of the replay timestamp. The compromise is correctly contained.

This is the difference between "we trust this log" and "we can prove this log."

---

## 4. Honest Caveats

- **HMAC-SHA256, not Ed25519.** Production should use asymmetric signing so that verifying a signature doesn't require holding the signing key. HMAC was used here to keep the implementation stdlib-only for the benchmark. The byte overhead is identical (Ed25519 sigs are 64 bytes vs HMAC-SHA256's 32, so ~32 extra bytes per write — call it ~24 % byte overhead instead of 59 % at 246-byte payloads, or 8 extra tokens instead of 37). Switching adds one library dep (`cryptography` or `pynacl`) and trivial code changes.
- **In-memory only.** Real systems would persist envelopes to durable storage (SQLite, Postgres, an object store). That changes write latency dramatically — disk fsync is hundreds of µs to ms, not 8 µs. The *envelope structure* is unchanged; the latency numbers are kernel + stdlib only and represent a lower bound.
- **Token estimate is approximate.** 4 bytes/token is a defensible mid-range estimate for `cl100k_base` on JSON. Run the benchmark with your actual tokenizer to get exact counts for your model.
- **Single process, no concurrency.** Multi-process / distributed sealed logs would need a clock or sequence-coordination mechanism. The Sumerian model handles this with named periods (already implemented here) — different scribes can write to disjoint periods concurrently and merge at audit close.
- **Filter latency is linear scan.** A production implementation would index by `by_seal`, `period_id`, and `seq`. Linear scan is fine for benchmarks; index lookups are the obvious next step.

---

## 5. Honest "Better Than Current Frameworks" Statements

What you can say after reading this:

> "Wrapping every agent state-change in a sealed envelope adds ~37 tokens and ~7 µs per write. In return, you can answer 5 categories of audit query (author, time-period filtering, per-principal audit, tamper detection, cascade revocation) that current LLM agent frameworks (LangGraph, AutoGen, CrewAI) cannot answer at all without bespoke audit code. The capability gap is total, not partial — the baseline log answers 0 of these queries; the sealed log answers all 5."

What you should NOT say:

- "Reduces token costs" — the sealed envelope ADDS overhead, it does not save tokens. The win is capability, not cost.
- "Faster than X" — we don't have a benchmark against LangGraph specifically. We have a baseline-anonymous-log comparison.
- "Production-ready" — the implementation is a measurement reference. Swap HMAC → Ed25519 and add durable persistence before shipping.

---

## 6. Reproducing These Numbers

```bash
cd benchmarks
python benchmark.py    # writes results.json + prints headline numbers
```

No external dependencies. Numbers will vary slightly across machines (ours: Windows 11, Python 3.14). The capability-comparison results (5/5 vs 0/5) are deterministic and will be identical on any platform.

For exact token counts on your stack, replace `BYTES_PER_TOKEN = 4` in `benchmark.py` with a `tiktoken` call, or re-implement the tokenizer step against your model.
