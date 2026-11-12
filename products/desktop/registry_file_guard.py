"""Operator-only SQLite registry file custody for offline premium issuance.

Inspect the pathname before and after opening the file descriptor. SQLite later
opens the path separately, so this is a best-effort preflight, NOT a binding of
SQLite to the inspected descriptor. Keep parent directory operator-controlled.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
_IDENTITY_FIELDS = (
    "st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
    "st_mtime_ns", "st_ctime_ns",
)


def _same_file(a: os.stat_result, b: os.stat_result) -> bool:
    return all(getattr(a, field) == getattr(b, field) for field in _IDENTITY_FIELDS)


def _file_problem(meta: os.stat_result) -> str | None:
    if getattr(meta, "st_file_attributes", 0) & _REPARSE_POINT:
        return "Registry path must not be a reparse point"
    if not stat.S_ISREG(meta.st_mode):
        return "Registry must be a regular file"
    if meta.st_nlink != 1:
        return "Registry must not have hard links"
    if os.name == "posix" and (meta.st_mode & 0o077 or meta.st_uid != os.getuid()):
        return "Registry file must be owned and readable only by operator"
    return None


def verify_registry_file(path: Path, error_type: type[Exception]) -> None:
    """Fail closed on alias, reparse, path replacement and private OS failures.

    Creates a 0600 registry only when absent; does not modify an existing file.
    The public path and opened descriptor must have the same identity before
    SQLite subsequently opens by pathname. Descriptor cleanup is unconditional.
    No private OSError is retained in the public exception chain.
    """
    failure: str | None = None
    before: os.stat_result | None = None
    try:
        if path.is_symlink():
            failure = "Registry must not be a symlink"
        else:
            try:
                before = os.lstat(path)
            except FileNotFoundError:
                pass
            if before is not None:
                failure = _file_problem(before)
    except OSError:
        failure = "Cannot inspect protected registry path"
    if failure is not None:
        raise error_type(failure)

    flags = (os.O_RDWR | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    descriptor: int | None = None
    created = False
    try:
        try:
            descriptor = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o600)
            created = True
        except FileExistsError:
            try:
                descriptor = os.open(path, flags)
            except OSError:
                failure = "Cannot open protected registry"
        except OSError:
            failure = "Cannot create protected registry"

        if descriptor is not None:
            try:
                metadata = os.fstat(descriptor)
            except OSError:
                failure = "Cannot inspect protected registry"
            else:
                failure = _file_problem(metadata)
                if failure is None:
                    try:
                        current = os.lstat(path)
                    except OSError:
                        failure = "Cannot inspect protected registry path"
                    else:
                        failure = _file_problem(current)
                        if failure is None and (before is None) != created:
                            failure = "Registry identity changed during inspection"
                        if failure is None and before is not None and not _same_file(before, metadata):
                            failure = "Registry identity changed during inspection"
                        if failure is None and not _same_file(metadata, current):
                            failure = "Registry identity changed during inspection"
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                if failure is None:
                    failure = "Cannot close protected registry"

    if failure is not None:
        raise error_type(failure)
