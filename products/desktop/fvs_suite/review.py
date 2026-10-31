"""Deterministic, conservative matching labels for financial review tools.

Labels never assert compliance or authorize payment; every ambiguity remains
visible in the exported report, even when monetary totals happen to agree.
"""
from __future__ import annotations

from decimal import Decimal
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


def price_exceeds_tolerance(actual: Decimal, expected: Decimal) -> bool:
    """Maximum of one cent or 2% of expected value, with exact decimal math."""
    return abs(actual - expected) > max(Decimal("0.01"), abs(expected) * Decimal("0.02"))
