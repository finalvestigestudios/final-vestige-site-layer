"""R348 real ProcureGuard review_line integration: callback Decimal context custody.

Synthetic PO/invoice/receipt values. No CSV files, entitlement access, network,
or approval decisions. Must run against the full fvs_suite repository in CI.
"""
from decimal import (Context, Decimal, ROUND_DOWN, getcontext, setcontext)
import unittest

from fvs_suite.procurement import PricePolicy, review_line


def records(*, order_qty="3", invoice_qty="3", receipt_qty="3",
            price="0.12345678"):
    return (
        [{"po_number": "PO-TEST", "line": "1", "row": "2",
          "quantity": order_qty, "unit_price": price}],
        [{"po_number": "PO-TEST", "line": "1", "row": "3",
          "quantity": invoice_qty, "unit_price": price,
          "event_type": "invoice", "document_id": "INV-TEST",
          "related_document": ""}],
        [{"po_number": "PO-TEST", "line": "1", "row": "4",
          "quantity": receipt_qty, "event_type": "receipt",
          "document_id": "REC-TEST", "related_document": ""}],
    )


def key(value):
    return value.strip().casefold()


def poison_precision(value):
    getcontext().prec = 4
    return Decimal(value)


def poison_setcontext(value):
    setcontext(Context(prec=2, rounding=ROUND_DOWN))
    return Decimal(value)


def poison_flags(value):
    getcontext().rounding = ROUND_DOWN
    getcontext().prec = 2
    return Decimal(value)


class RealProcurementContextR348(unittest.TestCase):
    def review(self, data, qty=Decimal, price=Decimal):
        return review_line(*data, quantity=qty, unit_cost=price,
                           identifier=key, policy=PricePolicy())

    def test_price_parser_cannot_round_gross_exact(self):
        metrics, _ = self.review(records(), price=poison_precision)
        self.assertEqual(metrics["gross_invoice_total_exact"], "0.37037034")
        self.assertEqual(metrics["invoice_total_exact"], "0.37037034")
        self.assertEqual(metrics["invoice_total"], "0.37")

    def test_qty_parser_cannot_round_gross_exact(self):
        metrics, _ = self.review(records(), qty=poison_precision)
        self.assertEqual(metrics["gross_invoice_total_exact"], "0.37037034")
        self.assertEqual(Decimal(metrics["invoiced_qty"]), Decimal(3))

    def test_setcontext_price_parser_cannot_round_totals(self):
        metrics, _ = self.review(records(), price=poison_setcontext)
        self.assertEqual(metrics["invoice_total_exact"], "0.37037034")

    def test_setcontext_qty_parser_cannot_round_totals(self):
        metrics, _ = self.review(records(), qty=poison_setcontext)
        self.assertEqual(metrics["invoice_total_exact"], "0.37037034")

    def test_both_callback_families_poison_context(self):
        metrics, flags = self.review(records(), qty=poison_flags, price=poison_precision)
        self.assertEqual(metrics["invoice_total_exact"], "0.37037034")
        self.assertNotIn("price_variance_above_2pct", flags)

    def test_high_precision_quantity_source_exact(self):
        data = records(order_qty="3.00000001", invoice_qty="3.00000001",
                       receipt_qty="3.00000001")
        metrics, _ = self.review(data, qty=poison_precision)
        self.assertEqual(metrics["invoice_total_exact"], "0.3703703412345678")
        self.assertEqual(metrics["invoiced_qty"], "3.00000001")

    def test_price_parser_cannot_launder_amount_even_when_context_changed(self):
        def forge(_):
            getcontext().prec = 2
            return Decimal("0.12345677")
        with self.assertRaises(ValueError):
            self.review(records(), price=forge)

    def test_quantity_parser_private_exception_stays_redacted(self):
        def fail(_):
            getcontext().prec = 2
            raise OSError("PRIVATE_FINANCE_PATH")
        with self.assertRaises(ValueError) as caught:
            self.review(records(), qty=fail)
        self.assertNotIn("PRIVATE_FINANCE_PATH", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_repeated_review_is_deterministic_after_context_poison(self):
        a = self.review(records(), qty=poison_precision, price=poison_precision)
        b = self.review(records(), qty=poison_precision, price=poison_precision)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
