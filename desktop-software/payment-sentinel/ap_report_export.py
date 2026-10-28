"""Offline Payment Sentinel report outputs with source-preserving writes."""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Callable

REPORT_COLUMNS = (
    "source_sha256", "review_status", "records_reviewed", "rows_excluded",
    "severity", "rule", "source_csv_lines", "reason", "flag_status",
)


def excel_safe(value: object) -> str:
    """Neutralize spreadsheet formulas in free-text fields on CSV export."""
    text = str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")):
        return "'" + text
    return text


def render_csv(report: dict) -> str:
    """A filterable report; even zero findings produces a summary row."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\r\n")
    writer.writerow(REPORT_COLUMNS)
    base = [report.get("source_sha256", ""), report.get("status", "UNKNOWN"),
            report.get("records_reviewed", 0), report.get("rows_excluded", 0)]
    flags = report.get("flags", [])
    if not flags:
        writer.writerow([excel_safe(x) for x in (*base, "", "", "", "No exception flags", "")])
    for flag in flags:
        row = [*base, flag["severity"], flag["rule"],
               ";".join(str(x) for x in flag["rows"]), flag["reason"],
               flag.get("status", "REVIEW")]
        writer.writerow([excel_safe(cell) for cell in row])
    return output.getvalue()


def save_report(destination: Path, source: Path, report: dict,
                html_renderer: Callable[[dict], str]) -> Path:
    """Only create new outputs; never overwrite an existing file or source.

    Refuses unexpected extensions and removes incomplete output on write errors.
    """
    destination = Path(destination)
    source = Path(source)
    extension = destination.suffix.casefold()
    if extension not in (".html", ".csv", ".json"):
        raise ValueError("Choose a .html, .csv or .json report filename.")
    if destination.resolve() == source.resolve():
        raise ValueError("Report destination cannot be the source CSV.")
    if extension == ".html":
        body = html_renderer(report)
    elif extension == ".csv":
        body = render_csv(report)
    else:
        body = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    created = False
    try:
        with destination.open("x", encoding="utf-8", newline="") as output:
            created = True
            output.write(body)
    except Exception:
        if created:
            destination.unlink(missing_ok=True)
        raise
    return destination
