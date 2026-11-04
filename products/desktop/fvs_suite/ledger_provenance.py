"""Bind LedgerDiff Lite report rows to two verified CSV source snapshots.

Digests identify exact imported bytes, not origin, authorship or audit approval.
Identical source bytes require human review even where amounts reconcile.
"""
from __future__ import annotations

import re

_SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
IDENTICAL_INPUT_REVIEW = "identical_source_bytes_review"


def attach_ledger_provenance(
    report_rows: list[dict[str, str]], *,
    left_sha256: str, right_sha256: str,
) -> list[dict[str, str]]:
    """Own plain-text report values before binding both source-byte identities.

    This direct API can be called without the validated CSV reader. A Python
    subclass may otherwise forge an apparent source fingerprint through
    equality hooks, or forge report columns via overridden mapping methods.
    Read native dictionary storage and reject executable/mutable report values
    rather than letting them reach an evidence-bearing CSV export. Imported
    ordinary strings, deterministic report schemas and monetary text are not
    changed. Original inputs and report rows are never edited.
    """
    for value in (left_sha256, right_sha256):
        if type(value) is not str or _SHA256.fullmatch(value) is None:
            raise ValueError("Ledger source SHA-256 must be canonical lowercase hex")
    if type(report_rows) is not list:
        raise ValueError("Ledger report rows must be a plain list")

    review = IDENTICAL_INPUT_REVIEW if left_sha256 == right_sha256 else ""
    result: list[dict[str, str]] = []
    for row in report_rows:
        if not isinstance(row, dict):
            raise ValueError("Ledger report row must be a record")
        # Avoid dict subclass .get/.items/.keys/__iter__/__getitem__ views.
        # Reject custom keys before reconstructing a dict, avoiding attacker
        # defined __hash__/__eq__ during reconstruction.
        if any(type(field) is not str for field in dict.keys(row)):
            raise ValueError("Ledger report field names must be plain text")
        owned = dict(dict.items(row))
        if any(type(value) is not str for value in owned.values()):
            raise ValueError("Ledger report field values must be plain text")
        owned.update(left_source_sha256=left_sha256,
                     right_source_sha256=right_sha256,
                     input_identity_review=review)
        result.append(owned)
    return result
