"""R354 real ProcureGuard integration: normalized links still require original evidence.

Synthetic rows; must run with FULL private fvs_suite checkout on Ubuntu/Windows.
Passing these checks is not payment authorization or QD release approval.
"""
from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from fvs_suite import engine
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


    def test_actual_csv_document_columns_preserve_nbsp_boundary(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "invoice.csv"
            path.write_text("po_number,line,quantity,unit_price,event_type,document_id,related_document\n"
                            "PO-1,1,1,10,invoice,\u00a0INV1,\n", encoding="utf-8")
            rows = engine.table(path, ("po_number", "line", "quantity", "unit_price"),
                                ("event_type", "document_id", "related_document"))
        self.assertEqual(rows[0]["document_id"], "\u00a0INV1")
        self.assertEqual(rows[0]["po_number"], "PO-1")

    def test_actual_csv_related_column_preserves_narrow_nbsp_boundary(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "credit.csv"
            path.write_text("po_number,line,quantity,unit_price,event_type,document_id,related_document\n"
                            "PO-1,1,1,10,credit,CM1,INV1\u202f\n", encoding="utf-8")
            rows = engine.table(path, ("po_number", "line", "quantity", "unit_price"),
                                ("event_type", "document_id", "related_document"))
        self.assertEqual(rows[0]["related_document"], "INV1\u202f")

    def test_other_import_fields_retain_prior_unicode_strip_behavior(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "invoice.csv"
            path.write_text("po_number,line,quantity,unit_price,event_type,document_id\n"
                            "\u00a0PO-1\u00a0,1,1,10,invoice,INV1\n", encoding="utf-8")
            rows = engine.table(path, ("po_number", "line", "quantity", "unit_price"),
                                ("event_type", "document_id"))
        self.assertEqual(rows[0]["po_number"], "PO-1")
        self.assertEqual(rows[0]["document_id"], "INV1")

    def test_actual_csv_source_then_real_credit_review_flags_spelling(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "invoice.csv"
            path.write_text("po_number,line,quantity,unit_price,event_type,document_id,related_document\n"
                            "PO-1,1,2,10,invoice,\u00a0INV1,\n"
                            "PO-1,1,1,10,credit,CM1,INV1\n", encoding="utf-8")
            inv = engine.table(path, ("po_number", "line", "quantity", "unit_price"),
                               ("event_type", "document_id", "related_document"))
            metrics, flags = review(inv, [row(kind="receipt", doc="REC1")])
        self.assertEqual(metrics["invoice_total_exact"], "10")
        self.assertIn("normalized_credit_link_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)


if __name__ == "__main__":
    unittest.main()
