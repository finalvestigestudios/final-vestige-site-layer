"""Native-storage snapshots for premium audit event classification.

CSV imports already yield plain dictionaries. Direct Python API callers may
supply dict subclasses that lie via get/items/keys/iteration. Classify the
stored event instead of a virtual mapping view, without returning or logging
private source values. This does not authenticate caller-supplied records.
"""
from __future__ import annotations


def snapshot_event_record(row: object, *, family: str) -> dict[str, object]:
    """Copy actual dict storage with plain-text keys or reject the event.

    Plain Mapping objects have no trustworthy native storage to inspect; the
    review-only classification boundary explicitly requires a dictionary.
    """
    if not isinstance(row, dict):
        raise ValueError(f"{family} event record must be a dictionary")
    if any(type(field) is not str for field in dict.keys(row)):
        raise ValueError(f"{family} event field names must be plain text")
    return dict(dict.items(row))
