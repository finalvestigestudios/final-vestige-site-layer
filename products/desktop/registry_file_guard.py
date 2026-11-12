"""Operator-only SQLite registry file custody for offline premium issuance.

Inspect by descriptor, never through a followed symlink or an imported CSV path.
The caller's SQLite connection is opened separately after this check: this
function cannot prevent a privileged/same-user process from swapping paths
between inspection and SQLite open. Protect the parent directory (0700 on POSIX).
"""
from __future__ import annotations

import os
import stat
from pathlib import Path


def verify_registry_file(path: Path, error_type: type[Exception]) -> None:
    """Create or inspect a private single-link regular file without leaking IO faults.

    Every raw descriptor is closed, including failed metadata reads. A hard link
    can alias an unrelated operator file and must never be accepted as a registry.
    Raise a fixed public error only *after* the private OSError handler unwinds,
    so __context__ and __cause__ do not retain private paths or OS messages.
    """
    failure: str | None = None
    try:
        if path.is_symlink():
            failure = "Registry must not be a symlink"
    except OSError:
        failure = "Cannot inspect protected registry path"
    if failure is not None:
        raise error_type(failure)

    flags = os.O_RDWR | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor: int | None = None
    try:
        try:
            descriptor = os.open(path, flags | os.O_CREAT | os.O_EXCL, 0o600)
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
                if not stat.S_ISREG(metadata.st_mode):
                    failure = "Registry must be a regular file"
                elif metadata.st_nlink != 1:
                    failure = "Registry must not have hard links"
                elif os.name == "posix" and (
                    metadata.st_mode & 0o077 or metadata.st_uid != os.getuid()
                ):
                    failure = "Registry file must be owned and readable only by operator"
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                # A failed close is not proof the descriptor was safely retired.
                if failure is None:
                    failure = "Cannot close protected registry"

    if failure is not None:
        raise error_type(failure)
