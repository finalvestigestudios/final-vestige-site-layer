"""Fail-closed semantic inspection of the *operator-side* issuance registry.

R14 validates SQLite schema, not row content. Run this guard *inside* the
existing BEGIN IMMEDIATE transaction and before any reservation/finalization.
This detects malformed state transitions, invalid SHA-256 values, accidental
record corruption and ambiguous reused fulfillment destinations. It is not a
MAC, an authenticated audit log, or protection from coherent database replay.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import datetime

_IDENTIFIER = re.compile(r"[A-Za-z0-9_-]{4,64}\Z", flags=re.ASCII)
_SHA256 = re.compile(r"[0-9a-f]{64}\Z", flags=re.ASCII)
_PRODUCTS = frozenset({"grants", "procurement"})


class RegistryRowError(ValueError):
    """The issuance ledger contains an invalid or ambiguous record."""


def _identifier(value: object) -> bool:
    return isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None


def _sha(value: object) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        stamp = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None
    return stamp if stamp.strftime("%Y-%m-%dT%H:%M:%SZ") == value else None


def enforce_registry_rows(db: sqlite3.Connection) -> None:
    """Reject any invalid registry row before a new signed license can issue.

    The caller MUST first enforce the exact R14 schema and hold BEGIN IMMEDIATE.
    Validation intentionally scans all rows. The registry is an operator-side
    database, not a customer-scale online entitlement service.
    """
    io_fault = False
    try:
        rows = db.execute(
            "SELECT license_id,product,kid,output_path_sha256,state,"
            "license_sha256,reserved_at,issued_at FROM issuance ORDER BY license_id"
        )
        seen_paths: set[str] = set()
        for license_id, product, kid, path_hash, state, digest, reserved, issued in rows:
            if (
                not _identifier(license_id)
                or product not in _PRODUCTS
                or not _identifier(kid)
                or not _sha(path_hash)
                or path_hash in seen_paths
            ):
                raise RegistryRowError("Unsafe issuance metadata or duplicate output destination")
            seen_paths.add(path_hash)
            reservation_time = _timestamp(reserved)
            if reservation_time is None:
                raise RegistryRowError("Invalid issuance reservation timestamp")
            if state == "reserved":
                if digest is not None or issued is not None:
                    raise RegistryRowError("Reserved issuance has an unexpected finalization marker")
            elif state == "issued":
                issued_time = _timestamp(issued)
                if not _sha(digest) or issued_time is None or issued_time < reservation_time:
                    raise RegistryRowError("Issued record has invalid digest or chronology")
            else:
                raise RegistryRowError("Unknown issuance state")
    except sqlite3.Error:
        io_fault = True
    # Do not carry underlying private SQLite failure text in an exception chain.
    if io_fault:
        raise RegistryRowError("Unable to inspect issuance registry rows")
