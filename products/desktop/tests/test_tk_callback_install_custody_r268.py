"""R268: Tk callback safety handler must be installed, not merely assigned.

Headless Tk CallWrapper, injected root-assignment faults, no real customer data.
"""
from __future__ import annotations

import contextlib
import io
import tkinter as tk
import unittest
from unittest import mock

from fvs_suite import ui_callback_privacy as privacy

PRIVATE = "C:/Clients/SECRET_PAYROLL_2026.csv"
APPS = ("ledger", "invoices", "spend", "policy", "grants", "procurement")


class _Root:
    report_callback_exception = tk.Tk.report_callback_exception


class _Widget:
    _report_exception = tk.Misc._report_exception

    def __init__(self, root):
        self.root = root

    def _root(self):
        return self.root


def invoke(root, operation):
    return tk.CallWrapper(operation, None, _Widget(root))()


class _DropRoot:
    report_callback_exception = tk.Tk.report_callback_exception
    def __setattr__(self, name, value):
        # Return normally but discard critical safety assignment.
        if name != "report_callback_exception":
            object.__setattr__(self, name, value)


class _RejectRoot:
    report_callback_exception = tk.Tk.report_callback_exception
    def __setattr__(self, name, value):
        if name == "report_callback_exception":
            raise OSError(PRIVATE)
        object.__setattr__(self, name, value)


class _ReadRejectRoot:
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
    def __getattribute__(self, name):
        if name == "report_callback_exception":
            raise OSError(PRIVATE)
        return object.__getattribute__(self, name)


class _FalseReadRoot:
    report_callback_exception = tk.Tk.report_callback_exception
    def __getattribute__(self, name):
        if name == "report_callback_exception":
            return object.__getattribute__(_Root(), "report_callback_exception")
        return object.__getattribute__(self, name)


class CallbackInstallCustodyR268(unittest.TestCase):
    def _blocked(self, root):
        try:
            privacy.install_callback_privacy(root)
        except RuntimeError as error:
            self.assertEqual(str(error), privacy.INSTALL_MESSAGE)
            self.assertIsNone(error.__cause__)
            self.assertIsNone(error.__context__)
        else:
            self.fail("Unverified callback hook unexpectedly accepted")

    def test_assignment_that_raises_private_path_denies_cleanly(self):
        self._blocked(_RejectRoot())

    def test_silent_assignment_discard_denies(self):
        self._blocked(_DropRoot())

    def test_private_readback_exception_denies_cleanly(self):
        self._blocked(_ReadRejectRoot())

    def test_altered_readback_identity_denies(self):
        self._blocked(_FalseReadRoot())

    def test_real_tk_callback_dispatch_remains_safe_for_all_six_app_ids(self):
        for app in APPS:
            with self.subTest(app=app):
                root = _Root()
                dialogs = []
                with mock.patch.object(privacy.messagebox, "showerror", side_effect=lambda *a, **kw: dialogs.append((a,kw))):
                    privacy.install_callback_privacy(root)
                    with contextlib.redirect_stderr(io.StringIO()) as sink:
                        invoke(root, lambda: (_ for _ in ()).throw(OSError(f"{app}: {PRIVATE}")))
                self.assertEqual(sink.getvalue(), "")
                self.assertEqual(len(dialogs), 1)
                self.assertEqual(dialogs[0][0], (privacy.CALLBACK_TITLE, privacy.CALLBACK_MESSAGE))
                self.assertIs(dialogs[0][1]["parent"], root)

    def test_successful_callback_not_modified(self):
        root = _Root()
        privacy.install_callback_privacy(root)
        self.assertEqual(invoke(root, lambda: 14), 14)

    def test_installation_scope_is_one_window(self):
        left, right = _Root(), _Root()
        privacy.install_callback_privacy(left)
        self.assertIn("report_callback_exception", vars(left))
        self.assertNotIn("report_callback_exception", vars(right))

    def test_idempotent_reinstall_remains_protected(self):
        root = _Root()
        privacy.install_callback_privacy(root)
        privacy.install_callback_privacy(root)
        self.assertIn("report_callback_exception", vars(root))

    def test_handler_preserves_human_review_invalidation(self):
        root = _Root()
        selected = ["stale"]
        seen = []
        with mock.patch.object(privacy.messagebox, "showerror", side_effect=lambda *_a, **_k: seen.append(selected[0])):
            privacy.install_callback_privacy(root, invalidate_review=lambda: selected.__setitem__(0, None))
            invoke(root, lambda: (_ for _ in ()).throw(OSError(PRIVATE)))
        self.assertEqual(seen, [None])

    def test_modal_failure_still_uses_constant_fallback(self):
        root = _Root()
        privacy.install_callback_privacy(root)
        with mock.patch.object(privacy.messagebox, "showerror", side_effect=OSError(PRIVATE)):
            with contextlib.redirect_stderr(io.StringIO()) as sink:
                invoke(root, lambda: (_ for _ in ()).throw(ValueError(PRIVATE)))
        self.assertEqual(sink.getvalue(), privacy.FALLBACK_MESSAGE)

    def test_system_exit_is_not_swallowed_during_assignment(self):
        class Interrupt:
            def __setattr__(self, name, value):
                raise SystemExit(7)
        with self.assertRaises(SystemExit) as raised:
            privacy.install_callback_privacy(Interrupt())
        self.assertEqual(raised.exception.code, 7)

    def test_keyboard_interrupt_is_not_swallowed_during_readback(self):
        class Interrupt:
            def __setattr__(self, name, value):
                object.__setattr__(self, name, value)
            def __getattribute__(self, name):
                raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            privacy.install_callback_privacy(Interrupt())


if __name__ == "__main__":
    unittest.main()
