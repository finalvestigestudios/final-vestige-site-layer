"""R124: fail-closed, local-only inventory for human Windows 11 witness files.

Both the R122 one-check writer and R123 progress reader use this contract.
It checks filenames and file types, never reads or reveals observation text,
and never interprets a human PASS as compliance or distribution approval.
"""
from __future__ import annotations

import os
import stat
from pathlib import Path

import windows11_manual_acceptance_r109 as qa


def verify_clean(matrix: dict, directory: Path) -> int:
    """Require exactly the witness filenames referenced by a validated matrix.

    Call only after qa.validate_review and trusted directory checks. This
    intentionally fails on orphaned, hidden, temporary, hardlinked, or
    substituted entries, including an old witness from an interrupted write.
    It performs no deletion or repair; a human must investigate any HOLD.
    """
    if type(matrix) is not dict or type(matrix.get("apps")) is not dict:
        raise qa.ReviewHold("Invalid witness inventory matrix")

    expected = set()
    for app in qa.ALL:
        item = matrix["apps"].get(app)
        if type(item) is not dict or type(item.get("checks")) is not dict:
            raise qa.ReviewHold("Incomplete witness inventory matrix")
        for check in qa._checks(app):
            slot = item["checks"].get(check)
            if type(slot) is not dict:
                raise qa.ReviewHold("Invalid witness inventory slot")
            state = slot.get("state")
            if state in ("PASS", "FAIL"):
                if (type(slot.get("witness_sha256")) is not str or
                        qa.HEX.fullmatch(slot["witness_sha256"]) is None):
                    raise qa.ReviewHold("Missing witness digest")
                expected.add(app.removesuffix(".exe") + "--" + check + ".json")
            elif state == "NOT_RUN":
                if slot.get("witness_sha256") is not None:
                    raise qa.ReviewHold("Unexpected witness digest")
            else:
                raise qa.ReviewHold("Unrecognized witness state")

    seen = set()
    for entry in directory.iterdir():
        if entry.name not in expected or entry.name in seen:
            raise qa.ReviewHold("Unreferenced witness entry")
        metadata = entry.lstat()
        if (not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
                or entry.is_symlink()
                or (hasattr(entry, "is_junction") and entry.is_junction())
                or (os.name == "nt" and bool(
                    getattr(metadata, "st_file_attributes", 0) &
                    getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)))):
            raise qa.ReviewHold("Untrusted witness entry")
        seen.add(entry.name)

    if seen != expected:
        raise qa.ReviewHold("Referenced witness entry missing")
    return len(seen)
