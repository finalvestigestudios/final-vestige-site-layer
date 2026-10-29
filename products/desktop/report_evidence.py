"""Exclusive, atomic, offline publication of candidate verification evidence.

The evidence is NOT code signing, malware clearance, entitlement verification,
or approval to publish the six Windows executables.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


class ReportEvidenceError(ValueError):
    """Do not trust or release an evidence report from a failed publication."""


def prepare_report_path(report: str | Path, candidate_dir: str | Path) -> Path:
    """Validate a NEW report filename outside the candidate distribution tree.

    Called *before* smoke runs; a bad report location must not execute a binary.
    A subsequent exclusive hardlink is the authoritative no-overwrite check.
    """
    try:
        root = Path(candidate_dir).resolve(strict=True)
        supplied = Path(report)
        if not supplied.name or supplied.name in (".", ".."):
            raise ReportEvidenceError("Choose a file for verification evidence")
        parent = supplied.parent.resolve(strict=True)
        if not parent.is_dir():
            raise ReportEvidenceError("Evidence destination parent must exist")
        if parent == root or root in parent.parents:
            raise ReportEvidenceError("Evidence must be stored outside the candidate folder")
        destination = parent / supplied.name
        # lexists deliberately rejects dangling symlinks as well as ordinary files.
        if os.path.lexists(destination):
            raise ReportEvidenceError("Evidence destination already exists")
        return destination
    except ReportEvidenceError:
        raise
    except (OSError, RuntimeError, ValueError):
        raise ReportEvidenceError("Invalid evidence destination") from None


def publish_report(destination: str | Path, evidence: dict) -> None:
    """Stage, flush and atomically publish complete UTF-8 JSON without overwrite.

    os.link is exclusive even if another process creates the final path after
    preflight. Both paths are in the same directory. A link-unsupported volume
    fails closed rather than falling back to a partial destination write.
    """
    destination = Path(destination)
    parent = destination.parent
    temporary = None
    try:
        payload = (json.dumps(evidence, sort_keys=True, indent=2,
                              ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
        fd, name = tempfile.mkstemp(prefix=".fvs-candidate-report-", suffix=".tmp", dir=parent)
        temporary = Path(name)
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        # Never use rename/replace: those can overwrite previous verification evidence.
        os.link(temporary, destination)
    except (OSError, TypeError, ValueError, OverflowError):
        raise ReportEvidenceError("Could not exclusively publish complete verification evidence") from None
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                # The completed destination, if any, is intact; an orphan temp
                # requires operator investigation rather than destructive cleanup.
                pass
