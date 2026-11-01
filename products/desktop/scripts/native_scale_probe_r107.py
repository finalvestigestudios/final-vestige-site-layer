"""Native Windows Tk scroll/zoom preflight; never reads customer input.

Checks actual source-built interfaces at 200% and 400% simulated Tk scaling.
Does not certify Win11, NVDA, physical keyboard use or Windows high contrast.
Fails closed with constant diagnostic output; never unlocks premium editors.
"""
from __future__ import annotations

import os
import platform
import sys

FREE_INPUTS = {"ledger": 2, "invoices": 1, "spend": 1, "policy": 2}
SCALES = (2.0, 4.0)
ERROR = "BLOCKED: Labs native scaled-form accessibility gate unavailable"


class ScaleBlocked(ValueError):
    """No customer, path, widget text, traceback or finance data in CI."""


def verify_snapshot(app_id, *, scale, entries, browse, generate, scrollable,
                    focus_revealed, labels_wrapped, controls_nonfocus,
                    system_background):
    """Check bounded trusted observations, not file paths or screen pixels."""
    if app_id not in FREE_INPUTS or type(scale) is not float or scale not in SCALES:
        raise ScaleBlocked("Invalid source-controlled app or zoom")
    if (type(entries) is not int or entries != FREE_INPUTS[app_id] + 1 or
            type(browse) is not int or browse != FREE_INPUTS[app_id] + 1 or
            type(generate) is not int or generate != 1):
        raise ScaleBlocked("Required input/output widgets changed")
    if any(value is not True for value in (
            scrollable, focus_revealed, labels_wrapped,
            controls_nonfocus, system_background)):
        raise ScaleBlocked("Scaled-layout verification failed")


def _scan_one(app_id, scale):
    """Inspect only source-generated widgets, with financial actions disabled."""
    if app_id not in FREE_INPUTS or scale not in SCALES:
        raise ScaleBlocked("Unknown free app or test scale")
    import tkinter as tk
    from tkinter import ttk
    from unittest.mock import patch
    from fvs_suite import app

    source = app.APPS.get(app_id)
    if source is None or source[3] is not False or len(source[1]) != FREE_INPUTS[app_id]:
        raise ScaleBlocked("Product access scope changed")
    title, fields, _, premium = source
    examined = False
    root_created = None

    class ProbeTk(tk.Tk):
        def __init__(self, *args, **kwargs):
            nonlocal root_created
            super().__init__(*args, **kwargs)
            root_created = self
            self.tk.call("tk", "scaling", scale)

    def deny(*_args, **_kwargs):
        raise ScaleBlocked("Private source/engine action unexpectedly invoked")

    def inspect(root):
        nonlocal examined
        if examined or root is not root_created:
            raise ScaleBlocked("Unexpected root window")
        examined = True
        # Enforce minimum supported layout to expose vertical clipping.
        root.geometry("600x390")
        root.update_idletasks()
        root.focus_force()
        root.update()
        children = []
        def collect(parent):
            for child in parent.winfo_children():
                children.append(child)
                collect(child)
        collect(root)
        canvases = [w for w in children if isinstance(w, tk.Canvas)]
        scrollbars = [w for w in children if isinstance(w, ttk.Scrollbar)]
        entries = [w for w in children if isinstance(w, ttk.Entry)]
        buttons = [w for w in children if isinstance(w, ttk.Button)]
        browses = [w for w in buttons if w.cget("text") == "Browse…"]
        generates = [w for w in buttons if w.cget("text") == "Generate review report"]
        hints = [w for w in children if isinstance(w, ttk.Label)
                 and str(w.cget("text")).startswith("Keyboard:")]
        if len(canvases) != 1 or len(scrollbars) != 1 or len(hints) != 1:
            raise ScaleBlocked("Expected native form viewport not found")
        canvas, scrollbar = canvases[0], scrollbars[0]
        if not str(canvas.cget("yscrollcommand")) or not str(scrollbar.cget("command")):
            raise ScaleBlocked("Viewport scrollbar disconnected")
        if not all(w.winfo_ismapped() for w in (*entries, *browses, *generates)):
            raise ScaleBlocked("Required controls not mapped")
        upper = canvas.canvasy(0)
        canvas.yview_moveto(1.0)
        root.update_idletasks()
        lower = canvas.canvasy(0)
        scrollable = lower > upper + 10 and canvas.winfo_height() >= 100
        canvas.yview_moveto(0.0)
        root.update()
        # Native focus must automatically scroll a keyboard-accessible command
        # into view. Its callback is NEVER invoked; no report is generated.
        if len(generates) != 1:
            raise ScaleBlocked("Generate control changed")
        generates[0].focus_set()
        root.update()
        visible_top = canvas.canvasy(0)
        focused_y = generates[0].winfo_rooty() - (
            generates[0].winfo_parent() and
            next(w for w in children if isinstance(w, ttk.Frame) and
                 w is generates[0].master).winfo_rooty()
            if False else 0)
        # Use screen-space comparison to avoid relying on arbitrary ancestry:
        # if focused control is inside the scrolled viewport it must be fully
        # visible between the canvas screen top and bottom.
        focused_top = generates[0].winfo_rooty()
        focused_bottom = focused_top + generates[0].winfo_height()
        canvas_top = canvas.winfo_rooty()
        canvas_bottom = canvas_top + canvas.winfo_height()
        focus_revealed = (
            canvas.canvasy(0) > upper + 10 and
            focused_top >= canvas_top - 2 and
            focused_bottom <= canvas_bottom + 2 and
            root.focus_get() == generates[0])
        hints_wrap = int(float(hints[0].cget("wraplength")))
        labels_wrapped = 100 <= hints_wrap <= canvas.winfo_width() - 32
        controls_nonfocus = (
            str(canvas.cget("takefocus")) == "0" and
            str(scrollbar.cget("takefocus")) == "0")
        system_background = (
            str(canvas.cget("background")) == str(root.cget("background")))
        verify_snapshot(
            app_id, scale=scale, entries=len(entries), browse=len(browses),
            generate=len(generates), scrollable=scrollable,
            focus_revealed=focus_revealed, labels_wrapped=labels_wrapped,
            controls_nonfocus=controls_nonfocus,
            system_background=system_background)

    try:
        with (patch.object(tk, "Tk", ProbeTk),
              patch.object(ProbeTk, "mainloop", inspect),
              patch.dict(app.APPS, {app_id: (title, fields, deny, premium)}),
              patch.object(app.filedialog, "askopenfilename", side_effect=deny),
              patch.object(app.filedialog, "askdirectory", side_effect=deny)):
            app.run(app_id)
        if not examined:
            raise ScaleBlocked("Native Tk preflight did not execute")
    finally:
        if root_created is not None:
            try:
                root_created.destroy()
            except tk.TclError:
                pass


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv or os.name != "nt" or platform.machine().lower() not in ("amd64", "x86_64"):
        print(ERROR, file=sys.stderr)
        return 1
    try:
        for app_id in FREE_INPUTS:
            for scale in SCALES:
                _scan_one(app_id, scale)
    except Exception:
        print(ERROR, file=sys.stderr)
        return 1
    print("PASS: 4 free Tk forms x 2 scales = 8 native vertical-reflow/focus checks; not Win11/NVDA/QD approval")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
