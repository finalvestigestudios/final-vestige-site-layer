"""Retain significant Unicode boundary characters in SpendMap vendor evidence.

Vendor matching keys intentionally discard non-ASCII characters. This helper
preserves the original distinct, readable labels for human collision review;
it does not authenticate the CSV or authorize any compliance decision.
"""
from __future__ import annotations

from typing import Iterable, Mapping

from .audit_display import visible_source_text
from .review import ascii_case_identity

# Compatibility with existing CSV import: only ordinary ASCII boundary
# whitespace is insignificant. Python's default strip() erases NBSP and
# FIGURE/NARROW NBSP, incorrectly hiding distinct original source labels.
_ASCII_BOUNDARY_WHITESPACE = " \t\r\n\v\f"


def spend_vendor_evidence(
    rows: Iterable[Mapping[str, str]],
) -> tuple[bool, int, str]:
    """Return (needs identity review, ASCII-case variants, visible labels).

    Treat Unicode differences and actual backslash escape text as original
    evidence. Render controls invisibly only via the audited visible-source
    escape helper; a source semicolon cannot forge an output list separator.
    Raw cells are never echoed in validation errors.
    """
    originals: set[str] = set()
    for row in rows:
        original = row.get("vendor")
        if type(original) is not str:
            raise ValueError("Spend vendor evidence requires native source text")
        trimmed = original.strip(_ASCII_BOUNDARY_WHITESPACE)
        if trimmed:
            originals.add(trimmed)

    identities = {ascii_case_identity(value) for value in originals}
    labels = "; ".join(
        visible_source_text(value).replace(";", r"\u003B")
        for value in sorted(originals, key=lambda value: (value.casefold(), value))
    )
    return (len(identities) > 1, len(identities), labels)
