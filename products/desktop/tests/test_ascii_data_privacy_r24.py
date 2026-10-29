"""R24: reject ambiguous non-ASCII numeric/date lexemes and redact invalid dates.

Synthetic financial data only. Findings always require human review.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from fvs_suite import engine


class AsciiDataPrivacyR24(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-ascii-r24-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def csvfile(self, name, columns, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            writer.writerows(rows)
        return str(path)

    def assert_no_output(self, prefix):
        self.assertFalse(list(self.root.glob(prefix + "-*.csv")))
        self.assertFalse(list(self.root.glob("evidence-manifest-*.txt")))

    def test_ascii_accounting_grammar_retains_precision_and_sign(self):
        self.assertEqual(engine._exact_amount("$1,234.50"), Decimal("1234.50"))
        self.assertEqual(engine._exact_amount("($1,234.50)"), Decimal("-1234.50"))
        self.assertEqual(engine.money("-.005"), Decimal("-0.01"))
        self.assertEqual(engine.unit_cost("0.12345678"), Decimal("0.12345678"))

    def test_unicode_digits_are_not_treated_as_ascii_money(self):
        for source in ("١٢٣.٤٥", "１２３.４５", "१२३", "$٤.٥", "１２,３４５"):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    engine.money(source)

    def test_money_rejects_binary_floats_and_boolean_values(self):
        for source in (0.1, 1.0, True, False):
            with self.subTest(source=repr(source)):
                with self.assertRaisesRegex(ValueError, "Invalid amount format"):
                    engine.money(source)

    def test_unit_cost_rejects_unicode_digits(self):
        with self.assertRaises(ValueError):
            engine.unit_cost("٣.٢٥")

    def test_ascii_calendar_forms_remain_supported(self):
        for source, expected in (
            ("2026-10-28", "2026-10-28"),
            ("2026-1-2", "2026-01-02"),
            ("10/28/2026", "2026-10-28"),
            ("1/2/2026", "2026-01-02"),
            ("10/28/26", "2026-10-28"),
        ):
            with self.subTest(source=source):
                self.assertEqual(engine.parse_date(source).isoformat(), expected)

    def test_non_ascii_and_malformed_dates_fail_closed(self):
        for source in (
            "２０２６-１０-２８", "٢٠٢٦-١٠-٢٨", "2026-10-２８",
            "2026/10/28", "2026-13-01", "02/30/2026",
            "2026-10-28T10:00:00", "10/28/2", "",
        ):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    engine.parse_date(source)

    def test_invalid_date_error_does_not_echo_private_text(self):
        sensitive = "PRIVATE_CUSTOMER_DATE_DO_NOT_ECHO"
        with self.assertRaises(ValueError) as caught:
            engine.parse_date(sensitive)
        self.assertNotIn(sensitive, str(caught.exception))

    def test_invalid_amount_error_does_not_echo_private_text(self):
        sensitive = "PRIVATE_CUSTOMER_AMOUNT_DO_NOT_ECHO"
        with self.assertRaises(ValueError) as caught:
            engine.money(sensitive)
        self.assertNotIn(sensitive, str(caught.exception))

    def test_invoice_twin_bad_date_never_writes_review_report(self):
        source = self.csvfile(
            "invoices.csv", ("vendor", "invoice_number", "amount", "date"),
            [("Example Vendor", "A1", "25.00", "2026-10-28"),
             ("Example Vendor", "A2", "25.00", "٢٠٢٦-١٠-٢٨")],
        )
        original = Path(source).read_bytes()
        with self.assertRaisesRegex(ValueError, "Invalid date"):
            engine.invoice_twins(source, str(self.root))
        self.assertEqual(Path(source).read_bytes(), original)
        self.assert_no_output("invoice-twins")

    def test_spend_map_bad_date_never_writes_report(self):
        source = self.csvfile(
            "spend.csv", ("vendor", "amount", "date", "category"),
            [("Example Vendor", "25.00", "２０２６-１０-２８", "Office")],
        )
        with self.assertRaisesRegex(ValueError, "Invalid date"):
            engine.spend_map(source, str(self.root))
        self.assert_no_output("spend-map")

    def test_ledger_diff_rejects_unicode_amount_without_export(self):
        left = self.csvfile("left.csv", ("id", "amount"), [("T1", "١٢٣.٤٥")])
        right = self.csvfile("right.csv", ("id", "amount"), [("T1", "123.45")])
        with self.assertRaises(ValueError):
            engine.ledger_diff(left, right, str(self.root))
        self.assert_no_output("ledger-diff")

    def test_grant_budget_rejects_unicode_amount_without_export(self):
        claims = self.csvfile(
            "claims.csv", ("id", "amount", "program"), [("C1", "50", "G1")])
        ledger = self.csvfile(
            "ledger.csv", ("id", "amount", "program"), [("C1", "50", "G1")])
        budgets = self.csvfile(
            "budgets.csv", ("program", "budget"), [("G1", "١٠٠٠")])
        with self.assertRaises(ValueError):
            engine.grant_audit(claims, ledger, budgets, str(self.root))
        self.assert_no_output("grant-audit-exceptions")
        self.assert_no_output("grant-budget-check")

    def test_procurement_unicode_unit_price_blocks_report(self):
        po = self.csvfile(
            "po.csv", ("po_number", "line", "quantity", "unit_price"),
            [("P1", "1", "10", "١.٢٥")])
        invoices = self.csvfile(
            "invoices.csv", ("po_number", "line", "quantity", "unit_price"),
            [("P1", "1", "10", "1.25")])
        receipts = self.csvfile(
            "receipts.csv", ("po_number", "line", "quantity"),
            [("P1", "1", "10")])
        with self.assertRaises(ValueError):
            engine.procure_guard(po, invoices, receipts, str(self.root))
        self.assert_no_output("procurement-three-way")

    def test_normal_ascii_invoice_inputs_still_produce_review_findings(self):
        source = self.csvfile(
            "invoices.csv", ("vendor", "invoice_number", "amount", "date"),
            [("Example Vendor", "A1", "25.00", "2026-10-28"),
             ("Example Vendor", "A2", "25.00", "10/28/2026")],
        )
        outputs = engine.invoice_twins(source, str(self.root))
        self.assertEqual(len(outputs), 1)
        with outputs[0].open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "review_possible_duplicate")


if __name__ == "__main__":
    unittest.main()
