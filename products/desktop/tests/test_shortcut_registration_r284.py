"""R284: real Tk shortcut install is single-shot and all-or-nothing.

No file dialogs, customer data, network, report output or approval actions.
Runs under Xvfb on Linux and on Windows with a desktop session.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import unittest

from fvs_suite.keyboard_access import install_shortcuts


# Name, source entries, optional controls, binding inventory.
CASES = (
    ("LedgerDiffLite", 2, "ledger", 20),
    ("InvoiceTwinScout", 1, "invoice", 11),
    ("SpendMapLite", 1, "", 10),
    ("PolicyDeltaDesk", 2, "", 16),
    ("GrantAuditStudioPro", 3, "grant", 23),
    ("ProcureGuardStudioPro", 3, "procure", 25),
)


def controls(root, count, optional):
    invoked = []

    def entry():
        w = ttk.Entry(root)
        w.pack()
        return w

    def button(name):
        w = ttk.Button(root, text=name, command=lambda: invoked.append(name))
        w.pack()
        return w

    fields = [(entry(), button(f"browse-{i}")) for i in range(1, count + 1)]
    output = (entry(), button("output-browse"))
    generate = button("generate")
    kw = {}
    if optional == "ledger":
        kw["ledger_headers"] = tuple(entry() for _ in range(4))
    elif optional == "invoice":
        kw["invoice_window"] = entry()
    elif optional == "grant":
        kw["review"] = button("review")
    elif optional == "procure":
        kw["review"] = button("review")
        kw["policy_rules"] = (entry(), button("policy-browse"))
    return fields, output, generate, kw, invoked


def dispatch(root, source, event):
    source.focus_force()
    root.update()
    if root.focus_get() is not source:
        raise AssertionError("Could not establish Tk input focus")
    source.event_generate(event)
    root.update()


class NativeRegistrationR284(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.geometry("650x800")

    def tearDown(self):
        self.root.destroy()

    def check_no_double_bind(self, name, count, optional, expected):
        root = self.root
        fields, output, generate, kw, invoked = controls(root, count, optional)
        sequences = install_shortcuts(root, fields, output, generate, **kw)
        self.assertEqual(len(sequences), expected)
        before = {s: root.bind(s) for s in sequences}
        with self.assertRaisesRegex(ValueError, "already installed"):
            install_shortcuts(root, fields, output, generate, **kw)
        self.assertEqual(before, {s: root.bind(s) for s in sequences})
        dispatch(root, fields[0][0], "<Control-Key-1>")
        dispatch(root, fields[0][0], "<Control-Return>")
        self.assertEqual(invoked, ["browse-1", "generate"], name)
        self.assertFalse(any(v == "review" for v in invoked))

    def check_atomic_failure_and_retry(self, name, count, optional, expected):
        root = self.root
        fields, output, generate, kw, invoked = controls(root, count, optional)
        # A prior app handler must survive rollback (it is NOT ours to remove).
        old_calls = []
        marker_id = root.bind("<Control-Key-1>", lambda _event: old_calls.append("old"), add="+")
        preserved = root.bind("<Control-Key-1>")
        real_bind = root.bind
        attempts = [0]

        def fail_during_install(sequence, handler, add=None):
            attempts[0] += 1
            if attempts[0] == 5:
                raise tk.TclError("synthetic failed registration")
            return real_bind(sequence, handler, add=add)

        root.bind = fail_during_install
        try:
            with self.assertRaises(tk.TclError):
                install_shortcuts(root, fields, output, generate, **kw)
        finally:
            root.bind = real_bind
        self.assertFalse(getattr(root, "_fvs_shortcuts_installed", False))
        self.assertEqual(root.bind("<Control-Key-1>").strip(), preserved.strip())
        self.assertFalse(root.bind("<Alt-Key-1>"))
        self.assertFalse(root.bind("<Alt-Key-KP_1>"))
        self.assertFalse(root.bind("<Control-Key-KP_1>"))
        self.assertEqual(invoked, [])

        sequences = install_shortcuts(root, fields, output, generate, **kw)
        self.assertEqual(len(sequences), expected)
        dispatch(root, fields[0][0], "<Control-Key-1>")
        self.assertEqual(invoked, ["browse-1"], name)
        # Existing handler, which was never destroyed, continues to run.
        self.assertEqual(old_calls, ["old"])
        self.assertIn(marker_id, root.bind("<Control-Key-1>"))


for case in CASES:
    name, count, optional, expected = case
    def _double(self, case=case):
        self.check_no_double_bind(*case)
    def _atomic(self, case=case):
        self.check_atomic_failure_and_retry(*case)
    setattr(NativeRegistrationR284, "test_no_double_" + name, _double)
    setattr(NativeRegistrationR284, "test_atomic_" + name, _atomic)


if __name__ == "__main__":
    unittest.main(verbosity=2)
