"""Retain significant Unicode boundary characters in SpendMap vendor evidence.

Vendor matching keys intentionally discard non-ASCII characters. This helper
preserves the original distinct, readable labels for human collision review;
it does not authenticate the CSV or authorize any compliance decision.
"""
from __future__ import annotations

from typing import Iterable, Mapping

from .audit_display import visible_source_text
from .review import ascii_case_identity

# CSV ingestion now retains exact vendor spelling (R398). Matching may ignore
# boundary whitespace, but reviewed labels must show the original differences.


def _visible_vendor_label(value: str) -> str:
    """Show boundary ASCII spaces explicitly, separate from literal escapes."""
    leading = len(value) - len(value.lstrip(" "))
    remainder = value[leading:]
    trailing = len(remainder) - len(remainder.rstrip(" "))
    center = remainder[:-trailing] if trailing else remainder
    return (r"\u0020" * leading
            + visible_source_text(center).replace(";", r"\u003B")
            + r"\u0020" * trailing)


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
        if original:
            originals.add(original)

    identities = {ascii_case_identity(value) for value in originals}
    labels = "; ".join(
        _visible_vendor_label(value)
        for value in sorted(originals, key=lambda value: (value.casefold(), value))
    )
    return (len(identities) > 1, len(identities), labels)
