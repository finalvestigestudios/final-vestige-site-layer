"""Canonical source-group inputs for SpendMap Lite membership fingerprints.

A group fingerprint is navigation evidence, not a signature. Callers must not
forge its vendor/month identity or physical source membership through Python
subclasses, noncanonical line order or duplicate source coordinates.
"""
from __future__ import annotations

import re

from .spend_source_digest_r426 import require_native_spend_source_sha256

_VENDOR = re.compile(r"[A-Z0-9]+\Z", re.ASCII)
_MONTH = re.compile(r"(?!0{1,4}-)[0-9]{1,4}-(?:0[1-9]|1[0-2])\Z", re.ASCII)
MAX_GROUP_ROWS = 200_000
MAX_VENDOR_KEY_CHARS = 1_048_576
MAX_PHYSICAL_ROW = 9_999_999_999
_ERROR = "Invalid SpendMap vendor/month source-group evidence"


def checked_spend_group_evidence(source_sha256: object, vendor: object,
                                 month: object, ordered_lines: object
                                 ) -> tuple[str, str, str, tuple[int, ...]]:
    """Own and validate all domain-separated digest inputs before hashing.

    The production summarizer already validates its source records. This
    independent direct-helper boundary prevents forged or silently reordered
    evidence if the helper is called outside the summarizer.
    """
    source_sha256 = require_native_spend_source_sha256(source_sha256)
    if (type(vendor) is not str or not 1 <= len(vendor) <= MAX_VENDOR_KEY_CHARS
            or _VENDOR.fullmatch(vendor) is None
            or type(month) is not str or _MONTH.fullmatch(month) is None
            or type(ordered_lines) is not list
            or not 1 <= len(ordered_lines) <= MAX_GROUP_ROWS):
        raise ValueError(_ERROR)
    lines = tuple(ordered_lines)
    previous = 1
    for line in lines:
        if (type(line) is not int or line <= previous
                or line > MAX_PHYSICAL_ROW):
            raise ValueError(_ERROR)
        previous = line
    return source_sha256, vendor, month, lines
