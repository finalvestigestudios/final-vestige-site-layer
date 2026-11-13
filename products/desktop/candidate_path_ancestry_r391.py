"""Fail-closed ancestry evidence for staged Windows desktop release candidates.

An ordinary final file may be reached THROUGH an unsafe symlink/junction parent.
Walk each lexical parent by lstat (never resolve links), including the staging
root when checking a child, and capture immutable identity evidence for a
second check after reading. Local-only verification; NOT binary approval.
"""
from __future__ import annotations

import stat
from pathlib import Path

from candidate_reparse_r390 import unsafe_windows_reparse


class UnsafeCandidateAncestry(ValueError):
    """A staged file must not be read or released through this parent chain."""


def snapshot_candidate_parents(path: str | Path) -> tuple[tuple[object, ...], ...]:
    """Snapshot every lexical ancestor from filesystem root to immediate parent.

    Do not use Path.resolve(): following a symlink would erase the very link we
    must reject. Reject explicit '..' rather than canonicalizing through it.
    No source paths or lower-level filesystem exceptions escape on failure.
    """
    failed = False
    evidence: list[tuple[object, ...]] = []
    try:
        candidate = Path(path)
        if ".." in candidate.parts:
            failed = True
        else:
            absolute = candidate.absolute()
            for parent in reversed(absolute.parents):
                info = parent.lstat()
                if (not stat.S_ISDIR(info.st_mode)
                        or unsafe_windows_reparse(info)):
                    failed = True
                    break
                # Snapshot path AND directory identity, without reporting them
                # publicly. Timestamp/attribute drift during verification is a
                # rejection, not a silent evidence revalidation.
                evidence.append((str(parent), info.st_dev, info.st_ino,
                                 info.st_mode, info.st_nlink, info.st_size,
                                 info.st_mtime_ns, info.st_ctime_ns,
                                 getattr(info, "st_file_attributes", None)))
    except (OSError, ValueError, RuntimeError, TypeError, AttributeError):
        failed = True
    if failed or not evidence:
        raise UnsafeCandidateAncestry("Unsafe or changing candidate parent directory")
    return tuple(evidence)
