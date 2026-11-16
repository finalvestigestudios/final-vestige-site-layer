"""R482: four-type original document reuse caches privacy-validated row ordering.

This native unittest imports the real suite module on checkout/CI. It only
computes human-review citations: no payment approvals, network or file I/O.
"""
from __future__ import annotations

import random
import unittest
from unittest.mock import patch

from fvs_suite import procurement_cross_po_r471 as index


def row(kind, identifier="A", physical="2"):
    return {"event_type": kind, "document_id": identifier, "row": physical}


def review(invoice, receipt):
    return index.cross_po_all_document_source_rows(
        invoice, receipt, document_key=lambda value: value,
        invoice_event_type=lambda item: item["event_type"],
        receipt_event_type=lambda item: item["event_type"])


class SharedRowKeyCacheR482Tests(unittest.TestCase):
    def test_thirty_invoice_groups_parse_single_source_row_once(self):
        invoices = {(f"PO{n:02}", "1"): [row("invoice", "I", "2")]
                    for n in range(30)}
        real = index._source_row_sort_key
        with patch.object(index, "_source_row_sort_key", wraps=real) as tracked:
            evidence = review(invoices, {})["invoice"]
        self.assertEqual(tracked.call_count, 1)
        self.assertEqual(len(evidence), 30)
        self.assertTrue(all(value == ("2",) for value in evidence.values()))

    def test_four_document_types_share_one_validated_physical_spelling(self):
        invoices = {("P", "1"): [row("invoice", "I"), row("credit", "C")],
                    ("Q", "1"): [row("invoice", "I"), row("credit", "C")]}
        receipts = {("P", "1"): [row("receipt", "R"), row("return", "T")],
                    ("Q", "1"): [row("receipt", "R"), row("return", "T")]}
        real = index._source_row_sort_key
        with patch.object(index, "_source_row_sort_key", wraps=real) as tracked:
            evidence = review(invoices, receipts)
        self.assertEqual(tracked.call_count, 1)
        self.assertEqual(set(evidence), {"invoice", "credit", "receipt", "return"})
        for kind in evidence:
            self.assertEqual(evidence[kind], {("P", "1"): ("2",),
                                              ("Q", "1"): ("2",)})

    def test_legacy_typed_credit_wrapper_uses_the_same_single_parse(self):
        invoices = {(f"P{n:02}", "1"): [row("credit", "C", "12")]
                    for n in range(25)}
        real = index._source_row_sort_key
        with patch.object(index, "_source_row_sort_key", wraps=real) as tracked:
            result = index.cross_po_credit_source_rows(
                invoices, document_key=lambda value: value,
                event_type=lambda value: value["event_type"])
        self.assertEqual(tracked.call_count, 1)
        self.assertEqual(len(result), 25)

    def test_canonical_numeric_and_leading_zero_order_does_not_change(self):
        inputs = {("B", "4"): [row("invoice", "I", "10"),
                                 row("invoice", "I", "02")],
                  ("A", "9"): [row("invoice", "I", "2"),
                                 row("invoice", "I", "10")]}
        evidence = review(inputs, {})["invoice"]
        self.assertEqual(list(evidence), [("A", "9"), ("B", "4")])
        self.assertEqual(evidence[("A", "9")], ("2", "02", "10"))
        self.assertEqual(evidence[("B", "4")], ("2", "02", "10"))

    def test_distinct_documents_merge_into_group_once(self):
        inputs = {("A", "1"): [row("invoice", "X", "10"), row("invoice", "Y", "2")],
                  ("B", "1"): [row("invoice", "X", "10"), row("invoice", "Y", "2")],
                  ("C", "1"): [row("invoice", "Y", "2")]}
        evidence = review(inputs, {})["invoice"]
        self.assertEqual(evidence, {("A", "1"): ("2", "10"),
                                    ("B", "1"): ("2", "10"),
                                    ("C", "1"): ("2",)})

    def test_same_po_other_line_alone_does_not_cross_alert(self):
        invoices = {("P", "1"): [row("invoice", "I", "2")],
                    ("P", "2"): [row("invoice", "I", "3")]}
        with patch.object(index, "_source_row_sort_key") as checked:
            self.assertEqual(review(invoices, {})["invoice"], {})
        checked.assert_not_called()

    def test_second_type_invalid_private_row_fails_before_any_materialization(self):
        invoices = {("P", "1"): [row("invoice", "I", "2")],
                    ("Q", "1"): [row("invoice", "I", "2")]}
        receipts = {("R", "1"): [row("receipt", "R", "customer/private.csv")],
                    ("S", "1"): [row("receipt", "R", "2")]}
        with patch.object(index, "_materialize_index", side_effect=AssertionError(
                "Partial report materialized")):
            with self.assertRaises(ValueError) as caught:
                review(invoices, receipts)
        self.assertEqual(str(caught.exception),
                         "Cross-order review requires numeric source row citations")
        self.assertIsNone(caught.exception.__cause__)

    def test_late_budget_failure_does_not_render_early_document_type(self):
        invoices = {("P", "1"): [row("invoice", "I", "2")],
                    ("Q", "1"): [row("invoice", "I", "2")]}
        receipts = {("P", "1"): [row("receipt", "R", "3")],
                    ("Q", "1"): [row("receipt", "R", "3")]}
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 2):
            with patch.object(index, "_materialize_index", side_effect=AssertionError(
                    "Partial report materialized")):
                with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                    review(invoices, receipts)

    def test_hostile_row_object_never_hashed_before_privacy_validation(self):
        class Hostile:
            def __hash__(self):
                raise AssertionError("Hash must not execute on unknown row objects")
        bad = Hostile()
        invoices = {("P", "1"): [row("invoice", "I", bad)],
                    ("Q", "1"): [row("invoice", "I", "2")]}
        with self.assertRaises(ValueError) as caught:
            review(invoices, {})
        self.assertEqual(str(caught.exception),
                         "Cross-order review requires numeric source row citations")

    def test_same_numeric_different_spelling_not_collapsed(self):
        invoices = {("P", "1"): [row("invoice", "I", "2")],
                    ("Q", "1"): [row("invoice", "I", "02")]}
        real = index._source_row_sort_key
        with patch.object(index, "_source_row_sort_key", wraps=real) as tracked:
            evidence = review(invoices, {})["invoice"]
        self.assertEqual(tracked.call_count, 2)
        self.assertEqual(evidence[("P", "1")], ("2", "02"))

    def test_no_mutation_of_imported_source_rows(self):
        invoices = {("P", "1"): [row("invoice", "I", "2")],
                    ("Q", "1"): [row("invoice", "I", "3")]}
        before = repr(invoices)
        review(invoices, {})
        self.assertEqual(repr(invoices), before)

    def test_randomized_four_type_reference_oracle(self):
        rng = random.Random(482)
        for _ in range(220):
            invoice, receipt = {}, {}
            for source, kinds in ((invoice, ("invoice", "credit")),
                                  (receipt, ("receipt", "return"))):
                groups = [(f"P{n // 2}", str(n % 2)) for n in range(8)]
                rng.shuffle(groups)
                for group in groups:
                    source[group] = [row(rng.choice(kinds), rng.choice(("A", "B", "")),
                                         rng.choice(("2", "02", "3", "10")))
                                     for _ in range(rng.randrange(5))]
            actual = review(invoice, receipt)
            for kind, source in (("invoice", invoice), ("credit", invoice),
                                 ("receipt", receipt), ("return", receipt)):
                by_id = {}
                for group, records in source.items():
                    for record in records:
                        if record["event_type"] == kind and record["document_id"]:
                            by_id.setdefault(record["document_id"], []).append(
                                (group, record["row"]))
                expected_sets = {}
                for occurrences in by_id.values():
                    if len({group[0] for group, _ in occurrences}) < 2:
                        continue
                    all_rows = {physical for _, physical in occurrences}
                    for group, _ in occurrences:
                        expected_sets.setdefault(group, set()).update(all_rows)
                expected = {group: tuple(sorted(physical, key=index._source_row_sort_key))
                            for group, physical in sorted(expected_sets.items())}
                self.assertEqual(actual[kind], expected)


if __name__ == "__main__":
    unittest.main()
