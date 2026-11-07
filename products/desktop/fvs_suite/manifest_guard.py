"""Build an unambiguous, bounded, local SHA-256 evidence inventory.

The inventory describes bytes observed while hashing; it is not a signature,
a proof of source immutability since reconciliation, or a compliance judgment.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import unicodedata
from pathlib import Path

from .csv_snapshot import _same_path_descriptor_signature
from .premium_link_custody import open_inventory_stream

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
        # Reuse the leak-safe inventory stream adoption from premium verification.
        # An interrupted or failed fdopen must not leave private evidence open.
        stream = open_inventory_stream(path, flags)
    except FileNotFoundError:
        raise FileNotFoundError("Inventory evidence file is missing") from None
    except Exception:
        raise ValueError("Cannot safely open inventory evidence") from None
    try:
        with stream:
            opened = os.fstat(stream.fileno())
            if not stat.S_ISREG(opened.st_mode) or not _same_path_descriptor_signature(before, opened):
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
    after_path = _metadata(path)
    if (_signature(after_path) != _signature(before)
            or not _same_path_descriptor_signature(after_path, opened)):
        raise ValueError("Inventory evidence path changed while hashing")
    # Return PATH-view identity for the later whole-inventory path recheck.
    # The descriptor's full signature was independently verified above.
    return digest.hexdigest(), _signature(after_path)


def inventory_text(inputs, outputs, *, expected_input_digests=None) -> str:
    """Build a private inventory, optionally binding every CSV to parsed bytes.

    With expected_input_digests, the source digest *must* match the exact
    snapshot that drove the report, even if a later source has the same size.
    No supplied provenance means a descriptive inventory, as before; direct
    callers must not present it as proof of report/source consistency.
    """
    input_paths = [Path(path) for path in inputs]
    output_paths = [Path(path) for path in outputs]
    supplied = None
    if expected_input_digests is not None:
        try:
            supplied = {os.fspath(path): digest for path, digest
                        in expected_input_digests.items()}
        except (AttributeError, TypeError, ValueError):
            raise ValueError("Invalid source digest map") from None
        selected_names = [os.fspath(path) for path in input_paths]
        if (len(selected_names) != len(set(selected_names))
                or set(supplied) != set(selected_names)):
            raise ValueError("Source digest coverage mismatch")
        if any(not isinstance(digest, str)
               or re.fullmatch(r"[0-9a-f]{64}", digest) is None
               for digest in supplied.values()):
            raise ValueError("Invalid source digest")
    selected = [(path, MAX_INPUT_BYTES) for path in input_paths]
    selected += [(path, MAX_REPORT_BYTES) for path in output_paths]
    seen_names: set[str] = set()
    for path, _ in selected:
        label = unicodedata.normalize("NFKC", path.name).casefold()
        if label in seen_names:
            raise ValueError("Ambiguous evidence names; rename duplicate basenames")
        seen_names.add(label)
    lines = [_HEADER]
    snapshots = []
    seen_files: set[tuple[int, int]] = set()
    for index, (path, maximum) in enumerate(selected):
        digest, signature = _hash_regular(path, maximum)
        if (supplied is not None and index < len(input_paths)
                and digest != supplied[os.fspath(path)]):
            raise ValueError("Source bytes changed after reconciliation")
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
