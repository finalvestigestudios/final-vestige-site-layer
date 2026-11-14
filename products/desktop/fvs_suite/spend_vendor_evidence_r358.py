"""Retain significant Unicode boundary characters in SpendMap vendor evidence.

Vendor matching keys intentionally discard non-ASCII characters. This helper
preserves the original distinct, readable labels for human collision review;
it does not authenticate the CSV or authorize any compliance decision.
"""
from __future__ import annotations

from typing import Iterable, Mapping

from .audit_display import visible_identity_label
from .review import ascii_case_identity

# Compatibility with existing CSV import: only ordinary ASCII boundary
# whitespace is insignificant to *matching*, not to source-label evidence.
_ASCII_BOUNDARY_WHITESPACE = " \t\r\n\v\f"


def spend_vendor_evidence(
    rows: Iterable[Mapping[str, str]],
) -> tuple[bool, int, str]:
    """Return (needs identity review, ASCII-case variants, visible labels).

    Match ordinary ASCII boundary whitespace as before, but preserve it in
    the *displayed original*. Escaped spaces/controls distinguish actual CSV
    vendor cells from trimmed aliases without manufacturing a collision flag.
    Render semicolons visibly so source labels cannot forge list separators.
    Raw cells are never echoed in validation errors.
    """
    originals: set[str] = set()
    for row in rows:
        original = row.get("vendor")
        if type(original) is not str:
            raise ValueError("Spend vendor evidence requires native source text")
        if original.strip(_ASCII_BOUNDARY_WHITESPACE):
            originals.add(original)

    identities = {ascii_case_identity(value.strip(_ASCII_BOUNDARY_WHITESPACE))
                  for value in originals}
    labels = "; ".join(
        visible_identity_label(value)
        for value in sorted(originals, key=lambda value: (value.casefold(), value))
    )
    return (len(identities) > 1, len(identities), labels)
