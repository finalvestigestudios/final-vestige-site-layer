"""Canonical LF/CRLF framing for local, human-authored premium review journals.

This is a *record-boundary* guard, not a replacement for source-bound event
hashes, chronology, schema validation, or any compliance/human approval step.
Only complete LF-terminated records exist. CR is accepted solely before LF
for compatibility; bare CR must never create phantom events. Raw VT/FF
are also rejected to keep malformed control bytes out of the journal.
"""
from __future__ import annotations

MAX_JOURNAL_BYTES = 16 * 1024 * 1024
MAX_EVENTS = 20_000
_ERROR = "Review journal has noncanonical record boundaries"


def canonical_review_records(data: bytes) -> tuple[bytes, ...]:
    """Parse bounded journal framing, without decoding or trusting event fields.

    Return unmodified JSON bytes except for an optional terminal CR on each
    CRLF-delimited line. The caller must validate the JSON event, report binding,
    hash chain, chronology, and human decisions *after* this check.
    """
    if type(data) is not bytes or len(data) > MAX_JOURNAL_BYTES:
        raise ValueError(_ERROR)
    if not data:
        return ()
    if not data.endswith(b"\n"):
        raise ValueError(_ERROR)
    records = data[:-1].split(b"\n")
    if len(records) > MAX_EVENTS:
        raise ValueError(_ERROR)
    result = []
    for record in records:
        if record.endswith(b"\r"):
            record = record[:-1]
        if (not record or b"\r" in record or b"\x00" in record or
                b"\x0b" in record or b"\x0c" in record):
            raise ValueError(_ERROR)
        result.append(record)
    return tuple(result)
