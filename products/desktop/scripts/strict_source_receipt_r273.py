"""Reject ambiguous JSON in the private six-app source-suite receipt.

A private build receipt is evidence, not customer data and not release approval.
JSON duplicate keys or nonstandard constants must never be silently accepted by
Python's permissive default decoder. Only a fixed diagnostic is exposed.
"""
from __future__ import annotations

import json

SAFE_ERROR = "Invalid or ambiguous private source-suite receipt"


class ReceiptJSONRejected(ValueError):
    """Fixed message; never include untrusted receipt contents or paths."""


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ReceiptJSONRejected(SAFE_ERROR)
        obj[key] = value
    return obj


def _reject_nonstandard_constant(_value):
    raise ReceiptJSONRejected(SAFE_ERROR)


def loads_strict_receipt(data: bytes | bytearray) -> object:
    """Decode one JSON document, rejecting duplicate keys even in nested data.

    Does not validate evidence schema or establish that the producer was trusted;
    caller must retain its full structural, file-custody and checksum gates.
    """
    decoded = None
    parsed = False
    try:
        if type(data) not in (bytes, bytearray):
            raise ReceiptJSONRejected(SAFE_ERROR)
        decoded = json.loads(
            data, object_pairs_hook=_unique_object,
            parse_constant=_reject_nonstandard_constant,
        )
        parsed = True
    except (ValueError, TypeError, UnicodeError, RecursionError):
        # Do not retain a decoder exception containing a private path or row.
        pass
    if not parsed:
        raise ReceiptJSONRejected(SAFE_ERROR)
    return decoded
