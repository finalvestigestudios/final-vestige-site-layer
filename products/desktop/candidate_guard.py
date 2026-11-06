"""Fail-closed offline custody checks for all six Windows release candidates.

This only checks the exact staging-folder membership, regular-file identity,
and bytes read; it is not code-signing, malware scanning, or release approval.
"""
from __future__ import annotations

import hashlib
from contextlib import contextmanager
import os
import stat
from pathlib import Path

MAX_EXE_BYTES = 512 * 1024 * 1024
MAX_CHECKSUM_BYTES = 4096
CHUNK_BYTES = 1024 * 1024


class CandidateGuardError(ValueError):
    """The staged candidate must not be executed or distributed."""


def _signature(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _same_path_descriptor_signature(path_info: os.stat_result,
                                    descriptor_info: os.stat_result,
                                    *, windows: bool | None = None) -> bool:
    """Keep strict two-view custody while tolerating Windows creation-time API drift.

    Path lstat and fd fstat can report different st_ctime_ns on Windows for an
    unchanged file. Compare all other identity fields across APIs, and retain
    full within-path and within-descriptor timestamp checks around the read.
    Linux retains the full cross-API signature equality.
    """
    if windows is None:
        windows = os.name == "nt"
    path_sig = _signature(path_info)
    descriptor_sig = _signature(descriptor_info)
    return path_sig[:-1] == descriptor_sig[:-1] if windows else path_sig == descriptor_sig


def _ordinary(path: Path, maximum: int) -> os.stat_result:
    try:
        info = path.lstat()
    except OSError:
        raise CandidateGuardError("Missing or inaccessible candidate payload") from None
    if not stat.S_ISREG(info.st_mode) or info.st_nlink > 1:
        raise CandidateGuardError("Candidate payload must be a distinct ordinary file")
    if info.st_size > maximum:
        raise CandidateGuardError("Candidate payload exceeds the safety limit")
    return info


def _read_chunks(stream):
    while chunk := stream.read(CHUNK_BYTES):
        yield chunk



@contextmanager
def _private_candidate_stream(stream):
    """Own the stream even when its context entry fails; redact private I/O.

    Descriptor ownership has passed from os.open to os.fdopen. A failed
    __enter__ does not run __exit__, so explicitly close in that case.
    Keep deliberate validation errors and system interruptions unchanged.
    """
    entered = False
    try:
        with stream:
            entered = True
            yield stream
    except CandidateGuardError:
        raise
    except Exception:
        raise CandidateGuardError("Unable to read candidate payload safely") from None
    finally:
        if not entered:
            try:
                stream.close()
            except Exception:
                # Never report a user-derived exception from failed cleanup.
                pass


def _inspect(path: str | Path, maximum: int, *, return_bytes: bool):
    """Single verified descriptor, no pathname-following, bounded read, pre/post checks.

    On filesystems without O_NOFOLLOW, pre/post lstat checks still reject links
    that remain on disk, but cannot guarantee protection against every race.
    """
    path = Path(path)
    before = _ordinary(path, maximum)
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        descriptor = os.open(path, flags)
    except OSError:
        raise CandidateGuardError("Unable to open candidate payload safely") from None
    # A raw descriptor belongs to this function until fdopen has succeeded.
    # If fdopen fails (including BaseException interruptions), no stream exists
    # to close it. Never leave an untracked handle to a private candidate.
    try:
        stream = os.fdopen(descriptor, "rb")
    except BaseException as exc:
        try:
            os.close(descriptor)
        except OSError:
            pass
        if isinstance(exc, Exception):
            # Suppress OS paths, client-provided messages, and exception chains.
            raise CandidateGuardError("Unable to read candidate payload safely") from None
        raise
    try:
        with _private_candidate_stream(stream):
            opened = os.fstat(stream.fileno())
            if (not _same_path_descriptor_signature(before, opened)
                    or not stat.S_ISREG(opened.st_mode) or opened.st_nlink > 1):
                raise CandidateGuardError("Candidate changed during opening")
            digest = hashlib.sha256()
            chunks = [] if return_bytes else None
            total = 0
            for chunk in _read_chunks(stream):
                total += len(chunk)
                if total > maximum:
                    raise CandidateGuardError("Candidate payload exceeds the safety limit")
                digest.update(chunk)
                if chunks is not None:
                    chunks.append(chunk)
            finished = os.fstat(stream.fileno())
            if total != opened.st_size or _signature(finished) != _signature(opened):
                raise CandidateGuardError("Candidate changed during reading")
    except OSError:
        raise CandidateGuardError("Unable to read candidate payload safely") from None
    after_path = _ordinary(path, maximum)
    if (_signature(after_path) != _signature(before)
            or not _same_path_descriptor_signature(after_path, opened)):
        raise CandidateGuardError("Candidate path changed during reading")
    if return_bytes:
        return b"".join(chunks)
    return digest.hexdigest()


def sha256_candidate(path: str | Path, *, maximum: int = MAX_EXE_BYTES) -> str:
    """Hash a bounded, distinct regular candidate without following file links."""
    return _inspect(path, maximum, return_bytes=False)


def read_checksum_candidate(path: str | Path) -> bytes:
    """Read the exact small ASCII checksum inventory from a verified descriptor."""
    return _inspect(path, MAX_CHECKSUM_BYTES, return_bytes=True)


def check_candidate_directory(folder: str | Path, expected_exes) -> None:
    """Require exactly the six named EXEs and the checksum inventory, nothing else.

    Any stray JSON, script, DLL, readme, hidden file, link or directory makes a
    candidate unsuitable for bulk-archive or distribution. Evidence reports
    belong OUTSIDE this seven-file staging directory; no cleanup is attempted.
    """
    root = Path(folder)
    try:
        info = root.lstat()
        if not stat.S_ISDIR(info.st_mode):
            raise CandidateGuardError("Candidate root must be a real directory")
        members = list(root.iterdir())
    except OSError:
        raise CandidateGuardError("Cannot inspect candidate directory") from None
    allowed = set(expected_exes) | {"SHA256SUMS.txt"}
    if len(members) != len(allowed) or {m.name for m in members} != allowed:
        raise CandidateGuardError("Candidate directory has missing or unapproved payloads")
    for path in members:
        _ordinary(path, MAX_CHECKSUM_BYTES if path.name == "SHA256SUMS.txt" else MAX_EXE_BYTES)
