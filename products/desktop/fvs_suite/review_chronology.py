"""UTC chronology guard for offline, human-authored premium review records.

A SHA-256 journal chain is not a trusted timestamp or an electronic signature.
This guard detects out-of-order recorded times and local clock rollback; it
never approves a financial exception or silently repairs journal history.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone


def parse_review_utc(value: object) -> datetime:
    """Accept finite ISO-8601 UTC instants only, without logging private input."""
    if type(value) is not str or not value or len(value) > 64 or value != value.strip():
        raise ValueError("Review journal has an invalid UTC timestamp")
    try:
        result = datetime.fromisoformat(value)
        if result.tzinfo is None or result.utcoffset() != timedelta(0):
            raise ValueError
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("Review journal has an invalid UTC timestamp") from exc
    return result.astimezone(timezone.utc)


def check_record_order(previous: datetime | None, recorded: object) -> datetime:
    """Reject backwards timestamps; equal-second decisions remain permissible."""
    current = parse_review_utc(recorded)
    if previous is not None:
        if not isinstance(previous, datetime) or previous.tzinfo is None or previous.utcoffset() is None:
            raise ValueError("Review journal has an invalid previous UTC timestamp")
        if current < previous.astimezone(timezone.utc):
            raise ValueError("Review journal timestamps are out of chronological order")
    return current


def check_new_review_clock(latest_recorded: object | None, current: datetime) -> None:
    """A clock behind the latest saved review cannot append an earlier action."""
    if not isinstance(current, datetime) or current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("Review requires a timezone-aware current clock")
    if current.utcoffset() != timedelta(0):
        raise ValueError("Review requires a UTC current clock")
    if latest_recorded is not None and current.astimezone(timezone.utc) < parse_review_utc(latest_recorded):
        raise ValueError("Review system clock predates the last decision; inspect clock and journal")
