"""R75 ProcureGuard credit/return Unicode link-to-source integration checks.

Runs the real review_line method in a full repository checkout. Synthetic only.
"""
from __future__ import annotations

from decimal import Decimal
import re
import unittest

from fvs_suite.procurement import PricePolicy, review_line


def qty(text: str) -> Decimal:
    amount = Decimal(str(text))
    if not amount.is_finite() or amount < 0:
        raise ValueError("Invalid synthetic quantity")
    return amount


def cost(text: str) -> Decimal:
    amount = Decimal(str(text))
    if not amount.is_finite():
        raise ValueError("Invalid synthetic unit cost")
    return amount


def key(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", str(text).upper())


def item(quantity: str, price: str = "10.00", *, kind: str = "", doc: str = "",
         related: str = "") -> dict[str, str]:
    return {"quantity": quantity, "unit_price": price, "event_type": kind,
            "document_id": doc, "related_document": related, "row": "3"}


def run(*, original_invoice: str = "INV1", credit_reference: str | None = None,
        original_receipt: str = "RC1", return_reference: str | None = None):
    invoice_rows = [item("10", doc=original_invoice)]
    receipt_rows = [item("10", doc=original_receipt)]
    if credit_reference is not None:
        invoice_rows.append(item("2", kind="credit", doc="CM1", related=credit_reference))
    if return_reference is not None:
        receipt_rows.append(item("2", kind="return", doc="RT1", related=return_reference))
    return review_line([item("10")], invoice_rows, receipt_rows,
                       quantity=qty, unit_cost=cost, identifier=key, policy=PricePolicy())


class ProcurementDocumentLinkReviewR75(unittest.TestCase):
    def test_credit_sharp_s_expansion_requires_review(self):
        data, flags = run(original_invoice="ß1", credit_reference="SS1")
        self.assertIn("normalized_credit_link_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)
        self.assertEqual(data["invoice_total"], "80.00")

    def test_credit_long_s_expansion_requires_review(self):
        _, flags = run(original_invoice="ſ1", credit_reference="S1")
        self.assertIn("normalized_credit_link_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)

    def test_credit_ligature_expansion_requires_review(self):
        _, flags = run(original_invoice="ﬀ1", credit_reference="FF1")
        self.assertIn("normalized_credit_link_review", flags)

    def test_credit_reverse_sharp_s_expansion_requires_review(self):
        _, flags = run(original_invoice="SS1", credit_reference="ß1")
        self.assertIn("normalized_credit_link_review", flags)

    def test_ascii_case_credit_reference_is_not_normalized(self):
        _, flags = run(original_invoice="InV1", credit_reference="inv1")
        self.assertNotIn("normalized_credit_link_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)

    def test_exact_unicode_credit_reference_is_not_normalized(self):
        _, flags = run(original_invoice="ß1", credit_reference="ß1")
        self.assertNotIn("normalized_credit_link_review", flags)

    def test_punctuation_credit_normalization_still_flagged(self):
        _, flags = run(original_invoice="INV-1", credit_reference="INV1")
        self.assertIn("normalized_credit_link_review", flags)

    def test_wrong_credit_reference_remains_unlinked(self):
        _, flags = run(original_invoice="INV1", credit_reference="WRONG")
        self.assertIn("unlinked_credit_review", flags)

    def test_return_sharp_s_expansion_requires_review(self):
        data, flags = run(original_receipt="ß1", return_reference="SS1")
        self.assertIn("normalized_return_link_review", flags)
        self.assertNotIn("unlinked_return_review", flags)
        self.assertEqual(data["received_qty"], "8")

    def test_return_long_s_expansion_requires_review(self):
        _, flags = run(original_receipt="ſ1", return_reference="S1")
        self.assertIn("normalized_return_link_review", flags)

    def test_return_ligature_expansion_requires_review(self):
        _, flags = run(original_receipt="ﬀ1", return_reference="FF1")
        self.assertIn("normalized_return_link_review", flags)

    def test_ascii_case_return_reference_is_not_normalized(self):
        _, flags = run(original_receipt="Rc1", return_reference="rc1")
        self.assertNotIn("normalized_return_link_review", flags)
        self.assertNotIn("unlinked_return_review", flags)

    def test_exact_unicode_return_reference_is_not_normalized(self):
        _, flags = run(original_receipt="ß1", return_reference="ß1")
        self.assertNotIn("normalized_return_link_review", flags)

    def test_punctuation_return_normalization_still_flagged(self):
        _, flags = run(original_receipt="RC-1", return_reference="RC1")
        self.assertIn("normalized_return_link_review", flags)

    def test_wrong_return_reference_remains_unlinked(self):
        _, flags = run(original_receipt="RC1", return_reference="WRONG")
        self.assertIn("unlinked_return_review", flags)

    def test_both_unicode_links_are_flagged_without_changing_decimal_totals(self):
        data, flags = run(original_invoice="ß1", credit_reference="SS1",
                          original_receipt="ſ1", return_reference="S1")
        self.assertIn("normalized_credit_link_review", flags)
        self.assertIn("normalized_return_link_review", flags)
        self.assertEqual(data["invoice_total"], "80.00")
        self.assertEqual((data["invoiced_qty"], data["received_qty"]), ("8", "8"))


if __name__ == "__main__":
    unittest.main()
