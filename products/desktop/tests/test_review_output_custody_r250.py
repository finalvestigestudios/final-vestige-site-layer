"""R250: finite, synthetic output custody regressions for the premium UI.

No customer reports, files, network calls or licensed applications are used.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))

from fvs_suite.review_io import perform_custodied_output


class PremiumOutputCustodyR250Tests(unittest.TestCase):
    def setUp(self):
        self.events: list[str] = []

    def revoker(self):
        self.events.append("revoke")

    def action(self, value):
        self.events.append("run")
        return value

    def assert_revoked_once(self):
        self.assertEqual(self.events, ["run", "revoke"])

    def test_valid_path_retained(self):
        result = perform_custodied_output(lambda: self.action(Path("synthetic.csv")), self.revoker)
        self.assertEqual(result, Path("synthetic.csv"))
        self.assertEqual(self.events, ["run"])

    def test_nested_path_retained(self):
        result = perform_custodied_output(lambda: self.action(Path("test-out/archive.fvault")), self.revoker)
        self.assertEqual(result.name, "archive.fvault")
        self.assertEqual(self.events, ["run"])

    def test_null_result_fails_and_revokes(self):
        with self.assertRaises(ValueError):
            perform_custodied_output(lambda: self.action(None), self.revoker)
        self.assert_revoked_once()

    def test_text_result_fails_and_revokes(self):
        with self.assertRaises(ValueError):
            perform_custodied_output(lambda: self.action("synthetic.csv"), self.revoker)
        self.assert_revoked_once()

    def test_empty_path_fails_and_revokes(self):
        with self.assertRaises(ValueError):
            perform_custodied_output(lambda: self.action(Path(".")), self.revoker)
        self.assert_revoked_once()

    def test_os_error_after_write_revokes(self):
        def interrupted():
            self.events.append("run")
            raise OSError("PRIVATE_CUSTOMER_FILENAME")
        with self.assertRaises(OSError):
            perform_custodied_output(interrupted, self.revoker)
        self.assert_revoked_once()

    def test_value_error_revokes(self):
        def interrupted():
            self.events.append("run")
            raise ValueError("PRIVATE_INVOICE_CONTENT")
        with self.assertRaises(ValueError):
            perform_custodied_output(interrupted, self.revoker)
        self.assert_revoked_once()

    def test_unicode_error_revokes(self):
        def interrupted():
            self.events.append("run")
            raise UnicodeError("PRIVATE_UNICODE_CONTENT")
        with self.assertRaises(UnicodeError):
            perform_custodied_output(interrupted, self.revoker)
        self.assert_revoked_once()

    def test_runtime_error_revokes(self):
        def interrupted():
            self.events.append("run")
            raise RuntimeError("PRIVATE_PATH")
        with self.assertRaises(RuntimeError):
            perform_custodied_output(interrupted, self.revoker)
        self.assert_revoked_once()

    def test_type_error_revokes(self):
        def interrupted():
            self.events.append("run")
            raise TypeError("PRIVATE_PATH")
        with self.assertRaises(TypeError):
            perform_custodied_output(interrupted, self.revoker)
        self.assert_revoked_once()

    def test_keyboard_interrupt_revokes_without_swallowing(self):
        def interrupted():
            self.events.append("run")
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            perform_custodied_output(interrupted, self.revoker)
        self.assert_revoked_once()

    def test_system_exit_revokes_without_swallowing(self):
        def interrupted():
            self.events.append("run")
            raise SystemExit()
        with self.assertRaises(SystemExit):
            perform_custodied_output(interrupted, self.revoker)
        self.assert_revoked_once()

    def test_invalid_action_rejected_without_touching_review(self):
        with self.assertRaises(ValueError):
            perform_custodied_output(None, self.revoker)
        self.assertEqual(self.events, [])

    def test_invalid_revoker_rejected_before_side_effect(self):
        with self.assertRaises(ValueError):
            perform_custodied_output(lambda: self.action(Path("synthetic.csv")), None)
        self.assertEqual(self.events, [])

    def test_scrub_failure_does_not_fake_success(self):
        def interrupted():
            self.events.append("run")
            raise RuntimeError("write failed")
        def failed_scrub():
            self.events.append("revoke")
            raise RuntimeError("cannot scrub")
        with self.assertRaisesRegex(RuntimeError, "cannot scrub"):
            perform_custodied_output(interrupted, failed_scrub)
        self.assert_revoked_once()


if __name__ == "__main__":
    unittest.main()
