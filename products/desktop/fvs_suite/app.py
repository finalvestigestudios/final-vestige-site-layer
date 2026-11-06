"""Accessible minimal desktop interface; no accounts, telemetry, or network access."""
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from . import engine
from .keyboard_access import install_shortcuts
from .form_layout import standard_stacked_rows
from .scroll_access import ScrollableForm
from .ui_errors import safe_error_message

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


def _ledger_stacked_rows(input_count):
    """Row plan for a narrow/high-DPI LedgerDiff form; no entry values read."""
    if type(input_count) is not int or input_count != 2:
        raise ValueError("Unexpected LedgerDiff input inventory")
    inputs = tuple((3 + 3*i, 4 + 3*i, 5 + 3*i)
                   for i in range(input_count))
    first = 3 + 3*input_count
    return {
        "inputs": inputs,
        "keys": ((first, first + 1), (first + 2, first + 3)),
        "amounts": ((first + 4, first + 5), (first + 6, first + 7)),
        "output": (first + 8, first + 9, first + 10),
        "status": first + 11,
        "generate": first + 12,
        "disclaimer": first + 13,
        "hint": first + 14,
    }


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
    root.geometry("920x610" if premium else "780x500")
    root.minsize(760, 520) if premium else root.minsize(600, 390)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    scroll = ScrollableForm(root)
    frame = scroll.frame
    def ui_label(*args, **kwargs):
        return scroll.track_label(ttk.Label(*args, **kwargs))
    ui_label(frame, text=title, font=("Segoe UI", 17, "bold")).grid(
        row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))
    ui_label(frame, text="Local-first review tools. Findings are not audit, legal, or fraud determinations.",
              wraplength=700).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 16))
    if premium:
        ui_label(frame, text="PRE-RELEASE: not licensed for production use.",
                  font=("Segoe UI", 10, "bold")).grid(row=2, column=0, columnspan=3, sticky="w")
    # Fixed 65-character input widths plus a separate label column pushed
    # every LedgerDiff entry beyond the 600px viewport at 400% Tk scaling.
    # A stacked layout keeps native Tab order and survives resizing.
    ledger_layout = _ledger_stacked_rows(len(labels)) if app_id == "ledger" else None
    other_layout = standard_stacked_rows(app_id, len(labels)) if app_id != "ledger" else None
    layout = ledger_layout or other_layout
    if layout:
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=0)
    selected = [tk.StringVar() for _ in labels]
    input_controls = []
    last_report = [None]
    for index, label in enumerate(labels):
        label_row, entry_row, browse_row = layout["inputs"][index]
        ui_label(frame, text=label).grid(
            row=label_row, column=0, columnspan=3, sticky="ew",
            pady=7, padx=(0, 12))
        entry = ttk.Entry(frame, textvariable=selected[index], width=1)
        entry.grid(row=entry_row, column=0, columnspan=3,
                   sticky="ew", pady=7)
        def choose_file(i=index):
            ext = [("Text and CSV", "*.txt *.md *.csv"), ("All files", "*.*")] if app_id=="policy" else [("CSV files", "*.csv")]
            name = filedialog.askopenfilename(parent=root, title=labels[i], filetypes=ext)
            if name: selected[i].set(name)
        browse = ttk.Button(frame, text="Browse…", command=choose_file)
        browse.grid(row=browse_row, column=0, columnspan=3, sticky="w")
        input_controls.append((entry, browse))
    ledger_columns = None
    if ledger_layout:
        ledger_columns = (tk.StringVar(), tk.StringVar())
        for side, variable in enumerate(ledger_columns):
            label_row, entry_row = ledger_layout["keys"][side]
            label = ("Left" if side == 0 else "Right") + " match-key CSV header (optional)"
            ui_label(frame, text=label).grid(
                row=label_row, column=0, columnspan=3, sticky="ew",
                padx=(0, 12), pady=7)
            ttk.Entry(frame, textvariable=variable, width=1).grid(
                row=entry_row, column=0, columnspan=3,
                sticky="ew", pady=7)
    ledger_amount_columns = None
    if ledger_layout:
        ledger_amount_columns = (tk.StringVar(), tk.StringVar())
        for side, variable in enumerate(ledger_amount_columns):
            label_row, entry_row = ledger_layout["amounts"][side]
            label = ("Left" if side == 0 else "Right") + " amount CSV header (optional)"
            ui_label(frame, text=label).grid(
                row=label_row, column=0, columnspan=3, sticky="ew",
                padx=(0, 12), pady=7)
            ttk.Entry(frame, textvariable=variable, width=1).grid(
                row=entry_row, column=0, columnspan=3, sticky="ew", pady=7)
    invoice_window = tk.StringVar(value="7") if app_id == "invoices" else None
    invoice_window_entry = None
    if invoice_window is not None:
        ui_label(frame, text="Near-match days (0-365)", wraplength=220).grid(
            row=layout["window"][0], column=0, columnspan=3,
            sticky="ew", pady=7, padx=(0, 12))
        invoice_window_entry = ttk.Entry(frame, textvariable=invoice_window, width=1)
        invoice_window_entry.grid(
            row=layout["window"][1], column=0, columnspan=3,
            sticky="ew", pady=7)
    output = tk.StringVar(value=str(Path.home() / "Documents"))
    ui_label(frame, text="Output folder").grid(
        row=layout["output"][0], column=0, columnspan=3,
        sticky="ew", padx=(0, 12))
    output_entry = ttk.Entry(frame, textvariable=output, width=1)
    output_entry.grid(row=layout["output"][1], column=0,
                      columnspan=3, sticky="ew")
    def choose_output():
        folder = filedialog.askdirectory(parent=root, title="Choose output folder")
        if folder: output.set(folder)
    output_browse = ttk.Button(frame, text="Browse…", command=choose_output)
    output_browse.grid(row=layout["output"][2], column=0,
                       columnspan=3, sticky="w")
    rules = tk.StringVar()
    policy_rules_controls = None
    if app_id == "procurement":
        ui_label(frame, text="Price review policy JSON (optional)").grid(
            row=layout["rules"][0], column=0, columnspan=3,
            sticky="ew", padx=(0, 12), pady=7)
        rules_entry = ttk.Entry(frame, textvariable=rules, width=1)
        rules_entry.grid(
            row=layout["rules"][1], column=0, columnspan=3, sticky="ew", pady=7)
        def choose_rules():
            file = filedialog.askopenfilename(parent=root, title="Optional price review policy",
                                              filetypes=[("JSON policy", "*.json")])
            if file: rules.set(file)
        rules_browse = ttk.Button(frame, text="Browse…", command=choose_rules)
        rules_browse.grid(
            row=layout["rules"][2], column=0, columnspan=3, sticky="w")
        policy_rules_controls = (rules_entry, rules_browse)
    status = tk.StringVar(value="Choose your input files. Originals will not be modified.")
    status_row = layout["status"]
    ui_label(frame, textvariable=status, wraplength=690).grid(
        row=status_row, column=0, columnspan=3, sticky="w", pady=(18, 8))
    def execute():
        if premium and not _require_current_premium_entitlement(root, app_id, entitlement_source):
            return
        if any(not p.get().strip() for p in selected):
            messagebox.showwarning("Missing input", "Select every required input file.", parent=root)
            return
        try:
            args = [p.get().strip() for p in selected]
            if app_id == "procurement":
                outputs = action(*args, output.get().strip(), policy_path=rules.get().strip() or None)
            elif app_id == "ledger":
                outputs = action(
                    *args, output.get().strip(),
                    left_match_column=ledger_columns[0].get().strip() or None,
                    right_match_column=ledger_columns[1].get().strip() or None,
                    left_amount_column=ledger_amount_columns[0].get().strip() or None,
                    right_amount_column=ledger_amount_columns[1].get().strip() or None)
            elif app_id == "invoices":
                outputs = action(*args, output.get().strip(),
                                 window_days=engine.invoice_window_days(
                                     invoice_window.get().strip()))
            else:
                outputs = action(*args, output.get().strip())
        except (ValueError, OSError, UnicodeError) as exc:
            detail = safe_error_message(exc, operation="generate")
            status.set("Failed: " + detail)
            messagebox.showerror("Review input files", detail, parent=root)
            return
        last_report[0] = str(outputs[0]) if outputs else None
        names = ", ".join(p.name for p in outputs)
        status.set("Created: " + names)
        messagebox.showinfo("Review reports", "Saved in: " + output.get() + "\n\n" + names, parent=root)
    generate_button = ttk.Button(frame, text="Generate review report", command=execute)
    generate_row = layout["generate"]
    generate_button.grid(row=generate_row, column=0, columnspan=3, sticky="w", pady=(8, 16))
    review_button = None
    if premium:
        def open_exception_review():
            if not _require_current_premium_entitlement(root, app_id, entitlement_source):
                return
            from .review_ui import open_review_window
            from .offline_entitlement import verify_license
            try:
                open_review_window(
                    root, app_id, report_path=last_report[0],
                    authorize=lambda: verify_license(entitlement_source, app_id))
            except (ValueError, OSError, UnicodeError) as exc:
                detail = safe_error_message(exc, operation="report")
                status.set("Review unavailable: " + detail)
                messagebox.showerror("Cannot open review", detail, parent=root)
        review_button = ttk.Button(frame, text="Review exceptions (human only)…",
                                   command=open_exception_review)
        review_button.grid(row=layout["review"], column=0, columnspan=3, sticky="w")
    disclaimer_row = layout["disclaimer"]
    ui_label(frame, text="No AI model is used in this preview. All flags follow deterministic rules.",
              wraplength=690).grid(row=disclaimer_row, column=0,
                                   columnspan=3, sticky="w")
    hint = (f"Keyboard: Alt+1..{len(labels)} focus an input; Ctrl+1..{len(labels)} browse; "
            "Alt+O/Ctrl+O output; Alt+G/Ctrl+Enter generate")
    if app_id == "ledger":
        hint += "; Tab to optional left/right match and amount headers (blank = automatic)"
    if app_id == "invoices":
        hint += "; Alt+W near-match day window (0-365; default 7)"
    if app_id == "procurement":
        hint += "; Alt+P optional policy; Ctrl+P browse policy"
    if premium:
        hint += "; Alt+R review exceptions"
    hint_row = layout["hint"]
    ui_label(frame, text=hint, wraplength=700).grid(
        row=hint_row, column=0, columnspan=3,
        sticky="w", pady=(6, 0))
    install_shortcuts(root, input_controls, (output_entry, output_browse),
                      generate_button, review=review_button,
                      invoice_window=invoice_window_entry,
                      policy_rules=policy_rules_controls)
    root.after_idle(input_controls[0][0].focus_set)
    root.mainloop()
