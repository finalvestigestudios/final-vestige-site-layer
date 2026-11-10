"""Read local review evidence using a safely owned duplicate descriptor.

The caller owns the original pinned descriptor and performs identity, size,
and pathname checks around this read.  The duplicate must be closed even if
fdopen or context entry fails, without reopening the private pathname.
"""
from __future__ import annotations

import os


def read_bounded_duplicate(descriptor: int, limit: int) -> bytes:
    """Read at most limit+1 bytes; always close only our duplicate.

    A read of limit+1 makes an over-limit file fail closed in the caller.
    The original descriptor stays open for its post-read custody checks.
    """
    if type(limit) is not int or limit < 0:
        raise ValueError("Review evidence read limit is invalid")
    duplicate = os.dup(descriptor)
    try:
        with os.fdopen(duplicate, "rb") as stream:
            # Ownership transfers only after the stream has entered. Before
            # then, even a failed __enter__ must not orphan the duplicate.
            duplicate = None
            return stream.read(limit + 1)
    finally:
        if duplicate is not None:
            try:
                os.close(duplicate)
            except OSError:
                # Preserve the primary fdopen/enter failure, including when
                # an implementation closed the fd before raising.
                pass
