"""Review-only source-sign custody for ProcureGuard unit prices.

A Decimal negative zero compares equal to positive zero, but the explicit
minus sign is material financial source evidence and must remain visible to
human reviewers. Never use this review flag to authorize a payment.
"""
from __future__ import annotations

from decimal import Decimal


def negative_price_review_required(price: Decimal) -> bool:
    """Flag any finite native Decimal with its sign bit set, including -0.

    Caller validation in ``checked_unit_price`` retains exact source meaning.
    This function does not round, normalize, or reinterpret financial inputs.
    Reject unknown Python objects rather than evaluating forged comparisons.
    """
    if type(price) is not Decimal or not price.is_finite():
        raise ValueError("Procurement price review requires a finite native Decimal")
    return price.is_signed()
