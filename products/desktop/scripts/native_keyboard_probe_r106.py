"""Windows-only, source-Tk keyboard focus preflight for the four free Labs apps.

Runs the actual application's Tk widget construction in a private QA process,
without entering its event loop or selecting financial/customer files. The
engine action and every file chooser are replaced by deny-only guards. The
premium applications are NEVER started by this audit.

This is keyboard traversal/binding evidence, NOT an NVDA, physical keypress,
packaged-EXE, WCAG, Windows 11, or commercial release certification. R105
separately observes the packaged EXE windows and locked premium dialogs.
"""
from __future__ import annotations

import os
import platform
import sys

# Exact source-owned product inventory. Do not derive this from mutable widgets.
FREE = {
    "ledger": (2, "Final Vestige Labs — LedgerDiff Lite"),
    "invoices": (1, "Final Vestige Labs — Invoice Twin Scout"),
    "spend": (1, "Final Vestige Labs — SpendMap Lite"),
    "policy": (2, "Final Vestige Labs — Policy Delta Desk"),
}
LEDGER_KEY_LABELS = ("Left match-key CSV header (optional)", "Right match-key CSV header (optional)")
LEDGER_AMOUNT_LABELS = ("Left amount CSV header (optional)", "Right amount CSV header (optional)")
INVOICE_WINDOW_LABEL = "Near-match days (0-365)"
ERROR = "BLOCKED: native Labs keyboard/focus contract could not be verified"


class KeyboardBlocked(ValueError):
    """Fail closed without displaying private widget state or exception details."""


def _expected_order(inputs: int, *, ledger_keys: bool = False,
                    invoice_window: bool = False) -> tuple[str, ...]:
    if (type(inputs) is not int or not 1 <= inputs <= 3
            or type(ledger_keys) is not bool or type(invoice_window) is not bool
            or (ledger_keys and invoice_window)):
        raise KeyboardBlocked("Invalid source-owned input count")
    result = []
    for i in range(1, inputs + 1):
        result.extend((f"input_{i}", f"browse_{i}"))
    if ledger_keys:
        result.extend(("ledger_left_key", "ledger_right_key",
                       "ledger_left_amount", "ledger_right_amount"))
    if invoice_window:
        result.append("invoice_window")
    result.extend(("output", "browse_output", "generate"))
    return tuple(result)


def _expected_bindings(inputs: int) -> frozenset[str]:
    _expected_order(inputs)
    bindings = {"<Alt-Key-o>", "<Control-Key-o>",
                "<Alt-Key-g>", "<Control-Return>"}
    for i in range(1, inputs + 1):
        bindings.add(f"<Alt-Key-{i}>")
        bindings.add(f"<Control-Key-{i}>")
    return frozenset(bindings)


def _verify_snapshot(app_id: str, *, window_title: str, entry_count: int,
                     traversal: tuple[str, ...], cycle_closed: bool,
                     bindings: frozenset[str], first_focus: bool,
                     static_labels: tuple[str, ...],
                     source_input_labels: tuple[str, ...]) -> None:
    """Validate synthetic or real Tk observations using strict, fixed names.

    There are deliberately no assert statements: -OO may not bypass checks.
    Caller must never include actual entry text, file paths or user-provided
    financial data in these arguments or in any output.
    """
    if app_id not in FREE or type(entry_count) is not int:
        raise KeyboardBlocked("Unknown or premium product")
    inputs, expected_title = FREE[app_id]
    if window_title != expected_title or entry_count != inputs + 1 + (4 if app_id == "ledger" else 1 if app_id == "invoices" else 0):
        raise KeyboardBlocked("Window or editable-control contract changed")
    if type(traversal) is not tuple or traversal != _expected_order(inputs, ledger_keys=(app_id == "ledger"),
                                         invoice_window=(app_id == "invoices")):
        raise KeyboardBlocked("Incomplete or reordered Tab sequence")
    if cycle_closed is not True or first_focus is not True:
        raise KeyboardBlocked("Keyboard cycle or first focus unavailable")
    if type(bindings) is not frozenset or not _expected_bindings(inputs) <= bindings:
        raise KeyboardBlocked("Missing keyboard accelerator")
    if "<Alt-Key-r>" in bindings:
        raise KeyboardBlocked("Unexpected premium review accelerator in free app")
    if (type(static_labels) is not tuple or
            type(source_input_labels) is not tuple or
            len(source_input_labels) != inputs or
            any(type(label) is not str for label in static_labels + source_input_labels)):
        raise KeyboardBlocked("Missing source-owned labels")
    expected_labels = (*source_input_labels, "Output folder")
    if app_id == "ledger":
        expected_labels += LEDGER_KEY_LABELS + LEDGER_AMOUNT_LABELS
    if app_id == "invoices":
        expected_labels += (INVOICE_WINDOW_LABEL,)
    if any(label not in static_labels for label in expected_labels):
        raise KeyboardBlocked("Input/output/ledger-key labels missing")
    if app_id != "invoices" and INVOICE_WINDOW_LABEL in static_labels:
        raise KeyboardBlocked("Invoice-only control exposed in another app")
    if app_id != "ledger" and any(label in static_labels for label in
                                   LEDGER_KEY_LABELS + LEDGER_AMOUNT_LABELS):
        raise KeyboardBlocked("Ledger-only controls exposed in another app")
    if not any("Keyboard:" in label and "Alt+G" in label and
               "Ctrl+Enter" in label and "Alt+1" in label and
               "Ctrl+1" in label for label in static_labels):
        raise KeyboardBlocked("Visible keyboard instructions missing")
    if not any("Findings are not audit, legal, or fraud determinations." in label
               for label in static_labels):
        raise KeyboardBlocked("Human-review disclaimer missing")


