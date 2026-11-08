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

from .csv_snapshot import _same_path_descriptor_signature


def _safe_lstat(path: Path) -> os.stat_result:
    """Return lock metadata or reject without retaining a private-path error."""
    failure = None
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        failure = "Review writer lock disappeared; inspect journal before retrying"
    except OSError:
        failure = "Review writer lock cannot be inspected; inspect before retrying"
    if failure is not None:
        # Outside the handler: no original OSError survives in __context__.
        raise ValueError(failure)
    return info


def _create_private_lock(path: Path, flags: int) -> int:
    """Reject lock collisions and filesystem failures without retaining paths."""
    failure = None
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError:
        failure = "Review journal locked; inspect the existing lock before retrying"
    except OSError:
        failure = "Review writer lock cannot be created; inspect local permissions"
    if failure is not None:
        raise ValueError(failure)
    return fd


def _remove_owned_lock(path: Path) -> None:
    """Never expose sensitive lock paths when final unlink is denied."""
    failed = False
    try:
        os.unlink(path)
    except OSError:
        failed = True
    if failed:
        raise ValueError("Review writer lock cleanup failed; inspect before retrying")


def _identity(info: os.stat_result) -> tuple[int, int]:
    return info.st_dev, info.st_ino


def _owned(path: Path, baseline: os.stat_result,
           path_baseline: os.stat_result) -> None:
    """Reject loss, replacement, aliasing, or modification of our lock."""
    now = _safe_lstat(path)
    # Cross-view Windows descriptor/path creation-time values can disagree.
    # Compare all portable fields across views, then the *complete* path
    # signature against its own original pathname observation. Descriptor
    # custody is separately checked on every assert_owned() call.
    fields = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
              "st_mtime_ns", "st_ctime_ns")
    if (not stat.S_ISREG(now.st_mode) or now.st_nlink != 1
            or not _same_path_descriptor_signature(now, baseline)
            or any(getattr(now, name) != getattr(path_baseline, name)
                   for name in fields)):
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
    fd = _create_private_lock(target, flags)
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
        # Keep the first pathname identity for same-view ctime drift detection.
        # No successful writer is admitted before both views are checked.
        path_baseline = _safe_lstat(target)
        _owned(target, baseline, path_baseline)
        issued = True

        def assert_owned() -> None:
            _owned(target, baseline, path_baseline)
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
                _owned(target, baseline, path_baseline)
            except ValueError:
                pass
            else:
                _remove_owned_lock(target)
