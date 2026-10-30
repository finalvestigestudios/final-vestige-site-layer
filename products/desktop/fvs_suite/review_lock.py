"""Fail-closed, descriptor-owned writer lock for offline premium review journals.

A lock is cooperative coordination, not a defense against a privileged attacker
or a replacement for validating the complete financial review journal.
"""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import stat
from typing import Callable, Iterator


def _identity(info: os.stat_result) -> tuple[int, int]:
    return info.st_dev, info.st_ino


def _owned(path: Path, baseline: os.stat_result) -> None:
    """Reject loss, replacement, aliasing, or modification of our lock."""
    try:
        now = os.lstat(path)
    except FileNotFoundError as exc:
        raise ValueError("Review writer lock disappeared; inspect journal before retrying") from exc
    if (not stat.S_ISREG(now.st_mode) or now.st_nlink != 1
            or _identity(now) != _identity(baseline)
            or now.st_size != baseline.st_size
            or now.st_mtime_ns != baseline.st_mtime_ns
            or now.st_ctime_ns != baseline.st_ctime_ns):
        raise ValueError("Review writer lock changed; inspect journal before retrying")


def _write_all(fd: int, data: bytes) -> None:
    position = 0
    while position < len(data):
        count = os.write(fd, data[position:])
        if count <= 0:
            raise OSError("Review writer lock was not fully written")
        position += count


@contextmanager
def exclusive_review_lock(journal: str | Path) -> Iterator[Callable[[], None]]:
    """Create a private exclusive lock and yield its live ownership check.

    Re-check ownership immediately before publishing a human decision and after
    append has completed. Lost ownership fails closed; if the lock was replaced,
    it is *never* unlinked by this context manager. Stale locks require manual
    review rather than automatic breakage, avoiding concurrent writers.
    """
    target = Path(str(journal) + ".lock")
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_NOFOLLOW", 0)
             | getattr(os, "O_CLOEXEC", 0)
             | getattr(os, "O_BINARY", 0))
    try:
        fd = os.open(target, flags, 0o600)
    except FileExistsError as exc:
        raise ValueError("Review journal locked; inspect the existing lock before retrying") from exc
    issued = False
    baseline = None
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size != 0:
            raise ValueError("New review lock is not a unique empty regular file")
        if os.name == "posix" and info.st_mode & 0o077:
            raise ValueError("Review lock must be private to its owner")
        _write_all(fd, f"pid={os.getpid()}\n".encode("ascii"))
        os.fsync(fd)
        baseline = os.fstat(fd)
        _owned(target, baseline)
        issued = True

        def assert_owned() -> None:
            _owned(target, baseline)
            current = os.fstat(fd)
            if (_identity(current) != _identity(baseline)
                    or current.st_size != baseline.st_size
                    or current.st_mtime_ns != baseline.st_mtime_ns
                    or current.st_ctime_ns != baseline.st_ctime_ns
                    or current.st_nlink != 1):
                raise ValueError("Review writer lock descriptor changed; inspect before retrying")

        yield assert_owned
        assert_owned()
    finally:
        os.close(fd)
        # Only remove a lock which is *still exactly ours*. An altered,
        # disappeared, or substituted lock is left untouched for investigation.
        if issued and baseline is not None:
            try:
                _owned(target, baseline)
            except ValueError:
                pass
            else:
                os.unlink(target)
