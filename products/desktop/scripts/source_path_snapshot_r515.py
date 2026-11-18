"""R515/R516: digest-only custody for read-only desktop source evidence.

R516 additionally checks root and hard-link custody, descriptor identity and
post-read stability. These checks reduce common filesystem races; they cannot
provide atomic tree custody against an adversarial concurrent writer.
"""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import stat

_MAX_SOURCE_BYTES = 1_048_576


class SourceSnapshotRejected(ValueError):
    """A required source check cannot be trusted or has changed."""


def _linked(path: Path) -> bool:
    if path.is_symlink():
        return True
    junction = getattr(path, "is_junction", None)
    return bool(junction is not None and junction())


def _identity(receipt: os.stat_result) -> tuple[int, ...]:
    return (receipt.st_dev, receipt.st_ino, receipt.st_mode, receipt.st_nlink,
            receipt.st_size, receipt.st_mtime_ns, receipt.st_ctime_ns)


def _regular_unique(receipt: os.stat_result) -> bool:
    return (stat.S_ISREG(receipt.st_mode) and receipt.st_nlink == 1 and
            0 <= receipt.st_size <= _MAX_SOURCE_BYTES)


def source_fingerprint(root: Path, parts: tuple[str, ...]) -> bytes:
    """Hash an unlinked regular source with bounded, stable descriptor receipts.

    Sanitize all errors; neither the path, original bytes nor OS error text is
    suitable for source CI logs. O_NOFOLLOW covers leaf swap races where available.
    """
    if (not isinstance(root, Path) or not root.is_absolute() or
            ".." in root.parts or type(parts) is not tuple or not parts or
            any(type(part) is not str or not part or part in (".", "..") or
                "/" in part or "\\" in part for part in parts)):
        raise SourceSnapshotRejected("Source custody preflight rejected")
    try:
        # A linked checkout root bypassed R515's leaf/descendant path checks.
        if any(_linked(ancestor) for ancestor in (root, *root.parents)) or not root.is_dir():
            raise OSError("untrusted checkout root")
        leaf = root
        for part in parts:
            leaf = leaf / part
            if _linked(leaf):
                raise OSError("linked source")
        before = leaf.lstat()
        if not _regular_unique(before):
            raise OSError("non-unique or oversized source")
        flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0) |
                 getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0) |
                 getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(os.open(leaf, flags), "rb") as reader:
            opened = os.fstat(reader.fileno())
            if not _regular_unique(opened) or _identity(opened) != _identity(before):
                raise OSError("source changed before open")
            raw = reader.read(_MAX_SOURCE_BYTES + 1)
            after_read = os.fstat(reader.fileno())
        after_path = leaf.lstat()
        if (len(raw) != before.st_size or
                _identity(before) != _identity(after_read) or
                _identity(before) != _identity(after_path) or
                not _regular_unique(after_path) or _linked(leaf)):
            raise OSError("source changed during read")
        return sha256(raw).digest()
    except (OSError, ValueError):
        raise SourceSnapshotRejected("Source custody preflight rejected") from None


def matches_source_fingerprint(root: Path, parts: tuple[str, ...], expected: bytes) -> bool:
    """Fail closed if source bytes, link topology or metadata changed."""
    if type(expected) is not bytes or len(expected) != 32:
        return False
    try:
        return source_fingerprint(root, parts) == expected
    except SourceSnapshotRejected:
        return False
