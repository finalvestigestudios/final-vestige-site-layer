"""Publish one complete, private, local ProcureGuard evidence directory.

A report and its SHA-256 inventory are staged together, then revealed via one
same-filesystem directory rename. This is not a payment authorization, digital
signature, power-loss guarantee or defense against privileged local writers.
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


def publish_procurement_bundle(
    folder: str | Path, build: Callable[[Path], Sequence[Path]]
) -> list[Path]:
    """Stage the review CSV and inventory; publish neither if either fails.

    The builder receives a new private staging directory and must return two
    paths inside it: procurement-three-way-*.csv, evidence-manifest-*.txt.
    Neither existing evidence nor original input files are modified.
    """
    parent = Path(folder)
    if not parent.is_dir() or parent.is_symlink():
        raise ValueError("Choose an existing, non-symlink output folder")
    try:
        staging = Path(tempfile.mkdtemp(prefix=".fvs-procure-pending-", dir=parent))
    except OSError:
        raise ValueError("Unable to prepare private procurement evidence") from None
    committed = False
    try:
        outputs = list(build(staging))
        if len(outputs) != 2:
            raise ValueError("Procurement package requires one report and one inventory")
        paths = [Path(p) for p in outputs]
        names = [p.name for p in paths]
        if (len(set(names)) != 2
                or any(p.parent != staging for p in paths)
                or not names[0].startswith("procurement-three-way-")
                or not names[1].startswith("evidence-manifest-")
                or [p.suffix.lower() for p in paths] != [".csv", ".txt"]):
            raise ValueError("Unexpected procurement evidence package layout")
        if set(names) != {p.name for p in staging.iterdir()}:
            raise ValueError("Unexpected files in procurement evidence package")
        identities = set()
        for path in paths:
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                raise ValueError("Procurement evidence must contain regular files")
            identity = (info.st_dev, info.st_ino)
            if info.st_ino and identity in identities:
                raise ValueError("Procurement evidence files must be distinct")
            identities.add(identity)
        final = parent / (
            "procurement-evidence-"
            + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-")
            + secrets.token_hex(16)
        )
        if os.path.lexists(final):
            raise ValueError("Procurement evidence destination already exists")
        try:
            os.rename(staging, final)
        except OSError:
            raise ValueError("Unable to publish complete procurement evidence") from None
        committed = True
        return [final / path.name for path in paths]
    finally:
        if not committed:
            shutil.rmtree(staging)
