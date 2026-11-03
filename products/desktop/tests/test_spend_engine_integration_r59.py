"""SpendMap R59 integration contracts; require the complete trusted checkout.

Exercise the real CSV import, provenance, report writer and sheet sanitization;
these tests are intentionally NOT replaced by the isolated helper tests.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine


class SpendEngineIntegrationR59(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-spend-r59-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def source(self, records, *, name="spend.csv"):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(records)
        return path

    @staticmethod
    def read(path):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_source_rows_and_vendor_labels_survive_real_csv_writer(self):
        source = self.source([
            ("A-CME", "1.25", "2026-01-01", "Parts", "quoted\nextra line"),
            ("ACME", "2.75", "2026-01-02", "Parts", "plain"),
        ])
        report = self.read(engine.spend_map(source, self.root)[0])[0]
        self.assertEqual(report["source_rows"], "2;4")
        self.assertEqual(report["source_vendor_labels"], "A-CME; ACME")
        self.assertEqual(report["vendor_label_variants"], "2")
        self.assertEqual(report["amount"], "4.00")
        self.assertEqual(report["flag"], "normalized_vendor_collision_review")

    def test_cross_month_collision_survives_real_csv_import(self):
        source = self.source([
            ("A-CME", "1", "2026-01-01", "A", ""),
            ("ACME", "1", "2026-02-01", "B", ""),
        ])
        rows = self.read(engine.spend_map(source, self.root)[0])
        self.assertEqual([row["flag"] for row in rows],
                         ["normalized_vendor_collision_review"] * 2)

    def test_existing_spike_contract_and_explainable_baseline(self):
        source = self.source([
            ("ACME", "10", "2026-01-01", "Parts", ""),
            ("ACME", "10", "2026-02-01", "Parts", ""),
            ("ACME", "10", "2026-03-01", "Parts", ""),
            ("ACME", "30", "2026-04-01", "Parts", ""),
        ])
        final = self.read(engine.spend_map(source, self.root)[0])[-1]
        self.assertEqual(final["flag"], "review_spike")
        self.assertEqual(final["vendor_month_total"], "30.00")
        self.assertEqual(final["baseline_median"], "10.00")
        self.assertEqual(final["history_months"], "3")

    def test_csv_formula_original_vendor_is_neutralized(self):
        source = self.source([("=ACME", "1", "2026-01-01", "Parts", "")])
        row = self.read(engine.spend_map(source, self.root)[0])[0]
        self.assertEqual(row["source_vendor_labels"], "'=ACME")

    def test_case_only_variants_still_group_without_collision(self):
        source = self.source([
            ("Acme", "1", "2026-01-01", "Parts", ""),
            ("ACME", "1", "2026-01-01", "Parts", ""),
        ])
        row = self.read(engine.spend_map(source, self.root)[0])[0]
        self.assertEqual(row["amount"], "2.00")
        self.assertEqual(row["flag"], "")
        self.assertEqual(row["vendor_label_variants"], "1")

    def test_invalid_decimal_fails_without_partial_spend_report(self):
        source = self.source([
            ("ACME", "10", "2026-01-01", "Parts", ""),
            ("ACME", "NaN", "2026-01-02", "Parts", ""),
        ])
        with self.assertRaises(ValueError):
            engine.spend_map(source, self.root)
        self.assertEqual(list(self.root.glob("spend-map-*.csv")), [])

    def test_report_has_explicit_provenance_columns(self):
        source = self.source([("ACME", "1", "2026-01-01", "Parts", "")])
        report_path = engine.spend_map(source, self.root)[0]
        with report_path.open(encoding="utf-8-sig", newline="") as stream:
            headers = next(csv.reader(stream))
        self.assertEqual(headers, [
            "vendor_key", "month", "category", "amount", "flag",
            "vendor_month_total", "baseline_median", "history_months",
            "category_history_months", "category_baseline_median", "category_review_flag",
            "gross_charges", "gross_credits", "credit_offset_review",
            "vendor_month_evidence_rows", "vendor_month_evidence_count",
            "vendor_month_evidence_omitted",
            "vendor_month_gross_charges", "vendor_month_gross_credits",
            "vendor_month_offset_review",
            "source_rows", "source_vendor_labels", "vendor_label_variants",
            "source_sha256",
        ])


if __name__ == "__main__":
    unittest.main()
