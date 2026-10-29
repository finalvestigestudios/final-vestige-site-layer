"""Build an unambiguous, bounded, local SHA-256 evidence inventory.

The inventory describes bytes observed while hashing; it is not a signature,
a proof of source immutability since reconciliation, or a compliance judgment.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path

# Source CSV imports have a 64 MiB cap; finished reports can be larger.
MAX_INPUT_BYTES = 64 * 1024 * 1024
MAX_REPORT_BYTES = 256 * 1024 * 1024
CHUNK_BYTES = 1024 * 1024
_HEADER = "SHA-256 file inventory. Hashes do not certify accuracy or compliance.\n"


def _signature(info: os.stat_result) -> tuple[int, int, int, int, int]:
    """Metadata fingerprint for detecting ordinary edits/replacements."""
    return (info.st_dev, info.st_ino, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _metadata(path: Path) -> os.stat_result:
    """lstat (not stat): a link must never redirect a financial inventory."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        raise FileNotFoundError("Inventory evidence file is missing") from None
    except OSError:
        raise ValueError("Cannot inspect inventory evidence file") from None
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("Inventory evidence must be a regular file, not a link")
    return info


def _hash_regular(path: Path, maximum: int) -> tuple[str, tuple[int, int, int, int, int]]:
    """Bounded streaming from one descriptor, with pre/post identity checks."""
    before = _metadata(path)
    if before.st_size > maximum:
        raise ValueError("Inventory evidence exceeds the file-size limit")
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError:
        raise FileNotFoundError("Inventory evidence file is missing") from None
    except OSError:
        raise ValueError("Cannot safely open inventory evidence") from None
    try:
        with os.fdopen(descriptor, "rb") as stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or _signature(opened) != _signature(before):
                raise ValueError("Inventory evidence changed while opening")
            digest = hashlib.sha256()
            total = 0
            while chunk := stream.read(CHUNK_BYTES):
                total += len(chunk)
                if total > maximum:
                    raise ValueError("Inventory evidence exceeds the file-size limit")
                digest.update(chunk)
            finished = os.fstat(stream.fileno())
            if total != opened.st_size or _signature(finished) != _signature(opened):
                raise ValueError("Inventory evidence changed while hashing")
    except OSError:
        raise ValueError("Unable to read inventory evidence") from None
    # Reject replacement of the pathname while the descriptor was being read.
    if _signature(_metadata(path)) != _signature(opened):
        raise ValueError("Inventory evidence path changed while hashing")
    return digest.hexdigest(), _signature(opened)


def inventory_text(inputs, outputs) -> str:
    """Return deterministic UTF-8 inventory text; publication is separate.

    Ambiguous basenames (even with different directories/case) are rejected;
    absolute directory names are never included in the private manifest.
    Files must be regular non-symlinks and remain unchanged through the final
    recheck. This reduces common TOCTOU errors but cannot freeze other writers.
    """
    selected = [(Path(path), MAX_INPUT_BYTES) for path in inputs]
    selected += [(Path(path), MAX_REPORT_BYTES) for path in outputs]
    seen_names: set[str] = set()
    for path, _ in selected:
        label = path.name.casefold()
        if label in seen_names:
            raise ValueError("Ambiguous evidence names; rename duplicate basenames")
        seen_names.add(label)
    lines = [_HEADER]
    snapshots = []
    seen_files: set[tuple[int, int]] = set()
    for path, maximum in selected:
        digest, signature = _hash_regular(path, maximum)
        identity = signature[:2]
        # Ignore absent/zero inode information on filesystems that lack it.
        if identity[1] and identity in seen_files:
            raise ValueError("Evidence files must be distinct, not hard-link aliases")
        if identity[1]:
            seen_files.add(identity)
        safe_name = json.dumps(path.name, ensure_ascii=True)[1:-1]
        lines.append(f"{safe_name}\t{digest}\n")
        snapshots.append((path, signature))
    # Detect changes to earlier files while hashing subsequent files.
    for path, signature in snapshots:
        if _signature(_metadata(path)) != signature:
            raise ValueError("Inventory evidence changed before publication")
    return "".join(lines)
