"""R23: procurement quantities must not silently change due to lossy parsing.

Synthetic data only. All results are review findings, never payment approval.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from fvs_suite import engine


class QuantityLexicalIntegrityR23(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-qty-r23-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def csvfile(self, name, columns, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            writer.writerows(rows)
        return str(path)

    def inputs(self, po_quantity="10", invoice_quantity="10", receipt_quantity="10"):
        po = self.csvfile(
            "po.csv", ("po_number", "line", "quantity", "unit_price"),
            [("P1", "1", po_quantity, "1.25")])
        invoices = self.csvfile(
            "invoices.csv", ("po_number", "line", "quantity", "unit_price"),
            [("P1", "1", invoice_quantity, "1.25")])
        receipts = self.csvfile(
            "receipts.csv", ("po_number", "line", "quantity"),
            [("P1", "1", receipt_quantity)])
        return po, invoices, receipts

    def assert_no_report(self):
        self.assertFalse(list(self.root.glob("procurement-three-way-*.csv")))
        self.assertFalse(list(self.root.glob("evidence-manifest-*.txt")))

    def test_valid_plain_grouped_and_fractional_quantities_are_exact(self):
        values = {
            "1,000,000.125": Decimal("1000000.125"),
            "1,000": Decimal("1000"),
            ".5": Decimal("0.5"),
            "+1.25": Decimal("1.25"),
            "0.00000001": Decimal("0.00000001"),
            "1.0000000000": Decimal("1.0000000000"),
            "0": Decimal("0"),
            "1.": Decimal("1"),
            "1,000,000,000": Decimal("1000000000"),
        }
        for source, expected in values.items():
            with self.subTest(source=source):
                self.assertEqual(engine.qty(source), expected)

    def test_bad_grouping_or_exponents_never_change_quantity(self):
        for source in (
            "1,2,3", "1,00", "1,2345", "12,34.56", "1,,000",
            "1,000,00", "1e3", "2E2", "1e-2", "1 000", "1.2.3"
        ):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    engine.qty(source)

    def test_negative_currency_unicode_and_nonfinite_fail_closed(self):
        for source in (
            "-1", "-0", "($1)", "$10", "NaN", "Infinity", ".",
            "٠١٢", "＋1", "1+", "--1", "", "  "
        ):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    engine.qty(source)

    def test_precision_bounds_and_nonstring_binary_floats(self):
        for source in ("0.000000001", "1.000000001", "1,000,000,001",
                       "1,000,000,000.01", "1" * 81, 0.1, True):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    engine.qty(source)

    def test_errors_do_not_echo_private_quantity_text(self):
        secret = "CUSTOMER_DO_NOT_LOG_0000123"
        with self.assertRaises(ValueError) as caught:
            engine.qty(secret)
        self.assertNotIn(secret, str(caught.exception))

    def test_grouped_quantity_reconciles_exactly_offline(self):
        sources = self.inputs("1,000", "1,000", "1,000")
        outputs = engine.procure_guard(*sources, str(self.root))
        self.assertEqual(len(outputs), 2)
        with outputs[0].open(encoding="utf-8-sig", newline="") as stream:
            report = list(csv.DictReader(stream))
        self.assertEqual(len(report), 1)
        row = report[0]
        self.assertEqual(row["po_qty"], "1000")
        self.assertEqual(row["invoiced_qty"], "1000")
        self.assertEqual(row["received_qty"], "1000")
        self.assertEqual(row["invoice_total"], "1250.00")
        self.assertEqual(row["status"], "matched")
        self.assertEqual(row["po_rows"], "2")
        self.assertEqual(row["invoice_rows"], "2")
        self.assertEqual(row["receipt_rows"], "2")

    def test_bad_purchase_order_quantity_blocks_export(self):
        sources = self.inputs("1,2,3")
        before = Path(sources[0]).read_bytes()
        with self.assertRaisesRegex(ValueError, "quantity"):
            engine.procure_guard(*sources, str(self.root))
        self.assertEqual(Path(sources[0]).read_bytes(), before)
        self.assert_no_report()

    def test_bad_invoice_quantity_blocks_export(self):
        sources = self.inputs("10", "1e1")
        with self.assertRaisesRegex(ValueError, "quantity"):
            engine.procure_guard(*sources, str(self.root))
        self.assert_no_report()

    def test_bad_receipt_quantity_blocks_export(self):
        sources = self.inputs("10", "10", "1,0")
        with self.assertRaisesRegex(ValueError, "quantity"):
            engine.procure_guard(*sources, str(self.root))
        self.assert_no_report()

    def test_excess_precision_blocks_export(self):
        sources = self.inputs("0.000000001", "0.000000001", "0.000000001")
        with self.assertRaisesRegex(ValueError, "precision"):
            engine.procure_guard(*sources, str(self.root))
        self.assert_no_report()

    def test_invalid_later_group_never_leaves_partial_audit(self):
        po = self.csvfile("po.csv", ("po_number", "line", "quantity", "unit_price"),
                          [("P1", "1", "10", "1.25"),
                           ("P2", "1", "1,2,3", "1.25")])
        invoices = self.csvfile("invoices.csv",
                                ("po_number", "line", "quantity", "unit_price"),
                                [("P1", "1", "10", "1.25"),
                                 ("P2", "1", "123", "1.25")])
        receipts = self.csvfile("receipts.csv", ("po_number", "line", "quantity"),
                                [("P1", "1", "10"), ("P2", "1", "123")])
        with self.assertRaises(ValueError):
            engine.procure_guard(po, invoices, receipts, str(self.root))
        self.assert_no_report()

    def test_credit_and_return_still_require_human_review(self):
        po = self.csvfile("po.csv", ("po_number", "line", "quantity", "unit_price"),
                          [("P1", "1", "1,000", "1.25")])
        invoices = self.csvfile(
            "invoices.csv",
            ("po_number", "line", "quantity", "unit_price",
             "event_type", "document_id", "related_document"),
            [("P1", "1", "1,000", "1.25", "invoice", "INV1", ""),
             ("P1", "1", "200", "1.25", "credit", "CM1", "INV1")])
        receipts = self.csvfile(
            "receipts.csv",
            ("po_number", "line", "quantity",
             "event_type", "document_id", "related_document"),
            [("P1", "1", "1,000", "receipt", "R1", ""),
             ("P1", "1", "200", "return", "RR1", "R1")])
        output, _ = engine.procure_guard(po, invoices, receipts, str(self.root))
        with output.open(encoding="utf-8-sig", newline="") as stream:
            row = list(csv.DictReader(stream))[0]
        self.assertEqual(row["invoiced_qty"], "800")
        self.assertEqual(row["received_qty"], "800")
        self.assertEqual(row["credit_qty"], "200")
        self.assertIn("credit_memo_review", row["status"])
        self.assertIn("return_review", row["status"])
        self.assertNotEqual(row["status"], "matched")


if __name__ == "__main__":
    unittest.main()
