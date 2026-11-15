"""Bounded post-publication verification of local premium evidence inventories.

The SHA-256 inventory is descriptive, not signed proof of compliance. Recheck
its report entries before the GUI announces success; never read source CSVs,
write output, log customer filenames, or approve financial decisions.
"""
from __future__ import annotations

import json
import os
import re
import stat
import unicodedata
from pathlib import Path

from .csv_snapshot import _same_path_descriptor_signature
from .evidence_label import canonical_evidence_label
from .manifest_guard import MAX_REPORT_BYTES, _hash_regular
from .premium_link_custody import open_inventory_stream, require_single_link

_HEADER = "SHA-256 file inventory. Hashes do not certify accuracy or compliance."
_HEX = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)
_MAX_MANIFEST_BYTES = 128 * 1024
# Grant: claims, ledger, budget. Procurement: PO, invoice, receipt, optional policy.
_INPUT_COUNTS = {"grants": (3,), "procurement": (3, 4)}
_REPORT_COUNTS = {"grants": 2, "procurement": 1}


def _signature(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def _read_bounded_inventory(path: Path) -> str:
    """Read one regular manifest descriptor with pre/post pathname custody."""
    read_failed = False
    try:
        before = path.lstat()
        if (not stat.S_ISREG(before.st_mode)
                or not 0 < before.st_size <= _MAX_MANIFEST_BYTES):
            raise ValueError("Invalid premium evidence inventory")
        require_single_link(before)
        flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
                 | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with open_inventory_stream(path, flags) as stream:
            opened = os.fstat(stream.fileno())
            require_single_link(opened)
            if (not stat.S_ISREG(opened.st_mode)
                    or not _same_path_descriptor_signature(before, opened)):
                raise ValueError("Premium inventory changed while opening")
            raw = stream.read(_MAX_MANIFEST_BYTES + 1)
            finished = os.fstat(stream.fileno())
            require_single_link(finished)
            if (len(raw) != before.st_size
                    or _signature(finished) != _signature(opened)):
                raise ValueError("Premium inventory changed while reading")
        after = path.lstat()
        require_single_link(after)
        if (_signature(after) != _signature(before)
                or not _same_path_descriptor_signature(after, finished)):
            raise ValueError("Premium inventory was replaced")
        decoded = raw.decode("ascii", errors="strict")
    except (OSError, UnicodeError):
        read_failed = True
    # An OSError can contain private file paths; a UnicodeDecodeError can
    # retain the entire private manifest in .object. Do not attach either
    # exception as __context__ on the public verifier refusal.
    if read_failed:
        raise ValueError("Cannot verify premium evidence inventory")
    return decoded


def verify_premium_inventory(paths: tuple[Path, ...], app_id: str) -> None:
    """Require precisely the published report bytes referenced by a manifest.

    Input digest entries document the original builder's source snapshots and
    are NOT revalidated here. This is a point-in-time local integrity check,
    not a signature, immutable audit vault, or protection from privileged edits.
    """
    count = _REPORT_COUNTS.get(app_id)
    if count is None or len(paths) != count + 1:
        raise ValueError("Invalid premium evidence inventory layout")
    reports, manifest = paths[:-1], paths[-1]
    if manifest.parent != reports[0].parent:
        raise ValueError("Premium inventory is outside the evidence package")
    # The atomic publisher creates only this inventory and the output reports.
    # Detect injected/leftover files before silently treating the bundle as complete.
    inspect_failed = False
    try:
        entries = set(manifest.parent.iterdir())
    except OSError:
        inspect_failed = True
    if inspect_failed:
        raise ValueError("Cannot inspect premium evidence package")
    if entries != set(paths):
        raise ValueError("Premium evidence package contains unexpected files")
    content = _read_bounded_inventory(manifest)
    if not content.endswith("\n") or "\r" in content:
        raise ValueError("Malformed premium evidence inventory")
    lines = content.splitlines()
    if not lines or lines[0] != _HEADER:
        raise ValueError("Malformed premium evidence inventory")
    rows = lines[1:]
    if len(rows) - count not in _INPUT_COUNTS[app_id]:
        raise ValueError("Unexpected premium inventory entry count")
    decoded_names: set[str] = set()
    for row in rows:
        fields = row.split("\t")
        if len(fields) != 2 or _HEX.fullmatch(fields[1]) is None:
            raise ValueError("Malformed premium evidence inventory entry")
        invalid_label = False
        try:
            name = json.loads('"' + fields[0] + '"')
        except (ValueError, TypeError):
            invalid_label = True
        if invalid_label:
            raise ValueError("Malformed premium evidence inventory label")
        # Each inventory row must be one canonical writer-produced basename.
        # Reject visually misleading controls and alternate JSON spellings
        # before those labels reach a human reviewer or exported evidence.
        invalid_name = False
        try:
            canonical = canonical_evidence_label(name)
        except ValueError:
            invalid_name = True
        if invalid_name:
            raise ValueError("Invalid premium evidence label")
        if fields[0] != canonical:
            raise ValueError("Noncanonical premium evidence label")
        folded = unicodedata.normalize("NFKC", name).casefold()
        if folded in decoded_names:
            raise ValueError("Ambiguous premium inventory names")
        decoded_names.add(folded)
    report_snapshots: list[tuple[Path, tuple[int, int, int, int, int]]] = []
    for path, entry in zip(reports, rows[-count:]):
        # Inventory writer JSON-escapes a *basename* and writes lowercase SHA.
        expected_name = json.dumps(path.name, ensure_ascii=True)[1:-1]
        inspect_failed = False
        try:
            require_single_link(path.lstat())
        except OSError:
            inspect_failed = True
        if inspect_failed:
            raise ValueError("Cannot inspect premium report link custody")
        digest, signature = _hash_regular(path, MAX_REPORT_BYTES)
        if entry != f"{expected_name}\t{digest}":
            raise ValueError("Premium report does not match evidence inventory")
        report_snapshots.append((path, signature))

    # Reports can take time to hash. Recheck every published file and directory
    # after hashing, so late edits are not implicitly selected for review.
    # This remains point-in-time verification, not a durable filesystem lock.
    if _read_bounded_inventory(manifest) != content:
        raise ValueError("Premium inventory changed while reports were verified")
    recheck_failed = False
    try:
        for path, signature in report_snapshots:
            current = path.lstat()
            require_single_link(current)
            if not stat.S_ISREG(current.st_mode) or _signature(current) != signature:
                raise ValueError("Premium report changed during package verification")
        if set(manifest.parent.iterdir()) != set(paths):
            raise ValueError("Premium evidence package changed during verification")
    except OSError:
        recheck_failed = True
    if recheck_failed:
        raise ValueError("Cannot recheck premium evidence package")
