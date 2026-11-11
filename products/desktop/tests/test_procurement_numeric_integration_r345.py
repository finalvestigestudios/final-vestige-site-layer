"""R345: full ProcureGuard review_line numeric-callback integration gates.

CI must run these with the COMPLETE private fvs_suite source on Ubuntu and
Windows, normal and -OO Python. No local test is an executable release gate.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
import unittest

from fvs_suite.identity_inputs import normalize_key
from fvs_suite.procurement import PricePolicy, review_line


def row(qty="3", price="2.50", kind="", doc="", related=""):
    return {"quantity": qty, "unit_price": price, "event_type": kind,
            "document_id": doc, "related_document": related, "row": "2"}


def review(ordered=None, invoices=None, receipts=None,
           quantity=Decimal, unit_cost=Decimal):
    return review_line(
        ordered if ordered is not None else [row()],
        invoices if invoices is not None else [row(doc="INV1")],
        receipts if receipts is not None else [row(doc="REC1")],
        quantity=quantity, unit_cost=unit_cost,
        identifier=normalize_key, policy=PricePolicy(),
    )


class NumericCallbackIntegrationR345(unittest.TestCase):
    def private_rejection(self, action):
        with self.assertRaises(ValueError) as trapped:
            action()
        self.assertNotIn("PRIVATE_CLIENT", str(trapped.exception))
        self.assertIsNone(trapped.exception.__cause__)

    def test_baseline_exact_decimal_unchanged(self):
        data, flags = review()
        self.assertEqual(data["invoice_total_exact"], "7.50")
        self.assertEqual(flags, [])

    def test_order_negative_quantity_rejected(self):
        self.private_rejection(lambda: review(ordered=[row(qty="-3")]))

    def test_invoice_negative_quantity_rejected(self):
        self.private_rejection(lambda: review(invoices=[row(qty="-1")]))

    def test_receipt_negative_quantity_rejected(self):
        self.private_rejection(lambda: review(receipts=[row(qty="-1")]))

    def test_credit_negative_quantity_rejected_not_offset(self):
        self.private_rejection(lambda: review(invoices=[
            row(doc="INV1"), row(qty="-2", kind="credit", doc="CM1", related="INV1")]))

    def test_return_negative_quantity_rejected_not_offset(self):
        self.private_rejection(lambda: review(receipts=[
            row(doc="REC1"), row(qty="-2", kind="return", doc="RMA1", related="REC1")]))

    def test_order_nan_price_rejected(self):
        self.private_rejection(lambda: review(ordered=[row(price="NaN")]))

    def test_invoice_infinite_price_rejected(self):
        self.private_rejection(lambda: review(invoices=[row(price="Infinity")]))

    def test_receipt_nan_quantity_rejected(self):
        self.private_rejection(lambda: review(receipts=[row(qty="NaN")]))

    def test_invoice_float_callback_rejected(self):
        self.private_rejection(lambda: review(unit_cost=lambda v: float(v)))

    def test_quantity_string_callback_rejected(self):
        self.private_rejection(lambda: review(quantity=lambda v: v))

    def test_quantity_callback_error_private_path_redacted(self):
        def bad(_):
            raise RuntimeError("PRIVATE_CLIENT_PATH")
        self.private_rejection(lambda: review(quantity=bad))

    def test_price_callback_error_private_path_redacted(self):
        def bad(_):
            raise OSError("PRIVATE_CLIENT_PATH")
        self.private_rejection(lambda: review(unit_cost=bad))

    def test_invoice_price_too_large_at_low_precision(self):
        with localcontext() as ctx:
            ctx.prec = 4
            self.private_rejection(lambda: review(invoices=[
                row(price="1000000000000.00000001")]))

    def test_invoice_price_ninth_fraction_rejected(self):
        self.private_rejection(lambda: review(invoices=[row(price="0.000000001")]))

    def test_invoice_qty_above_documented_maximum_rejected(self):
        self.private_rejection(lambda: review(invoices=[row(qty="1000000001")]))

    def test_negative_price_is_review_flag_not_auto_rejection(self):
        data, flags = review(ordered=[row(price="-2.50")],
                             invoices=[row(price="-2.50", doc="INV1")])
        self.assertEqual(data["invoice_total_exact"], "-7.50")
        self.assertIn("negative_unit_price_review", flags)

    def test_subcent_value_preserved(self):
        data, _ = review(ordered=[row(price="0.00000001")],
                         invoices=[row(price="0.00000001", doc="INV1")])
        self.assertEqual(data["invoice_total_exact"], "0.00000003")

    def test_zero_quantity_with_pathological_exponent_rejected(self):
        self.private_rejection(lambda: review(invoices=[row(qty="0E-999999")]))

    def test_zero_price_with_pathological_exponent_rejected(self):
        self.private_rejection(lambda: review(invoices=[row(price="0E-999999")]))

    def test_input_rows_unchanged_on_failure(self):
        inv = [row(qty="NaN", doc="INV1")]
        before = dict(inv[0])
        self.private_rejection(lambda: review(invoices=inv))
        self.assertEqual(inv[0], before)


if __name__ == "__main__":
    unittest.main()
