"""R515: digest-only, prelaunch source-file custody for the read-only test matrix.

Source checks may run hundreds of sequential Python processes. An earlier test
must not replace a later test or smoke script after the initial manifest check.
This recheck is not an atomic filesystem sandbox or an executable release gate.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

_MAX_SOURCE_BYTES = 1_048_576


class SourceSnapshotRejected(ValueError):
    """A required source check no longer matches its inspected bytes."""


def source_fingerprint(root: Path, parts: tuple[str, ...]) -> bytes:
    """Hash a regular, unlinked, size-bounded repository source file.

    Never include source bytes, filenames or OS exception text in failures.
    The preflight cannot eliminate an adversarial rename race on every OS.
    """
    if (not isinstance(root, Path) or type(parts) is not tuple or not parts or
            any(type(part) is not str or not part or part in (".", "..") or
                "/" in part or "\\" in part for part in parts)):
        raise SourceSnapshotRejected("Source custody preflight rejected")
    failed = False
    digest = b""
    try:
        leaf = root
        for part in parts:
            leaf = leaf / part
            if leaf.is_symlink():
                raise OSError("linked source")
            junction = getattr(leaf, "is_junction", None)
            if junction is not None and junction():
                raise OSError("linked source")
        if not leaf.is_file():
            raise OSError("missing source")
        with leaf.open("rb") as reader:
            raw = reader.read(_MAX_SOURCE_BYTES + 1)
        if len(raw) > _MAX_SOURCE_BYTES:
            raise OSError("oversized source")
        digest = sha256(raw).digest()
    except (OSError, ValueError):
        failed = True
    if failed:
        raise SourceSnapshotRejected("Source custody preflight rejected")
    return digest


def matches_source_fingerprint(root: Path, parts: tuple[str, ...], expected: bytes) -> bool:
    """Fail closed if source bytes or any path component changed since snapshot."""
    if type(expected) is not bytes or len(expected) != 32:
        return False
    try:
        return source_fingerprint(root, parts) == expected
    except SourceSnapshotRejected:
        return False
