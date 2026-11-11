"""R353 ProcureGuard live review/offset integration, synthetic rows only.

Requires the FULL private fvs_suite checkout. No release authority is conferred
by passing tests; references still require independent human review.
"""
from __future__ import annotations

from collections import Counter
from decimal import Decimal
import json
import unittest

from fvs_suite.identity_inputs import normalize_key
from fvs_suite.procurement import PricePolicy, offset_source_line_links, review_line


def row(q="1", price="10", kind="", doc="", related="", line="2"):
    return {"quantity": q, "unit_price": price, "event_type": kind,
            "document_id": doc, "related_document": related, "row": line}


def flipper():
    """Produce a different candidate key on subsequent calls for same label."""
    calls = Counter()
    def identifier(text):
        calls[text] += 1
        return normalize_key(text) if calls[text] == 1 else "POISONED-" + text
    return identifier, calls


def review(invoices, receipts, identifier):
    return review_line([row(q="2")], invoices, receipts, quantity=Decimal,
                       unit_cost=Decimal, identifier=identifier, policy=PricePolicy())


class SourceIdentitySessionIntegrationR353(unittest.TestCase):
    def test_repeated_invoice_id_still_flags_duplicate(self):
        invoices = [row(doc="INV-1", line="3"), row(doc="INV-1", line="4")]
        receipts = [row(q="2", kind="receipt", doc="REC-1")]
        identity, calls = flipper()
        metrics, flags = review(invoices, receipts, identity)
        self.assertIn("repeated_invoice_document_id_review", flags)
        self.assertEqual(metrics["invoice_total_exact"], "20")
        self.assertEqual(calls["INV-1"], 1)
        self.assertEqual((metrics, flags), review(invoices, receipts, normalize_key))

    def test_repeated_receipt_id_still_flags_duplicate(self):
        invoices = [row(q="2", doc="INV-1")]
        receipts = [row(kind="receipt", doc="REC-1", line="4"),
                    row(kind="receipt", doc="REC-1", line="5")]
        identity, calls = flipper()
        result = review(invoices, receipts, identity)
        self.assertIn("repeated_receipt_document_id_review", result[1])
        self.assertEqual(calls["REC-1"], 1)
        self.assertEqual(result, review(invoices, receipts, normalize_key))

    def test_credit_reference_remains_linked(self):
        invoices = [row(q="2", doc="INV-1"),
                    row(q="1", kind="credit", doc="CM-1", related="INV-1", line="3")]
        receipts = [row(kind="receipt", doc="REC-1")]
        identity, calls = flipper()
        result = review(invoices, receipts, identity)
        self.assertIn("credit_memo_review", result[1])
        self.assertNotIn("unlinked_credit_review", result[1])
        self.assertEqual(calls["INV-1"], 1)
        self.assertEqual(result, review(invoices, receipts, normalize_key))

    def test_return_reference_remains_linked(self):
        invoices = [row(q="2", doc="INV-1")]
        receipts = [row(q="2", kind="receipt", doc="REC-1"),
                    row(q="1", kind="return", doc="RET-1", related="REC-1", line="4")]
        identity, calls = flipper()
        result = review(invoices, receipts, identity)
        self.assertIn("return_review", result[1])
        self.assertNotIn("unlinked_return_review", result[1])
        self.assertEqual(calls["REC-1"], 1)
        self.assertEqual(result, review(invoices, receipts, normalize_key))

    def test_duplicate_return_document_still_flagged(self):
        receipts = [row(q="2", kind="receipt", doc="REC-1"),
                    row(kind="return", doc="RET-1", related="REC-1", line="4"),
                    row(kind="return", doc="RET-1", related="REC-1", line="5")]
        identity, calls = flipper()
        result = review([row(q="2", doc="INV-1")], receipts, identity)
        self.assertIn("repeated_return_document_id_review", result[1])
        self.assertEqual(calls["RET-1"], 1)
        self.assertEqual(result, review([row(q="2", doc="INV-1")], receipts, normalize_key))

    def test_credit_offset_json_links_canonical_source_rows(self):
        invoices = [row(kind="invoice", doc="INV-1", line="2"),
                    row(kind="credit", doc="CM-1", related="INV-1", line="3")]
        identity, calls = flipper()
        actual = offset_source_line_links(invoices, source="invoice", offset="credit",
                                          identifier=identity)
        expected = offset_source_line_links(invoices, source="invoice", offset="credit",
                                            identifier=normalize_key)
        self.assertEqual(actual, expected)
        self.assertEqual(json.loads(actual), [{"offset_row":"3", "target_rows":["2"]}])
        self.assertEqual(calls["INV-1"], 1)

    def test_return_offset_json_links_canonical_source_rows(self):
        receipts = [row(kind="receipt", doc="REC-1", line="2"),
                    row(kind="return", doc="RET-1", related="REC-1", line="3")]
        identity, calls = flipper()
        actual = offset_source_line_links(receipts, source="receipt", offset="return",
                                          identifier=identity)
        self.assertEqual(json.loads(actual), [{"offset_row":"3", "target_rows":["2"]}])
        self.assertEqual(calls["REC-1"], 1)

    def test_multiple_original_source_rows_remain_visible_in_links(self):
        invoices = [row(kind="invoice", doc="INV-1", line="2"),
                    row(kind="invoice", doc="INV-1", line="3"),
                    row(kind="credit", doc="CM-1", related="INV-1", line="4")]
        identity, calls = flipper()
        result = offset_source_line_links(invoices, source="invoice", offset="credit",
                                          identifier=identity)
        self.assertEqual(json.loads(result), [{"offset_row":"4", "target_rows":["2", "3"]}])
        self.assertEqual(calls["INV-1"], 1)

    def test_empty_ids_still_report_unidentified_offsets(self):
        receipts = [row(kind="receipt", doc="", line="2"),
                    row(kind="return", doc="", related="", line="3")]
        identity, calls = flipper()
        result = review([row(doc="INV-1")], receipts, identity)
        self.assertIn("unidentified_return_review", result[1])
        self.assertIn("unlinked_return_review", result[1])
        self.assertEqual(calls[""], 1)

    def test_context_and_totals_unmodified_by_stateful_identifier(self):
        invoices = [row(q="2", price="0.12345678", doc="INV-1")]
        receipts = [row(q="2", kind="receipt", doc="REC-1")]
        identity, calls = flipper()
        output, flags = review_line([row(q="2", price="0.12345678")], invoices,
                                    receipts, quantity=Decimal, unit_cost=Decimal,
                                    identifier=identity, policy=PricePolicy())
        self.assertEqual(output["invoice_total_exact"], "0.24691356")
        self.assertNotIn("price_variance_above_2pct", flags)
        self.assertEqual(calls["INV-1"], 1)


if __name__ == "__main__":
    unittest.main()
