"""Payment Sentinel — explainable, offline AP export exception review.

No bank connections, external services or changes to source files. Flags are
review prompts, never findings of fraud. Python 3.11+.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSION = "0.1.0"
ALIASES = {
    "vendor": {"vendor", "vendor name", "supplier", "supplier name", "payee"},
    "invoice": {"invoice", "invoice number", "invoice #", "invoice no", "bill number"},
    "amount": {"amount", "payment amount", "paid amount", "total", "gross amount"},
    "date": {"payment date", "date paid", "paid date", "date", "transaction date"},
    "account": {"vendor account", "bank account", "account number", "bank account number"},
}


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "",text.casefold())


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
        canonical = {}
        for header in reader.fieldnames:
            lowered = header.strip().casefold()
            for target, choices in ALIASES.items():
                if lowered in choices and target not in canonical:
                    canonical[target] = header
        missing = {"vendor", "invoice", "amount", "date"} - canonical.keys()
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
        for idx, row in enumerate(reader, 2):
            try:
                if "__extra__" in row:
                    raise ValueError("Row has more columns than the header.")
                vendor = (row[canonical["vendor"]] or "").strip()
                invoice = (row[canonical["invoice"]] or "").strip()
                if not vendor or not invoice:
                    raise ValueError("Vendor and invoice must be present.")
                value = parse_amount(row[canonical["amount"]] or "")
                paid = parse_date(row[canonical["date"]] or "")
                account = (row.get(canonical.get("account", ""), "") or "").strip()
                records.append({
                    "row": idx, "vendor": vendor, "vendor_key": normalize(vendor),
                    "invoice": invoice, "invoice_key": normalize(invoice),
                    "amount": value, "date": paid,
                    "account_key": normalize(account),
                })
            except (ValueError, TypeError, KeyError) as exc:
                problems.append({"row": idx, "code": "INVALID_INPUT", "message": str(exc)})
    return records, problems


def review(path: Path) -> dict:
    records, problems = load_payments(path)
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
        "file": path.name, "records_reviewed": len(records),
        "rows_excluded": len(problems), "flags_by_severity": summary,
        "flags": flags, "status": "REVIEW" if flags else "NO_FLAGS",
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
            "<h1>Payment Sentinel</h1><p>Rows reviewed: " + str(report["records_reviewed"]) +
            "; skipped: " + str(report["rows_excluded"]) + "</p><p>" +
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
    status = tk.StringVar(value="Select an AP payment CSV to begin.")
    ttk.Label(frame, textvariable=status).pack(anchor="w")

    def do_review() -> None:
        try:
            latest[0] = review(Path(path.get()))
            output.config(state="normal")
            output.delete("1.0", "end")
            output.insert("1.0", json.dumps(latest[0], indent=2, ensure_ascii=False))
            output.config(state="disabled")
            status.set(f"{latest[0]['records_reviewed']} payments reviewed · "
                       f"{len(latest[0]['flags'])} review flags")
        except (OSError, ValueError, csv.Error, UnicodeError) as exc:
            messagebox.showerror("Review failed", str(exc))

    def export() -> None:
        if latest[0] is None:
            return
        filename = filedialog.asksaveasfilename(defaultextension=".html",
                                                filetypes=[("HTML review report", "*.html")])
        if filename:
            Path(filename).write_text(report_html(latest[0]), encoding="utf-8")
            status.set("Report saved: " + filename)

    controls = ttk.Frame(frame)
    controls.pack(fill="x", before=output)
    ttk.Button(controls, text="Run review", command=do_review).pack(side="left")
    ttk.Button(controls, text="Save HTML review", command=export).pack(side="left", padx=10)
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
            if args.report.suffix.lower() == ".html":
                args.report.write_text(report_html(result), encoding="utf-8")
            else:
                args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 1 if result["flags"] else 0
    except (OSError, ValueError, csv.Error, UnicodeError) as exc:
        print("Review failed:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
