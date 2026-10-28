"""Trust boundaries for offline accounts-payable CSV reviews.

No network access; fingerprints do not include file contents in reports.
"""
from __future__ import annotations

import hashlib
import unicodedata
from pathlib import Path

MAX_SOURCE_BYTES = 80 * 1024 * 1024
MAX_PAYMENTS = 200_000
BLOCK = 1024 * 1024


def normalize_search_key(text: str) -> str:
    """Preserve Unicode letters/digits while normalizing presentation differences.

    This is a candidate-matching key, not evidence of vendor identity.
    """
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return "".join(char for char in normalized if char.isalnum())


def resolve_headers(headers: list[str] | None,
                    aliases: dict[str, set[str]],
                    required: set[str]) -> dict[str, str]:
    """Reject duplicate or ambiguous logical columns rather than guessing."""
    if not headers:
        raise ValueError("Empty CSV file or missing header row.")
    normalized: dict[str, str] = {}
    for header in headers:
        if not isinstance(header, str) or not header.strip():
            raise ValueError("CSV contains a blank column heading.")
        key = unicodedata.normalize("NFKC", header).strip().casefold()
        if key in normalized:
            raise ValueError("Repeated CSV column heading: " + repr(header))
        normalized[key] = header
    canonical: dict[str, str] = {}
    for field, choices in aliases.items():
        matches = [original for key, original in normalized.items() if key in choices]
        if len(matches) > 1:
            raise ValueError("Ambiguous " + field + " columns: " + ", ".join(matches))
        if matches:
            canonical[field] = matches[0]
    missing = required - canonical.keys()
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
    return canonical


def source_fingerprint(path: Path) -> dict[str, str | int]:
    """Hash a stable regular file, detecting replacement and in-flight edits."""
    if not path.is_file():
        raise ValueError("Select an existing CSV file.")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        before = stream.fileno()
        import os
        first = os.fstat(before)
        if first.st_size > MAX_SOURCE_BYTES:
            raise ValueError("CSV exceeds the 80 MiB safe import limit.")
        for chunk in iter(lambda: stream.read(BLOCK), b""):
            digest.update(chunk)
        last = os.fstat(before)
    current = path.stat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
    if identity(first) != identity(last) or identity(last) != identity(current):
        raise ValueError("CSV changed during integrity check; review stopped.")
    return {"sha256": digest.hexdigest(), "bytes": last.st_size}


def record_start_line(end_line: int, row: dict) -> int:
    """Locate the physical first line of a CSV record even after blank lines.

    DictReader.line_num counts consumed physical lines, including quoted
    newlines. Those are preserved in returned field values; subtract them.
    """
    if not isinstance(end_line, int) or end_line < 1:
        raise ValueError("Invalid CSV source line number.")
    values = []
    for value in row.values():
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, list):  # DictReader restkey for extra fields
            values.extend(item for item in value if isinstance(item, str))
    inside = sum(value.count("\n") + value.count("\r") - value.count("\r\n")
                 for value in values)
    start = end_line - inside
    if start < 1:
        raise ValueError("Invalid multiline CSV row boundary.")
    return start
