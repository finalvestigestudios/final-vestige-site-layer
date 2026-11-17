"""Pre-publication path custody for six offline Windows candidates.

Rejects symlink/junction ancestors, reparse payloads, and changed staging
membership before publication. Not PE verification or release authorization.
"""
from __future__ import annotations

import stat
from pathlib import Path

from candidate_path_ancestry_r391 import snapshot_candidate_parents
from candidate_reparse_r390 import unsafe_windows_reparse


class InventoryStagePathError(ValueError):
    """No checksum manifest may be created under this staging path."""


def _inspect_stage(
    root: str | Path,
    expected: tuple[str, ...],
    *,
    maximum: int,
    stage_name: str | None = None,
) -> tuple[tuple[object, ...], ...]:
    """Check lexical ancestry, exact six files, and optional private stage."""
    if (type(expected) is not tuple or not expected
            or any(type(name) is not str or not name.endswith(".exe")
                   or "/" in name or "\\" in name or name in (".", "..")
                   for name in expected)
            or len(set(expected)) != len(expected)
            or type(maximum) is not int or maximum < 1):
        raise InventoryStagePathError("Unsafe six-app inventory staging path")
    if stage_name is not None and (
            type(stage_name) is not str
            or not stage_name.startswith(".fvs-inventory-")
            or "/" in stage_name or "\\" in stage_name
            or stage_name in expected):
        raise InventoryStagePathError("Unsafe six-app inventory staging path")
    root = Path(root)
    parents = snapshot_candidate_parents(root)
    info = root.lstat()
    if not stat.S_ISDIR(info.st_mode) or unsafe_windows_reparse(info):
        raise InventoryStagePathError("Unsafe six-app inventory staging path")
    names = set(expected) | ({stage_name} if stage_name is not None else set())
    members = tuple(root.iterdir())
    if len(members) != len(names) or {member.name for member in members} != names:
        raise InventoryStagePathError("Unsafe six-app inventory staging path")
    for item in members:
        found = item.lstat()
        if (not stat.S_ISREG(found.st_mode) or unsafe_windows_reparse(found)
                or found.st_nlink != 1 or not 1 <= found.st_size <= maximum):
            raise InventoryStagePathError("Unsafe six-app inventory staging path")
    if snapshot_candidate_parents(root) != parents:
        raise InventoryStagePathError("Unsafe six-app inventory staging path")
    return parents


def preflight_inventory_stage(
    root: str | Path,
    expected: tuple[str, ...],
    *,
    maximum: int,
    stage_name: str | None = None,
) -> tuple[tuple[object, ...], ...]:
    """Fail closed with one fixed message and no retained private exception."""
    failed = False
    try:
        return _inspect_stage(root, expected, maximum=maximum, stage_name=stage_name)
    except Exception:
        failed = True
    if failed:
        # Raise OUTSIDE the handler; `from None` still retains __context__.
        raise InventoryStagePathError("Unsafe six-app inventory staging path")
    raise InventoryStagePathError("Unsafe six-app inventory staging path")
