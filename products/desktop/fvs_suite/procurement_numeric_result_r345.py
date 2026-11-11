"""Fail-closed Decimal custody for ProcureGuard's injectable review parsers.

The normal CSV engine enforces limits, but review_line is also a Python API
whose supplied parser callbacks may be incorrect or hostile. Never let a
nonfinite, negative quantity, rounded float, or forged Decimal reach totals.
This is validation of arithmetic evidence, not payment approval.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Callable

_MAX_QUANTITY = Decimal("1000000000")
_MAX_UNIT_PRICE = Decimal("1000000000000")
_QUANTITY_ERROR = "Procurement quantity must be a bounded exact nonnegative Decimal"
_PRICE_ERROR = "Procurement unit price must be a bounded exact finite Decimal"


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


def _checked(value: object, parser: Callable, *, quantity: bool) -> Decimal:
    failure = _QUANTITY_ERROR if quantity else _PRICE_ERROR
    # Avoid invoking __str__, __float__ or any other hook before the parser.
    # Retain the engine's documented native str/int/Decimal input contract.
    if type(value) not in (str, int, Decimal):
        raise ValueError(failure)
    if type(value) is int and value.bit_length() > 269:
        raise ValueError(failure)
    try:
        result = parser(value)
    except Exception:
        # Callback exception text and chaining can disclose private CSV paths.
        raise ValueError(failure) from None
    if (type(result) is not Decimal or not result.is_finite()
            or result.copy_abs() > (_MAX_QUANTITY if quantity else _MAX_UNIT_PRICE)
            or (quantity and result < 0)
            or _fractional_places(result) > 8):
        raise ValueError(failure)
    return result


def checked_quantity(value: object, parser: Callable) -> Decimal:
    """Validate a caller's quantity parser output before exact aggregation."""
    return _checked(value, parser, quantity=True)


def checked_unit_price(value: object, parser: Callable) -> Decimal:
    """Allow documented negative prices but never a nonfinite/rounded value."""
    return _checked(value, parser, quantity=False)
