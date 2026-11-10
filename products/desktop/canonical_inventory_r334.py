"""Strict, deterministic parser for six Windows candidate SHA-256 inventories.

Accept only the exact canonical LF/ASCII/ordered format emitted by
build_inventory.py. This is an input-format gate, NOT a binary signature,
malware scan, native Windows smoke test, or release approval.
"""
from __future__ import annotations

import re
from collections.abc import Sequence

_LOWER_SHA256 = re.compile(rb"[0-9a-f]{64}\Z")


class CanonicalInventoryError(ValueError):
    """Inventory evidence is noncanonical; stop without running any EXE."""


def parse_canonical_inventory(payload: bytes, expected_names: Sequence[str]) -> dict[str, str]:
    """Require exactly one SHA256SUMS line per expected EXE, in fixed order.

    The producer writes ``<64 lowercase hex><two ASCII spaces><name><LF>``.
    Do not normalize Windows newlines, silently reorder evidence, accept
    trailing bytes, or use lenient Unicode decoding. The input has already
    been read by the pinned-descriptor, size-bounded candidate guard.
    """
    if type(payload) is not bytes:
        raise CanonicalInventoryError("Checksum inventory must be raw ASCII bytes")
    names = tuple(expected_names)
    if not names or len(names) != len(set(names)):
        raise CanonicalInventoryError("Expected candidate names are ambiguous")
    try:
        encoded = tuple(name.encode("ascii") for name in names)
    except (AttributeError, UnicodeError):
        raise CanonicalInventoryError("Expected candidate names must be ASCII") from None
    if any(not re.fullmatch(rb"[A-Za-z0-9]+\.exe", name) for name in encoded):
        raise CanonicalInventoryError("Expected candidate names are invalid")

    # Fixed length and per-position checks reject missing/extra lines, CRLF,
    # BOM, reordered lines, whitespace drift, duplicates and missing final LF.
    expected_size = sum(64 + 2 + len(name) + 1 for name in encoded)
    if len(payload) != expected_size:
        raise CanonicalInventoryError("Checksum inventory is not canonical")
    result: dict[str, str] = {}
    cursor = 0
    for original, name in zip(names, encoded):
        width = 64 + 2 + len(name) + 1
        row = payload[cursor:cursor + width]
        cursor += width
        digest = row[:64]
        if (_LOWER_SHA256.fullmatch(digest) is None or row[64:66] != b"  "
                or row[66:-1] != name or row[-1:] != b"\n"):
            raise CanonicalInventoryError("Checksum inventory is not canonical")
        result[original] = digest.decode("ascii")
    return result
