"""R481: exact typed foreign-offset evidence with one numeric-row validation per row.

Tests import the real source helper in CI. They never open customer files,
authorize payments, edit originals, or require any premium entitlement.
"""
from __future__ import annotations

import random
import unittest
from unittest.mock import patch

from fvs_suite import procurement_cross_po_r471 as index


def row(kind, document="", related="", physical="2"):
    return {"event_type": kind, "document_id": document,
            "related_document": related, "row": physical}


def review(invoice, receipt, key=lambda value: value):
    return index.cross_po_foreign_offset_source_rows(
        invoice, receipt, document_key=key,
        invoice_event_type=lambda item: item["event_type"],
        receipt_event_type=lambda item: item["event_type"])


class ForeignRowKeyCacheR481Tests(unittest.TestCase):
    def test_one_source_three_rows_ninety_targets_only_three_numeric_validations(self):
        inputs = {("ORIGINAL", "1"): [
            row("invoice", "I", physical="10"),
            row("invoice", "I", physical="02"),
            row("invoice", "I", physical="2"),
            row("invoice", "I", physical="2"),
        ]}
        inputs.update({(f"T{n:03}", "1"): [row("credit", "CM", "I")]
                       for n in range(90)})
        real = index._source_row_sort_key
        with patch.object(index, "_source_row_sort_key", wraps=real) as checked:
            result = review(inputs, {})
        self.assertEqual(checked.call_count, 3)
        self.assertEqual(len(result["credit"]), 90)
        self.assertTrue(all(value == ("2", "02", "10")
                            for value in result["credit"].values()))
        self.assertEqual(list(result["credit"]), sorted(result["credit"]))

    def test_same_row_spelling_in_two_references_validates_only_once(self):
        inputs = {
            ("S1", "1"): [row("invoice", "A", physical="2")],
            ("S2", "1"): [row("invoice", "B", physical="2")],
            ("T1", "1"): [row("credit", "C", "A")],
            ("T2", "1"): [row("credit", "D", "B")],
        }
        real = index._source_row_sort_key
        with patch.object(index, "_source_row_sort_key", wraps=real) as checked:
            got = review(inputs, {})["credit"]
        self.assertEqual(checked.call_count, 1)
        self.assertEqual(got, {("T1", "1"): ("2",), ("T2", "1"): ("2",)})

    def test_cross_type_reused_source_row_uses_one_safe_key(self):
        invoice = {("I", "1"): [row("invoice", "A", physical="2")],
                   ("T", "1"): [row("credit", "C", "A")]}
        receipt = {("R", "1"): [row("receipt", "B", physical="2")],
                   ("U", "1"): [row("return", "D", "B")]}
        real = index._source_row_sort_key
        with patch.object(index, "_source_row_sort_key", wraps=real) as checked:
            got = review(invoice, receipt)
        self.assertEqual(checked.call_count, 1)
        self.assertEqual(got, {"credit": {("T", "1"): ("2",)},
                               "return": {("U", "1"): ("2",)}})

    def test_overlap_of_multiple_references_still_merges_sorted_evidence(self):
        inputs = {
            ("S", "1"): [row("invoice", "A", physical="10"),
                         row("invoice", "B", physical="2")],
            ("T", "1"): [row("credit", "X", "A"),
                         row("credit", "Y", "B")],
            ("U", "1"): [row("credit", "Z", "B")],
        }
        self.assertEqual(review(inputs, {})["credit"],
                         {("T", "1"): ("2", "10"), ("U", "1"): ("2",)})

    def test_same_po_original_suppresses_foreign_reference_without_validation(self):
        inputs = {("S", "1"): [row("invoice", "A", physical="2")],
                  ("T", "1"): [row("invoice", "A", physical="3")],
                  ("T", "9"): [row("credit", "C", "A")]}
        with patch.object(index, "_source_row_sort_key") as checked:
            self.assertEqual(review(inputs, {})["credit"], {})
        checked.assert_not_called()

    def test_late_type_invalid_row_remains_redacted_and_never_returns_partial_report(self):
        invoice = {("S", "1"): [row("invoice", "A", physical="2")],
                   ("T", "1"): [row("credit", "C", "A")]}
        receipt = {("R", "1"): [row("receipt", "B", physical="private/customer/path")],
                   ("U", "1"): [row("return", "D", "B")]}
        with self.assertRaises(ValueError) as caught:
            review(invoice, receipt)
        self.assertEqual(str(caught.exception),
                         "Cross-order review requires numeric source row citations")
        self.assertIsNone(caught.exception.__cause__)

    def test_aggregate_budget_rejected_without_truncated_result(self):
        invoice = {("S", "1"): [row("invoice", "A", physical="2"),
                                row("invoice", "A", physical="3")],
                   ("T", "1"): [row("credit", "C", "A")]}
        receipt = {("R", "1"): [row("receipt", "B", physical="7")],
                   ("U", "1"): [row("return", "D", "B")]}
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 2):
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                review(invoice, receipt)

    def test_unmatched_reference_never_validates_unrelated_original_row(self):
        inputs = {("S", "1"): [row("invoice", "A", physical="private")],
                  ("T", "1"): [row("credit", "C", "UNMATCHED")]}
        with patch.object(index, "_source_row_sort_key") as checked:
            self.assertEqual(review(inputs, {})["credit"], {})
        checked.assert_not_called()

    def test_seeded_oracle_for_two_types_preserves_exact_foreign_citations(self):
        rng = random.Random(481)
        for _ in range(175):
            sources = []
            for original_kind, offset_kind, prefix in (
                    ("invoice", "credit", "I"), ("receipt", "return", "R")):
                groups = {}
                for n in range(8):
                    group = (f"P{n // 2}", str(n % 2))
                    groups[group] = [row(rng.choice((original_kind, offset_kind)),
                                         rng.choice((prefix + "0", prefix + "1", "")),
                                         rng.choice((prefix + "0", prefix + "1", "")),
                                         rng.choice(("2", "02", "10", "11")))
                                     for _ in range(rng.randrange(4))]
                sources.append(groups)
            actual = review(*sources)
            for kind, original_kind, source in (
                    ("credit", "invoice", sources[0]), ("return", "receipt", sources[1])):
                originals = [(group[0], entry["document_id"], entry["row"])
                             for group, values in source.items() for entry in values
                             if entry["event_type"] == original_kind and entry["document_id"]]
                expected_sets = {}
                for group, values in source.items():
                    for entry in values:
                        if entry["event_type"] != kind or not entry["related_document"]:
                            continue
                        if any(po == group[0] and doc == entry["related_document"]
                               for po, doc, _ in originals):
                            continue
                        matches = {physical for po, doc, physical in originals
                                   if po != group[0] and doc == entry["related_document"]}
                        if matches:
                            expected_sets.setdefault(group, set()).update(matches)
                expected = {group: tuple(sorted(rows, key=index._source_row_sort_key))
                            for group, rows in sorted(expected_sets.items())}
                self.assertEqual(actual[kind], expected)


if __name__ == "__main__":
    unittest.main()
