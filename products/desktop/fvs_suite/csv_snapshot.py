"""Bounded, immutable-in-memory snapshot of one local financial CSV input.

An input is read once from one regular-file descriptor. This rejects common
symlink/path replacement, concurrent edit and growth races before parsing.
The resulting bytes are a point-in-time snapshot, *not* a filesystem lock or
proof the file remains unchanged for a later inventory step.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

CHUNK_BYTES = 1024 * 1024


def _signature(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _metadata(path: Path) -> os.stat_result:
    try:
        info = path.lstat()
    except FileNotFoundError:
        raise ValueError("CSV input file is missing") from None
    except OSError:
        raise ValueError("Cannot inspect CSV input") from None
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("CSV input must be a regular file, not a link")
    return info


def read_csv_snapshot(path: str | Path, maximum: int) -> bytes:
    """Return stable raw source bytes, never opening links or unbounded streams.

    Checks exact opened-descriptor identity against the original and final
    pathname; checks size and timestamps before and after the bounded read.
    A malicious actor can still defeat metadata checks or edit after return.
    """
    if maximum < 0:
        raise ValueError("Invalid CSV input size limit")
    source = Path(path)
    before = _metadata(source)
    if before.st_size > maximum:
        raise ValueError("CSV input exceeds 64 MiB file-size limit")
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        descriptor = os.open(source, flags)
    except OSError:
        raise ValueError("Cannot safely open CSV input") from None
    try:
        try:
            stream = os.fdopen(descriptor, "rb")
        except OSError:
            os.close(descriptor)
            raise
        with stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or _signature(opened) != _signature(before):
                raise ValueError("CSV input changed while opening")
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = stream.read(min(CHUNK_BYTES, maximum - total + 1))
                if not chunk:
                    break
                total += len(chunk)
                if total > maximum:
                    raise ValueError("CSV input exceeds 64 MiB file-size limit")
                chunks.append(chunk)
            closed = os.fstat(stream.fileno())
            if total != opened.st_size or _signature(closed) != _signature(opened):
                raise ValueError("CSV input changed while reading")
    except OSError:
        raise ValueError("Cannot read CSV input") from None
    if _signature(_metadata(source)) != _signature(opened):
        raise ValueError("CSV input path changed during reading")
    return b"".join(chunks)
