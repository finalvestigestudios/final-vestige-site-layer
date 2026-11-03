"""Stable, local-only evidence identifiers for Invoice Twin Scout review rows.

A source SHA-256 identifies the bytes actually imported, not the origin or
truth of an invoice. Candidate IDs bind two physical CSV lines and their
review classification to that source snapshot; no approval is inferred.
"""
from __future__ import annotations

import hashlib
import json
import re

from .invoice_match import MAX_CANDIDATES

_SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_PHYSICAL_LINE = re.compile(r"[1-9][0-9]{0,9}\Z", re.ASCII)
_CANDIDATE_KINDS = frozenset(("exact_invoice_key", "review_possible_duplicate"))
_DOMAIN = b"final-vestige-invoice-candidate-v1\0"


def attach_invoice_provenance(
    report_rows: list[dict[str, str]], *, source_sha256: str,
) -> list[dict[str, str]]:
    """Return copied candidate rows with a byte-snapshot SHA and stable ID.

    Uses CSV physical line numbers from the verified source snapshot. An ID
    is a deterministic locator, NOT a signature or fraud/compliance finding.
    An empty report remains empty; still validate the supplied digest.
    Direct API source records are copied from native dictionary storage and
    must use exact built-in audit identity types, never subclassed views.
    """
    if type(source_sha256) is not str or not _SHA256.fullmatch(source_sha256):
        raise ValueError("Invoice source SHA-256 must be canonical lowercase hex")
    if type(report_rows) is not list:
        raise ValueError("Invoice candidate report must be a list")
    if len(report_rows) > MAX_CANDIDATES:
        raise ValueError("Too many invoice review candidates; no report was saved")
    result = []
    seen: set[str] = set()
    # An unordered physical-row pair has ONE review classification per report.
    # Including status in this key would allow contradictory exact/near labels
    # for the same two source rows, each with a plausible candidate_ref.
    seen_pairs: set[frozenset[str]] = set()
    for row in report_rows:
        if not isinstance(row, dict):
            raise ValueError("Invoice candidate must be a report record")
        # A direct API caller can supply a dict subclass whose get(), items(),
        # keys(), __iter__() or __getitem__() manufactures a benign view.
        # Inspect real storage through built-in descriptors before copying; this
        # is the same source-custody rule enforced before candidate discovery.
        # Subclassed str field names can forge hash/equality with "row_a".
        if any(type(field) is not str for field in dict.keys(row)):
            raise ValueError("Invoice candidate field names must be plain text")
        row = dict(dict.items(row))
        a, b, status = row.get("row_a"), row.get("row_b"), row.get("status")
        if (type(a) is not str or not _PHYSICAL_LINE.fullmatch(a)
                or int(a) < 2 or type(b) is not str
                or not _PHYSICAL_LINE.fullmatch(b) or int(b) < 2 or a == b):
            raise ValueError("Invoice candidate requires two distinct physical CSV rows")
        if type(status) is not str or status not in _CANDIDATE_KINDS:
            raise ValueError("Invoice candidate has an unsupported review classification")
        unordered = frozenset((a, b))
        if unordered in seen_pairs:
            raise ValueError("Duplicate invoice candidate pair; no report was saved")
        seen_pairs.add(unordered)
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
