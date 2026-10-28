"""R22: malformed accounting syntax must never silently change a financial amount."""
from __future__ import annotations

import csv
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from fvs_suite import engine


class AmountLexicalIntegrityR22(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-money-r22-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def csvfile(self, name, headers, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)
        return str(path)

    def assert_no_reports(self, pattern):
        self.assertEqual(list(self.root.glob(pattern)), [],
                         "Malformed financial input must not create an audit report")

    def test_standard_accounting_notation_is_exact(self):
        cases = {
            "($1,234.56)": "-1234.56",
            "$1,234.56": "1234.56",
            "-$12.34": "-12.34",
            "$-12.34": "-12.34",
            "+1234.56": "1234.56",
            "1,234.56": "1234.56",
            "0.005": "0.01",
            ".50": "0.50",
            "1.": "1.00",
            "  ( $0.01 )  ": "-0.01",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(engine.money(source), Decimal(expected))

    def test_malformed_lexemes_do_not_flip_sign_or_reorder_magnitude(self):
        invalid = (
            "(12.34", "12.34)", ")12.34(", "((12.34))",
            "($-12.34)", "($+12.34)", "1,00", "1,2,3", "12,34.56",
            "$1$2", "1e3", "1 000", "-", "+", ".", "NaN",
            "Infinity", "", "$()", "--123", "1..1", "1,234,56",
            "2.3.4", "(1,000.00)-", "0" * 100, "1,2345.00",
        )
        for source in invalid:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    engine.money(source)

    def test_unit_cost_retains_subcent_precision_and_rejects_bad_syntax(self):
        self.assertEqual(engine.unit_cost("0.00000001"), Decimal("0.00000001"))
        with self.assertRaisesRegex(ValueError, "precision exceeds eight"):
            engine.unit_cost("0.000000001")
        for source in ("($10.00", "($-10.00)", "10,01"):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    engine.unit_cost(source)

    def test_bounds_and_error_messages_do_not_echo_sensitive_input(self):
        self.assertEqual(engine.money("1,000,000,000,000"),
                         Decimal("1000000000000.00"))
        with self.assertRaisesRegex(ValueError, "out-of-range"):
            engine.money("1,000,000,000,000.01")
        with self.assertRaises(ValueError) as caught:
            engine.money("CONFIDENTIAL_CLIENT_FINANCIAL_DATA")
        self.assertNotIn("CONFIDENTIAL_CLIENT_FINANCIAL_DATA", str(caught.exception))

    def test_ledger_diff_rejects_unclosed_negative_without_writing_report(self):
        left = self.csvfile("ledger-left.csv", ("id", "amount"), [("A", "(100.00")])
        right = self.csvfile("ledger-right.csv", ("id", "amount"), [("A", "100.00")])
        with self.assertRaises(ValueError):
            engine.ledger_diff(left, right, str(self.root))
        self.assert_no_reports("ledger-diff-*.csv")

    def test_invoice_twins_rejects_bad_grouping_without_writing_report(self):
        invoices = self.csvfile("invoices.csv",
                                ("vendor", "invoice_number", "amount", "date"),
                                [("ACME", "INV-1", "1,2,3", "2026-01-01"),
                                 ("ACME", "INV-1", "123", "2026-01-02")])
        with self.assertRaises(ValueError):
            engine.invoice_twins(invoices, str(self.root))
        self.assert_no_reports("invoice-twins-*.csv")

    def test_spend_map_rejects_partial_negative_without_writing_report(self):
        spend = self.csvfile("spend.csv", ("vendor", "amount", "date"),
                             [("ACME", "40.00)", "2026-01-01")])
        with self.assertRaises(ValueError):
            engine.spend_map(spend, str(self.root))
        self.assert_no_reports("spend-map-*.csv")

    def test_grant_audit_rejects_corrupt_claim_before_evidence_export(self):
        claims = self.csvfile("claims.csv", ("id", "amount", "program"),
                              [("A", "($100.00", "G1")])
        ledger = self.csvfile("grant-ledger.csv", ("id", "amount", "program"),
                              [("A", "100.00", "G1")])
        budgets = self.csvfile("budgets.csv", ("program", "budget"),
                               [("G1", "200.00")])
        with self.assertRaises(ValueError):
            engine.grant_audit(claims, ledger, budgets, str(self.root))
        self.assert_no_reports("grant-audit-exceptions-*.csv")
        self.assert_no_reports("evidence-manifest-*.txt")

    def test_procure_guard_rejects_corrupt_unit_price_before_export(self):
        orders = self.csvfile("purchase-orders.csv",
                              ("po_number", "line", "quantity", "unit_price"),
                              [("PO1", "1", "2", "10.00")])
        invoices = self.csvfile("procure-invoices.csv",
                                ("po_number", "line", "quantity", "unit_price"),
                                [("PO1", "1", "2", "$-($10.00)")])
        receipts = self.csvfile("receipts.csv",
                                ("po_number", "line", "quantity"),
                                [("PO1", "1", "2")])
        with self.assertRaises(ValueError):
            engine.procure_guard(orders, invoices, receipts, str(self.root))
        self.assert_no_reports("procurement-three-way-*.csv")


if __name__ == "__main__":
    unittest.main()
