"""Fail-fast Invoice Twin Scout review-window policy shared by API paths.

Check the exact native integer BEFORE private CSV reads or candidate iteration.
The window is a human-review search bound, never a compliance decision.
"""
from __future__ import annotations

MAX_REVIEW_WINDOW_DAYS = 365


def require_invoice_review_window(window_days: int) -> int:
    """Return a valid day window without coercing floats, bools or subclasses."""
    if type(window_days) is not int or not 0 <= window_days <= MAX_REVIEW_WINDOW_DAYS:
        raise ValueError("Duplicate window must be an integer between 0 and 365 days")
    return window_days
