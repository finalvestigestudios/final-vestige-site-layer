"""Fail-closed Decimal custody for ProcureGuard's injectable review parsers.

The normal CSV engine enforces limits, but review_line is also a Python API
whose supplied parser callbacks may be incorrect or hostile. Never let a
nonfinite, negative quantity, rounded float, or forged Decimal reach totals.
This is validation of arithmetic evidence, not payment approval.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Callable

_MAX_QUANTITY = Decimal("1000000000")
_MAX_UNIT_PRICE = Decimal("1000000000000")
_QUANTITY_ERROR = "Procurement quantity must be a bounded exact nonnegative Decimal"
_PRICE_ERROR = "Procurement unit price must be a bounded exact finite Decimal"
_MAX_INPUT_CHARS = 80
_MAX_EXPONENT = 80


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


def _source_value(value: object, *, quantity: bool) -> Decimal | None:
    """Bound native financial input before invoking an untrusted callback.

    Plain numeric strings, integers and Decimals also carry independent exact
    values: a supplied parser must not silently change those amounts. Other
    permitted accounting strings retain the established callback grammar; they
    are still bounded and never presumed to be verified by this helper.
    """
    failure = _QUANTITY_ERROR if quantity else _PRICE_ERROR
    if type(value) is str:
        if (len(value) > _MAX_INPUT_CHARS or not value
                or any(ord(c) < 32 or ord(c) == 127 for c in value)):
            raise ValueError(failure)
        raw = value.strip()
        if not raw:
            raise ValueError(failure)
        # Decimal's plain-number parser intentionally does not understand
        # $ signs, grouping commas or accounting parentheses. Keep those
        # formats available for the existing engine parser, but bind native
        # numeric tokens (including E notation) to their exact source value.
        if not raw.isascii():
            return None
        try:
            original = Decimal(raw)
        except InvalidOperation:
            return None
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
        result = parser(value)
    except Exception:
        # Callback exception text and chaining can disclose private CSV paths.
        raise ValueError(failure) from None
    if (type(result) is not Decimal or not result.is_finite()
            or not -_MAX_EXPONENT <= result.as_tuple().exponent <= _MAX_EXPONENT
            or result.copy_abs() > (_MAX_QUANTITY if quantity else _MAX_UNIT_PRICE)
            or (quantity and result < 0)
            or _fractional_places(result) > 8
            or (original is not None and result != original)):
        raise ValueError(failure)
    return result


def checked_quantity(value: object, parser: Callable) -> Decimal:
    """Validate a caller's quantity parser output before exact aggregation."""
    return _checked(value, parser, quantity=True)


def checked_unit_price(value: object, parser: Callable) -> Decimal:
    """Allow documented negative prices but never a nonfinite/rounded value."""
    return _checked(value, parser, quantity=False)
