"""Privacy-preserving, fixed-point intake for ProcureGuard review controls.

No parsing path prints source financial fields or makes an approval decision.
"""
from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Mapping

# Price tolerances are explicit, ASCII, fixed-point decimals. The engine's
# quantity and unit-price inputs already cap precision at eight places.
_POLICY_DECIMAL = re.compile(r"(?:0|[1-9][0-9]{0,2})(?:\.[0-9]{1,8})?\Z")
_ROW_NUMBER = re.compile(r"[0-9]{1,9}\Z")
_EVENT_TYPES = {
    "invoice": frozenset(("invoice", "credit")),
    "receipt": frozenset(("receipt", "return")),
}


def exact_policy_limit(value: object, name: str, maximum: Decimal) -> Decimal:
    """Reject surprising JSON threshold syntax before interpreting money.

    No exponent, sign, leading zero, whitespace, Unicode digit, excessive
    precision, boolean, float or unbounded numeric text is accepted.
    """
    if isinstance(value, (bool, float)) or not isinstance(value, (str, int)):
        raise ValueError(f"{name} must be an ASCII fixed-point decimal string or integer")
    raw = str(value)
    if len(raw) > 16 or _POLICY_DECIMAL.fullmatch(raw) is None:
        raise ValueError(f"{name} must be an ASCII fixed-point decimal with at most eight places")
    try:
        result = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"{name} has invalid decimal syntax") from exc
    if not result.is_finite() or result > maximum:
        raise ValueError(f"{name} must be between zero and the documented maximum")
    return result


def event_kind(row: Mapping[str, str], *, source: str) -> str:
    """Classify an explicit movement, without reflecting private CSV values."""
    if source not in _EVENT_TYPES:
        raise ValueError("Unsupported procurement event stream")
    value = str(row.get("event_type", "") or source).strip().casefold()
    if value not in _EVENT_TYPES[source]:
        raw_line = str(row.get("row", "?"))
        line = raw_line if _ROW_NUMBER.fullmatch(raw_line) else "?"
        raise ValueError(f"Unsupported {source} event_type at input physical row {line}")
    return value
