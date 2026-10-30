"""R70 actual atomic-writer register integration with synthetic private reports."""
from __future__ import annotations

import csv
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import Mock

from fvs_suite.review_register import publish_review_register

GOOD = "a" * 64
OTHER = "b" * 64
COLS = ("case_id", "source_row", "source_key", "original_flags", "review_state",
        "reviewer", "rationale", "reviewed_utc", "report_sha256")


@dataclass(frozen=True)
class Case:
    case_id: str
    report_row: int
    source_key: str
    flags: str


@dataclass(frozen=True)
class Batch:
    report_sha256: str
    cases: tuple[Case, ...]


class RegisterBindingR70(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="fvs-r70-register-")
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.old = Batch(GOOD, (Case("id-1", 7, "PO-1", "amount-review"),))
        self.new = Batch(OTHER, (Case("id-2", 10, "PO-2", "missing-receipt"),))
        self.reader = Mock(return_value=self.old)
        self.journal = Mock(return_value=[])

    def publish(self, expected=GOOD):
        return publish_review_register(self.root / "source.csv", "procurement",
                                       self.root / "source.review.jsonl", self.root,
                                       read_cases=self.reader, read_journal=self.journal,
                                       columns=COLS, cell=str,
                                       expected_report_sha256=expected)

    def assert_no_output(self):
        self.assertEqual([], list(self.root.iterdir()))

    def test_exact_selected_report_publishes_one_complete_register(self):
        path = self.publish()
        self.assertTrue(path.is_file())
        with path.open(encoding="utf-8-sig", newline="") as inp:
            rows = list(csv.DictReader(inp))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["report_sha256"], GOOD)
        self.assertEqual(rows[0]["source_row"], "7")
        self.assertEqual(self.reader.call_count, 2)
        self.assertEqual(self.journal.call_count, 2)
        self.assertFalse(list(self.root.glob("*.partial")))

    def test_replaced_report_before_start_refuses_publication(self):
        self.reader.return_value = self.new
        with self.assertRaisesRegex(ValueError, "reopen"):
            self.publish()
        self.assert_no_output()
        self.journal.assert_not_called()

    def test_replaced_report_during_staging_refuses_publication(self):
        self.reader.side_effect = [self.old, self.new]
        with self.assertRaisesRegex(ValueError, "reopen"):
            self.publish()
        self.assert_no_output()
        self.assertEqual(self.reader.call_count, 2)

    def test_same_report_but_modified_journal_fails_atomic_publication(self):
        self.journal.side_effect = [[], [{"case_id": "id-1", "decision": "reviewed"}]]
        with self.assertRaisesRegex(ValueError, "changed"):
            self.publish()
        self.assert_no_output()

    def test_malformed_loaded_fingerprint_refuses_before_journal_read(self):
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.publish(GOOD.upper())
        self.assert_no_output()
        self.journal.assert_not_called()

    def test_legacy_caller_without_expected_digest_preserves_backward_compat(self):
        self.reader.return_value = self.new
        path = self.publish(None)
        with path.open(encoding="utf-8-sig", newline="") as inp:
            rows = list(csv.DictReader(inp))
        self.assertEqual(rows[0]["report_sha256"], OTHER)

    def test_presented_report_journal_state_retained_only_when_consistent(self):
        event = {"case_id": "id-1", "decision": "needs_evidence", "reviewer": "AB",
                 "rationale": "Documentation needed", "created_utc": "2026-10-30T00:00:00+00:00"}
        self.journal.return_value = [event]
        path = self.publish()
        with path.open(encoding="utf-8-sig", newline="") as inp:
            row = next(csv.DictReader(inp))
        self.assertEqual(row["review_state"], "needs_evidence")
        self.assertEqual(row["reviewer"], "AB")
        self.assertEqual(row["rationale"], "Documentation needed")


if __name__ == "__main__":
    unittest.main()
