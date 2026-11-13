"""Fail-closed input boundary for direct SpendMap Lite summarizer callers.

The normal CSV importer validates rows and sizes, but the reusable summarizer
can be called without that importer. Keep source-row evidence, amounts, and
vendor keys deterministic without reflecting confidential input in errors.
"""
from __future__ import annotations

from datetime import date
from decimal import Context, Decimal, localcontext
from types import MappingProxyType
import re
from typing import Callable, Iterator, Mapping

from .spend_callback_context_r355 import invoke_spend_callback
from .spend_source_custody_r356 import canonical_spend_source_cents, spend_parser_preserves_source
from .spend_date_custody_r359 import canonical_spend_source_date, spend_date_parser_preserves_source
from .spend_vendor_session_r360 import SpendVendorSession
from .spend_source_budget_r361 import SpendSourceBudget, MAX_SPEND_SOURCE_COLUMNS

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
    source_budget = SpendSourceBudget()
    for original in records:
        if not isinstance(original, dict):
            raise ValueError("Spend source record must be a mapping")
        if dict.__len__(original) > MAX_SPEND_SOURCE_COLUMNS:
            raise ValueError("Spend source column limit exceeded; no report was saved")
        if any(type(field) is not str for field in dict.keys(original)):
            raise ValueError("Spend source field names must be plain text")
        # The CSV entry path is byte-capped, but the direct list/dict API
        # previously allowed giant source/category/unused text fields. Check
        # every detached native cell and the aggregate UTF-8 budget before
        # invoking ANY externally supplied parsing or normalization callback.
        detached = dict(dict.items(original))
        source_budget.attest(detached)
        frozen_records.append(detached)

    # Validate all frozen source coordinates and required plain-text fields
    # before running ANY external parser callback or yielding ANY row. A late
    # malformed row must not cause partial report evidence or callback effects.
    seen_rows: set[str] = set()
    canonical_source_amounts: list[Decimal] = []
    canonical_source_dates: list[date] = []
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
        # CSV imports carry only native text. Even an unused extra column must
        # not smuggle a mutable object or a method-bearing str subclass into
        # the returned evidence record. Never invoke the object's methods.
        if any(type(value) is not str for value in record.values()):
            raise ValueError(f"Spend source column values must be plain text at physical row {physical_row}")
        # Verify original money before ANY supplied parser is invoked. A
        # callback must never replace an invalid future source cell with a
        # fabricated valid Decimal after earlier rows have been processed.
        failed_source_amount = False
        try:
            source_amount = canonical_spend_source_cents(record["amount"])
        except ValueError:
            failed_source_amount = True
        if failed_source_amount:
            raise ValueError(f"Invalid original spend amount at physical row {physical_row}")
        canonical_source_amounts.append(source_amount)
        # Verify original calendar facts before any external callback can
        # substitute a plausible but false month in the spend report.
        failed_source_date = False
        try:
            source_date = canonical_spend_source_date(record["date"])
        except ValueError:
            failed_source_date = True
        if failed_source_date:
            raise ValueError(f"Invalid original spend date at physical row {physical_row}")
        canonical_source_dates.append(source_date)

    # Private exceptions from original source validators and injected callbacks
    # must not survive through either __cause__ or __context__. In particular
    # 'raise ... from None' inside except would retain their source payloads.
    # Precompute every semantic result *before* yielding the first one.
    # Previously the first valid row escaped to a direct iterator consumer
    # before a later callback/date/Decimal failure became known. A consumer
    # could write partial evidence while believing it had validated the file.
    # The CSV-reader bound caps this additional in-memory result collection.
    # Callback side effects cannot be rolled back: callbacks must be trusted
    # and source authenticity remains a separate descriptor-verified concern.
    prepared_rows: list[tuple[Mapping[str, str], str, str, str, Decimal]] = []
    # Enforce one stable matching key for each ASCII-source-equivalent vendor
    # throughout this fully precomputed report. Never silently fragment totals.
    vendor_session = SpendVendorSession()
    for record, canonical_source_amount, canonical_source_day in zip(
            frozen_records, canonical_source_amounts, canonical_source_dates):
        physical_row = record["row"]
        category = record.get("category", "")
        failed_vendor = False
        try:
            vendor = invoke_spend_callback(normalize_vendor, record["vendor"])
        except Exception:
            failed_vendor = True
        if failed_vendor:
            raise ValueError(f"Invalid vendor at physical row {physical_row}")
        if type(vendor) is not str:
            raise ValueError(f"Invalid normalized vendor key at physical row {physical_row}")
        if vendor == "":
            # Preserve the original R59 message for the normal CSV pathway.
            raise ValueError("Blank vendor at row " + physical_row)
        if _VENDOR_KEY.fullmatch(vendor) is None:
            raise ValueError(f"Invalid normalized vendor key at physical row {physical_row}")
        vendor_session.attest(record["vendor"], vendor, physical_row)

        failed_date_parser = False
        try:
            calendar_day = invoke_spend_callback(parse_date, record["date"])
        except Exception:
            failed_date_parser = True
        if failed_date_parser:
            raise ValueError(f"Invalid spend date at physical row {physical_row}")
        if type(calendar_day) is not date:
            raise ValueError(f"Spend date must be a calendar date at physical row {physical_row}")
        if not spend_date_parser_preserves_source(canonical_source_day, calendar_day):
            raise ValueError(f"Spend parser changed original date at physical row {physical_row}")

        failed_money_parser = False
        try:
            amount = invoke_spend_callback(parse_money, record["amount"])
        except Exception:
            failed_money_parser = True
        if failed_money_parser:
            raise ValueError(f"Invalid spend amount at physical row {physical_row}")
        if type(amount) is not Decimal or not amount.is_finite():
            raise ValueError(f"Spend amount must be a finite exact Decimal at physical row {physical_row}")
        if not spend_parser_preserves_source(canonical_source_amount, amount):
            raise ValueError(f"Spend parser changed original amount at physical row {physical_row}")
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
        failed_cent_check = False
        try:
            # Direct helper callers may have a low/trapping Decimal context;
            # check cent equivalence under a private fixed-point context.
            with localcontext(Context(prec=64)):
                has_subcent = amount != amount.quantize(_CENT)
        except Exception:
            failed_cent_check = True
        if failed_cent_check:
            raise ValueError(f"Invalid cent precision at physical row {physical_row}")
        if has_subcent:
            raise ValueError(f"Spend amount must have cent precision at physical row {physical_row}")

        # A mutable record escaping here lets direct consumers rewrite the
        # physical line or source label *after* successful verification, while
        # leaving the parsed Decimal and associated file digest unchanged.
        # The dictionary is our private copied storage; expose read-only view.
        prepared_rows.append((MappingProxyType(record), vendor,
                              calendar_day.strftime("%Y-%m"),
                              category or "Uncategorized", amount))

    # No caller can consume or export a partially parsed source collection.
    yield from prepared_rows
