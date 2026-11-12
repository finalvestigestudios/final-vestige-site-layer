"""Bounded, descriptor-owned fingerprinting of an issued offline entitlement.

This helper does not verify signatures or authorize fulfillment. The caller
compares the digest to its already-verified, in-memory signed payload before
updating the human-reviewed issuance registry. No path is logged or persisted.
"""
from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path


# Windows and some remote filesystems may expose reparse points as regular
# files. The public path must never redirect to a different evidence object.
_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
_IDENTITY_FIELDS = ("st_dev", "st_ino", "st_mode", "st_nlink",
                    "st_size", "st_mtime_ns", "st_ctime_ns")


def _same_evidence(a: os.stat_result, b: os.stat_result) -> bool:
    return all(getattr(a, key) == getattr(b, key) for key in _IDENTITY_FIELDS)


def _unsafe_alias(meta: os.stat_result) -> bool:
    return (not stat.S_ISREG(meta.st_mode) or meta.st_nlink != 1 or
            bool(getattr(meta, "st_file_attributes", 0) & _REPARSE_POINT))


def fingerprint_issued_entitlement(path: Path, max_bytes: int,
                                   error_type: type[Exception]) -> str:
    """Read bounded signed bytes only while the public path still names this FD.

    Check lstat before opening, match the opened descriptor to that path, and
    recheck the path after reading. This catches swaps to other regular files
    (including same-content aliases) that O_NOFOLLOW and FD-only fstat miss.
    Reject Windows reparse-point attributes when exposed by lstat. POSIX uses
    O_NOFOLLOW as an additional last-component guard. Parent-directory swaps
    after the final pathname witness still require operator filesystem custody.
    """
    error: str | None = None
    digest: str | None = None
    fd: int | None = None
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        if path.is_symlink():
            error = "Issued file must be an absolute regular file"
        else:
            pathname_before = os.lstat(path)
            if _unsafe_alias(pathname_before):
                error = "Issued file must be a single-link regular file"
            elif not 0 < pathname_before.st_size <= max_bytes:
                error = "Issued file is empty or is not a bounded regular file"
            else:
                fd = os.open(path, flags)
                before = os.fstat(fd)
                if _unsafe_alias(before):
                    error = "Issued file must be a single-link regular file"
                elif not _same_evidence(pathname_before, before):
                    error = "Issued file changed during fingerprint; review reservation"
                else:
                    hasher = hashlib.sha256()
                    total = 0
                    while total <= max_bytes:
                        block = os.read(fd, min(4096, max_bytes + 1 - total))
                        if not block:
                            break
                        total += len(block)
                        hasher.update(block)
                    after = os.fstat(fd)
                    pathname_after = os.lstat(path)
                    if (total != before.st_size or total > max_bytes or
                            _unsafe_alias(pathname_after) or
                            not _same_evidence(before, after) or
                            not _same_evidence(after, pathname_after)):
                        error = "Issued file changed during fingerprint; review reservation"
                    else:
                        digest = hasher.hexdigest()
    except OSError:
        error = "Cannot read issued entitlement for fingerprint"
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                error = "Cannot close issued entitlement after fingerprint"
    if error is not None:
        raise error_type(error)
    if digest is None:
        raise error_type("Cannot fingerprint issued entitlement")
    return digest
