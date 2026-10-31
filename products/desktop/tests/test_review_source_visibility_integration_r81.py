"""R81 full-repository integration regressions for both premium review products.

Synthetic report/journal files only. Requires actual premium engine source;
do not treat pure display tests as Windows executable or CI verification.
"""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import exception_review as review
from fvs_suite.audit_display import visible_source_text


class ReviewSourceVisibilityIntegrationR81(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r81-premium-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.source = self.folder / "premium-exceptions.csv"
        self.journal = self.folder / "human-decisions.jsonl"

    def source_csv(self, product, records):
        fields = ("id", "status") if product == "grants" else ("po", "line", "status")
        with self.source.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(fields)
            writer.writerows(records)
        return self.source.read_bytes()

    def export_rows(self, product):
        path = review.export_register(self.source, product, self.journal, self.folder)
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_grant_hidden_source_visible_without_input_mutation(self):
        raw_identifier = "CLM\u202E=100"
        raw_flag = "needs\u200B_evidence"
        baseline = self.source_csv("grants", [(raw_identifier, raw_flag)])
        batch = review.read_cases(self.source, "grants")
        self.assertEqual(batch.cases[0].source_key, raw_identifier)
        self.assertEqual(batch.cases[0].flags, raw_flag)
        self.assertEqual(batch.report_sha256, hashlib.sha256(baseline).hexdigest())
        rows = self.export_rows("grants")
        self.assertEqual(rows[0]["source_key"], r"CLM\u202E=100")
        self.assertEqual(rows[0]["original_flags"], r"needs\u200B_evidence")
        self.assertEqual(rows[0]["source_row"], "2")
        self.assertEqual(rows[0]["case_id"], batch.cases[0].case_id)
        self.assertEqual(rows[0]["report_sha256"], batch.report_sha256)
        self.assertEqual(self.source.read_bytes(), baseline)
        self.assertFalse(self.journal.exists())

    def test_procurement_hidden_source_visible(self):
        baseline = self.source_csv(
            "procurement", [("PO\u2066-12", "2\uFE0F", "review\u2029_hold")])
        batch = review.read_cases(self.source, "procurement")
        rows = self.export_rows("procurement")
        self.assertEqual(rows[0]["source_key"], r"PO\u2066-12 / 2\uFE0F")
        self.assertEqual(rows[0]["original_flags"], r"review\u2029_hold")
        self.assertEqual(rows[0]["review_state"], "pending")
        self.assertEqual(self.source.read_bytes(), baseline)
        self.assertEqual(rows[0]["report_sha256"], batch.report_sha256)

    def test_literal_source_escape_distinct_from_hidden_character(self):
        baseline = self.source_csv("grants", [
            ("CLM\u202E", "variance"), (r"CLM\u202E", "variance"),
        ])
        rows = self.export_rows("grants")
        self.assertEqual(rows[0]["source_key"], r"CLM\u202E")
        self.assertEqual(rows[1]["source_key"], r"CLM\\u202E")
        self.assertNotEqual(rows[0]["source_key"], rows[1]["source_key"])
        self.assertEqual(self.source.read_bytes(), baseline)

    def test_formula_prefix_uses_existing_csv_guard(self):
        self.source_csv("grants", [
            ("=1+1", "needs_evidence"), ("\u200B=1+1", "needs_evidence"),
        ])
        rows = self.export_rows("grants")
        self.assertEqual(rows[0]["source_key"], "'=1+1")
        self.assertEqual(rows[1]["source_key"], r"\u200B=1+1")

    def test_raw_report_flags_remain_bound_to_journal_hash(self):
        raw_flag = "unverified\u202E_amount"
        baseline = self.source_csv("grants", [("CLM-6", raw_flag)])
        batch = review.read_cases(self.source, "grants")
        event = review.append_review(
            self.source, "grants", self.journal,
            case_id=batch.cases[0].case_id,
            expected_report_sha256=batch.report_sha256,
            reviewer="Audit Reviewer", decision="needs_evidence",
            rationale="Inspect original unrendered source and supporting evidence.",
        )
        self.assertEqual(event["flags"], raw_flag)
        self.assertEqual(review.read_journal(self.journal, batch), [event])
        row = self.export_rows("grants")[0]
        self.assertEqual(row["original_flags"], visible_source_text(raw_flag))
        self.assertEqual(row["review_state"], "needs_evidence")
        self.assertEqual(row["reviewer"], "Audit Reviewer")
        self.assertEqual(self.source.read_bytes(), baseline)


if __name__ == "__main__":
    unittest.main()
