"""Offline, fail-closed filesystem/checklist guardrails for Packet Preflight.

The scanner reads filenames and metadata only. It never follows symbolic links,
opens document contents, alters source files, or makes network requests.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import math
import os
import stat
import unicodedata
from functools import lru_cache
from pathlib import Path

MAX_CHECKLIST_BYTES = 1_048_576
MAX_RULES = 1_000


def validate_checklist(config: object) -> dict:
    if not isinstance(config, dict):
        raise ValueError("Checklist must be a JSON object.")
    rules = config.get("rules")
    if not isinstance(rules, list) or not rules or len(rules) > MAX_RULES:
        raise ValueError(f"Checklist must contain 1–{MAX_RULES} rules.")
    if "title" in config and not isinstance(config["title"], str):
        raise ValueError("Checklist title must be text.")
    if not isinstance(config.get("forbid_unmatched", False), bool):
        raise ValueError("forbid_unmatched must be true or false.")
    _positive_limit(config.get("max_total_size_mb"), "max_total_size_mb")
    names = set()
    for n, rule in enumerate(rules, 1):
        if not isinstance(rule, dict):
            raise ValueError(f"Rule {n} must be an object.")
        name, pattern = rule.get("name"), rule.get("pattern")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Rule {n}: name is required.")
        if name.strip().casefold() in names:
            raise ValueError(f"Rule {n}: duplicate rule name {name!r}.")
        names.add(name.strip().casefold())
        if not isinstance(pattern, str) or not pattern or "\\" in pattern or ":" in pattern or "\x00" in pattern:
            raise ValueError(f"Rule {n}: invalid relative glob pattern.")
        segments = pattern.split("/")
        if any(part in {"", ".", ".."} for part in segments) or pattern.startswith("/"):
            raise ValueError(f"Rule {n}: pattern must be relative and cannot traverse directories.")
        if any(ord(char) < 32 for char in pattern):
            raise ValueError(f"Rule {n}: pattern contains control characters.")
        minimum, maximum = rule.get("minimum", 1), rule.get("maximum")
        if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 0:
            raise ValueError(f"Rule {n}: minimum must be a nonnegative integer.")
        if maximum is not None and (isinstance(maximum, bool) or not isinstance(maximum, int) or maximum < minimum):
            raise ValueError(f"Rule {n}: maximum must be at least minimum.")
        if not isinstance(rule.get("allow_empty", False), bool):
            raise ValueError(f"Rule {n}: allow_empty must be true or false.")
        _positive_limit(rule.get("max_size_mb"), f"Rule {n}: max_size_mb")
        extensions = rule.get("extensions", [])
        if not isinstance(extensions, list) or any(
            not isinstance(ext, str) or len(ext) < 2 or not ext.startswith(".") or
            any(ch in ext for ch in "/\\:\x00") or ext != ext.strip()
            for ext in extensions
        ):
            raise ValueError(f"Rule {n}: extensions must be values such as '.pdf'.")
    return config


def _positive_limit(value: object, name: str) -> None:
    if value is not None and (
        isinstance(value, bool) or not isinstance(value, (int, float))
        or (isinstance(value, float) and not math.isfinite(value)) or value <= 0 or value > 1_000_000_000
    ):
        raise ValueError(f"{name} must be a positive finite number.")


def load_checklist(path: Path) -> tuple[dict, str]:
    """Read a bounded checklist and reject modification during the read."""
    before = path.stat()
    if before.st_size > MAX_CHECKLIST_BYTES:
        raise ValueError("Checklist exceeds 1 MiB safety limit.")
    raw = path.read_bytes()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError("Checklist changed during analysis; retry.")
    if len(raw) > MAX_CHECKLIST_BYTES:
        raise ValueError("Checklist exceeds 1 MiB safety limit.")
    try:
        config = json.loads(raw.decode("utf-8-sig"))
    except UnicodeError as exc:
        raise ValueError("Checklist must be UTF-8 JSON.") from exc
    return validate_checklist(config), hashlib.sha256(raw).hexdigest()


def match_relative_path(relative: str, pattern: str) -> bool:
    """Case-insensitive, directory-anchored glob: '*' does not consume '/'.

    '**' as an entire directory component matches zero or more directories.
    '*.pdf' matches ONLY the selected folder, not nested descendants.
    """
    if not isinstance(relative, str) or not relative or relative.startswith("/"):
        return False
    paths = tuple(relative.casefold().split("/"))
    globs = tuple(pattern.casefold().split("/"))

    @lru_cache(maxsize=None)
    def matches(i: int, j: int) -> bool:
        if i == len(globs):
            return j == len(paths)
        if globs[i] == "**":
            return matches(i + 1, j) or (j < len(paths) and matches(i, j + 1))
        return j < len(paths) and fnmatch.fnmatchcase(paths[j], globs[i]) and matches(i + 1, j + 1)

    return matches(0, 0)


def scan_files(root: Path) -> tuple[list[dict], list[dict]]:
    """Walk without following symlinks; make skipped paths and walk errors visible."""
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Select a folder.")
    files: list[dict] = []
    errors: list[dict] = []

    def walk_error(exc: OSError) -> None:
        try:
            location = Path(exc.filename).relative_to(root).as_posix() if exc.filename else "."
        except (ValueError, TypeError):
            location = "."
        errors.append({"file": location, "message": f"Cannot scan folder: {exc.strerror or exc}"})

    for directory, folders, filenames in os.walk(root, topdown=True, followlinks=False, onerror=walk_error):
        retained = []
        for folder in sorted(folders):
            path = Path(directory) / folder
            if path.is_symlink():
                errors.append({"file": path.relative_to(root).as_posix(), "message": "Symbolic-link folder skipped."})
            else:
                retained.append(folder)
        folders[:] = retained
        for name in sorted(filenames):
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            try:
                metadata = path.lstat()
                if stat.S_ISLNK(metadata.st_mode):
                    errors.append({"file": relative, "message": "Symbolic-link file skipped."})
                    continue
                if not stat.S_ISREG(metadata.st_mode):
                    errors.append({"file": relative, "message": "Non-regular file skipped."})
                    continue
                files.append({"path": relative, "bytes": metadata.st_size, "mtime_ns": metadata.st_mtime_ns})
            except OSError as exc:
                errors.append({"file": relative, "message": f"Cannot inspect file: {exc.strerror or exc}"})
    # A submission that differs only in Unicode normalization/case would be
    # ambiguous on ordinary Windows file systems. Do not report it as clean.
    seen: dict[str, str] = {}
    for item in files:
        folded = unicodedata.normalize("NFC", item["path"]).casefold()
        if folded in seen:
            errors.append({"file": item["path"], "message": f"Windows filename collision with {seen[folded]!r}."})
        else:
            seen[folded] = item["path"]
    return files, errors


def snapshot_digest(files: list[dict], errors: list[dict]) -> str:
    payload = {"files": sorted(files, key=lambda f: f["path"]),
               "errors": sorted(errors, key=lambda e: (e["file"], e["message"]))}
    canonical = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def write_new_report(destination: Path, text: str, *, packet_folder: Path | None = None,
                     protected: tuple[Path, ...] = ()) -> None:
    """Create a new output only; never overwrite source, checklist or report.

    Output within the scanned packet is forbidden because it would change the
    inventory being certified. Exclusive creation closes the overwrite race.
    """
    destination = Path(destination)
    resolved = destination.resolve(strict=False)
    if packet_folder is not None and resolved.is_relative_to(packet_folder.resolve(strict=True)):
        raise ValueError("Save reports outside the submission folder.")
    for candidate in protected:
        if resolved == candidate.resolve(strict=False):
            raise ValueError("Report destination conflicts with an input file.")
    with destination.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
