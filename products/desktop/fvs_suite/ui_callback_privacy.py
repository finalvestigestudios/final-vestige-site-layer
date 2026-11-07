"""Path-private fallback for unexpected Tk callbacks in all six utilities.

Tkinter's default ``report_callback_exception`` prints full tracebacks to
stderr, potentially exposing financial filenames and row data when a browse,
report, or review callback raises outside its usual input-validation handler.
This is a last-resort boundary, not a substitute for normal UI error handling.
"""
from __future__ import annotations

import sys
from tkinter import messagebox

CALLBACK_TITLE = "Action not completed"
CALLBACK_MESSAGE = (
    "An unexpected error interrupted this action. "
    "No compliance decision was made. Review your local output files before retrying."
)
FALLBACK_MESSAGE = "Final Vestige Labs action failed; private diagnostics suppressed\n"


def install_callback_privacy(root, *, invalidate_review=None) -> None:
    """Install a per-window redacted fallback before any user callbacks run.

    ``invalidate_review`` must invalidate any implicit premium report selection.
    Exception arguments are deliberately neither inspected nor saved. A native
    message box informs keyboard and screen-reader users; if even that fails,
    output only a fixed path-free message to stderr. No telemetry or logging.
    """
    def report_callback_exception(_kind, _value, _traceback):
        if invalidate_review is not None:
            try:
                invalidate_review()
            except Exception:
                # A failed invalidator may itself contain a private filename.
                pass
        try:
            messagebox.showerror(CALLBACK_TITLE, CALLBACK_MESSAGE, parent=root)
        except Exception:
            # Do not invoke Tkinter's default traceback printer on this path.
            try:
                sys.stderr.write(FALLBACK_MESSAGE)
            except Exception:
                pass

    root.report_callback_exception = report_callback_exception
