"""Windows-only Tk event-dispatch and cancel-safety preflight for four FREE apps.

Unlike R106, this sends Tk synthetic *key events* through the real bound
callbacks. No physical keyboard, NVDA, packaged-EXE or high-contrast certification.
Customer files, reporting operations and premium editors are never opened.
"""
from __future__ import annotations

import os
import platform
import sys

FREE_INPUTS = {"ledger": 2, "invoices": 1, "spend": 1, "policy": 2}
ERROR = "BLOCKED: Labs free-app Tk accelerator/cancel safety was not verified"


class ShortcutBlocked(ValueError):
    """Do not include user input, paths, Tk internals, or exception text in CI."""


def verify_snapshot(app_id, *, input_focus, input_cancels, output_focus,
                    output_cancel, blocked_generates, warnings, engine_calls,
                    files_selected, extra_dialogs, premium_opened):
    """Validate bounded event observations, never customer text or paths.

    All numbers/booleans are strictly typed; -OO must not disable any checks.
    """
    if app_id not in FREE_INPUTS:
        raise ShortcutBlocked("Premium or unknown application rejected")
    expected = FREE_INPUTS[app_id]
    for label, value, target in (
        ("input_focus", input_focus, expected),
        ("input_cancels", input_cancels, expected),
        ("blocked_generates", blocked_generates, 2),
        ("warnings", warnings, 2),
        ("engine_calls", engine_calls, 0),
        ("files_selected", files_selected, 0),
        ("extra_dialogs", extra_dialogs, 0),
    ):
        if type(value) is not int or value != target:
            raise ShortcutBlocked("Invalid " + label + " event observation")
    if output_focus is not True or output_cancel is not True or premium_opened is not False:
        raise ShortcutBlocked("Output focus, cancel or product boundary failed")


