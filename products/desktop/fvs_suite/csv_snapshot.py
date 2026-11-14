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
# Absolute intake ceiling for every finance CSV consumer, independent of caller.
MAX_SNAPSHOT_BYTES = 64 * 1024 * 1024


def _signature(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _same_path_descriptor_signature(path_info: os.stat_result,
                                    descriptor_info: os.stat_result,
                                    *, windows: bool | None = None) -> bool:
    """Compare two API views without treating Windows ctime as portable identity.

    On Windows, pathname lstat and descriptor fstat can disagree about creation
    time for the same file. All other identity fields must match across views.
    Each view's *full* signature, including ctime, is checked independently
    before/after reading; this never ignores an observed mutation.
    """
    if windows is None:
        windows = os.name == "nt"
    path_sig = _signature(path_info)
    descriptor_sig = _signature(descriptor_info)
    return path_sig[:-1] == descriptor_sig[:-1] if windows else path_sig == descriptor_sig


def _metadata(path: Path) -> os.stat_result:
    failure = None
    try:
        info = path.lstat()
    except FileNotFoundError:
        failure = "CSV input file is missing"
    except OSError:
        failure = "Cannot inspect CSV input"
    # Raise *after* leaving the handler: `from None` alone suppresses display
    # but retains the customer's private path in exception.__context__.
    if failure is not None:
        raise ValueError(failure)
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("CSV input must be a regular file, not a link")
    return info


def read_csv_snapshot(path: str | Path, maximum: int) -> bytes:
    """Return stable raw source bytes, never opening links or unbounded streams.

    Checks exact opened-descriptor identity against the original and final
    pathname; checks size and timestamps before and after the bounded read.
    A malicious actor can still defeat metadata checks or edit after return.
    """
    # Fail before path conversion, stat or open. NaN/infinity and int subclasses
    # could otherwise disable the bound or invoke caller-controlled methods.
    if type(maximum) is not int or not (0 <= maximum <= MAX_SNAPSHOT_BYTES):
        raise ValueError("Invalid CSV input size limit")
    source = Path(path)
    before = _metadata(source)
    if before.st_size > maximum:
        raise ValueError("CSV input exceeds 64 MiB file-size limit")
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    open_failed = False
    try:
        descriptor = os.open(source, flags)
    except Exception:
        open_failed = True
    if open_failed:
        # The originating OS exception must no longer be the active handler.
        raise ValueError("Cannot safely open CSV input")
    try:
        adoption_failed = False
        try:
            stream = os.fdopen(descriptor, "rb")
        except BaseException as exc:
            # If fdopen did not assume ownership, close our raw handle even
            # for interrupts, without replacing a KeyboardInterrupt/SystemExit.
            try:
                os.close(descriptor)
            except OSError:
                pass
            if isinstance(exc, Exception) and not isinstance(exc, MemoryError):
                adoption_failed = True
            else:
                raise
        if adoption_failed:
            raise ValueError("Cannot read CSV input")
        with stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or not _same_path_descriptor_signature(before, opened):
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
        read_failed = True
    else:
        read_failed = False
    if read_failed:
        # No private exception (or its traceback) is retained in the chain.
        raise ValueError("Cannot read CSV input")
    after_path = _metadata(source)
    if (_signature(after_path) != _signature(before)
            or not _same_path_descriptor_signature(after_path, opened)):
        raise ValueError("CSV input path changed during reading")
    return b"".join(chunks)
