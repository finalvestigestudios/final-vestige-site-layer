"""Payment Sentinel — explainable, offline AP export exception review.

No bank connections, external services or changes to source files. Flags are
review prompts, never findings of fraud. Python 3.11+.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from ap_input_guard import MAX_PAYMENTS, normalize_search_key, record_start_line, resolve_headers, source_fingerprint
from ap_report_export import save_report

VERSION = "0.1.0"
ALIASES = {
    "vendor": {"vendor", "vendor name", "supplier", "supplier name", "payee"},
    "invoice": {"invoice", "invoice number", "invoice #", "invoice no", "bill number"},
    "amount": {"amount", "payment amount", "paid amount", "total", "gross amount"},
    "date": {"payment date", "date paid", "paid date", "date", "transaction date"},
    "account": {"vendor account", "bank account", "account number", "bank account number"},
}


def normalize(text: str) -> str:
    return normalize_search_key(text)


def parse_amount(raw: str) -> Decimal:
    value = str(raw).strip()
    negative = value.startswith("(") and value.endswith(")")
    value = value.strip("()").replace(",", "").replace("$", "").strip()
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Amount must be numeric.") from exc
    if not amount.is_finite() or amount.as_tuple().exponent < -2:
        raise ValueError("Amount must be finite and have at most two decimal places.")
    return -amount if negative else amount


def parse_date(raw: str) -> date:
    for pattern in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(raw.strip(), pattern).date()
        except ValueError:
            continue
    raise ValueError("Date must be YYYY-MM-DD or MM/DD/YYYY.")


def load_payments(path: Path) -> tuple[list[dict], list[dict]]:
    records = []
    problems = []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        sample = stream.read(8192)
        stream.seek(0)
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = ","
        reader = csv.DictReader(stream, delimiter=delimiter, restkey="__extra__", restval="", strict=True)
        if reader.fieldnames is None:
            raise ValueError("Empty CSV file.")
        canonical = resolve_headers(reader.fieldnames, ALIASES,
                                    {"vendor", "invoice", "amount", "date"})
        for index, row in enumerate(reader, 1):
            if index > MAX_PAYMENTS:
                raise ValueError("CSV exceeds the 200,000-payment review limit.")
            # Correct when CSV records contain quoted newlines or blank lines.
            csv_line = record_start_line(reader.line_num, row)
            try:
                if "__extra__" in row:
                    raise ValueError("Row has more columns than the header.")
                vendor = (row[canonical["vendor"]] or "").strip()
                invoice = (row[canonical["invoice"]] or "").strip()
                if not vendor or not invoice:
                    raise ValueError("Vendor and invoice must be present.")
                vendor_key, invoice_key = normalize(vendor), normalize(invoice)
                if not vendor_key or not invoice_key:
                    raise ValueError("Vendor and invoice need searchable letters or digits.")
                value = parse_amount(row[canonical["amount"]] or "")
                paid = parse_date(row[canonical["date"]] or "")
                account = (row.get(canonical.get("account", ""), "") or "").strip()
                records.append({
                    "row": csv_line, "vendor": vendor, "vendor_key": vendor_key,
                    "invoice": invoice, "invoice_key": invoice_key,
                    "amount": value, "date": paid,
                    "account_key": normalize(account),
                })
            except (ValueError, TypeError, KeyError) as exc:
                problems.append({"row": csv_line, "code": "INVALID_INPUT", "message": str(exc)})
    return records, problems


def review(path: Path) -> dict:
    original = source_fingerprint(path)
    records, problems = load_payments(path)
    if source_fingerprint(path) != original:
        raise ValueError("CSV changed while processing; discard this review and retry.")
    flags = []
    seen_invoice: dict[tuple[str, str], dict] = {}
    by_vendor: dict[str, list[dict]] = defaultdict(list)
    seen_same_amount: dict[tuple[str, Decimal], list[dict]] = defaultdict(list)

    def flag(rule: str, severity: str, rows: list[int], description: str) -> None:
        flags.append({"rule": rule, "severity": severity, "rows": sorted(rows),
                      "reason": description, "status": "REVIEW"})

    for item in records:
        by_vendor[item["vendor_key"]].append(item)
        invoice_key = (item["vendor_key"], item["invoice_key"])
        previous = seen_invoice.get(invoice_key)
        if previous:
            same_amount = previous["amount"] == item["amount"]
            flag("REPEATED_INVOICE", "HIGH" if same_amount else "MEDIUM",
                 [previous["row"], item["row"]],
                 "Same vendor and normalized invoice reference appears more than once" +
                 (" for the same amount." if same_amount else " with different amounts."))
        else:
            seen_invoice[invoice_key] = item
        amount_key = (item["vendor_key"], item["amount"])
        for prior in seen_same_amount[amount_key]:
            if prior["invoice_key"] != item["invoice_key"] and abs((item["date"] - prior["date"]).days) <= 3:
                flag("SAME_AMOUNT_NEAR_DATE", "MEDIUM", [prior["row"], item["row"]],
                     "Same vendor and amount paid within three days under different invoice references.")
                break
        seen_same_amount[amount_key].append(item)

    for vendor, items in by_vendor.items():
        accounts = {item["account_key"] for item in items if item["account_key"]}
        if len(accounts) > 1:
            flag("MULTIPLE_VENDOR_ACCOUNTS", "MEDIUM", [item["row"] for item in items],
                 "More than one bank account identifier appears for this vendor; verify approved changes. "
                 "Account numbers are not exported in the report.")
        positives = [item["amount"] for item in items if item["amount"] > 0]
        if len(positives) >= 6:
            median = statistics.median(positives)
            for item in items:
                if item["amount"] > max(Decimal("250"), median * 3):
                    flag("VENDOR_AMOUNT_OUTLIER", "LOW", [item["row"]],
                         "Payment amount exceeds three times this vendor's median positive payment.")

    for error in problems:
        flag("INVALID_INPUT", "HIGH", [error["row"]],
             "CSV row was excluded from review: " + error["message"])
    flags.sort(key=lambda x: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["severity"]], x["rows"]))
    summary = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for item in flags:
        summary[item["severity"]] += 1
    return {
        "tool": "Final Vestige Payment Sentinel", "version": VERSION,
        "file": path.name, "source_sha256": original["sha256"],
        "source_bytes": original["bytes"], "records_reviewed": len(records),
        "rows_excluded": len(problems), "flags_by_severity": summary,
        "flags": flags,
        "status": "INCOMPLETE" if not records else ("REVIEW" if flags else "NO_FLAGS"),
        "disclaimer": "Exceptions are leads for human review, not proof of error or fraud.",
    }


def report_html(report: dict) -> str:
    rows = []
    for item in report["flags"]:
        rows.append("<tr><td>" + html.escape(item["severity"]) + "</td><td>" +
                    html.escape(item["rule"]) + "</td><td>" +
                    ", ".join(str(x) for x in item["rows"]) + "</td><td>" +
                    html.escape(item["reason"]) + "</td></tr>")
    return ("<!doctype html><html lang='en'><meta charset='utf-8'>"
            "<title>Payment Sentinel Review</title><style>body{font:16px system-ui;"
            "max-width:1000px;margin:3rem auto;padding:1rem}table{border-collapse:collapse;width:100%}"
            "th,td{border:1px solid #ccc;padding:.75rem;text-align:left}</style>"
            "<h1>Payment Sentinel</h1><p>Review state: " +
            html.escape(report.get("status", "REVIEW")) +
            "; rows reviewed: " + str(report["records_reviewed"]) +
            "; skipped: " + str(report["rows_excluded"]) +
            "</p><p>Input SHA-256: <code>" +
            html.escape(report.get("source_sha256", "not recorded")) + "</code></p><p>" +
            html.escape(report["disclaimer"]) + "</p><table><thead><tr><th>Priority</th>"
            "<th>Check</th><th>CSV rows</th><th>Reason</th></tr></thead><tbody>" +
            "".join(rows) + "</tbody></table></html>")


def gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    app = tk.Tk()
    app.title(f"Payment Sentinel {VERSION} · Final Vestige Studios")
    app.geometry("880x570")
    frame = ttk.Frame(app, padding=20)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Payment Sentinel", font=("Segoe UI", 22, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Review payables exports locally. Findings are prompts for verification, not fraud claims.").pack(anchor="w", pady=(0, 18))
    path = tk.StringVar()
    row = ttk.Frame(frame)
    row.pack(fill="x")
    ttk.Entry(row, textvariable=path).pack(side="left", fill="x", expand=True)
    ttk.Button(row, text="Choose CSV", command=lambda: path.set(
        filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")]) or path.get())).pack(side="left", padx=8)
    output = tk.Text(frame, state="disabled", wrap="word")
    output.pack(fill="both", expand=True, pady=15)
    latest = [None]
    reviewed_path = [None]
    status = tk.StringVar(value="Select an AP payment CSV to begin.")
    ttk.Label(frame, textvariable=status).pack(anchor="w")

    def do_review() -> None:
        # Failed imports must not leave an earlier report eligible for export.
        latest[0], reviewed_path[0] = None, None
        output.config(state="normal")
        output.delete("1.0", "end")
        output.config(state="disabled")
        status.set("Checking payment data...")
        try:
            source = Path(path.get()).resolve(strict=True)
            result = review(source)
            latest[0], reviewed_path[0] = result, source
            output.config(state="normal")
            output.insert("1.0", json.dumps(result, indent=2, ensure_ascii=False))
            output.config(state="disabled")
            status.set(f"{result['records_reviewed']} payments reviewed · "
                       f"{len(result['flags'])} flags · {result['status']}")
        except (OSError, ValueError, csv.Error, UnicodeError) as exc:
            status.set("Review failed. No report available for export.")
            messagebox.showerror("Review failed", str(exc))

    def export() -> None:
        if latest[0] is None or reviewed_path[0] is None:
            return
        try:
            if Path(path.get()).resolve() != reviewed_path[0]:
                raise ValueError("File selection changed; rerun the review before exporting.")
            current = source_fingerprint(reviewed_path[0])
            if (current["sha256"], current["bytes"]) != (
                    latest[0]["source_sha256"], latest[0]["source_bytes"]):
                raise ValueError("Source CSV changed since the review; rerun before exporting.")
        except (OSError, ValueError) as exc:
            latest[0], reviewed_path[0] = None, None
            status.set("Source changed or unavailable. Rerun the review.")
            messagebox.showerror("Export blocked", str(exc))
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML review report", "*.html"),
                       ("CSV review spreadsheet", "*.csv"),
                       ("JSON review data", "*.json")])
        if filename:
            try:
                save_report(Path(filename), reviewed_path[0], latest[0], report_html)
                status.set("Report saved: " + filename)
            except (OSError, ValueError) as exc:
                messagebox.showerror("Save failed", str(exc))

    controls = ttk.Frame(frame)
    controls.pack(fill="x", before=output)
    ttk.Button(controls, text="Run review", command=do_review).pack(side="left")
    ttk.Button(controls, text="Save review report", command=export).pack(side="left", padx=10)
    app.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline AP payments exception review")
    parser.add_argument("csv", nargs="?")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.csv:
        gui()
        return 0
    try:
        result = review(Path(args.csv))
        if args.report:
            now = source_fingerprint(Path(args.csv))
            if (now["sha256"], now["bytes"]) != (
                    result["source_sha256"], result["source_bytes"]):
                raise ValueError("Source CSV changed since review; report not saved.")
            save_report(args.report, Path(args.csv), result, report_html)
        print(json.dumps(result, indent=2))
        return 2 if result["status"] == "INCOMPLETE" else (1 if result["flags"] else 0)
    except (OSError, ValueError, csv.Error, UnicodeError) as exc:
        print("Review failed:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
