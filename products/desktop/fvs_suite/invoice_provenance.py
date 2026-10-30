"""Stable, local-only evidence identifiers for Invoice Twin Scout review rows.

A source SHA-256 identifies the bytes actually imported, not the origin or
truth of an invoice. Candidate IDs bind two physical CSV lines and their
review classification to that source snapshot; no approval is inferred.
"""
from __future__ import annotations

import hashlib
import json
import re

_SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_PHYSICAL_LINE = re.compile(r"[1-9][0-9]*\Z", re.ASCII)
_CANDIDATE_KINDS = frozenset(("exact_invoice_key", "review_possible_duplicate"))
_DOMAIN = b"final-vestige-invoice-candidate-v1\0"


def attach_invoice_provenance(
    report_rows: list[dict[str, str]], *, source_sha256: str,
) -> list[dict[str, str]]:
    """Return copied candidate rows with a byte-snapshot SHA and stable ID.

    Uses CSV physical line numbers from the verified source snapshot. An ID
    is a deterministic locator, NOT a signature or fraud/compliance finding.
    An empty report remains empty; still validate the supplied digest.
    """
    if not isinstance(source_sha256, str) or not _SHA256.fullmatch(source_sha256):
        raise ValueError("Invoice source SHA-256 must be canonical lowercase hex")
    result = []
    seen: set[str] = set()
    for row in report_rows:
        if not isinstance(row, dict):
            raise ValueError("Invoice candidate must be a report record")
        a, b, status = row.get("row_a"), row.get("row_b"), row.get("status")
        if (not isinstance(a, str) or not _PHYSICAL_LINE.fullmatch(a)
                or int(a) < 2 or not isinstance(b, str)
                or not _PHYSICAL_LINE.fullmatch(b) or int(b) < 2 or a == b):
            raise ValueError("Invoice candidate requires two distinct physical CSV rows")
        if status not in _CANDIDATE_KINDS:
            raise ValueError("Invoice candidate has an unsupported review classification")
        locator = json.dumps(
            {"row_a": a, "row_b": b, "status": status},
            sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        ).encode("ascii")
        fingerprint = hashlib.sha256(
            _DOMAIN + bytes.fromhex(source_sha256) + b"\0" + locator
        ).hexdigest()
        if fingerprint in seen:
            raise ValueError("Duplicate invoice candidate identifier; no report was saved")
        seen.add(fingerprint)
        result.append({**row, "source_sha256": source_sha256,
                       "candidate_ref": fingerprint})
    return result
