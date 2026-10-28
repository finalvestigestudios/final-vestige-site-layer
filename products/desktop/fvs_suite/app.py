"""Accessible minimal desktop interface; no accounts, telemetry, or network access."""
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from . import engine

APPS = {
    "ledger": ("LedgerDiff Lite", ["Left ledger CSV", "Right ledger CSV"], engine.ledger_diff, False),
    "invoices": ("Invoice Twin Scout", ["Invoice CSV"], engine.invoice_twins, False),
    "spend": ("SpendMap Lite", ["Spend CSV"], engine.spend_map, False),
    "policy": ("Policy Delta Desk", ["Old policy TXT/MD/CSV", "New policy TXT/MD/CSV"], engine.policy_delta, False),
    "grants": ("GrantAudit Studio Pro — development preview",
               ["Claims CSV", "Ledger CSV", "Budgets CSV"], engine.grant_audit, True),
    "procurement": ("ProcureGuard Studio Pro — development preview",
                    ["Purchase orders CSV", "Invoices CSV", "Receipts CSV"], engine.procure_guard, True),
}

def run(app_id):
    if app_id not in APPS: raise ValueError("Unknown application")
    title, labels, action, premium = APPS[app_id]
    root = tk.Tk()
    root.title("Final Vestige Labs — " + title)
    root.geometry("780x470")
    root.minsize(600, 390)
    root.columnconfigure(0, weight=1)
    frame = ttk.Frame(root, padding=24)
    frame.grid(sticky="nsew")
    frame.columnconfigure(1, weight=1)
    ttk.Label(frame, text=title, font=("Segoe UI", 17, "bold")).grid(
        row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
    ttk.Label(frame, text="Local-first review tools. Findings are not audit, legal, or fraud determinations.",
              wraplength=700).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 16))
    if premium:
        ttk.Label(frame, text="PRE-RELEASE: not licensed for production use.",
                  foreground="#9c3d20").grid(row=2, column=0, columnspan=3, sticky="w")
    selected = [tk.StringVar() for _ in labels]
    base_row = 3
    for index, label in enumerate(labels):
        row = base_row + index
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=7, padx=(0, 12))
        ttk.Entry(frame, textvariable=selected[index], width=65).grid(row=row, column=1, sticky="ew", pady=7)
        def choose_file(i=index):
            ext = [("Text and CSV", "*.txt *.md *.csv"), ("All files", "*.*")] if app_id=="policy" else [("CSV files", "*.csv")]
            name = filedialog.askopenfilename(title=labels[i], filetypes=ext)
            if name: selected[i].set(name)
        ttk.Button(frame, text="Browse…", command=choose_file).grid(row=row, column=2, padx=(8, 0))
    output = tk.StringVar(value=str(Path.home() / "Documents"))
    folder_row = base_row + len(labels) + 1
    ttk.Label(frame, text="Output folder").grid(row=folder_row, column=0, sticky="w", padx=(0, 12))
    ttk.Entry(frame, textvariable=output).grid(row=folder_row, column=1, sticky="ew")
    def choose_output():
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder: output.set(folder)
    ttk.Button(frame, text="Browse…", command=choose_output).grid(row=folder_row, column=2, padx=(8, 0))
    status = tk.StringVar(value="Choose your input files. Originals will not be modified.")
    ttk.Label(frame, textvariable=status, wraplength=690).grid(
        row=folder_row+2, column=0, columnspan=3, sticky="w", pady=(18, 8))
    def execute():
        if any(not p.get().strip() for p in selected):
            messagebox.showwarning("Missing input", "Select every required input file.")
            return
        try:
            outputs = action(*(p.get().strip() for p in selected), output.get().strip())
        except (ValueError, OSError, UnicodeError, PermissionError) as exc:
            status.set("Failed: " + str(exc))
            messagebox.showerror("Review input files", str(exc))
            return
        names = ", ".join(p.name for p in outputs)
        status.set("Created: " + names)
        messagebox.showinfo("Review reports", "Saved in: " + output.get() + "\n\n" + names)
    ttk.Button(frame, text="Generate review report", command=execute).grid(
        row=folder_row+3, column=0, columnspan=3, sticky="w", pady=(8, 16))
    ttk.Label(frame, text="No AI model is used in this preview. All flags follow deterministic rules.",
              wraplength=690).grid(row=folder_row+4, column=0, columnspan=3, sticky="w")
    root.mainloop()
