"""R359: bind SpendMap report periods to original local CSV calendar values.

Custom direct-API date callbacks may reformat a source date but must never
replace its calendar day. This source consistency check is not an attestation
of a file's authenticity and never approves a compliance decision.
"""
from __future__ import annotations

from datetime import date

from .identity_inputs import parse_date as _native_parse_date

_ERROR = "Invalid original SpendMap date; no report was saved"


def canonical_spend_source_date(raw: object) -> date:
    """Parse supported original date text independently of caller callbacks.

    The engine's native calendar syntax is deliberately shared here: ISO
    YYYY-M-D and US M/D/YYYY or M/D/YY, with real Gregorian validation.
    Reject str subclasses and never repeat private source text in errors.
    """
    if type(raw) is not str:
        raise ValueError(_ERROR)
    try:
        day = _native_parse_date(raw)
    except (ValueError, TypeError):
        raise ValueError(_ERROR) from None
    if type(day) is not date:
        raise ValueError(_ERROR)
    return day


def spend_date_parser_preserves_source(source_day: date, parsed: object) -> bool:
    """Require an exact built-in date equal to independently parsed evidence."""
    return type(source_day) is date and type(parsed) is date and parsed == source_day
