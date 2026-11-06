"""Deterministic native financial CSV cell input boundary.

Default engine exports must not execute caller-defined __str__/__format__ hooks,
forge evidence through subclasses, or materialize unlimited input text. This
checks source values BEFORE the shared spreadsheet sanitizer; the final writer
still independently checks rendered output, formulas and serialized byte caps.
"""
from __future__ import annotations

from decimal import Decimal

from .atomic_reports import MAX_REPORT_CELL_CHARS

# Native integers are permitted for record counts, but arbitrary giant Python
# integers must not trigger expensive conversion or Python's digit-limit error.
_MAX_NATIVE_INT_BITS = 269


def native_report_text(value: object) -> str:
    """Accept only owned str/int/Decimal, never caller-controlled coercion.

    Decimal values retain their exact decimal string, including trailing zeros;
    no binary float conversions or financial compliance decisions are made.
    """
    if type(value) is str:
        text = value
    elif type(value) is int:
        if value.bit_length() > _MAX_NATIVE_INT_BITS:
            raise ValueError("Invalid native CSV report cell")
        text = str(value)
    elif type(value) is Decimal:
        if not value.is_finite() or len(value.as_tuple().digits) > MAX_REPORT_CELL_CHARS:
            raise ValueError("Invalid native CSV report cell")
        text = str(value)
    else:
        raise ValueError("Invalid native CSV report cell")
    if len(text) > MAX_REPORT_CELL_CHARS:
        raise ValueError("CSV report cell size limit exceeded")
    return text
