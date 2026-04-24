"""
kishib3 — Minimal Sumerian-style sealed write envelope.

Every state-changing call carries (payload, by_seal, witnesses, period_id).
Authority service mints, revokes, and verifies seals; revocation cascades to
filiation children; period_id pins each write to a named time period.

This is the reference *measurement* implementation, not production:
  - HMAC-SHA256 (stdlib only) instead of Ed25519 (no crypto deps)
  - In-memory stores instead of durable persistence
  - Single-process, no network

Production hardening would swap HMAC → Ed25519, dict → SQLite/Postgres,
and add rotation/expiry/scope checks. Capability semantics are identical.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field, asdict
from typing import Any


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Principal:
    id: str                           # e.g. "shulgi-ili"
    role: str                         # e.g. "scribe", "ensi", "lugal"
    parent_id: str | None = None      # filiation edge (dumu-of)


@dataclass
class Seal:
    id: str                           # opaque seal id
    principal_id: str
    secret: bytes                     # HMAC key (would be Ed25519 priv key in prod)
    valid_from: float                 # unix ts
    valid_to: float | None = None     # set on revocation


@dataclass(frozen=True)
class Period:
    id: str                           # e.g. "year-of-X"
    name: str                         # human-readable name
    start_ts: float


@dataclass(frozen=True)
class WriteEnvelope:
    """The Sumerian invariant: every state-changing call is sealed and dated."""
    seq: int
    payload: dict
    by_seal: str                      # seal id of author
    witnesses: tuple[str, ...]        # seal ids of live witnesses
    period_id: str
    written_at: float                 # unix ts
    signature: str                    # hex-encoded HMAC-SHA256

    def canonical_bytes(self) -> bytes:
        """Bytes used for signing/verifying. Order-stable JSON."""
        body = {
            "seq": self.seq,
            "payload": self.payload,
            "by_seal": self.by_seal,
            "witnesses": list(self.witnesses),
            "period_id": self.period_id,
            "written_at": self.written_at,
        }
        return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


# ---------------------------------------------------------------------------
# Authority service
# ---------------------------------------------------------------------------

class SealAuthority:
    """Manages principals, seals, revocation, verification."""

    def __init__(self) -> None:
        self.principals: dict[str, Principal] = {}
        self.seals: dict[str, Seal] = {}

    # -- registration ------------------------------------------------------

    def register_principal(self, p: Principal) -> None:
        if p.id in self.principals:
            raise ValueError(f"principal {p.id!r} already registered")
        if p.parent_id and p.parent_id not in self.principals:
            raise ValueError(f"parent {p.parent_id!r} unknown")
        self.principals[p.id] = p

    def mint_seal(self, principal_id: str, *, now: float | None = None) -> Seal:
        if principal_id not in self.principals:
            raise ValueError(f"principal {principal_id!r} unknown")
        s = Seal(
            id=secrets.token_hex(8),
            principal_id=principal_id,
            secret=secrets.token_bytes(32),
            valid_from=now if now is not None else time.time(),
        )
        self.seals[s.id] = s
        return s

    # -- revocation --------------------------------------------------------

    def revoke(self, seal_id: str, *, now: float | None = None) -> None:
        s = self.seals.get(seal_id)
        if s is None:
            raise ValueError(f"unknown seal {seal_id!r}")
        if s.valid_to is None:
            s.valid_to = now if now is not None else time.time()

    def revoke_principal_cascade(self, principal_id: str, *, now: float | None = None) -> int:
        """Revoke all seals belonging to principal_id and all descendant principals.
        Returns number of seals revoked. This is the kišib₃-cascade primitive."""
        ts = now if now is not None else time.time()
        descendants = self._descendants_inclusive(principal_id)
        revoked = 0
        for sid, seal in list(self.seals.items()):
            if seal.principal_id in descendants and seal.valid_to is None:
                seal.valid_to = ts
                revoked += 1
        return revoked

    def _descendants_inclusive(self, principal_id: str) -> set[str]:
        result = {principal_id}
        # walk filiation tree
        added = True
        while added:
            added = False
            for p in self.principals.values():
                if p.parent_id in result and p.id not in result:
                    result.add(p.id)
                    added = True
        return result

    # -- signing & verification -------------------------------------------

    def sign(self, seal_id: str, payload: bytes) -> str:
        s = self.seals[seal_id]
        return hmac.new(s.secret, payload, hashlib.sha256).hexdigest()

    def verify_seal_active_at(self, seal_id: str, ts: float) -> bool:
        s = self.seals.get(seal_id)
        if s is None:
            return False
        if ts < s.valid_from:
            return False
        if s.valid_to is not None and ts >= s.valid_to:
            return False
        return True

    def verify_envelope(self, env: WriteEnvelope, *, check_active_at: float | None = None) -> bool:
        """Verify signature + author seal active at write time + all witnesses
        active at write time. If check_active_at is given, additionally verify
        the seal is STILL active at that timestamp (revocation check)."""
        s = self.seals.get(env.by_seal)
        if s is None:
            return False
        expected = self.sign(env.by_seal, env.canonical_bytes())
        if not hmac.compare_digest(expected, env.signature):
            return False
        if not self.verify_seal_active_at(env.by_seal, env.written_at):
            return False
        for wid in env.witnesses:
            if not self.verify_seal_active_at(wid, env.written_at):
                return False
        if check_active_at is not None:
            if not self.verify_seal_active_at(env.by_seal, check_active_at):
                return False
        return True


# ---------------------------------------------------------------------------
# Period registry (year-name analog)
# ---------------------------------------------------------------------------

class PeriodRegistry:
    def __init__(self) -> None:
        self.periods: dict[str, Period] = {}

    def name_period(self, p: Period) -> None:
        if p.id in self.periods:
            raise ValueError(f"period {p.id!r} already named")
        self.periods[p.id] = p

    def get(self, period_id: str) -> Period:
        return self.periods[period_id]


# ---------------------------------------------------------------------------
# Sealed log — append-only ledger of envelopes
# ---------------------------------------------------------------------------

class SealedLog:
    """Append-only log. Every entry is a verified WriteEnvelope."""

    def __init__(self, authority: SealAuthority, periods: PeriodRegistry) -> None:
        self.authority = authority
        self.periods = periods
        self.entries: list[WriteEnvelope] = []
        self._next_seq = 0

    def post(
        self,
        payload: dict,
        *,
        by_seal: str,
        witnesses: tuple[str, ...] = (),
        period_id: str,
        now: float | None = None,
    ) -> WriteEnvelope:
        ts = now if now is not None else time.time()
        # Validate seal + witnesses + period before emitting envelope.
        if not self.authority.verify_seal_active_at(by_seal, ts):
            raise PermissionError(f"seal {by_seal!r} not active at {ts}")
        for wid in witnesses:
            if not self.authority.verify_seal_active_at(wid, ts):
                raise PermissionError(f"witness {wid!r} not active at {ts}")
        if period_id not in self.periods.periods:
            raise ValueError(f"unknown period {period_id!r}")
        env_unsigned = WriteEnvelope(
            seq=self._next_seq,
            payload=payload,
            by_seal=by_seal,
            witnesses=witnesses,
            period_id=period_id,
            written_at=ts,
            signature="",
        )
        sig = self.authority.sign(by_seal, env_unsigned.canonical_bytes())
        env = WriteEnvelope(
            seq=env_unsigned.seq,
            payload=env_unsigned.payload,
            by_seal=env_unsigned.by_seal,
            witnesses=env_unsigned.witnesses,
            period_id=env_unsigned.period_id,
            written_at=env_unsigned.written_at,
            signature=sig,
        )
        self.entries.append(env)
        self._next_seq += 1
        return env

    # -- the queries that distinguish sealed from anonymous logs -----------

    def who_wrote(self, seq: int) -> str | None:
        for e in self.entries:
            if e.seq == seq:
                return e.by_seal
        return None

    def writes_by_seal(self, seal_id: str) -> list[WriteEnvelope]:
        return [e for e in self.entries if e.by_seal == seal_id]

    def writes_in_period(self, period_id: str) -> list[WriteEnvelope]:
        return [e for e in self.entries if e.period_id == period_id]

    def replay_as_of(self, ts: float) -> list[WriteEnvelope]:
        """Return only the writes whose seals are STILL valid as of ts.
        This is the cascade-revocation invariant: revoking a parent invalidates
        every descendant write retroactively in the replay."""
        return [
            e for e in self.entries
            if e.written_at <= ts and self.authority.verify_envelope(e, check_active_at=ts)
        ]

    def verify_all(self) -> tuple[int, int]:
        """Returns (n_valid, n_total)."""
        n = 0
        for e in self.entries:
            if self.authority.verify_envelope(e):
                n += 1
        return n, len(self.entries)

    def serialize(self) -> bytes:
        """Wire-format size for overhead measurement."""
        return json.dumps([asdict(e) for e in self.entries], separators=(",", ":")).encode("utf-8")
