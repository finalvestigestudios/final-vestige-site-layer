"""Regression cases for Payment Sentinel's complete CSV-to-report path."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ap_input_guard
import payment_sentinel
from payment_sentinel import report_html, review


class PaymentImportSafetyTests(unittest.TestCase):
    def make(self, folder, body):
        path = Path(folder) / "payments.csv"
        path.write_text(body, encoding="utf-8")
        return path

    def test_ambiguous_amount_aliases_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder,
                "Vendor,Invoice,Amount,Payment Amount,Date\n"
                "Acme,INV-1,10.00,900.00,2026-10-01\n")
            with self.assertRaisesRegex(ValueError, "Ambiguous amount"):
                review(path)

    def test_duplicate_case_insensitive_headers_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder,
                "Vendor,vendor,Invoice,Amount,Date\n"
                "Acme,Acme,INV-1,10.00,2026-10-01\n")
            with self.assertRaisesRegex(ValueError, "Repeated CSV column"):
                review(path)

    def test_blank_header_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder,
                "Vendor,,Invoice,Amount,Date\n"
                "Acme,ignored,INV-1,10.00,2026-10-01\n")
            with self.assertRaisesRegex(ValueError, "blank column heading"):
                review(path)

    def test_zero_payment_rows_are_incomplete_not_clean(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder, "Vendor,Invoice,Amount,Date\n")
            result = review(path)
            self.assertEqual(result["status"], "INCOMPLETE")
            self.assertEqual(result["records_reviewed"], 0)
            self.assertEqual(result["flags"], [])
            self.assertEqual(len(result["source_sha256"]), 64)
            self.assertEqual(result["source_bytes"], path.stat().st_size)

    def test_unicode_vendor_keys_do_not_collapse_to_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder,
                "Vendor,Invoice,Amount,Date\n"
                "株式会社A,INV-1,10.00,2026-10-01\n"
                "株式会社B,INV-1,10.00,2026-10-02\n")
            result = review(path)
            self.assertEqual(result["records_reviewed"], 2)
            self.assertEqual(result["status"], "NO_FLAGS")
            self.assertFalse(any(f["rule"] == "REPEATED_INVOICE" for f in result["flags"]))

    def test_nonsearchable_invoice_is_excluded_and_flagged(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder,
                "Vendor,Invoice,Amount,Date\n"
                "Acme,!!!,10.00,2026-10-01\n"
                "Acme,INV-2,10.00,2026-10-02\n")
            result = review(path)
            self.assertEqual(result["rows_excluded"], 1)
            self.assertEqual(result["status"], "REVIEW")
            self.assertIn("INVALID_INPUT", {f["rule"] for f in result["flags"]})

    def test_multiline_csv_provenance_uses_physical_start_line(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder,
                'Vendor,Invoice,Amount,Date\n'
                '"Vendor\nCorp",INV-1,10.00,2026-10-01\n'
                '"Vendor\nCorp",INV-1,10.00,2026-10-02\n')
            result = review(path)
            matches = [f for f in result["flags"] if f["rule"] == "REPEATED_INVOICE"]
            self.assertEqual(len(matches), 1)
            self.assertEqual(matches[0]["rows"], [2, 4])

    def test_modification_during_analysis_aborts_report(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder, "Vendor,Invoice,Amount,Date\nAcme,X,10,2026-10-01\n")

            def tamper(source):
                source.write_text("Vendor,Invoice,Amount,Date\nAcme,X,99,2026-10-01\n",
                                  encoding="utf-8")
                return [], []

            with patch.object(payment_sentinel, "load_payments", side_effect=tamper):
                with self.assertRaisesRegex(ValueError, "changed while processing"):
                    review(path)

    def test_payments_limit_rejects_partial_reviews(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder,
                "Vendor,Invoice,Amount,Date\n"
                "Acme,X1,10.00,2026-10-01\n"
                "Acme,X2,20.00,2026-10-02\n")
            with patch.object(payment_sentinel, "MAX_PAYMENTS", 1):
                with self.assertRaisesRegex(ValueError, "review limit"):
                    review(path)

    def test_size_limit_rejects_unbounded_import(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder, "Vendor,Invoice,Amount,Date\n")
            with patch.object(ap_input_guard, "MAX_SOURCE_BYTES", 8):
                with self.assertRaisesRegex(ValueError, "safe import limit"):
                    review(path)

    def test_reports_include_provenance_without_raw_bank_data(self):
        with tempfile.TemporaryDirectory() as folder:
            path = self.make(folder,
                "Vendor,Invoice,Amount,Date,Bank Account\n"
                "Acme,INV-1,10.00,2026-10-01,123456789\n"
                "Acme,INV-1,10.00,2026-10-02,123456789\n")
            result = review(path)
            html = report_html(result)
            self.assertIn(result["source_sha256"], html)
            self.assertIn("REVIEW", html)
            self.assertNotIn("123456789", html)
            self.assertNotIn("123456789", str(result))


if __name__ == "__main__":
    unittest.main()
