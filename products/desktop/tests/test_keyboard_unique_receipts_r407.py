"""R407: each Tk shortcut must have one unique, bounded callback receipt.

Headless, offline, synthetic Tk adapters only. No customer inputs, money,
premium license change, automated approval, or release artifacts are used.
"""
from __future__ import annotations

import unittest

from fvs_suite.keyboard_access import _verify_callback_ack, install_shortcuts
from test_keyboard_bind_ack_r406 import bind_count
from test_keyboard_staged_activation_r405 import (
    APP_SHAPES, StagedRoot, configuration, operation_total,
)


class ReceiptRoot(StagedRoot):
    """Register a distinct handler but acknowledge with a hostile/misleading ID."""

    def __init__(self, changes=None, **kwargs):
        super().__init__(**kwargs)
        self.changes = dict(changes or {})

    def bind(self, sequence, handler, add=None):
        real_ack = super().bind(sequence, handler, add=add)
        return self.changes.get(self.bind_count, real_ack)


def install(root, parts):
    fields, output, generate, _, options, _ = parts
    return install_shortcuts(root, fields, output, generate, **options)


def assert_inert(test, root, parts):
    before = operation_total(parts)
    for sequence, handler in root.registered:
        with test.subTest(sequence=sequence):
            test.assertEqual(handler(object()), "break")
    test.assertEqual(operation_total(parts), before)


class KeyboardUniqueReceiptPredicateR407(unittest.TestCase):
    def test_native_ascii_ids_are_accepted_once(self):
        seen = set()
        for number in range(1, 25):
            _verify_callback_ack(f"{number}handle", seen)
        self.assertEqual(len(seen), 24)

    def test_reusing_callback_id_fails_without_mutating_seen(self):
        seen = set()
        _verify_callback_ack("123handle", seen)
        with self.assertRaisesRegex(ValueError, "callback ID"):
            _verify_callback_ack("123handle", seen)
        self.assertEqual(seen, {"123handle"})

    def test_invalid_acknowledgements_do_not_change_seen(self):
        seen = {"known"}
        invalid = (None, 0, [], object(), "", " a", "b ", "a b",
                   "\x00", "\x1f", "ab\tc", "ab\nc", "\x7f",
                   "é", "Ａ", "\u200b", "a" * 129)
        for value in invalid:
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(ValueError, "callback ID"):
                    _verify_callback_ack(value, seen)
                self.assertEqual(seen, {"known"})

    def test_printable_ascii_receipt_boundary_is_supported(self):
        seen = set()
        for valid in ("a" * 128, "!", "~", "id-1", "_callback:1"):
            _verify_callback_ack(valid, seen)
        self.assertEqual(len(seen), 5)

    def test_hostile_str_subclass_does_not_run_special_methods(self):
        class Hostile(str):
            def __len__(self):
                raise AssertionError("subclass __len__ must never run")
            def __hash__(self):
                raise AssertionError("subclass __hash__ must never run")
        seen = set()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            _verify_callback_ack(Hostile("123handle"), seen)
        self.assertEqual(seen, set())

    def test_bad_ack_then_good_ack_does_not_poison_id_set(self):
        seen = set()
        for invalid in ("name name", "\r", "\n", "a" * 129, "\u0455"):
            with self.assertRaisesRegex(ValueError, "callback ID"):
                _verify_callback_ack(invalid, seen)
        _verify_callback_ack("good_0001", seen)
        self.assertEqual(seen, {"good_0001"})


