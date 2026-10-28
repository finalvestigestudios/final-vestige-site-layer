"""Data Import Doctor: offline CSV import-preflight engine and desktop UI.

Python 3.11+. Does not modify original data or access networks.
Schema example:
{"required_columns":["id","amount"],"keys":["id"],
 "types":{"amount":"decimal","date":"date","quantity":"integer"},
 "allowed_values":{"status":["open","closed"]}}
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSION = "0.1.0"
MAX_EXAMPLES = 250
TYPES = {"integer", "decimal", "date", "boolean", "text"}


def load_schema(path: Path | None) -> dict:
    if path is None:
        return {}
    with path.open(encoding="utf-8") as stream:
        schema = json.load(stream)
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a JSON object.")
    for key in ("required_columns", "keys"):
        values = schema.get(key, [])
        if not isinstance(values, list) or any(not isinstance(v, str) or not v for v in values):
            raise ValueError(f"{key} must be a list of column names.")
    types = schema.get("types", {})
    if not isinstance(types, dict) or any(
        not isinstance(k, str) or v not in TYPES for k, v in types.items()
    ):
        raise ValueError("types must map column names to integer, decimal, date, boolean, or text.")
    allowed = schema.get("allowed_values", {})
    if not isinstance(allowed, dict) or any(
        not isinstance(k, str) or not isinstance(v, list) or
        any(not isinstance(item, str) for item in v) for k, v in allowed.items()
    ):
        raise ValueError("allowed_values must map column names to lists of strings.")
    return schema


def valid_type(value: str, kind: str) -> bool:
    if kind == "text":
        return True
    if kind == "integer":
        return re.fullmatch(r"[+-]?\d+", value) is not None
    if kind == "boolean":
        return value.casefold() in {"yes", "no", "true", "false", "0", "1"}
    if kind == "date":
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
            return False
        try:
            date.fromisoformat(value)
            return True
        except ValueError:
            return False
    if kind == "decimal":
        try:
            return Decimal(value.replace(",", "")).is_finite()
        except InvalidOperation:
            return False
    return False


def analyze(csv_path: Path, schema_path: Path | None = None) -> dict:
    schema = load_schema(schema_path)
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)
    counters: Counter = Counter()
    examples: list[dict] = []
    report = {
        "tool": "Final Vestige Data Import Doctor",
        "version": VERSION,
        "source_file": csv_path.name,
        "row_count": 0,
        "columns": [],
        "delimiter": None,
        "issue_counts": {},
        "examples": examples,
        "examples_truncated": False,
    }

    def issue(code: str, row: int, message: str) -> None:
        counters[code] += 1
        if len(examples) < MAX_EXAMPLES:
            examples.append({"code": code, "row": row, "message": message})

    with csv_path.open("r", encoding="utf-8-sig", newline="") as stream:
        sample = stream.read(8192)
        stream.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ","
        report["delimiter"] = delimiter
        reader = csv.reader(stream, delimiter=delimiter, strict=True)
        try:
            headers = next(reader)
        except StopIteration:
            issue("empty_file", 1, "CSV file is empty.")
            headers = []
        except csv.Error as exc:
            issue("csv_parse_error", 1, f"Header parse failure: {exc}")
            headers = []
        clean = [h.strip() for h in headers]
        report["columns"] = clean
        normalized = [h.casefold() for h in clean]
        duplicates = [h for h, n in Counter(normalized).items() if n > 1]
        for name in duplicates:
            issue("duplicate_header", 1, f"Duplicate column name: {name!r}")
        for index, name in enumerate(clean):
            if not name:
                issue("blank_header", 1, f"Column {index + 1} has no name.")
        index_of = {name: idx for idx, name in enumerate(clean)}
        for required in schema.get("required_columns", []):
            if required not in index_of:
                issue("missing_required_column", 1, f"Required column {required!r} is absent.")
        for key in schema.get("keys", []):
            if key not in index_of:
                issue("missing_key_column", 1, f"Key column {key!r} is absent.")
        for column in (*schema.get("types", {}).keys(), *schema.get("allowed_values", {}).keys()):
            if column not in index_of:
                issue("missing_rule_column", 1, f"Rule references missing column {column!r}.")
        seen_keys: dict[tuple[str, ...], int] = {}
        if headers:
            try:
                for row_number, row in enumerate(reader, start=2):
                    report["row_count"] += 1
                    if len(row) != len(clean):
                        issue("column_count_mismatch", row_number,
                              f"Expected {len(clean)} fields, found {len(row)}.")
                        continue
                    values = {clean[i]: value.strip() for i, value in enumerate(row)}
                    for required in schema.get("required_columns", []):
                        if required in values and not values[required]:
                            issue("blank_required_value", row_number, f"Required column {required!r} is blank.")
                    keys = schema.get("keys", [])
                    if keys and all(key in values for key in keys):
                        key_tuple = tuple(values[key].casefold() for key in keys)
                        if any(not part for part in key_tuple):
                            issue("blank_key", row_number, "One or more key values are blank.")
                        elif key_tuple in seen_keys:
                            issue("duplicate_key", row_number,
                                  f"Duplicate key found; first appearance at row {seen_keys[key_tuple]}.")
                        else:
                            seen_keys[key_tuple] = row_number
                    for column, kind in schema.get("types", {}).items():
                        value = values.get(column, "")
                        if value and not valid_type(value, kind):
                            issue("invalid_type", row_number,
                                  f"Column {column!r} must contain {kind} values.")
                    for column, choices in schema.get("allowed_values", {}).items():
                        value = values.get(column, "")
                        if value and value not in choices:
                            issue("invalid_allowed_value", row_number,
                                  f"Column {column!r} has an unrecognized value.")
            except csv.Error as exc:
                issue("csv_parse_error", max(2, report["row_count"] + 2), f"Malformed CSV: {exc}")
    report["issue_counts"] = dict(sorted(counters.items()))
    report["examples_truncated"] = sum(counters.values()) > len(examples)
    report["issues_total"] = sum(counters.values())
    report["status"] = "PASS" if not counters else "ISSUES"
    return report


def gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    app = tk.Tk()
    app.title(f"Data Import Doctor {VERSION} · Final Vestige Studios")
    app.geometry("870x610")
    frame = ttk.Frame(app, padding=18)
    frame.pack(fill="both", expand=True)
    csv_value = tk.StringVar()
    schema_value = tk.StringVar()
    status = tk.StringVar(value="Choose a CSV file. Optionally supply a reusable JSON import schema.")
    latest = [None]

    ttk.Label(frame, text="Data Import Doctor", font=("Segoe UI", 22, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Diagnose import problems without changing your files.").pack(anchor="w", pady=(0, 18))

    def chooser(label: str, variable: tk.StringVar, types: list[tuple[str, str]]) -> None:
        ttk.Label(frame, text=label).pack(anchor="w")
        line = ttk.Frame(frame)
        line.pack(fill="x", pady=(3, 12))
        ttk.Entry(line, textvariable=variable).pack(side="left", fill="x", expand=True)
        ttk.Button(line, text="Browse…", command=lambda: variable.set(
            filedialog.askopenfilename(filetypes=types) or variable.get())).pack(side="left", padx=(8, 0))

    chooser("CSV data", csv_value, [("CSV files", "*.csv"), ("All files", "*.*")])
    chooser("Import schema (optional)", schema_value, [("JSON schema", "*.json")])
    display = tk.Text(frame, state="disabled", wrap="word", height=18)
    display.pack(fill="both", expand=True, pady=10)

    def show(message: str) -> None:
        display.config(state="normal")
        display.delete("1.0", "end")
        display.insert("1.0", message)
        display.config(state="disabled")

    def check() -> None:
        if not csv_value.get():
            messagebox.showwarning("Choose CSV", "Select a CSV file first.")
            return
        try:
            result = analyze(Path(csv_value.get()), Path(schema_value.get()) if schema_value.get() else None)
            latest[0] = result
            show(json.dumps({
                "status": result["status"], "rows": result["row_count"],
                "columns": result["columns"], "issue_counts": result["issue_counts"],
                "examples": result["examples"], "examples_truncated": result["examples_truncated"]
            }, indent=2, ensure_ascii=False))
            status.set(f"{result['row_count']} data rows · {result['issues_total']} issues")
        except (OSError, ValueError, json.JSONDecodeError, UnicodeError) as exc:
            messagebox.showerror("Analysis failed", str(exc))

    def export() -> None:
        if latest[0] is None:
            messagebox.showinfo("No report", "Analyze a file first.")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON report", "*.json")])
        if filename:
            try:
                Path(filename).write_text(json.dumps(latest[0], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                status.set("Report saved to " + filename)
            except OSError as exc:
                messagebox.showerror("Save failed", str(exc))

    row = ttk.Frame(frame)
    row.pack(fill="x")
    ttk.Button(row, text="Analyze CSV", command=check).pack(side="left")
    ttk.Button(row, text="Export JSON report", command=export).pack(side="left", padx=10)
    ttk.Label(frame, textvariable=status).pack(anchor="w", pady=(10, 0))
    app.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline CSV import preflight")
    parser.add_argument("csv", nargs="?")
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.csv:
        gui()
        return 0
    try:
        report = analyze(Path(args.csv), args.schema)
        result = json.dumps(report, ensure_ascii=False, indent=2)
        if args.report:
            args.report.write_text(result + "\n", encoding="utf-8")
        print(result)
        return 1 if report["issues_total"] else 0
    except (OSError, ValueError, json.JSONDecodeError, UnicodeError) as exc:
        print("Analysis failed:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
