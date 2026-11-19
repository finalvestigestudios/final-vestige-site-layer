"""Reject invalid LedgerDiff CSV mappings before reading either private source.

This is configuration validation only, not column existence or reconciliation.
The CSV importer continues to resolve real headers and make audit decisions.
"""
from __future__ import annotations

import re

_COLUMN = re.compile(r"[a-z_][a-z0-9_]{0,127}\Z", re.ASCII)


def _column_name(value, label: str) -> str | None:
    if value is None:
        return None
    # Match table()'s existing canonicalization without consulting caller
    # methods on strings/subclasses or echoing private header values.
    if type(value) is not str:
        raise ValueError(f"Invalid explicit ledger {label} column")
    normalized = value.strip().lower().replace(" ", "_")
    if _COLUMN.fullmatch(normalized) is None:
        raise ValueError(f"Invalid explicit ledger {label} column")
    return normalized


def preflight_ledger_overrides(*, left_match_column=None, right_match_column=None,
                               left_amount_column=None, right_amount_column=None) -> None:
    """Fail closed for all four mappings before opening LEFT or RIGHT CSV.

    Each source is independent: matching header names on opposite sources
    are allowed; match/amount aliases on the *same* source must be distinct.
    Real input-specific collisions remain the importer's responsibility.
    """
    for match, amount in (
            (left_match_column, left_amount_column),
            (right_match_column, right_amount_column)):
        normalized_match = _column_name(match, "match")
        normalized_amount = _column_name(amount, "amount")
        if normalized_match is not None and normalized_match == normalized_amount:
            raise ValueError("Ledger match and amount must use distinct CSV columns")
