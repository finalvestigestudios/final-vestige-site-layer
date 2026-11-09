"""Post-write, descriptor-bound plaintext verification for premium vault restores.

Only an already-authenticated, local restore may call this with its expected
plaintext bytes and exclusive-create descriptor identities. This verifies the
whole restored set (including the manifest), not only the parsed report.
It is a postcondition, NOT a defense against a hostile directory after return.
No network, logs, compliance approval, or changes to source archives.
"""
from __future__ import annotations

import errno
import os
import stat
from pathlib import Path

_BLOCK = 256 * 1024
_ERROR = "Cannot verify private restored evidence"


def _same(current: os.stat_result, owned: os.stat_result, *, folder: bool = False) -> bool:
    correct = stat.S_ISDIR(current.st_mode) if folder else stat.S_ISREG(current.st_mode)
    return (correct and owned.st_ino != 0 and current.st_ino != 0
            and current.st_dev == owned.st_dev and current.st_ino == owned.st_ino)


def _read_exact(fd: int, count: int) -> bytes:
    parts = bytearray()
    while len(parts) < count:
        chunk = os.read(fd, count - len(parts))
        if type(chunk) is not bytes or not chunk or len(chunk) > count - len(parts):
            raise OSError(errno.EIO, _ERROR)
        parts.extend(chunk)
    return bytes(parts)


def _check_one(folder: Path, directory_id: os.stat_result, path: Path,
               owned: os.stat_result, expected: bytes) -> None:
    if not _same(os.lstat(folder), directory_id, folder=True):
        raise OSError(errno.EIO, _ERROR)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        before = os.fstat(fd)
        if (not _same(before, owned) or before.st_nlink != 1
                or before.st_size != len(expected)):
            raise OSError(errno.EIO, _ERROR)
        offset = 0
        while offset < len(expected):
            target = expected[offset:offset + _BLOCK]
            if _read_exact(fd, len(target)) != target:
                raise OSError(errno.EIO, _ERROR)
            offset += len(target)
        if os.read(fd, 1) != b"":
            raise OSError(errno.EIO, _ERROR)
        after = os.fstat(fd)
        if (not _same(after, owned) or after.st_nlink != 1
                or after.st_size != len(expected)
                or after.st_mtime_ns != before.st_mtime_ns
                or after.st_ctime_ns != before.st_ctime_ns):
            raise OSError(errno.EIO, _ERROR)
    finally:
        os.close(fd)
    named = os.lstat(path)
    if (not _same(named, owned) or named.st_nlink != 1
            or named.st_size != len(expected)
            or named.st_mtime_ns != after.st_mtime_ns
            or named.st_ctime_ns != after.st_ctime_ns
            or not _same(os.lstat(folder), directory_id, folder=True)):
        raise OSError(errno.EIO, _ERROR)


def verify_private_restore_members(
    folder: Path, directory_id: os.stat_result,
    created: list[tuple[Path, os.stat_result]],
    expected: list[tuple[Path, bytes]],
) -> None:
    """Fail closed unless *all* owned filenames still contain exact source bytes.

    Reject missing, additional recorded, reordered and duplicate entries.
    Read in bounded blocks, tolerate ordinary short OS reads, and recheck
    descriptor/name/directory identity. OS diagnostics are redacted *outside*
    their exception handlers, to avoid retaining private paths in traceback.
    Caller rolls back its identity-bound files on any failure or interruption.
    """
    if len(created) != len(expected) or not expected:
        raise ValueError(_ERROR)
    seen: set[Path] = set()
    for (stored_path, _), (wanted_path, data) in zip(created, expected):
        if (stored_path != wanted_path or wanted_path in seen
                or type(data) is not bytes or wanted_path.parent != folder):
            raise ValueError(_ERROR)
        seen.add(wanted_path)
    failed = False
    try:
        for (_, owned), (path, data) in zip(created, expected):
            _check_one(folder, directory_id, path, owned, data)
        # No unregistered evidence may be silently introduced into a successful
        # restored bundle. Never delete a stranger's extra file on failure.
        if not _same(os.lstat(folder), directory_id, folder=True):
            raise OSError(errno.EIO, _ERROR)
        with os.scandir(folder) as entries:
            actual_names = {entry.name for entry in entries}
        if actual_names != {path.name for path, _ in expected}:
            raise OSError(errno.EIO, _ERROR)
        if not _same(os.lstat(folder), directory_id, folder=True):
            raise OSError(errno.EIO, _ERROR)
    except OSError:
        failed = True
    if failed:
        raise ValueError(_ERROR)
