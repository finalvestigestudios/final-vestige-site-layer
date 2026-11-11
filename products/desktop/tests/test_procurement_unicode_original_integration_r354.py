"""R354 real ProcureGuard integration: normalized links still require original evidence.

Synthetic rows; must run with FULL private fvs_suite checkout on Ubuntu/Windows.
Passing these checks is not payment authorization or QD release approval.
"""
from __future__ import annotations

from decimal import Decimal
import json
import unittest

from fvs_suite.identity_inputs import normalize_key
from fvs_suite.procurement import PricePolicy, offset_source_line_links, review_line


def row(*, q="1", cost="10", kind="", doc="", related="", line="2"):
    return {"quantity": q, "unit_price": cost, "event_type": kind,
            "document_id": doc, "related_document": related, "row": line}


def review(inv, rec):
    return review_line([row(q="2")], inv, rec, quantity=Decimal,
                       unit_cost=Decimal, identifier=normalize_key,
                       policy=PricePolicy())


class UnicodeOriginalIntegrationR354(unittest.TestCase):
    def test_nbsp_source_credit_plain_reference_requires_review(self):
        inv = [row(doc="\u00a0INV1"), row(kind="credit", doc="CM1",
                                          related="INV1", line="3")]
        _, flags = review(inv, [row(kind="receipt", doc="R1")])
        self.assertIn("normalized_credit_link_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)

    def test_figure_space_source_credit_plain_reference_requires_review(self):
        inv = [row(doc="INV1\u2007"), row(kind="credit", doc="CM1",
                                          related="INV1", line="3")]
        _, flags = review(inv, [row(kind="receipt", doc="R1")])
        self.assertIn("normalized_credit_link_review", flags)

    def test_narrow_nbsp_source_return_plain_reference_requires_review(self):
        rec = [row(kind="receipt", doc="\u202fREC1"),
               row(kind="return", doc="RET1", related="REC1", line="3")]
        _, flags = review([row(doc="INV1")], rec)
        self.assertIn("normalized_return_link_review", flags)
        self.assertNotIn("unlinked_return_review", flags)

    def test_ideographic_space_source_return_plain_reference_requires_review(self):
        rec = [row(kind="receipt", doc="REC1\u3000"),
               row(kind="return", doc="RET1", related="REC1", line="3")]
        _, flags = review([row(doc="INV1")], rec)
        self.assertIn("normalized_return_link_review", flags)

    def test_genuine_unicode_original_credit_reference_not_spuriously_flagged(self):
        inv = [row(doc="\u00a0INV1"), row(kind="credit", doc="CM1",
                                          related="\u00a0INV1", line="3")]
        _, flags = review(inv, [row(kind="receipt", doc="R1")])
        self.assertNotIn("normalized_credit_link_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)

    def test_ascii_boundary_space_still_compatible(self):
        inv = [row(doc=" INV1 "), row(kind="credit", doc="CM1",
                                       related="INV1", line="3")]
        _, flags = review(inv, [row(kind="receipt", doc="R1")])
        self.assertNotIn("normalized_credit_link_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)

    def test_exact_financial_total_unchanged_while_flag_is_added(self):
        inv = [row(q="2", cost="0.12345678", doc="\u00a0INV1"),
               row(q="1", cost="0.12345678", kind="credit", doc="CM1",
                   related="INV1", line="3")]
        metrics, flags = review(inv, [row(kind="receipt", doc="R1")])
        self.assertEqual(metrics["invoice_total_exact"], "0.12345678")
        self.assertIn("normalized_credit_link_review", flags)

    def test_lossy_candidate_links_still_show_source_row(self):
        inv = [row(doc="\u00a0INV1", line="2"),
               row(kind="credit", doc="CM1", related="INV1", line="3")]
        links = json.loads(offset_source_line_links(
            inv, source="invoice", offset="credit", identifier=normalize_key))
        self.assertEqual(links, [{"offset_row": "3", "target_rows": ["2"]}])


if __name__ == "__main__":
    unittest.main()
