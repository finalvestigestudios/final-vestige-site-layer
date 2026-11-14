"""Native source-SHA custody for deterministic SpendMap Lite audit evidence.

The SHA string is a provenance identifier, not an authenticity signature. A
caller must compute it from the exact descriptor-verified CSV snapshot. Reject
string subclasses before their encode/equality hooks can forge grouping hashes.
"""
from __future__ import annotations

_ERROR = "Source snapshot SHA-256 must be 64 lowercase hexadecimal characters"
_HEX = frozenset("0123456789abcdef")


def require_native_spend_source_sha256(value: object) -> str:
    """Return an owned native lowercase SHA-256 identity or refuse privately."""
    if type(value) is not str or len(value) != 64 or any(ch not in _HEX for ch in value):
        raise ValueError(_ERROR)
    return value
