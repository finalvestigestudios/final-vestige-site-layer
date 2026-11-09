"""Best-effort identity-bound rollback for local premium vault plaintext restores.

A restore may fail midway through writing its private folder. Delete only
regular files whose current file IDs match handles opened by this restore;
never remove a detectably replaced file, symlink or directory. This narrows
same-user filesystem races but is NOT a race-free hostile-directory defense.
No contents or customer paths are logged, returned, or inspected.
"""
from __future__ import annotations

import errno
import os
import stat
from pathlib import Path
from typing import Iterable


def snapshot_new_file(fd: int) -> os.stat_result:
    """Capture the identity from the exclusive create descriptor before writing."""
    identity = os.fstat(fd)
    if (not stat.S_ISREG(identity.st_mode) or identity.st_ino == 0
            or identity.st_nlink != 1):
        raise OSError(errno.EIO, "Restored evidence file identity unavailable")
    return identity


def snapshot_new_folder(folder: Path) -> os.stat_result:
    """Require a real, identifiable directory created for this restore."""
    identity = os.lstat(folder)
    if not stat.S_ISDIR(identity.st_mode) or identity.st_ino == 0:
        raise OSError(errno.EIO, "Restored evidence directory identity unavailable")
    return identity


def _same_object(current: os.stat_result, saved: os.stat_result, *, directory: bool) -> bool:
    correct_type = stat.S_ISDIR(current.st_mode) if directory else stat.S_ISREG(current.st_mode)
    return (correct_type and saved.st_ino != 0 and current.st_ino != 0
            and current.st_dev == saved.st_dev and current.st_ino == saved.st_ino)


def rollback_owned_restore(folder: Path, folder_identity: os.stat_result,
                           created: Iterable[tuple[Path, os.stat_result]]) -> None:
    """Do not mask the original restore exception or delete other writers' names.

    The directory must remain unchanged before attempting each unlink. A
    replaced file is left in place, and its nonempty folder is retained.
    Cleanup errors are best effort; physical access controls remain required.
    """
    files = tuple(created)
    for path, identity in reversed(files):
        try:
            if not _same_object(os.lstat(folder), folder_identity, directory=True):
                return
            if _same_object(os.lstat(path), identity, directory=False):
                os.unlink(path)
        except OSError:
            continue
    try:
        if _same_object(os.lstat(folder), folder_identity, directory=True):
            os.rmdir(folder)  # Only removes the directory if now empty.
    except OSError:
        pass
