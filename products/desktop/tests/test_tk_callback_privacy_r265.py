"""R265: exercise the actual tkinter.CallWrapper exception dispatch, headless.

No GUI display, real customer files, network requests, or premium entitlements.
A real Tkinter CallWrapper uses a lightweight widget double whose exception
reporting method is the original tkinter.Misc._report_exception implementation.
"""
from __future__ import annotations

import contextlib
import io
import tkinter as tk
import unittest
from unittest import mock

from fvs_suite import ui_callback_privacy as privacy

SECRET = "C:/Customers/PRIVATE_REIMBURSEMENTS_2026.csv"
APPS = ("ledger", "invoices", "spend", "policy", "grants", "procurement")


class _Root:
    # This is Tk's actual built-in default (leaking) error handler; the
    # installer must replace it BEFORE CallWrapper is invoked.
    report_callback_exception = tk.Tk.report_callback_exception


class _Widget:
    _report_exception = tk.Misc._report_exception

    def __init__(self, root):
        self.root = root

    def _root(self):
        return self.root


def dispatch(root, fn):
    return tk.CallWrapper(fn, None, _Widget(root))()


class TkCallbackPrivacyR265(unittest.TestCase):
    def setUp(self):
        self.root = _Root()
        self.modals = []
        self.patcher = mock.patch.object(
            privacy.messagebox, "showerror",
            side_effect=lambda title, msg, **kw: self.modals.append((title, msg, kw)),
        )
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def trigger(self, fn, on_fault=None):
        privacy.install_callback_privacy(self.root, invalidate_review=on_fault)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            dispatch(self.root, fn)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(len(self.modals), 1)
        title, msg, kw = self.modals[-1]
        self.assertEqual((title, msg), (privacy.CALLBACK_TITLE, privacy.CALLBACK_MESSAGE))
        self.assertIs(kw["parent"], self.root)
        self.assertNotIn(SECRET, title + msg)

    def test_default_tk_callback_handler_would_expose_private_path(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            dispatch(self.root, lambda: (_ for _ in ()).throw(ValueError(SECRET)))
        self.assertIn(SECRET, stderr.getvalue())
        self.assertIn("Traceback", stderr.getvalue())

    def test_each_app_identity_uses_shared_handler(self):
        for app in APPS:
            with self.subTest(app=app):
                self.modals.clear()
                self.trigger(lambda app=app: (_ for _ in ()).throw(RuntimeError(f"{app}: {SECRET}")))

    def test_private_oserror(self):
        self.trigger(lambda: (_ for _ in ()).throw(OSError(5, "not found", SECRET)))

    def test_nested_exception_chaining(self):
        def fail():
            try:
                raise ValueError(SECRET)
            except ValueError:
                raise RuntimeError("nested") from OSError(SECRET)
        self.trigger(fail)

    def test_callback_with_unsafe_string_conversion_not_inspected(self):
        class Hostile(Exception):
            def __str__(self):
                raise AssertionError("exception must never be formatted")
        self.trigger(lambda: (_ for _ in ()).throw(Hostile()))

    def test_invalidate_stale_premium_report_before_modal(self):
        report = [SECRET]
        observed = []
        def invalidate():
            report[0] = None
        def showerror(*_args, **_kw):
            observed.append(report[0])
        with mock.patch.object(privacy.messagebox, "showerror", side_effect=showerror):
            privacy.install_callback_privacy(self.root, invalidate_review=invalidate)
            dispatch(self.root, lambda: (_ for _ in ()).throw(RuntimeError(SECRET)))
        self.assertEqual(observed, [None])
        self.assertIsNone(report[0])

    def test_invalidation_failure_does_not_reveal_private_path(self):
        def invalidate():
            raise OSError(5, "invalidating", SECRET)
        self.trigger(lambda: (_ for _ in ()).throw(ValueError(SECRET)), on_fault=invalidate)

    def test_dialog_failure_prints_fixed_redacted_fallback(self):
        privacy.install_callback_privacy(self.root)
        stderr = io.StringIO()
        with mock.patch.object(privacy.messagebox, "showerror", side_effect=OSError(SECRET)):
            with contextlib.redirect_stderr(stderr):
                dispatch(self.root, lambda: (_ for _ in ()).throw(ValueError(SECRET)))
        self.assertEqual(stderr.getvalue(), privacy.FALLBACK_MESSAGE)
        self.assertNotIn(SECRET, stderr.getvalue())

    def test_fallback_stderr_write_failure_is_contained(self):
        privacy.install_callback_privacy(self.root)
        class BrokenWriter:
            def write(self, _):
                raise OSError(SECRET)
        with mock.patch.object(privacy.messagebox, "showerror", side_effect=ValueError(SECRET)):
            with mock.patch.object(privacy.sys, "stderr", BrokenWriter()):
                dispatch(self.root, lambda: (_ for _ in ()).throw(ValueError(SECRET)))

    def test_successful_callback_has_no_modal_or_stderr(self):
        privacy.install_callback_privacy(self.root)
        output = io.StringIO()
        with contextlib.redirect_stderr(output):
            result = dispatch(self.root, lambda: 42)
        self.assertEqual(result, 42)
        self.assertEqual(self.modals, [])
        self.assertEqual(output.getvalue(), "")

    def test_installation_is_per_root(self):
        first = _Root()
        second = _Root()
        privacy.install_callback_privacy(first)
        self.assertIn("report_callback_exception", vars(first))
        self.assertNotIn("report_callback_exception", vars(second))

    def test_all_callback_arguments_are_uninspected(self):
        class Untrusted:
            def __str__(self):
                raise AssertionError("not safe")
        privacy.install_callback_privacy(self.root)
        self.root.report_callback_exception(Untrusted(), Untrusted(), Untrusted())
        self.assertEqual(len(self.modals), 1)


if __name__ == "__main__":
    unittest.main()
