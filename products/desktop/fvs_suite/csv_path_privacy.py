"""Private, non-destructive financial CSV pathname preflight.

A successful preflight is not source authorization: csv_snapshot.read_csv_snapshot
must still enforce descriptor identity, no-link and mutation checks. Errors are
translated after leaving the originating exception handler, so an OSError's
private filename is not retained in ValueError.__context__.
"""
from __future__ import annotations

from os import PathLike
from pathlib import Path

from .csv_diagnostics import csv_input_error


def checked_csv_path(value: str | PathLike[str]) -> Path:
    """Preserve the existing CSV file-selection contract without path leaks.

    The returned Path is only a locator. The caller must independently verify
    and snapshot the actual opened file descriptor; is_file() is not a lock.
    """
    rejected = False
    try:
        path = Path(value)
        if path.suffix.lower() != ".csv" or not path.is_file():
            rejected = True
    except (OSError, ValueError, TypeError):
        rejected = True
    if rejected:
        raise csv_input_error("select_file")
    return path
