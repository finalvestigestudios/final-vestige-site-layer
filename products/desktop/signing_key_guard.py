"""Read one bounded operator-owned signing key without exposing file diagnostics.

This module is issuer-only; never bundle it, a PEM, or a private key in an EXE.
Identity checks detect ordinary pathname swaps, NOT a privileged attacker that
can rewrite file contents and restore metadata or replace an ancestor directory.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

_REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
_IDENTITY = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
             "st_mtime_ns", "st_ctime_ns")


def _same(a: os.stat_result, b: os.stat_result) -> bool:
    return all(getattr(a, name) == getattr(b, name) for name in _IDENTITY)


def _problem(meta: os.stat_result, limit: int) -> str | None:
    if getattr(meta, "st_file_attributes", 0) & _REPARSE:
        return "Signing key must not be a reparse point"
    if stat.S_ISLNK(meta.st_mode):
        return "Signing key must not be a symlink"
    if not stat.S_ISREG(meta.st_mode) or meta.st_size < 0:
        return "Signing key must be a bounded regular file"
    if meta.st_nlink != 1:
        return "Signing key must not have hard links"
    if meta.st_size > limit:
        return "Signing key must be a bounded regular file"
    if os.name == "posix" and (meta.st_mode & 0o077 or meta.st_uid != os.getuid()):
        return "Signing key permissions must be owner-only (0600)"
    return None


def read_signing_key(path: str | Path, limit: int,
                     error_type: type[Exception]) -> bytes:
    """Read exact bytes through one FD, check before/after path and close FD.

    OSError faults from lstat/open/fstat/read/close are reduced to fixed messages
    *outside* the original handler. No raw error or private path remains in
    __context__/__cause__. The read never creates or changes any input file.
    """
    source = Path(path)
    if type(limit) is not int or limit <= 0:
        raise ValueError("Signing key limit must be a positive integer")
    failure: str | None = None
    before = None
    try:
        before = os.lstat(source)
    except OSError:
        failure = "Cannot open signing key as a regular file"
    if failure is None:
        failure = _problem(before, limit)
    if failure is not None:
        raise error_type(failure)

    descriptor: int | None = None
    content = b""
    try:
        flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
                 | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        try:
            descriptor = os.open(source, flags)
        except OSError:
            failure = "Cannot open signing key as a regular file"
        if descriptor is not None:
            try:
                opened = os.fstat(descriptor)
                failure = _problem(opened, limit)
                if failure is None and not _same(before, opened):
                    failure = "Signing key identity changed during inspection"
                if failure is None:
                    blocks = bytearray()
                    while len(blocks) <= limit:
                        chunk = os.read(descriptor, min(32768, limit + 1 - len(blocks)))
                        if not chunk:
                            break
                        blocks.extend(chunk)
                    if len(blocks) > limit:
                        failure = "Signing key must be a bounded regular file"
                if failure is None:
                    after_fd = os.fstat(descriptor)
                    after_path = os.lstat(source)
                    if not (_same(opened, after_fd) and _same(after_fd, after_path)):
                        failure = "Signing key identity changed during inspection"
                    else:
                        failure = _problem(after_fd, limit) or _problem(after_path, limit)
                    if failure is None and len(blocks) != opened.st_size:
                        failure = "Signing key must be a bounded regular file"
                    if failure is None:
                        content = bytes(blocks)
            except OSError:
                failure = "Cannot inspect or read protected signing key"
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                if failure is None:
                    failure = "Cannot close protected signing key"

    if failure is not None:
        raise error_type(failure)
    return content
