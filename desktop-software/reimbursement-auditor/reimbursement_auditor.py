"""Reimbursement Auditor — offline reimbursement evidence review.

Compares user-provided claims CSV to a manually verified support index CSV and
attachment folder. Does NOT read or authenticate the contents of scanned PDFs.
Outputs review findings, not reimbursement eligibility or compliance decisions.
Python 3.11+.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath

VERSION = "0.1.0"
ALIASES = {
    "vendor": {"vendor", "vendor name", "supplier", "payee"},
    "invoice": {"invoice", "invoice number", "invoice #", "invoice no"},
    "amount": {"amount", "claimed amount", "invoice amount", "total", "requested amount"},
    "file": {"file", "attachment", "supporting file", "filename", "evidence file"},
}


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").casefold())


def amount_value(raw: str) -> Decimal:
    value = (raw or "").strip()
    negative = value.startswith("(") and value.endswith(")")
    value = value.strip("()").replace(",", "").replace("$", "").strip()
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Amount is not a valid decimal.") from exc
    if not result.is_finite() or result.as_tuple().exponent < -2:
        raise ValueError("Amount must be finite with at most two decimal places.")
    return -result if negative else result


def csv_items(source: Path, require_file: bool) -> tuple[list[dict], list[dict]]:
    records, errors = [], []
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        sample = stream.read(8192)
        stream.seek(0)
        try:
            delim = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            delim = ","
        reader = csv.DictReader(stream, delimiter=delim, restkey="__extra__", restval="", strict=True)
        if not reader.fieldnames:
            raise ValueError(f"{source.name} is empty.")
        columns = {}
        for name in reader.fieldnames:
            value = name.strip().casefold()
            for field, aliases in ALIASES.items():
                if field not in columns and value in aliases:
                    columns[field] = name
        required = {"vendor", "invoice", "amount"} | ({"file"} if require_file else set())
        if required - columns.keys():
            raise ValueError(f"{source.name} is missing columns: " + ", ".join(sorted(required - columns.keys())))
        for number, row in enumerate(reader, 2):
            try:
                if "__extra__" in row:
                    raise ValueError("Extra fields in CSV row.")
                vendor = (row.get(columns["vendor"]) or "").strip()
                invoice = (row.get(columns["invoice"]) or "").strip()
                if not vendor or not invoice:
                    raise ValueError("Vendor and invoice reference are required.")
                money = amount_value(row.get(columns["amount"]) or "")
                name = (row.get(columns.get("file", ""), "") or "").strip() if require_file else ""
                if require_file and not name:
                    raise ValueError("Supporting filename is required.")
                records.append({
                    "row": number, "vendor": vendor, "invoice": invoice,
                    "key": (normalize(vendor), normalize(invoice)),
                    "amount": money, "file": name,
                })
            except (ValueError, TypeError) as exc:
                errors.append({"row": number, "message": str(exc)})
    return records, errors


def attached_path(root: Path, entry: str) -> Path:
    if not isinstance(entry, str) or not entry or "\\" in entry:
        raise ValueError("Attachments must use safe relative forward-slash paths.")
    normalized = PurePosixPath(entry)
    if normalized.is_absolute() or ".." in normalized.parts or ":" in normalized.parts[0]:
        raise ValueError("Attachment filename escapes packet folder.")
    resolved = root.joinpath(*normalized.parts)
    if not resolved.resolve().is_relative_to(root.resolve()):
        raise ValueError("Attachment points outside packet folder.")
    return resolved


def audit(claims_csv: Path, support_csv: Path, attachment_folder: Path) -> dict:
    folder = attachment_folder.resolve(strict=True)
    if not folder.is_dir():
        raise ValueError("Attachments must be a folder.")
    claims, claim_errors = csv_items(claims_csv, False)
    supports, support_errors = csv_items(support_csv, True)
    by_claim: dict[tuple[str, str], list[dict]] = defaultdict(list)
    by_support: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in claims:
        by_claim[row["key"]].append(row)
    for row in supports:
        by_support[row["key"]].append(row)
    findings = []

    def report(code: str, level: str, rows: list[int], detail: str) -> None:
        findings.append({"code": code, "priority": level, "claim_rows": sorted(rows), "reason": detail})

    for key, grouped in by_claim.items():
        if len(grouped) > 1:
            report("DUPLICATE_CLAIM_REFERENCE", "HIGH", [x["row"] for x in grouped],
                   "Vendor and invoice reference appear on multiple claim rows.")
        if key not in by_support:
            report("SUPPORT_INDEX_MISSING", "HIGH", [x["row"] for x in grouped],
                   "No corresponding invoice reference found in the support index.")
        else:
            claimed = sum((x["amount"] for x in grouped), Decimal("0"))
            supported = sum((x["amount"] for x in by_support[key]), Decimal("0"))
            if claimed != supported:
                report("AMOUNT_MISMATCH", "HIGH", [x["row"] for x in grouped],
                       f"Claimed {claimed} differs from user-entered support index total {supported}.")
    referenced_files: dict[str, list[int]] = defaultdict(list)
    for item in supports:
        try:
            path = attached_path(folder, item["file"])
            referenced_files[item["file"].casefold()].append(item["row"])
            if not path.exists():
                report("ATTACHMENT_MISSING", "HIGH", [], "Support row " + str(item["row"]) +
                       ": referenced attachment is missing.")
            elif not path.is_file() or path.is_symlink():
                report("ATTACHMENT_NOT_REGULAR_FILE", "HIGH", [],
                       "Support row " + str(item["row"]) + ": attachment is not a regular file.")
            elif path.stat().st_size == 0:
                report("ATTACHMENT_EMPTY", "MEDIUM", [],
                       "Support row " + str(item["row"]) + ": attachment is empty.")
        except (ValueError, OSError) as exc:
            report("UNSAFE_OR_UNREADABLE_ATTACHMENT", "HIGH", [],
                   "Support row " + str(item["row"]) + ": " + str(exc))
    for path, rows in referenced_files.items():
        if len(rows) > 1:
            report("REUSED_ATTACHMENT_REFERENCE", "MEDIUM", [],
                   "The same attachment filename is referenced on support rows " +
                   ", ".join(str(x) for x in rows) + ".")

    for item in supports:
        if item["key"] not in by_claim:
            report("UNLINKED_SUPPORT_ROW", "LOW", [],
                   "Support index row " + str(item["row"]) + " has no corresponding claim.")
    for item in claim_errors:
        report("INVALID_CLAIM_ROW", "HIGH", [item["row"]], "Claim row excluded: " + item["message"])
    for item in support_errors:
        report("INVALID_SUPPORT_ROW", "HIGH", [], "Support index row " + str(item["row"]) +
               " excluded: " + item["message"])
    level = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    findings.sort(key=lambda item: (level[item["priority"]], item["claim_rows"]))
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for item in claims:
        totals[item["vendor"]] += item["amount"]
    return {
        "tool": "Final Vestige Reimbursement Auditor", "version": VERSION,
        "claim_file": claims_csv.name, "support_file": support_csv.name,
        "claims": len(claims), "support_rows": len(supports),
        "claim_rows_excluded": len(claim_errors), "support_rows_excluded": len(support_errors),
        "claim_totals_by_vendor": {k: str(v) for k, v in sorted(totals.items())},
        "findings": findings, "finding_count": len(findings),
        "status": "REVIEW" if findings else "NO_FILE_OR_INDEX_EXCEPTIONS",
        "disclaimer": "This audits file presence and user-provided index amounts only. "
                      "It does not inspect PDFs, validate receipts, certify eligibility or establish compliance.",
    }


def html_report(data: dict) -> str:
    body = []
    for item in data["findings"]:
        body.append("<tr><td>" + html.escape(item["priority"]) + "</td><td>" +
                    html.escape(item["code"]) + "</td><td>" +
                    html.escape(", ".join(str(x) for x in item["claim_rows"])) + "</td><td>" +
                    html.escape(item["reason"]) + "</td></tr>")
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><title>Reimbursement audit</title>"
            "<style>body{font:16px system-ui;max-width:1100px;margin:3rem auto;padding:1rem}"
            "th,td{border:1px solid #ccc;padding:.75rem;text-align:left}table{border-collapse:collapse;width:100%}</style>"
            "<h1>Reimbursement Auditor</h1><p>" + html.escape(data["disclaimer"]) +
            "</p><p>Claim rows reviewed: " + str(data["claims"]) + " — findings: " +
            str(data["finding_count"]) + "</p><table><thead><tr><th>Priority</th><th>Check</th>"
            "<th>Claim rows</th><th>Explanation</th></tr></thead><tbody>" + "".join(body) +
            "</tbody></table></html>")


def gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    app = tk.Tk()
    app.title(f"Reimbursement Auditor {VERSION} · Final Vestige Studios")
    app.geometry("930x630")
    frame = ttk.Frame(app, padding=18)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Reimbursement Auditor", font=("Segoe UI", 22, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Compare claims, a user-created evidence index, and the actual files—entirely offline.").pack(anchor="w", pady=(0, 18))
    claims, support, folder = tk.StringVar(), tk.StringVar(), tk.StringVar()
    latest = [None]

    for label, variable, directory in (("Claims CSV", claims, False),
                                        ("Supporting evidence index CSV", support, False),
                                        ("Attachment folder", folder, True)):
        ttk.Label(frame, text=label).pack(anchor="w")
        line = ttk.Frame(frame)
        line.pack(fill="x", pady=(3, 11))
        ttk.Entry(line, textvariable=variable).pack(side="left", fill="x", expand=True)
        def choose(v=variable, is_dir=directory):
            new = filedialog.askdirectory() if is_dir else filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv")])
            if new:
                v.set(new)
        ttk.Button(line, text="Browse…", command=choose).pack(side="left", padx=8)
    output = tk.Text(frame, state="disabled", wrap="word")
    output.pack(fill="both", expand=True, pady=10)
    status = tk.StringVar(value="Use your own verified support index; the tool does not read PDF contents.")

    def run() -> None:
        try:
            latest[0] = audit(Path(claims.get()), Path(support.get()), Path(folder.get()))
            output.config(state="normal")
            output.delete("1.0", "end")
            output.insert("1.0", json.dumps(latest[0], indent=2))
            output.config(state="disabled")
            status.set(f"{latest[0]['claims']} claims · {latest[0]['finding_count']} exceptions")
        except (OSError, ValueError, UnicodeError, csv.Error) as exc:
            messagebox.showerror("Could not audit", str(exc))

    def export() -> None:
        if latest[0] is None:
            return
        filename = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML reports", "*.html")])
        if filename:
            try:
                Path(filename).write_text(html_report(latest[0]), encoding="utf-8")
                status.set("Review report saved: " + filename)
            except OSError as exc:
                messagebox.showerror("Save failed", str(exc))

    controls = ttk.Frame(frame)
    controls.pack(fill="x", before=output)
    ttk.Button(controls, text="Audit packet", command=run).pack(side="left")
    ttk.Button(controls, text="Save review report", command=export).pack(side="left", padx=10)
    ttk.Label(frame, textvariable=status).pack(anchor="w")
    app.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline reimbursement packet evidence audit.")
    parser.add_argument("claims", nargs="?")
    parser.add_argument("support", nargs="?")
    parser.add_argument("folder", nargs="?")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not any((args.claims, args.support, args.folder)):
        gui()
        return 0
    if not all((args.claims, args.support, args.folder)):
        parser.error("Provide claims CSV, support index CSV and attachments folder.")
    try:
        result = audit(Path(args.claims), Path(args.support), Path(args.folder))
        if args.report:
            if args.report.suffix.lower() == ".html":
                args.report.write_text(html_report(result), encoding="utf-8")
            else:
                args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 1 if result["finding_count"] else 0
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        print("Audit failed:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
