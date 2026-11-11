"""Fail-closed Decimal custody for ProcureGuard's injectable review parsers.

The normal CSV engine enforces limits, but review_line is also a Python API
whose supplied parser callbacks may be incorrect or hostile. Never let a
nonfinite, negative quantity, rounded float, or forged Decimal reach totals.
This is validation of arithmetic evidence, not payment approval.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation, localcontext
from typing import Callable

_MAX_QUANTITY = Decimal("1000000000")
_MAX_UNIT_PRICE = Decimal("1000000000000")
_QUANTITY_ERROR = "Procurement quantity must be a bounded exact nonnegative Decimal"
_PRICE_ERROR = "Procurement unit price must be a bounded exact finite Decimal"
_MAX_INPUT_CHARS = 80
_MAX_EXPONENT = 80
# Mirror the suite's ASCII quantity/price grammar before untrusted parser calls.
# Keep legacy plain scientific notation but exclude Decimal-only conveniences
# (Unicode digits and underscores) that the real CSV intake rejects.
_PLAIN_NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
_GROUPED_QUANTITY = re.compile(
    r"[+]?(?:(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]*)?|\.[0-9]+)\Z"
)
_ACCOUNTING_PRICE = re.compile(
    r"(?P<prefix>(?:[+-]?\$|\$[+-]?|[+-]?))"
    r"(?P<number>(?:(?:[0-9]{1,3}(?:,[0-9]{3})+)|[0-9]+)(?:\.[0-9]*)?|\.[0-9]+)\Z"
)


def _fractional_places(value: Decimal) -> int:
    """Count meaningful fractional digits without ambient-context rounding."""
    numeric = value.as_tuple()
    if numeric.exponent >= 0 or not any(numeric.digits):
        return 0
    trailing = 0
    for digit in reversed(numeric.digits):
        if digit:
            break
        trailing += 1
    return max(0, -numeric.exponent - trailing)


def _parse_source_text(raw: str, *, quantity: bool) -> Decimal:
    """Interpret ordinary accounting tokens independently of parser callbacks.

    The standard CSV engine uses the same strict ASCII grouping, currency and
    parenthesis grammar. Unknown tokens fail closed *before* callbacks run.
    """
    failure = _QUANTITY_ERROR if quantity else _PRICE_ERROR
    if not raw.isascii():
        raise ValueError(failure)
    if _PLAIN_NUMBER.fullmatch(raw):
        return Decimal(raw)
    if quantity:
        if _GROUPED_QUANTITY.fullmatch(raw):
            return Decimal(raw.replace(",", ""))
        raise ValueError(failure)
    parenthesized = raw.startswith("(") or raw.endswith(")")
    if parenthesized:
        if not (raw.startswith("(") and raw.endswith(")")):
            raise ValueError(failure)
        raw = raw[1:-1].strip()
    match = _ACCOUNTING_PRICE.fullmatch(raw)
    if match is None or (parenthesized and
                         ("+" in match.group("prefix") or "-" in match.group("prefix"))):
        raise ValueError(failure)
    result = Decimal(match.group("number").replace(",", ""))
    return result.copy_negate() if parenthesized or "-" in match.group("prefix") else result


def _source_value(value: object, *, quantity: bool) -> Decimal:
    """Bound native financial input before invoking an untrusted callback.

    All supported source tokens carry an independent exact numeric meaning:
    supplied parsers must neither change amounts nor launder malformed input.
    """
    failure = _QUANTITY_ERROR if quantity else _PRICE_ERROR
    if type(value) is str:
        if (len(value) > _MAX_INPUT_CHARS or not value
                or any(ord(c) < 32 or ord(c) == 127 for c in value)):
            raise ValueError(failure)
        raw = value.strip()
        if not raw:
            raise ValueError(failure)
        original = _parse_source_text(raw, quantity=quantity)
    elif type(value) is int:
        if value.bit_length() > 269:
            raise ValueError(failure)
        original = Decimal(value)
    elif type(value) is Decimal:
        original = value
    else:
        raise ValueError(failure)
    if not original.is_finite():
        raise ValueError(failure)
    spec = original.as_tuple()
    if (len(spec.digits) > _MAX_INPUT_CHARS
            or not -_MAX_EXPONENT <= spec.exponent <= _MAX_EXPONENT
            or original.copy_abs() > (_MAX_QUANTITY if quantity else _MAX_UNIT_PRICE)
            or (quantity and original < 0)
            or _fractional_places(original) > 8):
        raise ValueError(failure)
    return original


def _checked(value: object, parser: Callable, *, quantity: bool) -> Decimal:
    failure = _QUANTITY_ERROR if quantity else _PRICE_ERROR
    # Direct API values must be size-bounded before callbacks. A custom
    # callback must not launder a simple source numeral into a different sum.
    original = _source_value(value, quantity=quantity)
    try:
        # Parser code may alter getcontext(), setcontext(), traps or status
        # flags. Isolate it so a valid Decimal return cannot silently lower
        # review_line's 64-digit arithmetic precision for subsequent totals.
        with localcontext():
            result = parser(value)
    except Exception:
        # Callback exception text and chaining can disclose private CSV paths.
        raise ValueError(failure) from None
    if (type(result) is not Decimal or not result.is_finite()
            or not -_MAX_EXPONENT <= result.as_tuple().exponent <= _MAX_EXPONENT
            or result.copy_abs() > (_MAX_QUANTITY if quantity else _MAX_UNIT_PRICE)
            or (quantity and result < 0)
            or _fractional_places(result) > 8
            or result != original):
        raise ValueError(failure)
    return result


def checked_quantity(value: object, parser: Callable) -> Decimal:
    """Validate a caller's quantity parser output before exact aggregation."""
    return _checked(value, parser, quantity=True)


def checked_unit_price(value: object, parser: Callable) -> Decimal:
    """Allow documented negative prices but never a nonfinite/rounded value."""
    return _checked(value, parser, quantity=False)
