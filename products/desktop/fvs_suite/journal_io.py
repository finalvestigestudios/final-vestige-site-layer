"""Descriptor-checked local review evidence I/O for the two premium apps.

Never uploads records, signs/approves a review, or trusts a pathname alone.
The cooperating writer lock lives in exception_review. This module rejects
*observed* file substitution/changes; it is not a defence against privileged
filesystem adversaries or a guarantee that a file stays immutable afterward.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat
from typing import Callable


def _regular(info: os.stat_result, limit: int, kind: str) -> None:
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError(f"{kind} must be one regular file without aliases or links (not a symlink)")
    if info.st_size < 0 or info.st_size > limit:
        raise ValueError(f"{kind} exceeds its allowed size")


def _identity(info: os.stat_result) -> tuple[int, int]:
    return info.st_dev, info.st_ino


def _unchanged(before: os.stat_result, after: os.stat_result) -> bool:
    return (
        _identity(before) == _identity(after)
        and before.st_mode == after.st_mode
        and before.st_nlink == after.st_nlink
        and before.st_size == after.st_size
        and before.st_mtime_ns == after.st_mtime_ns
        and before.st_ctime_ns == after.st_ctime_ns
    )


def _same_path(path: Path, descriptor: os.stat_result, kind: str) -> None:
    try:
        current = os.lstat(path)
    except FileNotFoundError as exc:
        raise ValueError(f"{kind} path changed during access") from exc
    if (not stat.S_ISREG(current.st_mode) or current.st_nlink != 1
            or _identity(current) != _identity(descriptor)):
        raise ValueError(f"{kind} path changed during access")


def _flags(base: int) -> int:
    # O_NOFOLLOW is available on POSIX. Windows lacks it, so pre/post lstat
    # comparisons and descriptor identity checks are mandatory on both systems.
    return base | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)


def read_regular_bytes(path: str | Path, limit: int, kind: str) -> bytes:
    """Read at most ``limit`` bytes from a stable, non-aliased regular file.

    Use a pinned descriptor rather than stat(path) followed by open(path).
    Compare both the descriptor and the pathname before and after reading.
    """
    source = Path(path)
    initial = os.lstat(source)
    _regular(initial, limit, kind)
    descriptor = os.open(source, _flags(os.O_RDONLY))
    try:
        before = os.fstat(descriptor)
        _regular(before, limit, kind)
        if not _unchanged(initial, before):
            raise ValueError(f"{kind} changed before read")
        _same_path(source, before, kind)
        with os.fdopen(os.dup(descriptor), "rb") as stream:
            data = stream.read(limit + 1)
        after = os.fstat(descriptor)
        _regular(after, limit, kind)
        if len(data) > limit or not _unchanged(before, after):
            raise ValueError(f"{kind} changed during read or exceeded its size limit")
        _same_path(source, after, kind)
        return data
    finally:
        os.close(descriptor)


def append_verified_event(path: str | Path, data: bytes, limit: int,
                          verify: Callable[[], None]) -> None:
    """Append one validated JSONL event without following replaced journal paths.

    ``verify`` must revalidate the original report and the complete previous
    journal chain. It runs with the destination descriptor open but *before*
    writing. A noncooperating writer is detected when observed; all normal
    writers must still use exception_review's exclusive journal lock.
    """
    if not isinstance(data, bytes) or not data or data.count(b"\n") != 1 or not data.endswith(b"\n") or b"\x00" in data:
        raise ValueError("One newline-terminated review event is required")
    if len(data) > limit:
        raise ValueError("Review event exceeds journal size limit")
    target = Path(path)
    try:
        first = os.lstat(target)
    except FileNotFoundError:
        first = None
    if first is not None:
        _regular(first, limit, "Review journal")
    flags = os.O_WRONLY | os.O_APPEND
    if first is None:
        flags |= os.O_CREAT | os.O_EXCL
    descriptor = os.open(target, _flags(flags), 0o600)
    created = first is None
    wrote = False
    try:
        before = os.fstat(descriptor)
        _regular(before, limit, "Review journal")
        if first is not None and not _unchanged(first, before):
            raise ValueError("Review journal changed before append")
        if created and before.st_size != 0:
            raise ValueError("New review journal was not empty")
        _same_path(target, before, "Review journal")
        if before.st_size + len(data) > limit:
            raise ValueError("Review journal file-size limit reached")
        verify()
        verified = os.fstat(descriptor)
        _regular(verified, limit, "Review journal")
        if not _unchanged(before, verified):
            raise ValueError("Review journal changed while validating append")
        _same_path(target, verified, "Review journal")
        offset = 0
        while offset < len(data):
            count = os.write(descriptor, data[offset:])
            if count <= 0:
                raise OSError("Review journal write was incomplete")
            offset += count
            wrote = True
        os.fsync(descriptor)
        ending = os.fstat(descriptor)
        _regular(ending, limit, "Review journal")
        if ending.st_size != verified.st_size + len(data):
            raise ValueError("Review journal size changed during append")
        _same_path(target, ending, "Review journal")
    finally:
        os.close(descriptor)
        # Never leave an empty new journal after a pre-write verification error.
        # Do not remove a file that a concurrent actor has replaced or edited.
        if created and not wrote:
            try:
                current = os.lstat(target)
                if (stat.S_ISREG(current.st_mode)
                    and _identity(current) == _identity(before)
                    and current.st_size == 0):
                    os.unlink(target)
            except (FileNotFoundError, UnboundLocalError):
                pass
