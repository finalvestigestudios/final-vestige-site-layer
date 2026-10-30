"""Bind LedgerDiff Lite report rows to the two imported CSV snapshots.

Hashes identify exact bytes, not authorship, audit approval, or independent
origination. Equal input bytes require human review, even if totals match.
"""
from __future__ import annotations

import re

_SHA256 = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
IDENTICAL_INPUT_REVIEW = "identical_source_bytes_review"


def attach_ledger_provenance(
    report_rows: list[dict[str, str]], *,
    left_sha256: str, right_sha256: str,
) -> list[dict[str, str]]:
    """Return an independent report copy with exact per-side source identity.

    Both fingerprints must come from the same descriptor-verified CSV snapshots
    that supplied the matching rows; never reopen input paths just to hash.
    A byte-identical pair is NOT proof that data are independent exports.
    Validate even header-only reports, where no row can carry the digests.
    """
    for value in (left_sha256, right_sha256):
        if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
            raise ValueError("Ledger source SHA-256 must be canonical lowercase hex")
    review = IDENTICAL_INPUT_REVIEW if left_sha256 == right_sha256 else ""
    return [
        {
            **row,
            "left_source_sha256": left_sha256,
            "right_source_sha256": right_sha256,
            "input_identity_review": review,
        }
        for row in report_rows
    ]
