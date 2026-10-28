"""Data Import Doctor — offline CSV preflight GUI and CLI.

Usage: python data_import_doctor.py [file.csv] [--schema rules.json] [--report report.json]
Without a positional file, starts a local Tkinter GUI. No upload or telemetry.
"""
from __future__ import annotations

import argparse
import json
import queue
import sys
import threading
from pathlib import Path

from data_import_checks import VERSION, analyze, load_schema, valid_type, safe_export_report


def report_text(report: dict) -> str:
    lines = [
        f"RESULT: {report['status']}",
        f"Source: {report['source_file']}",
        f"Data records: {report['row_count']}",
        f"Delimiter: {report['delimiter']!r}",
        f"SHA-256: {report['source_sha256']}",
        f"Complete scan: {'yes' if report['scan_complete'] else 'NO — DO NOT RELY ON THIS REVIEW'}",
        f"Total issues: {report['issues_total']}",
        "",
        "ISSUE COUNTS",
    ]
    lines.extend(f"  {key}: {count}" for key, count in report['issue_counts'].items())
    if not report['issue_counts']:
        lines.append("  None detected under the configured rules.")
    lines.append("\nEXAMPLES / LINE REFERENCES")
    lines.extend(f"  line {item['row']}: [{item['code']}] {item['message']}" for item in report['examples'])
    if report['examples_truncated']:
        lines.append("  ...additional issues omitted from examples; counts include all detected issues.")
    lines.append("\nImport compatibility depends on the destination system. A PASS is not a compliance guarantee.")
    return "\n".join(lines)


def gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    app = tk.Tk()
    app.title(f"Data Import Doctor {VERSION} · Final Vestige Studios")
    app.geometry("920x640")
    app.minsize(700, 470)
    pane = ttk.Frame(app, padding=20)
    pane.pack(fill="both", expand=True)
    source_value = tk.StringVar()
    rules_value = tk.StringVar()
    status_value = tk.StringVar(value="Choose a CSV file and optionally an import-rule JSON file.")
    latest: dict | None = None
    latest_source: Path | None = None
    latest_rules: Path | None = None
    busy = False
    events: queue.Queue[tuple[str, object]] = queue.Queue()
    controls: list[ttk.Widget] = []

    ttk.Label(pane, text="Data Import Doctor", font=("Segoe UI", 24, "bold")).pack(anchor="w")
    ttk.Label(pane, text="Spot bad columns, duplicate keys and import failures before they cost you time.").pack(
        anchor="w", pady=(0, 18)
    )

    def invalidate(*_: object) -> None:
        nonlocal latest, latest_source, latest_rules
        latest = None
        latest_source = None
        latest_rules = None
        export_button.state(["disabled"])

    def picker(title: str, variable: tk.StringVar, file_types: list[tuple[str, str]]) -> None:
        ttk.Label(pane, text=title).pack(anchor="w")
        line = ttk.Frame(pane)
        line.pack(fill="x", pady=(3, 12))
        entry = ttk.Entry(line, textvariable=variable)
        entry.pack(side="left", fill="x", expand=True)
        choose = ttk.Button(line, text="Browse…", command=lambda: variable.set(
            filedialog.askopenfilename(filetypes=file_types) or variable.get()))
        choose.pack(side="left", padx=(8, 0))
        controls.extend([entry, choose])
        variable.trace_add("write", invalidate)

    picker("Source CSV", source_value, [("CSV files", "*.csv"), ("All files", "*.*")])
    picker("Import rules (optional JSON)", rules_value, [("JSON rules", "*.json")])

    display = tk.Text(pane, state="disabled", wrap="word", font=("Consolas", 10), height=18)
    display.pack(fill="both", expand=True, pady=12)

    def show(text: str) -> None:
        display.configure(state="normal")
        display.delete("1.0", "end")
        display.insert("1.0", text)
        display.configure(state="disabled")

    def set_busy(value: bool) -> None:
        nonlocal busy
        busy = value
        for widget in controls:
            widget.state(["disabled"] if value else ["!disabled"])
        analyze_button.state(["disabled"] if value else ["!disabled"])
        export_button.state(["disabled"] if value or latest is None else ["!disabled"])

    def poll() -> None:
        nonlocal latest, latest_source, latest_rules
        try:
            kind, payload = events.get_nowait()
        except queue.Empty:
            if busy:
                app.after(80, poll)
            return
        set_busy(False)
        if kind == "error":
            invalidate()
            status_value.set("Analysis failed; no report is available.")
            show("Could not complete analysis. No previous results can be exported.")
            messagebox.showerror("Analysis failed", str(payload))
            return
        assert isinstance(payload, tuple)
        latest, latest_source, latest_rules = payload
        export_button.state(["!disabled"])
        status_value.set(f"{latest['status']} · {latest['row_count']} records · {latest['issues_total']} issues")
        show(report_text(latest))

    def check() -> None:
        if busy:
            return
        path_text = source_value.get().strip()
        if not path_text:
            messagebox.showwarning("Choose CSV", "Please select a CSV file.")
            return
        invalidate()
        source = Path(path_text)
        rules = Path(rules_value.get().strip()) if rules_value.get().strip() else None
        set_busy(True)
        status_value.set("Analyzing locally… Your files are not uploaded or modified.")
        show("Analyzing file and checking source integrity…")

        def worker() -> None:
            try:
                result = analyze(source, rules)
                events.put(("result", (result, source, rules)))
            except (OSError, ValueError, json.JSONDecodeError, UnicodeError) as exc:
                events.put(("error", str(exc)))
            except Exception as exc:
                events.put(("error", f"Unexpected analysis error ({type(exc).__name__})."))

        threading.Thread(target=worker, daemon=True).start()
        app.after(80, poll)

    def export() -> None:
        if busy or latest is None or latest_source is None:
            messagebox.showinfo("No report", "Analyze a CSV first.")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON report", "*.json")])
        if not filename:
            return
        try:
            safe_export_report(latest, Path(filename), latest_source, latest_rules)
            status_value.set("Report saved without modifying source files: " + filename)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Export blocked", str(exc))

    actions = ttk.Frame(pane)
    actions.pack(fill="x")
    analyze_button = ttk.Button(actions, text="Analyze CSV", command=check)
    analyze_button.pack(side="left")
    export_button = ttk.Button(actions, text="Save JSON report", command=export)
    export_button.pack(side="left", padx=10)
    export_button.state(["disabled"])
    ttk.Label(pane, textvariable=status_value).pack(anchor="w", pady=(10, 0))
    app.mainloop()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline, non-destructive CSV import preflight")
    parser.add_argument("csv", nargs="?", help="Source CSV; omit to open the graphical interface")
    parser.add_argument("--schema", type=Path, help="Optional JSON rules file")
    parser.add_argument("--report", type=Path, help="Save report to a new JSON file (never overwrite)")
    args = parser.parse_args(argv)
    if not args.csv:
        if args.schema or args.report:
            parser.error("--schema/--report require a source CSV")
        gui()
        return 0
    try:
        source = Path(args.csv)
        result = analyze(source, args.schema)
        if args.report:
            safe_export_report(result, args.report, source, args.schema)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2 if result["status"] == "INCOMPLETE" else 1 if result["issues_total"] else 0
    except (OSError, ValueError, json.JSONDecodeError, UnicodeError) as exc:
        print("Analysis failed:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
