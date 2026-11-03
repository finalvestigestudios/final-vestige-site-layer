"""R159 native SpendMap report-envelope spoofing regression tests.

All values are synthetic and temporary. We generate real SpendMap exports,
modify their CSV envelope, and require independent offline verification to HOLD.
"""
from __future__ import annotations

import contextlib
import csv
import inspect
import io
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine, spend_report_envelope
from fvs_suite.spend_evidence_verify import main, verify_membership


class SpendEnvelopeR159(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r159-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "source.csv"
        self.report = self.root / "report.csv"

    @staticmethod
    def row(vendor="ACME", amount="10.00", month=1, category="Parts", note=""):
        return (vendor, amount, f"2026-{month:02d}-01", category, note)

    def write(self, rows):
        with self.source.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(rows)
        self.report = Path(engine.spend_map(self.source, self.root)[0])
        return verify_membership(self.source, self.report)

    def read(self):
        with self.report.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            return list(reader.fieldnames), list(reader)

    def rewrite(self, headers, rows):
        with self.report.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def hold(self):
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_generated_schema_has_exact_25_fields(self):
        self.write([self.row()])
        header, rows = self.read()
        self.assertEqual(tuple(header), spend_report_envelope.COLUMNS)
        self.assertEqual((len(header), len(rows)), (25, 1))

    def test_unsorted_import_yields_verified_native_order(self):
        receipt = self.write([self.row("ZULU", month=4, category="Services"),
                              self.row("ACME", month=2, category="Parts"),
                              self.row("ACME", month=1, category="Services")])
        self.assertEqual(receipt.buckets_verified, 3)
        self.assertEqual([(r["vendor_key"], r["month"]) for r in self.read()[1]],
                         [("ACME", "2026-01"), ("ACME", "2026-02"),
                          ("ZULU", "2026-04")])

    def test_native_formula_safe_categories_verified(self):
        receipt = self.write([self.row(category="Parts"),
                              self.row(category="=1+1"),
                              self.row(category="+SUM(A1:A2)")])
        self.assertEqual(receipt.buckets_verified, 3)

    def test_mixed_credit_export_verified(self):
        receipt = self.write([self.row(amount="150.00", category="Parts"),
                              self.row(amount="-140.00", category="Services")])
        self.assertEqual(receipt.groups_verified, 1)

    def test_quoted_multiline_source_verified(self):
        receipt = self.write([self.row(note="two\nphysical lines"),
                              self.row(month=2, category="Services")])
        self.assertEqual(receipt.buckets_verified, 2)

    def test_schema_contract_does_not_import_generator(self):
        source = inspect.getsource(spend_report_envelope)
        self.assertNotIn("import engine", source)
        self.assertNotIn("summarize_spend", source)
        self.assertNotIn("requests", source)

    def test_added_payment_approved_column_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers.append("payment_approved")
        rows[0]["payment_approved"] = "yes"
        self.rewrite(headers, rows)
        self.hold()

    def test_added_compliance_verdict_column_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers.insert(0, "compliance_approved")
        rows[0]["compliance_approved"] = "true"
        self.rewrite(headers, rows)
        self.hold()

    def test_added_fraud_determination_column_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers.append("fraud_status")
        rows[0]["fraud_status"] = "no_fraud"
        self.rewrite(headers, rows)
        self.hold()

    def test_added_blank_notes_column_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers.append("notes")
        rows[0]["notes"] = ""
        self.rewrite(headers, rows)
        self.hold()

    def test_added_zero_width_claim_column_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers.append("approved\u200b")
        rows[0]["approved\u200b"] = "yes"
        self.rewrite(headers, rows)
        self.hold()

    def test_embedded_bom_header_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        old = headers[1]
        headers[1] = "\ufeff" + old
        rows[0][headers[1]] = rows[0].pop(old)
        self.rewrite(headers, rows)
        self.hold()

    def test_swapped_amount_and_flag_headers_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers[3], headers[4] = headers[4], headers[3]
        self.rewrite(headers, rows)
        self.hold()

    def test_reversed_headers_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        self.rewrite(list(reversed(headers)), rows)
        self.hold()

    def test_duplicate_header_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers[-1] = headers[-2]
        self.rewrite(headers, rows)
        self.hold()

    def test_missing_flag_header_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers.remove("flag")
        self.rewrite(headers, rows)
        self.hold()

    def test_blank_extra_header_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers.append("")
        rows[0][""] = "spoof"
        self.rewrite(headers, rows)
        self.hold()

    def test_space_suffix_vendor_header_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers[0] = "vendor_key "
        rows[0]["vendor_key "] = rows[0].pop("vendor_key")
        self.rewrite(headers, rows)
        self.hold()

    def test_uppercase_vendor_header_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers[0] = "VENDOR_KEY"
        rows[0]["VENDOR_KEY"] = rows[0].pop("vendor_key")
        self.rewrite(headers, rows)
        self.hold()

    def test_unicode_confusable_amount_header_holds(self):
        self.write([self.row()])
        headers, rows = self.read()
        headers[3] = "amоunt"  # Cyrillic o, not ASCII o
        rows[0]["amоunt"] = rows[0].pop("amount")
        self.rewrite(headers, rows)
        self.hold()

    def test_two_category_rows_swapped_holds(self):
        self.write([self.row(category="Parts"), self.row(category="Services")])
        headers, rows = self.read()
        self.rewrite(headers, list(reversed(rows)))
        self.hold()

    def test_two_month_rows_swapped_holds(self):
        self.write([self.row(month=1), self.row(month=2)])
        headers, rows = self.read()
        self.rewrite(headers, list(reversed(rows)))
        self.hold()

    def test_different_vendor_rows_swapped_holds(self):
        self.write([self.row(vendor="AAA"), self.row(vendor="ZZZ")])
        headers, rows = self.read()
        self.rewrite(headers, list(reversed(rows)))
        self.hold()

    def test_middle_row_reordered_holds(self):
        self.write([self.row(month=1), self.row(month=2), self.row(month=3)])
        headers, rows = self.read()
        rows[1], rows[2] = rows[2], rows[1]
        self.rewrite(headers, rows)
        self.hold()

    def test_unchanged_files_after_success(self):
        self.write([self.row(note="SYNTHETIC PRIVATE")])
        snapshots = self.source.read_bytes(), self.report.read_bytes()
        verify_membership(self.source, self.report)
        self.assertEqual(snapshots, (self.source.read_bytes(), self.report.read_bytes()))

    def test_failed_extra_column_cli_redacts_private_value(self):
        self.write([self.row(vendor="PRIVATESYNTHETIC")])
        headers, rows = self.read()
        headers.append("internal_client_secret")
        rows[0]["internal_client_secret"] = "SYNTHETIC-ACCOUNT-123"
        self.rewrite(headers, rows)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--source", str(self.source), "--report", str(self.report)])
        self.assertEqual(code, 1)
        self.assertIn("HOLD", err.getvalue())
        self.assertNotIn("SYNTHETIC-ACCOUNT-123", out.getvalue() + err.getvalue())
        self.assertNotIn(str(self.root), out.getvalue() + err.getvalue())


if __name__ == "__main__":
    unittest.main()
