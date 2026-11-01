"""Synthetic, test-only Windows file-custody race fixtures (never production code).

Windows can deny unlink/rename while a descriptor is open. Rather than skipping
TOCTOU adversarial coverage, these fixtures alter the *observed* stat identity
for an exact test pathname. They neither modify real input files nor relax the
real production descriptor/lock validation.
"""
from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace


STAT_FIELDS = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
               "st_mtime_ns", "st_ctime_ns")


def changed_stat(info, field: str = "st_ino") -> SimpleNamespace:
    """Return a complete synthetic security-relevant stat with one drift field."""
    if field not in STAT_FIELDS:
        raise ValueError("Unknown stat field for synthetic custody test")
    values = {name: getattr(info, name) for name in STAT_FIELDS}
    values[field] += 1
    return SimpleNamespace(**values)


def altered_lstat(target: Path, state: dict, original, *, missing=False, field="st_ino"):
    """Patcher side-effect: changed or missing path *after* state['active'].

    Save the original os.lstat function BEFORE patching it. All other paths
    retain their actual OS behavior, and the target is untouched on disk.
    """
    target = Path(target)

    def observe(path, *args, **kwargs):
        if (state.get("active", False)
                and isinstance(path, (str, os.PathLike))
                and Path(path) == target):
            if missing:
                raise FileNotFoundError("Synthetic pathname loss for custody test")
            return changed_stat(original(path, *args, **kwargs), field)
        return original(path, *args, **kwargs)

    return observe
