"""R246: premium GUI must never silently auto-open stale exception reports."""
from __future__ import annotations

import ast
from pathlib import Path
import sys
import unittest

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
from fvs_suite.review_target import clear_auto_review_target, watch_auto_review_target


class FakeTkVar:
    """A tiny Tk StringVar trace contract, without requiring a display server."""
    def __init__(self):
        self.traces = []

    def trace_add(self, mode, callback):
        self.traces.append((mode, callback))
        return str(len(self.traces))

    def write(self):
        for mode, callback in self.traces:
            if mode == "write":
                callback("unused", "unused", mode)


class ReportTargetR246Tests(unittest.TestCase):
    def setUp(self):
        self.variables = [FakeTkVar() for _ in range(6)]
        self.slot = [None]

    def test_bind_clears_preexisting_implicit_report(self):
        self.slot[0] = "old-report.csv"
        watch_auto_review_target(self.variables, self.slot)
        self.assertIsNone(self.slot[0])

    def test_each_input_edit_invalidates_report_without_deleting(self):
        watch_auto_review_target(self.variables, self.slot)
        for variable in self.variables:
            self.slot[0] = "previous-report.csv"
            variable.write()
            self.assertIsNone(self.slot[0])

    def test_callback_is_registered_as_write_trace_only(self):
        watch_auto_review_target(self.variables, self.slot)
        self.assertEqual([mode for v in self.variables for mode, _ in v.traces],
                         ["write"] * len(self.variables))

    def test_invalidation_is_idempotent(self):
        watch_auto_review_target(self.variables, self.slot)
        self.variables[0].write()
        self.variables[0].write()
        self.assertEqual(self.slot, [None])

    def test_no_mutation_of_customer_report_content_or_path(self):
        old = "Customer123/2026/financial-exceptions.csv"
        self.slot[0] = old
        watch_auto_review_target(self.variables, self.slot)
        self.assertEqual(old, "Customer123/2026/financial-exceptions.csv")

    def test_failed_attempt_clears_prior_report(self):
        self.slot[0] = "old-report.csv"
        clear_auto_review_target(self.slot)
        self.assertIsNone(self.slot[0])

    def test_success_after_attempt_requires_explicit_new_report_path(self):
        watch_auto_review_target(self.variables, self.slot)
        clear_auto_review_target(self.slot)
        self.assertIsNone(self.slot[0])
        self.slot[0] = "new-report.csv"
        self.assertEqual(self.slot[0], "new-report.csv")

    def test_empty_input_collection_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid premium review inputs"):
            watch_auto_review_target([], self.slot)

    def test_invalid_slot_rejected(self):
        for invalid in ([], ["one", "two"], ("one",), None):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "Invalid premium review target"):
                    clear_auto_review_target(invalid)

    def test_invalid_binding_rejected_without_traces(self):
        with self.assertRaisesRegex(ValueError, "Invalid premium review target"):
            watch_auto_review_target(self.variables, [])
        self.assertTrue(all(not v.traces for v in self.variables))

    def test_bind_does_not_log_report_path(self):
        # Neither callback nor public exceptions should contain a private path.
        self.slot[0] = "CLIENT_462_CONFIDENTIAL.csv"
        watch_auto_review_target(self.variables, self.slot)
        self.assertNotIn("CLIENT_462", str(self.slot))

    def test_report_slot_is_not_replaced_with_false_status(self):
        watch_auto_review_target(self.variables, self.slot)
        self.slot[0] = "report.csv"
        self.variables[-1].write()
        self.assertIsNone(self.slot[0])


if __name__ == "__main__":
    unittest.main()
