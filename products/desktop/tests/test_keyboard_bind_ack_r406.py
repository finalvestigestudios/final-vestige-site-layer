"""R406: fail closed when a Tk bind does not acknowledge its callback ID.

All tests are headless synthetic registrations. No money/customer file, GUI,
network call, entitlement change, or automated compliance approval occurs.
"""
from __future__ import annotations

import unittest

from fvs_suite.keyboard_access import install_shortcuts
from test_keyboard_staged_activation_r405 import (
    APP_SHAPES, StagedRoot, configuration, operation_total,
)


class InvalidAcknowledgementRoot(StagedRoot):
    """Can register a callback and then return an invalid acknowledgement."""

    def __init__(self, bad_at, bad_value, **kwargs):
        super().__init__(**kwargs)
        self.bad_at = bad_at
        self.bad_value = bad_value

    def bind(self, sequence, handler, add=None):
        result = super().bind(sequence, handler, add=add)
        if self.bind_count == self.bad_at:
            return self.bad_value
        return result


def install(root, parts):
    fields, output, generate, _, options, _ = parts
    return install_shortcuts(root, fields, output, generate, **options)


def assert_inert(test, root, parts):
    before = operation_total(parts)
    for sequence, handler in root.registered:
        with test.subTest(sequence=sequence):
            test.assertEqual(handler(object()), "break")
    test.assertEqual(operation_total(parts), before)


def bind_count(config):
    count = 6 * config.get("n", 1) + 4
    count += 4 if config.get("ledger") else 0
    count += 1 if config.get("invoice") else 0
    count += 2 if config.get("policy") else 0
    count += 1 if config.get("premium") else 0
    return count


class KeyboardCallbackAcknowledgementR406(unittest.TestCase):

    def test_first_missing_id_fails_closed_for_six_apps(self):
        for app, cfg in APP_SHAPES:
            with self.subTest(app=app):
                root, parts = StagedRoot(missing_id_at=1), configuration(**cfg)
                with self.assertRaisesRegex(ValueError, "callback ID"):
                    install(root, parts)
                self.assertEqual(root.bind_count, 1)
                self.assertTrue(root._fvs_shortcuts_installed)
                assert_inert(self, root, parts)

    def test_second_missing_id_ends_registration_immediately_for_six_apps(self):
        for app, cfg in APP_SHAPES:
            with self.subTest(app=app):
                root, parts = StagedRoot(missing_id_at=2), configuration(**cfg)
                with self.assertRaisesRegex(ValueError, "callback ID"):
                    install(root, parts)
                self.assertEqual(root.bind_count, 2)
                self.assertEqual(root.unbind_count, 1)
                assert_inert(self, root, parts)

    def test_final_missing_id_fails_closed_for_six_apps(self):
        for app, cfg in APP_SHAPES:
            with self.subTest(app=app):
                count = bind_count(cfg)
                root, parts = StagedRoot(missing_id_at=count), configuration(**cfg)
                with self.assertRaisesRegex(ValueError, "callback ID"):
                    install(root, parts)
                self.assertEqual(root.bind_count, count)
                self.assertEqual(root.unbind_count, count - 1)
                assert_inert(self, root, parts)

    def test_empty_string_ack_is_rejected(self):
        root, parts = InvalidAcknowledgementRoot(2, ""), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertEqual(root.bind_count, 2)
        assert_inert(self, root, parts)

    def test_integer_ack_is_rejected(self):
        root, parts = InvalidAcknowledgementRoot(1, 0), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        assert_inert(self, root, parts)

    def test_object_ack_is_rejected(self):
        root, parts = InvalidAcknowledgementRoot(1, object()), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        assert_inert(self, root, parts)

    def test_string_subclass_ack_is_rejected_without_running_custom_code(self):
        class EvilString(str):
            def __bool__(self):
                raise AssertionError("untrusted acknowledgement inspected")
        root, parts = InvalidAcknowledgementRoot(1, EvilString("callback")), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        assert_inert(self, root, parts)

    def test_unbind_failure_does_not_activate_orphan(self):
        root, parts = StagedRoot(missing_id_at=3, unbind_error=True), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertEqual(len(root.registered), 3)
        assert_inert(self, root, parts)

    def test_failed_ack_prevents_any_retry_even_when_cleanup_succeeds(self):
        root, parts = StagedRoot(missing_id_at=3), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        before = root.bind_count
        with self.assertRaisesRegex(ValueError, "already installed"):
            install(root, configuration())
        self.assertEqual(root.bind_count, before)

    def test_successful_str_ack_still_activates_generate(self):
        root, parts = StagedRoot(), configuration()
        keys = install(root, parts)
        self.assertEqual(len(keys), root.bind_count)
        self.assertEqual(operation_total(parts), 0)
        root.handlers["<Control-Return>"][0][1](object())
        self.assertEqual(parts[2].calls, 1)

    def test_successful_str_ack_still_activates_premium_review(self):
        root, parts = StagedRoot(), configuration(3, premium=True)
        install(root, parts)
        root.handlers["<Alt-Key-r>"][0][1](object())
        self.assertEqual(parts[3].calls, 1)

    def test_disabled_premium_review_never_bypassed(self):
        root, parts = StagedRoot(), configuration(3, premium=True)
        parts[3].enabled = False
        install(root, parts)
        root.handlers["<Alt-Key-r>"][0][1](object())
        self.assertEqual(parts[3].calls, 0)

    def test_late_premium_review_missing_id_cannot_execute(self):
        cfg = dict(n=3, premium=True)
        root, parts = StagedRoot(missing_id_at=bind_count(cfg)), configuration(**cfg)
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertIn("<Alt-Key-r>", root.handlers)
        assert_inert(self, root, parts)
        self.assertEqual(parts[3].calls, 0)

    def test_no_operations_even_if_root_reenters_during_failed_registration(self):
        root, parts = StagedRoot(missing_id_at=5, reenter=True), configuration()
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertTrue(root.reentered)
        self.assertTrue(all(value == "break" for value in root.reentered))
        assert_inert(self, root, parts)

    def test_existing_unrelated_binding_remains_usable(self):
        root, parts = StagedRoot(missing_id_at=2, unbind_error=True), configuration()
        before = root.handlers["<F12>"][0][1]
        with self.assertRaisesRegex(ValueError, "callback ID"):
            install(root, parts)
        self.assertIs(root.handlers["<F12>"][0][1], before)
        self.assertEqual(before(object()), "legacy")
        assert_inert(self, root, parts)

    def test_preflight_failure_does_not_mark_attempted(self):
        root, parts = StagedRoot(), configuration()
        with self.assertRaises(ValueError):
            install_shortcuts(root, [], parts[1], parts[2])
        self.assertFalse(hasattr(root, "_fvs_shortcuts_installed"))
        install(root, parts)
        self.assertGreater(root.bind_count, 0)


if __name__ == "__main__":
    unittest.main()
