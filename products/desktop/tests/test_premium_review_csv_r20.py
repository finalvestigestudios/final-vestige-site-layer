"""R20: premium human review must cite physical CSV lines and fail closed on damaged reports."""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import exception_review as review


class PremiumReviewCsvR20Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-review-csv-r20-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.report = self.root / "review-source.csv"
        self.journal = self.root / "human-review.jsonl"

    def write(self, fields, rows):
        with self.report.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            writer.writerows(rows)

    def cases(self, product="grants"):
        return review.read_cases(self.report, product)

    def test_ordinary_case_id_remains_stable(self):
        self.write(("id", "status"), (("A", "variance"), ("B", "matched"), ("C", "review")))
        batch = self.cases()
        self.assertEqual([c.report_row for c in batch.cases], [2, 4])
        expected = hashlib.sha256(
            f"FVS-CASE-v1|grants|{batch.report_sha256}|2".encode("ascii")
        ).hexdigest()
        self.assertEqual(batch.cases[0].case_id, expected)

    def test_multiline_grant_status_and_blank_line_track_physical_rows(self):
        self.write(("id", "status", "memo"),
                   (("A", "variance", "first\nsecond"), (),
                    ("B", "needs_evidence", "ok")))
        self.assertEqual([c.report_row for c in self.cases().cases], [2, 5])

    def test_multiline_header_shifts_first_record(self):
        self.write(("id", "status", "notes\nmetadata"), (("A", "variance", "note"),))
        self.assertEqual(self.cases().cases[0].report_row, 3)

    def test_procurement_multiline_physical_rows(self):
        self.write(("po", "line", "status", "memo"),
                   (("A", "1", "variance", "first\nsecond"), (),
                    ("B", "2", "review", "ok")))
        batch = self.cases("procurement")
        self.assertEqual([c.report_row for c in batch.cases], [2, 5])
        self.assertEqual(batch.cases[1].source_key, "B / 2")

    def test_blank_lines_skip_without_shifting_source_references(self):
        self.write(("id", "status"),
                   ((), (), ("A", "variance"), (), ("B", "review")))
        self.assertEqual([c.report_row for c in self.cases().cases], [4, 6])

    def test_truncated_row_rejected_before_review_queue(self):
        self.write(("id", "status", "notes"), (("A", "variance"),))
        with self.assertRaisesRegex(ValueError, "expected 3 columns, got 2"):
            self.cases()

    def test_extra_columns_rejected_before_review_queue(self):
        self.write(("id", "status"), (("A", "variance", "unexpected"),))
        with self.assertRaisesRegex(ValueError, "expected 2 columns, got 3"):
            self.cases()

    def test_unterminated_quote_fails_closed(self):
        self.report.write_text('id,status\nA,"variance', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Malformed CSV quoting"):
            self.cases()

    def test_invalid_character_after_closing_quote_fails_closed(self):
        self.report.write_text('id,status\nA,"variance"garbage\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Malformed CSV quoting"):
            self.cases()

    def test_duplicate_normalized_header_rejected(self):
        self.write(("id", "Status", "status"), (("A", "review", "matched"),))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.cases()

    def test_blank_identifier_rejected(self):
        self.write(("id", "status"), (("", "variance"),))
        with self.assertRaisesRegex(ValueError, "Missing identifier"):
            self.cases()

    def test_blank_status_rejected(self):
        self.write(("id", "status"), (("A", ""),))
        with self.assertRaisesRegex(ValueError, "Missing status"):
            self.cases()

    def test_later_malformed_row_invalidates_entire_queue(self):
        self.write(("id", "status"),
                   (("A", "variance"), ("B", "review", "extra")))
        with self.assertRaisesRegex(ValueError, "physical line 3"):
            self.cases()

    def test_utf8_bom_and_crlf_still_supported(self):
        self.write(("id", "status"), (("A", "review"),))
        self.assertEqual(self.cases().cases[0].report_row, 2)

    def test_bad_width_in_matched_row_is_not_ignored(self):
        self.write(("id", "status"), (("A", "matched", "smuggled"),))
        with self.assertRaisesRegex(ValueError, "expected 2"):
            self.cases()

    def test_multiline_case_journal_and_export_use_physical_line(self):
        self.write(("id", "status", "memo"),
                   (("A", "variance", "first\nsecond"), (), ("B", "variance", "ok")))
        batch = self.cases()
        self.assertEqual(batch.cases[1].report_row, 5)
        event = review.append_review(
            self.report, "grants", self.journal,
            case_id=batch.cases[1].case_id,
            expected_report_sha256=batch.report_sha256,
            reviewer="Audit Reviewer", decision="needs_evidence",
            rationale="Request additional signed evidence for this claim.",
        )
        self.assertEqual(event["report_row"], 5)
        output = review.export_register(self.report, "grants", self.journal, self.root)
        with output.open("r", encoding="utf-8-sig", newline="") as f:
            exported = list(csv.DictReader(f))
        self.assertEqual([r["source_row"] for r in exported], ["2", "5"])
        self.assertEqual(exported[1]["review_state"], "needs_evidence")
        self.assertEqual(len(review.read_journal(self.journal, self.cases())), 1)

    def test_malformed_source_cannot_append_or_create_journal(self):
        self.write(("id", "status"), (("A", "variance"),))
        batch = self.cases()
        self.write(("id", "status"), (("A", "variance", "unreported extra"),))
        with self.assertRaises(ValueError):
            review.append_review(
                self.report, "grants", self.journal,
                case_id=batch.cases[0].case_id,
                expected_report_sha256=batch.report_sha256,
                reviewer="Audit Reviewer", decision="reviewed",
                rationale="No decision may be recorded on malformed reports.",
            )
        self.assertFalse(self.journal.exists())


if __name__ == "__main__":
    unittest.main()
