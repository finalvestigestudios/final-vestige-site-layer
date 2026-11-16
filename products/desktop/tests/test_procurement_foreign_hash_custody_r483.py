"""R483: foreign-offset original source rows must be validated BEFORE hashing.

The real checked-out ProcureGuard helper is imported by CI. All examples are
synthetic; evidence is review-only and no file/network/payment I/O occurs.
"""
from __future__ import annotations

import random
import unittest
from unittest.mock import patch

from fvs_suite import procurement_cross_po_r471 as index

SAFE_ERROR = "Cross-order review requires numeric source row citations"


def row(kind, document="", related="", physical="2"):
    return {"event_type": kind, "document_id": document,
            "related_document": related, "row": physical}


def review(invoice, receipt):
    return index.cross_po_foreign_offset_source_rows(
        invoice, receipt, document_key=lambda text: text,
        invoice_event_type=lambda item: item["event_type"],
        receipt_event_type=lambda item: item["event_type"])


def original_and_offset(physical, *, event="invoice"):
    if event == "invoice":
        return ({("SRC", "1"): [row("invoice", "I", physical=physical)],
                 ("DEST", "1"): [row("credit", "C", "I")]}, {})
    return ({}, {("SRC", "1"): [row("receipt", "I", physical=physical)],
                 ("DEST", "1"): [row("return", "R", "I")]})


class ForeignHashCustodyR483Tests(unittest.TestCase):
    def assert_redacted(self, invoice, receipt):
        with self.assertRaises(ValueError) as caught:
            review(invoice, receipt)
        self.assertEqual(str(caught.exception), SAFE_ERROR)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)

    def test_foreign_invoice_object_hash_never_runs(self):
        class PrivateRow:
            def __hash__(self):
                raise AssertionError("private hash callback executed")
        self.assert_redacted(*original_and_offset(PrivateRow()))

    def test_foreign_receipt_object_hash_never_runs(self):
        class PrivateRow:
            def __hash__(self):
                raise AssertionError("private receipt hash callback executed")
        self.assert_redacted(*original_and_offset(PrivateRow(), event="receipt"))

    def test_native_str_subclass_hash_never_runs(self):
        class HostileString(str):
            def __hash__(self):
                raise AssertionError("private subclass hash executed")
        self.assert_redacted(*original_and_offset(HostileString("2")))

    def test_unhashable_row_is_private_value_error(self):
        self.assert_redacted(*original_and_offset({"sensitive": "private"}))

    def test_private_path_and_overlong_digit_sequence_are_redacted(self):
        for physical in ("customer/private/statement.csv", "8" * 5000, "²", "-4"):
            with self.subTest(physical_length=len(physical)):
                self.assert_redacted(*original_and_offset(physical))

    def test_late_invalid_return_does_not_return_partial_credit_review(self):
        invoice, _ = original_and_offset("2")
        _, receipt = original_and_offset("customer/receipt-private",
                                         event="receipt")
        self.assert_redacted(invoice, receipt)

    def test_nonforeign_invalid_source_is_not_examined(self):
        # No foreign source-row citation is needed for a local-only reference.
        invoice = {("SRC", "1"): [row("invoice", "I", physical=object())],
                   ("SRC", "9"): [row("credit", "C", "I")]}
        with patch.object(index, "_source_row_sort_key") as called:
            self.assertEqual(review(invoice, {}), {"credit": {}, "return": {}})
        called.assert_not_called()

    def test_unrelated_invalid_source_is_not_examined(self):
        invoice = {("SRC", "1"): [row("invoice", "I", physical=object())],
                   ("DEST", "1"): [row("credit", "C", "unmatched")]}
        with patch.object(index, "_source_row_sort_key") as called:
            self.assertEqual(review(invoice, {}), {"credit": {}, "return": {}})
        called.assert_not_called()

    def test_valid_citations_remain_numeric_sorted_across_two_review_types(self):
        invoice = {("ORIGIN", "1"): [
                       row("invoice", "I", physical=p)
                       for p in ("10", "02", "2", "2")],
                   ("DEST", "1"): [row("credit", "C", "I")],
                   ("NEXT", "1"): [row("credit", "D", "I")]}
        receipt = {("R-ORIGIN", "1"): [row("receipt", "R", physical="3")],
                   ("R-DEST", "1"): [row("return", "T", "R")]}
        real = index._source_row_sort_key
        with patch.object(index, "_source_row_sort_key", wraps=real) as counted:
            result = review(invoice, receipt)
        self.assertEqual(counted.call_count, 4)
        self.assertEqual(result, {
            "credit": {("DEST", "1"): ("2", "02", "10"),
                       ("NEXT", "1"): ("2", "02", "10")},
            "return": {("R-DEST", "1"): ("3",)}})
        self.assertEqual(list(result["credit"]), [("DEST", "1"), ("NEXT", "1")])

    def test_atomic_budget_fails_without_partial_evidence(self):
        invoice = {("SRC", "1"): [row("invoice", "I", physical="2"),
                                  row("invoice", "I", physical="3")],
                   ("DEST", "1"): [row("credit", "C", "I")],
                   ("NEXT", "1"): [row("credit", "D", "I")]}
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 3):
            with self.assertRaisesRegex(ValueError,
                                        "^Cross-order document review exceeds citation budget$"):
                review(invoice, {})

    def test_source_inputs_not_mutated(self):
        invoice, receipt = original_and_offset("02")
        original = repr((invoice, receipt))
        self.assertEqual(review(invoice, receipt)["credit"],
                         {("DEST", "1"): ("02",)})
        self.assertEqual(repr((invoice, receipt)), original)

    def test_160_seeded_oracle_cases_preserve_foreign_review_only_citations(self):
        rng = random.Random(483)
        for _ in range(160):
            streams = []
            for original_type, offset_type in (("invoice", "credit"),
                                               ("receipt", "return")):
                groups = {}
                po_lines = [(f"PO{i // 2}", str(i % 2)) for i in range(10)]
                rng.shuffle(po_lines)
                for group in po_lines:
                    groups[group] = [row(rng.choice((original_type, offset_type)),
                                         rng.choice(("A", "B", "")),
                                         rng.choice(("A", "B", "")),
                                         rng.choice(("2", "02", "10", "11")))
                                     for unused in range(rng.randrange(5))]
                streams.append(groups)
            actual = review(*streams)
            for kind, original_type, source in (
                    ("credit", "invoice", streams[0]),
                    ("return", "receipt", streams[1])):
                originals = [(group[0], entry["document_id"], entry["row"])
                             for group, records in source.items()
                             for entry in records
                             if entry["event_type"] == original_type
                             and entry["document_id"]]
                expected_sets = {}
                for group, records in source.items():
                    for entry in records:
                        if entry["event_type"] != kind or not entry["related_document"]:
                            continue
                        if any(po == group[0] and doc == entry["related_document"]
                               for po, doc, physical in originals):
                            continue
                        matches = {physical for po, doc, physical in originals
                                   if po != group[0] and doc == entry["related_document"]}
                        if matches:
                            expected_sets.setdefault(group, set()).update(matches)
                expected = {
                    group: tuple(sorted(rows, key=index._source_row_sort_key))
                    for group, rows in sorted(expected_sets.items())}
                self.assertEqual(actual[kind], expected)


if __name__ == "__main__":
    unittest.main()
