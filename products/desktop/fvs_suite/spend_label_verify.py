"""Independent R430 source-bound verification for SpendMap vendor-label evidence.

This is intentionally separate from the report generator and its Unicode
renderer: a shared bug must not be enough to make a forged report verify.
It checks report display evidence; it does not approve spending or compliance.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import re
import unicodedata
from typing import Iterable

_HIDDEN = frozenset(("Cc", "Cf", "Cs", "Co", "Cn", "Zl", "Zp"))
_FILLERS = frozenset((0x115F, 0x1160, 0x17B4, 0x17B5, 0x2800, 0x3164, 0xFFA0))
_NUMBER = re.compile(r"-[0-9]+(?:\.[0-9]+)?\Z", re.ASCII)
_ASCII_BOUNDARY = " \t\r\n\v\f"
_LABEL_LIMIT = 1024
_PREFIX_LIMIT = 64
_PREVIEW_COUNT = 32
_PREVIEW_LIMIT = 8000
_REPORT_LIMIT = 8192
_DIGEST_DOMAIN = b"FVS-SPEND-RAW-VENDOR-LABELS-v1\n"
_ERROR = "SpendMap vendor-label verification failed"


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
    """Reproduce the documented identity display grammar independently."""
    leading = len(text) - len(text.lstrip(" "))
    rest = text[leading:]
    trailing = len(rest) - len(rest.rstrip(" "))
    inner = rest[:-trailing] if trailing else rest
    output = [r"\u0020" * leading]
    for char in inner:
        code = ord(char)
        if char == "\\":
            output.append("\\\\")
        elif _ambiguous(char) or unicodedata.category(char) in ("Mn", "Mc", "Me"):
            output.append(
                "\\u" + format(code, "04X") if code <= 0xFFFF
                else "\\U" + format(code, "08X")
            )
        elif char == ";":
            output.append(r"\u003B")
        else:
            output.append(char)
    output.append(r"\u0020" * trailing)
    return "".join(output)


# Preserve an independent source-bound check for spreadsheet importers
# that NFKC-fold compatibility operators before evaluating a CSV cell.
# Keep raw source display unchanged; this is not an import, signature or approval.
_FORMULA_IGNORABLE = frozenset(("Cf", "Cc", "Mn", "Me"))


def _compatibility_formula_prefix(text: str) -> bool:
    """Independently reproduce the publisher's first-meaningful-character rule."""
    for index, character in enumerate(text):
        if character.isspace() or unicodedata.category(character) in _FORMULA_IGNORABLE:
            continue
        if character == "-":
            # Valid native negative Decimal text must not become a formula.
            return _NUMBER.fullmatch(text[index:]) is None
        normalized = unicodedata.normalize("NFKC", character)
        return bool(normalized and normalized[0] in "=+@-")
    return False


def _spreadsheet_safe(text: str) -> str:
    """Independent formula-prefix defense for final CSV field."""
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
            or (token.startswith("-") and _NUMBER.fullmatch(token) is None)
            or _compatibility_formula_prefix(text)):
        return "'" + text
    return text


def _label_digest(ordered: list[str]) -> str:
    """Recompute the domain-separated, full-native-label digest."""
    digest = sha256(_DIGEST_DOMAIN)
    for label in ordered:
        try:
            data = label.encode("utf-8")
        except UnicodeError:
            # Never chain an exception containing the customer source cell.
            raise ValueError(_ERROR) from None
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def _label_preview(ordered: list[str]) -> str:
    preview: list[str] = []
    length = 0
    clipped = False
    for label in ordered[:_PREVIEW_COUNT]:
        rendered = _visible(label) if len(label) <= _LABEL_LIMIT else ""
        is_clipped = not rendered or len(rendered) > _LABEL_LIMIT
        if is_clipped:
            rendered = _visible(label[:_PREFIX_LIMIT]) + r"\u[LABEL_PREFIX_ONLY]"
        width = len(rendered) + (2 if preview else 0)
        if length + width > _PREVIEW_LIMIT:
            break
        preview.append(rendered)
        length += width
        clipped |= is_clipped
    omitted = len(ordered) - len(preview)
    if omitted or clipped:
        preview.append(
            r"\u[PREVIEW_ONLY:shown=" + str(len(preview))
            + ":omitted=" + str(omitted)
            + ":sha256=" + _label_digest(ordered) + "]"
        )
    result = "; ".join(preview)
    if len(result) > _REPORT_LIMIT:
        raise ValueError(_ERROR)
    return result


def expected_vendor_labels(
    observations: Iterable[tuple[str, str, str, str]],
) -> dict[tuple[str, str, str], str]:
    """Recompute source labels per *vendor across all months/categories*.

    Observations: (normalized vendor, month, CSV-safe category, raw original
    vendor). Every bucket for the same vendor must have identical, complete
    or visibly truncated vendor-wide evidence. Source snapshot and financial
    membership checks remain the responsibility of the calling verifier.
    """
    keys: set[tuple[str, str, str]] = set()
    labels: dict[str, set[str]] = defaultdict(set)
    for vendor, month, category, raw_label in observations:
        if any(type(value) is not str for value in (vendor, month, category, raw_label)):
            raise ValueError(_ERROR)
        keys.add((vendor, month, category))
        if raw_label.strip(_ASCII_BOUNDARY):
            labels[vendor].add(raw_label)
    by_vendor = {
        vendor: _spreadsheet_safe(_label_preview(
            sorted(values, key=lambda value: (value.casefold(), value))))
        for vendor, values in labels.items()
    }
    return {key: by_vendor.get(key[0], "") for key in keys}