def _scan_one(app_id: str) -> None:
    """Generate actual Tk Alt/Ctrl keyboard events without any file input."""
    if app_id not in FREE_INPUTS:
        raise ShortcutBlocked("Premium editor is outside the source-owned scope")
    import tkinter as tk
    from tkinter import ttk
    from unittest.mock import patch
    from fvs_suite import app

    item = app.APPS.get(app_id)
    if item is None or item[3] is not False or len(item[1]) != FREE_INPUTS[app_id]:
        raise ShortcutBlocked("Source product entitlement scope changed")
    title, labels, _, premium = item
    counts = {"input_cancels": 0, "output_cancel": 0, "warnings": 0,
              "engine_calls": 0, "extra_dialogs": 0}
    seen = False
    to_destroy = None

    def engine_denied(*_args, **_kwargs):
        counts["engine_calls"] += 1
        raise ShortcutBlocked("Financial action reached from empty input")

    def cancel_input(*_args, **_kwargs):
        counts["input_cancels"] += 1
        return ""

    def cancel_output(*_args, **_kwargs):
        counts["output_cancel"] += 1
        return ""

    def record_warning(*_args, **_kwargs):
        counts["warnings"] += 1

    def forbidden_dialog(*_args, **_kwargs):
        counts["extra_dialogs"] += 1
        raise ShortcutBlocked("Unexpected dialog")

    def inspect(root):
        nonlocal seen, to_destroy
        if seen:
            raise ShortcutBlocked("Multiple source Tk event inspection")
        to_destroy = root
        root.update_idletasks()
        root.focus_force()
        root.update()
        controls = []

        def collect(parent):
            for child in parent.winfo_children():
                controls.append(child)
                collect(child)

        collect(root)
        entries = [w for w in controls if isinstance(w, ttk.Entry)]
        buttons = [w for w in controls if isinstance(w, ttk.Button)]
        browse = [w for w in buttons if str(w.cget("text")) == "Browse…"]
        generate = [w for w in buttons if str(w.cget("text")) == "Generate review report"]
        expected = FREE_INPUTS[app_id]
        optional_keys = 4 if app_id == "ledger" else 1 if app_id == "invoices" else 0
        if (len(entries) != expected + 1 + optional_keys or
                len(browse) != expected + 1 or len(generate) != 1 or
                root.title() != "Final Vestige Labs — " + title):
            raise ShortcutBlocked("Actual free-app control inventory changed")
        if any(not w.winfo_ismapped() for w in (*entries, *browse, *generate)):
            raise ShortcutBlocked("Free-app controls are not mapped")
        # The new LedgerDiff columns are *not* paths or file-picker fields.
        # Keep them blank throughout cancel/no-engine-call event validation.
        if app_id == "ledger" and any(
                entry.get() for entry in entries[expected:expected + optional_keys]):
            raise ShortcutBlocked("Optional LedgerDiff mapping unexpectedly populated")
        if app_id == "invoices" and entries[expected].get() != "7":
            raise ShortcutBlocked("Invoice window default changed")

        def key(sequence):
            # These are Tk-synthesized events, NOT Windows physical key delivery.
            root.event_generate(sequence, when="tail")
            root.update()

        focus_count = 0
        for index in range(expected):
            key(f"<Alt-KeyPress-{index + 1}>")
            if root.focus_get() != entries[index]:
                raise ShortcutBlocked("Alt input focus event did not reach entry")
            focus_count += 1
            old_cancel = counts["input_cancels"]
            key(f"<Control-KeyPress-{index + 1}>")
            if counts["input_cancels"] != old_cancel + 1 or entries[index].get() != "":
                raise ShortcutBlocked("Cancelled input browse changed the source entry")
        key("<Alt-KeyPress-o>")
        output_focus = root.focus_get() == entries[-1]
        old_output = counts["output_cancel"]
        original_output = entries[-1].get()
        key("<Control-KeyPress-o>")
        output_cancel = (counts["output_cancel"] == old_output + 1 and
                         entries[-1].get() == original_output)
        # Blank required inputs MUST produce warnings, not engine execution.
        # Both distinct bindings reach the same existing generate validation.
        before_warning = counts["warnings"]
        key("<Alt-KeyPress-g>")
        alt_blocked = counts["warnings"] == before_warning + 1
        key("<Control-KeyPress-Return>")
        ctrl_blocked = counts["warnings"] == before_warning + 2
        if not (alt_blocked and ctrl_blocked):
            raise ShortcutBlocked("Generate accelerators did not trigger distinct validation")
        if app_id == "invoices" and entries[expected].get() != "7":
            raise ShortcutBlocked("Invoice review window changed during cancelled events")
        verify_snapshot(
            app_id, input_focus=focus_count, input_cancels=counts["input_cancels"],
            output_focus=output_focus, output_cancel=output_cancel,
            blocked_generates=counts["warnings"], warnings=counts["warnings"],
            engine_calls=counts["engine_calls"],
            files_selected=sum(bool(entry.get()) for entry in entries[:expected]),
            extra_dialogs=counts["extra_dialogs"], premium_opened=False)
        seen = True

    try:
        with (patch.dict(app.APPS, {app_id: (title, labels, engine_denied, premium)}),
              patch.object(tk.Tk, "mainloop", inspect),
              patch.object(app.filedialog, "askopenfilename", side_effect=cancel_input),
              patch.object(app.filedialog, "askdirectory", side_effect=cancel_output),
              patch.object(app.messagebox, "showwarning", side_effect=record_warning),
              patch.object(app.messagebox, "showinfo", side_effect=forbidden_dialog),
              patch.object(app.messagebox, "showerror", side_effect=forbidden_dialog)):
            app.run(app_id)
        if not seen:
            raise ShortcutBlocked("App did not reach native event inspection")
    finally:
        if to_destroy is not None:
            try:
                to_destroy.destroy()
            except tk.TclError:
                pass


def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv or os.name != "nt" or platform.machine().lower() not in ("amd64", "x86_64"):
        print(ERROR, file=sys.stderr)
        return 1
    try:
        for app_id in FREE_INPUTS:
            _scan_one(app_id)
    except Exception:
        # Never leak private paths, input values, widget contents or tracebacks.
        print(ERROR, file=sys.stderr)
        return 1
    print("PASS: 4 free source-Tk UIs; 6 Alt input-focus events, 6 cancelled input pickers, "
          "4 output focus/cancel pairs, 8 blocked blank-input report triggers; "
          "premium editors untouched; NOT physical keys/NVDA/packaged-EXE/QD")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