def _verified_initial_focus(scheduled, root, first_entry):
    """Admit exactly one source-scheduled, bound first-field focus callback."""
    if type(scheduled) is not list or len(scheduled) != 1:
        raise KeyboardBlocked("Expected exactly one initial focus idle callback")
    owner, callback, args = scheduled[0]
    if (owner is not root or getattr(callback, "__self__", None) is not first_entry
            or getattr(callback, "__name__", None) != "focus_set"
            or args != () or not callable(callback)):
        raise KeyboardBlocked("Unexpected first focus callback")
    return callback


def _scan_one(app_id: str) -> None:
    """Construct actual free-app Tk widgets; reject unsafe calls and teardown."""
    if app_id not in FREE:
        raise KeyboardBlocked("Never scan a premium editor")
    import tkinter as tk
    from tkinter import ttk
    from unittest.mock import patch

    from fvs_suite import app

    product = app.APPS.get(app_id)
    if product is None or product[3] is not False or len(product[1]) != FREE[app_id][0]:
        raise KeyboardBlocked("Source product identity or entitlement changed")
    title, input_labels, _, premium = product
    examined = False
    root_to_destroy = None
    scheduled_initial_focus = []

    def capture_idle(root, callback, *args):
        # Keep the app's real declared initial focus target, but schedule it
        # only once the intercepted root has become an active native window.
        # A bare update_idletasks() can fire it before native focus is possible.
        scheduled_initial_focus.append((root, callback, args))
        return "r106-private-idle-capture"

    def deny(*_args, **_kwargs):
        raise KeyboardBlocked("Input chooser or financial action unexpectedly invoked")

    def inspect(root):
        nonlocal examined, root_to_destroy
        root_to_destroy = root
        if examined:
            raise KeyboardBlocked("Multiple root windows")
        # Real native Tk focus and traversal require a mapped window.
        root.update_idletasks()
        root.focus_force()
        root.update()
        widgets = []

        def collect(parent):
            for child in parent.winfo_children():
                widgets.append(child)
                collect(child)

        collect(root)
        entries = [widget for widget in widgets if isinstance(widget, ttk.Entry)]
        buttons = [widget for widget in widgets if isinstance(widget, ttk.Button)]
        browses = [widget for widget in buttons if widget.cget("text") == "Browse…"]
        generate = [widget for widget in buttons
                    if widget.cget("text") == "Generate review report"]
        inputs = FREE[app_id][0]
        expected_entries = inputs + 1 + (4 if app_id == "ledger" else 1 if app_id == "invoices" else 0)
        if len(entries) != expected_entries or len(browses) != inputs + 1 or len(generate) != 1:
            raise KeyboardBlocked("Interactive control inventory changed")
        if any(not widget.winfo_ismapped() for widget in (*entries, *browses, *generate)):
            raise KeyboardBlocked("Required control not mapped")

        expected = _expected_order(inputs, ledger_keys=(app_id == "ledger"),
                                   invoice_window=(app_id == "invoices"))
        canonical_widgets = []
        for i in range(inputs):
            canonical_widgets.extend((entries[i], browses[i]))
        if app_id == "ledger":
            canonical_widgets.extend(entries[inputs:inputs + 4])
        if app_id == "invoices":
            canonical_widgets.append(entries[inputs])
        canonical_widgets.extend((entries[-1], browses[-1], generate[0]))
        names_by_widget = dict(zip(canonical_widgets, expected))
        current = entries[0]
        observed = []
        for _ in expected:
            observed.append(names_by_widget.get(current, "<unverified>"))
            current = current.tk_focusNext()
            if current is None:
                raise KeyboardBlocked("Tk focus traversal unavailable")

        focus_callback = _verified_initial_focus(
            scheduled_initial_focus, root, entries[0])
        focus_callback()
        root.update()
        keys = _expected_bindings(inputs) | frozenset(("<Alt-Key-r>",))
        active_bindings = frozenset(key for key in keys if root.bind(key))
        static_labels = tuple(str(widget.cget("text")) for widget in widgets
                              if isinstance(widget, ttk.Label))
        _verify_snapshot(
            app_id, window_title=root.title(), entry_count=len(entries),
            traversal=tuple(observed), cycle_closed=(current == entries[0]),
            bindings=active_bindings, first_focus=(root.focus_get() == entries[0]),
            static_labels=static_labels, source_input_labels=tuple(input_labels))
        examined = True

    try:
        # Replace file access and financial processing with unconditional rejects.
        # The UI layout and keyboard bindings still come from real app.run().
        guarded = (title, input_labels, deny, premium)
        with (patch.dict(app.APPS, {app_id: guarded}),
              patch.object(tk.Tk, "mainloop", inspect),
              patch.object(tk.Tk, "after_idle", capture_idle),
              patch.object(app.filedialog, "askopenfilename", side_effect=deny),
              patch.object(app.filedialog, "askdirectory", side_effect=deny)):
            app.run(app_id)
        if not examined:
            raise KeyboardBlocked("App did not reach native Tk focus inspection")
    finally:
        if root_to_destroy is not None:
            try:
                root_to_destroy.destroy()
            except tk.TclError:
                pass


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv or os.name != "nt" or platform.machine().lower() not in ("amd64", "x86_64"):
        print(ERROR, file=sys.stderr)
        return 1
    try:
        for app_id in FREE:
            _scan_one(app_id)
    except Exception:
        # Deliberately no exception, filesystem path, widget text or traceback
        # is exported to CI: failure is blocking, investigation is local only.
        print(ERROR, file=sys.stderr)
        return 1
    print("PASS: 4/4 free native Tk focus/Tab/accelerator contracts, including "
          "4 LedgerDiff source-header Tab stops; premium editor untouched; "
          "NOT NVDA/physical-keys/WCAG/Win11/QD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
