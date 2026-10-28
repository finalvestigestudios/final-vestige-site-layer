"""Non-destructive file operations for Renewal Radar (Python 3.11+).

Bulk CSV imports are validated completely before any SQLite changes; failures
leave the existing database untouched. Calendar exports never overwrite files.
This module uses only Python's standard library and makes no network calls.
"""
from __future__ import annotations

import csv
import hashlib
import os
import sqlite3
from datetime import date
from pathlib import Path

MAX_IMPORT_BYTES = 8 * 1024 * 1024
MAX_IMPORT_ROWS = 20_000
FIELDS = ("title", "due", "category", "cadence", "remind_days", "notes")
CADENCES = {"none", "monthly", "yearly"}
INSERT_SQL = ("INSERT INTO renewal(title, due, category, cadence, remind_days, notes) "
              "VALUES(?,?,?,?,?,?)")


def _sha256(source: Path) -> str:
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize(row: dict, line: int) -> tuple:
    if None in row or any(value is None for value in row.values()):
        raise ValueError("Record has more or fewer fields than the CSV header.")
    title = (row.get("title") or "").strip()
    due = (row.get("due") or "").strip()
    category = (row.get("category") or "").strip()
    cadence = (row.get("cadence") or "none").strip()
    notes = row.get("notes") or ""
    if not title or len(title) > 200 or "\x00" in title:
        raise ValueError("Renewal title must have 1–200 characters and no NUL bytes.")
    if len(category) > 120 or "\x00" in category:
        raise ValueError("Category must have at most 120 characters and no NUL bytes.")
    if len(notes) > 2000 or "\x00" in notes:
        raise ValueError("Notes must have at most 2000 characters and no NUL bytes.")
    try:
        parsed = date.fromisoformat(due)
    except ValueError as exc:
        raise ValueError("Due date must be a valid YYYY-MM-DD date.") from exc
    if parsed.isoformat() != due:
        raise ValueError("Due date must use YYYY-MM-DD format.")
    if cadence not in CADENCES:
        raise ValueError("Cadence must be none, monthly or yearly.")
    raw_days = (row.get("remind_days") or "30").strip()
    if not raw_days.isascii() or not raw_days.isdecimal():
        raise ValueError("Reminder days must be a whole number from 0 to 3650.")
    remind_days = int(raw_days)
    if remind_days > 3650:
        raise ValueError("Reminder days must be between 0 and 3650.")
    return title, due, category, cadence, remind_days, notes


def import_csv_atomic(conn: sqlite3.Connection, source: Path) -> dict:
    """Import an entire CSV or nothing; reject invalid and duplicate rows.

    Returns {inserted, problems, source_sha256}. Row problem numbers reference
    the first physical CSV line, even when earlier cells contain newlines.
    A repeated identical import is refused to avoid duplicate reminders.
    """
    source = Path(source)
    if source.is_symlink() or not source.is_file():
        raise ValueError("Import must be a regular CSV file, not a link or directory.")
    before = source.stat()
    if before.st_size > MAX_IMPORT_BYTES:
        raise ValueError("CSV exceeds the 8 MiB import safety limit.")
    before_hash = _sha256(source)
    valid: list[tuple] = []
    problems: list[dict] = []
    seen: dict[tuple, int] = {}
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        try:
            columns = reader.fieldnames
        except csv.Error as exc:
            raise ValueError(f"Malformed CSV header: {exc}") from exc
        if (not columns or len(columns) != len(set(columns))
                or not {"title", "due"}.issubset(columns)
                or any(col not in FIELDS for col in columns)):
            raise ValueError("CSV needs unique title,due columns; optional columns: category,cadence,remind_days,notes.")
        last_line = reader.line_num
        try:
            for row in reader:
                start_line = last_line + 1
                last_line = reader.line_num
                if len(valid) + len(problems) >= MAX_IMPORT_ROWS:
                    raise ValueError("CSV exceeds the 20,000-row import limit.")
                try:
                    item = _normalize(row, start_line)
                    key = (item[0].casefold(), *item[1:])
                    if key in seen:
                        raise ValueError(f"Duplicate of CSV row {seen[key]}.")
                    seen[key] = start_line
                    valid.append(item)
                except (TypeError, ValueError) as exc:
                    problems.append({"row": start_line, "reason": str(exc)})
        except csv.Error as exc:
            problems.append({"row": reader.line_num, "reason": f"Malformed CSV: {exc}"})
    after = source.stat()
    if ((before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns)
            or before_hash != _sha256(source)):
        raise ValueError("CSV changed during import review; no rows were added.")
    if not valid and not problems:
        raise ValueError("CSV contains no renewal records.")
    existing = {
        (r[0].casefold(), *r[1:])
        for r in conn.execute("SELECT title, due, category, cadence, remind_days, notes FROM renewal")
    }
    for item in valid:
        if (item[0].casefold(), *item[1:]) in existing:
            problems.append({"row": seen[(item[0].casefold(), *item[1:])],
                             "reason": "Identical renewal already exists in the local database."})
    if problems:
        return {"inserted": 0, "problems": problems, "source_sha256": before_hash}
    with conn:
        conn.executemany(INSERT_SQL, valid)
    return {"inserted": len(valid), "problems": [], "source_sha256": before_hash}


def write_new_file(destination: Path, payload: bytes) -> None:
    """Write a new export exclusively, never replacing an existing file.

    Existing symlinks also fail with FileExistsError under exclusive creation.
    If a disk write fails, remove only this newly created partial file.
    """
    destination = Path(destination)
    created = False
    try:
        with destination.open("xb") as stream:
            created = True
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        if created:
            destination.unlink(missing_ok=True)
        raise
