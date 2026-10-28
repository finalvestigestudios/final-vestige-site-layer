"""Packet Preflight — checklist-based, offline document submission auditing.

All analysis is based on filenames and metadata; no regulatory compliance guarantee.
Python 3.11+. Original files are never changed or uploaded.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from collections import Counter
from pathlib import Path
from packet_safety import (load_checklist, match_relative_path, scan_files,
                           snapshot_digest, validate_checklist, write_new_report)

VERSION = "0.1.0"
STARTER_RULES = {
    "title": "Example submission checklist — replace with your actual requirements",
    "rules": [
        {"name": "Application PDF", "pattern": "application*.pdf", "minimum": 1, "maximum": 1, "max_size_mb": 20},
        {"name": "Budget spreadsheet", "pattern": "budget*.xlsx", "minimum": 1, "maximum": 1},
        {"name": "Supporting attachments", "pattern": "supporting/*", "minimum": 0, "max_size_mb": 20},
    ],
}


def validate_rules(config: object) -> dict:
    """Public compatibility wrapper for existing checklists and tests."""
    return validate_checklist(config)


def match_path(relative: str, pattern: str) -> bool:
    return match_relative_path(relative, pattern)


def list_files(root: Path) -> tuple[list[dict], list[dict]]:
    return scan_files(root)


def preflight(folder: Path, rules_file: Path) -> dict:
    root = folder.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Select a folder.")
    config, rules_digest = load_checklist(rules_file)
    files, scan_errors = list_files(root)
    total_bytes = sum(f["bytes"] for f in files)
    counts: Counter = Counter()
    results = []
    match_tally: Counter = Counter()
    matching_rules: dict[str, list[str]] = {}
    matched_files: set[str] = set()

    for rule in config["rules"]:
        matches = [file for file in files if match_path(file["path"], rule["pattern"])]
        for item in matches:
            match_tally[item["path"]] += 1
            matching_rules.setdefault(item["path"], []).append(rule["name"])
        matched_files.update(item["path"] for item in matches)
        problems: list[dict] = []
        minimum, maximum = rule.get("minimum", 1), rule.get("maximum")
        if len(matches) < minimum:
            problems.append({"code": "TOO_FEW", "detail": f"Found {len(matches)}; require at least {minimum}."})
        if maximum is not None and len(matches) > maximum:
            problems.append({"code": "TOO_MANY", "detail": f"Found {len(matches)}; maximum {maximum}."})
        for match in matches:
            if match["bytes"] == 0 and not rule.get("allow_empty", False):
                problems.append({"code": "EMPTY", "file": match["path"], "detail": "File is empty."})
            limit = rule.get("max_size_mb")
            if limit is not None and match["bytes"] > limit * 1024 * 1024:
                problems.append({"code": "OVERSIZE", "file": match["path"], "detail": f"Exceeds {limit} MiB."})
            extensions = [ext.casefold() for ext in rule.get("extensions", [])]
            if extensions and not any(match["path"].casefold().endswith(ext) for ext in extensions):
                problems.append({"code": "WRONG_EXTENSION", "file": match["path"],
                                 "detail": "Extension not in " + ", ".join(extensions)})
        for problem in problems:
            counts[problem["code"]] += 1
        results.append({
            "name": rule["name"], "pattern": rule["pattern"],
            "matched": len(matches), "files": [item["path"] for item in matches],
            "status": "PASS" if not problems else "CHECK",
            "problems": problems,
        })

    unmatched = sorted(f["path"] for f in files if f["path"] not in matched_files)
    overlapping = [{"file": filename, "rules": matching_rules[filename]}
                   for filename, hits in sorted(match_tally.items()) if hits > 1]
    if overlapping:
        counts["OVERLAPPING_RULES"] += len(overlapping)
    if config.get("forbid_unmatched", False):
        counts["UNMATCHED_FILE"] += len(unmatched)
    if config.get("max_total_size_mb") is not None and total_bytes > config["max_total_size_mb"] * 1024 * 1024:
        counts["TOTAL_OVERSIZE"] += 1
    if scan_errors:
        counts["SCAN_ERROR"] += len(scan_errors)
    return {
        "tool": "Final Vestige Packet Preflight", "version": VERSION,
        "checklist": config.get("title", rules_file.stem),
        "folder": str(root), "file_count": len(files), "total_bytes": total_bytes,
        "results": results, "unmatched_files": unmatched,
        "overlapping_files": overlapping, "scan_errors": scan_errors,
        "rules_sha256": rules_digest,
        "source_snapshot_sha256": snapshot_digest(files, scan_errors),
        "issue_counts": dict(sorted(counts.items())),
        "issues_total": sum(counts.values()), "status": "PASS" if not counts else "CHECK",
        "limitations": "Metadata-only validation. This is not a guarantee of content, eligibility or compliance.",
    }


def render_html(report: dict) -> str:
    rows = []
    for result in report["results"]:
        problems = "; ".join(p["code"] + ": " + p["detail"] for p in result["problems"])
        rows.append("<tr><td>" + html.escape(result["name"]) + "</td><td>" +
                    html.escape(result["pattern"]) + "</td><td>" + str(result["matched"]) +
                    "</td><td>" + html.escape(result["status"]) + "</td><td>" +
                    html.escape(problems) + "</td></tr>")
    extras = "".join("<li>" + html.escape(value) + "</li>" for value in report["unmatched_files"])
    scans = "".join("<li>" + html.escape(err["file"] + ": " + err["message"]) +
                    "</li>" for err in report["scan_errors"])
    overlaps = "".join("<li>" + html.escape(item["file"] + ": " + ", ".join(item["rules"])) +
                       "</li>" for item in report.get("overlapping_files", []))
    issues = "".join("<li>" + html.escape(code) + ": " + str(count) + "</li>"
                     for code, count in sorted(report.get("issue_counts", {}).items()))
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><title>Packet Preflight</title>"
            "<style>body{font:16px system-ui;max-width:1100px;margin:3rem auto;padding:1rem;color:#222}"
            "table{border-collapse:collapse;width:100%}td,th{padding:.8rem;border:1px solid #ccc;text-align:left}"
            "th{background:#eee}</style><h1>Packet Preflight</h1><p>Checklist: " +
            html.escape(str(report["checklist"])) + "</p><p>Status: <strong>" +
            html.escape(report["status"]) + "</strong> — " + str(report["issues_total"]) +
            " issue(s). File names and sizes only; no content or legal compliance validation.</p>"
            "<p>Total scanned bytes: " + str(report.get("total_bytes", "unknown")) +
            ". Snapshot fingerprint (metadata, not file contents): <code>" +
            html.escape(report.get("source_snapshot_sha256", "unknown")) + "</code></p>"
            "<h2>Issue breakdown</h2><ul>" + (issues or "<li>No findings</li>") + "</ul>"
            "<table><thead><tr><th>Requirement</th><th>Pattern</th><th>Found</th><th>Status</th>"
            "<th>Issues</th></tr></thead><tbody>" + "".join(rows) +
            "</tbody></table><h2>Unmatched files</h2><ul>" + (extras or "<li>None</li>") +
            "</ul><h2>Overlapping rule matches</h2><ul>" + (overlaps or "<li>None</li>") +
            "</ul><h2>Scan errors</h2><ul>" + (scans or "<li>None</li>") + "</ul></html>")


def gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    app = tk.Tk()
    app.title(f"Packet Preflight {VERSION} · Final Vestige Studios")
    app.geometry("850x590")
    frame = ttk.Frame(app, padding=18)
    frame.pack(fill="both", expand=True)
    folder_var, rules_var = tk.StringVar(), tk.StringVar()
    note = tk.StringVar(value="Choose a folder and a checklist. The program never changes source files.")
    latest = [None, None, None]
    ttk.Label(frame, text="Packet Preflight", font=("Segoe UI", 22, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Find missing, unexpected and oversized submission attachments.").pack(anchor="w", pady=(0, 16))

    def choose(label: str, var: tk.StringVar, isfolder: bool) -> None:
        ttk.Label(frame, text=label).pack(anchor="w")
        line = ttk.Frame(frame)
        line.pack(fill="x", pady=(4, 12))
        ttk.Entry(line, textvariable=var).pack(side="left", fill="x", expand=True)
        def browse() -> None:
            selected = filedialog.askdirectory() if isfolder else filedialog.askopenfilename(
                filetypes=[("JSON checklist", "*.json")])
            if selected:
                var.set(selected)
        ttk.Button(line, text="Browse…", command=browse).pack(side="left", padx=8)
    choose("Submission folder", folder_var, True)
    choose("Rules checklist (JSON)", rules_var, False)
    output = tk.Text(frame, wrap="word", state="disabled")
    output.pack(fill="both", expand=True, pady=10)

    def show(value: str) -> None:
        output.config(state="normal")
        output.delete("1.0", "end")
        output.insert("1.0", value)
        output.config(state="disabled")

    def run() -> None:
        try:
            if not folder_var.get() or not rules_var.get():
                raise ValueError("Select a folder and rules JSON.")
            latest[0] = preflight(Path(folder_var.get()), Path(rules_var.get()))
            latest[1], latest[2] = Path(folder_var.get()), Path(rules_var.get())
            show(json.dumps({key: latest[0][key] for key in
                             ("status", "checklist", "issue_counts", "results", "unmatched_files",
                              "overlapping_files", "scan_errors", "total_bytes", "limitations")},
                            indent=2, ensure_ascii=False))
            note.set(f"{latest[0]['file_count']} files · {latest[0]['issues_total']} issue(s)")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            latest[:] = [None, None, None]
            show("No current report. Analysis failed; check the selected inputs and try again.")
            note.set("No valid report available")
            messagebox.showerror("Preflight failed", str(exc))

    def save_template() -> None:
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON checklist", "*.json")])
        if filename:
            try:
                write_new_report(Path(filename), json.dumps(STARTER_RULES, indent=2) + "\n",
                                 packet_folder=Path(folder_var.get()) if folder_var.get() else None)
                rules_var.set(filename)
            except (OSError, ValueError) as exc:
                messagebox.showerror("Save failed", str(exc))

    def save_report() -> None:
        if latest[0] is None:
            messagebox.showinfo("No report yet", "Run a preflight first.")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML report", "*.html")])
        if filename:
            try:
                if (Path(folder_var.get()) != latest[1] or Path(rules_var.get()) != latest[2]):
                    raise ValueError("Inputs changed. Run preflight again before saving.")
                fresh = preflight(latest[1], latest[2])
                if (fresh["source_snapshot_sha256"] != latest[0]["source_snapshot_sha256"] or
                    fresh["rules_sha256"] != latest[0]["rules_sha256"]):
                    raise ValueError("Submission or checklist changed. Run preflight again before saving.")
                write_new_report(Path(filename), render_html(latest[0]), packet_folder=latest[1],
                                 protected=(latest[2],))
                note.set("Report saved: " + filename)
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                messagebox.showerror("Save failed", str(exc))

    buttons = ttk.Frame(frame)
    buttons.pack(fill="x", before=output)
    ttk.Button(buttons, text="Run preflight", command=run).pack(side="left")
    ttk.Button(buttons, text="Create sample checklist", command=save_template).pack(side="left", padx=8)
    ttk.Button(buttons, text="Save HTML report", command=save_report).pack(side="left")
    ttk.Label(frame, textvariable=note).pack(anchor="w", pady=8)
    app.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a folder against a JSON checklist.")
    parser.add_argument("folder", nargs="?")
    parser.add_argument("--rules", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--sample", type=Path)
    args = parser.parse_args()
    try:
        if args.sample:
            write_new_report(args.sample, json.dumps(STARTER_RULES, indent=2) + "\n")
            return 0
        if not args.folder:
            gui()
            return 0
        if not args.rules:
            parser.error("--rules is required when a folder is specified.")
        result = preflight(Path(args.folder), args.rules)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if args.report:
            fresh = preflight(Path(args.folder), args.rules)
            if (fresh["source_snapshot_sha256"] != result["source_snapshot_sha256"] or
                fresh["rules_sha256"] != result["rules_sha256"]):
                raise ValueError("Inputs changed during preflight. Rerun before exporting.")
            output = (render_html(result) if args.report.suffix.lower() == ".html"
                      else json.dumps(result, indent=2, ensure_ascii=False) + "\n")
            write_new_report(args.report, output, packet_folder=Path(args.folder), protected=(args.rules,))
        return 1 if result["issues_total"] else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("Preflight failed:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
