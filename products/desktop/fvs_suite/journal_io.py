"""Descriptor-checked local review evidence I/O for the two premium apps.

Never uploads records, signs/approves a review, or trusts a pathname alone.
The cooperating writer lock lives in exception_review. This module rejects
*observed* file substitution/changes; it is not a defence against privileged
filesystem adversaries or a guarantee that a file stays immutable afterward.
"""
from __future__ import annotations

from functools import wraps
import os
from pathlib import Path
import stat
from typing import Callable

from .csv_snapshot import _same_path_descriptor_signature
from .journal_write_receipt import require_exact_append_readback, digest_pinned_prefix
from .journal_fd_read import read_bounded_duplicate


def _redact_os_errors(message: str):
    """Drop sensitive OS-error paths from messages and exception chains.

    Raise only after leaving the handler: ``from None`` still retains
    ``__context__`` and can expose a financial evidence pathname to callers.
    Ordinary domain ValueErrors and interrupts are not translated.
    """
    def decorate(func):
        @wraps(func)
        def guarded(*args, **kwargs):
            failed = False
            try:
                return func(*args, **kwargs)
            except OSError:
                failed = True
            if failed:
                raise ValueError(message)
        return guarded
    return decorate


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


def _same_path(path: Path, descriptor: os.stat_result, kind: str) -> os.stat_result:
    missing = False
    try:
        current = os.lstat(path)
    except FileNotFoundError:
        missing = True
    if missing:
        raise ValueError(f"{kind} path changed during access")
    if (not stat.S_ISREG(current.st_mode) or current.st_nlink != 1
            or _identity(current) != _identity(descriptor)):
        raise ValueError(f"{kind} path changed during access")
    return current


def _flags(base: int) -> int:
    # O_NOFOLLOW is available on POSIX. Windows lacks it, so pre/post lstat
    # comparisons and descriptor identity checks are mandatory on both systems.
    # A checked regular file can be swapped for a FIFO before os.open():
    # nonblocking opens prevent both reader and writer hangs in that race.
    # Regular-file semantics are unchanged; all fstat/path checks still apply.
    return (base | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0))


@_redact_os_errors("Review evidence cannot be read; inspect local input permissions")
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
        if not _same_path_descriptor_signature(initial, before):
            raise ValueError(f"{kind} changed before read")
        if not _unchanged(initial, _same_path(source, before, kind)):
            raise ValueError(f"{kind} path changed during access")
        data = read_bounded_duplicate(descriptor, limit)
        after = os.fstat(descriptor)
        _regular(after, limit, kind)
        # An unchanged stat snapshot is insufficient if read() returned a
        # truncated or fabricated payload. Require the exact observed length.
        if len(data) != before.st_size or len(data) > limit or not _unchanged(before, after):
            raise ValueError(f"{kind} changed during read or exceeded its size limit")
        if not _unchanged(initial, _same_path(source, after, kind)):
            raise ValueError(f"{kind} path changed during access")
        return data
    finally:
        os.close(descriptor)


@_redact_os_errors("Review journal I/O failed; inspect journal before retrying")
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
    # Read access is necessary to verify the exact just-written bytes on
    # the SAME descriptor, before reporting successful review custody.
    flags = os.O_RDWR | os.O_APPEND
    if first is None:
        flags |= os.O_CREAT | os.O_EXCL
    descriptor = os.open(target, _flags(flags), 0o600)
    created = first is None
    wrote = False
    path_baseline = None
    try:
        before = os.fstat(descriptor)
        _regular(before, limit, "Review journal")
        if first is not None and not _same_path_descriptor_signature(first, before):
            raise ValueError("Review journal changed before append")
        if created and before.st_size != 0:
            raise ValueError("New review journal was not empty")
        path_baseline = _same_path(target, before, "Review journal")
        if first is not None and not _unchanged(first, path_baseline):
            raise ValueError("Review journal path changed before append")
        if before.st_size + len(data) > limit:
            raise ValueError("Review journal file-size limit reached")
        verify()
        verified = os.fstat(descriptor)
        _regular(verified, limit, "Review journal")
        if not _unchanged(before, verified):
            raise ValueError("Review journal changed while validating append")
        if not _unchanged(path_baseline, _same_path(target, verified, "Review journal")):
            raise ValueError("Review journal path changed before append")
        # Snapshot the exact prior journal bytes from this pinned descriptor.
        # Byte counts alone cannot detect corruption of earlier review events
        # during the subsequent write of the new, correctly appended event.
        prefix_witness = digest_pinned_prefix(descriptor, verified.st_size)
        if not _unchanged(verified, os.fstat(descriptor)):
            raise ValueError("Review journal changed while binding prior events")
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
        require_exact_append_readback(descriptor, verified.st_size, data)
        if digest_pinned_prefix(descriptor, verified.st_size) != prefix_witness:
            raise ValueError("Review journal previous events changed during append")
        after_witness = os.fstat(descriptor)
        if not _unchanged(ending, after_witness):
            raise ValueError("Review journal changed after append readback")
        # A pathname can still refer to the same inode after a rival writer
        # grows or rewrites it between final fstat and lstat. Compare the
        # observed pathname metadata with the pinned descriptor snapshot;
        # Windows ctime may legitimately differ across those API views.
        final_path = _same_path(target, after_witness, "Review journal")
        if not _same_path_descriptor_signature(final_path, after_witness):
            raise ValueError("Review journal path changed during append")
    finally:
        os.close(descriptor)
        # An indeterminate empty journal is review evidence, not disposable.
        # Unlink only the same *unchanged pathname snapshot* established before
        # validation; do not rely on inode + zero size alone.
        if created and not wrote and path_baseline is not None:
            try:
                current = os.lstat(target)
                if (stat.S_ISREG(current.st_mode)
                    and current.st_size == 0
                    and _unchanged(path_baseline, current)):
                    os.unlink(target)
            except FileNotFoundError:
                pass
