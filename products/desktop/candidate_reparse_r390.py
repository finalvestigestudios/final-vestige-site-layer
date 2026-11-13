"""Windows release-candidate reparse custody, without interpreting a file as safe.

On Windows, st_file_attributes is required on both path and descriptor views.
Reject all reparse points, including junctions, cloud placeholders and non-symlink
tags. On non-Windows systems, existing POSIX lstat/fstat link and inode checks
remain authoritative. This is not Defender, code signing, or release approval.
"""
from __future__ import annotations

import os
import stat

_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def unsafe_windows_reparse(info: object, *, on_windows: bool | None = None) -> bool:
    """True means reject; missing/forged Windows attributes fail closed.

    on_windows exists solely for synthetic cross-platform regression tests.
    Production callers omit it, so only the actual host OS controls policy.
    """
    if on_windows is None:
        on_windows = os.name == "nt"
    if type(on_windows) is not bool:
        return True
    if not on_windows:
        return False
    try:
        attributes = getattr(info, "st_file_attributes", None)
    except Exception:
        return True
    return type(attributes) is not int or bool(attributes & _REPARSE_POINT)
