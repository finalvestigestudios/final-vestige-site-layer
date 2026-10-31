"""Deterministic, bounded invoice duplicate candidate discovery.

Exact-key anchors are independent of date; possible duplicates use a
chronological seven-day sliding window. No fraud claim is implied.
"""
from __future__ import annotations

from collections import defaultdict, deque
from datetime import date
from decimal import Decimal
import re
from typing import Any, Iterable

from .review import ascii_case_identity

WINDOW_DAYS = 7
MAX_CANDIDATES = 100_000
MAX_RECORDS = 200_000  # Matches the bounded CSV importer.
_PHYSICAL_ROW = re.compile(r"[1-9][0-9]{0,9}\Z", re.ASCII)
_NORMALIZED_KEY = re.compile(r"[A-Z0-9]+\Z", re.ASCII)


def _validated_records(records: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    """Check audit identity and exact money before building candidate groups.

    This public engine is also called without CSV import. Reject direct-call
    floats, nonfinite Decimals, unparseable physical line citations, and
    ambiguous duplicate source positions; never interpolate private values.
    """
    seen_rows: set[str] = set()
    for record in records:
        if len(seen_rows) >= MAX_RECORDS:
            raise ValueError("Too many invoice source records; no report was saved")
        if not isinstance(record, dict):
            raise ValueError("Invoice source record must be a mapping")
        source_row = record.get("row")
        if (not isinstance(source_row, str)
                or _PHYSICAL_ROW.fullmatch(source_row) is None
                or int(source_row) < 2):
            raise ValueError("Invoice source requires a canonical physical CSV row")
        if source_row in seen_rows:
            raise ValueError("Duplicate invoice physical CSV row; no report was saved")
        seen_rows.add(source_row)
        if type(record.get("dt")) is not date:
            raise ValueError("Candidate date must be a parsed calendar date")
        amount = record.get("amt")
        if not isinstance(amount, Decimal) or not amount.is_finite():
            raise ValueError("Invoice amount must be a finite exact Decimal")
        for field in ("v", "inv"):
            key = record.get(field)
            if not isinstance(key, str) or _NORMALIZED_KEY.fullmatch(key) is None:
                raise ValueError("Invoice vendor and invoice keys must be normalized ASCII")
        yield record


def candidate_pairs(records: Iterable[dict[str, Any]], *,
                    window_days: int = WINDOW_DAYS,
                    max_candidates: int = MAX_CANDIDATES
                    ) -> list[tuple[dict[str, Any], dict[str, Any], str, str]]:
    """Find exact and near invoice candidates without quadratic all-history scans.

    Callers provide normalized v and inv identifiers, amt as finite Decimal,
    dt as date, and unique original physical CSV rows. Exact normalized invoice
    groups use the first source row as a stable anchor. Near matches compare
    same-vendor/same-amount invoices only within window_days.

    In dense duplicate clusters the result itself can be quadratic.
    Fail closed with an explicit error once the report limit is reached;
    do not emit a partial report or claim completeness.
    """
    if type(window_days) is not int or not 0 <= window_days <= 365:
        raise ValueError("Duplicate window must be an integer between 0 and 365 days")
    if type(max_candidates) is not int or max_candidates < 1:
        raise ValueError("Candidate limit must be a positive integer")
    if max_candidates > MAX_CANDIDATES:
        raise ValueError(f"Candidate limit exceeds safety maximum of {MAX_CANDIDATES:,}")

    exact: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    by_amount: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for record in _validated_records(records):
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
        active_by_invoice: dict[str, deque[dict[str, Any]]] = {}
        for later in ordered:
            while active and (later["dt"] - active[0]["dt"]).days > window_days:
                expired = active.popleft()
                bucket = active_by_invoice[expired["inv"]]
                bucket.popleft()
                if not bucket:
                    del active_by_invoice[expired["inv"]]
            # Grouping active rows by invoice key avoids comparing a large
            # collection of identical recurring invoices against itself.
            # Cross-key comparisons still emit every potential review pair.
            for invoice_key, bucket in active_by_invoice.items():
                if invoice_key == later["inv"]:
                    continue
                for earlier in bucket:
                    add(earlier, later, "review_possible_duplicate",
                        f"same normalized vendor and amount within {window_days} days")
            active.append(later)
            active_by_invoice.setdefault(later["inv"], deque()).append(later)
    return results


def review_flags(a: dict[str, Any], b: dict[str, Any], status: str,
                 *, window_days: int = WINDOW_DAYS) -> str:
    """Surface sources of ambiguity without claiming fraudulent activity."""
    flags: list[str] = []
    if ascii_case_identity(a["vendor"]) != ascii_case_identity(b["vendor"]):
        flags.append("normalized_vendor_key_review")
    if (ascii_case_identity(a["invoice_number"]) != ascii_case_identity(b["invoice_number"])
            and status == "exact_invoice_key"):
        flags.append("normalized_invoice_key_review")
    if status == "exact_invoice_key":
        if a["amt"] != b["amt"]:
            flags.append("amount_variance_review")
        if abs((a["dt"] - b["dt"]).days) > window_days:
            flags.append("distant_dates_review")
    return ";".join(flags)
