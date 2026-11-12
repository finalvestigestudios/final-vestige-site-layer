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


def fingerprint_issued_entitlement(path: Path, max_bytes: int,
                                   error_type: type[Exception]) -> str:
    """Read exactly one bounded regular file with no alias or raw-FD leakage.

    Reject links, special files, modification during reading, truncated reads,
    and closing failures. Translate private OSError information only after the
    active exception handler has exited, leaving a clean public exception chain.
    The descriptor is read-only; this function never repairs or edits evidence.
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
            fd = os.open(path, flags)
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                error = "Issued file must be a single-link regular file"
            elif not 0 < before.st_size <= max_bytes:
                error = "Issued file is empty or is not a bounded regular file"
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
                identity = ("st_dev", "st_ino", "st_mode", "st_nlink",
                            "st_size", "st_mtime_ns", "st_ctime_ns")
                if (total != before.st_size or total > max_bytes or
                        any(getattr(before, key) != getattr(after, key)
                            for key in identity)):
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
