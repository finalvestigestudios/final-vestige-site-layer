"""R399 real SpendMap source/report/replay integration on synthetic local CSVs.

Requires full repository; no account, network, compliance decision or publishing.
"""
from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fvs_suite.engine import spend_map
from fvs_suite.spend_evidence_verify import verify_membership


class SpendVendorReplayIntegrationR399(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory(prefix="fvs-r399-spend-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source = self.root / "source.csv"
        self.output = self.root / "reports"
        self.output.mkdir()

    def make_report(self, rows):
        with self.source.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category"))
            writer.writerows(rows)
        before = self.source.read_bytes()
        report = Path(spend_map(self.source, self.output)[0])
        self.assertEqual(self.source.read_bytes(), before)
        with report.open("r", encoding="utf-8-sig", newline="") as stream:
            parsed = list(csv.DictReader(stream))
        self.assertTrue(parsed)
        return report, parsed

    def test_boundary_whitespace_collision_and_verified_replay(self):
        report, rows = self.make_report([
            (" ACME", "10.00", "2026-01-01", "Parts"),
            ("ACME", "10.00", "2026-01-02", "Parts"),
        ])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["amount"], "20.00")
        self.assertEqual(rows[0]["vendor_label_variants"], "2")
        self.assertEqual(rows[0]["source_vendor_labels"], r"\u0020ACME; ACME")
        self.assertIn("normalized_vendor_collision_review", rows[0]["flag"])
        self.assertEqual(verify_membership(self.source, report).buckets_verified, 1)

    def test_category_labels_are_scoped_but_review_flag_vendor_wide(self):
        report, rows = self.make_report([
            (" ACME", "10.00", "2026-01-01", "Parts"),
            ("ACME", "-3.00", "2026-01-02", "Services"),
        ])
        self.assertEqual(len(rows), 2)
        labels = {r["category"]: r["source_vendor_labels"] for r in rows}
        self.assertEqual(labels, {"Parts": r"\u0020ACME", "Services": "ACME"})
        self.assertTrue(all(r["vendor_label_variants"] == "2" for r in rows))
        self.assertTrue(all("normalized_vendor_collision_review" in r["flag"] for r in rows))
        self.assertEqual(verify_membership(self.source, report).buckets_verified, 2)

    def test_month_labels_are_scoped_but_review_flag_vendor_wide(self):
        report, rows = self.make_report([
            (" ACME", "1.00", "2026-01-01", "Parts"),
            ("ACME", "2.00", "2026-02-01", "Parts"),
        ])
        labels = {r["month"]: r["source_vendor_labels"] for r in rows}
        self.assertEqual(labels, {"2026-01": r"\u0020ACME", "2026-02": "ACME"})
        self.assertTrue(all("normalized_vendor_collision_review" in r["flag"] for r in rows))
        self.assertEqual(verify_membership(self.source, report).groups_verified, 2)

    def test_ascii_case_only_does_not_trigger_review(self):
        report, rows = self.make_report([
            (" ACME", "5.00", "2026-01-01", "Parts"),
            (" acme", "5.00", "2026-01-02", "Parts"),
        ])
        self.assertEqual(rows[0]["vendor_label_variants"], "1")
        self.assertNotIn("normalized_vendor_collision_review", rows[0]["flag"])
        self.assertEqual(verify_membership(self.source, report).buckets_verified, 1)

    def test_suppressed_collision_flag_cannot_verify(self):
        report, rows = self.make_report([
            (" ACME", "5.00", "2026-01-01", "Parts"),
            ("ACME", "5.00", "2026-01-02", "Parts"),
        ])
        self.assertIn("normalized_vendor_collision_review", rows[0]["flag"])
        rows[0]["flag"] = ""
        with report.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaises(ValueError):
            verify_membership(self.source, report)


if __name__ == "__main__":
    unittest.main()
