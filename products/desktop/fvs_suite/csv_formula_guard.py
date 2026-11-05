"""Defense-in-depth check for spreadsheet formulas in locally exported CSV cells.

CSV quoting is not a formula-escaping mechanism. The shared publisher must
reject unneutralized formulas even if a caller forgets to use its safe_cell
sanitizer. Keep negative amounts valid; this is not a compliance decision.
"""
from __future__ import annotations

# Some spreadsheet import paths trim leading whitespace or ignore formatting
# marks before interpreting =, + or @ as operators. Leading apostrophes are
# intentionally NOT skipped: they are a common explicit safe-cell escape.
_INVISIBLE_PREFIX = frozenset("\ufeff\u200b\u200c\u200d\u2060\u200e\u200f")
_FORMULA_OPERATORS = frozenset("=+@")


def has_unescaped_formula_prefix(value: str) -> bool:
    """Detect a formula after Unicode whitespace / invisible prefix marks.

    Call only with a built-in str, after the length/type checks in the CSV
    publisher. The publisher also requires a caller-owned safe-cell policy.
    """
    for char in value:
        if char.isspace() or char in _INVISIBLE_PREFIX:
            continue
        return char in _FORMULA_OPERATORS
    return False
