"""R479: foreign purchase-order offset targets remain review-only and cited.

These tests import the real ProcureGuard helper. No customer files or paid
entitlement are needed; no test authorizes a credit or return.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch

from fvs_suite import procurement_cross_po_r471 as index


def row(kind, ident="", related="", physical="2"):
    return {"event_type": kind, "document_id": ident,
            "related_document": related, "row": physical}


def inspect(invoice, receipt, normalizer=lambda value: value):
    return index.cross_po_foreign_offset_source_rows(
        invoice, receipt, document_key=normalizer,
        invoice_event_type=lambda value: value["event_type"],
        receipt_event_type=lambda value: value["event_type"])


class ForeignOffsetReviewR479Tests(unittest.TestCase):
    def test_credit_foreign_target_cites_original_invoice(self):
        results = inspect({
            ("P1", "1"): [row("invoice", "INV-1", physical="2")],
            ("P2", "1"): [row("credit", "CM-1", "INV-1", "3")]}, {})
        self.assertEqual(results["credit"], {("P2", "1"): ("2",)})
        self.assertEqual(results["return"], {})

    def test_return_foreign_target_cites_original_receipt(self):
        results = inspect({}, {
            ("P1", "1"): [row("receipt", "REC-1", physical="8")],
            ("P2", "1"): [row("return", "RET", "REC-1", "9")]})
        self.assertEqual(results["return"], {("P2", "1"): ("8",)})

    def test_different_lines_same_purchase_order_do_not_trigger(self):
        inv = {("P1", "1"): [row("invoice", "I")],
               ("P1", "2"): [row("credit", "C", "I")]}
        self.assertEqual(inspect(inv, {})["credit"], {})

    def test_local_original_suppresses_foreign_candidate(self):
        inv = {("P1", "1"): [row("invoice", "I", physical="2")],
               ("P2", "1"): [row("invoice", "I", physical="3"),
                              row("credit", "C", "I", "4")]}
        self.assertEqual(inspect(inv, {})["credit"], {})

    def test_normalized_references_match_but_blank_never_matches(self):
        inv = {("P1", "1"): [row("invoice", "AB-1")],
               ("P2", "1"): [row("credit", "CM", "AB1"),
                              row("credit", "", "")]}
        self.assertEqual(inspect(
            inv, {}, lambda value: value.replace("-", ""))["credit"],
            {("P2", "1"): ("2",)})

    def test_credit_and_return_find_only_their_own_source_type(self):
        inv = {("P1", "1"): [row("invoice", "REC")],
               ("P2", "1"): [row("credit", "C", "REC")]}
        rec = {("P1", "1"): [row("receipt", "INV")],
               ("P2", "1"): [row("return", "R", "INV")]}
        result = inspect(inv, rec)
        self.assertEqual(result["credit"][("P2", "1")], ("2",))
        self.assertEqual(result["return"][("P2", "1")], ("2",))

    def test_cross_stream_id_collision_is_not_a_document_link(self):
        inv = {("P1", "1"): [row("invoice", "INV")],
               ("P2", "1"): [row("credit", "C", "REC")]}
        rec = {("P1", "1"): [row("receipt", "REC")],
               ("P2", "1"): [row("return", "R", "INV")]}
        self.assertEqual(inspect(inv, rec), {"credit": {}, "return": {}})

    def test_numeric_citation_ties_and_group_order_are_deterministic(self):
        inv = {("Z", "1"): [row("credit", "C", "I")],
               ("X", "1"): [row("credit", "D", "I")],
               ("A", "1"): [row("invoice", "I", physical="02"),
                             row("invoice", "I", physical="2"),
                             row("invoice", "I", physical="10")]}
        self.assertEqual(inspect(inv, {})["credit"],
                         {("X", "1"): ("2", "02", "10"),
                          ("Z", "1"): ("2", "02", "10")})

    def test_duplicate_references_and_original_rows_deduplicate(self):
        inv = {("A", "1"): [row("invoice", "I", physical="2"),
                             row("invoice", "I", physical="2")],
               ("B", "1"): [row("credit", "C1", "I"),
                             row("credit", "C2", "I")]}
        self.assertEqual(inspect(inv, {})["credit"], {("B", "1"): ("2",)})

    def test_missing_foreign_target_is_not_a_false_positive(self):
        inv = {("A", "1"): [row("invoice", "I")],
               ("B", "1"): [row("credit", "C", "OTHER")]}
        self.assertEqual(inspect(inv, {}), {"credit": {}, "return": {}})

    def test_bad_origin_row_is_redacted_before_evidence_expansion(self):
        inv = {("A", "1"): [row("invoice", "I", physical="PRIVATE/PATH")],
               ("B", "1"): [row("credit", "C", "I")]}
        with self.assertRaises(ValueError) as captured:
            inspect(inv, {})
        self.assertEqual(str(captured.exception),
                         "Cross-order review requires numeric source row citations")
        self.assertIsNone(captured.exception.__cause__)

    def test_expansion_budget_rejects_before_any_partial_report(self):
        inv = {("A", "1"): [row("invoice", "I", physical="2"),
                             row("invoice", "I", physical="3")],
               ("B", "1"): [row("credit", "C", "I")]}
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 1):
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                inspect(inv, {})

    def test_unexpected_events_are_ignored(self):
        inv = {("A", "1"): [row("other", "I")],
               ("B", "1"): [row("credit", "C", "I")]}
        self.assertEqual(inspect(inv, {})["credit"], {})

    def test_source_insertion_order_does_not_change_result(self):
        a = {("A", "1"): [row("invoice", "I", physical="3"),
                          row("invoice", "I", physical="2")],
             ("B", "1"): [row("credit", "C", "I")]}
        b = {("B", "1"): [row("credit", "C", "I")],
             ("A", "1"): [row("invoice", "I", physical="2"),
                          row("invoice", "I", physical="3")]}
        self.assertEqual(inspect(a, {}), inspect(b, {}))

    def test_event_callback_is_invoked_once_per_row(self):
        calls = []
        inputs = {("A", "1"): [row("invoice", "I", physical="2")],
                  ("B", "1"): [row("credit", "C", "I", "3")]}
        result = index.cross_po_foreign_offset_source_rows(
            inputs, {}, document_key=lambda v: v,
            invoice_event_type=lambda v: (calls.append(v["row"]) or v["event_type"]),
            receipt_event_type=lambda v: v["event_type"])
        self.assertEqual(calls, ["2", "3"])
        self.assertEqual(result["credit"][("B", "1")], ("2",))

    def test_unrelated_credits_and_returns_never_fabricate_source_rows(self):
        invoice = {("A", "1"): [row("invoice", "I")],
                   ("B", "1"): [row("credit", "C", "UNRELATED")]}
        receipt = {("A", "1"): [row("receipt", "R")],
                   ("B", "1"): [row("return", "T", "UNRELATED")]}
        self.assertEqual(inspect(invoice, receipt),
                         {"credit": {}, "return": {}})


if __name__ == "__main__":
    unittest.main()
