"""R430 real source/report verification integration; synthetic local CSV only.

Requires the full desktop package, unlike the isolated 20-case helper suite.
No network calls, customer data, release action or payment approval.
"""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fvs_suite import engine
from fvs_suite.spend_evidence_verify import verify_membership
from fvs_suite.spend_review_verify import compute_expected_review_fields


class SpendLabelVerificationIntegrationR430(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory(prefix="fvs-r430-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "source.csv"
        self.report = None

    def export(self, rows):
        with self.source.open("w", encoding="utf-8", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(("vendor", "amount", "date", "category"))
            writer.writerows(rows)
        self.report = Path(engine.spend_map(self.source, self.root)[0])
        with self.report.open("r", encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    @staticmethod
    def row(vendor, category="Parts", month="01", amount="10.00"):
        return vendor, amount, "2026-" + month + "-01", category

    def test_plain_native_report_still_verifies(self):
        rows = self.export([self.row("ACME")])
        self.assertEqual(rows[0]["source_vendor_labels"], "ACME")
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 1)

    def test_original_ascii_boundaries_verify_vendor_wide_across_categories(self):
        rows = self.export([self.row(" ACME", "Parts"),
                            self.row("ACME ", "Services")])
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["source_vendor_labels"] for r in rows},
                         {r"\u0020ACME; ACME\u0020"})
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 2)

    def test_original_variants_verify_across_months(self):
        rows = self.export([self.row(" ACME", month="01"),
                            self.row("ACME ", month="02")])
        self.assertEqual({r["source_vendor_labels"] for r in rows},
                         {r"\u0020ACME; ACME\u0020"})
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 2)

    def test_more_than_32_original_labels_verify_full_truncation_digest(self):
        rows = self.export([self.row(" " * n + "ACME") for n in range(1, 42)])
        self.assertEqual(len(rows), 1)
        self.assertIn("PREVIEW_ONLY:shown=32:omitted=9:sha256=",
                      rows[0]["source_vendor_labels"])
        self.assertLessEqual(len(rows[0]["source_vendor_labels"]), 8192)
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 1)

    def test_3000_codepoint_label_full_digest_verifies(self):
        rows = self.export([self.row("A" * 3000)])
        self.assertIn("LABEL_PREFIX_ONLY", rows[0]["source_vendor_labels"])
        self.assertIn("PREVIEW_ONLY", rows[0]["source_vendor_labels"])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 1)

    def test_nonascii_boundary_collision_verifies_not_silenced(self):
        rows = self.export([self.row("ACME"), self.row("\u00a0ACME")])
        self.assertEqual(rows[0]["vendor_label_variants"], "2")
        self.assertIn("normalized_vendor_collision_review", rows[0]["flag"])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 1)

    def test_truncated_digest_tamper_holds(self):
        rows = self.export([self.row(" " * n + "ACME") for n in range(1, 42)])
        rows[0]["source_vendor_labels"] = rows[0]["source_vendor_labels"].replace(
            "sha256=", "sha256=0")
        with self.report.open("w", encoding="utf-8-sig", newline="") as out:
            writer = csv.DictWriter(out, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_independent_variant_count_respects_ascii_only_boundaries(self):
        fields = compute_expected_review_fields([
            ("ACME", "2026-01", "Parts", Decimal("10.00"), " ACME "),
            ("ACME", "2026-01", "Parts", Decimal("5.00"), "ACME"),
        ])
        self.assertEqual(fields[("ACME", "2026-01", "Parts")]["vendor_label_variants"], "1")
        fields = compute_expected_review_fields([
            ("ACME", "2026-01", "Parts", Decimal("10.00"), "ACME"),
            ("ACME", "2026-01", "Parts", Decimal("5.00"), "\u00a0ACME"),
        ])
        self.assertEqual(fields[("ACME", "2026-01", "Parts")]["vendor_label_variants"], "2")

    def test_verification_never_rewrites_customer_source_or_report(self):
        self.export([self.row(" ACME"), self.row("ACME ")])
        before = (self.source.read_bytes(), self.report.read_bytes())
        verify_membership(self.source, self.report)
        self.assertEqual((self.source.read_bytes(), self.report.read_bytes()), before)


if __name__ == "__main__":
    unittest.main()
