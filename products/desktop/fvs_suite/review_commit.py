"""Read-after-write confirmation for offline premium human-review journals.

A successful fsync proves only that a write was requested; it does not prove
that the complete source-bound hash chain still encodes the expected decision.
This module provides *observed* confirmation, not an immutable audit signature.
"""
from __future__ import annotations

from typing import Callable


def confirm_review_commit(
    report: object,
    product: str,
    journal: object,
    *,
    expected_batch: object,
    previous_events: list[dict],
    expected_event: dict,
    assert_lock_owned: Callable[[], None],
    read_cases: Callable[[object, str], object],
    read_journal: Callable[[object, object], list[dict]],
) -> None:
    """Confirm the exact new event and every predecessor after journal fsync.

    Raise on changed source, malformed/altered history, missing or duplicated
    event, or lost writer lock. A raised error after append means the outcome
    is *indeterminate*: a person must inspect the journal before retrying.
    No writes, journal repair, payment decisions, or private-data logging occur.
    """
    assert_lock_owned()
    observed_batch = read_cases(report, product)
    if observed_batch != expected_batch:
        raise ValueError(
            "Review source changed after journal write; inspect before retrying"
        )
    observed_events = read_journal(journal, observed_batch)
    if observed_events != [*previous_events, expected_event]:
        raise ValueError(
            "Review journal commit could not be confirmed; inspect before retrying"
        )
    assert_lock_owned()
