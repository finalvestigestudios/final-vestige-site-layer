"""R156 synthetic source-bound monetary recheck; no real accounts or remote IO."""
from __future__ import annotations

import contextlib
import csv
import io
import tempfile
import unittest
from decimal import Inexact, getcontext, setcontext
from pathlib import Path

from fvs_suite import engine
from fvs_suite.spend_evidence_verify import main, verify_membership


class SpendMoneyRecheckR156(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fvs-r156-synthetic-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "data.csv"
        self.report = None

    def write(self, rows):
        with self.source.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(rows)
        self.report = Path(engine.spend_map(self.source, self.root)[0])
        return self.report

    @staticmethod
    def row(amount="1.00", vendor="ACME", category="Parts", date="2026-01-01", note=""):
        return (vendor, amount, date, category, note)

    def alter(self, field, value, index=0):
        with self.report.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields, rows = list(reader.fieldnames), list(reader)
        rows[index][field] = value
        with self.report.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def hold_after_change(self, field, value, rows=None, index=0):
        self.write(rows or [self.row()])
        self.alter(field, value, index=index)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_single_positive_amount(self):
        self.write([self.row("1234.56")])
        result = verify_membership(self.source, self.report)
        self.assertEqual((result.groups_verified, result.buckets_verified), (1, 1))

    def test_negative_only_credit(self):
        self.write([self.row("-123.45")])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 1)

    def test_zero_amount_is_not_an_offset(self):
        self.write([self.row("0.00"), self.row("-0.00")])
        self.assertEqual(verify_membership(self.source, self.report).groups_verified, 1)

    def test_net_zero_positive_and_negative(self):
        self.write([self.row("150.00"), self.row("-150.00")])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 1)

    def test_cross_category_offset_totals(self):
        self.write([self.row("150.00", category="Parts"),
                    self.row("-140.00", category="Services")])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 2)

    def test_multiple_months_and_vendors(self):
        self.write([self.row("100.00"), self.row("-5.00", date="2026-02-02"),
                    self.row("20.01", vendor="OTHER")])
        self.assertEqual(verify_membership(self.source, self.report).groups_verified, 3)

    def test_normalized_vendor_collisions(self):
        self.write([self.row("3.00", vendor="A-CME"),
                    self.row("-2.00", vendor="ACME")])
        self.assertEqual(verify_membership(self.source, self.report).groups_verified, 1)

    def test_spreadsheet_escaped_category(self):
        self.write([self.row("12.34", category="=SUM(A1:A2)")])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 1)

    def test_exact_200_line_aggregate(self):
        self.write([self.row("0.01") for _ in range(200)])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 1)

    def test_multiline_records_keep_money_and_line_membership(self):
        self.write([self.row("15.00", note="first\nsecond"),
                    self.row("-4.00", category="Other")])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 2)

    def test_ambient_low_precision_and_inexact_trap(self):
        self.write([self.row("1234.56"), self.row("0.01"), self.row("-0.02")])
        old = getcontext().copy()
        try:
            getcontext().prec = 3
            getcontext().traps[Inexact] = True
            receipt = verify_membership(self.source, self.report)
            self.assertEqual(receipt.buckets_verified, 1)
        finally:
            setcontext(old)

    def test_net_amount_tamper_hold(self):
        self.hold_after_change("amount", "1.01")

    def test_gross_charge_tamper_hold(self):
        self.hold_after_change("gross_charges", "0.00")

    def test_gross_credit_tamper_hold(self):
        self.hold_after_change("gross_credits", "1.00",
                               rows=[self.row("5.00"), self.row("-2.00")])

    def test_vendor_month_total_tamper_hold(self):
        self.hold_after_change("vendor_month_total", "1.01")

    def test_vendor_month_charge_tamper_hold(self):
        self.hold_after_change("vendor_month_gross_charges", "200.00",
                               rows=[self.row("150", category="Parts"),
                                     self.row("-140", category="Services")])

    def test_vendor_month_credit_tamper_hold(self):
        self.hold_after_change("vendor_month_gross_credits", "0.00",
                               rows=[self.row("150", category="Parts"),
                                     self.row("-140", category="Services")])

    def test_same_category_offset_flag_tamper_hold(self):
        self.hold_after_change("credit_offset_review", "",
                               rows=[self.row("150"), self.row("-140")])

    def test_vendor_month_offset_flag_tamper_hold(self):
        self.hold_after_change("vendor_month_offset_review", "",
                               rows=[self.row("150", category="Parts"),
                                     self.row("-140", category="Services")])

    def test_cross_category_second_bucket_tamper_hold(self):
        self.hold_after_change("amount", "500.00",
                               rows=[self.row("150", category="Parts"),
                                     self.row("-140", category="Services")],
                               index=1)

    def test_false_positive_offset_flag_hold(self):
        self.hold_after_change("credit_offset_review", "review_mixed_sign_offset")

    def test_noncanonical_money_format_hold(self):
        self.hold_after_change("amount", "1.0")

    def test_required_monetary_header_removed_hold(self):
        self.write([self.row()])
        with self.report.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields, rows = list(reader.fieldnames), list(reader)
        fields.remove("gross_charges")
        with self.report.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_original_source_and_report_not_mutated(self):
        self.write([self.row("8.25"), self.row("-1.05")])
        original = (self.source.read_bytes(), self.report.read_bytes())
        verify_membership(self.source, self.report)
        self.assertEqual((self.source.read_bytes(), self.report.read_bytes()), original)

    def test_private_cli_failure_does_not_echo_amount(self):
        self.write([self.row("987654.32", vendor="PRIVATE-CLIENT-731")])
        self.alter("amount", "987654.33")
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(["--source", str(self.source), "--report", str(self.report)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("HOLD", stderr.getvalue())
        self.assertNotIn("987654", stderr.getvalue())
        self.assertNotIn("PRIVATE-CLIENT-731", stderr.getvalue())
        self.assertNotIn(str(self.root), stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
