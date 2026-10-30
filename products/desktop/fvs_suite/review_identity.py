"""Privacy-preserving identity gate for a reviewer-selected premium report.

The optional expected fingerprint is supplied by a trusted, already validated
review selection. This is not authentication and does not protect a source file
from modifications that occur after a final consistency check.
"""
from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path

from .journal_io import read_regular_bytes

_HEX = frozenset("0123456789abcdef")


def require_snapshot_match(expected_report_sha256: str | None,
                           observed_report_sha256: str) -> None:
    """Refuse an observed report different from the one shown to the reviewer.

    ``None`` preserves legacy direct API callers, which must still satisfy the
    underlying source/journal consistency rules. The premium GUI always passes
    its selected 64-character lowercase SHA-256 digest. Errors never interpolate
    a user-controlled path, CSV value, or digest.
    """
    if expected_report_sha256 is None:
        return
    if (type(expected_report_sha256) is not str
            or len(expected_report_sha256) != 64
            or any(char not in _HEX for char in expected_report_sha256)):
        raise ValueError("Loaded report fingerprint is invalid; reopen the report")
    if (type(observed_report_sha256) is not str
            or len(observed_report_sha256) != 64
            or any(char not in _HEX for char in observed_report_sha256)):
        raise ValueError("Current report fingerprint is invalid; reopen the report")
    if not hmac.compare_digest(expected_report_sha256, observed_report_sha256):
        raise ValueError("Source report changed since it was opened; reopen before exporting or sealing")


def journal_snapshot_identity(journal: str | Path) -> str:
    """Fingerprint descriptor-verified journal bytes, or its genuine absence.

    The identity distinguishes an absent journal from an empty existing file.
    This detects observed concurrent changes, not malicious re-hashing or
    reviewer authenticity; no customer content or path appears in errors.
    """
    from .exception_review import MAX_JOURNAL_BYTES

    path = Path(journal)
    try:
        os.lstat(path)
    except FileNotFoundError:
        return "absent"
    # Once present, disappearance during the bounded descriptor read is an
    # error, NOT another acceptable absent snapshot.
    data = read_regular_bytes(path, MAX_JOURNAL_BYTES, "Review journal")
    return "sha256:" + hashlib.sha256(data).hexdigest()
