"""Defense-in-depth check for formulas in locally exported financial CSV cells.

CSV quoting is not a spreadsheet formula escape. This predicate is an
additional publisher boundary; normal callers must still apply safe_cell.
It makes no compliance or financial approval decisions.
"""
from __future__ import annotations

import re
import unicodedata

# Excel-compatible importers may discard many format/control/combining marks
# when interpreting a cell. Inspect past these marks without changing evidence.
# An initial apostrophe is *not* ignored: it is an explicit sanitizer escape.
_IGNORABLE_CATEGORIES = frozenset(("Cf", "Cc", "Mn", "Me"))
_FORMULA_OPERATORS = frozenset("=+@")
# Align with engine.safe_cell's canonical negative Decimal exception. Allow
# only an ASCII integral/fractional literal: no expressions, names, exponents,
# grouping, currency signs or non-ASCII digits. Other minus values must first
# be escaped by the caller's sanitizer.
_CANONICAL_NEGATIVE_DECIMAL = re.compile(r"-[0-9]+(?:\.[0-9]+)?\Z", re.ASCII)


def has_unescaped_formula_prefix(value: str) -> bool:
    """Detect unescaped formula-like cells, including nonnumeric minus forms.

    Called only with built-in str, after size/type checks in the CSV publisher.
    Skip import-ignorable *leading* characters for inspection only. Preserve
    legitimate plain negative amounts and apostrophe-escaped source text.
    Inspect NFKC-compatible operator variants at the same leading boundary,
    but do not normalize or alter the exported evidence itself.
    """
    for index, char in enumerate(value):
        if char.isspace() or unicodedata.category(char) in _IGNORABLE_CATEGORIES:
            continue
        if char in _FORMULA_OPERATORS:
            return True
        if char == "-":
            return _CANONICAL_NEGATIVE_DECIMAL.fullmatch(value[index:]) is None
        # Some spreadsheet importers apply Unicode compatibility folds before
        # deciding whether a cell is a formula. Check the first meaningful
        # character's NFKC equivalent without rewriting the source evidence.
        # A compatibility-form minus is *never* a canonical ASCII Decimal
        # prefix: the sanitizer must explicitly escape it for review.
        compatibility = unicodedata.normalize("NFKC", char)
        return bool(compatibility and compatibility[0] in "=+@-")
    return False
