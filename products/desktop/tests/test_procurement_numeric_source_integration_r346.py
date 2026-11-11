"""R346 genuine ProcureGuard review integration; requires complete fvs_suite tree.

These tests intentionally depend on review_line and must run under full CI,
not the isolated helper-only test harness. Synthetic financial rows only.
"""
from decimal import Decimal
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


class NumericSourceIntegrationR346(unittest.TestCase):
    def reject(self, action):
        with self.assertRaises(ValueError) as caught:
            action()
        self.assertIsNone(caught.exception.__cause__)
        self.assertNotIn("PRIVATE_CUSTOMER_PATH", str(caught.exception))

    def test_real_review_accepts_normal_exact_financial_data(self):
        evidence, flags = review()
        self.assertEqual(evidence["invoice_total_exact"], "7.50")
        self.assertEqual(flags, [])

    def test_invoice_quantity_callback_cannot_forge_3_into_4(self):
        self.reject(lambda: review(quantity=lambda _: Decimal(4)))

    def test_receipt_quantity_callback_cannot_forge_3_into_2(self):
        self.reject(lambda: review(quantity=lambda _: Decimal(2)))

    def test_order_unit_price_callback_cannot_forge_2_5_into_3(self):
        self.reject(lambda: review(unit_cost=lambda _: Decimal(3)))

    def test_invoice_nan_source_cannot_be_mapped_into_numeric_quantity(self):
        self.reject(lambda: review(invoices=[row(qty="NaN", doc="INV1")],
                                   quantity=lambda _: Decimal(3)))

    def test_invoice_negative_source_cannot_be_mapped_into_positive_quantity(self):
        self.reject(lambda: review(invoices=[row(qty="-3", doc="INV1")],
                                   quantity=lambda _: Decimal(3)))

    def test_credit_negative_source_cannot_be_mapped_into_positive_offset(self):
        self.reject(lambda: review(invoices=[row(doc="INV1"),
            row(qty="-1", kind="credit", doc="CM1", related="INV1")],
            quantity=lambda _: Decimal(3)))

    def test_return_negative_source_cannot_be_mapped_into_positive_offset(self):
        self.reject(lambda: review(receipts=[row(doc="REC1"),
            row(qty="-1", kind="return", doc="RTN1", related="REC1")],
            quantity=lambda _: Decimal(3)))

    def test_long_financial_cell_rejected_before_injected_parser(self):
        self.reject(lambda: review(invoices=[row(qty="1" * 100_000, doc="INV1")],
                                   quantity=lambda _: Decimal(3)))

    def test_control_character_rejected_before_injected_parser(self):
        self.reject(lambda: review(invoices=[row(price="2.50\0", doc="INV1")],
                                   unit_cost=lambda _: Decimal("2.50")))

    def test_source_price_eight_places_survives(self):
        evidence, _ = review(ordered=[row(price="0.00000001")],
                             invoices=[row(price="0.00000001", doc="INV1")])
        self.assertEqual(evidence["invoice_total_exact"], "0.00000003")

    def test_formatted_accounting_price_parser_remains_allowed(self):
        def accounting(value):
            if value == "($2.50)":
                return Decimal("-2.50")
            return Decimal(value)
        evidence, flags = review(ordered=[row(price="($2.50)")],
                                  invoices=[row(price="($2.50)", doc="INV1")],
                                  unit_cost=accounting)
        self.assertEqual(evidence["invoice_total_exact"], "-7.50")
        self.assertIn("negative_unit_price_review", flags)


if __name__ == "__main__":
    unittest.main()
