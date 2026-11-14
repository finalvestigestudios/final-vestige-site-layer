"""R419 direct premium journal integration: reject forged identities before I/O.

Synthetic grant/procurement audit reports only. Human review is not payment
authorization or compliance clearance; no release candidate is validated.
"""
from __future__ import annotations

import csv
from pathlib import Path
import tempfile
import unittest

from fvs_suite import exception_review as review


class PremiumReviewInputIdentityR419(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.report = self.root / "synthetic-grants.csv"
        self.journal = self.root / "review.jsonl"
        with self.report.open("w", encoding="utf-8", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(("id", "status", "amount"))
            writer.writerow(("G-1", "variance_review", "10.00"))
        self.batch = review.read_cases(self.report, "grants")
        self.arguments = dict(
            case_id=self.batch.cases[0].case_id,
            expected_report_sha256=self.batch.report_sha256,
            reviewer="Review Analyst",
            decision="needs_evidence",
            rationale="Verify original invoice and signed supporting evidence.",
        )

    def append(self, **changes):
        arguments = {**self.arguments, **changes}
        return review.append_review(
            self.report, "grants", self.journal, **arguments)

    def test_plain_review_is_journaled_as_human_only(self):
        event = self.append()
        self.assertEqual(event["decision"], "needs_evidence")
        self.assertEqual(event["report_sha256"], self.batch.report_sha256)
        self.assertEqual(len(review.read_journal(self.journal, self.batch)), 1)
        self.assertNotIn("approved", event["decision"])

    def test_forged_stale_source_hash_rejected_before_file_changes(self):
        class ForgedHash(str):
            def __eq__(self, other):
                raise AssertionError("PRIVATE_COMPARISON")
            def __ne__(self, other):
                raise AssertionError("PRIVATE_COMPARISON")
            def __len__(self):
                raise AssertionError("PRIVATE_LENGTH")
        with self.assertRaisesRegex(ValueError, "canonical") as caught:
            self.append(expected_report_sha256=ForgedHash("0" * 64))
        self.assertNotIn("PRIVATE_", str(caught.exception))
        self.assertFalse(self.journal.exists())

    def test_forged_case_id_rejected_before_dictionary_lookup(self):
        class ForgedId(str):
            def __hash__(self):
                raise AssertionError("PRIVATE_CASE_HASH")
        with self.assertRaisesRegex(ValueError, "native text"):
            self.append(case_id=ForgedId(self.batch.cases[0].case_id))
        self.assertFalse(self.journal.exists())

    def test_forged_decision_cannot_be_written(self):
        class ForgedDecision(str):
            def __eq__(self, other):
                raise AssertionError("PRIVATE_DECISION")
        with self.assertRaisesRegex(ValueError, "Decision must"):
            self.append(decision=ForgedDecision("approved"))
        self.assertFalse(self.journal.exists())

    def test_forged_reviewer_strip_hook_not_invoked(self):
        class ForgedReviewer(str):
            def strip(self, *args, **kwargs):
                raise AssertionError("PRIVATE_REVIEWER")
        with self.assertRaisesRegex(ValueError, "Reviewer must be text"):
            self.append(reviewer=ForgedReviewer("Another Reviewer"))
        self.assertFalse(self.journal.exists())

    def test_forged_rationale_text_hook_not_invoked(self):
        class ForgedRationale(str):
            def __iter__(self):
                raise AssertionError("PRIVATE_RATIONALE")
        with self.assertRaisesRegex(ValueError, "Rationale must be text"):
            self.append(rationale=ForgedRationale("Sufficient detail for review."))
        self.assertFalse(self.journal.exists())

    def test_product_subclass_rejected_before_source_read(self):
        class ForgedProduct(str):
            def __eq__(self, other):
                raise AssertionError("PRIVATE_PRODUCT")
        with self.assertRaisesRegex(ValueError, "Only premium"):
            review.read_cases(self.report, ForgedProduct("grants"))
        with self.assertRaisesRegex(ValueError, "Only premium"):
            review.append_review(self.report, ForgedProduct("grants"),
                                 self.journal, **self.arguments)
        self.assertFalse(self.journal.exists())

    def test_wrong_source_hash_with_native_text_still_rejected(self):
        with self.assertRaisesRegex(ValueError, "changed since"):
            self.append(expected_report_sha256="0" * 64)
        self.assertFalse(self.journal.exists())

    def test_invalid_hash_syntax_rejected_before_journal(self):
        with self.assertRaisesRegex(ValueError, "canonical"):
            self.append(expected_report_sha256="F" * 64)
        self.assertFalse(self.journal.exists())

    def test_real_procurement_case_still_available_for_human_review(self):
        other = self.root / "synthetic-procurement.csv"
        with other.open("w", encoding="utf-8", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(("po", "line", "status"))
            writer.writerow(("P-1", "1", "price_variance_review"))
        batch = review.read_cases(other, "procurement")
        self.assertEqual(len(batch.cases), 1)
        self.assertEqual(batch.cases[0].source_key, "P-1 / 1")


if __name__ == "__main__":
    unittest.main()
