"""Keyboard-usable review workbench for *human* premium exception decisions."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .exception_review import (
    DECISIONS, append_review, export_register, latest_states, read_cases,
)


def open_review_window(parent: tk.Misc, product: str, report_path: str | None = None):
    if product not in ("grants", "procurement"):
        raise ValueError("Review window is only available for premium products")

    window = tk.Toplevel(parent)
    window.title("Final Vestige Labs — Human Exception Review")
    window.geometry("1080x730")
    window.minsize(850, 590)
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)
    frame = ttk.Frame(window, padding=18)
    frame.grid(sticky="nsew")
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(3, weight=1)

    ttk.Label(frame, text="Exception Review · Human decisions only",
              font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
    ttk.Label(frame, text=("Review completion is NOT an audit opinion, "
              "eligibility finding, payment authorization or fraud determination. "
              "Journal files are local and NOT encrypted."),
              wraplength=1000).grid(row=1, column=0, sticky="w", pady=(6, 14))
    top = ttk.Frame(frame)
    top.grid(row=2, column=0, sticky="ew")
    top.columnconfigure(1, weight=1)
    ttk.Label(top, text="Source report").grid(row=0, column=0, sticky="w")
    report_text = tk.StringVar()
    ttk.Entry(top, textvariable=report_text, state="readonly").grid(
        row=0, column=1, sticky="ew", padx=8)

    columns = ("row", "reference", "flags", "decision")
    tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse", height=10)
    for col, label, size in (
        ("row", "CSV row", 90), ("reference", "Record reference", 220),
        ("flags", "Original exception flags", 490), ("decision", "Human review state", 160),
    ):
        tree.heading(col, text=label)
        tree.column(col, width=size, stretch=col == "flags")
    tree.grid(row=3, column=0, sticky="nsew", pady=12)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=3, column=1, sticky="ns", pady=12)

    form = ttk.Frame(frame)
    form.grid(row=4, column=0, sticky="ew")
    form.columnconfigure(1, weight=1)
    reviewer = tk.StringVar()
    decision = tk.StringVar(value=DECISIONS[0])
    ttk.Label(form, text="Reviewer name / initials").grid(row=0, column=0, sticky="w", pady=5)
    reviewer_entry = ttk.Entry(form, textvariable=reviewer)
    reviewer_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=5)
    ttk.Label(form, text="Review outcome").grid(row=1, column=0, sticky="w", pady=5)
    ttk.Combobox(form, values=DECISIONS, textvariable=decision, state="readonly",
                 width=24).grid(row=1, column=1, sticky="w", padx=8, pady=5)
    ttk.Label(form, text="Rationale (12–2000 characters)").grid(row=2, column=0, sticky="nw", pady=5)
    rationale = tk.Text(form, width=65, height=4, wrap="word")
    rationale.grid(row=2, column=1, sticky="ew", padx=8, pady=5)
    status_text = tk.StringVar(value="Choose a report; select an exception to record a decision.")
    ttk.Label(frame, textvariable=status_text, wraplength=1000).grid(
        row=6, column=0, sticky="w", pady=(6, 0))
    button_row = ttk.Frame(frame)
    button_row.grid(row=5, column=0, sticky="w", pady=(10, 2))
    batch_holder = [None]
    journal_holder = [None]

    def display():
        batch = batch_holder[0]
        if batch is None:
            return
        tree.delete(*tree.get_children())
        states = latest_states(journal_holder[0], batch)
        for case in batch.cases:
            result = states.get(case.case_id)
            tree.insert("", "end", iid=case.case_id, values=(
                case.report_row, case.source_key, case.flags,
                result["decision"] if result else "pending"))
        status_text.set(f"{len(batch.cases)} exceptions; {len(states)} have recorded human decisions. "
                        "Each review decision remains subject to organizational approval.")

    def load_report(path):
        try:
            batch = read_cases(path, product)
            journal = Path(path).with_suffix(".review.jsonl")
            latest_states(journal, batch)  # Fail closed on corrupted or stale journals.
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror("Cannot open review queue", str(exc), parent=window)
            return
        batch_holder[0], journal_holder[0] = batch, journal
        report_text.set(str(path))
        display()

    def choose_report():
        name = filedialog.askopenfilename(
            parent=window, title="Select generated premium exception report",
            filetypes=[("CSV review reports", "*.csv")])
        if name:
            load_report(name)

    ttk.Button(top, text="Browse…", command=choose_report).grid(row=0, column=2)

    def log_review():
        batch = batch_holder[0]
        if batch is None:
            messagebox.showwarning("Missing report", "Open an exception report first.", parent=window)
            return
        chosen = tree.selection()
        if not chosen:
            messagebox.showwarning("Missing selection", "Select an exception row first.", parent=window)
            return
        try:
            append_review(report_text.get(), product, journal_holder[0],
                          case_id=chosen[0], expected_report_sha256=batch.report_sha256,
                          reviewer=reviewer.get(), decision=decision.get(),
                          rationale=rationale.get("1.0", "end-1c"))
            display()
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror("Review not recorded", str(exc), parent=window)
            return
        status_text.set("Human review action recorded locally. No payment or grant action authorized.")
        rationale.delete("1.0", "end")

    def export():
        batch = batch_holder[0]
        if batch is None:
            messagebox.showwarning("Missing report", "Open a report first.", parent=window)
            return
        target = filedialog.askdirectory(
            parent=window, title="Choose output folder for sanitized review register")
        if not target:
            return
        try:
            path = export_register(report_text.get(), product, journal_holder[0], target)
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror("Export failed", str(exc), parent=window)
            return
        status_text.set(f"Human review register exported: {path.name}")
        messagebox.showinfo("Register created", str(path), parent=window)

    ttk.Button(button_row, text="Record human review", command=log_review).pack(
        side="left", padx=(0, 8))
    ttk.Button(button_row, text="Export review register…", command=export).pack(side="left")
    ttk.Button(button_row, text="Close", command=window.destroy).pack(side="left", padx=8)
    window.bind("<Control-Return>", lambda _event: log_review())
    window.bind("<Escape>", lambda _event: window.destroy())
    if report_path:
        load_report(report_path)
    window.transient(parent)
    reviewer_entry.focus_set()
    return window
