"""Publish a complete, local GrantAudit evidence bundle as one directory.

A failed source recheck or manifest write must not leave independently
publishable exception/budget CSVs behind. The destination directory is
private, unpredictable and published with one same-filesystem rename.
This is not digital signing or a defense against privileged local writers.
"""
from __future__ import annotations

import os
import secrets
import shutil
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence


def publish_grant_bundle(folder, build: Callable[[Path], Sequence[Path]]) -> list[Path]:
    """Build both reports and their manifest privately, then publish together.

    `build(staging)` writes *only* the two report CSVs and the final evidence
    manifest into the private staging directory, and returns their three paths.
    If any step fails, clean the staging directory without touching existing
    evidence. Returned paths point to the newly published package directory.
    """
    parent = Path(folder)
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("Choose an existing, non-symlink output folder")
    try:
        staging = Path(tempfile.mkdtemp(prefix=".fvs-grant-pending-", dir=parent))
    except OSError:
        raise ValueError("Unable to prepare private grant evidence package") from None
    committed = False
    try:
        outputs = list(build(staging))
        if len(outputs) != 3:
            raise ValueError("Grant package requires two reports and one inventory")
        paths = [Path(p) for p in outputs]
        names = [p.name for p in paths]
        if (len(set(names)) != 3
                or any(p.parent != staging for p in paths)
                or not names[0].startswith("grant-audit-exceptions-")
                or not names[1].startswith("grant-budget-check-")
                or not names[2].startswith("evidence-manifest-")
                or [p.suffix.lower() for p in paths] != [".csv", ".csv", ".txt"]):
            raise ValueError("Unexpected grant evidence package layout")
        if set(names) != {p.name for p in staging.iterdir()}:
            raise ValueError("Unexpected files in grant evidence package")
        for path in paths:
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise ValueError("Grant evidence must contain regular files")
        # A 128-bit random suffix makes collisions exceedingly unlikely. This
        # is an atomic same-parent rename, NOT a cross-platform no-replace
        # primitive against a malicious concurrent local writer.
        final = parent / ("grant-evidence-" +
                          datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") +
                          secrets.token_hex(16))
        if os.path.lexists(final):
            raise ValueError("Grant evidence package destination already exists")
        try:
            os.rename(staging, final)
        except OSError:
            raise ValueError("Unable to publish complete grant evidence package") from None
        committed = True
        return [final / p.name for p in paths]
    finally:
        if not committed:
            # These are exclusively our private temporary files. Never delete
            # previously published user reports or arbitrary source inputs.
            shutil.rmtree(staging)