class KeyboardUniqueReceiptIntegrationR407(unittest.TestCase):
    def test_duplicate_second_ack_blocks_every_app_shape(self):
        for name, cfg in APP_SHAPES:
            with self.subTest(app=name):
                root, parts = ReceiptRoot({2: "id-1"}), configuration(**cfg)
                with self.assertRaisesRegex(ValueError, "callback ID"):
                    install(root, parts)
                self.assertTrue(root._fvs_shortcuts_installed)
                self.assertEqual(root.bind_count, 2)
                self.assertEqual(root.unbind_count, 1)
                assert_inert(self, root, parts)

    def test_duplicate_final_ack_blocks_every_app_shape(self):
        for name, cfg in APP_SHAPES:
            with self.subTest(app=name):
                final = bind_count(cfg)
                root, parts = ReceiptRoot({final: "id-1"}), configuration(**cfg)
                with self.assertRaisesRegex(ValueError, "callback ID"):
                    install(root, parts)
                self.assertEqual(root.bind_count, final)
                self.assertEqual(root.unbind_count, final - 1)
                assert_inert(self, root, parts)

    def test_later_receipt_can_not_reuse_second_ack(self):
        root, parts = ReceiptRoot({8: "id-2"}), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertEqual(root.bind_count, 8)
        assert_inert(self, root, parts)

    def test_invisible_and_nonascii_receipts_never_activate(self):
        for invalid in ("a b", "\x00", "\n", "a\t", "é", "\u200b", "a" * 129):
            with self.subTest(ack=repr(invalid)):
                root, parts = ReceiptRoot({2: invalid}), configuration()
                with self.assertRaisesRegex(ValueError, "callback ID"):
                    install(root, parts)
                self.assertEqual(root.bind_count, 2)
                assert_inert(self, root, parts)

    def test_reused_receipt_on_generate_action_cannot_invoke_it(self):
        root, parts = ReceiptRoot({10: "id-1"}), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertIn("<Control-Return>", root.handlers)
        assert_inert(self, root, parts)
        self.assertEqual(parts[2].calls, 0)

    def test_reused_receipt_on_premium_review_cannot_invoke_it(self):
        cfg = dict(n=3, premium=True)
        final = bind_count(cfg)
        root, parts = ReceiptRoot({final: "id-1"}), configuration(**cfg)
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertIn("<Alt-Key-r>", root.handlers)
        assert_inert(self, root, parts)
        self.assertEqual(parts[3].calls, 0)

    def test_rollback_failure_retains_only_inert_shortcuts(self):
        root, parts = ReceiptRoot({5: "id-1"}, unbind_error=True), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertEqual(len(root.registered), 5)
        assert_inert(self, root, parts)

    def test_reentrancy_during_rejected_registration_is_inert(self):
        root, parts = ReceiptRoot({7: "id-1"}, reenter=True), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertTrue(root.reentered)
        self.assertTrue(all(item == "break" for item in root.reentered))
        assert_inert(self, root, parts)

    def test_existing_keyboard_bindings_remain_usable(self):
        root, parts = ReceiptRoot({2: "id-1"}, unbind_error=True), configuration()
        old = root.handlers["<F12>"][0][1]
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertIs(root.handlers["<F12>"][0][1], old)
        self.assertEqual(old(object()), "legacy")
        assert_inert(self, root, parts)

    def test_failed_receipt_keeps_same_root_retry_hard_hold(self):
        root, parts = ReceiptRoot({2: "id-1"}), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        before = root.bind_count
        with self.assertRaisesRegex(ValueError, "already installed"):
            install(root, configuration())
        self.assertEqual(root.bind_count, before)

    def test_normal_ids_preserve_generate_access_across_six_apps(self):
        for name, cfg in APP_SHAPES:
            with self.subTest(app=name):
                root, parts = ReceiptRoot(), configuration(**cfg)
                keys = install(root, parts)
                self.assertEqual(len(keys), bind_count(cfg))
                root.handlers["<Control-Return>"][0][1](object())
                self.assertEqual(parts[2].calls, 1)

    def test_normal_ids_preserve_gated_premium_review(self):
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                root, parts = ReceiptRoot(), configuration(3, premium=True)
                parts[3].enabled = enabled
                install(root, parts)
                root.handlers["<Alt-Key-r>"][0][1](object())
                self.assertEqual(parts[3].calls, int(enabled))


if __name__ == "__main__":
    unittest.main()
