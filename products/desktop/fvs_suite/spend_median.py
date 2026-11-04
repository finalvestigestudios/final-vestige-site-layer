"""Exact, incrementally maintained Decimal median for SpendMap Lite.

Two heaps keep historical month baselines at O(log n) insertion and O(1)
median lookup, rather than sorting an ever-growing history every month.
Financial values must be finite, native, bounded Decimals; never use floats.
"""
from __future__ import annotations

from decimal import Context, Decimal, localcontext
from heapq import heappop, heappush

# Source CSV amounts are bounded; even a 200k-row monthly total remains far
# below this direct-API envelope. Existing historical 70-digit synthetic
# precision tests also remain valid. Enforce it BEFORE heap insertion so
# hostile Decimal subclasses or huge exponents cannot reach comparisons or
# context-dependent median arithmetic.
_MAX_MONTH_DIGITS = 80
_MAX_MONTH_EXPONENT = 80


def _validate_month_total(value: Decimal) -> None:
    if type(value) is not Decimal or not value.is_finite():
        raise ValueError("Monthly total must be a finite native Decimal")
    parts = value.as_tuple()
    if (len(parts.digits) > _MAX_MONTH_DIGITS
            or not -_MAX_MONTH_EXPONENT <= parts.exponent <= _MAX_MONTH_EXPONENT):
        raise ValueError("Monthly total exceeds bounded Decimal envelope")


def _exact_midpoint(left: Decimal, right: Decimal) -> Decimal:
    """Average finite Decimals without inheriting the caller's rounding precision.

    Two fixed-point values need their highest integer place and lowest decimal
    place preserved, plus a carry and the possible extra half-digit. This
    derived precision also supports the helper's finite direct-call contract.
    """
    decimals = max(0, -left.as_tuple().exponent, -right.as_tuple().exponent)
    integers = max(1, left.adjusted() + 1, right.adjusted() + 1)
    with localcontext(Context(prec=max(28, integers + decimals + 3))):
        return (left + right) / Decimal(2)


class RunningDecimalMedian:
    """Median of values already added; current month is added *after* review.

    The lower heap uses negated Decimal values as Python's heapq is a min-heap.
    It holds either the same number of values as the upper heap or one more.
    """

    def __init__(self) -> None:
        self._lower: list[Decimal] = []
        self._upper: list[Decimal] = []

    def __len__(self) -> int:
        return len(self._lower) + len(self._upper)

    def add(self, value: Decimal) -> None:
        """Add a complete, validated monthly total without lossy conversion."""
        _validate_month_total(value)
        # Unary - applies the ambient Decimal precision and can *silently*
        # round a heap key. copy_negate preserves the original coefficient.
        if not self._lower or value <= self._lower[0].copy_negate():
            heappush(self._lower, value.copy_negate())
        else:
            heappush(self._upper, value)
        if len(self._lower) > len(self._upper) + 1:
            heappush(self._upper, heappop(self._lower).copy_negate())
        elif len(self._upper) > len(self._lower):
            heappush(self._lower, heappop(self._upper).copy_negate())

    def median(self) -> Decimal:
        """Return the exact historical median; reject an empty history."""
        if not self._lower:
            raise ValueError("Cannot find median of empty history")
        if len(self._lower) > len(self._upper):
            return self._lower[0].copy_negate()
        return _exact_midpoint(self._lower[0].copy_negate(), self._upper[0])
