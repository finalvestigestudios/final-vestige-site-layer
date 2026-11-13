"""Unambiguous local display of untrusted financial source references.

Rendered values are for human review cells only, not replacements for raw
source bytes, source SHA-256, physical row references or journal evidence.
No normalization, matching, network I/O or compliance decisions occur here.
"""
from __future__ import annotations

from typing import Iterable
import unicodedata

from .unicode_hazards import is_visually_blank_filler


_HIDDEN_CATEGORIES = frozenset(("Cc", "Cf", "Cs", "Co", "Cn", "Zl", "Zp"))


def _escape_source_character(character: str) -> bool:
    codepoint = ord(character)
    category = unicodedata.category(character)
    return (
        category in _HIDDEN_CATEGORIES
        or (category == "Zs" and character != " ")
        or codepoint == 0x034F  # Invisible combining grapheme joiner.
        or 0x180B <= codepoint <= 0x180F  # Mongolian variation selectors.
        or 0xFE00 <= codepoint <= 0xFE0F  # Standard variation selectors.
        or 0xE0100 <= codepoint <= 0xE01EF  # Supplementary selectors.
        or is_visually_blank_filler(character)  # Non-control blank glyphs.
    )


def visible_source_text(value: str) -> str:
    """Escape ambiguous source Unicode and literal backslashes for display.

    Every input codepoint maps deterministically to itself, a doubled
    backslash, a 4-digit Unicode escape or an 8-digit Unicode escape.
    A literal source escape stays distinguishable from an actual control.
    Never call on previously rendered text; escape is not idempotent.
    """
    if not isinstance(value, str):
        raise TypeError("Audit source display requires text")
    parts: list[str] = []
    for character in value:
        codepoint = ord(character)
        if character == "\\":
            parts.append("\\\\")
        elif _escape_source_character(character):
            parts.append(f"\\u{codepoint:04X}" if codepoint <= 0xFFFF
                         else f"\\U{codepoint:08X}")
        else:
            parts.append(character)
    return "".join(parts)


def visible_identity_label(value: str) -> str:
    """Display original identity boundaries without changing audit provenance.

    A leading or trailing ASCII space can distinguish identifiers that share
    a normalized matching key. Mark such spaces explicitly, just as hidden
    Unicode is escaped. Literal backslashes cannot imitate those markers.
    """
    if type(value) is not str:
        raise TypeError("Audit source identity labels require native text")
    leading = len(value) - len(value.lstrip(" "))
    rest = value[leading:]
    trailing = len(rest) - len(rest.rstrip(" "))
    inner = rest[:-trailing] if trailing else rest
    return (r"\u0020" * leading
            + visible_source_text(inner).replace(";", r"\u003B")
            + r"\u0020" * trailing)


def visible_source_label_list(values: Iterable[str]) -> str:
    """Render an unambiguous source-document list, including boundary spaces.

    Never trim or normalize source identities in a human audit display.
    The first-level sort preserves prior ordering for unchanged inputs.
    Empty labels are absent; whitespace-only labels remain visible evidence.
    """
    labels: set[str] = set()
    for value in values:
        if type(value) is not str:
            raise TypeError("Audit source document labels require native text")
        if value:
            labels.add(value)
    return "; ".join(visible_identity_label(value) for value in sorted(labels))


def visible_review_row(case: object, decision: str) -> tuple[int, str, str, str]:
    """Treeview values only: do not mutate the raw exception case.

    Case identity remains in the Treeview item ID outside display cells,
    and the raw case is bound to the original report SHA-256.
    """
    return (
        case.report_row, visible_identity_label(case.source_key),
        visible_source_text(case.flags), decision,
    )
