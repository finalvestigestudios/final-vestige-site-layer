"""Build an unambiguous, bounded, local SHA-256 evidence inventory.

The inventory describes bytes observed while hashing; it is not a signature,
a proof of source immutability since reconciliation, or a compliance judgment.
"""
from __future__ import annotations

import hashlib
import os
import re
import stat
import unicodedata
from pathlib import Path

from .csv_snapshot import _same_path_descriptor_signature
from .evidence_label import canonical_evidence_label
from .premium_link_custody import open_inventory_stream, require_single_link

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
    missing = False
    inspect_failed = False
    try:
        info = path.lstat()
    except FileNotFoundError:
        missing = True
    except OSError:
        inspect_failed = True
    # 'raise ... from None' inside except still retains the private pathname
    # in __context__. Raise after leaving the handler instead.
    if missing:
        raise FileNotFoundError("Inventory evidence file is missing")
    if inspect_failed:
        raise ValueError("Cannot inspect inventory evidence file")
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("Inventory evidence must be a regular file, not a link")
    return info


def _hash_regular(path: Path, maximum: int) -> tuple[str, tuple[int, int, int, int, int]]:
    """Bounded streaming from one descriptor, with pre/post identity checks."""
    # Direct API callers must not bypass the absolute report ceiling with
    # infinities, booleans, int subclasses or attacker-sized native integers.
    # Validate BEFORE inspecting or opening a private filesystem path.
    if type(maximum) is not int or not (0 <= maximum <= MAX_REPORT_BYTES):
        raise ValueError("Invalid inventory size limit")
    before = _metadata(path)
    # An external hard-link alias can mutate the same private evidence bytes.
    # Refuse it before opening; repeat the check on every descriptor/path view.
    require_single_link(before)
    if before.st_size > maximum:
        raise ValueError("Inventory evidence exceeds the file-size limit")
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    missing_on_open = False
    open_failed = False
    try:
        # Reuse the leak-safe inventory stream adoption from premium verification.
        # An interrupted or failed fdopen must not leave private evidence open.
        stream = open_inventory_stream(path, flags)
    except FileNotFoundError:
        missing_on_open = True
    except Exception:
        open_failed = True
    # No OS exception holding private path text should remain in the public
    # error chain, including hidden __context__ objects.
    if missing_on_open:
        raise FileNotFoundError("Inventory evidence file is missing")
    if open_failed:
        raise ValueError("Cannot safely open inventory evidence")
    read_failed = False
    try:
        with stream:
            opened = os.fstat(stream.fileno())
            require_single_link(opened)
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
            require_single_link(finished)
            if total != opened.st_size or _signature(finished) != _signature(opened):
                raise ValueError("Inventory evidence changed while hashing")
    except OSError:
        read_failed = True
    if read_failed:
        raise ValueError("Unable to read inventory evidence")
    # Reject replacement of the pathname while the descriptor was being read.
    after_path = _metadata(path)
    require_single_link(after_path)
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
        # Direct API callers must not forge source provenance through a
        # mapping's virtual items()/keys() or a path object's __fspath__ hook.
        # Engine calls pass native dictionaries keyed by str or Path.
        if not isinstance(expected_input_digests, dict):
            raise ValueError("Invalid source digest map")
        supplied = {}
        for path, digest in dict.items(expected_input_digests):
            if type(path) is str:
                name = path
            elif type(path) is type(Path()):
                name = os.fspath(path)
            else:
                raise ValueError("Invalid source digest map")
            if name in supplied:
                raise ValueError("Source digest coverage mismatch")
            supplied[name] = digest
        selected_names = [os.fspath(path) for path in input_paths]
        if (len(selected_names) != len(set(selected_names))
                or set(supplied) != set(selected_names)):
            raise ValueError("Source digest coverage mismatch")
        if any(type(digest) is not str
               or re.fullmatch(r"[0-9a-f]{64}", digest) is None
               for digest in supplied.values()):
            raise ValueError("Invalid source digest")
    selected = [(path, MAX_INPUT_BYTES) for path in input_paths]
    selected += [(path, MAX_REPORT_BYTES) for path in output_paths]
    seen_names: set[str] = set()
    for path, _ in selected:
        # Refuse misleading labels before opening or hashing any private file.
        canonical_evidence_label(path.name)
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
        safe_name = canonical_evidence_label(path.name)
        lines.append(f"{safe_name}\t{digest}\n")
        snapshots.append((path, signature))
    # Detect changes to earlier files while hashing subsequent files.
    for path, signature in snapshots:
        current = _metadata(path)
        # st_nlink is intentionally not part of the five-field fingerprint.
        # Enforce single-link custody separately on the final whole-set pass.
        require_single_link(current)
        if _signature(current) != signature:
            raise ValueError("Inventory evidence changed before publication")
    return "".join(lines)
