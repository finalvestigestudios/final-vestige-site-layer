"""R84: procurement fixed-point arithmetic must never obey a lossy ambient context.

Synthetic, offline source tests. Full repository/Windows execution is a release
prerequisite; an isolated preflight cannot substitute for these methods.
"""
from __future__ import annotations

import csv
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN, localcontext
from pathlib import Path
import tempfile
import unittest

from fvs_suite import engine, procurement

Q = "999999999.99999999"
P = "999999999999.99999999"


def exact_product(quantity=Q, price=P):
    # Build the oracle in a deliberately higher-precision *test* context.
    with localcontext() as context:
        context.prec = 100
        return Decimal(quantity) * Decimal(price)


class ProcurementDecimalContextR84(unittest.TestCase):
    def review(self, *, quantity=Q, price=P, order_price=P, invoices=None):
        po = [{"quantity": quantity, "unit_price": order_price}]
        if invoices is None:
            invoices = [{"quantity": quantity, "unit_price": price,
                         "event_type": "invoice", "document_id": "INV-1"}]
        receipts = [{"quantity": quantity, "event_type": "receipt",
                     "document_id": "REC-1"}]
        return procurement.review_line(
            po, invoices, receipts, quantity=engine.qty,
            unit_cost=engine.unit_cost, identifier=engine.key,
            policy=procurement.PricePolicy())

    def test_default_28_digit_context_actually_loses_source_evidence(self):
        with localcontext() as context:
            context.prec = 28
            rounded = Decimal(Q) * Decimal(P)
        self.assertNotEqual(format(rounded, "f"), format(exact_product(), "f"))

    def test_review_exact_at_default_decimal_precision(self):
        metrics, flags = self.review()
        self.assertEqual(metrics["invoice_total_exact"], format(exact_product(), "f"))
        self.assertEqual(metrics["gross_invoice_total_exact"], format(exact_product(), "f"))
        self.assertEqual(flags, [])

    def test_review_exact_at_low_ambient_precision(self):
        for precision in (6, 12, 28):
            with self.subTest(precision=precision), localcontext() as context:
                context.prec = precision
                metrics, flags = self.review()
                self.assertEqual(metrics["invoice_total_exact"],
                                 format(exact_product(), "f"))
                self.assertEqual(flags, [])

    def test_review_exact_under_alternate_rounding(self):
        for rounding in (ROUND_DOWN, ROUND_HALF_EVEN):
            with self.subTest(rounding=rounding), localcontext() as context:
                context.prec = 8
                context.rounding = rounding
                metrics, _ = self.review()
                self.assertEqual(metrics["invoice_total_exact"],
                                 format(exact_product(), "f"))

    def test_review_does_not_change_callers_context(self):
        for precision in (6, 28, 80):
            with self.subTest(precision=precision), localcontext() as context:
                context.prec = precision
                context.rounding = ROUND_DOWN
                self.review()
                self.assertEqual(context.prec, precision)
                self.assertEqual(context.rounding, ROUND_DOWN)

    def test_display_large_amount_with_low_context(self):
        with localcontext() as context:
            context.prec = 6
            displayed = procurement._display_money(exact_product())
        self.assertEqual(displayed, "999999999999999989990.00")

    def test_display_half_cent_policy_unchanged(self):
        for source, expected in (("0.005", "0.01"),
                                 ("-0.005", "-0.01"),
                                 ("0.015", "0.02")):
            with self.subTest(source=source):
                self.assertEqual(procurement._display_money(Decimal(source)), expected)

    def test_exact_subcent_low_magnitude_survives(self):
        metrics, flags = self.review(quantity="0.00000001", price="0.00000001",
                                     order_price="0.00000001")
        self.assertEqual(metrics["invoice_total_exact"], "0.0000000000000001")
        self.assertEqual(flags, [])

    def test_gross_large_addition_keeps_subcent_suffix(self):
        invoice_rows = [
            {"quantity": Q, "unit_price": P,
             "event_type": "invoice", "document_id": "INV-1"},
            {"quantity": Q, "unit_price": P,
             "event_type": "invoice", "document_id": "INV-2"},
        ]
        metrics, flags = self.review(invoices=invoice_rows)
        with localcontext() as context:
            context.prec = 100
            expected = exact_product() * Decimal(2)
        self.assertEqual(metrics["gross_invoice_total_exact"], format(expected, "f"))
        self.assertIn("invoiced_above_order", flags)

    def test_equal_credit_preserves_exact_gross_and_zero_net(self):
        invoice_rows = [
            {"quantity": Q, "unit_price": P, "event_type": "invoice",
             "document_id": "INV-1"},
            {"quantity": Q, "unit_price": P, "event_type": "credit",
             "document_id": "CM-1", "related_document": "INV-1"},
        ]
        metrics, flags = self.review(invoices=invoice_rows)
        self.assertEqual(metrics["gross_invoice_total_exact"], format(exact_product(), "f"))
        self.assertEqual(metrics["credit_value_exact"], format(exact_product(), "f"))
        self.assertEqual(Decimal(metrics["invoice_total_exact"]), Decimal(0))
        self.assertIn("credit_memo_review", flags)

    def test_negative_prices_remain_review_not_approval(self):
        metrics, flags = self.review(price="-" + P, order_price="-" + P)
        self.assertEqual(metrics["invoice_total_exact"], "-" + format(exact_product(), "f"))
        self.assertIn("negative_unit_price_review", flags)

    def test_existing_cent_rounded_contract_preserved(self):
        metrics, flags = self.review(quantity="1", price="0.005",
                                     order_price="0.005")
        self.assertEqual(metrics["invoice_total"], "0.01")
        self.assertEqual(metrics["invoice_total_exact"], "0.005")
        self.assertEqual(flags, [])

    def test_price_variance_uses_exact_quantities(self):
        metrics, flags = self.review(price="999999999999.99999999",
                                     order_price="999999999998.99999999")
        self.assertEqual(metrics["invoice_total_exact"], format(exact_product(), "f"))
        self.assertNotIn("price_variance_above_2pct", flags)

    def test_end_to_end_csv_uses_exact_values_and_unmodified_sources(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r84-") as name:
            root = Path(name)
            fixtures = [
                ("po.csv", ("po_number", "line", "quantity", "unit_price"),
                 (("PO1", "1", Q, P),)),
                ("inv.csv", ("po_number", "line", "quantity", "unit_price"),
                 (("PO1", "1", Q, P),)),
                ("rec.csv", ("po_number", "line", "quantity"),
                 (("PO1", "1", Q),)),
            ]
            paths = []
            original_bytes = []
            for filename, headers, rows in fixtures:
                source = root / filename
                with source.open("w", encoding="utf-8", newline="") as output:
                    writer = csv.writer(output)
                    writer.writerow(headers)
                    writer.writerows(rows)
                paths.append(source)
                original_bytes.append(source.read_bytes())
            with localcontext() as context:
                context.prec = 7
                outputs = engine.procure_guard(
                    *(str(source) for source in paths), str(root))
            self.assertEqual(len(outputs), 2)
            with outputs[0].open("r", encoding="utf-8-sig", newline="") as stream:
                results = list(csv.DictReader(stream))
            self.assertEqual(len(results), 1)
            row = results[0]
            self.assertEqual(row["status"], "matched")
            self.assertEqual(row["invoice_total_exact"], format(exact_product(), "f"))
            self.assertEqual(row["invoice_total"], "999999999999999989990.00")
            self.assertEqual(row["po_rows"], "2")
            self.assertEqual(row["invoice_rows"], "2")
            self.assertEqual(row["receipt_rows"], "2")
            self.assertTrue(outputs[1].exists())
            self.assertEqual([source.read_bytes() for source in paths], original_bytes)


if __name__ == "__main__":
    unittest.main()
