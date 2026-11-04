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
# Match the lexical envelope of the shared financial CSV reader. Extreme
# Decimal zero exponents can bypass a value-only range/cent check, then turn
# into huge fixed-point review strings (or produce attacker-sized coefficients).
_MAX_SPEND_DIGITS = 80
_MIN_SPEND_EXPONENT = -80
_MAX_SPEND_EXPONENT = 12
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
    if type(records) is not list:
        raise ValueError("Spend source records must be a list")
    if len(records) > MAX_SPEND_ROWS:
        raise ValueError("Too many spend source records; no report was saved")
    # Freeze the *entire* direct-API collection before invoking any caller
    # callback. A normalizer/parser for the first row can otherwise mutate,
    # delete, append or reorder later caller-owned rows and forge the physical
    # CSV lines or amounts associated with the supplied source digest.
    # Copy native dict storage only: dict subclasses may override .items(),
    # .keys(), .get(), __getitem__ or iteration with unsafe side effects.
    frozen_records: list[dict[str, str]] = []
    for original in records:
        if not isinstance(original, dict):
            raise ValueError("Spend source record must be a mapping")
        if any(type(field) is not str for field in dict.keys(original)):
            raise ValueError("Spend source field names must be plain text")
        frozen_records.append(dict(dict.items(original)))

    # Validate all frozen source coordinates and required plain-text fields
    # before running ANY external parser callback or yielding ANY row. A late
    # malformed row must not cause partial report evidence or callback effects.
    seen_rows: set[str] = set()
    for record in frozen_records:
        physical_row = record.get("row")
        if (type(physical_row) is not str
                or _PHYSICAL_ROW.fullmatch(physical_row) is None
                or int(physical_row) < 2):
            raise ValueError("Spend source requires a canonical physical CSV row")
        if physical_row in seen_rows:
            raise ValueError("Duplicate spend physical CSV row; no report was saved")
        seen_rows.add(physical_row)
        for field in ("vendor", "date", "amount"):
            if type(record.get(field)) is not str:
                raise ValueError(f"Spend {field} must be imported text at physical row {physical_row}")
        category = record.get("category", "")
        if type(category) is not str:
            raise ValueError(f"Spend category must be imported text at physical row {physical_row}")

    # Precompute every semantic result *before* yielding the first one.
    # Previously the first valid row escaped to a direct iterator consumer
    # before a later callback/date/Decimal failure became known. A consumer
    # could write partial evidence while believing it had validated the file.
    # The CSV-reader bound caps this additional in-memory result collection.
    # Callback side effects cannot be rolled back: callbacks must be trusted
    # and source authenticity remains a separate descriptor-verified concern.
    prepared_rows: list[tuple[Mapping[str, str], str, str, str, Decimal]] = []
    for record in frozen_records:
        physical_row = record["row"]
        category = record.get("category", "")
        try:
            vendor = normalize_vendor(record["vendor"])
        except Exception:
            raise ValueError(f"Invalid vendor at physical row {physical_row}") from None
        if type(vendor) is not str:
            raise ValueError(f"Invalid normalized vendor key at physical row {physical_row}")
        if vendor == "":
            # Preserve the original R59 message for the normal CSV pathway.
            raise ValueError("Blank vendor at row " + physical_row)
        if _VENDOR_KEY.fullmatch(vendor) is None:
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
        if type(amount) is not Decimal or not amount.is_finite():
            raise ValueError(f"Spend amount must be a finite exact Decimal at physical row {physical_row}")
        # The CSV path uses engine.money (<= 1 trillion, rounded to cents).
        # Enforce the same finite fixed-point domain for direct callers so a
        # custom parser cannot bypass the 64-digit aggregation safety bound.
        if amount.copy_abs() > _MAX_SPEND_AMOUNT:
            raise ValueError(f"Spend amount exceeds permitted range at physical row {physical_row}")
        # A Decimal may be numerically zero while carrying an extreme exponent
        # or a very large trailing-zero coefficient. Check its representation
        # *before* quantization; no strings, unbounded formatting or rounding.
        parts = amount.as_tuple()
        if (len(parts.digits) > _MAX_SPEND_DIGITS
                or not _MIN_SPEND_EXPONENT <= parts.exponent <= _MAX_SPEND_EXPONENT):
            raise ValueError(
                f"Spend amount has unsupported numeric representation at physical row {physical_row}")
        if parts.exponent < 0 and any(parts.digits):
            trailing = 0
            for digit in reversed(parts.digits):
                if digit:
                    break
                trailing += 1
            if -parts.exponent - trailing > 2:
                raise ValueError(
                    f"Spend amount must have cent precision at physical row {physical_row}")
        try:
            # Direct helper callers may have a low/trapping Decimal context;
            # check cent equivalence under a private fixed-point context.
            with localcontext(Context(prec=64)):
                has_subcent = amount != amount.quantize(_CENT)
        except Exception:
            raise ValueError(f"Invalid cent precision at physical row {physical_row}") from None
        if has_subcent:
            raise ValueError(f"Spend amount must have cent precision at physical row {physical_row}")

        prepared_rows.append((record, vendor, calendar_day.strftime("%Y-%m"),
                              category or "Uncategorized", amount))

    # No caller can consume or export a partially parsed source collection.
    yield from prepared_rows
