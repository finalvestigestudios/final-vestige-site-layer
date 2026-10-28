"""Renewal Radar: private, offline renewal tracker with calendar export.

Stores only local SQLite data. Calendar exports contain only the entries the
user explicitly exports. No cloud services or background tracking.
Python 3.11+.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import os
import sqlite3
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from ical_utils import render_ical_lines
from renewal_safety import import_csv_atomic, write_new_file

VERSION = "0.2.0"
CADENCES = {"none", "monthly", "yearly"}


def default_db() -> Path:
    location = os.getenv("APPDATA")
    if location:
        return Path(location) / "Final Vestige Studios" / "Renewal Radar" / "renewals.sqlite3"
    return Path.home() / ".local" / "share" / "final-vestige" / "renewal-radar.sqlite3"


def open_store(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS renewal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT '',
        due TEXT NOT NULL,
        cadence TEXT NOT NULL DEFAULT 'none',
        remind_days INTEGER NOT NULL DEFAULT 30,
        notes TEXT NOT NULL DEFAULT ''
    )""")
    return conn


def parse_due(value: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Due date must be YYYY-MM-DD and a valid calendar date.") from exc
    if parsed.isoformat() != value:
        raise ValueError("Due date must be written YYYY-MM-DD.")
    return parsed


def add_entry(conn: sqlite3.Connection, title: str, due: str, category: str = "",
              cadence: str = "none", remind_days: int = 30, notes: str = "") -> int:
    if not isinstance(title, str) or not title.strip() or len(title) > 200:
        raise ValueError("Title must contain 1–200 characters.")
    parse_due(due)
    if cadence not in CADENCES:
        raise ValueError("Cadence must be none, monthly or yearly.")
    if not isinstance(remind_days, int) or not 0 <= remind_days <= 3650:
        raise ValueError("Reminder must be between 0 and 3650 days.")
    with conn:
        result = conn.execute(
            "INSERT INTO renewal(title, category, due, cadence, remind_days, notes) VALUES(?,?,?,?,?,?)",
            (title.strip(), category[:120], due, cadence, remind_days, notes[:2000])
        )
    return int(result.lastrowid)


def delete_entry(conn: sqlite3.Connection, row_id: int) -> bool:
    with conn:
        cursor = conn.execute("DELETE FROM renewal WHERE id=?", (row_id,))
    return cursor.rowcount == 1


def next_occurrence(start: date, cadence: str, as_of: date) -> date | None:
    """Find next date on/after as_of. RFC5545 skips invalid recurrence dates.

    Example: a monthly event on Jan 31 next occurs Mar 31, not Feb 28.
    """
    if cadence == "none":
        return start if start >= as_of else None
    if cadence not in CADENCES:
        raise ValueError("Invalid recurrence.")
    if start >= as_of:
        return start
    if cadence == "yearly":
        year = as_of.year
        for candidate_year in range(year, min(year + 9, 10000)):
            try:
                candidate = start.replace(year=candidate_year)
            except ValueError:
                continue  # Feb 29 in a nonleap year
            if candidate >= as_of:
                return candidate
        return None
    year, month = as_of.year, as_of.month
    if (year, month) < (start.year, start.month):
        year, month = start.year, start.month
    for _ in range(36):
        if year > 9999:
            return None
        if start.day <= calendar.monthrange(year, month)[1]:
            candidate = date(year, month, start.day)
            if candidate >= as_of and candidate >= start:
                return candidate
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return None


def entries(conn: sqlite3.Connection, as_of: date | None = None) -> list[dict]:
    as_of = as_of or date.today()
    rows = []
    for raw in conn.execute("SELECT * FROM renewal ORDER BY title COLLATE NOCASE"):
        row = dict(raw)
        due = next_occurrence(parse_due(row["due"]), row["cadence"], as_of)
        row["next_due"] = due.isoformat() if due else None
        row["days_remaining"] = (due - as_of).days if due else None
        rows.append(row)
    rows.sort(key=lambda r: (r["next_due"] is None, r["next_due"] or "9999-12-31", r["title"].casefold()))
    return rows


def ical_escape(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "").replace(",", "\\,").replace(";", "\\;")


def render_ical(rows: list[dict]) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Final Vestige Studios//Renewal Radar 0.1//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
    ]
    for row in rows:
        due = parse_due(row["due"])
        end = due + timedelta(days=1) if due < date.max else None
        uid = uuid.uuid5(uuid.NAMESPACE_URL, f"finalvestige:renewal-radar:{row['id']}").hex
        lines.extend([
            "BEGIN:VEVENT", f"UID:{uid}@finalvestige.local", f"DTSTAMP:{stamp}",
            f"SUMMARY:{ical_escape(row['title'])}", f"DTSTART;VALUE=DATE:{due:%Y%m%d}",
            f"DESCRIPTION:{ical_escape(row['category'] + ' — ' + row['notes'])}",
        ])
        if end is not None:
            lines.append(f"DTEND;VALUE=DATE:{end:%Y%m%d}")
        if row["cadence"] != "none":
            lines.append("RRULE:FREQ=" + ("MONTHLY" if row["cadence"] == "monthly" else "YEARLY"))
        lines.extend([
            "BEGIN:VALARM", f"TRIGGER:-P{int(row['remind_days'])}D",
            "ACTION:DISPLAY", f"DESCRIPTION:{ical_escape('Reminder: ' + row['title'])}",
            "END:VALARM", "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return render_ical_lines(lines)


def export_ics(conn: sqlite3.Connection, destination: Path) -> int:
    all_rows = [dict(row) for row in conn.execute("SELECT * FROM renewal ORDER BY id")]
    data = render_ical(all_rows)
    write_new_file(destination, data.encode("utf-8"))
    return len(all_rows)


def import_csv(conn: sqlite3.Connection, source: Path) -> dict:
    """Validate an entire CSV before one transaction; never partially import."""
    return import_csv_atomic(conn, source)


def gui(db_path: Path) -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    conn = open_store(db_path)
    app = tk.Tk()
    app.title(f"Renewal Radar {VERSION} · Final Vestige Studios")
    app.geometry("930x620")
    frame = ttk.Frame(app, padding=18)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Renewal Radar", font=("Segoe UI", 22, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Your dates stay on this computer. Export to your calendar for notifications.").pack(anchor="w", pady=(0, 12))
    fields = ttk.Frame(frame)
    fields.pack(fill="x")
    title = tk.StringVar()
    due = tk.StringVar()
    category = tk.StringVar()
    cadence = tk.StringVar(value="none")
    remind = tk.StringVar(value="30")
    for col, (label, var, width) in enumerate((
        ("Renewal name", title, 28), ("Due YYYY-MM-DD", due, 16),
        ("Category", category, 18), ("Cadence", cadence, 12), ("Reminder days", remind, 12))):
        block = ttk.Frame(fields)
        block.grid(row=0, column=col, padx=4, sticky="ew")
        ttk.Label(block, text=label).pack(anchor="w")
        if label == "Cadence":
            ttk.Combobox(block, textvariable=var, values=sorted(CADENCES), state="readonly", width=width).pack()
        else:
            ttk.Entry(block, textvariable=var, width=width).pack()
    columns = ("id", "title", "category", "due", "cadence", "days_remaining")
    table = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
    for col, label, width in (
        ("id", "ID", 40), ("title", "Renewal", 220), ("category", "Category", 130),
        ("due", "Original due", 115), ("cadence", "Repeat", 100), ("days_remaining", "Days until next", 115)):
        table.heading(col, text=label)
        table.column(col, width=width, stretch=col == "title")
    table.pack(fill="both", expand=True, pady=14)
    note = tk.StringVar(value=f"Local database: {db_path}")

    def refresh() -> None:
        table.delete(*table.get_children())
        for item in entries(conn):
            table.insert("", "end", iid=str(item["id"]), values=(
                item["id"], item["title"], item["category"], item["due"], item["cadence"],
                item["days_remaining"] if item["days_remaining"] is not None else "Past / no recurrence"))

    def add() -> None:
        try:
            add_entry(conn, title.get(), due.get(), category.get(), cadence.get(), int(remind.get()))
            title.set("")
            refresh()
            note.set("Renewal saved locally.")
        except (ValueError, OSError) as exc:
            messagebox.showerror("Could not save renewal", str(exc))

    def remove() -> None:
        selected = table.selection()
        if selected and messagebox.askyesno("Delete entry?", "Remove selected renewal from your local database?"):
            delete_entry(conn, int(selected[0]))
            refresh()

    def ics() -> None:
        filename = filedialog.asksaveasfilename(defaultextension=".ics", filetypes=[("Calendar files", "*.ics")])
        if filename:
            try:
                count = export_ics(conn, Path(filename))
                note.set(f"Exported {count} renewal(s) to {filename}. Import this file into your calendar.")
            except OSError as exc:
                messagebox.showerror("Export failed", str(exc))

    def csv_import() -> None:
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filename:
            try:
                result = import_csv(conn, Path(filename))
                refresh()
                if result["problems"]:
                    note.set("CSV rejected. No entries added; correct the listed errors and retry.")
                else:
                    note.set(f"Imported {result['inserted']} renewal(s) successfully.")
                if result["problems"]:
                    messagebox.showwarning("Import blocked — database unchanged", str(result["problems"][:10]))
            except (OSError, ValueError, UnicodeError, sqlite3.DatabaseError) as exc:
                messagebox.showerror("Import failed", str(exc))

    controls = ttk.Frame(frame)
    controls.pack(fill="x", before=table)
    ttk.Button(controls, text="Add renewal", command=add).pack(side="left")
    ttk.Button(controls, text="Delete selected", command=remove).pack(side="left", padx=6)
    ttk.Button(controls, text="Import CSV", command=csv_import).pack(side="left", padx=6)
    ttk.Button(controls, text="Export calendar (.ics)", command=ics).pack(side="left", padx=6)
    ttk.Label(frame, textvariable=note).pack(anchor="w", pady=4)
    refresh()
    app.protocol("WM_DELETE_WINDOW", lambda: (conn.close(), app.destroy()))
    app.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Private renewal tracking and ICS export")
    parser.add_argument("--db", type=Path, default=default_db())
    commands = parser.add_subparsers(dest="command")
    add = commands.add_parser("add")
    add.add_argument("title")
    add.add_argument("due")
    add.add_argument("--category", default="")
    add.add_argument("--cadence", choices=sorted(CADENCES), default="none")
    add.add_argument("--remind-days", type=int, default=30)
    delete = commands.add_parser("delete")
    delete.add_argument("id", type=int)
    commands.add_parser("list")
    export = commands.add_parser("export")
    export.add_argument("destination", type=Path)
    imported = commands.add_parser("import")
    imported.add_argument("csv", type=Path)
    args = parser.parse_args()
    try:
        if args.command is None:
            gui(args.db)
            return 0
        conn = open_store(args.db)
        try:
            if args.command == "add":
                print("Added ID", add_entry(conn, args.title, args.due, args.category,
                                            args.cadence, args.remind_days))
            elif args.command == "list":
                for row in entries(conn):
                    print(f"{row['id']:4}  {row['title']}  due={row['next_due'] or 'past'}  cadence={row['cadence']}")
            elif args.command == "delete":
                return 0 if delete_entry(conn, args.id) else 1
            elif args.command == "export":
                print("Exported entries:", export_ics(conn, args.destination))
            elif args.command == "import":
                result = import_csv(conn, args.csv)
                print(result)
                return 1 if result["problems"] else 0
            return 0
        finally:
            conn.close()
    except (OSError, ValueError, sqlite3.DatabaseError) as exc:
        print("Renewal Radar error:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
