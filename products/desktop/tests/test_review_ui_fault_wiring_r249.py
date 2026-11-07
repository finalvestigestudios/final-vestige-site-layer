"""R249: execute GUI evidence-error handlers extracted from the real Tk source.

The preflight is displayless. No Windows UI, customer report or entitlement is
needed. It tests the actual nested function body, not a hand-copied surrogate.
"""
from __future__ import annotations

import ast
import copy
from pathlib import Path
import unittest


GUI = Path(__file__).resolve().parents[1] / "fvs_suite" / "review_ui.py"


class Messages:
    def __init__(self):
        self.errors = []

    def showerror(self, title, message, **kwargs):
        self.errors.append((title, message, kwargs))


class PremiumGuiFailureR249Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = GUI.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.opener = next(n for n in cls.tree.body if
                          isinstance(n, ast.FunctionDef) and n.name == "open_review_window")
        cls.nested = {n.name: n for n in cls.opener.body if
                      isinstance(n, ast.FunctionDef)}

    def function(self, name, namespace):
        statement = copy.deepcopy(self.nested[name])
        module = ast.fix_missing_locations(ast.Module(body=[statement], type_ignores=[]))
        exec(compile(module, "<real_review_ui_nested_function>", "exec"), namespace)
        return namespace[name]

    def environment(self, selection):
        events = []
        messages = Messages()
        namespace = {
            "selection": selection, "product": "grants",
            "read_cases": lambda *_: object(), "latest_states": lambda *_: {},
            "_reset_report_view": lambda: events.append("scrub"),
            "messagebox": messages, "window": object(),
            "safe_error_message": lambda *_args, **_kw: "Private-safe validation failure",
            "_authorized": lambda: True,
        }
        return namespace, events, messages

    def test_unexpected_source_error_scrubs_and_does_not_leak(self):
        class Fault:
            def verify_current(self, *_):
                raise RuntimeError("PRIVATE_CUSTOMER_AND_DIRECTORY")
        namespace, events, messages = self.environment(Fault())
        result = self.function("_verify_selected_evidence", namespace)()
        self.assertFalse(result)
        self.assertEqual(events, ["scrub"])
        self.assertEqual(len(messages.errors), 1)
        self.assertNotIn("PRIVATE_CUSTOMER", repr(messages.errors))
        self.assertIn("cleared", messages.errors[0][1])

    def test_unexpected_journal_error_scrubs_and_does_not_leak(self):
        class Fault:
            def verify_current(self, *_):
                raise TypeError("SECRET_JOURNAL_PATH")
        namespace, events, messages = self.environment(Fault())
        result = self.function("_verify_selected_evidence", namespace)()
        self.assertFalse(result)
        self.assertEqual(events, ["scrub"])
        self.assertNotIn("SECRET_JOURNAL", repr(messages.errors))

    def test_expected_evidence_fault_still_uses_safe_message(self):
        class Fault:
            def verify_current(self, *_):
                raise ValueError("SENSITIVE_CSV_PATH")
        namespace, events, messages = self.environment(Fault())
        self.assertFalse(self.function("_verify_selected_evidence", namespace)())
        self.assertEqual(events, ["scrub"])
        self.assertEqual(messages.errors[0][1], "Private-safe validation failure")

    def test_valid_evidence_keeps_existing_review(self):
        class Valid:
            def verify_current(self, *_):
                return object()
        namespace, events, messages = self.environment(Valid())
        self.assertTrue(self.function("_verify_selected_evidence", namespace)())
        self.assertFalse(events)
        self.assertFalse(messages.errors)

    def test_unexpected_load_error_clears_before_return_and_redacts(self):
        class Fault:
            def load(self, *_):
                raise RuntimeError("PRIVATE_LICENSE_AND_REPORT")
        namespace, events, messages = self.environment(Fault())
        self.assertIsNone(self.function("load_report", namespace)("synthetic.csv"))
        self.assertEqual(events, ["scrub", "scrub"])
        self.assertEqual(len(messages.errors), 1)
        self.assertNotIn("PRIVATE_LICENSE", repr(messages.errors))

    def test_unexpected_display_error_clears_queue_and_redacts(self):
        class Loaded:
            report_path = Path("synthetic.csv")
            def load(self, *_):
                return None
        class ReportText:
            def set(self, value):
                self.value = value
        namespace, events, messages = self.environment(Loaded())
        namespace["display"] = lambda: (_ for _ in ()).throw(
            RuntimeError("SECRET_ROW_REFERENCE"))
        namespace["report_text"] = ReportText()
        self.assertIsNone(self.function("load_report", namespace)("synthetic.csv"))
        self.assertEqual(events, ["scrub", "scrub"])
        self.assertNotIn("SECRET_ROW", repr(messages.errors))
        self.assertEqual(len(messages.errors), 1)

    def test_unexpected_post_append_handler_requires_journal_inspection(self):
        review = self.nested["log_review"]
        handlers = [node for node in ast.walk(review) if isinstance(node, ast.ExceptHandler)
                    and isinstance(node.type, ast.Name) and node.type.id == "Exception"]
        self.assertEqual(len(handlers), 1)
        body = ast.get_source_segment(self.source, handlers[0])
        self.assertIn("_reset_report_view()", body)
        self.assertIn("Inspect the local review journal", body)
        self.assertNotIn("str(exc)", body)
        self.assertNotIn("safe_error_message(exc", body)


if __name__ == "__main__":
    unittest.main()
