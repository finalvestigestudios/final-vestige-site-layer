"""R155 synthetic tests for independent, read-only SpendMap membership verification."""
from __future__ import annotations

import contextlib
import csv
import io
import os
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine
from fvs_suite.spend_evidence_verify import main, verify_membership


class SpendIndependentMembershipR155(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fvs-r155-synthetic-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.csv"
        self.report = None

    @staticmethod
    def item(vendor="ACME", amount="2.00", month="01", category="Parts", note=""):
        return (vendor, amount, f"2026-{month}-01", category, note)

    def write(self, rows):
        with self.source.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(rows)
        self.report = Path(engine.spend_map(self.source, self.root)[0])
        return self.report

    def mutate(self, column, value, row=0):
        with self.report.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields, rows = list(reader.fieldnames), list(reader)
        rows[row][column] = value
        with self.report.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def invoke(self, *flags):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(list(flags))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_single_group_verified_with_two_pins(self):
        self.write([self.item()])
        receipt = verify_membership(self.source, self.report)
        self.assertEqual((receipt.groups_verified, receipt.buckets_verified), (1, 1))
        self.assertEqual(len(receipt.report_sha256), 64)

    def test_multiple_months_and_vendors(self):
        self.write([self.item(), self.item(month="02"), self.item(vendor="OTHER")])
        receipt = verify_membership(self.source, self.report)
        self.assertEqual((receipt.groups_verified, receipt.buckets_verified), (3, 3))

    def test_cross_category_monthly_proof(self):
        self.write([self.item(amount="150"), self.item(category="Services", amount="-140")])
        receipt = verify_membership(self.source, self.report)
        self.assertEqual((receipt.groups_verified, receipt.buckets_verified), (1, 2))

    def test_thirty_three_citations_with_omission(self):
        self.write([self.item(category="C" + str(i % 3)) for i in range(33)])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 3)

    def test_two_hundred_line_members(self):
        self.write([self.item(category="C" + str(i % 7)) for i in range(200)])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 7)

    def test_multiline_source_physical_line_numbers(self):
        self.write([self.item(note="first\nsecond"), self.item(category="Services")])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 2)

    def test_normalization_collision_group(self):
        self.write([self.item(vendor="A-CME"), self.item(vendor="ACME")])
        self.assertEqual(verify_membership(self.source, self.report).groups_verified, 1)

    def test_safe_csv_export_category(self):
        self.write([self.item(category="=1+1"), self.item(category="Parts")])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 2)

    def test_tampered_membership_hash_hold(self):
        self.write([self.item()])
        self.mutate("vendor_month_evidence_sha256", "0" * 64)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_tampered_source_pin_hold(self):
        self.write([self.item()])
        self.mutate("source_sha256", "0" * 64)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_tampered_preview_hold(self):
        self.write([self.item()])
        self.mutate("vendor_month_evidence_rows", "999")
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_tampered_count_hold(self):
        self.write([self.item()])
        self.mutate("vendor_month_evidence_count", "9")
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_tampered_omitted_hold(self):
        self.write([self.item()])
        self.mutate("vendor_month_evidence_omitted", "9")
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_tampered_category_lines_hold(self):
        self.write([self.item(), self.item(category="Services")])
        self.mutate("source_rows", "1000")
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_renamed_bucket_hold(self):
        self.write([self.item()])
        self.mutate("category", "Different")
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_duplicate_bucket_hold(self):
        self.write([self.item(), self.item(category="Services")])
        self.mutate("category", "Parts", row=1)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_missing_bucket_hold(self):
        self.write([self.item(), self.item(category="Services")])
        with self.report.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fields, rows = list(reader.fieldnames), list(reader)
        with self.report.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fields)
            writer.writeheader()
            writer.writerow(rows[0])
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_original_source_modified_after_export_hold(self):
        self.write([self.item(note="original")])
        with self.source.open("a", encoding="utf-8") as stream:
            stream.write("\n")
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_header_only_financial_source_hold(self):
        self.write([])
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_report_source_not_modified_by_verification(self):
        self.write([self.item()])
        old_source = self.source.read_bytes()
        old_report = self.report.read_bytes()
        verify_membership(self.source, self.report)
        self.assertEqual((self.source.read_bytes(), self.report.read_bytes()),
                         (old_source, old_report))

    def test_cli_success_no_private_path(self):
        self.write([self.item()])
        code, stdout, stderr = self.invoke("--source", str(self.source),
                                           "--report", str(self.report))
        self.assertEqual((code, stderr), (0, ""))
        self.assertIn("MEMBERSHIP VERIFIED", stdout)
        self.assertNotIn(str(self.root), stdout)

    def test_cli_bad_source_no_leak(self):
        self.write([self.item()])
        secret = "CONFIDENTIAL-ACCT-7890"
        code, stdout, stderr = self.invoke("--source", secret,
                                           "--report", str(self.report))
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertNotIn(secret, stderr)
        self.assertIn("HOLD", stderr)

    def test_cli_duplicate_report_hold(self):
        self.write([self.item()])
        code, stdout, stderr = self.invoke("--source", str(self.source),
                                           "--report", str(self.report),
                                           "--report", "PRIVATE-SECOND.csv")
        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertNotIn("PRIVATE-SECOND", stderr)

    def test_cli_unexpected_option_hold(self):
        self.write([self.item()])
        code, stdout, stderr = self.invoke("--source", str(self.source),
                                           "--report", str(self.report),
                                           "--secret", "ACCOUNT-234")
        self.assertEqual(code, 1)
        self.assertNotIn("ACCOUNT-234", stdout + stderr)

    def test_symlink_source_rejected_when_supported(self):
        self.write([self.item()])
        alias = self.root / "alias.csv"
        try:
            alias.symlink_to(self.source)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable on this host")
        with self.assertRaises(ValueError):
            verify_membership(alias, self.report)

    def test_report_without_evidence_columns_hold(self):
        self.write([self.item()])
        self.report.write_text("vendor_key,month,category\nACME,2026-01,Parts\n",
                               encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)


if __name__ == "__main__":
    unittest.main()
