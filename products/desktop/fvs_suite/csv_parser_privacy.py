"""Fail-closed CSV iteration without exposing private parser exception chains.

R297: a caught UnicodeDecodeError can retain the complete source byte buffer in
`exception.object`; `raise safe_error from None` inside its except block only
hides that error in formatted output, leaving it reachable via `__context__`.
The raised diagnostics below occur *after* their exception handlers finish.
"""
from __future__ import annotations

import csv
from collections.abc import Iterator

from .csv_diagnostics import csv_input_error


def safe_csv_header(reader: Iterator[list[str]]) -> list[str] | None:
    """Read a header once, preserving None for an empty source."""
    failed = False
    try:
        header = next(reader, None)
    except (csv.Error, UnicodeError):
        failed = True
    if failed:
        raise csv_input_error("bad_header")
    return header


def safe_csv_rows(reader: Iterator[list[str]]) -> Iterator[list[str]]:
    """Yield records lazily; report only the parser's bounded physical line.

    Regular EOF, arbitrary row contents, ordering and reader.line_num are
    unchanged. The caller still performs its own shape, NUL and row-limit gates.
    """
    while True:
        failed = False
        exhausted = False
        try:
            row = next(reader)
        except StopIteration:
            exhausted = True
        except (csv.Error, UnicodeError):
            failed = True
        if failed:
            raise csv_input_error("bad_record", line=reader.line_num)
        if exhausted:
            return
        yield row
