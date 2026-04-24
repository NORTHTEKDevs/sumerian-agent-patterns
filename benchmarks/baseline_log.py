"""
baseline_log — The "what most LLM agent frameworks do today" comparison.

A flat append-only event log with no author identity, no signing, no period
binding, no witness set. Mirrors the typical pattern in LangGraph / AutoGen /
CrewAI where agent state changes are stored as plain dicts indexed by sequence.

Used as the comparison point for kishib3.py overhead and capability benchmarks.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class AnonymousEvent:
    seq: int
    payload: dict
    written_at: float


class AnonymousLog:
    def __init__(self) -> None:
        self.entries: list[AnonymousEvent] = []
        self._next_seq = 0

    def post(self, payload: dict, *, now: float | None = None) -> AnonymousEvent:
        ts = now if now is not None else time.time()
        e = AnonymousEvent(seq=self._next_seq, payload=payload, written_at=ts)
        self.entries.append(e)
        self._next_seq += 1
        return e

    # -- the queries we will compare against the sealed log ---------------

    def who_wrote(self, seq: int) -> None:
        # Cannot answer — no author was ever recorded.
        return None

    def writes_by_seal(self, seal_id: str) -> list[AnonymousEvent]:
        # Cannot filter by author — no author is recorded.
        return []

    def writes_in_period(self, period_id: str) -> list[AnonymousEvent]:
        # Cannot answer — no period was ever recorded.
        return []

    def replay_as_of(self, ts: float) -> list[AnonymousEvent]:
        # Best the baseline can do: filter by timestamp. Cannot exclude
        # writes whose author was later revoked, because there is no author.
        return [e for e in self.entries if e.written_at <= ts]

    def verify_all(self) -> tuple[int, int]:
        # No signatures → cannot verify integrity. Returns (0, n) by convention.
        return 0, len(self.entries)

    def serialize(self) -> bytes:
        return json.dumps([asdict(e) for e in self.entries], separators=(",", ":")).encode("utf-8")
