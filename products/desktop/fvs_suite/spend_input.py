"""Fail-closed input boundary for direct SpendMap Lite summarizer callers.

The normal CSV importer validates rows and sizes, but the reusable summarizer
can be called without that importer. Keep source-row evidence, amounts, and
vendor keys deterministic without reflecting confidential input in errors.
"""
from __future__ import annotations

from datetime import date
from decimal import Context, Decimal, localcontext
import re
from typing import Callable, Iterator, Mapping

MAX_SPEND_ROWS = 200_000  # Mirrors the bounded shared financial CSV reader.
_PHYSICAL_ROW = re.compile(r"[1-9][0-9]{0,9}\Z", re.ASCII)
_VENDOR_KEY = re.compile(r"[A-Z0-9]+\Z", re.ASCII)
_MAX_SPEND_AMOUNT = Decimal("1000000000000")
_CENT = Decimal("0.01")


def validated_spend_rows(
    records: list[dict[str, str]], *,
    normalize_vendor: Callable[[str], str],
    parse_date: Callable[[str], object],
    parse_money: Callable[[str], Decimal],
) -> Iterator[tuple[Mapping[str, str], str, str, str, Decimal]]:
    """Parse evidence-bearing input exactly once and reject invalid direct calls.

    Preserve input order and original vendor labels for review; never coerce a
    float to Decimal or echo an untrusted cell in an exception. This function
    is not a CSV authenticity check: the caller must supply a digest from the
    *same* descriptor-verified byte snapshot as its records.
    """
    if not isinstance(records, list):
        raise ValueError("Spend source records must be a list")
    if len(records) > MAX_SPEND_ROWS:
        raise ValueError("Too many spend source records; no report was saved")
    seen_rows: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Spend source record must be a mapping")
        physical_row = record.get("row")
        if (not isinstance(physical_row, str)
                or _PHYSICAL_ROW.fullmatch(physical_row) is None
                or int(physical_row) < 2):
            raise ValueError("Spend source requires a canonical physical CSV row")
        if physical_row in seen_rows:
            raise ValueError("Duplicate spend physical CSV row; no report was saved")
        seen_rows.add(physical_row)
        for field in ("vendor", "date", "amount"):
            if not isinstance(record.get(field), str):
                raise ValueError(f"Spend {field} must be imported text at physical row {physical_row}")
        category = record.get("category", "")
        if not isinstance(category, str):
            raise ValueError(f"Spend category must be imported text at physical row {physical_row}")

        try:
            vendor = normalize_vendor(record["vendor"])
        except Exception:
            raise ValueError(f"Invalid vendor at physical row {physical_row}") from None
        if vendor == "":
            # Preserve the original R59 message for the normal CSV pathway.
            raise ValueError("Blank vendor at row " + physical_row)
        if not isinstance(vendor, str) or _VENDOR_KEY.fullmatch(vendor) is None:
            raise ValueError(f"Invalid normalized vendor key at physical row {physical_row}")

        try:
            calendar_day = parse_date(record["date"])
        except Exception:
            raise ValueError(f"Invalid spend date at physical row {physical_row}") from None
        if type(calendar_day) is not date:
            raise ValueError(f"Spend date must be a calendar date at physical row {physical_row}")

        try:
            amount = parse_money(record["amount"])
        except Exception:
            raise ValueError(f"Invalid spend amount at physical row {physical_row}") from None
        if not isinstance(amount, Decimal) or not amount.is_finite():
            raise ValueError(f"Spend amount must be a finite exact Decimal at physical row {physical_row}")
        # The CSV path uses engine.money (<= 1 trillion, rounded to cents).
        # Enforce the same finite fixed-point domain for direct callers so a
        # custom parser cannot bypass the 64-digit aggregation safety bound.
        if amount.copy_abs() > _MAX_SPEND_AMOUNT:
            raise ValueError(f"Spend amount exceeds permitted range at physical row {physical_row}")
        try:
            # Direct helper callers may have a low/trapping Decimal context;
            # check cent equivalence under a private fixed-point context.
            with localcontext(Context(prec=64)):
                has_subcent = amount != amount.quantize(_CENT)
        except Exception:
            raise ValueError(f"Invalid cent precision at physical row {physical_row}") from None
        if has_subcent:
            raise ValueError(f"Spend amount must have cent precision at physical row {physical_row}")

        yield (record, vendor, calendar_day.strftime("%Y-%m"),
               category or "Uncategorized", amount)
