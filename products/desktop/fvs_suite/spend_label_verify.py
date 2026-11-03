"""R158 independent custody check for SpendMap human-visible vendor labels.

Source labels are display evidence, NOT canonical financial identifiers.  This
module deliberately DOES NOT import the report's labels_for_report,
visible_source_text, raw_values, or safe_cell helpers: it separately reproduces
the documented wire representation from the pinned original source labels.
"""
from __future__ import annotations

from collections import defaultdict
import re
import unicodedata
from typing import Iterable

_HIDDEN = frozenset(("Cc", "Cf", "Cs", "Co", "Cn", "Zl", "Zp"))
_FILLERS = frozenset((
    0x115F, 0x1160, 0x17B4, 0x17B5, 0x2800, 0x3164, 0xFFA0,
))
_NUMBER = re.compile(r"-[0-9]+(?:\.[0-9]+)?\Z", re.ASCII)


def _ambiguous(char: str) -> bool:
    point = ord(char)
    category = unicodedata.category(char)
    return (
        category in _HIDDEN
        or (category == "Zs" and char != " ")
        or point == 0x034F
        or point in _FILLERS
        or 0x180B <= point <= 0x180F
        or 0xFE00 <= point <= 0xFE0F
        or 0xE0100 <= point <= 0xE01EF
    )


def _visible(text: str) -> str:
    """Independent unambiguous display encoding, preserving original bytes elsewhere."""
    result: list[str] = []
    for char in text:
        code = ord(char)
        if char == "\\":
            result.append("\\\\")
        elif _ambiguous(char):
            result.append(
                "\\u" + format(code, "04X") if code <= 0xFFFF
                else "\\U" + format(code, "08X")
            )
        elif char == ";":
            result.append(r"\u003B")
        else:
            result.append(char)
    return "".join(result)


def _spreadsheet_safe(text: str) -> str:
    """Replicate CSV export formula-prefix defense independently for this field."""
    index = 0
    invisible = False
    while index < len(text):
        char = text[index]
        if char == " ":
            index += 1
            continue
        if (char.isspace() or _ambiguous(char)
                or unicodedata.category(char) in ("Mn", "Me")):
            invisible = True
            index += 1
            continue
        break
    token = text[index:]
    if (invisible or token.startswith(("=", "+", "@"))
            or (token.startswith("-") and _NUMBER.fullmatch(token) is None)):
        return "'" + text
    return text


def expected_vendor_labels(
    observations: Iterable[tuple[str, str, str, str]],
) -> dict[tuple[str, str, str], str]:
    """Independent expected source_vendor_labels per *category*, not vendor/month.

    Input tuples are (normalized vendor, YYYY-MM, report-safe category,
    untouched imported raw vendor). Source validation and SHA pinning occur in
    the calling verifier. Labels are trimmed/deduplicated exactly as documented,
    with Unicode casefold used for ORDER ONLY, never merging source identities.
    """
    groups: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for vendor, month, category, raw_label in observations:
        bucket = (vendor, month, category)
        label = raw_label.strip()
        if label:
            groups[bucket].add(label)
        else:
            groups[bucket]  # Retain an existing bucket with no visible label.
    result = {}
    for bucket, labels in groups.items():
        ordered = sorted(labels, key=lambda value: (value.casefold(), value))
        result[bucket] = _spreadsheet_safe("; ".join(_visible(x) for x in ordered))
    return result
