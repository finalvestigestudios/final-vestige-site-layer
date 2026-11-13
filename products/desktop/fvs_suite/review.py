"""Deterministic, conservative matching labels for financial review tools.

Labels never assert compliance or authorize payment; every ambiguity remains
visible in the exported report, even when monetary totals happen to agree.
"""
from __future__ import annotations

from decimal import Context, Decimal, localcontext
from typing import Iterable, Mapping

from .audit_display import visible_source_text


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
    """Keep distinct original source spellings without lossy whitespace trimming.

    Boundary whitespace can distinguish two names or IDs which share a
    normalized matching key. Discard only truly absent/empty labels, never
    a literal whitespace-only source field. Reject nonnative values rather
    than evaluating potentially sensitive customer-defined __str__ methods.
    """
    found: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("Source review rows must be mappings")
        value = row.get(field, "")
        if type(value) is not str:
            raise ValueError("Source identity label must be text")
        if value:
            found.add(value)
    return tuple(sorted(found, key=lambda s: (s.casefold(), s)))


def _visible_identity_label(value: str) -> str:
    """Render boundary ASCII spaces as explicit escapes, not ambiguous padding.

    Literal backslashes are escaped by visible_source_text, so real spaces
    remain distinct from a source spelling containing the characters \\u0020.
    """
    leading = len(value) - len(value.lstrip(" "))
    tail = value[leading:]
    trailing = len(tail) - len(tail.rstrip(" "))
    middle = tail[:-trailing] if trailing else tail
    return (r"\u0020" * leading
            + visible_source_text(middle).replace(";", r"\u003B")
            + r"\u0020" * trailing)


def labels_for_report(rows: Iterable[Mapping[str, str]], field: str) -> str:
    """Display each exact source label; human review, never an approval decision.

    Source SHA-256 and physical rows remain authoritative. Explicit boundary
    spaces and escaped separators distinguish visually similar identities.
    """
    return "; ".join(_visible_identity_label(label) for label in raw_values(rows, field))


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
# Source prices and quantities have at most eight decimal places each;
# their exact extended totals therefore need at most sixteen. Price-policy
# fractions have at most eight. The direct API must enforce the same finite
# fixed-point domain, rather than trusting a 64-digit context to preserve
# arbitrarily long Decimal coefficients supplied by outside callers.
_PRICE_OPERAND_MAX_PLACES = 16
_POLICY_FRACTION_MAX_PLACES = 8
_PRICE_OPERAND_MAX_DIGITS = 64


def _price_operand_scale_valid(value: Decimal, max_places: int) -> bool:
    """Validate a Decimal coefficient without rounding or caller context.

    Trailing zeroes do not add significant fractional precision. A digit cap
    also prevents a direct caller from supplying unbounded coefficients that
    could exhaust resources or escape the 64-digit exact-arithmetic envelope.
    """
    digits = value.as_tuple().digits
    exponent = value.as_tuple().exponent
    if (len(digits) > _PRICE_OPERAND_MAX_DIGITS
            or exponent < -_PRICE_OPERAND_MAX_DIGITS or exponent > 27):
        return False
    if exponent >= 0 or not any(digits):
        return True
    trailing = 0
    for digit in reversed(digits):
        if digit != 0:
            break
        trailing += 1
    return -exponent - trailing <= max_places


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
            or fraction < 0 or fraction > 1
            or any(not _price_operand_scale_valid(value, _PRICE_OPERAND_MAX_PLACES)
                   for value in (actual, expected, absolute))
            or not _price_operand_scale_valid(fraction, _POLICY_FRACTION_MAX_PLACES)):
        raise ValueError("Price tolerance operands exceed suite review bounds")
    with localcontext(Context(prec=64)):
        deviation = (actual - expected).copy_abs()
        threshold = max(absolute, expected.copy_abs() * fraction)
        return deviation > threshold


def price_exceeds_tolerance(actual: Decimal, expected: Decimal) -> bool:
    """Legacy one-cent-or-2% review flag; never financial authorization."""
    return price_outside_tolerance(
        actual, expected, Decimal("0.01"), Decimal("0.02"))
