"""Canonical, display-safe labels for local premium evidence inventories.

Only file *basenames* are encoded. This is formatting validation, not a
signature, proof of source provenance, or authorization to approve a claim.
"""
from __future__ import annotations

import json
import unicodedata

# Win32 device aliases, including ISO-8859-1 superscript port suffixes.
# These aliases remain reserved even when followed by a file extension.
_WINDOWS_DEVICES = frozenset({
    "CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$",
    *(f"COM{digit}" for digit in "123456789¹²³"),
    *(f"LPT{digit}" for digit in "123456789¹²³"),
})
_WINDOWS_FORBIDDEN = frozenset('<>:"/\\|?*')


def canonical_evidence_label(name: str) -> str:
    """Return one portable, ASCII-JSON-encoded evidence basename.

    Refuse invisible formatting, controls, surrogates, noncharacters, and path
    separators so human reviewers cannot confuse distinct evidence labels.
    Windows device aliases, alternate-data-stream punctuation and nonportable
    trailing/leading spaces are also refused. Visible international filenames
    and ordinary interior ASCII spaces remain valid.
    """
    if (type(name) is not str or not name or name in (".", "..")
            or len(name) > 255 or name.startswith(" ")
            or any(character in _WINDOWS_FORBIDDEN for character in name)
            or name.endswith((".", " "))):
        raise ValueError("Invalid evidence filename label")
    for character in name:
        number = ord(character)
        kind = unicodedata.category(character)
        if (kind in {"Cc", "Cf", "Cs", "Zl", "Zp"}
                or (character.isspace() and character != " ")
                or 0xFDD0 <= number <= 0xFDEF
                or (number & 0xFFFE) == 0xFFFE):
            raise ValueError("Invalid evidence filename label")
    # Win32 device lookup ignores the extension and spaces before it.
    stem = name.split(".", 1)[0].rstrip(" ").upper()
    if (stem in _WINDOWS_DEVICES
            or len(name.encode("utf-16-le")) // 2 > 255):
        raise ValueError("Invalid evidence filename label")
    return json.dumps(name, ensure_ascii=True)[1:-1]
