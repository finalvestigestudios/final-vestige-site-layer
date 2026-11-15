"""Pure, deterministic display-safety boundary for offline entitlement holders.

The holder is human-facing audit metadata, not a proof of legal identity. Keep
international visible letters intact while refusing invisible/control formatting
that can hide, reverse, or split a purported organization's displayed name.
No locale, I/O, telemetry, normalization rewrite or external dependencies.
"""
from __future__ import annotations

import unicodedata

MAX_HOLDER_CODEPOINTS = 120
# Cc: controls (including C1); Cf: zero-width and bidi formatting;
# Cs: unpaired surrogate; Zl/Zp: Unicode line/paragraph separators.
_UNSAFE_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Zl", "Zp"})


def valid_holder(value: object) -> bool:
    """Validate the exact text that will be signed and later displayed.

    Reject str subclasses before invoking their overridable methods. Do not
    silently normalize, modify, redact or conflate legal organization names.
    """
    if type(value) is not str:
        return False
    if not (1 <= len(value) <= MAX_HOLDER_CODEPOINTS) or value != value.strip():
        return False
    for ch in value:
        point = ord(ch)
        # Noncharacters cannot represent stable customer display identities.
        # Fixed codepoint ranges avoid Unicode-database-version differences.
        if 0xFDD0 <= point <= 0xFDEF or point & 0xFFFE == 0xFFFE:
            return False
        # Variation selectors can be invisible but still alter signed bytes.
        if 0xFE00 <= point <= 0xFE0F or 0xE0100 <= point <= 0xE01EF:
            return False
        category = unicodedata.category(ch)
        # Other Unicode spaces can look identical to ordinary U+0020 and
        # cause two visibly indistinguishable signed holder names to differ.
        if category in _UNSAFE_CATEGORIES or (category == "Zs" and ch != " "):
            return False
    return True
