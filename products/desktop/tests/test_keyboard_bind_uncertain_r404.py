"""R404: unknown Tk bind side effects must block every subsequent install.

Uses synthetic Tk roots only. Tests preserve premium command handlers without
reading files, starting Tk, or accessing customer data or a network.
"""
from __future__ import annotations

import unittest

from fvs_suite.keyboard_access import install_shortcuts


class Entry:
    def __init__(self):
        self.focus_count = 0

    def focus_set(self):
        self.focus_count += 1


class Button:
    def __init__(self, command=None, enabled=True):
        self.invoked = 0
        self.command = command
        self.enabled = enabled

    def invoke(self):
        if self.enabled:
            self.invoked += 1
            if self.command:
                self.command()


class UncertainRoot:
    """Optionally creates a binding and then raises without returning its ID."""

    def __init__(self, fail_at=None, error_type=RuntimeError,
                 mutate_before_failure=True, unbind_failure=False,
                 missing_id_at=None):
        self.handlers = {"<F12>": [("preexisting", lambda _: "kept")]}
        self.fail_at = fail_at
        self.error_type = error_type
        self.mutate_before_failure = mutate_before_failure
        self.unbind_failure = unbind_failure
        self.missing_id_at = missing_id_at
        self.bind_calls = 0
        self.unbind_calls = []

    def bind(self, key, handler, add=None):
        if add != "+":
            raise AssertionError("Existing Tk handlers must remain intact")
        self.bind_calls += 1
        callback_id = f"r404-{self.bind_calls}"
        if self.fail_at == self.bind_calls and not self.mutate_before_failure:
            raise self.error_type("simulated Tk callback registration failure")
        self.handlers.setdefault(key, []).append((callback_id, handler))
        if self.fail_at == self.bind_calls:
            raise self.error_type("simulated post-registration failure")
        return None if self.missing_id_at == self.bind_calls else callback_id

    def unbind(self, key, callback_id):
        self.unbind_calls.append((key, callback_id))
        if self.unbind_failure:
            raise RuntimeError("simulated Tk unbind failure")
        existing = self.handlers[key]
        matching = [pair for pair in existing if pair[0] == callback_id]
        if len(matching) != 1:
            raise AssertionError("No matching callback ID")
        self.handlers[key] = [pair for pair in existing if pair[0] != callback_id]
        if not self.handlers[key]:
            del self.handlers[key]


def controls(count, *, premium=False):
    fields = [(Entry(), Button()) for _ in range(count)]
    output = (Entry(), Button())
    generate = Button()
    review = Button() if premium else None
    return fields, output, generate, review


