"""R46 atomic and snapshot-consistent premium human register exports."""
from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from fvs_suite.review_register import publish_review_register

COLUMNS = (
    "case_id", "source_row", "source_key", "original_flags", "review_state",
    "reviewer", "rationale", "reviewed_utc", "report_sha256",
)


@dataclass(frozen=True)
class Case:
    case_id: str
    report_row: int
    source_key: str
    flags: str


@dataclass(frozen=True)
class Batch:
    product: str
    report_sha256: str
    cases: tuple[Case, ...]


class ReviewRegisterR46(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r46-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.report = self.root / "private-review.csv"
        self.journal = self.root / "private-journal.jsonl"
        self.batch = Batch("grants", "f" * 64, (
            Case("case1", 2, "A-001", "amount_variance"),
            Case("case2", 7, "B-002", "missing_ledger")))
        self.events = [{"case_id": "case1", "decision": "needs_evidence",
                        "reviewer": "Human Reviewer", "rationale": "Need invoice receipt",
                        "created_utc": "2026-10-29T12:00:00+00:00"}]
        self.case_reads = 0
        self.journal_reads = 0
        self.on_case_read = lambda _: None
        self.on_journal_read = lambda _: None

    def cases(self, report, product):
        self.assertEqual(report, self.report)
        self.assertEqual(product, "grants")
        self.case_reads += 1
        self.on_case_read(self.case_reads)
        return self.batch

    def journal_events(self, journal, batch):
        self.assertEqual(journal, self.journal)
        self.assertEqual(batch, self.batch)
        self.journal_reads += 1
        self.on_journal_read(self.journal_reads)
        return list(self.events)

    @staticmethod
    def sanitizing_cell(value):
        text = str(value)
        return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) else text

    def export(self, *, cell=None, folder=None):
        return publish_review_register(
            self.report, "grants", self.journal, self.root if folder is None else folder,
            read_cases=self.cases, read_journal=self.journal_events,
            columns=COLUMNS, cell=self.sanitizing_cell if cell is None else cell)

    def assert_no_staging(self):
        self.assertEqual(list(self.root.glob("*.partial")), [])
        self.assertEqual(list(self.root.glob(".*.partial")), [])

    def assert_no_final(self):
        self.assertEqual(list(self.root.glob("review-register-*.csv")), [])
        self.assert_no_staging()

    def test_two_cases_preserve_exact_fields_and_human_states(self):
        path = self.export()
        self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"))
        with path.open(encoding="utf-8-sig", newline="") as stream:
            fields = list(csv.DictReader(stream))
        self.assertEqual([item["source_row"] for item in fields], ["2", "7"])
        self.assertEqual(fields[0]["review_state"], "needs_evidence")
        self.assertEqual(fields[1]["review_state"], "pending")
        self.assertEqual(fields[0]["reviewer"], "Human Reviewer")
        self.assertEqual(fields[0]["report_sha256"], "f" * 64)
        self.assertEqual(list(fields[0]), list(COLUMNS))
        self.assertEqual((self.case_reads, self.journal_reads), (2, 2))
        self.assert_no_staging()

    def test_all_six_fingerprint_fields_have_deterministic_order(self):
        path = self.export()
        self.assertEqual(path.read_text(encoding="utf-8-sig").splitlines()[0],
                         ",".join(COLUMNS))

    def test_no_decisions_does_not_imply_approval(self):
        self.events.clear()
        path = self.export()
        with path.open(encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
        self.assertTrue(all(item["review_state"] == "pending" for item in rows))
        self.assertTrue(all(not item["reviewer"] for item in rows))

    def test_latest_decision_wins_without_auto_approval(self):
        self.events.append({"case_id": "case1", "decision": "reviewed", "reviewer": "Analyst",
                            "rationale": "Evidence reviewed by human", "created_utc": "2026-10-29T13:00:00+00:00"})
        path = self.export()
        with path.open(encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[0]["review_state"], "reviewed")
        self.assertNotIn("approved", path.read_text(encoding="utf-8-sig"))

    def test_report_changed_after_first_read_blocks_final_publication(self):
        original = self.batch
        self.on_case_read = lambda n: setattr(self, "batch", replace(original, report_sha256="e" * 64)) if n == 2 else None
        with self.assertRaisesRegex(ValueError, "changed during"):
            self.export()
        self.assert_no_final()

    def test_source_case_order_change_blocks_publication(self):
        original = self.batch
        self.on_case_read = lambda n: setattr(self, "batch", replace(original, cases=tuple(reversed(original.cases)))) if n == 2 else None
        with self.assertRaisesRegex(ValueError, "changed during"):
            self.export()
        self.assert_no_final()

    def test_journal_appended_after_first_read_blocks_publication(self):
        extra = {"case_id": "case2", "decision": "escalated", "reviewer": "Human",
                 "rationale": "Additional examination", "created_utc": "2026-10-29T14:00:00+00:00"}
        self.on_journal_read = lambda n: self.events.append(extra) if n == 2 else None
        with self.assertRaisesRegex(ValueError, "changed during"):
            self.export()
        self.assert_no_final()

    def test_rewritten_journal_event_even_same_latest_state_is_rejected(self):
        original = dict(self.events[0])
        def mutate(n):
            if n == 2:
                self.events[0] = {**original, "rationale": "Different immutable history"}
        self.on_journal_read = mutate
        with self.assertRaisesRegex(ValueError, "changed during"):
            self.export()
        self.assert_no_final()

    def test_journal_reordered_while_exporting_is_rejected(self):
        self.events.append({"case_id": "case2", "decision": "escalated", "reviewer": "Analyst",
                            "rationale": "Need follow-up", "created_utc": "2026-10-29T13:00:00+00:00"})
        self.on_journal_read = lambda n: self.events.reverse() if n == 2 else None
        with self.assertRaisesRegex(ValueError, "changed during"):
            self.export()
        self.assert_no_final()

    def test_validation_exception_during_end_check_keeps_no_partial(self):
        def failure(n):
            if n == 2:
                raise ValueError("Corrupt review chain")
        self.on_journal_read = failure
        with self.assertRaisesRegex(ValueError, "Corrupt review chain"):
            self.export()
        self.assert_no_final()

    def test_cell_conversion_failure_does_not_publish_incomplete_csv(self):
        def bad(value):
            if str(value) == "A-001":
                raise ValueError("Cannot serialize")
            return str(value)
        with self.assertRaisesRegex(ValueError, "Cannot serialize"):
            self.export(cell=bad)
        self.assert_no_final()

    def test_csv_formulas_in_source_keys_are_escaped_by_caller_policy(self):
        self.batch = replace(self.batch, cases=(Case("case1", 2, '=HYPERLINK("https://host", "x")', "flag"),))
        path = self.export()
        with path.open(encoding="utf-8-sig") as stream:
            row = next(csv.DictReader(stream))
        self.assertTrue(row["source_key"].startswith("'="))

    def test_invalid_destination_directory_creates_no_final(self):
        with self.assertRaisesRegex(ValueError, "existing output folder"):
            self.export(folder=self.root / "not-a-directory")
        self.assert_no_final()

    def test_old_export_cannot_be_overwritten_when_timestamp_collides(self):
        fixed = datetime(2026, 10, 29, 21, 1, 2, 334455, tzinfo=timezone.utc)
        with patch("fvs_suite.review_register.datetime") as mockdt:
            mockdt.now.return_value = fixed
            first = self.export()
            original = first.read_bytes()
            with self.assertRaises(FileExistsError):
                self.export()
            self.assertEqual(first.read_bytes(), original)
        self.assert_no_staging()

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_preexisting_symlink_not_followed_or_overwritten(self):
        fixed = datetime(2026, 10, 29, 21, 1, 2, 334455, tzinfo=timezone.utc)
        destination = self.root / ("review-register-" + fixed.strftime("%Y%m%d-%H%M%S-%f") + ".csv")
        secret = self.root / "secret-financial.txt"
        secret.write_text("private", encoding="utf-8")
        destination.symlink_to(secret)
        with patch("fvs_suite.review_register.datetime") as mockdt:
            mockdt.now.return_value = fixed
            with self.assertRaises(FileExistsError):
                self.export()
        self.assertTrue(destination.is_symlink())
        self.assertEqual(secret.read_text(), "private")
        self.assert_no_staging()

    def test_empty_exception_queue_still_publishes_headers_only(self):
        self.batch = replace(self.batch, cases=())
        self.events.clear()
        path = self.export()
        self.assertEqual(len(path.read_text(encoding="utf-8-sig").splitlines()), 1)
        self.assertEqual((self.case_reads, self.journal_reads), (2, 2))

    def test_failed_sync_does_not_publish(self):
        with patch("fvs_suite.atomic_reports.os.fsync", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.export()
        self.assert_no_final()

    def test_failed_atomic_publish_does_not_publish(self):
        name = "os.rename" if os.name == "nt" else "os.link"
        with patch("fvs_suite.atomic_reports." + name, side_effect=OSError("no atomic link")):
            with self.assertRaises(OSError):
                self.export()
        self.assert_no_final()

    @unittest.skipIf(os.name == "nt", "POSIX permissions check")
    def test_export_permissions_are_private_on_posix(self):
        path = self.export()
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
