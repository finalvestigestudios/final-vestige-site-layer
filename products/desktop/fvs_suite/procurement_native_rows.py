"""Own procurement input row storage before totals or audit citations.

ProcureGuard is a local-first review tool, not an approval engine. Parsed CSV
rows have native list/dict storage; direct callers can supply subclasses whose
virtual views misrepresent quantities, source IDs or original row numbers.
Copies keep the underlying source values unchanged while preventing caller
method overrides from steering the deterministic review computation.
"""
from __future__ import annotations

from .event_custody import snapshot_event_record

_RECORD_ERROR = "Procurement review requires a native list of source records"
_ROW_ERROR = "Procurement source citation requires a canonical physical row number"


def owned_procurement_rows(rows: object) -> list[dict[str, object]]:
    """Return a new list of genuine dictionary storage, not virtual views.

    This is an input boundary, not authentication: a caller may still provide
    fabricated plain dictionaries. CSV digests and the original parser remain
    the authoritative evidence of which financial bytes were imported.
    """
    if type(rows) is not list:
        raise ValueError(_RECORD_ERROR)
    return [snapshot_event_record(row, family="Procurement") for row in rows]


def physical_source_row(value: object) -> str:
    """Reject forged/noncanonical citation text without conversion hooks.

    Imported row labels are ASCII decimal physical-row indices starting at 2.
    Match the event-intake 10-digit ceiling; no Unicode digits, control codes,
    whitespace, signs, leading zeroes, or caller-defined ``__str__``.
    Grammar validation cannot independently prove a claimed row is genuine.
    """
    if (type(value) is not str or not 1 <= len(value) <= 10
            or value == "1" or value[0] == "0"
            or any(character < "0" or character > "9" for character in value)):
        raise ValueError(_ROW_ERROR)
    return value
