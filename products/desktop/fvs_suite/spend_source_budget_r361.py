"""Bound direct SpendMap source records before any caller-owned parser runs.

A CSV file is limited to 64 MiB, but direct summarize_spend callers can pass
in-memory source dictionaries without the CSV reader. Account for all retained
fields, including unused extras, so large labels or many columns cannot evade
that safety envelope or exhaust CSV evidence rendering. This is a resource
bound, not a source-authenticity claim.
"""
from __future__ import annotations

MAX_SPEND_SOURCE_COLUMNS = 64
MAX_SPEND_SOURCE_CELL_CHARS = 1_048_576
MAX_SPEND_SOURCE_TEXT_BYTES = 64 * 1024 * 1024
# A UTF-8 byte budget alone does not bound Python's per-field dictionary and
# evidence bookkeeping overhead: millions of tiny/empty fields may fit under
# 64 MiB yet require hundreds of MiB of container allocations. With the
# 200k-row cap this allows an average of 10 source columns per row.
MAX_SPEND_SOURCE_TOTAL_FIELDS = 2_000_000


class SpendSourceBudget:
    """One-report source-text AND field-count budget for detached native rows.

    The total counts every retained key/value and a two-byte-per-field framing
    allowance. It is NOT the original CSV byte length (which includes quoting,
    delimiters and discarded columns). The CSV path separately verifies and
    hashes the actual file snapshot. Failures never reveal a customer cell.
    """

    def __init__(self) -> None:
        self._used = 0
        self._fields = 0

    def attest(self, record: dict[str, str]) -> None:
        if type(record) is not dict or dict.__len__(record) > MAX_SPEND_SOURCE_COLUMNS:
            raise ValueError("Spend source column limit exceeded; no report was saved")
        count = dict.__len__(record)
        # Check BEFORE text encoding, copying into result sets or running any
        # external callback. Subtraction avoids oversized intermediate totals;
        # both counters are report-scoped and only advance on success.
        if count > MAX_SPEND_SOURCE_TOTAL_FIELDS - self._fields:
            raise ValueError("Spend source field-count limit exceeded; no report was saved")
        consumed = 0
        for field, value in dict.items(record):
            if type(field) is not str or type(value) is not str:
                raise ValueError("Spend source requires native UTF-8 text columns")
            if (len(field) > MAX_SPEND_SOURCE_CELL_CHARS
                    or len(value) > MAX_SPEND_SOURCE_CELL_CHARS):
                raise ValueError("Spend source cell size limit exceeded; no report was saved")
            invalid_utf8 = False
            try:
                # Encode one bounded cell at a time; lone surrogates and other
                # invalid UTF-8 source representations fail before callbacks.
                consumed += len(field.encode("utf-8")) + len(value.encode("utf-8")) + 2
            except UnicodeError:
                invalid_utf8 = True
            if invalid_utf8:
                # Raise outside the UnicodeError handler so private source
                # strings cannot remain reachable through __context__.
                raise ValueError("Spend source requires valid UTF-8 text") from None
            if consumed > MAX_SPEND_SOURCE_TEXT_BYTES - self._used:
                raise ValueError("Spend source text byte limit exceeded; no report was saved")
        self._used += consumed
        self._fields += count
