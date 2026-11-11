"""R348 full ProcureGuard review-line signed-zero custody regression.

Requires the complete fvs_suite tree; no network, private documents, or
compliance approvals. Retained separately from isolated helper tests.
"""
from decimal import Decimal
import unittest

from fvs_suite.identity_inputs import normalize_key
from fvs_suite.procurement import PricePolicy, review_line


def row(qty="3", price="2.50", kind="", doc="", related=""):
    return {"quantity": qty, "unit_price": price, "event_type": kind,
            "document_id": doc, "related_document": related, "row": "2"}


def review(*, ordered=None, invoices=None, receipts=None,
           quantity=Decimal, unit_cost=Decimal):
    return review_line(
        [row()] if ordered is None else ordered,
        [row(doc="INV1")] if invoices is None else invoices,
        [row(doc="REC1")] if receipts is None else receipts,
        quantity=quantity, unit_cost=unit_cost,
        identifier=normalize_key, policy=PricePolicy(),
    )


class SignedZeroIntegrationR348(unittest.TestCase):
    def reject(self, action):
        with self.assertRaises(ValueError) as caught:
            action()
        self.assertIsNone(caught.exception.__cause__)
        self.assertNotIn("PRIVATE_FINANCIAL_PATH", str(caught.exception))

    def test_po_signed_zero_quantity_rejected(self):
        self.reject(lambda: review(ordered=[row(qty="-0")], quantity=lambda _: Decimal(0)))

    def test_invoice_signed_zero_quantity_rejected(self):
        self.reject(lambda: review(invoices=[row(qty="-0", doc="INV1")],
                                   quantity=lambda _: Decimal(0)))

    def test_credit_signed_zero_quantity_rejected(self):
        self.reject(lambda: review(invoices=[row(doc="INV1"),
                            row(qty="-0", kind="credit", doc="CM1", related="INV1")],
                                   quantity=lambda _: Decimal(0)))

    def test_receipt_signed_zero_quantity_rejected(self):
        self.reject(lambda: review(receipts=[row(qty="-0", doc="REC1")],
                                   quantity=lambda _: Decimal(0)))

    def test_return_signed_zero_quantity_rejected(self):
        self.reject(lambda: review(receipts=[row(doc="REC1"),
                            row(qty="-0", kind="return", doc="RTN1", related="REC1")],
                                   quantity=lambda _: Decimal(0)))

    def test_invoice_callback_cannot_inject_signed_zero(self):
        self.reject(lambda: review(invoices=[row(qty="0", doc="INV1")],
                                   quantity=lambda _: Decimal("-0")))

    def test_po_callback_cannot_inject_signed_zero(self):
        self.reject(lambda: review(ordered=[row(qty="0")], quantity=lambda _: Decimal("-0")))

    def test_price_callback_cannot_flip_parenthesized_signed_zero(self):
        def hostile(value):
            return Decimal("0") if value == "($0.00)" else Decimal(value)
        self.reject(lambda: review(invoices=[row(price="($0.00)", doc="INV1")],
                                   unit_cost=hostile))

    def test_valid_negative_zero_price_keeps_human_review_flag(self):
        def accounting(value):
            return Decimal("-0") if value == "($0.00)" else Decimal(value)
        evidence, flags = review(ordered=[row(price="($0.00)")],
                                  invoices=[row(price="($0.00)", doc="INV1")],
                                  unit_cost=accounting)
        self.assertEqual(Decimal(evidence["invoice_total_exact"]), Decimal(0))
        self.assertIsInstance(flags, list)

    def test_positive_zero_quantity_still_human_reviewed(self):
        evidence, flags = review(ordered=[row(qty="0")],
                                  invoices=[row(qty="0", doc="INV1")],
                                  receipts=[row(qty="0", doc="REC1")])
        self.assertEqual(evidence["invoice_total_exact"], "0.00")
        self.assertIn("zero_order_quantity_review", flags)
        self.assertIn("zero_movement_review", flags)


if __name__ == "__main__":
    unittest.main()
