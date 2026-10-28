import tempfile
import unittest
from pathlib import Path
from payment_sentinel import parse_amount, parse_date, report_html, review


class PaymentSentinelTests(unittest.TestCase):
    def test_duplicate_invoice_same_amount_and_change_account(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ap.csv"
            p.write_text(
                "Vendor,Invoice Number,Payment Amount,Payment Date,Bank Account\n"
                "Acme,INV-001,100.00,2026-01-01,1234567\n"
                "Acme,INV001,100.00,2026-01-02,1234567\n"
                "Acme,INV-002,100.00,2026-01-03,7654321\n"
                "Acme,INV-003,NaN,2026-01-05,7654321\n", encoding="utf-8")
            r = review(p)
            rules = [f["rule"] for f in r["flags"]]
            self.assertIn("REPEATED_INVOICE", rules)
            self.assertIn("SAME_AMOUNT_NEAR_DATE", rules)
            self.assertIn("MULTIPLE_VENDOR_ACCOUNTS", rules)
            self.assertIn("INVALID_INPUT", rules)
            self.assertEqual(r["rows_excluded"], 1)
            self.assertNotIn("1234567", str(r))
            self.assertNotIn("7654321", str(r))

    def test_high_amount_with_repeated_small_vendor_payments(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ap.csv"
            rows = ["Vendor,Invoice,Amount,Date"]
            rows.extend(f"Supplier,I-{i},50.00,2026-01-{i:02d}" for i in range(1, 7))
            rows.append("Supplier,I-7,500.00,2026-01-07")
            p.write_text("\n".join(rows) + "\n", encoding="utf-8")
            r = review(p)
            self.assertIn("VENDOR_AMOUNT_OUTLIER", {f["rule"] for f in r["flags"]})

    def test_amount_validation_and_dates(self):
        self.assertEqual(str(parse_amount("($1,234.50)")), "-1234.50")
        for value in ("NaN", "Infinity", "1.1234", "none"):
            with self.assertRaises(ValueError):
                parse_amount(value)
        self.assertEqual(parse_date("10/27/2026").isoformat(), "2026-10-27")

    def test_missing_columns_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ap.csv"
            p.write_text("vendor,amount\nAcme,5\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                review(p)

    def test_html_output_is_escaped(self):
        r = {"flags":[{"severity":"HIGH","rule":"TEST","rows":[1],
                        "reason":"<script>alert(1)</script>"}],
             "records_reviewed":1,"rows_excluded":0,"disclaimer":"Reviewer decision only."}
        self.assertNotIn("<script>", report_html(r))
        self.assertIn("&lt;script&gt;", report_html(r))


if __name__ == "__main__":
    unittest.main()
