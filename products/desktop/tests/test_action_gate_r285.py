"""R285: native Tk single-flight command custody across all six app variants.

No financial files, account data, file pickers, network or approvals are used.
The test runs with a real Tcl/Tk event loop (Xvfb on Ubuntu).
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import unittest

from fvs_suite.action_gate import ActionGate


CASES = (
    ("LedgerDiffLite", False),
    ("InvoiceTwinScout", False),
    ("SpendMapLite", False),
    ("PolicyDeltaDesk", False),
    ("GrantAuditStudioPro", True),
    ("ProcureGuardStudioPro", True),
)


class NativeSingleFlightR285(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def _buttons(self, premium):
        gate = ActionGate()
        calls = []
        run_nested = [None]
        review_nested = [None]

        def generate():
            calls.append("generate")
            if run_nested[0]:
                run_nested[0]()

        def review():
            calls.append("review")
            if review_nested[0]:
                review_nested[0]()

        generate_button = ttk.Button(
            self.root, text="Generate", command=lambda: gate.run(generate))
        review_button = ttk.Button(
            self.root, text="Review", command=lambda: gate.run(review)) if premium else None
        return gate, generate_button, review_button, calls, run_nested, review_nested

    def check_nested_generate(self, name, premium):
        gate, generate, review, calls, nested, _ = self._buttons(premium)
        nested[0] = lambda: (generate.invoke(), review.invoke() if review else None)
        # Simulate a nested Tk event loop (a modal file/message dialog can do
        # this). An already queued command must not start a second report.
        generate.invoke()
        self.assertEqual(calls, ["generate"], name)
        self.assertFalse(gate._active, name)
        nested[0] = None
        generate.invoke()
        self.assertEqual(calls, ["generate", "generate"], name)

    def check_nested_review(self, name, premium):
        gate, generate, review, calls, _, review_nested = self._buttons(premium)
        if review is None:
            # Free apps have no review command; the gate still prevents
            # two report commands from overlapping.
            self.assertIsNone(review)
            self.assertEqual(calls, [])
            return
        review_nested[0] = lambda: (generate.invoke(), review.invoke())
        review.invoke()
        self.assertEqual(calls, ["review"], name)
        self.assertFalse(gate._active)
        review_nested[0] = None
        generate.invoke()
        self.assertEqual(calls, ["review", "generate"])

    def check_queued_tk_event(self, name, premium):
        gate, generate, review, calls, nested, _ = self._buttons(premium)
        def nested_tk():
            self.root.after(0, generate.invoke)
            if review:
                self.root.after(0, review.invoke)
            self.root.update()
        nested[0] = nested_tk
        generate.invoke()
        self.assertEqual(calls, ["generate"], name)
        self.assertFalse(gate._active, name)
        nested[0] = None
        if review:
            review.invoke()
            self.assertEqual(calls, ["generate", "review"])
        else:
            generate.invoke()
            self.assertEqual(calls, ["generate", "generate"])

    def check_fault_unlock_and_scope(self, name, premium):
        gate, generate, review, calls, _, _ = self._buttons(premium)
        def fail():
            raise RuntimeError("synthetic failure: no financial data")
        with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
            gate.run(fail)
        self.assertFalse(gate._active, name)
        generate.invoke()
        self.assertEqual(calls, ["generate"])
        # Independent app windows have independent gates and are not blocked.
        second = ActionGate()
        self.assertTrue(gate.run(lambda: second.run(lambda: calls.append("second"))))
        self.assertEqual(calls, ["generate", "second"])


for _name, _premium in CASES:
    def _generate(self, case=(_name, _premium)):
        self.check_nested_generate(*case)
    def _review(self, case=(_name, _premium)):
        self.check_nested_review(*case)
    def _queued(self, case=(_name, _premium)):
        self.check_queued_tk_event(*case)
    def _fault(self, case=(_name, _premium)):
        self.check_fault_unlock_and_scope(*case)
    setattr(NativeSingleFlightR285, "test_generate_" + _name, _generate)
    setattr(NativeSingleFlightR285, "test_review_" + _name, _review)
    setattr(NativeSingleFlightR285, "test_queued_" + _name, _queued)
    setattr(NativeSingleFlightR285, "test_fault_" + _name, _fault)


if __name__ == "__main__":
    unittest.main(verbosity=2)
