"""Keyboard-usable review workbench for *human* premium exception decisions."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from .exception_review import (
    DECISIONS, append_review, export_register, latest_states, read_cases,
)
from .evidence_vault import restore_evidence, seal_evidence
from .audit_display import visible_review_row
from .ui_errors import safe_error_message
from .review_queue_load import ReviewQueue
from .review_io import perform_custodied_output
from .review_target import revalidate_or_revoke


def open_review_window(parent: tk.Misc, product: str, report_path: str | None = None,
                       *, authorize=None):
    if product not in ("grants", "procurement"):
        raise ValueError("Review window is only available for premium products")
    if authorize is None:
        raise ValueError("Premium review requires a verified entitlement callback")
    # Require affirmative, privacy-safe proof BEFORE constructing the window.
    # A verifier returning None/False or unexpectedly failing must not open
    # a workbench on an unverified premium entitlement.
    if not revalidate_or_revoke(authorize, lambda: None, product=product):
        raise ValueError("Premium entitlement denied")

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
              "Journal files are local and NOT encrypted. "
              "Source references may show Unicode escape sequences for invisible "
              "characters; refer to the original hashed report for exact text."),
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
    selection = ReviewQueue()

    def _revoke_review_view():
        # Fail closed on license expiry/replacement, including while a modal
        # file or passphrase dialog was open. No disk report is deleted.
        _reset_report_view()
        reviewer.set("")
        decision.set(DECISIONS[0])
        rationale.delete("1.0", "end")

    def _authorized():
        if revalidate_or_revoke(authorize, _revoke_review_view, product=product):
            return True
        messagebox.showerror(
            "Premium entitlement required",
            "Your signed entitlement is no longer valid. "
            "Loaded review evidence was cleared; no review, export "
            "or evidence operation was performed.",
            parent=window)
        return False

    def display():
        batch = selection.batch
        if batch is None:
            return
        old_items = tree.get_children()
        if old_items:
            tree.delete(*old_items)
        states = latest_states(selection.journal, batch)
        for case in batch.cases:
            result = states.get(case.case_id)
            tree.insert("", "end", iid=case.case_id, values=visible_review_row(
                case, result["decision"] if result else "pending"))
        status_text.set(f"{len(batch.cases)} exceptions; {len(states)} have recorded human decisions. "
                        "Each review decision remains subject to organizational approval.")

    def _reset_report_view():
        # Switching sources invalidates the old actionable review queue, even
        # if the new CSV, journal, or entitlement fails validation.
        selection.clear()
        report_text.set("")
        previous = tree.get_children()
        if previous:
            tree.delete(*previous)
        status_text.set("No verified report is loaded. Select a valid premium exception report.")


    def _verify_selected_evidence() -> bool:
        try:
            selection.verify_current(product, read_cases, latest_states)
        except (ValueError, OSError, UnicodeError) as exc:
            _reset_report_view()
            messagebox.showerror(
                "Review evidence changed", safe_error_message(exc, operation="report"),
                parent=window)
            return False
        except Exception:
            # Unexpected engine/identity faults must not leave customer rows
            # selected or display private exception/filename diagnostics.
            _reset_report_view()
            messagebox.showerror(
                "Review evidence changed",
                "Review evidence could not be reverified. The selection was cleared; reopen the report.",
                parent=window)
            return False
        return True

    def load_report(path):
        _reset_report_view()
        if not _authorized():
            return
        try:
            selection.load(path, product, read_cases, latest_states)
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror(
                "Cannot open review queue", safe_error_message(exc, operation="report"),
                parent=window)
            return
        except Exception:
            _reset_report_view()
            messagebox.showerror(
                "Cannot open review queue",
                "Review verification stopped unexpectedly. The selection was cleared.",
                parent=window)
            return
        report_text.set(str(selection.report_path))
        try:
            display()
        except (ValueError, OSError, UnicodeError) as exc:
            _reset_report_view()
            messagebox.showerror("Review evidence changed",
                                 safe_error_message(exc, operation="report"), parent=window)
        except Exception:
            _reset_report_view()
            messagebox.showerror(
                "Review evidence changed",
                "Review display could not be verified. The selection was cleared.",
                parent=window)

    def choose_report():
        if not _authorized():
            return
        name = filedialog.askopenfilename(
            parent=window, title="Select generated premium exception report",
            filetypes=[("CSV review reports", "*.csv")])
        if name:
            load_report(name)

    ttk.Button(top, text="Browse…", command=choose_report).grid(row=0, column=2)

    def log_review():
        if not _authorized():
            return
        batch = selection.batch
        if batch is None:
            messagebox.showwarning("Missing report", "Open an exception report first.", parent=window)
            return
        if not _verify_selected_evidence():
            return
        chosen = tree.selection()
        if not chosen:
            messagebox.showwarning("Missing selection", "Select an exception row first.", parent=window)
            return
        # A license may expire or be replaced while the operator edits notes.
        if not _authorized():
            return
        recorded = False
        try:
            append_review(selection.report_path, product, selection.journal,
                          case_id=chosen[0], expected_report_sha256=batch.report_sha256,
                          reviewer=reviewer.get(), decision=decision.get(),
                          rationale=rationale.get("1.0", "end-1c"))
            recorded = True
            # This operator just appended a reviewed event. Bind the GUI to
            # the newly verified history rather than leaving the old snapshot
            # actionable; a concurrent journal edit must force a reload.
            selection.load(selection.report_path, product, read_cases, latest_states)
            display()
        except (ValueError, OSError, UnicodeError) as exc:
            _reset_report_view()
            messagebox.showerror(
                "Review state changed" if recorded else "Review not recorded",
                safe_error_message(exc, operation="review"), parent=window)
            return
        except Exception:
            _reset_report_view()
            # The append might have committed before the unexpected failure;
            # never imply the action is safe to repeat without journal review.
            messagebox.showerror(
                "Review outcome requires inspection",
                "Review processing stopped unexpectedly. The selection was cleared. "
                "Inspect the local review journal before attempting this action again.",
                parent=window)
            return
        status_text.set("Human review action recorded locally. No payment or grant action authorized.")
        rationale.delete("1.0", "end")

    def export():
        if not _authorized():
            return
        batch = selection.batch
        if batch is None:
            messagebox.showwarning("Missing report", "Open a report first.", parent=window)
            return
        target = filedialog.askdirectory(
            parent=window, title="Choose output folder for sanitized review register")
        if not target:
            return
        if not _verify_selected_evidence():
            return
        # The folder picker can remain open beyond license expiry.
        if not _authorized():
            return
        try:
            path = perform_custodied_output(
                lambda: export_register(selection.report_path, product, selection.journal, target,
                                        expected_report_sha256=batch.report_sha256),
                _reset_report_view)
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror(
                "Export needs inspection",
                safe_error_message(exc, operation="export") +
                " The review selection was invalidated. Inspect the chosen folder before retrying.",
                parent=window)
            return
        except Exception:
            messagebox.showerror(
                "Export needs inspection",
                "Review register output could not be verified. The selection was invalidated. "
                "Inspect the chosen folder for an incomplete output before retrying.",
                parent=window)
            return
        status_text.set(f"Human review register exported: {path.name}")
        messagebox.showinfo("Register created", str(path), parent=window)

    def seal_archive():
        if not _authorized():
            return
        batch = selection.batch
        if batch is None:
            messagebox.showwarning("Missing report", "Open a premium exception report first.", parent=window)
            return
        target = filedialog.askdirectory(parent=window, title="Choose encrypted backup destination")
        if not target:
            return
        secret = simpledialog.askstring(
            "Encrypt evidence backup", "Enter a unique passphrase (at least 16 characters).\n"
            "This password is not stored or recoverable.", parent=window, show="*")
        if secret is None:
            return
        confirm = simpledialog.askstring(
            "Confirm passphrase", "Re-enter the passphrase to prevent backup lockout.",
            parent=window, show="*")
        if confirm is None:
            return
        if secret != confirm:
            messagebox.showerror("Passphrases differ", "No archive was created.", parent=window)
            return
        try:
            if not _verify_selected_evidence():
                return
            # Revalidate after the two password prompts, before encryption.
            if not _authorized():
                return
            path = perform_custodied_output(
                lambda: seal_evidence(selection.report_path, product, selection.journal, target,
                                      secret, expected_report_sha256=batch.report_sha256),
                _reset_report_view)
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror(
                "Encrypted backup needs inspection",
                safe_error_message(exc, operation="backup") +
                " The review selection was invalidated. Inspect the chosen folder before retrying.",
                parent=window)
            return
        except Exception:
            messagebox.showerror(
                "Encrypted backup needs inspection",
                "The encrypted output could not be verified. The selection was invalidated. "
                "Inspect the chosen folder for an incomplete archive before retrying.",
                parent=window)
            return
        finally:
            secret = confirm = None
        status_text.set("Authenticated encrypted evidence copy created. Original files remain plaintext.")
        messagebox.showinfo(
            "Encrypted backup created",
            f"Saved: {path.name}\n\nThe original report and journal are still UNENCRYPTED. "
            "Protect or securely dispose of the originals using your organization's procedures. "
            "Losing the passphrase means this backup cannot be recovered.",
            parent=window)

    def restore_archive():
        if not _authorized():
            return
        source = filedialog.askopenfilename(
            parent=window, title="Choose encrypted evidence backup",
            filetypes=[("Final Vestige Evidence Vault", "*.fvault")])
        if not source:
            return
        target = filedialog.askdirectory(parent=window, title="Choose restore destination")
        if not target:
            return
        secret = simpledialog.askstring(
            "Restore encrypted evidence", "Enter the archive passphrase.",
            parent=window, show="*")
        if secret is None:
            return
        try:
            # File, folder and password dialogs can outlive the entitlement.
            if not _authorized():
                return
            folder = perform_custodied_output(
                lambda: restore_evidence(source, target, secret, expected_product=product),
                _reset_report_view)
        except (ValueError, OSError, UnicodeError) as exc:
            messagebox.showerror(
                "Restore needs inspection",
                safe_error_message(exc, operation="restore") +
                " The review selection was invalidated. Inspect the chosen folder before retrying.",
                parent=window)
            return
        except Exception:
            messagebox.showerror(
                "Restore needs inspection",
                "Restored evidence could not be verified. The selection was invalidated. "
                "Inspect the chosen folder for incomplete plaintext before retrying.",
                parent=window)
            return
        finally:
            secret = None
        status_text.set(f"Restored evidence to new folder: {folder.name}. This restored copy is plaintext.")
        messagebox.showinfo(
            "Evidence restored",
            f"Restored to: {folder}\n\nRestored report and journal are PLAINTEXT. "
            "Open the report in its corresponding premium review window.",
            parent=window)

    ttk.Button(button_row, text="Record human review", command=log_review).pack(
        side="left", padx=(0, 8))
    ttk.Button(button_row, text="Export review register…", command=export).pack(side="left")
    ttk.Button(button_row, text="Seal encrypted copy…", command=seal_archive).pack(side="left", padx=8)
    ttk.Button(button_row, text="Restore encrypted copy…", command=restore_archive).pack(side="left")
    ttk.Button(button_row, text="Close", command=window.destroy).pack(side="left", padx=8)
    window.bind("<Control-Return>", lambda _event: log_review())
    window.bind("<Control-Shift-s>", lambda _event: seal_archive())
    window.bind("<Control-Shift-o>", lambda _event: restore_archive())
    window.bind("<Escape>", lambda _event: window.destroy())
    if report_path:
        load_report(report_path)
    window.transient(parent)
    reviewer_entry.focus_set()
    return window
