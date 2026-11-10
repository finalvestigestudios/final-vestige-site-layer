"""Strict, private, local JSONL event preflight for premium review journals.

The caller must still verify report identity, prior journal hashes and human
review decisions. This guard only blocks malformed record bytes *before* a
new journal can be created or an existing one appended; it is not approval.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import json

_ERROR = "Review event must be one valid UTF-8 JSON object with unique keys"


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_raw: str) -> None:
    raise ValueError("nonfinite JSON constant")


def require_jsonl_object(data: bytes) -> None:
    """Require one LF-terminated UTF-8 JSON object without duplicate keys.

    Use Decimal for JSON floating point literals so huge exponents never
    silently parse to infinite binary float. No source paths, JSON fields,
    values, or parser details are included in any rejection text/exception.
    Semantic review-event schema and hash validation remain with the caller.
    """
    if (type(data) is not bytes or not data.endswith(b"\n")
            or data.count(b"\n") != 1 or b"\r" in data or b"\x00" in data):
        raise ValueError(_ERROR)
    failed = False
    obj = None
    try:
        obj = json.loads(
            data[:-1].decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=Decimal,
        )
    except (UnicodeError, ValueError, RecursionError, OverflowError, InvalidOperation):
        failed = True
    if failed or type(obj) is not dict:
        raise ValueError(_ERROR)
