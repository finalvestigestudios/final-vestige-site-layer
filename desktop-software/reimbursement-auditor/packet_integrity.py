"""Local packet fingerprints and safe report saving for Reimbursement Auditor.

Hashes prove only byte identity across scans, never the authenticity of receipts
or compliance with a reimbursement program. No content leaves the computer.
"""
from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

MAX_CSV_BYTES = 32 * 1024 * 1024
MAX_ATTACHMENT_FILES = 5000
MAX_ATTACHMENT_BYTES = 2 * 1024 * 1024 * 1024
CHUNK = 1024 * 1024


def _is_inside(path: Path, folder: Path) -> bool:
    return path.resolve().is_relative_to(folder.resolve())


def hash_file(path: Path, *, max_bytes: int | None = None) -> dict:
    """Fingerprint a regular non-symlink file; reject changes during hashing."""
    if path.is_symlink():
        raise ValueError(f"Symbolic-link file is not allowed: {path.name}")
    before = path.stat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError(f"Not a regular file: {path.name}")
    if max_bytes is not None and before.st_size > max_bytes:
        raise ValueError(f"File exceeds {max_bytes} byte limit: {path.name}")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for data in iter(lambda: stream.read(CHUNK), b""):
            size += len(data)
            if max_bytes is not None and size > max_bytes:
                raise ValueError(f"File grew beyond {max_bytes} byte limit: {path.name}")
            digest.update(data)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns, before.st_ino) != (
        after.st_size, after.st_mtime_ns, after.st_ino
    ) or size != after.st_size:
        raise ValueError(f"File changed while being read: {path.name}")
    return {"bytes": size, "sha256": digest.hexdigest()}


def input_fingerprints(claims: Path, support: Path) -> dict:
    """Capture the two input CSVs; duplicate paths cannot be independent evidence."""
    if claims.resolve() == support.resolve():
        raise ValueError("Claims and support index must be different files.")
    return {
        "claims": hash_file(claims, max_bytes=MAX_CSV_BYTES),
        "support": hash_file(support, max_bytes=MAX_CSV_BYTES),
    }


def attachment_inventory(folder: Path, claims: Path, support: Path) -> dict:
    """Snapshot the evidence directory, recording uninspectable entries as errors.

    We deliberately include files not referenced in the support index, so a
    later addition or removal invalidates a previously generated report.
    """
    if folder.is_symlink():
        raise ValueError("Attachment folder must not be a symbolic link.")
    folder = folder.resolve(strict=True)
    if not folder.is_dir():
        raise ValueError("Attachment path must be a folder.")
    excluded = {claims.resolve(), support.resolve()}
    entries: list[dict] = []
    errors: list[dict] = []
    file_count = 0
    total_bytes = 0

    def walk_error(exc: OSError) -> None:
        errors.append({"path": "[directory]", "error": str(exc)})

    for parent, directories, files in os.walk(folder, topdown=True, followlinks=False,
                                              onerror=walk_error):
        base = Path(parent)
        for name in list(directories):
            candidate = base / name
            if candidate.is_symlink():
                directories.remove(name)
                errors.append({"path": candidate.relative_to(folder).as_posix(),
                               "error": "Symbolic-link directory not inspected"})
        directories.sort()
        for name in sorted(files):
            candidate = base / name
            rel = candidate.relative_to(folder).as_posix()
            if candidate.is_symlink():
                errors.append({"path": rel, "error": "Symbolic-link file not inspected"})
                continue
            if candidate in excluded or candidate.resolve() in excluded:
                continue
            file_count += 1
            if file_count > MAX_ATTACHMENT_FILES:
                raise ValueError("Attachment folder exceeds the 5000-file scan limit.")
            try:
                stat_info = candidate.stat()
                total_bytes += stat_info.st_size
                if total_bytes > MAX_ATTACHMENT_BYTES:
                    raise ValueError("Attachment folder exceeds the 2 GiB scan limit.")
                item = hash_file(candidate)
                entries.append({"path": rel, **item})
            except (OSError, ValueError) as exc:
                # Never claim a fully inspected packet when one entry failed.
                errors.append({"path": rel, "error": str(exc)})
    return {"files": sorted(entries, key=lambda x: x["path"]),
            "errors": sorted(errors, key=lambda x: x["path"])}


def packet_snapshot(claims: Path, support: Path, folder: Path) -> dict:
    before = input_fingerprints(claims, support)
    inventory = attachment_inventory(folder, claims, support)
    after = input_fingerprints(claims, support)
    if before != after:
        raise ValueError("Input CSV changed while the packet was being inspected.")
    return {"sources": before, "attachments": inventory}


def ensure_fresh(snapshot: dict, claims: Path, support: Path, folder: Path) -> None:
    if snapshot != packet_snapshot(claims, support, folder):
        raise ValueError("Packet changed since analysis; run the audit again before saving.")


def write_report(destination: Path, content: str, claims: Path, support: Path,
                 folder: Path, snapshot: dict) -> None:
    """Write a report exclusively, after resnapshotting all inputs."""
    destination = destination.absolute()
    if destination.suffix.lower() not in (".html", ".json"):
        raise ValueError("Report must have .html or .json extension.")
    if destination.resolve() in (claims.resolve(), support.resolve()):
        raise ValueError("Report cannot replace an input CSV.")
    if _is_inside(destination, folder):
        raise ValueError("Save reports outside the attachment folder to preserve evidence.")
    ensure_fresh(snapshot, claims, support, folder)
    # 'x' is exclusive: existing reports are never silently replaced.
    with destination.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