class UncertainRegistrationR404(unittest.TestCase):
    def install(self, root, count=3, *, premium=False, **kwargs):
        fields, output, generate, review = controls(count, premium=premium)
        sequences = install_shortcuts(
            root, fields, output, generate, review=review, **kwargs
        )
        return sequences, fields, output, generate, review

    def assert_hard_hold(self, root, count=3, premium=False, **kwargs):
        before = root.bind_calls
        with self.assertRaisesRegex(ValueError, "already installed"):
            self.install(root, count, premium=premium, **kwargs)
        self.assertEqual(root.bind_calls, before)
        self.assertEqual(root.handlers["<F12>"][0][0], "preexisting")

    def test_successful_free_install(self):
        root = UncertainRoot()
        keys, fields, output, generate, _ = self.install(root, 1)
        self.assertEqual(len(keys), 10)
        self.assertEqual(root.handlers["<Control-Return>"][0][1](None), "break")
        self.assertEqual(generate.invoked, 1)
        self.assertEqual(fields[0][0].focus_count, 0)
        self.assert_hard_hold(root, 1)

    def test_successful_premium_uses_existing_review_command(self):
        root = UncertainRoot()
        _, _, _, _, review = self.install(root, 3, premium=True)
        self.assertEqual(root.handlers["<Alt-Key-r>"][0][1](None), "break")
        self.assertEqual(review.invoked, 1)
        self.assert_hard_hold(root, 3, premium=True)

    def test_premium_disabled_review_stays_disabled(self):
        root = UncertainRoot()
        fields, output, generate, review = controls(3, premium=True)
        review.enabled = False
        review.command = lambda: self.fail("premium approval bypassed")
        install_shortcuts(root, fields, output, generate, review=review)
        root.handlers["<Alt-Key-r>"][0][1](None)
        self.assertEqual(review.invoked, 0)

    def test_early_binding_failure_without_side_effect_still_holds(self):
        root = UncertainRoot(fail_at=1, mutate_before_failure=False)
        with self.assertRaisesRegex(RuntimeError, "registration failure"):
            self.install(root, 1)
        self.assertEqual(set(root.handlers), {"<F12>"})
        self.assert_hard_hold(root, 1)

    def test_first_binding_mutates_then_raises(self):
        root = UncertainRoot(fail_at=1)
        with self.assertRaisesRegex(RuntimeError, "post-registration"):
            self.install(root, 1)
        self.assertIn("<Alt-Key-1>", root.handlers)
        self.assertEqual(root.unbind_calls, [])
        self.assert_hard_hold(root, 1)

    def test_second_binding_mutates_then_raises(self):
        root = UncertainRoot(fail_at=2)
        with self.assertRaisesRegex(RuntimeError, "post-registration"):
            self.install(root, 1)
        self.assertNotIn("<Alt-Key-1>", root.handlers)  # known ID rolled back
        self.assertIn("<Control-Key-1>", root.handlers)  # unknown ID retained
        self.assertEqual(len(root.unbind_calls), 1)
        self.assert_hard_hold(root, 1)

    def test_middle_binding_mutates_then_raises(self):
        root = UncertainRoot(fail_at=9)
        with self.assertRaises(RuntimeError):
            self.install(root, 2)
        self.assertEqual(len(root.unbind_calls), 8)
        self.assert_hard_hold(root, 2)

    def test_final_generate_binding_mutates_then_raises(self):
        root = UncertainRoot(fail_at=10)
        with self.assertRaises(RuntimeError):
            self.install(root, 1)
        self.assertIn("<Control-Return>", root.handlers)
        self.assert_hard_hold(root, 1)

    def test_final_premium_review_binding_mutates_then_raises(self):
        root = UncertainRoot(fail_at=23)
        with self.assertRaises(RuntimeError):
            self.install(root, 3, premium=True)
        self.assertIn("<Alt-Key-r>", root.handlers)
        self.assert_hard_hold(root, 3, premium=True)

    def test_keyboard_interrupt_mid_bind_keeps_hold(self):
        root = UncertainRoot(fail_at=4, error_type=KeyboardInterrupt)
        with self.assertRaises(KeyboardInterrupt):
            self.install(root, 1)
        self.assertEqual(len(root.unbind_calls), 3)
        self.assert_hard_hold(root, 1)

    def test_system_exit_mid_bind_keeps_hold(self):
        root = UncertainRoot(fail_at=2, error_type=SystemExit)
        with self.assertRaises(SystemExit):
            self.install(root, 2)
        self.assertEqual(len(root.unbind_calls), 1)
        self.assert_hard_hold(root, 2)

    def test_failure_before_registration_rolls_back_known_ids(self):
        root = UncertainRoot(fail_at=8, mutate_before_failure=False)
        with self.assertRaises(RuntimeError):
            self.install(root, 1)
        self.assertEqual(set(root.handlers), {"<F12>"})
        self.assertEqual(len(root.unbind_calls), 7)
        self.assert_hard_hold(root, 1)

    def test_unbind_failure_does_not_replace_original_exception(self):
        root = UncertainRoot(fail_at=5, unbind_failure=True)
        with self.assertRaisesRegex(RuntimeError, "post-registration"):
            self.install(root, 1)
        self.assertGreater(len(root.handlers), 2)
        self.assert_hard_hold(root, 1)

    def test_unknown_callback_id_cannot_be_removed_after_later_failure(self):
        root = UncertainRoot(fail_at=4, missing_id_at=2)
        with self.assertRaisesRegex(ValueError, "callback ID"):
            self.install(root, 1)
        self.assertEqual(root.bind_calls, 2)
        self.assertIn("<Control-Key-1>", root.handlers)
        self.assert_hard_hold(root, 1)

    def test_preserves_preexisting_unrelated_binding(self):
        root = UncertainRoot(fail_at=3)
        old = root.handlers["<F12>"][0][1]
        with self.assertRaises(RuntimeError):
            self.install(root, 1)
        self.assertIs(root.handlers["<F12>"][0][1], old)
        self.assertEqual(old(None), "kept")

    def test_preflight_failure_does_not_touch_root(self):
        root = UncertainRoot()
        with self.assertRaises(ValueError):
            self.install(root, 4)
        self.assertFalse(hasattr(root, "_fvs_shortcuts_installed"))
        self.assertEqual(root.bind_calls, 0)

    def test_bad_premium_review_does_not_register(self):
        root = UncertainRoot()
        fields, output, generate, _ = controls(3)
        with self.assertRaises(ValueError):
            install_shortcuts(root, fields, output, generate, review=object())
        self.assertEqual(root.bind_calls, 0)
        self.assertFalse(hasattr(root, "_fvs_shortcuts_installed"))

    def test_all_six_control_shapes_success(self):
        cases = (
            ("LedgerDiff Lite", 2, {"ledger_headers": tuple(Entry() for _ in range(4))}),
            ("Invoice Twin Scout", 1, {"invoice_window": Entry()}),
            ("SpendMap Lite", 1, {}),
            ("Policy Delta Desk", 2, {}),
            ("GrantAudit Studio Pro", 3, {"premium": True}),
            ("ProcureGuard Studio Pro", 3, {"premium": True, "policy_rules": (Entry(), Button())}),
        )
        for name, n, options in cases:
            with self.subTest(product=name):
                root = UncertainRoot()
                keys, *_ = self.install(root, n, **options)
                self.assertTrue(root._fvs_shortcuts_installed)
                self.assertEqual(len(keys), root.bind_calls)
                self.assert_hard_hold(root, n, **options)

    def test_all_six_control_shapes_partial_failure_holds(self):
        cases = (
            ("LedgerDiff Lite", 2, {"ledger_headers": tuple(Entry() for _ in range(4))}),
            ("Invoice Twin Scout", 1, {"invoice_window": Entry()}),
            ("SpendMap Lite", 1, {}),
            ("Policy Delta Desk", 2, {}),
            ("GrantAudit Studio Pro", 3, {"premium": True}),
            ("ProcureGuard Studio Pro", 3, {"premium": True, "policy_rules": (Entry(), Button())}),
        )
        for name, n, options in cases:
            with self.subTest(product=name):
                root = UncertainRoot(fail_at=2)
                with self.assertRaises(RuntimeError):
                    self.install(root, n, **options)
                self.assert_hard_hold(root, n, **options)


if __name__ == "__main__":
    unittest.main()
