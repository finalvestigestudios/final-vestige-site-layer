"""Local-only verification of desktop report outputs before announcing success.

This verifies only the GUI's immediately observable output contract, not the
content integrity, provenance or durability of engine reports. It never reads
financial data or writes, deletes, uploads, or retries a destination.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path


_MAX_REPORTS = 16
_NATIVE_PATH_TYPE = type(Path())


def confirm_report_files(outputs: object) -> tuple[Path, ...]:
    """Reject empty/malformed output inventories and missing/nonregular reports.

    Exact native Path objects avoid invoking user-defined path hooks. A single
    non-following ``stat`` checks each report leaf (rejecting links, directories
    and empty files). Checks are snapshots, not an atomic filesystem lease.
    Callers must keep a human inspection hold after ANY failed generation: an
    engine may have written an output before failing its final verification.
    """
    if type(outputs) not in (list, tuple) or not 1 <= len(outputs) <= _MAX_REPORTS:
        raise ValueError("Invalid generated report inventory")
    checked: list[Path] = []
    seen: set[Path] = set()
    for path in outputs:
        if type(path) is not _NATIVE_PATH_TYPE or not path.name or path in seen:
            raise ValueError("Invalid generated report path")
        info = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode) or info.st_size <= 0:
            raise ValueError("Generated report is not a nonempty regular file")
        seen.add(path)
        checked.append(path)
    return tuple(checked)
