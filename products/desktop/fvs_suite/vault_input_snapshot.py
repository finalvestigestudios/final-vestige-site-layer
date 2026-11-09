"""Bounded private descriptor snapshots for premium evidence-vault inputs.

A pathname is only a locator. Inspect the path without following links, open
one descriptor, then verify its identity/size/timestamps before and after a
bounded read. All expected operating-system failures become fixed diagnostics
outside their original exception handler: customer paths must not survive in
``__cause__`` or ``__context__``. No telemetry, uploads, or source mutations.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

CHUNK_BYTES = 1024 * 1024
_LABELS = frozenset(("Report", "Journal", "Encrypted archive"))


def _signature(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _same_path_and_descriptor(path_info: os.stat_result,
                              fd_info: os.stat_result) -> bool:
    """On Windows pathname and descriptor ctime can differ for the same file."""
    a, b = _signature(path_info), _signature(fd_info)
    return a[:-1] == b[:-1] if os.name == "nt" else a == b


def _metadata(path: Path, label: str) -> os.stat_result:
    failure = None
    try:
        info = path.lstat()
    except FileNotFoundError:
        failure = f"{label} must be an existing regular file, not a symlink"
    except OSError:
        failure = f"Cannot inspect {label.lower()} source"
    if failure is not None:
        raise ValueError(failure)
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"{label} must be an existing regular file, not a symlink")
    return info


def read_vault_input(path: str | Path, limit: int, label: str) -> bytes:
    """Read a stable non-link file into memory, refusing mutations and unsafe IO.

    A successful snapshot does not prove another program will not change the
    original *after* return; callers continue to bind SHA-256 to their report
    and journal and independently validate restored evidence. On Windows
    st_ctime differs between path and descriptor on some filesystems, but the
    full ctime signature is compared within each metadata view over time.
    """
    if label not in _LABELS or type(limit) is not int or limit < 0:
        raise ValueError("Invalid vault input contract")
    source = Path(path)
    initial = _metadata(source, label)
    if initial.st_size > limit:
        raise ValueError(f"{label} exceeds the size limit")

    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    open_failed = False
    try:
        descriptor = os.open(source, flags)
    except OSError:
        open_failed = True
    if open_failed:
        raise ValueError(f"Cannot safely open {label.lower()} source")

    read_failed = False
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or not _same_path_and_descriptor(initial, opened):
            raise ValueError(f"{label} changed while opening")
        parts: list[bytes] = []
        total = 0
        while True:
            part = os.read(descriptor, min(CHUNK_BYTES, limit - total + 1))
            if not part:
                break
            total += len(part)
            if total > limit:
                raise ValueError(f"{label} exceeds the size limit")
            parts.append(part)
        completed = os.fstat(descriptor)
        if total != opened.st_size or _signature(completed) != _signature(opened):
            raise ValueError(f"{label} changed while reading")
    except OSError:
        read_failed = True
    finally:
        try:
            os.close(descriptor)
        except OSError:
            read_failed = True
    if read_failed:
        raise ValueError(f"Cannot read {label.lower()} source")

    final = _metadata(source, label)
    if (_signature(final) != _signature(initial)
            or not _same_path_and_descriptor(final, opened)):
        raise ValueError(f"{label} path changed during reading")
    return b"".join(parts)
