"""R515–R518: digest-only custody for read-only desktop source evidence.

R516 checks root/hardlink custody, descriptor identity and postread stability.
R517 preserves same-view Windows creation-time custody while avoiding false
path/descriptor mismatches caused by differing st_ctime_ns across APIs.
R518 strips private exception chains and closes unadopted descriptors.
These checks are not atomic tree custody against a concurrent writer.
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


def _same_path_descriptor_identity(path_info: os.stat_result,
                                   descriptor_info: os.stat_result,
                                   *, windows: bool | None = None) -> bool:
    """Compare structural identity without conflating Windows ctime views.

    On Windows, Python path.lstat and descriptor fstat may disagree on
    st_ctime_ns for the very same file. Only omit ctime in cross-view checks;
    retain the full receipt in every before/after check of the same view.
    """
    if windows is None:
        windows = os.name == "nt"
    path_identity = _identity(path_info)
    descriptor_identity = _identity(descriptor_info)
    return (path_identity[:-1] == descriptor_identity[:-1] if windows
            else path_identity == descriptor_identity)


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
        descriptor = os.open(leaf, flags)
        try:
            reader = os.fdopen(descriptor, "rb")
        except (OSError, ValueError):
            # fdopen did not adopt ownership: close the raw descriptor before
            # leaving the handler. Do not retain private OS error chains.
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise
        with reader:
            opened = os.fstat(reader.fileno())
            if (not _regular_unique(opened) or
                    not _same_path_descriptor_identity(before, opened)):
                raise OSError("source changed before open")
            raw = reader.read(_MAX_SOURCE_BYTES + 1)
            after_read = os.fstat(reader.fileno())
        after_path = leaf.lstat()
        if (len(raw) != before.st_size or
                _identity(opened) != _identity(after_read) or
                _identity(before) != _identity(after_path) or
                not _same_path_descriptor_identity(after_path, after_read) or
                not _regular_unique(after_path) or _linked(leaf)):
            raise OSError("source changed during read")
        return sha256(raw).digest()
    except (OSError, ValueError):
        # Raise only AFTER the handler has exited. `raise ... from None`
        # suppresses display but keeps private filenames in __context__.
        pass
    raise SourceSnapshotRejected("Source custody preflight rejected")


def matches_source_fingerprint(root: Path, parts: tuple[str, ...], expected: bytes) -> bool:
    """Fail closed if source bytes, link topology or metadata changed."""
    if type(expected) is not bytes or len(expected) != 32:
        return False
    try:
        return source_fingerprint(root, parts) == expected
    except SourceSnapshotRejected:
        return False
