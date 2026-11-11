"""R350 complete-engine signed-zero reviewer flags (requires private suite)."""
from __future__ import annotations

from decimal import Decimal
import unittest

from fvs_suite.identity_inputs import normalize_key
from fvs_suite.procurement import PricePolicy, review_line


def row(*, quantity="3", price="0", kind="", doc="", related=""):
    return {"quantity": quantity, "unit_price": price, "event_type": kind,
            "document_id": doc, "related_document": related, "row": "2"}


def review(*, po="0", invoice="0", invoices=None, unit_cost=Decimal):
    return review_line(
        [row(price=po)],
        [row(price=invoice, doc="INV1")] if invoices is None else invoices,
        [row(doc="REC1")],
        quantity=Decimal, unit_cost=unit_cost,
        identifier=normalize_key, policy=PricePolicy(),
    )


class PriceSignIntegrationR350(unittest.TestCase):
    def test_positive_zero_prices_do_not_flag_negative_review(self):
        _, flags = review()
        self.assertNotIn("negative_unit_price_review", flags)

    def test_negative_zero_order_price_requires_human_review(self):
        _, flags = review(po="-0.00")
        self.assertIn("negative_unit_price_review", flags)

    def test_negative_zero_invoice_price_requires_human_review(self):
        _, flags = review(invoice="-0.00")
        self.assertIn("negative_unit_price_review", flags)

    def test_both_negative_zero_prices_deduplicate_flag(self):
        _, flags = review(po="-0.00", invoice="-0.00")
        self.assertEqual(flags.count("negative_unit_price_review"), 1)

    def test_negative_zero_order_with_positive_invoice_no_variance(self):
        _, flags = review(po="-0.00", invoice="0.00")
        self.assertIn("negative_unit_price_review", flags)
        self.assertNotIn("price_variance_above_2pct", flags)

    def test_negative_zero_invoice_with_positive_order_no_variance(self):
        _, flags = review(po="0.00", invoice="-0.00")
        self.assertIn("negative_unit_price_review", flags)
        self.assertNotIn("price_variance_above_2pct", flags)

    def test_regular_negative_prices_remain_review_only(self):
        data, flags = review(po="-1", invoice="-1")
        self.assertEqual(data["invoice_total_exact"], "-3")
        self.assertIn("negative_unit_price_review", flags)

    def test_signed_zero_invoice_exact_amount_remains_zero(self):
        data, flags = review(invoice="-0.00")
        self.assertEqual(Decimal(data["invoice_total_exact"]), Decimal(0))
        self.assertIn("negative_unit_price_review", flags)

    def test_negative_zero_credit_price_gets_both_review_flags(self):
        invoices = [row(doc="INV1"), row(quantity="1", price="-0.00",
                                           kind="credit", doc="CM1", related="INV1")]
        _, flags = review(invoices=invoices)
        self.assertIn("negative_unit_price_review", flags)
        self.assertIn("negative_credit_price_review", flags)
        self.assertIn("credit_memo_review", flags)

    def test_positive_zero_credit_price_not_marked_negative(self):
        invoices = [row(doc="INV1"), row(quantity="1", price="0.00",
                                           kind="credit", doc="CM1", related="INV1")]
        _, flags = review(invoices=invoices)
        self.assertNotIn("negative_unit_price_review", flags)
        self.assertNotIn("negative_credit_price_review", flags)
        self.assertIn("credit_memo_review", flags)

    def test_accounting_negative_zero_price_preserves_review(self):
        def parse_price(value):
            if value == "($0.00)":
                return Decimal("-0.00")
            return Decimal(value)
        _, flags = review(invoice="($0.00)", unit_cost=parse_price)
        self.assertIn("negative_unit_price_review", flags)

    def test_consecutive_reviews_are_deterministic(self):
        self.assertEqual(review(po="-0.00", invoice="-0.00"),
                         review(po="-0.00", invoice="-0.00"))


if __name__ == "__main__":
    unittest.main()
