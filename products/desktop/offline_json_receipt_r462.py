"""Strict private JSON receipt decoder shared by six-app source verification.

Duplicate fields make audit evidence ambiguous: two consumers may choose
opposite values. Reject duplicate keys at *every* nesting level before
schema/status checks. This is source-only validation, never release approval.
"""
from __future__ import annotations

import json


class PrivateReceiptJSONError(ValueError):
    """Fixed-message failure; never echo customer-controlled receipt text."""


def _unique_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    values: dict[str, object] = {}
    for key, value in pairs:
        if key in values:
            raise PrivateReceiptJSONError("Ambiguous private source receipt rejected")
        values[key] = value
    return values


def _reject_nonfinite(_: str) -> None:
    raise PrivateReceiptJSONError("Ambiguous private source receipt rejected")


def load_private_receipt(raw: bytes) -> object:
    """Parse strict UTF-8 JSON without duplicate keys or non-finite tokens.

    Callers independently enforce bounded length, exact schema, count and
    source digest. This decoder is NOT an authentication primitive.
    """
    if type(raw) is not bytes:
        raise PrivateReceiptJSONError("Ambiguous private source receipt rejected")
    try:
        return json.loads(raw, object_pairs_hook=_unique_fields,
                          parse_constant=_reject_nonfinite)
    except (ValueError, UnicodeError, TypeError, RecursionError):
        raise PrivateReceiptJSONError("Ambiguous private source receipt rejected") from None
