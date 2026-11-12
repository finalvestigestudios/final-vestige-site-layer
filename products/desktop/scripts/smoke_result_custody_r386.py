"""Fail-closed synthetic smoke output references for all six desktop engines.

The real smoke runner already validates generated temporary files. This module
protects the *receipt* boundary against zero-output generators, forged path
objects, duplicates, traversal and inflated output counts. Source-only proof;
not evidence of a Windows build, QD decision or approved distribution.
"""
from __future__ import annotations

import re
from pathlib import Path

_NATIVE_PATH_TYPE = type(Path())
_SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z", re.ASCII)
MAX_SMOKE_OUTPUTS = 32


def checked_smoke_outputs(outputs: object) -> list[Path]:
    """Accept only a bounded, nonempty native list of unique basename Paths.

    Do not coerce unknown objects or iterate arbitrary generators; doing so
    could invoke caller-defined hooks and fabricate a successful receipt.
    The returned paths remain references, not asserted persistent artifacts:
    the smoke runner destroys its synthetic temporary directory on return.
    """
    if type(outputs) is not list:
        raise RuntimeError("Synthetic source smoke returned unsafe output references")
    if not outputs:
        raise RuntimeError("Synthetic source smoke returned no source-smoke outputs")
    if len(outputs) > MAX_SMOKE_OUTPUTS:
        raise RuntimeError("Synthetic source smoke returned unsafe output references")
    seen: set[str] = set()
    for item in outputs:
        if type(item) is not _NATIVE_PATH_TYPE:
            raise RuntimeError("Synthetic source smoke returned unsafe output references")
        basename = item.as_posix()
        if (item.is_absolute() or len(item.parts) != 1
                or item.name in ("", ".", "..")
                or _SAFE_NAME.fullmatch(basename) is None
                or basename in seen):
            raise RuntimeError("Synthetic source smoke returned unsafe output references")
        seen.add(basename)
    return outputs.copy()
