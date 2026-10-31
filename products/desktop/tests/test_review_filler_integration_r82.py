"""R82: two-premium-product journal boundary regressions (source-only).

Requires full fvs_suite checkout. Synthetic files; no Windows release implied.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from fvs_suite import exception_review as review
from fvs_suite.unicode_hazards import VISUALLY_BLANK_FILLERS
from fvs_suite.audit_display import visible_source_text


class PremiumBlankReviewBoundaryR82(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-r82-synthetic-")
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.report = self.home / "exceptions.csv"
        self.journal = self.home / "exceptions.review.jsonl"

    def prepare(self, product, *, key="REF-01"):
        with self.report.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            if product == "grants":
                writer.writerows((("id", "status"), (key, "requires_evidence")))
            else:
                writer.writerows((("po", "line", "status"), (key, "1", "variance_review")))
        batch = review.read_cases(self.report, product)
        return batch, self.report.read_bytes()

    def append(self, batch, **kwargs):
        values = dict(case_id=batch.cases[0].case_id,
                      expected_report_sha256=batch.report_sha256,
                      reviewer="Human Reviewer", decision="needs_evidence",
                      rationale="Inspect the original evidence before signing.")
        values.update(kwargs)
        return review.append_review(self.report, batch.product, self.journal, **values)

    def assert_no_evidence_write(self, original):
        self.assertFalse(self.journal.exists())
        self.assertFalse(Path(str(self.journal) + ".lock").exists())
        self.assertEqual(self.report.read_bytes(), original)

    def test_every_filler_reviewer_rejected_before_write_for_both_products(self):
        for product in ("grants", "procurement"):
            batch, original = self.prepare(product)
            for point in sorted(VISUALLY_BLANK_FILLERS):
                with self.subTest(product=product, codepoint=hex(point)):
                    with self.assertRaisesRegex(ValueError, "hidden or control"):
                        self.append(batch, reviewer="Audit" + chr(point) + "Reviewer")
                    self.assert_no_evidence_write(original)

    def test_every_filler_rationale_rejected_before_write_for_both_products(self):
        for product in ("grants", "procurement"):
            batch, original = self.prepare(product)
            for point in sorted(VISUALLY_BLANK_FILLERS):
                with self.subTest(product=product, codepoint=hex(point)):
                    with self.assertRaisesRegex(ValueError, "hidden or control"):
                        self.append(batch, rationale="Inspect" + chr(point) +
                                    "the source evidence before approval.")
                    self.assert_no_evidence_write(original)

    def test_rehashed_historical_filler_reviewer_fails_closed(self):
        for product in ("grants", "procurement"):
            batch, original = self.prepare(product)
            event = self.append(batch)
            event["reviewer"] = "Finance\u3164Lead"
            event["event_hash"] = review._hex_hash(
                review._json({name: event[name] for name in review.FIELDS}))
            self.journal.write_bytes(review._json(event) + b"\n")
            before = self.journal.read_bytes()
            with self.subTest(product=product):
                with self.assertRaisesRegex(ValueError, "hidden or control"):
                    review.read_journal(self.journal, batch)
                with self.assertRaises(ValueError):
                    review.export_register(self.report, product, self.journal, self.home)
                self.assertEqual(before, self.journal.read_bytes())
                self.assertEqual(original, self.report.read_bytes())
                self.assertFalse(list(self.home.glob("review-register-*.csv")))
            self.journal.unlink()

    def test_preexisting_raw_source_is_display_only_not_rewritten(self):
        for product in ("grants", "procurement"):
            raw_key = "ID\u2800-4"
            batch, original = self.prepare(product, key=raw_key)
            self.assertEqual(batch.cases[0].source_key.split(" / ")[0], raw_key)
            self.assertEqual(visible_source_text(raw_key), r"ID\u2800-4")
            self.assertEqual(self.report.read_bytes(), original)
            self.assertFalse(self.journal.exists())

    def test_plain_multilingual_and_normal_spaces_still_allowed(self):
        for product in ("grants", "procurement"):
            batch, original = self.prepare(product)
            event = self.append(batch, reviewer="Élodie Méndez",
                                rationale="Reviewer checked 東京 records and original receipts.")
            self.assertEqual(review.read_journal(self.journal, batch), [event])
            self.assertEqual(self.report.read_bytes(), original)
            self.journal.unlink()


if __name__ == "__main__":
    unittest.main()
