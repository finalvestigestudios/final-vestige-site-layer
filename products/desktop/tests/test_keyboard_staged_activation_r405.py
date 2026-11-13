"""R405: callbacks retained after failed Tk registration never run operations.

Headless synthetic roots intentionally inject callbacks before raising. No Tk
window, customer files, network, money processing, or premium entitlement used.
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
    def __init__(self, enabled=True):
        self.calls = 0
        self.enabled = enabled

    def invoke(self):
        if self.enabled:
            self.calls += 1


class StagedRoot:
    """Record callbacks, optionally fail after registration or reenter bind."""

    def __init__(self, *, fail_at=None, error=RuntimeError,
                 fail_before=False, unbind_error=False,
                 missing_id_at=None, reenter=False):
        self.fail_at = fail_at
        self.error = error
        self.fail_before = fail_before
        self.unbind_error = unbind_error
        self.missing_id_at = missing_id_at
        self.reenter = reenter
        self.bind_count = 0
        self.handlers = {"<F12>": [("legacy", lambda _: "legacy")]}
        self.registered = []
        self.reentered = []
        self.unbind_count = 0

    def bind(self, sequence, handler, add=None):
        if add != "+":
            raise AssertionError("preexisting bindings must be preserved")
        self.bind_count += 1
        callback_id = f"id-{self.bind_count}"
        if self.fail_before and self.fail_at == self.bind_count:
            raise self.error("injected failure before bind")
        self.handlers.setdefault(sequence, []).append((callback_id, handler))
        self.registered.append((sequence, handler))
        if self.reenter:
            self.reentered.append(handler(object()))
        if self.fail_at == self.bind_count:
            raise self.error("injected failure after bind")
        return None if self.missing_id_at == self.bind_count else callback_id

    def unbind(self, sequence, callback_id):
        self.unbind_count += 1
        if self.unbind_error:
            raise RuntimeError("injected unbind error")
        self.handlers[sequence] = [
            (i, f) for i, f in self.handlers[sequence] if i != callback_id
        ]
        if not self.handlers[sequence]:
            del self.handlers[sequence]


def configuration(n=1, *, premium=False, ledger=False,
                  invoice=False, policy=False):
    fields = [(Entry(), Button()) for _ in range(n)]
    output = (Entry(), Button())
    generate = Button()
    review = Button() if premium else None
    options = {"review": review}
    optional = []
    if ledger:
        headers = tuple(Entry() for _ in range(4))
        options["ledger_headers"] = headers
        optional.extend(headers)
    if invoice:
        window = Entry()
        options["invoice_window"] = window
        optional.append(window)
    if policy:
        pair = (Entry(), Button())
        options["policy_rules"] = pair
        optional.extend(pair)
    return fields, output, generate, review, options, optional


def operation_total(parts):
    fields, output, generate, review, _, optional = parts
    widgets = [x for pair in (*fields, output) for x in pair]
    widgets += [generate] + ([review] if review else []) + optional
    return sum(getattr(w, "calls", 0) + getattr(w, "focus_count", 0)
               for w in widgets)


APP_SHAPES = (
    ("LedgerDiff Lite", dict(n=2, ledger=True)),
    ("Invoice Twin Scout", dict(n=1, invoice=True)),
    ("SpendMap Lite", dict(n=1)),
    ("Policy Delta Desk", dict(n=2)),
    ("GrantAudit Studio Pro", dict(n=3, premium=True)),
    ("ProcureGuard Studio Pro", dict(n=3, premium=True, policy=True)),
)


class KeyboardStagedActivationR405(unittest.TestCase):
    def run_install(self, root, parts):
        fields, output, generate, _, options, _ = parts
        return install_shortcuts(root, fields, output, generate, **options)

    def assert_all_captured_callbacks_inert(self, root, parts):
        before = operation_total(parts)
        for sequence, callback in root.registered:
            with self.subTest(sequence=sequence):
                self.assertEqual(callback(object()), "break")
        self.assertEqual(operation_total(parts), before)
        self.assertEqual(root.handlers["<F12>"][0][1](object()), "legacy")

    def test_successful_generate_activates_after_full_install(self):
        root, parts = StagedRoot(), configuration()
        keys = self.run_install(root, parts)
        self.assertIn("<Control-Return>", keys)
        self.assertEqual(operation_total(parts), 0)
        root.handlers["<Control-Return>"][0][1](object())
        self.assertEqual(parts[2].calls, 1)

    def test_successful_review_activates_after_full_install(self):
        root, parts = StagedRoot(), configuration(3, premium=True)
        self.run_install(root, parts)
        root.handlers["<Alt-Key-r>"][0][1](object())
        self.assertEqual(parts[3].calls, 1)

    def test_disabled_review_stays_disabled_after_activation(self):
        root, parts = StagedRoot(), configuration(3, premium=True)
        parts[3].enabled = False
        self.run_install(root, parts)
        root.handlers["<Alt-Key-r>"][0][1](object())
        self.assertEqual(parts[3].calls, 0)

    def test_successful_browse_and_focus_work_after_activation(self):
        root, parts = StagedRoot(), configuration()
        self.run_install(root, parts)
        root.handlers["<Alt-Key-1>"][0][1](object())
        root.handlers["<Control-Key-1>"][0][1](object())
        self.assertEqual(parts[0][0][0].focus_count, 1)
        self.assertEqual(parts[0][0][1].calls, 1)

    def test_no_operation_during_registration_even_when_reentered(self):
        root, parts = StagedRoot(reenter=True), configuration(3, premium=True)
        self.run_install(root, parts)
        self.assertTrue(root.reentered)
        self.assertTrue(all(v == "break" for v in root.reentered))
        self.assertEqual(operation_total(parts), 0)
        root.handlers["<Alt-Key-r>"][0][1](object())
        self.assertEqual(parts[3].calls, 1)

    def test_first_callback_orphan_is_inert_after_failure(self):
        root, parts = StagedRoot(fail_at=1), configuration()
        with self.assertRaisesRegex(RuntimeError, "after bind"):
            self.run_install(root, parts)
        self.assert_all_captured_callbacks_inert(root, parts)

    def test_last_generate_orphan_is_inert(self):
        root, parts = StagedRoot(fail_at=10), configuration()
        with self.assertRaises(RuntimeError):
            self.run_install(root, parts)
        self.assertIn("<Control-Return>", root.handlers)
        self.assert_all_captured_callbacks_inert(root, parts)
        self.assertEqual(parts[2].calls, 0)

    def test_last_premium_review_orphan_is_inert(self):
        root, parts = StagedRoot(fail_at=23), configuration(3, premium=True)
        with self.assertRaises(RuntimeError):
            self.run_install(root, parts)
        self.assertIn("<Alt-Key-r>", root.handlers)
        self.assert_all_captured_callbacks_inert(root, parts)
        self.assertEqual(parts[3].calls, 0)

    def test_unbind_errors_leave_orphans_inert(self):
        root, parts = StagedRoot(fail_at=9, unbind_error=True), configuration()
        with self.assertRaisesRegex(RuntimeError, "after bind"):
            self.run_install(root, parts)
        self.assertEqual(len(root.registered), 9)
        self.assertGreater(len(root.handlers), 3)
        self.assert_all_captured_callbacks_inert(root, parts)

    def test_missing_callback_id_then_later_failure_inert(self):
        root, parts = StagedRoot(fail_at=8, missing_id_at=2), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            self.run_install(root, parts)
        self.assertEqual(root.bind_count, 2)
        self.assertIn("<Control-Key-1>", root.handlers)
        self.assert_all_captured_callbacks_inert(root, parts)

    def test_binding_throws_before_any_registration(self):
        root, parts = StagedRoot(fail_at=1, fail_before=True), configuration()
        with self.assertRaises(RuntimeError):
            self.run_install(root, parts)
        self.assertEqual(root.registered, [])
        self.assert_all_captured_callbacks_inert(root, parts)

    def test_keyboard_interrupt_retained_callback_inert(self):
        root, parts = StagedRoot(fail_at=7, error=KeyboardInterrupt), configuration()
        with self.assertRaises(KeyboardInterrupt):
            self.run_install(root, parts)
        self.assert_all_captured_callbacks_inert(root, parts)

    def test_system_exit_retained_callback_inert(self):
        root, parts = StagedRoot(fail_at=8, error=SystemExit), configuration()
        with self.assertRaises(SystemExit):
            self.run_install(root, parts)
        self.assert_all_captured_callbacks_inert(root, parts)

    def test_no_retry_after_failure_even_with_no_remaining_handlers(self):
        root, parts = StagedRoot(fail_at=8, fail_before=True), configuration()
        with self.assertRaises(RuntimeError):
            self.run_install(root, parts)
        count = root.bind_count
        with self.assertRaisesRegex(ValueError, "already installed"):
            self.run_install(root, configuration())
        self.assertEqual(root.bind_count, count)
        self.assert_all_captured_callbacks_inert(root, parts)

    def test_preflight_error_does_not_poison_new_root(self):
        root, parts = StagedRoot(), configuration()
        with self.assertRaises(ValueError):
            install_shortcuts(root, (), parts[1], parts[2])
        self.assertFalse(hasattr(root, "_fvs_shortcuts_installed"))
        self.run_install(root, parts)
        self.assertEqual(root.bind_count, 10)

    def test_all_six_app_shapes_success_then_activation(self):
        for name, cfg in APP_SHAPES:
            with self.subTest(product=name):
                root, parts = StagedRoot(), configuration(**cfg)
                self.run_install(root, parts)
                self.assertEqual(operation_total(parts), 0)
                root.handlers["<Control-Return>"][0][1](object())
                self.assertEqual(parts[2].calls, 1)

    def test_all_six_app_shapes_failure_cannot_invoke_stale_callbacks(self):
        for name, cfg in APP_SHAPES:
            with self.subTest(product=name):
                root, parts = StagedRoot(fail_at=2, unbind_error=True), configuration(**cfg)
                with self.assertRaises(RuntimeError):
                    self.run_install(root, parts)
                self.assert_all_captured_callbacks_inert(root, parts)

    def test_all_six_app_shapes_last_action_failure_is_inert(self):
        for name, cfg in APP_SHAPES:
            with self.subTest(product=name):
                parts = configuration(**cfg)
                # Number of binds = six per source + four common + optional.
                count = 6 * cfg.get("n", 1) + 4
                if cfg.get("ledger"):
                    count += 4
                if cfg.get("invoice"):
                    count += 1
                if cfg.get("policy"):
                    count += 2
                if cfg.get("premium"):
                    count += 1
                root = StagedRoot(fail_at=count)
                with self.assertRaises(RuntimeError):
                    self.run_install(root, parts)
                self.assertEqual(len(root.registered), count)
                self.assert_all_captured_callbacks_inert(root, parts)

    def test_reentrant_callback_at_failing_bind_is_inert(self):
        root, parts = StagedRoot(fail_at=23, reenter=True), configuration(3, premium=True)
        with self.assertRaises(RuntimeError):
            self.run_install(root, parts)
        self.assertTrue(all(v == "break" for v in root.reentered))
        self.assertEqual(operation_total(parts), 0)
        self.assert_all_captured_callbacks_inert(root, parts)

    def test_unrelated_existing_binding_kept_and_active(self):
        root, parts = StagedRoot(fail_at=3, unbind_error=True), configuration()
        old = root.handlers["<F12>"][0][1]
        with self.assertRaises(RuntimeError):
            self.run_install(root, parts)
        self.assertIs(old, root.handlers["<F12>"][0][1])
        self.assertEqual(old(object()), "legacy")
        self.assert_all_captured_callbacks_inert(root, parts)


if __name__ == "__main__":
    unittest.main()
