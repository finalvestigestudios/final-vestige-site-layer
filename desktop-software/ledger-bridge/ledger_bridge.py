"""Ledger Bridge — offline two-file transaction reconciliation.

Matches exact reference+amount before attempting unique date/amount matches.
Never modifies books and never silently matches ambiguous transactions.
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
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSION = "0.1.0"
FIELDS = {
    "date": {"date", "transaction date", "posted", "posting date", "payment date"},
    "amount": {"amount", "net amount", "transaction amount", "total"},
    "debit": {"debit", "debits", "withdrawal"},
    "credit": {"credit", "credits", "deposit"},
    "reference": {"reference", "ref", "reference number", "transaction id", "id", "check number"},
    "description": {"description", "memo", "details", "payee", "narrative"},
    "currency": {"currency", "ccy", "currency code"},
}


def parse_money(raw: str, allow_blank: bool = False) -> Decimal:
    raw = (raw or "").strip()
    is_negative = raw.startswith("(") and raw.endswith(")")
    raw = raw.strip("()").replace(",", "").replace("$", "").strip()
    if not raw:
        if allow_blank:
            return Decimal("0")
        raise ValueError("Amount cannot be blank; use 0 explicitly.")
    try:
        result = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError("Invalid monetary value.") from exc
    if not result.is_finite() or result.as_tuple().exponent < -2:
        raise ValueError("Amounts must be finite with no more than two decimal places.")
    return -result if is_negative else result


def parse_day(raw: str) -> date:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime((raw or "").strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError("Date must be YYYY-MM-DD or MM/DD/YYYY.")


def normalized_reference(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").casefold())


def read_ledger(source: Path, flip_sign: bool = False) -> tuple[list[dict], list[dict]]:
    records = []
    errors = []
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        sample = stream.read(8192)
        stream.seek(0)
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = ","
        reader = csv.DictReader(stream, delimiter=delimiter, restkey="__extra__", restval="", strict=True)
        if not reader.fieldnames:
            raise ValueError(f"{source.name}: empty CSV.")
        index = {}
        for name in reader.fieldnames:
            clean = name.strip().casefold()
            for target, names in FIELDS.items():
                if target not in index and clean in names:
                    index[target] = name
        if "date" not in index or ("amount" not in index and not
                                   ("debit" in index and "credit" in index)):
            raise ValueError(f"{source.name}: require date + amount, or date + debit and credit columns.")
        for row_number, row in enumerate(reader, 2):
            try:
                if "__extra__" in row:
                    raise ValueError("Extra CSV fields.")
                day = parse_day(row.get(index["date"], ""))
                if "amount" in index:
                    amount = parse_money(row.get(index["amount"], ""))
                else:
                    credit_raw = row.get(index["credit"], "") or ""
                    debit_raw = row.get(index["debit"], "") or ""
                    if not credit_raw.strip() and not debit_raw.strip():
                        raise ValueError("Both debit and credit are blank.")
                    amount = (parse_money(credit_raw, allow_blank=True) -
                              parse_money(debit_raw, allow_blank=True))
                amount = -amount if flip_sign else amount
                ccy = (row.get(index.get("currency", ""), "USD") or "USD").strip().upper()
                if not re.fullmatch(r"[A-Z]{3}", ccy):
                    raise ValueError("Currency must be a three-letter ISO code.")
                ref = (row.get(index.get("reference", ""), "") or "").strip()
                records.append({
                    "row": row_number, "date": day, "amount": amount,
                    "reference": ref, "normalized_reference": normalized_reference(ref),
                    "description": (row.get(index.get("description", ""), "") or "").strip(),
                    "currency": ccy,
                })
            except (ValueError, KeyError, TypeError) as exc:
                errors.append({"row": row_number, "message": str(exc)})
    return records, errors


def reconcile(left: Path, right: Path, date_tolerance: int = 3,
              flip_right_sign: bool = False) -> dict:
    if not isinstance(date_tolerance, int) or not 0 <= date_tolerance <= 31:
        raise ValueError("Date tolerance must be an integer from 0 to 31 days.")
    lhs, errors_left = read_ledger(left)
    rhs, errors_right = read_ledger(right, flip_sign=flip_right_sign)
    used_left: set[int] = set()
    used_right: set[int] = set()
    matches: list[dict] = []

    def match(a: dict, b: dict, reason: str) -> None:
        used_left.add(a["row"])
        used_right.add(b["row"])
        matches.append({
            "left_row": a["row"], "right_row": b["row"],
            "basis": reason, "amount": str(a["amount"]),
            "currency": a["currency"], "date_difference_days": abs((a["date"] - b["date"]).days),
        })

    # Multiplicity matters: FIFO-pairing duplicate reference/amount keys would
    # invent a pairing without evidence. Quarantine those groups for review.
    exact_left: dict[tuple[str, str, Decimal], list[dict]] = defaultdict(list)
    exact_right: dict[tuple[str, str, Decimal], list[dict]] = defaultdict(list)
    for a in lhs:
        if a["normalized_reference"]:
            exact_left[(a["currency"], a["normalized_reference"], a["amount"])].append(a)
    for b in rhs:
        if b["normalized_reference"]:
            exact_right[(b["currency"], b["normalized_reference"], b["amount"])].append(b)
    blocked_left: set[int] = set()
    blocked_right: set[int] = set()
    ambiguous_reference_groups: list[dict] = []
    for key, left_group in exact_left.items():
        right_group = exact_right.get(key, [])
        if not right_group:
            continue
        if len(left_group) == len(right_group) == 1:
            match(left_group[0], right_group[0], "EXACT_REFERENCE_AND_AMOUNT")
        else:
            blocked_left.update(x["row"] for x in left_group)
            blocked_right.update(x["row"] for x in right_group)
            ambiguous_reference_groups.append({
                "currency": key[0], "reference": key[1], "amount": str(key[2]),
                "left_rows": sorted(x["row"] for x in left_group),
                "right_rows": sorted(x["row"] for x in right_group),
                "reason": "Duplicate reference/amount identity; pairing requires human review.",
            })

    remaining_left = [a for a in lhs if a["row"] not in used_left and a["row"] not in blocked_left]
    remaining_right = [b for b in rhs if b["row"] not in used_right and b["row"] not in blocked_right]
    candidates_left: dict[int, list[int]] = defaultdict(list)
    candidates_right: dict[int, list[int]] = defaultdict(list)
    indexed_right: dict[tuple[str, Decimal], list[dict]] = defaultdict(list)
    by_right_row = {b["row"]: b for b in remaining_right}
    for b in remaining_right:
        indexed_right[(b["currency"], b["amount"])].append(b)
    for a in remaining_left:
        for b in indexed_right[(a["currency"], a["amount"])]:
            if abs((a["date"] - b["date"]).days) <= date_tolerance:
                candidates_left[a["row"]].append(b["row"])
                candidates_right[b["row"]].append(a["row"])
    for a in remaining_left:
        options = candidates_left[a["row"]]
        if len(options) == 1 and len(candidates_right[options[0]]) == 1:
            match(a, by_right_row[options[0]], "UNIQUE_AMOUNT_AND_DATE")

    ambiguous_left = sorted(blocked_left | {
        row for row, options in candidates_left.items()
        if len(options) > 1 or (len(options) == 1 and len(candidates_right[options[0]]) > 1)
    })
    ambiguous_right = sorted(blocked_right | {
        row for row, options in candidates_right.items()
        if len(options) > 1 or (len(options) == 1 and len(candidates_left[options[0]]) > 1)
    })
    unmatched_left = [
        {"row": a["row"], "date": a["date"].isoformat(), "amount": str(a["amount"]),
         "currency": a["currency"], "reference": a["reference"]}
        for a in lhs if a["row"] not in used_left
    ]
    unmatched_right = [
        {"row": b["row"], "date": b["date"].isoformat(), "amount": str(b["amount"]),
         "currency": b["currency"], "reference": b["reference"]}
        for b in rhs if b["row"] not in used_right
    ]
    totals = {}
    for side, records in (("left", lhs), ("right", rhs)):
        values: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
        for item in records:
            values[item["currency"]] += item["amount"]
        totals[side] = {key: str(value) for key, value in sorted(values.items())}
    suggested = [m for m in matches if m["basis"] == "UNIQUE_AMOUNT_AND_DATE"]
    distant_exact = [m for m in matches if (
        m["basis"] == "EXACT_REFERENCE_AND_AMOUNT" and
        m["date_difference_days"] > date_tolerance
    )]
    warnings = []
    if suggested:
        warnings.append({
            "code": "AMOUNT_DATE_SUGGESTIONS", "count": len(suggested),
            "message": "Amount/date matches are suggestions requiring verification.",
        })
    if distant_exact:
        warnings.append({
            "code": "EXACT_REFERENCE_DATE_GAP", "count": len(distant_exact),
            "left_rows": sorted(m["left_row"] for m in distant_exact),
            "message": "Exact-reference entries have dates beyond the tolerance window.",
        })
    if not lhs or not rhs:
        warnings.append({
            "code": "EMPTY_LEDGER", "message": "At least one input has no valid transactions.",
        })
    report = {
        "tool": "Final Vestige Ledger Bridge", "version": VERSION,
        "inputs": {"left": left.name, "right": right.name},
        "settings": {"date_tolerance_days": date_tolerance, "flip_right_sign": flip_right_sign},
        "counts": {"left": len(lhs), "right": len(rhs), "matched": len(matches),
                   "suggested_matches": len(suggested),
                   "unmatched_left": len(unmatched_left), "unmatched_right": len(unmatched_right),
                   "errors_left": len(errors_left), "errors_right": len(errors_right)},
        "totals_by_currency": totals,
        "matches": sorted(matches, key=lambda v: v["left_row"]),
        "unmatched_left": unmatched_left, "unmatched_right": unmatched_right,
        "ambiguous_left_rows": ambiguous_left,
        "ambiguous_right_rows": ambiguous_right,
        "ambiguous_reference_groups": ambiguous_reference_groups,
        "warnings": warnings,
        "input_errors": {"left": errors_left, "right": errors_right},
        "status": "RECONCILED" if not (
            unmatched_left or unmatched_right or errors_left or errors_right or
            ambiguous_reference_groups or warnings
        ) else "REVIEW",
        "disclaimer": "Amount/date matches are suggestions, not confirmed reconciliation. "
                      "Resolve warnings and inspect original statements before approving.",
    }
    return report


def render_html(report: dict) -> str:
    def row(items: list[dict], side: str) -> str:
        return "".join("<tr><td>" + html.escape(side) + "</td><td>" + str(x["row"]) +
                       "</td><td>" + html.escape(x["date"]) + "</td><td>" +
                       html.escape(x["amount"] + " " + x["currency"]) + "</td><td>" +
                       html.escape(x["reference"]) + "</td></tr>" for x in items)
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><title>Ledger Bridge</title>"
            "<style>body{font:16px system-ui;max-width:1100px;margin:3rem auto;padding:1rem}"
            "table{border-collapse:collapse;width:100%}th,td{border:1px solid #ccc;padding:.7rem;text-align:left}</style>"
            "<h1>Ledger Bridge review</h1><p>" + html.escape(report["disclaimer"]) + "</p>"
            "<pre>" + html.escape(json.dumps({"status": report["status"], "counts": report["counts"],
                "totals_by_currency": report["totals_by_currency"]}, indent=2)) + "</pre>"
            "<h2>Unmatched transactions</h2><table><thead><tr><th>Ledger</th><th>Row</th>"
            "<th>Date</th><th>Amount</th><th>Reference</th></tr></thead><tbody>" +
            row(report["unmatched_left"], "Left") + row(report["unmatched_right"], "Right") +
            "</tbody></table></html>")


def gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    app = tk.Tk()
    app.title(f"Ledger Bridge {VERSION} · Final Vestige Studios")
    app.geometry("900x600")
    frame = ttk.Frame(app, padding=20)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Ledger Bridge", font=("Segoe UI", 22, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Explain differences between two exported ledgers. Nothing is uploaded or changed.").pack(anchor="w", pady=(0, 18))
    left, right = tk.StringVar(), tk.StringVar()
    tolerance = tk.StringVar(value="3")
    flip = tk.BooleanVar(value=False)
    result = [None]

    for label, var in (("First ledger (CSV)", left), ("Second ledger (CSV)", right)):
        ttk.Label(frame, text=label).pack(anchor="w")
        line = ttk.Frame(frame)
        line.pack(fill="x", pady=(3, 12))
        ttk.Entry(line, textvariable=var).pack(side="left", fill="x", expand=True)
        ttk.Button(line, text="Browse…", command=lambda v=var: v.set(
            filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")]) or v.get())).pack(side="left", padx=8)
    settings = ttk.Frame(frame)
    settings.pack(anchor="w", pady=5)
    ttk.Label(settings, text="Date tolerance (days)").pack(side="left")
    ttk.Entry(settings, textvariable=tolerance, width=5).pack(side="left", padx=8)
    ttk.Checkbutton(settings, text="Reverse sign of second ledger", variable=flip).pack(side="left", padx=10)
    box = tk.Text(frame, wrap="word", state="disabled")
    box.pack(fill="both", expand=True, pady=10)
    status = tk.StringVar(value="Choose both CSV files to begin.")

    def run() -> None:
        try:
            result[0] = reconcile(Path(left.get()), Path(right.get()), int(tolerance.get()), flip.get())
            box.config(state="normal")
            box.delete("1.0", "end")
            box.insert("1.0", json.dumps(result[0], indent=2))
            box.config(state="disabled")
            status.set(f"{result[0]['counts']['matched']} pairs matched · Status: {result[0]['status']}")
        except (OSError, ValueError, UnicodeError, csv.Error) as exc:
            messagebox.showerror("Reconciliation failed", str(exc))

    def export() -> None:
        if result[0] is None:
            return
        filename = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML reports", "*.html")])
        if filename:
            try:
                Path(filename).write_text(render_html(result[0]), encoding="utf-8")
                status.set("Report saved: " + filename)
            except OSError as exc:
                messagebox.showerror("Report failed", str(exc))
    controls = ttk.Frame(frame)
    controls.pack(fill="x", before=box)
    ttk.Button(controls, text="Reconcile", command=run).pack(side="left")
    ttk.Button(controls, text="Save HTML report", command=export).pack(side="left", padx=10)
    ttk.Label(frame, textvariable=status).pack(anchor="w")
    app.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline export reconciliation.")
    parser.add_argument("left", nargs="?")
    parser.add_argument("right", nargs="?")
    parser.add_argument("--tolerance", type=int, default=3)
    parser.add_argument("--flip-right", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not args.left and not args.right:
        gui()
        return 0
    if not args.left or not args.right:
        parser.error("Provide both ledger files.")
    try:
        result = reconcile(Path(args.left), Path(args.right), args.tolerance, args.flip_right)
        if args.report:
            if args.report.suffix.lower() == ".html":
                args.report.write_text(render_html(result), encoding="utf-8")
            else:
                args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "RECONCILED" else 1
    except (OSError, ValueError, UnicodeError, csv.Error) as exc:
        print("Reconciliation failed:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
