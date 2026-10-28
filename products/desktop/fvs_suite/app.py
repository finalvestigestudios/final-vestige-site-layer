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

def _select_premium_entitlement(root, product):
    """No premium UI or customer files before an Ed25519 entitlement verifies."""
    from . import offline_entitlement as license
    if not license.TRUSTED_PUBLIC_KEYS:
        messagebox.showerror(
            "Premium preview locked",
            "This development build has no production signing authority. "
            "The premium tools remain unavailable for customer data.",
            parent=root)
        return None
    installed = license.installed_license_path(product)
    try:
        license.verify_license(installed, product)
        return installed
    except (license.EntitlementError, OSError, UnicodeError):
        chosen = filedialog.askopenfilename(
            parent=root, title="Select signed Final Vestige premium entitlement",
            filetypes=[("Signed entitlement", "*.fvslicense")])
        if not chosen:
            return None
        try:
            license.verify_license(chosen, product)
            return Path(chosen)
        except (license.EntitlementError, OSError, UnicodeError):
            messagebox.showerror(
                "Premium entitlement rejected",
                "This entitlement is invalid, expired, or not issued for this product.",
                parent=root)
            return None


def _require_current_premium_entitlement(root, product, source):
    from . import offline_entitlement as license
    try:
        license.verify_license(source, product)
        return True
    except (license.EntitlementError, OSError, UnicodeError):
        messagebox.showerror(
            "Premium entitlement required",
            "This product's entitlement can no longer be verified. "
            "No report or review action was performed.",
            parent=root)
        return False


def run(app_id):
    if app_id not in APPS: raise ValueError("Unknown application")
    title, labels, action, premium = APPS[app_id]
    root = tk.Tk()
    entitlement_source = None
    if premium:
        root.withdraw()
        entitlement_source = _select_premium_entitlement(root, app_id)
        if entitlement_source is None:
            root.destroy()
            return
        root.deiconify()
    root.title("Final Vestige Labs — " + title)
    root.geometry("920x580" if premium else "780x470")
    root.minsize(760, 520) if premium else root.minsize(600, 390)
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
    last_report = [None]
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
    rules = tk.StringVar()
    if app_id == "procurement":
        ttk.Label(frame, text="Price review policy JSON (optional)").grid(
            row=folder_row+1, column=0, sticky="w", padx=(0, 12), pady=7)
        ttk.Entry(frame, textvariable=rules).grid(row=folder_row+1, column=1, sticky="ew", pady=7)
        def choose_rules():
            file = filedialog.askopenfilename(title="Optional price review policy",
                                              filetypes=[("JSON policy", "*.json")])
            if file: rules.set(file)
        ttk.Button(frame, text="Browse…", command=choose_rules).grid(
            row=folder_row+1, column=2, padx=(8, 0))
    status = tk.StringVar(value="Choose your input files. Originals will not be modified.")
    ttk.Label(frame, textvariable=status, wraplength=690).grid(
        row=folder_row+2, column=0, columnspan=3, sticky="w", pady=(18, 8))
    def execute():
        if premium and not _require_current_premium_entitlement(root, app_id, entitlement_source):
            return
        if any(not p.get().strip() for p in selected):
            messagebox.showwarning("Missing input", "Select every required input file.")
            return
        try:
            args = [p.get().strip() for p in selected]
            if app_id == "procurement":
                outputs = action(*args, output.get().strip(), policy_path=rules.get().strip() or None)
            else:
                outputs = action(*args, output.get().strip())
        except (ValueError, OSError, UnicodeError, PermissionError) as exc:
            status.set("Failed: " + str(exc))
            messagebox.showerror("Review input files", str(exc))
            return
        last_report[0] = str(outputs[0]) if outputs else None
        names = ", ".join(p.name for p in outputs)
        status.set("Created: " + names)
        messagebox.showinfo("Review reports", "Saved in: " + output.get() + "\n\n" + names)
    ttk.Button(frame, text="Generate review report", command=execute).grid(
        row=folder_row+3, column=0, columnspan=3, sticky="w", pady=(8, 16))
    if premium:
        def open_exception_review():
            if not _require_current_premium_entitlement(root, app_id, entitlement_source):
                return
            from .review_ui import open_review_window
            from .offline_entitlement import verify_license
            open_review_window(
                root, app_id, report_path=last_report[0],
                authorize=lambda: verify_license(entitlement_source, app_id))
        ttk.Button(frame, text="Review exceptions (human only)…",
                   command=open_exception_review).grid(
                       row=folder_row+4, column=0, columnspan=3, sticky="w")
    ttk.Label(frame, text="No AI model is used in this preview. All flags follow deterministic rules.",
              wraplength=690).grid(row=folder_row+(5 if premium else 4), column=0,
                                   columnspan=3, sticky="w")
    root.mainloop()
