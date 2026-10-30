"""R49 read-after-fsync tests using synthetic, local-only review evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from fvs_suite.review_commit import confirm_review_commit


class ReviewCommitConfirmationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.report = root / "synthetic.csv"
        self.report.write_bytes(b"id,status\nC1,variance\n")
        self.journal = root / "synthetic.jsonl"
        self.original = {"case_id": "C1", "decision": "needs_evidence", "event_hash": "a" * 64}
        self.expected = {"case_id": "C1", "decision": "reviewed", "event_hash": "b" * 64}
        self.history = []
        self.lock_checks = 0
        self.lock_error_on = 0
        self.product = "grants"
        self.write_events([self.expected])

    def write_events(self, events):
        self.journal.write_bytes(b"".join(
            json.dumps(row, sort_keys=True).encode("utf-8") + b"\n" for row in events
        ))

    def read_cases(self, report, product):
        self.assertEqual(product, self.product)
        self.assertEqual(report, self.report)
        return (product, hashlib.sha256(report.read_bytes()).hexdigest())

    def read_journal(self, path, batch):
        self.assertEqual(path, self.journal)
        self.assertEqual(batch, self.read_cases(self.report, self.product))
        raw = path.read_bytes()
        if raw and not raw.endswith(b"\n"):
            raise ValueError("incomplete journal tail")
        return [json.loads(line) for line in raw.splitlines()]

    def owned(self):
        self.lock_checks += 1
        if self.lock_checks == self.lock_error_on:
            raise ValueError("writer lock missing")

    def confirm(self):
        return confirm_review_commit(
            self.report, self.product, self.journal,
            expected_batch=self.read_cases(self.report, self.product),
            previous_events=self.history,
            expected_event=self.expected,
            assert_lock_owned=self.owned,
            read_cases=self.read_cases,
            read_journal=self.read_journal,
        )

    def test_grant_valid_exactly_one_event(self):
        self.confirm()
        self.assertEqual(self.lock_checks, 2)

    def test_procurement_valid_exactly_one_event(self):
        self.product = "procurement"
        self.confirm()
        self.assertEqual(self.lock_checks, 2)

    def test_preserves_all_prior_events(self):
        self.history = [self.original]
        self.write_events([self.original, self.expected])
        self.confirm()

    def test_no_new_event_is_not_success(self):
        self.write_events([])
        with self.assertRaisesRegex(ValueError, "could not be confirmed"):
            self.confirm()

    def test_duplicate_new_event_is_not_success(self):
        self.write_events([self.expected, self.expected])
        with self.assertRaises(ValueError):
            self.confirm()

    def test_extra_event_is_not_success(self):
        self.write_events([self.expected, self.original])
        with self.assertRaises(ValueError):
            self.confirm()

    def test_different_final_decision_is_not_success(self):
        self.write_events([{**self.expected, "decision": "escalated"}])
        with self.assertRaises(ValueError):
            self.confirm()

    def test_same_length_modified_previous_hash_is_rejected(self):
        self.history = [self.original]
        self.write_events([{**self.original, "event_hash": "f" * 64}, self.expected])
        with self.assertRaises(ValueError):
            self.confirm()

    def test_reordered_prior_events_are_rejected(self):
        second = {"case_id": "C2", "event_hash": "c" * 64}
        self.history = [self.original, second]
        self.write_events([second, self.original, self.expected])
        with self.assertRaises(ValueError):
            self.confirm()

    def test_mutated_source_is_rejected(self):
        baseline = self.read_cases(self.report, self.product)
        self.report.write_bytes(b"id,status\nC1,matched\n")
        with self.assertRaisesRegex(ValueError, "source changed"):
            confirm_review_commit(
                self.report, self.product, self.journal,
                expected_batch=baseline, previous_events=self.history,
                expected_event=self.expected, assert_lock_owned=self.owned,
                read_cases=self.read_cases,
                read_journal=self.read_journal,
            )

    def test_lock_lost_before_recheck(self):
        self.lock_error_on = 1
        with self.assertRaisesRegex(ValueError, "lock missing"):
            self.confirm()

    def test_lock_lost_after_recheck(self):
        self.lock_error_on = 2
        with self.assertRaisesRegex(ValueError, "lock missing"):
            self.confirm()

    def test_incomplete_tail_is_rejected(self):
        self.journal.write_bytes(b'{"case_id": "C1"')
        with self.assertRaisesRegex(ValueError, "incomplete journal tail"):
            self.confirm()

    def test_invalid_json_is_rejected(self):
        self.journal.write_bytes(b"not-json\n")
        with self.assertRaises(ValueError):
            self.confirm()

    def test_parsing_failure_remains_fail_closed(self):
        def denied(*args):
            raise PermissionError("private local path omitted")
        with self.assertRaises(PermissionError):
            confirm_review_commit(
                self.report, self.product, self.journal,
                expected_batch=self.read_cases(self.report, self.product),
                previous_events=self.history, expected_event=self.expected,
                assert_lock_owned=self.owned, read_cases=denied,
                read_journal=self.read_journal,
            )

    def test_success_is_read_only(self):
        before_report, before_journal = self.report.read_bytes(), self.journal.read_bytes()
        self.confirm()
        self.assertEqual(self.report.read_bytes(), before_report)
        self.assertEqual(self.journal.read_bytes(), before_journal)


if __name__ == "__main__":
    unittest.main()
