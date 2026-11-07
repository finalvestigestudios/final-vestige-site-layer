"""Single-link custody and leak-safe descriptor adoption for premium inventories.

This verifies the current filesystem view; it is neither a durable lock nor
proof of authentic financial source data. No evidence contents are logged.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import BinaryIO


def require_single_link(info: os.stat_result) -> None:
    """Fail closed on absent/ambiguous nlink evidence or hard-link aliases."""
    if info.st_nlink != 1:
        raise ValueError("Premium evidence must have exactly one file link")


def open_inventory_stream(path: Path, flags: int) -> BinaryIO:
    """Transfer one raw descriptor to a buffered stream without leaking on failure.

    The caller owns the returned stream and must close it (prefer a with block).
    Path and regular-file identity are checked by the caller before/after read.
    """
    fd = os.open(path, flags)
    try:
        return os.fdopen(fd, "rb")
    except BaseException:
        # fdopen can fail before it takes ownership; do not retain an open
        # handle to private inventory evidence after a failed adoption.
        try:
            os.close(fd)
        except OSError:
            pass  # Descriptor was already closed; retain the original error.
        raise
