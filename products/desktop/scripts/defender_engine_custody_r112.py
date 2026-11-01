"""Fail-closed identity/hash custody for the installed local Defender scan engine.

Independent of customer files and application data.  This only establishes
that the same ordinary scanner file was observed around each command; it is
NOT proof of AV clearance, code signing of the candidates, or release approval.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import stat

MAX_SCANNER_BYTES = 128 * 1024 * 1024
VERSION = re.compile(r"\A\d+(?:\.\d+){2,4}(?:-\d+)?\Z", re.ASCII)


class EngineHold(ValueError):
    """The claimed Defender engine cannot be bound to a stable local file."""


@dataclass(frozen=True)
class EnginePin:
    sha256: str
    # The fingerprint records file identity, not its absolute local path.
    path_identity: tuple[int, int, int, int, int]


def platform_version(name: str) -> tuple[int, ...] | None:
    """Parse Defender Platform numeric directories without lexical sorting bugs.

    Supports installed four-component versions and optional dash revision;
    rejects unrecognized directory labels rather than guessing their order.
    """
    if type(name) is not str or not VERSION.fullmatch(name):
        return None
    version, dash, revision = name.partition("-")
    numbers = tuple(int(n) for n in version.split("."))
    if any(n > 2**31 - 1 for n in numbers):
        return None
    return numbers + (0,) * (5 - len(numbers)) + (int(revision) if dash else 0,)


def installed_platform_engines(root: Path) -> list[Path]:
    """Prefer latest numeric Defender build; ignore malformed/reparse folders."""
    try:
        if not root.is_dir() or root.is_symlink():
            return []
        candidates = []
        for folder in root.iterdir():
            if not folder.is_dir() or folder.is_symlink():
                continue
            order = platform_version(folder.name)
            if order is None:
                continue
            scanner = folder / "MpCmdRun.exe"
            if scanner.is_file() and not scanner.is_symlink():
                candidates.append((order, scanner))
        candidates.sort(key=lambda item: item[0], reverse=True)
        return [p for _, p in candidates]
    except (OSError, ValueError):
        raise EngineHold("Defender platform location cannot be verified") from None


def _signature(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _same_cross_view(path_signature, fd_signature, *, windows: bool | None = None) -> bool:
    """Windows descriptor/path ctime differs; compare SAME view fully."""
    if windows is None:
        windows = os.name == "nt"
    return (path_signature[:-1] == fd_signature[:-1] if windows
            else path_signature == fd_signature)


def fingerprint(scanner: Path) -> EnginePin:
    """Read a bounded executable on one descriptor and reject observed swaps.

    This protects scanner identity between commands, not an atomic scanner
    launch: OS-protected installation directories and a trusted host remain
    prerequisites for valid security-review evidence.
    """
    scanner = Path(scanner)
    try:
        resolved = scanner.resolve(strict=True)
        before = scanner.lstat()
        initial = _signature(before)
        if (scanner.is_symlink() or not stat.S_ISREG(before.st_mode)
                or before.st_nlink != 1
                or not 1 <= before.st_size <= MAX_SCANNER_BYTES):
            raise EngineHold("Defender scanner file is unsafe")
        flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(scanner, flags)
        try:
            opened = os.fstat(fd)
            if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                    or not _same_cross_view(initial, _signature(opened))):
                raise EngineHold("Defender scanner changed while opening")
            digest = hashlib.sha256()
            total = 0
            while total <= MAX_SCANNER_BYTES:
                chunk = os.read(fd, min(1024 * 1024, MAX_SCANNER_BYTES + 1 - total))
                if not chunk:
                    break
                total += len(chunk)
                digest.update(chunk)
            if (total != opened.st_size or total > MAX_SCANNER_BYTES
                    or _signature(os.fstat(fd)) != _signature(opened)):
                raise EngineHold("Defender scanner changed during hashing")
        finally:
            os.close(fd)
        after = scanner.lstat()
        if (_signature(after) != initial or scanner.resolve(strict=True) != resolved):
            raise EngineHold("Defender scanner path changed")
        return EnginePin(digest.hexdigest(), initial)
    except EngineHold:
        raise
    except (OSError, RuntimeError, OverflowError, ValueError, TypeError):
        raise EngineHold("Defender scanner cannot be fingerprinted safely") from None


def require_same_engine(scanner: Path, pinned: EnginePin) -> None:
    """Refuse a changed scanner before/after every external scan command."""
    if type(pinned) is not EnginePin or fingerprint(scanner) != pinned:
        raise EngineHold("Defender scanner changed during six-app scan")
