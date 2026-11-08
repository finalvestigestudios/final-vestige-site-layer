"""R286: atomic single-flight admission under deliberately synchronized races.

The six named configurations use the same per-window gate. These tests do not
invoke Tk on background threads, generate financial files, or approve payment.
"""
from __future__ import annotations

import threading
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


class _RacyReadGate(ActionGate):
    """Force both old check-then-set reads to see idle before either writes.

    The hardened gate never consults _active to decide admission, so it does
    not enter the synthetic barrier. This is a reproducible regression test,
    not a reliance on probabilistic Python thread scheduling.
    """
    def __init__(self):
        super().__init__()
        self._reads = threading.Barrier(2)

    def __getattribute__(self, name):
        if name == "_active" and threading.current_thread() is not threading.main_thread():
            current = object.__getattribute__(self, "__dict__")["_active"]
            if current is False:
                object.__getattribute__(self, "_reads").wait(timeout=2)
            return current
        return object.__getattribute__(self, name)


class AtomicAdmissionR286(unittest.TestCase):
    def check_atomic_contest(self, name, premium):
        gate = _RacyReadGate()
        go = threading.Barrier(3)
        release = threading.Event()
        entered = []
        results = []
        state_lock = threading.Lock()

        def action():
            with state_lock:
                entered.append(name)
            if not release.wait(timeout=4):
                raise RuntimeError("synthetic command hold timed out")

        def worker():
            go.wait(timeout=3)
            result = gate.run(action)
            with state_lock:
                results.append(result)

        threads = [threading.Thread(target=worker, daemon=True) for _ in range(2)]
        for thread in threads:
            thread.start()
        try:
            go.wait(timeout=3)
            # A rejecting thread must finish promptly without waiting for the
            # in-flight action to finish. The other thread remains in action().
            end = threading.Event()
            for _ in range(200):
                with state_lock:
                    if results:
                        end.set()
                        break
                if end.wait(0.005):
                    break
            self.assertTrue(end.is_set(), name + " blocked a rejected command")
            with state_lock:
                self.assertEqual(entered, [name])
                self.assertEqual(results, [False])
        finally:
            release.set()
            for thread in threads:
                thread.join(timeout=3)
        self.assertFalse(any(thread.is_alive() for thread in threads))
        self.assertEqual(sorted(results), [False, True])
        self.assertFalse(gate._active)

    def check_cross_action(self, name, premium):
        gate = ActionGate()
        entered = threading.Event()
        release = threading.Event()
        calls = []
        result = []

        def generate():
            calls.append("generate")
            entered.set()
            if not release.wait(timeout=3):
                raise RuntimeError("synthetic hold timed out")

        thread = threading.Thread(target=lambda: result.append(gate.run(generate)), daemon=True)
        thread.start()
        try:
            self.assertTrue(entered.wait(2))
            rejected = gate.run(lambda: calls.append("review" if premium else "generate-again"))
            self.assertFalse(rejected, name)
            self.assertEqual(calls, ["generate"], name)
        finally:
            release.set()
            thread.join(timeout=3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(result, [True])
        self.assertEqual(calls, ["generate"])
        self.assertTrue(gate.run(lambda: calls.append("review" if premium else "generate-again")))
        self.assertEqual(len(calls), 2, name)

    def check_exception_and_scope(self, name, premium):
        gate = ActionGate()
        second_window = ActionGate()
        with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
            gate.run(lambda: (_ for _ in ()).throw(RuntimeError("synthetic failure")))
        self.assertFalse(gate._active, name)
        observed = []

        def outer():
            self.assertFalse(gate.run(lambda: observed.append("duplicate")))
            self.assertTrue(second_window.run(lambda: observed.append("other window")))
        self.assertTrue(gate.run(outer))
        self.assertEqual(observed, ["other window"], name)
        self.assertTrue(gate.run(lambda: observed.append("retry")))
        self.assertEqual(observed, ["other window", "retry"], name)


for _name, _premium in CASES:
    for _prefix, _method in (("atomic", "check_atomic_contest"),
                             ("cross", "check_cross_action"),
                             ("recovery", "check_exception_and_scope")):
        def _test(self, case=(_name, _premium), method=_method):
            getattr(self, method)(*case)
        setattr(AtomicAdmissionR286, f"test_{_prefix}_{_name}", _test)

if __name__ == "__main__":
    unittest.main(verbosity=2)
