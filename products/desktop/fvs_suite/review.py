"""Deterministic, conservative matching labels for financial review tools.

Labels never assert compliance or authorize payment; every ambiguity remains
visible in the exported report, even when monetary totals happen to agree.
"""
from __future__ import annotations

from decimal import Context, Decimal, localcontext
from typing import Iterable, Mapping


_ASCII_CASE_TABLE = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")


def ascii_case_identity(value: str) -> str:
    """Ignore ASCII letter case without folding distinct Unicode source labels.

    Unicode ``casefold``/``upper`` may expand visually different identifiers
    (e.g. LONG S -> s, SHARP S -> ss). Those labels must trigger human review
    when a lossy matching key groups them; do not declare them identical.
    """
    if type(value) is not str:
        raise ValueError("Source identity label must be text")
    return value.translate(_ASCII_CASE_TABLE)


def raw_values(rows: Iterable[Mapping[str, str]], field: str) -> tuple[str, ...]:
    """Return distinct, nonblank source labels, preserving exact spelling."""
    return tuple(sorted({str(row.get(field, "")).strip() for row in rows
                         if str(row.get(field, "")).strip()}, key=lambda s: (s.casefold(), s)))


def labels_for_report(rows: Iterable[Mapping[str, str]], field: str) -> str:
    """Show original keys, never only the lossy normalized matching key."""
    return "; ".join(raw_values(rows, field))


def normalized_collision(rows: Iterable[Mapping[str, str]], field: str) -> bool:
    """Ignore ASCII case only; any other normalized identity change needs review."""
    return len({ascii_case_identity(value) for value in raw_values(rows, field)}) > 1


def reconciliation_status(left: list[dict[str, str]], right: list[dict[str, str]],
                          left_total: Decimal, right_total: Decimal, *,
                          missing_left: str, missing_right: str,
                          fields: tuple[tuple[str, str], ...] = (("id", "normalized_id_review"),),
                          duplicate: str = "duplicate_id_review") -> str:
    """Keep every independent finding, including variances on duplicate keys."""
    if not left:
        return missing_left
    if not right:
        return missing_right
    findings = []
    if len(left) != 1 or len(right) != 1:
        findings.append(duplicate)
    combined = [*left, *right]
    for field, tag in fields:
        if normalized_collision(combined, field):
            findings.append(tag)
    if left_total != right_total:
        findings.append("variance")
    return ";".join(findings) or "matched"


# Up to 200,000 invoiced units/lines can produce totals far above 1e12.
# Keep the exact documented procurement aggregation envelope (<= 2e26).
_PRICE_LIMIT = Decimal("1000000000000000000000000000")


def price_outside_tolerance(actual: Decimal, expected: Decimal,
                            absolute: Decimal, fraction: Decimal) -> bool:
    """Evaluate review thresholds exactly, including when called directly.

    All four operands must be bounded, finite Decimal values. A private
    context makes the comparison independent of caller rounding, traps and
    exponent limits. This is a review flag, never authorization for payment.
    """
    values = (actual, expected, absolute, fraction)
    if any(type(value) is not Decimal or not value.is_finite() for value in values):
        raise ValueError("Price tolerance requires finite exact Decimal values")
    if (actual.copy_abs() > _PRICE_LIMIT or expected.copy_abs() > _PRICE_LIMIT
            or absolute < 0 or absolute > _PRICE_LIMIT
            or fraction < 0 or fraction > 1):
        raise ValueError("Price tolerance operands exceed suite review bounds")
    with localcontext(Context(prec=64)):
        deviation = (actual - expected).copy_abs()
        threshold = max(absolute, expected.copy_abs() * fraction)
        return deviation > threshold


def price_exceeds_tolerance(actual: Decimal, expected: Decimal) -> bool:
    """Legacy one-cent-or-2% review flag; never financial authorization."""
    return price_outside_tolerance(
        actual, expected, Decimal("0.01"), Decimal("0.02"))
