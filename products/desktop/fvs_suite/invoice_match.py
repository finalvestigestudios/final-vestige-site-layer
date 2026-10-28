"""Deterministic, bounded invoice duplicate candidate discovery.

Exact-key anchors are independent of date; possible duplicates use a
chronological seven-day sliding window. No fraud claim is implied.
"""
from __future__ import annotations

from collections import defaultdict, deque
from datetime import date
from typing import Any, Iterable

WINDOW_DAYS = 7
MAX_CANDIDATES = 100_000


def candidate_pairs(records: Iterable[dict[str, Any]], *,
                    window_days: int = WINDOW_DAYS,
                    max_candidates: int = MAX_CANDIDATES
                    ) -> list[tuple[dict[str, Any], dict[str, Any], str, str]]:
    """Find exact and near invoice candidates without quadratic all-history scans.

    Callers provide normalized v and inv identifiers, amt as Decimal,
    dt as date, and original CSV row. Exact normalized invoice groups
    use the first source row as a stable anchor. Near matches compare
    same-vendor/same-amount invoices only within window_days.

    In dense duplicate clusters the result itself can be quadratic.
    Fail closed with an explicit error once the report limit is reached;
    do not emit a partial report or claim completeness.
    """
    if not isinstance(window_days, int) or not 0 <= window_days <= 365:
        raise ValueError("Duplicate window must be an integer between 0 and 365 days")
    if not isinstance(max_candidates, int) or max_candidates < 1:
        raise ValueError("Candidate limit must be a positive integer")

    exact: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    by_amount: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if not isinstance(record["dt"], date):
            raise ValueError("Candidate date must be a parsed calendar date")
        exact[(record["v"], record["inv"])].append(record)
        by_amount[(record["v"], record["amt"])].append(record)

    results: list[tuple[dict[str, Any], dict[str, Any], str, str]] = []

    def add(a: dict[str, Any], b: dict[str, Any], status: str, reason: str):
        if len(results) >= max_candidates:
            raise ValueError(
                f"Too many invoice review candidates (limit {max_candidates:,}). "
                "Narrow the input by vendor or date; no incomplete report was saved."
            )
        results.append((a, b, status, reason))

    for items in exact.values():
        first = items[0]
        for later in items[1:]:
            add(first, later, "exact_invoice_key",
                "same normalized vendor and invoice number")

    for items in by_amount.values():
        # Source-order tiebreaker makes pair order reproducible across runs.
        ordered = sorted(items, key=lambda r: (r["dt"], int(r["row"])))
        active: deque[dict[str, Any]] = deque()
        for later in ordered:
            while active and (later["dt"] - active[0]["dt"]).days > window_days:
                active.popleft()
            for earlier in active:
                # Same-key pairs are already represented by exact-key anchors.
                if earlier["inv"] != later["inv"]:
                    add(earlier, later, "review_possible_duplicate",
                        f"same normalized vendor and amount within {window_days} days")
            active.append(later)
    return results


def review_flags(a: dict[str, Any], b: dict[str, Any], status: str,
                 *, window_days: int = WINDOW_DAYS) -> str:
    """Surface sources of ambiguity without claiming fraudulent activity."""
    flags: list[str] = []
    if a["vendor"].casefold() != b["vendor"].casefold():
        flags.append("normalized_vendor_key_review")
    if a["invoice_number"].casefold() != b["invoice_number"].casefold() and status == "exact_invoice_key":
        flags.append("normalized_invoice_key_review")
    if status == "exact_invoice_key":
        if a["amt"] != b["amt"]:
            flags.append("amount_variance_review")
        if abs((a["dt"] - b["dt"]).days) > window_days:
            flags.append("distant_dates_review")
    return ";".join(flags)
