"""Operator-only, fail-closed creation of one signed offline entitlement file.

No retries after ambiguous filesystem errors, no unlink-on-failure, no logging,
no network and no access to signing keys. A partial output requires explicit
human investigation and must NEVER be interpreted as an issued entitlement.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

_REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
_ID_FIELDS = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
              "st_mtime_ns", "st_ctime_ns")
MAX_ENTITLEMENT_BYTES = 8192


def _same(a: os.stat_result, b: os.stat_result) -> bool:
    return all(getattr(a, name) == getattr(b, name) for name in _ID_FIELDS)


def _valid_file(info: os.stat_result) -> bool:
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        return False
    if getattr(info, "st_file_attributes", 0) & _REPARSE:
        return False
    if os.name == "posix" and ((info.st_mode & 0o077) or info.st_uid != os.getuid()):
        return False
    return True


def create_issued_license(path: str | Path, data: bytes,
                          error_type: type[Exception]) -> None:
    """Create exactly one private file with O_EXCL and durable, witnessed bytes.

    If create, write, fsync or verification fails, leave any created file in
    place for manual triage; callers must retain the reserved license ID.
    Never retry the issuance automatically or replace an existing file. OS
    exceptions (including private filenames) are discarded before public raise.
    """
    if type(data) is not bytes or not (1 <= len(data) <= MAX_ENTITLEMENT_BYTES):
        raise error_type("Signed entitlement must be bounded bytes")

    destination = Path(path)
    descriptor: int | None = None
    failure: str | None = None
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        try:
            descriptor = os.open(destination, flags, 0o600)
        except FileExistsError:
            failure = "Entitlement output already exists; no overwrite permitted"
        except OSError:
            failure = "Cannot create private entitlement output"
        if descriptor is not None:
            try:
                opened = os.fstat(descriptor)
                if not _valid_file(opened) or opened.st_size != 0:
                    failure = "Entitlement output is not a new private regular file"
                if failure is None:
                    written = 0
                    while written < len(data):
                        count = os.write(descriptor, data[written:])
                        if type(count) is not int or count <= 0 or count > len(data) - written:
                            failure = "Cannot finish private entitlement output"
                            break
                        written += count
                if failure is None:
                    os.fsync(descriptor)
                    after_fd = os.fstat(descriptor)
                    after_path = os.lstat(destination)
                    if (not _valid_file(after_fd) or not _valid_file(after_path)
                        or after_fd.st_size != len(data)
                        or not _same(after_fd, after_path)):
                        failure = "Entitlement output identity or length changed"
            except OSError:
                failure = "Cannot complete or verify private entitlement output"
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                if failure is None:
                    failure = "Cannot close private entitlement output safely"

    if failure is not None:
        raise error_type(failure)
