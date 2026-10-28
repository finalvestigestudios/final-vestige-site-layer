"""Data Import Doctor's offline, deterministic CSV preflight engine.

No dependencies beyond Python's standard library. Does not modify source files.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSION = "0.2.0"
MAX_EXAMPLES = 250
MAX_SOURCE_BYTES = 80 * 1024 * 1024
MAX_SCHEMA_BYTES = 1024 * 1024
MAX_ROWS = 250_000
MAX_FIELD_CHARS = 1_000_000
TYPES = {"integer", "decimal", "date", "boolean", "text"}
SCHEMA_KEYS = {"required_columns", "keys", "types", "allowed_values"}
FATAL_CODES = {"empty_file", "no_data_rows", "csv_parse_error", "duplicate_header",
               "blank_header", "row_limit_exceeded", "source_changed"}
_DECIMAL = re.compile(r"[+-]?(?:(?:[0-9]+)|(?:[0-9]{1,3}(?:,[0-9]{3})+))(?:\.[0-9]+)?\Z")
_INTEGER = re.compile(r"[+-]?[0-9]+\Z")
_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")


def _no_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON property: {key!r}")
        result[key] = value
    return result


def _reject_constant(token: str) -> object:
    raise ValueError(f"JSON value {token!r} is not permitted")


def load_schema(path: Path | None) -> dict:
    """Validate schema strictly so a malformed rule never yields a clean report."""
    if path is None:
        return {}
    if path.stat().st_size > MAX_SCHEMA_BYTES:
        raise ValueError("Schema exceeds the 1 MiB size limit.")
    data = path.read_bytes()
    if len(data) > MAX_SCHEMA_BYTES:
        raise ValueError("Schema exceeds the 1 MiB size limit.")
    schema = json.loads(data.decode("utf-8-sig"), object_pairs_hook=_no_duplicate_json_keys,
                        parse_constant=_reject_constant)
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a JSON object.")
    unknown = set(schema) - SCHEMA_KEYS
    if unknown:
        raise ValueError("Unrecognized schema options: " + ", ".join(sorted(unknown)))
    for key in ("required_columns", "keys"):
        value = schema.get(key, [])
        if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() or x != x.strip() for x in value):
            raise ValueError(f"{key} must be a list of nonblank, unpadded column names.")
        if len(set(value)) != len(value):
            raise ValueError(f"{key} contains duplicate column names.")
    types = schema.get("types", {})
    if not isinstance(types, dict) or any(not isinstance(key, str) or not key.strip() or key != key.strip() or
                                           not isinstance(kind, str) or kind not in TYPES for key, kind in types.items()):
        raise ValueError("types must map column names to integer, decimal, date, boolean, or text.")
    allowed = schema.get("allowed_values", {})
    if not isinstance(allowed, dict) or any(
        not isinstance(key, str) or not key.strip() or key != key.strip() or
        not isinstance(choices, list) or not choices or
        any(not isinstance(choice, str) for choice in choices) or len(set(choices)) != len(choices)
        for key, choices in allowed.items()
    ):
        raise ValueError("allowed_values must map columns to nonempty, unique lists of text values.")
    return schema


def valid_type(value: str, kind: str) -> bool:
    if kind == "text":
        return True
    if kind == "integer":
        return _INTEGER.fullmatch(value) is not None
    if kind == "boolean":
        return value.casefold() in {"yes", "no", "true", "false", "0", "1"}
    if kind == "date":
        if not _DATE.fullmatch(value):
            return False
        try:
            date.fromisoformat(value)
            return True
        except ValueError:
            return False
    if kind == "decimal":
        if not _DECIMAL.fullmatch(value):
            return False
        try:
            return Decimal(value.replace(",", "")).is_finite()
        except InvalidOperation:
            return False
    return False


def _fingerprint(path: Path, *, limit: int) -> tuple[str, int]:
    before = path.stat()
    if not path.is_file():
        raise ValueError("Selected input must be a regular file.")
    if before.st_size > limit:
        raise ValueError(f"Input file exceeds configured limit of {limit} bytes.")
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
            if size > limit:
                raise ValueError(f"Input file exceeds configured limit of {limit} bytes.")
            digest.update(chunk)
    after = path.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
    ) or size != after.st_size:
        raise ValueError("Input changed during hashing. Rerun the analysis.")
    return digest.hexdigest(), size


def _clean_name(value: str) -> str:
    return unicodedata.normalize("NFC", value.strip()).casefold()


def analyze(csv_path: Path, schema_path: Path | None = None) -> dict:
    csv_path = Path(csv_path)
    schema_path = Path(schema_path) if schema_path is not None else None
    source_before, source_size = _fingerprint(csv_path, limit=MAX_SOURCE_BYTES)
    schema_before = _fingerprint(schema_path, limit=MAX_SCHEMA_BYTES)[0] if schema_path else None
    schema = load_schema(schema_path)
    if schema_path and _fingerprint(schema_path, limit=MAX_SCHEMA_BYTES)[0] != schema_before:
        raise ValueError("Schema changed while loading; rerun analysis.")
    counters: Counter[str] = Counter()
    examples: list[dict] = []
    report = {
        "tool": "Final Vestige Data Import Doctor", "version": VERSION,
        "source_file": csv_path.name, "source_sha256": source_before,
        "source_bytes": source_size, "schema_sha256": schema_before,
        "row_count": 0, "columns": [], "delimiter": None,
        "issue_counts": {}, "examples": examples, "examples_truncated": False,
        "scan_complete": True,
    }

    def issue(code: str, row: int, message: str) -> None:
        counters[code] += 1
        if len(examples) < MAX_EXAMPLES:
            examples.append({"code": code, "row": row, "message": message})
        if code in FATAL_CODES:
            report["scan_complete"] = False

    old_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(MAX_FIELD_CHARS)
        with csv_path.open("r", encoding="utf-8-sig", newline="") as stream:
            sample = stream.read(8192)
            stream.seek(0)
            if not sample.strip():
                issue("empty_file", 1, "CSV file contains no header or data.")
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            except csv.Error:
                delimiter = ","
            report["delimiter"] = delimiter
            reader = csv.reader(stream, delimiter=delimiter, strict=True)
            try:
                headers = next(reader)
            except StopIteration:
                headers = []
                if "empty_file" not in counters:
                    issue("empty_file", 1, "CSV file contains no header.")
            except csv.Error as exc:
                headers = []
                issue("csv_parse_error", 1, f"Header parse failed: {exc}")
            clean = [h.strip() for h in headers]
            report["columns"] = clean
            groups = Counter(_clean_name(h) for h in clean if h)
            duplicate_names = {name for name, count in groups.items() if count > 1}
            for name in sorted(duplicate_names):
                issue("duplicate_header", 1, f"Ambiguous duplicate header: {name!r}; rules cannot be trusted.")
            for col, name in enumerate(clean, start=1):
                if not name:
                    issue("blank_header", 1, f"Column {col} has no name.")
            unique_columns = {name: i for i, name in enumerate(clean)
                              if name and groups[_clean_name(name)] == 1}
            if headers:
                for name in schema.get("required_columns", []):
                    if name not in unique_columns:
                        issue("missing_required_column", 1, f"Required column {name!r} missing or ambiguous.")
                for name in schema.get("keys", []):
                    if name not in unique_columns:
                        issue("missing_key_column", 1, f"Key column {name!r} missing or ambiguous.")
                for name in set(schema.get("types", {})) | set(schema.get("allowed_values", {})):
                    if name not in unique_columns:
                        issue("missing_rule_column", 1, f"Rule column {name!r} missing or ambiguous.")
            seen_keys: dict[tuple[str, ...], int] = {}
            previous_line = reader.line_num
            try:
                for row in reader:
                    line_start = previous_line + 1
                    previous_line = reader.line_num
                    report["row_count"] += 1
                    if report["row_count"] > MAX_ROWS:
                        issue("row_limit_exceeded", line_start, f"Review limited to {MAX_ROWS} data records.")
                        break
                    if len(row) != len(clean):
                        issue("column_count_mismatch", line_start, f"Expected {len(clean)} fields, found {len(row)}.")
                        continue
                    if duplicate_names or any(not name for name in clean):
                        # Can't safely attribute values to ambiguous/blank headers.
                        continue
                    values = {name: row[index].strip() for name, index in unique_columns.items()}
                    for col in schema.get("required_columns", []):
                        if col in values and not values[col]:
                            issue("blank_required_value", line_start, f"Required column {col!r} is blank.")
                    keys = schema.get("keys", [])
                    if keys and all(key in values for key in keys):
                        tuple_key = tuple(unicodedata.normalize("NFC", values[key]).casefold() for key in keys)
                        if any(not part for part in tuple_key):
                            issue("blank_key", line_start, "One or more key fields are blank.")
                        elif tuple_key in seen_keys:
                            issue("duplicate_key", line_start,
                                  f"Duplicate key; first record starts on line {seen_keys[tuple_key]}.")
                        else:
                            seen_keys[tuple_key] = line_start
                    for col, kind in schema.get("types", {}).items():
                        value = values.get(col, "")
                        if value and not valid_type(value, kind):
                            issue("invalid_type", line_start, f"Column {col!r} must contain {kind} values.")
                    for col, choices in schema.get("allowed_values", {}).items():
                        value = values.get(col, "")
                        if value and value not in choices:
                            issue("invalid_allowed_value", line_start,
                                  f"Column {col!r} has value outside configured allowed choices.")
            except csv.Error as exc:
                issue("csv_parse_error", previous_line + 1, f"Malformed or oversized CSV field: {exc}")
            if report["row_count"] == 0 and headers:
                issue("no_data_rows", reader.line_num + 1, "CSV contains headers but no data records.")
    finally:
        csv.field_size_limit(old_limit)
    try:
        source_after, _ = _fingerprint(csv_path, limit=MAX_SOURCE_BYTES)
        schema_after = _fingerprint(schema_path, limit=MAX_SCHEMA_BYTES)[0] if schema_path else None
        if source_after != source_before or schema_after != schema_before:
            issue("source_changed", 0, "Input or schema changed during review; results are incomplete.")
    except (OSError, ValueError) as exc:
        issue("source_changed", 0, "Input or schema could not be rechecked: " + str(exc))
    report["issue_counts"] = dict(sorted(counters.items()))
    report["issues_total"] = sum(counters.values())
    report["examples_truncated"] = report["issues_total"] > len(examples)
    report["status"] = ("INCOMPLETE" if not report["scan_complete"] else
                        "ISSUES" if counters else "PASS")
    return report


def safe_export_report(report: dict, destination: Path, source: Path,
                       schema: Path | None = None) -> None:
    """Export a current report exactly once; never replace user data or old reports."""
    destination = Path(destination)
    source = Path(source)
    schema = Path(schema) if schema is not None else None
    dest_absolute = destination.absolute()
    if dest_absolute == source.absolute() or (schema and dest_absolute == schema.absolute()):
        raise ValueError("Report cannot overwrite source CSV or schema JSON.")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Report file already exists; choose a new filename.")
    forbidden = {source.resolve()}
    if schema:
        forbidden.add(schema.resolve())
    if destination.resolve() in forbidden:
        raise ValueError("Report destination resolves to a source file.")
    latest, _ = _fingerprint(source, limit=MAX_SOURCE_BYTES)
    current_schema = _fingerprint(schema, limit=MAX_SCHEMA_BYTES)[0] if schema else None
    if latest != report.get("source_sha256") or current_schema != report.get("schema_sha256"):
        raise ValueError("CSV or schema changed after analysis. Analyze again before exporting.")
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    with destination.open("x", encoding="utf-8", newline="\n") as output:
        output.write(payload)
