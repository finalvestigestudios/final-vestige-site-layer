"""Strict, private parsing of offline ProcureGuard price-review policy JSON.

Malformed policy contents are never attached as lower-level exception causes.
Thresholds remain a human-review control, not authority to approve payment.
"""
from __future__ import annotations

import json

_BAD_JSON = "Invalid UTF-8 JSON price policy"


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            raise ValueError("Duplicate JSON price policy key")
        result[name] = value
    return result


def _reject_nonfinite(_value: str) -> object:
    raise ValueError("Nonfinite JSON values are not allowed")


def decode_price_policy_document(data: bytes) -> object:
    """Decode bounded native bytes; reject malformed JSON with no chained payload.

    Keep the public legacy errors for nonfinite/duplicate keys. A malformed
    UTF-8/JSON decoding failure is translated only after leaving the exception
    handler, so JSONDecodeError.doc/UnicodeDecodeError.object cannot survive
    through __cause__ or __context__ of the public ValueError.
    """
    if type(data) is not bytes:
        raise ValueError(_BAD_JSON)
    try:
        parsed = json.loads(data.decode("utf-8-sig"),
                            object_pairs_hook=_unique_object,
                            parse_constant=_reject_nonfinite)
    except (UnicodeError, json.JSONDecodeError):
        invalid_document = True
    else:
        invalid_document = False
    if invalid_document:
        raise ValueError(_BAD_JSON)
    return parsed
