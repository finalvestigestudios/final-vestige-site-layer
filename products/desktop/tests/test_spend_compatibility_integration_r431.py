"""R431 full-engine SpendMap source/export/verifier regressions; synthetic CSV only.

These require the real repository fvs_suite package. They must not be counted
as executed merely because isolated source-label unit tests pass.
"""
from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fvs_suite import engine
from fvs_suite.spend_evidence_verify import verify_membership


class SpendCompatibilityIntegrationR431(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory(prefix="fvs-r431-compat-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "source.csv"
        self.report = None

    def export(self, vendors):
        with self.source.open("w", encoding="utf-8", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(("vendor", "amount", "date", "category"))
            writer.writerows((v, "12.30", "2026-01-10", "Parts") for v in vendors)
        self.report = Path(engine.spend_map(self.source, self.root)[0])
        with self.report.open("r", encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def assert_native_compatible(self, raw):
        rows = self.export([raw])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_vendor_labels"], "'" + raw)
        before = (self.source.read_bytes(), self.report.read_bytes())
        receipt = verify_membership(self.source, self.report)
        self.assertEqual(receipt.buckets_verified, 1)
        self.assertEqual((self.source.read_bytes(), self.report.read_bytes()), before)

    def test_fullwidth_plus_report_verifies(self):
        self.assert_native_compatible("＋ACME")

    def test_fullwidth_equals_report_verifies(self):
        self.assert_native_compatible("＝ACME")

    def test_fullwidth_at_report_verifies(self):
        self.assert_native_compatible("＠ACME")

    def test_small_plus_report_verifies(self):
        self.assert_native_compatible("﹢ACME")

    def test_small_minus_report_verifies(self):
        self.assert_native_compatible("﹣ACME")

    def test_unquoted_compatibility_operator_is_not_accepted(self):
        rows = self.export(["＋ACME"])
        rows[0]["source_vendor_labels"] = rows[0]["source_vendor_labels"].lstrip("'")
        with self.report.open("w", encoding="utf-8-sig", newline="") as out:
            writer = csv.DictWriter(out, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)


if __name__ == "__main__":
    unittest.main()
