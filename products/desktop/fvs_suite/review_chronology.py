"""UTC chronology guard for offline, human-authored premium review records.

A SHA-256 journal chain is not a trusted timestamp or an electronic signature.
This guard detects out-of-order recorded times and local clock rollback; it
never approves a financial exception or silently repairs journal history.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re

# datetime.fromisoformat accepts week dates, compact forms, arbitrary date/time
# separators, and fractional seconds beyond its six-digit resolution (which
# it silently truncates). A hash-linked human review must never let those
# alternate serializations mask the event's ordering or effective instant.
# Preserve documented historical UTC suffixes and 1-6 fractional digits;
# new journal records are emitted with whole seconds and +00:00.
_REVIEW_UTC = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]{1,6})?(?:Z|[+-]00:00)\Z",
    re.ASCII,
)


def parse_review_utc(value: object) -> datetime:
    """Accept bounded unambiguous UTC instants without leaking input/context.

    The parser explicitly refuses precision beyond microseconds rather than
    silently truncating a signed/hash-linked journal field.
    """
    if (type(value) is not str or len(value) > 64
            or _REVIEW_UTC.fullmatch(value) is None):
        raise ValueError("Review journal has an invalid UTC timestamp")
    invalid_calendar = False
    try:
        result = datetime.fromisoformat(value)
    except (ValueError, TypeError, OverflowError):
        invalid_calendar = True
    # Translation occurs OUTSIDE the exception handler: 'from None' would
    # still retain the private parse exception in __context__.
    if invalid_calendar:
        raise ValueError("Review journal has an invalid UTC timestamp")
    if result.utcoffset() != timedelta(0):
        raise ValueError("Review journal has an invalid UTC timestamp")
    return result.astimezone(timezone.utc)


def check_record_order(previous: datetime | None, recorded: object) -> datetime:
    """Reject backwards timestamps; equal-second decisions remain permissible."""
    current = parse_review_utc(recorded)
    if previous is not None:
        # A datetime subclass can override astimezone/utcoffset and fabricate
        # ordering. A custom tzinfo can execute user code while serializing a
        # supposedly offline journal and leak private values in exceptions.
        # The parser above produces only native datetime + fixed-offset zones.
        if type(previous) is not datetime or type(previous.tzinfo) is not timezone:
            raise ValueError("Review journal has an invalid previous UTC timestamp")
        if current < previous.astimezone(timezone.utc):
            raise ValueError("Review journal timestamps are out of chronological order")
    return current


def check_new_review_clock(latest_recorded: object | None, current: datetime) -> None:
    """A clock behind the latest saved review cannot append an earlier action."""
    # Refuse datetime subclasses and arbitrary tzinfo methods before invoking
    # their potentially forged or exception-leaking behavior. Native fixed
    # offsets remain accepted by the historical comparison path above.
    if type(current) is not datetime or type(current.tzinfo) is not timezone:
        raise ValueError("Review requires a timezone-aware current clock")
    if current.utcoffset() != timedelta(0):
        raise ValueError("Review requires a UTC current clock")
    if latest_recorded is not None and current.astimezone(timezone.utc) < parse_review_utc(latest_recorded):
        raise ValueError("Review system clock predates the last decision; inspect clock and journal")
