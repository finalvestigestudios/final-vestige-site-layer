"""Redact uncaught main-thread, background-thread and unraisable Python errors.

CPython's default ``sys.excepthook``, ``threading.excepthook`` and
``sys.unraisablehook`` print
exception objects and tracebacks. Those may include private financial paths,
invoice identifiers and source data. Install before importing any GUI module.
No customer payloads, exception objects, or traceback objects are retained.
This is defense in depth, not a substitute for explicit task error handling.
"""
from __future__ import annotations

import sys
import threading

MAIN_DIAGNOSTIC = "Final Vestige Labs uncaught error; private diagnostics suppressed\n"
THREAD_DIAGNOSTIC = "Final Vestige Labs background task failed; private diagnostics suppressed\n"
UNRAISABLE_DIAGNOSTIC = "Final Vestige Labs cleanup failed; private diagnostics suppressed\n"
INSTALL_DIAGNOSTIC = "Private background diagnostics could not be installed"


def _write_fixed(message: str) -> None:
    try:
        sys.stderr.write(message)
    except Exception:
        # Never call default hooks or print a private exception on fallback.
        pass


def _main_exception(_exc_type: object, _exc_value: object, _exc_traceback: object) -> None:
    # Unhandled main-thread exceptions are routed here by CPython.
    # Never inspect, stringify or retain a private exception or traceback.
    # SystemExit is intercepted by the interpreter before this hook.
    _write_fixed(MAIN_DIAGNOSTIC)


def _thread_exception(_args: object) -> None:
    # The default hook ignores SystemExit. Do the same without touching the
    # thread, traceback, or exception value (which can have unsafe __str__).
    try:
        if _args.exc_type is SystemExit:
            return
    except BaseException:
        # Even a forged hook argument must never escape to the default printer.
        pass
    _write_fixed(THREAD_DIAGNOSTIC)


def _unraisable_exception(_args: object) -> None:
    _write_fixed(UNRAISABLE_DIAGNOSTIC)


def install_background_privacy() -> None:
    """Install all three hooks idempotently, or deny startup if any fails.

    This function must run on the main thread, before the GUI and financial
    inputs. If a hook assignment is rejected or silently discarded, fail
    closed. Never include exception contents in diagnostics or exception chain.
    """
    ready = False
    try:
        threading.excepthook = _thread_exception
        sys.unraisablehook = _unraisable_exception
        sys.excepthook = _main_exception
        ready = (threading.excepthook is _thread_exception
                 and sys.unraisablehook is _unraisable_exception
                 and sys.excepthook is _main_exception)
    except Exception:
        pass
    if not ready:
        raise RuntimeError(INSTALL_DIAGNOSTIC)
