"""R478: cross-order evidence row parsing must never disclose private text.

Direct helper callers are deliberately tested with forged rows, in addition to
normal parser-generated physical line numbers. No test approves a payment.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from fvs_suite import procurement_cross_po_r471 as index


ERROR = "Cross-order review requires numeric source row citations"


def _row(kind: str, physical: object, document: str = "PRIVATE-DOC") -> dict:
    return {"event_type": kind, "row": physical, "document_id": document}


def _two(kind: str, physical: object) -> dict:
    return {
        ("PRIVATE-PO-A", "1"): [_row(kind, "2")],
        ("PRIVATE-PO-B", "1"): [_row(kind, physical)],
    }


def _all(invoices, receipts):
    return index.cross_po_all_document_source_rows(
        invoices, receipts,
        document_key=lambda value: value,
        invoice_event_type=lambda item: item["event_type"],
        receipt_event_type=lambda item: item["event_type"],
    )


class PrivateCrossPoCitationR478Tests(unittest.TestCase):
    def assert_private_rejection(self, invoice, receipt, secret):
        with patch.object(index, "_materialize_index") as expand:
            with self.assertRaises(ValueError) as caught:
                _all(invoice, receipt)
            expand.assert_not_called()
        self.assertEqual(str(caught.exception), ERROR)
        if secret:
            self.assertNotIn(secret, str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_private_invoice_label_does_not_leak(self):
        self.assert_private_rejection(_two("invoice", "SECRET-LEDGER-ROW"), {},
                                      "SECRET-LEDGER-ROW")

    def test_later_receipt_error_prevents_earlier_invoice_expansion(self):
        self.assert_private_rejection(_two("invoice", "3"),
                                      _two("receipt", "SECRET-RECEIPT-ROW"),
                                      "SECRET-RECEIPT-ROW")

    def test_later_return_error_prevents_earlier_credit_expansion(self):
        self.assert_private_rejection(_two("credit", "4"),
                                      _two("return", "PRIVATE-PATH/abc.csv"),
                                      "PRIVATE-PATH/abc.csv")

    def test_invalid_numeric_shapes_are_private_safe(self):
        for bad in ("-3", "+3", "3.0", " 3", "3 ", "3\nX", "3\t", "", "\u0663", "\uff13"):
            with self.subTest(repr=repr(bad)):
                self.assert_private_rejection(_two("invoice", bad), {}, bad)

    def test_overlong_ascii_integer_and_python_digit_limit_fail_safely(self):
        for bad in ("1" * 11, "3" * 4301):
            with self.subTest(digits=len(bad)):
                self.assert_private_rejection(_two("invoice", bad), {}, "33333333")

    def test_non_native_integer_citation_rejected_without_coercion(self):
        self.assert_private_rejection(_two("invoice", 3), {}, "PRIVATE-DOC")

    def test_hostile_object_str_is_never_called(self):
        class Hostile:
            def __str__(self):
                raise AssertionError("FORBIDDEN_PRIVATE_CALLBACK")

            def __repr__(self):
                raise AssertionError("FORBIDDEN_REPR_CALLBACK")

        self.assert_private_rejection(_two("invoice", Hostile()), {}, "PRIVATE-DOC")

    def test_legacy_typed_wrapper_uses_same_private_safe_preflight(self):
        with patch.object(index, "_materialize_index") as expand:
            with self.assertRaises(ValueError) as caught:
                index.cross_po_credit_source_rows(
                    _two("credit", "CONFIDENTIAL-ROW"),
                    document_key=lambda value: value,
                    event_type=lambda item: item["event_type"])
            expand.assert_not_called()
        self.assertEqual(str(caught.exception), ERROR)

    def test_direct_bounded_index_requires_valid_row_before_expansion(self):
        occurrences = {"DOC": [(("PO-A", "1"), "2"),
                               (("PO-B", "1"), "SECRET-CITATION")]}
        with patch.object(index, "_materialize_index") as expand:
            with self.assertRaises(ValueError) as caught:
                index._bounded_index(occurrences, 100)
            expand.assert_not_called()
        self.assertEqual(str(caught.exception), ERROR)

    def test_valid_noncanonical_numeric_ties_keep_r477_order(self):
        results = _all({
            ("Z", "1"): [_row("invoice", "02")],
            ("A", "1"): [_row("invoice", "2")],
            ("B", "1"): [_row("invoice", "0003")],
        }, {})["invoice"]
        self.assertEqual(list(results), [("A", "1"), ("B", "1"), ("Z", "1")])
        for citations in results.values():
            self.assertEqual(citations, ("2", "02", "0003"))

    def test_unlinked_non_cross_order_documents_remain_without_review(self):
        results = _all({("P", "1"): [_row("invoice", "2")],
                        ("P", "2"): [_row("invoice", "3")]}, {})
        self.assertEqual(results["invoice"], {})

    def test_distinct_document_ids_preserve_no_cross_po_alert(self):
        results = _all({("P1", "1"): [_row("invoice", "2", "DOC-A")],
                        ("P2", "1"): [_row("invoice", "3", "DOC-B")]}, {})
        self.assertEqual(results["invoice"], {})

    def test_all_four_valid_event_kinds_still_build_distinct_evidence(self):
        invoice = {
            ("P1", "1"): [_row("invoice", "2"), _row("credit", "3")],
            ("P2", "1"): [_row("invoice", "4"), _row("credit", "5")],
        }
        receipt = {
            ("P1", "1"): [_row("receipt", "6"), _row("return", "7")],
            ("P2", "1"): [_row("receipt", "8"), _row("return", "9")],
        }
        result = _all(invoice, receipt)
        self.assertEqual(tuple(result), ("invoice", "credit", "receipt", "return"))
        expected = {"invoice": ("2", "4"), "credit": ("3", "5"),
                    "receipt": ("6", "8"), "return": ("7", "9")}
        for kind, rows in expected.items():
            self.assertEqual(result[kind][("P1", "1")], rows)
            self.assertEqual(result[kind][("P2", "1")], rows)

    def test_existing_budget_preflight_is_still_atomic(self):
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 3), \
                patch.object(index, "_materialize_index") as expand:
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                _all(_two("invoice", "3"), {})
            expand.assert_not_called()


if __name__ == "__main__":
    unittest.main()
