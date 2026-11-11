"""R344: real ProcureGuard review totals and physical citation storage checks.

Requires complete fvs_suite checkout; CI executes standard and -OO Python.
No automated compliance decision and no customer data or network use.
"""
from __future__ import annotations

from decimal import Decimal
import json
import unittest

from fvs_suite.identity_inputs import normalize_key
from fvs_suite.procurement import PricePolicy, offset_source_line_links, review_line


class ForgedView(dict):
    calls = 0

    def get(self, name, default=None):
        ForgedView.calls += 1
        return "FAKE" if name in ("document_id", "related_document") else default

    def __getitem__(self, name):
        ForgedView.calls += 1
        return "900" if name in ("quantity", "unit_price") else "9"

    def items(self):
        ForgedView.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_PATH")


class HostileList(list):
    calls = 0

    def __iter__(self):
        HostileList.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_PATH")


class HostileRowLabel(str):
    calls = 0

    def __str__(self):
        HostileRowLabel.calls += 1
        raise RuntimeError("PRIVATE_CLIENT_PATH")


def entry(*, qty="10", price="10", kind="", document="", related="", row="2"):
    return {"quantity": qty, "unit_price": price, "event_type": kind,
            "document_id": document, "related_document": related, "row": row}


def review(order, invoices, receipts):
    return review_line(order, invoices, receipts, quantity=Decimal, unit_cost=Decimal,
                       identifier=normalize_key, policy=PricePolicy())


def links(rows):
    return offset_source_line_links(rows, source="invoice", offset="credit",
                                    identifier=normalize_key)


class ProcurementNativeRowIntegrationR344(unittest.TestCase):
    def setUp(self):
        ForgedView.calls = HostileList.calls = HostileRowLabel.calls = 0

    def assert_private_rejection(self, operation):
        with self.assertRaises(ValueError) as caught:
            operation()
        self.assertNotIn("PRIVATE_CLIENT", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertEqual((ForgedView.calls, HostileList.calls, HostileRowLabel.calls), (0, 0, 0))

    def test_native_invoice_total_not_virtual_quantity(self):
        invoice = ForgedView(entry(qty="3", price="2.50", document="INV1"))
        output, _ = review([entry()], [invoice], [entry()])
        self.assertEqual(output["invoice_total_exact"], "7.50")
        self.assertEqual(ForgedView.calls, 0)

    def test_native_order_quantity_not_virtual_getitem(self):
        order = ForgedView(entry(qty="3", price="2.50"))
        output, _ = review([order], [entry(qty="3", price="2.50")],
                           [entry(qty="3")])
        self.assertEqual(output["po_qty"], "3")
        self.assertEqual(output["po_unit_price"], "2.50")
        self.assertEqual(ForgedView.calls, 0)

    def test_native_receipt_quantity_not_virtual_getitem(self):
        receipt = ForgedView(entry(qty="4"))
        output, _ = review([entry()], [entry()], [receipt])
        self.assertEqual(output["received_qty"], "4")
        self.assertEqual(ForgedView.calls, 0)

    def test_native_credit_reference_not_virtual_get(self):
        credit = ForgedView(entry(qty="2", kind="credit", document="CM1",
                                  related="INV1", row="3"))
        output, flags = review([entry()], [entry(document="INV1"), credit], [entry()])
        self.assertEqual(output["invoice_total_exact"], "80")
        self.assertIn("credit_memo_review", flags)
        self.assertNotIn("unlinked_credit_review", flags)
        self.assertEqual(ForgedView.calls, 0)

    def test_original_records_are_unchanged_after_review(self):
        invoice = ForgedView(entry(qty="3", price="2.50", document="INV1"))
        before = dict(dict.items(invoice))
        review([entry()], [invoice], [entry()])
        self.assertEqual(dict(dict.items(invoice)), before)
        self.assertEqual(ForgedView.calls, 0)

    def test_native_citation_rows_not_virtual_getitem(self):
        original = ForgedView(entry(document="INV1", row="9"))
        credit = ForgedView(entry(qty="2", kind="credit", document="CM1",
                                  related="INV1", row="10"))
        data = json.loads(links([original, credit]))
        self.assertEqual(data, [{"offset_row": "10", "target_rows": ["9"]}])
        self.assertEqual(ForgedView.calls, 0)

    def test_citation_invalid_leading_zero_rejected(self):
        self.assert_private_rejection(lambda: links([entry(document="INV1", row="09")]))

    def test_citation_invalid_unicode_digit_rejected(self):
        self.assert_private_rejection(lambda: links([entry(document="INV1", row="٢")]))

    def test_citation_invalid_control_injection_rejected(self):
        self.assert_private_rejection(lambda: links([entry(document="INV1", row="9\n2")]))

    def test_citation_invalid_str_subclass_rejected(self):
        self.assert_private_rejection(lambda: links([entry(document="INV1",
                                                           row=HostileRowLabel("9"))]))

    def test_citation_missing_row_rejected(self):
        row = entry(document="INV1")
        del row["row"]
        self.assert_private_rejection(lambda: links([row]))

    def test_citation_invalid_integer_row_rejected(self):
        self.assert_private_rejection(lambda: links([entry(document="INV1", row=9)]))

    def test_citation_too_long_row_rejected(self):
        self.assert_private_rejection(lambda: links([entry(document="INV1", row="10000000000")]))

    def test_citation_valid_physical_multiline_start_rows(self):
        data = json.loads(links([entry(document="INV-1", row="20"),
                                 entry(qty="2", kind="credit", document="CM1",
                                       related="INV1", row="24")]))
        self.assertEqual(data, [{"offset_row": "24", "target_rows": ["20"]}])

    def test_citation_unlinked_reference_stays_human_review(self):
        data = json.loads(links([entry(document="INV1", row="9"),
                                 entry(qty="2", kind="credit", document="CM1",
                                       related="WRONG", row="10")]))
        self.assertEqual(data, [{"offset_row": "10", "target_rows": []}])

    def test_citation_list_subclass_rejected_without_iterator(self):
        self.assert_private_rejection(lambda: links(HostileList([entry(document="INV1")])))

    def test_review_list_subclass_rejected_before_any_callbacks(self):
        self.assert_private_rejection(lambda: review([entry()],
                                                  HostileList([entry(document="INV1")]),
                                                  [entry()]))

    def test_citation_rejects_nontext_key_before_callbacks(self):
        row = entry(document="INV1")
        row[1] = "hidden"
        self.assert_private_rejection(lambda: links([row]))


if __name__ == "__main__":
    unittest.main()
