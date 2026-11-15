"""Canonical, display-safe labels for local premium evidence inventories.

Only file *basenames* are encoded. This is formatting validation, not a
signature, proof of source provenance, or authorization to approve a claim.
"""
from __future__ import annotations

import json
import unicodedata


def canonical_evidence_label(name: str) -> str:
    """Return exactly the inventory writer's ASCII JSON string-body encoding.

    Refuse invisible formatting, controls, surrogates, noncharacters, and path
    separators so human reviewers cannot confuse distinct evidence labels.
    Ordinary visible international filenames and ASCII spaces remain valid.
    """
    if (type(name) is not str or not name or name in (".", "..")
            or "/" in name or "\\" in name):
        raise ValueError("Invalid evidence filename label")
    for character in name:
        number = ord(character)
        kind = unicodedata.category(character)
        if (kind in {"Cc", "Cf", "Cs", "Zl", "Zp"}
                or (character.isspace() and character != " ")
                or 0xFDD0 <= number <= 0xFDEF
                or (number & 0xFFFE) == 0xFFFE):
            raise ValueError("Invalid evidence filename label")
    return json.dumps(name, ensure_ascii=True)[1:-1]
