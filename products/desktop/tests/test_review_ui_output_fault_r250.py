"""R250: displayless tests compile real nested Tk callback bodies from review_ui.

These tests require the full repository's real review_ui.py. They are CI-gated,
not a native Windows Tk exercise. All paths and side effects are synthetic.
"""
from __future__ import annotations

import ast
import copy
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
from fvs_suite.review_io import perform_custodied_output

GUI = DESKTOP / "fvs_suite" / "review_ui.py"


class Messages:
    def __init__(self):
        self.errors = []
        self.infos = []

    def showerror(self, title, message, **kwargs):
        self.errors.append((title, message))

    def showinfo(self, title, message, **kwargs):
        self.infos.append((title, message))

    def showwarning(self, *args, **kwargs):
        raise AssertionError("Unexpected missing-selection warning")


class PremiumOutputUiR250Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(GUI.read_text(encoding="utf-8"))
        opener = next(n for n in cls.tree.body
                      if isinstance(n, ast.FunctionDef) and n.name == "open_review_window")
        cls.nested = {n.name: n for n in opener.body if isinstance(n, ast.FunctionDef)}

    def callback(self, name, namespace):
        definition = copy.deepcopy(self.nested[name])
        module = ast.fix_missing_locations(ast.Module(body=[definition], type_ignores=[]))
        exec(compile(module, "<real_review_ui_output_callback>", "exec"), namespace)
        return namespace[name]

    def environment(self, action):
        events = []
        messages = Messages()
        status = SimpleNamespace(set=lambda s: events.append("status:" + s))
        namespace = {
            "selection": SimpleNamespace(batch=SimpleNamespace(report_sha256="synthetic"),
                                          journal=Path("synthetic.review.jsonl"),
                                          report_path=Path("synthetic.csv")),
            "product": "grants", "window": object(),
            "_authorized": lambda: True, "_verify_selected_evidence": lambda: True,
            "_reset_report_view": lambda: events.append("revoke"),
            "perform_custodied_output": perform_custodied_output,
            "export_register": action, "seal_evidence": action, "restore_evidence": action,
            "filedialog": SimpleNamespace(askdirectory=lambda **kw: "synthetic-dir",
                                          askopenfilename=lambda **kw: "synthetic.fvault"),
            "simpledialog": SimpleNamespace(askstring=lambda *args, **kw: "abcdefghijklmnop"),
            "messagebox": messages, "status_text": status,
            "safe_error_message": lambda error, *, operation: "Private-safe validation failure",
        }
        return namespace, events, messages

    def invoke(self, callback_name, action):
        namespace, events, messages = self.environment(action)
        self.callback(callback_name, namespace)()
        return events, messages

    def _fault(self, error):
        def action(*args, **kwargs):
            raise error
        return action

    def _assert_failure(self, callback, error, inspection_term):
        events, messages = self.invoke(callback, self._fault(error))
        self.assertEqual(events, ["revoke"])
        self.assertEqual(len(messages.errors), 1)
        self.assertFalse(messages.infos)
        self.assertIn("Inspect the chosen folder", messages.errors[0][1])
        self.assertIn(inspection_term, messages.errors[0][1])
        self.assertNotIn("PRIVATE_CUSTOMER", repr(messages.errors))

    def test_export_unexpected_fault_scrubs_and_redacts(self):
        self._assert_failure("export", RuntimeError("PRIVATE_CUSTOMER_REPORT"), "incomplete output")

    def test_backup_unexpected_fault_scrubs_and_redacts(self):
        self._assert_failure("seal_archive", RuntimeError("PRIVATE_CUSTOMER_ARCHIVE"), "incomplete archive")

    def test_restore_unexpected_fault_scrubs_and_redacts(self):
        self._assert_failure("restore_archive", RuntimeError("PRIVATE_CUSTOMER_PLAINTEXT"), "incomplete plaintext")

    def test_export_expected_fault_scrubs_and_redacts(self):
        self._assert_failure("export", PermissionError("PRIVATE_CUSTOMER"), "before retrying")

    def test_backup_expected_fault_scrubs_and_redacts(self):
        self._assert_failure("seal_archive", ValueError("PRIVATE_CUSTOMER"), "before retrying")

    def test_restore_expected_fault_scrubs_and_redacts(self):
        self._assert_failure("restore_archive", UnicodeError("PRIVATE_CUSTOMER"), "before retrying")

    def test_export_malformed_success_is_not_reported(self):
        events, messages = self.invoke("export", lambda *a, **kw: None)
        self.assertEqual(events, ["revoke"])
        self.assertEqual(len(messages.errors), 1)
        self.assertFalse(messages.infos)

    def test_backup_malformed_success_is_not_reported(self):
        events, messages = self.invoke("seal_archive", lambda *a, **kw: None)
        self.assertEqual(events, ["revoke"])
        self.assertEqual(len(messages.errors), 1)
        self.assertFalse(messages.infos)

    def test_restore_malformed_success_is_not_reported(self):
        events, messages = self.invoke("restore_archive", lambda *a, **kw: None)
        self.assertEqual(events, ["revoke"])
        self.assertEqual(len(messages.errors), 1)
        self.assertFalse(messages.infos)

    def test_export_success_retains_selection(self):
        events, messages = self.invoke("export", lambda *a, **kw: Path("synthetic-dir/register.csv"))
        self.assertNotIn("revoke", events)
        self.assertEqual(len(messages.infos), 1)
        self.assertFalse(messages.errors)

    def test_backup_success_retains_selection(self):
        events, messages = self.invoke("seal_archive", lambda *a, **kw: Path("synthetic-dir/archive.fvault"))
        self.assertNotIn("revoke", events)
        self.assertEqual(len(messages.infos), 1)
        self.assertFalse(messages.errors)

    def test_restore_success_retains_selection(self):
        events, messages = self.invoke("restore_archive", lambda *a, **kw: Path("synthetic-dir/restored"))
        self.assertNotIn("revoke", events)
        self.assertEqual(len(messages.infos), 1)
        self.assertFalse(messages.errors)


if __name__ == "__main__":
    unittest.main()
