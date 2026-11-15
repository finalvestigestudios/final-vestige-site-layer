"""Prevent private CSV paths and abandoned staging descriptors from leaking.

Used only by the offline, non-overwriting financial CSV publication path.
The wrapper never treats failed evidence publication as a successful report.
"""
from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import TextIO


_COLLISION = "CSV report destination already exists"
_FAILED = "CSV report publication failed"


def require_free_destination(target: Path) -> None:
    """Reject occupied names, including dangling symlinks, before staging.

    This is a fast-fail convenience, not the authority against concurrent
    creators: the caller must still publish through exclusive link/rename.
    """
    try:
        target.lstat()
    except FileNotFoundError:
        return
    raise FileExistsError(_COLLISION)


def adopt_csv_descriptor(descriptor: int) -> TextIO:
    """Transfer a mkstemp FD to a UTF-8-BOM stream or close it on failure.

    fdopen may fail before assuming ownership. Also close for interrupts;
    callers handle removal of the unpublished staging directory entry.
    """
    try:
        return os.fdopen(descriptor, "w", encoding="utf-8-sig", newline="")
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise


def private_csv_failure(error: OSError) -> OSError:
    """Build a fixed diagnostic; the caller MUST raise it after its except block.

    Raising inside an active OSError handler, even with ``from None``, retains
    the private source exception in ``__context__``. Only native errno is used;
    no private paths, exception args or traceback objects are retained.
    """
    if isinstance(error, FileExistsError):
        return FileExistsError(_COLLISION)
    code = error.errno if type(error.errno) is int and error.errno > 0 else errno.EIO
    return OSError(code, _FAILED)
