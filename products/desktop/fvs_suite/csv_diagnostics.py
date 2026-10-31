"""Stable, privacy-preserving diagnostics for shared financial CSV imports.

Error strings intentionally never interpolate source paths, filenames, CSV cells,
column *values*, or exception messages. Only allowlisted schema names and
validated physical line numbers are included. Do not log raw parser exceptions.
"""
from __future__ import annotations

_FIELDS = frozenset({
    "id", "amount", "vendor", "invoice_number", "date", "category",
    "program", "budget", "po_number", "line", "quantity", "unit_price",
    "event_type", "document_id", "related_document", "ledger_reference",
    "claim_type", "related_claim",
})
_MESSAGES = {
    "select_file": "Select an existing CSV input",
    "bad_header": "CSV input: invalid CSV header",
    "missing_headers": "CSV input: Missing headers",
    "nul_header": "CSV input: CSV header contains a NUL character",
    "duplicate_header": "CSV input: blank or duplicate normalized CSV header",
    "bad_record": "CSV input: invalid CSV near physical line",
    "nul_record": "CSV input: CSV record contains a NUL character at physical line",
    "bad_row_shape": "CSV input: malformed CSV record at physical line",
    "blank_ledger_id": "Blank transaction ID at physical CSV row",
    "alias_ambiguous": "CSV input: ambiguous",
    "column_missing": "CSV input: missing",
}


def _line(value: object) -> str:
    """A parser-derived physical line only; never stringify untrusted objects."""
    return str(value) if type(value) is int and 1 <= value <= 1_000_000_000 else "unknown"


def _column_count(value: object) -> str:
    return str(value) if type(value) is int and 0 <= value <= 10_000 else "unknown"


def csv_input_error(kind: str, *, field: object = None,
                    line: object = None, expected: object = None,
                    actual: object = None) -> ValueError:
    """Construct a safe, deterministic ValueError without consulting CSV data.

    Field references must be recognized *internal schema keys*, never copied
    from imported headers. Invalid metadata becomes a generic marker instead
    of being interpolated into financial diagnostics.
    """
    if type(kind) is not str or kind not in _MESSAGES:
        return ValueError("CSV input: invalid CSV")
    message = _MESSAGES[kind]
    if kind == "alias_ambiguous":
        label = field if type(field) is str and field in _FIELDS else "required"
        message += f" '{label}' aliases"
    elif kind == "column_missing":
        label = field if type(field) is str and field in _FIELDS else "required"
        message += f" '{label}' column"
    elif kind in ("bad_record", "nul_record", "bad_row_shape", "blank_ledger_id"):
        message += " " + _line(line)
        if kind == "bad_row_shape":
            message += (f" (expected {_column_count(expected)} columns, "
                        f"got {_column_count(actual)})")
    return ValueError(message)
