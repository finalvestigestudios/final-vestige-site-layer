"""Exclusive, atomic, offline publication of candidate verification evidence.

The evidence is NOT code signing, malware clearance, entitlement verification,
or approval to publish the six Windows executables.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from report_link_witness_r338 import LinkWitnessError, verify_published_link


class ReportEvidenceError(ValueError):
    """Do not trust or release an evidence report from a failed publication."""


def prepare_report_path(report: str | Path, candidate_dir: str | Path) -> Path:
    """Validate a NEW report filename outside the candidate distribution tree.

    Called *before* smoke runs; a bad report location must not execute a binary.
    A subsequent exclusive hardlink is the authoritative no-overwrite check.
    """
    invalid_path = False
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
    except ReportEvidenceError:
        raise
    except (OSError, RuntimeError, ValueError):
        invalid_path = True
    if invalid_path:
        raise ReportEvidenceError("Invalid evidence destination")
    return destination


def _write_verified_stage(fd: int, payload: bytes) -> None:
    """Own the raw fd and prove exact staged report bytes before hardlinking.

    A short write, an incorrect write count, or same-length corruption must
    never be published as a successful release-gate report. Re-read through
    the same descriptor after fsync; do not trust the writer's return alone.
    """
    adoption_failed = False
    try:
        stream = os.fdopen(fd, "w+b")
    except BaseException as exc:
        # fdopen did not assume ownership; close the private raw descriptor.
        try:
            os.close(fd)
        except OSError:
            pass
        if isinstance(exc, Exception):
            adoption_failed = True
        else:
            raise
    if adoption_failed:
        raise ReportEvidenceError("Could not stage verification evidence safely")

    stage_failed = False
    try:
        with stream:
            count = stream.write(payload)
            if type(count) is not int or count != len(payload):
                raise ReportEvidenceError("Incomplete verification evidence staging")
            stream.flush()
            os.fsync(stream.fileno())
            stream.seek(0)
            witnessed = stream.read(len(payload) + 1)
            if type(witnessed) is not bytes or witnessed != payload:
                raise ReportEvidenceError("Verification evidence staging differs from intended bytes")
    except ReportEvidenceError:
        raise
    except Exception:
        stage_failed = True
    finally:
        # A failed __enter__ does not invoke __exit__; explicitly discharge ownership.
        try:
            stream.close()
        except Exception:
            pass
    if stage_failed:
        raise ReportEvidenceError("Could not stage verification evidence safely")


def publish_report(destination: str | Path, evidence: dict) -> None:
    """Stage, verify, and atomically publish exact UTF-8 JSON without overwrite.

    Every created staging path is retained for controlled human inspection;
    never unlink a possibly swapped pathname, even after successful linking.
    Stages are private, hardlinked to successful evidence, and never approved
    for distribution. Operators must clean them up only after review.

    os.link is exclusive even if another process creates the final path after
    preflight. Both paths are in the same directory. A link-unsupported volume
    fails closed rather than falling back to a partial destination write.
    """
    destination = Path(destination)
    parent = destination.parent
    publish_failed = False
    witness_failed = False
    try:
        payload = (json.dumps(evidence, sort_keys=True, indent=2,
                              ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")
        fd, name = tempfile.mkstemp(prefix=".fvs-candidate-report-", suffix=".tmp", dir=parent)
        temporary = Path(name)
        # Never automatically delete a potentially swapped staging path.
        _write_verified_stage(fd, payload)
        os.link(temporary, destination)
        try:
            verify_published_link(temporary, destination, payload)
        except LinkWitnessError:
            witness_failed = True
    except (OSError, TypeError, ValueError, OverflowError, RuntimeError):
        publish_failed = True
    # Publish errors must be constructed only after untrusted exception handlers
    # unwind: ``from None`` masks tracebacks but retains private __context__.
    if witness_failed:
        raise ReportEvidenceError("Published verification evidence failed custody check")
    if publish_failed:
        raise ReportEvidenceError("Could not exclusively publish complete verification evidence")
