"""R70 standalone fingerprint and fail-closed queue regressions."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from fvs_suite.review_identity import require_snapshot_match
from fvs_suite.review_queue_load import ReviewQueue


GOOD = "a" * 64
OTHER = "b" * 64


class ExactFingerprintBinding(unittest.TestCase):
    def test_valid_exact_digest_is_accepted(self):
        self.assertIsNone(require_snapshot_match(GOOD, GOOD))

    def test_legacy_direct_api_opt_out_keeps_existing_contract(self):
        self.assertIsNone(require_snapshot_match(None, "unvalidated direct caller"))

    def test_valid_different_digest_fails_without_exposing_either_digest(self):
        with self.assertRaises(ValueError) as err:
            require_snapshot_match(GOOD, OTHER)
        self.assertNotIn(GOOD, str(err.exception))
        self.assertNotIn(OTHER, str(err.exception))
        self.assertIn("reopen", str(err.exception))

    def test_bad_expected_fingerprints_fail_closed(self):
        values = ("", "a" * 63, "a" * 65, GOOD.upper(), GOOD + "\n", "a" * 63 + "é",
                  " " + GOOD, b"a" * 64, 7, True, [], {}, object())
        for value in values:
            with self.subTest(value_type=type(value).__name__), self.assertRaises(ValueError):
                require_snapshot_match(value, GOOD)

    def test_bad_observed_fingerprints_fail_closed(self):
        for value in ("", OTHER.upper(), "0" * 63, "0" * 65, "0" * 63 + "x", None, False, 9):
            with self.subTest(value_type=type(value).__name__), self.assertRaises(ValueError):
                require_snapshot_match(GOOD, value)

    def test_no_user_data_or_control_codes_in_errors(self):
        secret = "PERSONAL_ACCOUNT_123\n\x1b[31m"
        with self.assertRaises(ValueError) as err:
            require_snapshot_match(secret, GOOD)
        self.assertNotIn("PERSONAL_ACCOUNT", str(err.exception))
        self.assertNotIn("\x1b", str(err.exception))


class SelectedReviewRevalidation(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="fvs-r70-review-")
        self.addCleanup(self.folder.cleanup)
        self.source = Path(self.folder.name) / "report.csv"
        self.queue = ReviewQueue()
        self.snapshot = ("grants", GOOD)
        self.reader = Mock(return_value=self.snapshot)
        self.journal = Mock(return_value={})

    def load(self):
        self.queue.load(self.source, "grants", self.reader, self.journal)
        self.reader.reset_mock()
        self.journal.reset_mock()

    def assert_unloaded(self):
        self.assertIsNone(self.queue.batch)
        self.assertIsNone(self.queue.journal)
        self.assertIsNone(self.queue.report_path)

    def test_empty_selection_rejects_action(self):
        with self.assertRaisesRegex(ValueError, "No verified"):
            self.queue.verify_current("grants", self.reader, self.journal)
        self.reader.assert_not_called()
        self.journal.assert_not_called()

    def test_verified_unchanged_report_rechecks_both_sources(self):
        self.load()
        self.assertEqual(self.queue.verify_current("grants", self.reader, self.journal), self.snapshot)
        self.reader.assert_called_once_with(self.source, "grants")
        self.journal.assert_called_once_with(self.source.with_suffix(".review.jsonl"), self.snapshot)

    def test_replaced_report_fails_closed_before_journal_validation(self):
        self.load()
        self.reader.return_value = ("grants", OTHER)
        with self.assertRaisesRegex(ValueError, "changed"):
            self.queue.verify_current("grants", self.reader, self.journal)
        self.assert_unloaded()
        self.journal.assert_not_called()

    def test_deleted_report_fails_closed(self):
        self.load()
        self.reader.side_effect = OSError("source vanished")
        with self.assertRaises(OSError):
            self.queue.verify_current("grants", self.reader, self.journal)
        self.assert_unloaded()

    def test_invalid_journal_fails_closed(self):
        self.load()
        self.journal.side_effect = ValueError("broken hash chain")
        with self.assertRaisesRegex(ValueError, "broken hash"):
            self.queue.verify_current("grants", self.reader, self.journal)
        self.assert_unloaded()

    def test_unexpected_empty_result_fails_closed(self):
        self.load()
        self.reader.return_value = None
        with self.assertRaises(ValueError):
            self.queue.verify_current("grants", self.reader, self.journal)
        self.assert_unloaded()

    def test_wrong_product_fails_closed_without_accessing_disk(self):
        self.load()
        with self.assertRaises(ValueError):
            self.queue.verify_current("ledger", self.reader, self.journal)
        self.assert_unloaded()
        self.reader.assert_not_called()

    def test_reopen_after_failure_needs_fresh_report_and_journal(self):
        self.load()
        self.reader.return_value = ("grants", OTHER)
        with self.assertRaises(ValueError):
            self.queue.verify_current("grants", self.reader, self.journal)
        self.assert_unloaded()
        self.load()
        self.assertEqual(self.queue.verify_current("grants", self.reader, self.journal),
                         ("grants", OTHER))

    def test_preflight_never_writes_customer_disk(self):
        self.load()
        before = list(Path(self.folder.name).iterdir())
        self.queue.verify_current("grants", self.reader, self.journal)
        self.assertEqual(before, list(Path(self.folder.name).iterdir()))


if __name__ == "__main__":
    unittest.main()
