"""Publish complete, private CSV reports without overwriting existing evidence.

CSV rows are staged in a same-directory file so a failed conversion, interrupted
write, or full disk never leaves a misleading partial final report. Final
publication uses exclusive hard-link creation on POSIX and non-replacing rename
on Windows; both fail closed if a destination already exists. This is not an
all-or-nothing transaction for a multi-report package.
"""
from __future__ import annotations

import csv
import os
import tempfile
from pathlib import Path
from typing import Callable, Iterable, Mapping


def write_csv_report(destination: str | Path, fields: Iterable[str],
                     rows: Iterable[Mapping[str, object]],
                     cell: Callable[[object], str]) -> Path:
    """Write UTF-8-BOM CSV and publish only after the entire report is synced.

    ``cell`` must sanitize untrusted spreadsheet content. It is applied to
    every value, including ignored extra columns, as in the prior writer.
    Nothing ever overwrites an existing destination or follows its symlink.
    On a filesystem lacking the required safe publication operation, fail
    rather than silently fall back to an overwriting move.
    """
    target = Path(destination)
    if not target.parent.is_dir():
        raise ValueError("Choose an existing output folder")
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{target.stem}-", suffix=".partial", dir=target.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({name: cell(value) for name, value in row.items()})
            stream.flush()
            os.fsync(stream.fileno())
        if os.name == "nt":
            # Windows os.rename never replaces an existing destination.
            os.rename(temporary, target)
        else:
            # POSIX rename can overwrite; a hard link is exclusive and atomic.
            os.link(temporary, target)
            os.unlink(temporary)
        return target
    finally:
        # Failed writes and rejected destinations never leave partial reports.
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
