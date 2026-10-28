import tempfile
import unittest
from pathlib import Path
from ledger_bridge import reconcile, read_ledger, parse_money, render_html


class LedgerBridgeTests(unittest.TestCase):
    def test_exact_matches_before_unique_amount_date(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a, b = root / "a.csv", root / "b.csv"
            a.write_text("date,amount,reference\n2026-01-01,50.00,INV-1\n"
                         "2026-01-02,100.00,\n2026-01-05,200.00,X\n", encoding="utf-8")
            b.write_text("date,amount,reference\n2026-02-01,50.00,INV1\n"
                         "2026-01-03,100.00,Y\n2026-01-05,250.00,Z\n", encoding="utf-8")
            result = reconcile(a, b)
            self.assertEqual(result["counts"]["matched"], 2)
            self.assertEqual(result["counts"]["unmatched_left"], 1)
            self.assertEqual(result["counts"]["unmatched_right"], 1)
            self.assertEqual({m["basis"] for m in result["matches"]},
                             {"EXACT_REFERENCE_AND_AMOUNT", "UNIQUE_AMOUNT_AND_DATE"})

    def test_ambiguous_transaction_not_silently_matched(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            a, b = root / "a.csv", root / "b.csv"
            a.write_text("date,amount\n2026-01-02,20\n2026-01-02,20\n", encoding="utf-8")
            b.write_text("date,amount\n2026-01-02,20\n", encoding="utf-8")
            result = reconcile(a, b)
            self.assertEqual(result["counts"]["matched"], 0)
            self.assertEqual(result["ambiguous_left_rows"], [2, 3])

    def test_debit_credit_and_reversing_sign(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "statement.csv"
            p.write_text("date,debit,credit\n2026-01-01,12.00,\n", encoding="utf-8")
            rows, errors = read_ledger(p)
            self.assertEqual(str(rows[0]["amount"]), "-12.00")
            self.assertFalse(errors)
            rows, _ = read_ledger(p, flip_sign=True)
            self.assertEqual(str(rows[0]["amount"]), "12.00")

    def test_bad_amount_and_missing_fields(self):
        with self.assertRaises(ValueError):
            parse_money("NaN")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ledger.csv"
            p.write_text("reference,amount\nINV1,12.00\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                read_ledger(p)

    def test_html_escapes_untrusted_reference(self):
        report = {"status": "REVIEW", "disclaimer": "Review",
                  "counts": {}, "totals_by_currency": {},
                  "unmatched_left":[{"row":2,"date":"2026-01-01","amount":"10",
                                     "currency":"USD","reference":"<script>"}],
                  "unmatched_right":[]}
        self.assertNotIn("<script>", render_html(report))
        self.assertIn("&lt;script&gt;", render_html(report))


if __name__ == "__main__":
    unittest.main()
