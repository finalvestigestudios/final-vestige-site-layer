"""R475: bounded cross-order source citations; review only, never payment action."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from fvs_suite import procurement_cross_po_r471 as index


def _groups(count, *, kind="invoice", shared="PRIVATE_CUSTOMER_DOC"):
    return {
        (f"PO{i:04d}", "1"): [
            {"row": str(i + 2), "event_type": kind,
             "document_id": shared if shared is not None else f"DOC{i:04d}"}
        ]
        for i in range(count)
    }


def _key(value):
    return value


def _kind(row):
    return row["event_type"]


def _all(invoices, receipts):
    return index.cross_po_all_document_source_rows(
        invoices, receipts, document_key=_key,
        invoice_event_type=_kind, receipt_event_type=_kind)


class CrossPoCitationBudgetR475Tests(unittest.TestCase):
    def test_real_budget_rejects_1001_order_invoice_fanout_before_expansion(self):
        # 1001 * 1001 = 1,002,001 citations. Input itself is only 1001 rows.
        with self.assertRaisesRegex(ValueError, "exceeds citation budget") as caught:
            _all(_groups(1001), {})
        self.assertNotIn("PRIVATE_CUSTOMER_DOC", str(caught.exception))
        self.assertNotIn("PO0001", str(caught.exception))

    def test_legacy_invoice_wrapper_has_same_bound(self):
        with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
            index.cross_po_invoice_source_rows(
                _groups(1001), document_key=_key, event_type=_kind)

    def test_large_single_po_document_stays_out_of_cross_order_review(self):
        rows = {
            ("SAME_PO", str(i + 1)): [
                {"row": str(i + 2), "event_type": "invoice",
                 "document_id": "PRIVATE_CUSTOMER_DOC"}]
            for i in range(1001)
        }
        self.assertEqual(_all(rows, {})["invoice"], {})

    def test_distinct_ids_across_many_orders_do_not_trigger_fanout(self):
        self.assertEqual(_all(_groups(1001, shared=None), {})["invoice"], {})

    def test_shared_budget_applies_across_all_four_document_types(self):
        invoices = _groups(2, kind="invoice", shared="INV")
        receipts = _groups(2, kind="receipt", shared="REC")
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 7):
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                _all(invoices, receipts)
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 8):
            actual = _all(invoices, receipts)
        self.assertEqual(actual["invoice"][("PO0000", "1")], ("2", "3"))
        self.assertEqual(actual["receipt"][("PO0001", "1")], ("2", "3"))

    def test_budget_is_conservative_across_overlapping_documents(self):
        invoices = {
            ("P1", "1"): [
                {"row": "2", "event_type": "invoice", "document_id": "A"},
                {"row": "3", "event_type": "invoice", "document_id": "B"}],
            ("P2", "1"): [
                {"row": "4", "event_type": "invoice", "document_id": "A"},
                {"row": "5", "event_type": "invoice", "document_id": "B"}],
        }
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 7):
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                _all(invoices, {})
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 8):
            actual = _all(invoices, {})
        self.assertEqual(actual["invoice"][("P1", "1")], ("2", "3", "4", "5"))
        self.assertEqual(actual["invoice"][("P2", "1")], ("2", "3", "4", "5"))

    def test_four_typed_namespaces_retain_legacy_parity(self):
        invoice = {
            ("P1", "1"): [
                {"row": "2", "event_type": "invoice", "document_id": "I1"},
                {"row": "11", "event_type": "credit", "document_id": "C1"}],
            ("P2", "2"): [
                {"row": "4", "event_type": "invoice", "document_id": "I1"},
                {"row": "13", "event_type": "credit", "document_id": "C1"}],
        }
        receipt = {
            ("P1", "1"): [
                {"row": "3", "event_type": "receipt", "document_id": "R1"},
                {"row": "12", "event_type": "return", "document_id": "T1"}],
            ("P2", "2"): [
                {"row": "6", "event_type": "receipt", "document_id": "R1"},
                {"row": "14", "event_type": "return", "document_id": "T1"}],
        }
        bulk = _all(invoice, receipt)
        for kind, wrapper, records in (
            ("invoice", index.cross_po_invoice_source_rows, invoice),
            ("credit", index.cross_po_credit_source_rows, invoice),
            ("receipt", index.cross_po_receipt_source_rows, receipt),
            ("return", index.cross_po_return_source_rows, receipt),
        ):
            self.assertEqual(bulk[kind], wrapper(
                records, document_key=_key, event_type=_kind))
        self.assertEqual(bulk["invoice"][("P1", "1")], ("2", "4"))
        self.assertEqual(bulk["credit"][("P2", "2")], ("11", "13"))

    def test_deterministic_after_group_and_row_reordering(self):
        invoice = {
            ("P1", "1"): [
                {"row": "11", "event_type": "invoice", "document_id": "DOC"},
                {"row": "2", "event_type": "invoice", "document_id": "DOC"}],
            ("P2", "1"): [
                {"row": "7", "event_type": "invoice", "document_id": "DOC"}],
        }
        original = _all(invoice, {})
        flipped = {key: list(reversed(value))
                   for key, value in reversed(list(invoice.items()))}
        self.assertEqual(original, _all(flipped, {}))
        self.assertEqual(original["invoice"][("P1", "1")], ("2", "7", "11"))


if __name__ == "__main__":
    unittest.main()
