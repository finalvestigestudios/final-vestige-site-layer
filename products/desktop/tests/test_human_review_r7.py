"""R7 independent local review-journal tests; synthetic records only."""
from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from fvs_suite import exception_review as review


class HumanReviewR7Tests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="fvs-review-r7-")
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.report = self.folder / "grant-audit-exceptions-synthetic.csv"
        self.journal = self.folder / "review.jsonl"
        self.write_report(("id", "status", "amount"), [
            ("G1", "split_allocation_review", "10.00"),
            ("G2", "matched", "20.00"),
            ("G3", "credit_memo_review;variance", "30.00"),
        ])

    def write_report(self, fields, rows):
        with self.report.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(fields)
            writer.writerows(rows)

    def batch(self, product="grants"):
        return review.read_cases(self.report, product)

    def log(self, index=0, **kwargs):
        batch = self.batch()
        defaults = {
            "case_id": batch.cases[index].case_id,
            "expected_report_sha256": batch.report_sha256,
            "reviewer": "A. Reviewer",
            "decision": "needs_evidence",
            "rationale": "Supporting invoice and approval evidence needed.",
        }
        defaults.update(kwargs)
        return review.append_review(self.report, "grants", self.journal, **defaults)

    def test_exception_intake_skips_matched_and_is_repeatable(self):
        one = self.batch()
        self.assertEqual([c.report_row for c in one.cases], [2, 4])
        self.assertEqual(one, self.batch())
        self.assertEqual(one.report_sha256, hashlib.sha256(self.report.read_bytes()).hexdigest())
        self.assertFalse(self.journal.exists())

    def test_two_human_actions_form_verifiable_hash_chain(self):
        first = self.log()
        second = self.log(decision="reviewed", rationale="Reviewed; separate organizational approval required.")
        self.assertEqual(first["previous_hash"], review.ZERO_HASH)
        self.assertEqual(second["previous_hash"], first["event_hash"])
        events = review.read_journal(self.journal, self.batch())
        self.assertEqual(len(events), 2)
        self.assertEqual(review.latest_states(self.journal, self.batch())[
            self.batch().cases[0].case_id]["decision"], "reviewed")
        self.assertEqual(self.batch().cases[0].flags, "split_allocation_review")
        self.assertEqual(len(first["event_hash"]), 64)

    def test_production_never_automatically_approved(self):
        output = review.export_register(self.report, "grants", self.journal, self.folder)
        with output.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["review_state"] for r in rows}, {"pending"})
        self.assertNotIn("approved", ",".join(rows[0].values()))
        self.assertFalse(self.journal.exists())

    def test_explicit_review_does_not_change_input_report(self):
        original = self.report.read_bytes()
        self.log(decision="escalated", rationale="Escalate to independent accounting reviewer.")
        output = review.export_register(self.report, "grants", self.journal, self.folder)
        self.assertEqual(self.report.read_bytes(), original)
        with output.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(rows[0]["review_state"], "escalated")
        self.assertEqual(rows[1]["review_state"], "pending")
        self.assertEqual(rows[0]["original_flags"], "split_allocation_review")
        self.assertEqual(rows[0]["report_sha256"], self.batch().report_sha256)

    def test_unknown_or_matched_case_cannot_be_logged(self):
        with self.assertRaisesRegex(ValueError, "Unknown or already-matched"):
            self.log(case_id="a" * 64)
        self.assertFalse(self.journal.exists())

    def test_no_automatic_clear_without_reason_or_reviewer(self):
        for overrides in (
            {"reviewer": ""},
            {"reviewer": "x"},
            {"rationale": "short"},
            {"rationale": "=SUM(1+1)\nanything else"},
            {"decision": "approved"},
            {"decision": "paid"},
        ):
            with self.subTest(overrides=overrides):
                with self.assertRaises(ValueError):
                    self.log(**overrides)
                self.assertFalse(self.journal.exists())

    def test_changed_source_snapshot_rejects_stale_operator_action(self):
        batch = self.batch()
        self.write_report(("id", "status", "amount"), [
            ("G1", "split_allocation_review", "999.00")])
        with self.assertRaisesRegex(ValueError, "changed since"):
            review.append_review(
                self.report, "grants", self.journal,
                case_id=batch.cases[0].case_id,
                expected_report_sha256=batch.report_sha256,
                reviewer="A. Reviewer", decision="reviewed",
                rationale="This should never attach to modified financial evidence.")
        self.assertFalse(self.journal.exists())

    def test_edited_journal_hash_rejected_and_not_extended(self):
        self.log()
        original = self.journal.read_bytes()
        event = json.loads(original)
        event["decision"] = "reviewed"
        self.journal.write_text(json.dumps(event) + "\n", encoding="utf-8")
        before = self.journal.read_bytes()
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.log(decision="reviewed")
        self.assertEqual(self.journal.read_bytes(), before)

    def test_truncated_journal_rejected(self):
        self.log()
        self.journal.write_bytes(self.journal.read_bytes()[:-2])
        with self.assertRaisesRegex(ValueError, "incomplete final record"):
            review.read_journal(self.journal, self.batch())
        with self.assertRaisesRegex(ValueError, "incomplete final record"):
            self.log()

    def test_duplicate_json_keys_fail_closed(self):
        self.log()
        data = self.journal.read_text(encoding="utf-8")
        self.journal.write_text(data.replace('{"case_id":', '{"case_id":"extra","case_id":', 1),
                                encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Repeated JSON journal key"):
            review.read_journal(self.journal, self.batch())

    def test_report_changes_after_review_are_detected(self):
        self.log()
        self.write_report(("id", "status", "amount"), [
            ("G1", "split_allocation_review", "999")])
        with self.assertRaisesRegex(ValueError, "different report snapshot"):
            review.read_journal(self.journal, self.batch())
        with self.assertRaisesRegex(ValueError, "different report snapshot"):
            review.export_register(self.report, "grants", self.journal, self.folder)

    def test_lock_file_blocks_parallel_writer(self):
        self.journal.with_suffix(".jsonl.lock").write_text("active", encoding="ascii")
        with self.assertRaisesRegex(ValueError, "locked by another writer"):
            self.log()
        self.assertFalse(self.journal.exists())

    def test_procurement_review_queue_uses_po_and_line(self):
        path = self.folder / "procurement-three-way-synthetic.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("po", "line", "status"))
            writer.writerow(("P-1", "2", "price_variance_above_policy"))
            writer.writerow(("P-2", "1", "matched"))
        batch = review.read_cases(path, "procurement")
        self.assertEqual(len(batch.cases), 1)
        self.assertEqual(batch.cases[0].source_key, "P-1 / 2")
        event = review.append_review(path, "procurement", self.journal,
                                     case_id=batch.cases[0].case_id,
                                     expected_report_sha256=batch.report_sha256,
                                     reviewer="Manager", decision="escalated",
                                     rationale="Disputed unit cost; verify supporting PO.")
        self.assertEqual(event["product"], "procurement")

    def test_csv_formula_injection_neutralized_in_register(self):
        self.write_report(("id", "status"), [
            ("=HYPERLINK(\"http://example.test\", \"go\")", "@ALERT"),
        ])
        self.log(rationale="=HYPERLINK(1) formula-style note cannot execute.")
        result = review.export_register(self.report, "grants", self.journal, self.folder)
        with result.open(encoding="utf-8-sig", newline="") as stream:
            row = list(csv.DictReader(stream))[0]
        self.assertTrue(row["source_key"].startswith("'="))
        self.assertTrue(row["original_flags"].startswith("'@"))
        self.assertTrue(row["rationale"].startswith("'="))

    def test_ambiguous_csv_headers_rejected(self):
        self.write_report(("id", "Status", "status"), [("A", "matched", "variance")])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.batch()
        self.assertFalse(self.journal.exists())

    def test_malformed_record_has_no_automatic_review(self):
        self.report.write_text("id,status\nA,variance,extra\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Malformed CSV"):
            self.batch()

    def test_non_csv_or_wrong_product_rejected(self):
        with self.assertRaises(ValueError):
            self.batch("ledger")
        bad = self.folder / "review.txt"
        bad.write_text("id,status\nA,variance\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "CSV"):
            review.read_cases(bad, "grants")

    def test_does_not_overwrite_unrelated_report_with_journal(self):
        with self.assertRaisesRegex(ValueError, "separate"):
            review.append_review(
                self.report, "grants", self.report,
                case_id=self.batch().cases[0].case_id,
                expected_report_sha256=self.batch().report_sha256,
                reviewer="Reviewer", decision="reviewed",
                rationale="No source record should ever be overwritten.")


if __name__ == "__main__":
    unittest.main()
