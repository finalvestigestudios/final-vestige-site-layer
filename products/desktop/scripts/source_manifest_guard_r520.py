"""Fail-closed bounded, descriptor-bound read of the pinned desktop test manifest.

The caller must still verify the immutable Git blob digest and command allowlist.
No path, source byte or operating-system exception is included in failures.
This is not an atomic filesystem sandbox against concurrent writers.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat


class ManifestReadRejected(ValueError):
    """The command manifest was unsafe to read as reviewed source evidence."""


def _signature(info: os.stat_result) -> tuple[int, ...]:
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _same_cross_view(path_info: os.stat_result, fd_info: os.stat_result) -> bool:
    """Windows lstat/fstat creation-time views can disagree for one file."""
    left, right = _signature(path_info), _signature(fd_info)
    return left[:-1] == right[:-1] if os.name == "nt" else left == right


def _linked(path: Path) -> bool:
    if path.is_symlink():
        return True
    junction = getattr(path, "is_junction", None)
    return bool(junction is not None and junction())


def read_manifest_custodied(path: Path, limit: int) -> bytes:
    """Return exact unlinked regular-file bytes only after stable fd/path checks.

    Reject symlink/junction ancestors, hardlinks, in-flight mutation, irregular
    files, empty or oversized content and descriptor-vs-path replacement. Read
    no more than ``limit + 1`` bytes, regardless of file size. Never print the
    content or retain a private OS failure in the raised exception chain.
    """
    if (not isinstance(path, Path) or not path.is_absolute()
            or type(limit) is not int or not 1 <= limit <= 65_536):
        raise ManifestReadRejected("Unsafe source evidence manifest")
    try:
        if any(_linked(ancestor) for ancestor in (path, *path.parents)):
            raise OSError("linked manifest path")
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or not 0 < before.st_size <= limit):
            raise OSError("untrusted manifest file")
        flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
                 | getattr(os, "O_CLOEXEC", 0)
                 | getattr(os, "O_NOFOLLOW", 0)
                 | getattr(os, "O_NONBLOCK", 0))
        fd = os.open(path, flags)
        try:
            reader = os.fdopen(fd, "rb")
        except (OSError, ValueError):
            try:
                os.close(fd)
            except OSError:
                pass
            raise
        with reader:
            opened = os.fstat(reader.fileno())
            if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                    or not _same_cross_view(before, opened)):
                raise OSError("manifest changed before open")
            raw = reader.read(limit + 1)
            after_fd = os.fstat(reader.fileno())
        after_path = path.lstat()
        if (type(raw) is not bytes or len(raw) != before.st_size
                or not 0 < len(raw) <= limit
                or _signature(opened) != _signature(after_fd)
                or _signature(before) != _signature(after_path)
                or not _same_cross_view(after_path, after_fd)
                or _linked(path)):
            raise OSError("manifest changed during read")
        return raw
    except (OSError, ValueError, TypeError):
        # Raising after this handler exits drops the original exception
        # object, its private filename and any traceback context.
        pass
    raise ManifestReadRejected("Unsafe source evidence manifest")
