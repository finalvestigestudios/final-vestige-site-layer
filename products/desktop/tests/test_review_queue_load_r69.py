"""R69 synthetic, headless premium report-switch integrity tests."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from fvs_suite.review_queue_load import ReviewQueue


class ReviewQueueR69(unittest.TestCase):
    def setUp(self):
        self.queue = ReviewQueue()
        self.temp = tempfile.TemporaryDirectory(prefix="fvs-review-r69-")
        self.addCleanup(self.temp.cleanup)
        self.a = Path(self.temp.name) / "first.csv"
        self.b = Path(self.temp.name) / "next.csv"
        self.batch_a = object()
        self.batch_b = object()

    def load_good(self, path=None, batch=None, product="grants"):
        path = self.a if path is None else path
        batch = self.batch_a if batch is None else batch
        reader = Mock(return_value=batch)
        validator = Mock(return_value={})
        self.queue.load(path, product, reader, validator)
        return reader, validator

    def assert_empty(self):
        self.assertIsNone(self.queue.batch)
        self.assertIsNone(self.queue.journal)
        self.assertIsNone(self.queue.report_path)

    def test_initial_queue_has_no_actionable_evidence(self):
        self.assert_empty()

    def test_success_binds_report_and_derived_journal(self):
        reader, validator = self.load_good()
        self.assertIs(self.queue.batch, self.batch_a)
        self.assertEqual(self.queue.report_path, self.a)
        self.assertEqual(self.queue.journal, self.a.with_suffix(".review.jsonl"))
        reader.assert_called_once_with(self.a, "grants")
        validator.assert_called_once_with(self.a.with_suffix(".review.jsonl"), self.batch_a)

    def test_procurement_works_with_the_same_gate(self):
        reader, _ = self.load_good(product="procurement")
        reader.assert_called_once_with(self.a, "procurement")

    def test_second_valid_report_replaces_all_references(self):
        self.load_good()
        self.load_good(self.b, self.batch_b)
        self.assertIs(self.queue.batch, self.batch_b)
        self.assertEqual(self.queue.report_path, self.b)
        self.assertEqual(self.queue.journal, self.b.with_suffix(".review.jsonl"))

    def test_failed_report_read_discards_previous_actionable_queue(self):
        self.load_good()
        def invalid_reader(*_args):
            raise ValueError("sensitive invoice contents")
        with self.assertRaises(ValueError):
            self.queue.load(self.b, "grants", invalid_reader, lambda *_: None)
        self.assert_empty()

    def test_failed_journal_validation_discards_previous_queue(self):
        self.load_good()
        def invalid_journal(*_args):
            raise ValueError("corrupt journal")
        with self.assertRaises(ValueError):
            self.queue.load(self.b, "grants", lambda *_: self.batch_b, invalid_journal)
        self.assert_empty()

    def test_failed_journal_validation_never_publishes_new_batch(self):
        def inspect_not_committed(_journal, _batch):
            self.assert_empty()
            raise ValueError("not authorized")
        with self.assertRaises(ValueError):
            self.queue.load(self.a, "grants", lambda *_: self.batch_a, inspect_not_committed)
        self.assert_empty()

    def test_success_is_unpublished_until_journal_verification_finishes(self):
        def inspect_then_succeed(_journal, _batch):
            self.assert_empty()
        self.queue.load(self.a, "grants", lambda *_: self.batch_a, inspect_then_succeed)
        self.assertIs(self.queue.batch, self.batch_a)

    def test_none_batch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "no review batch"):
            self.queue.load(self.a, "grants", lambda *_: None, Mock())
        self.assert_empty()

    def test_manual_clear_discards_every_reference(self):
        self.load_good()
        self.queue.clear()
        self.assert_empty()
        self.queue.clear()
        self.assert_empty()

    def test_bad_product_fails_closed_and_skips_callbacks(self):
        self.load_good()
        reader = Mock()
        validator = Mock()
        with self.assertRaises(ValueError):
            self.queue.load(self.b, "ledger", reader, validator)
        self.assert_empty()
        reader.assert_not_called()
        validator.assert_not_called()

    def test_missing_path_fails_closed(self):
        self.load_good()
        for value in ("", "   ", None, 23):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.queue.load(value, "grants", Mock(), Mock())
            self.assert_empty()

    def test_path_object_references_are_not_exposed_by_value_errors(self):
        self.load_good()
        secret = "/financial/PRIVATE-VENDOR-ACCOUNT.csv"
        for value in ("", None, object()):
            try:
                self.queue.load(value, "grants", Mock(), Mock())
            except ValueError as exc:
                self.assertNotIn(secret, str(exc))
        self.assert_empty()

    def test_no_disk_writes_from_state_transitions(self):
        before = list(Path(self.temp.name).iterdir())
        self.load_good()
        self.queue.clear()
        self.assertEqual(before, list(Path(self.temp.name).iterdir()))

    def test_repeated_success_after_failure_restores_only_new_evidence(self):
        self.load_good()
        with self.assertRaises(ValueError):
            self.queue.load(self.b, "grants", lambda *_: self.batch_b,
                            lambda *_: (_ for _ in ()).throw(ValueError("bad journal")))
        self.assert_empty()
        self.load_good(self.b, self.batch_b)
        self.assertIs(self.queue.batch, self.batch_b)
        self.assertEqual(self.queue.report_path, self.b)


if __name__ == "__main__":
    unittest.main()
