"""R480 foreign-offset cross-PO fanout and atomic human-review custody.

The native repository module is imported; no network, customer records or
compliance/payment automation is involved.
"""
from __future__ import annotations

import random
import unittest
from unittest.mock import patch

from fvs_suite import procurement_cross_po_r471 as index


def row(kind: str, document: str = "", related: str = "", physical: str = "2") -> dict[str, str]:
    return {"event_type": kind, "document_id": document,
            "related_document": related, "row": physical}


def review(invoice, receipt, document_key=lambda value: value):
    return index.cross_po_foreign_offset_source_rows(
        invoice, receipt, document_key=document_key,
        invoice_event_type=lambda value: value["event_type"],
        receipt_event_type=lambda value: value["event_type"])


class ForeignOffsetFanoutR480Tests(unittest.TestCase):
    def test_one_row_many_foreign_groups_has_one_preflight_validation(self):
        invoice = {("SOURCE", "1"): [row("invoice", "INV", physical="2")]}
        invoice.update({(f"P{n:02}", "1"): [row("credit", f"C{n}", "INV", str(n + 3))]
                        for n in range(30)})
        real = index._source_row_sort_key
        with patch.object(index, "_source_row_sort_key", side_effect=real) as tracked:
            got = review(invoice, {})
        self.assertEqual(len(got["credit"]), 30)
        self.assertEqual(tracked.call_count, 31)  # 1 preflight + 30 output sorts

    def test_many_source_rows_are_deduplicated_before_fanout(self):
        inv = {("ORIG", "1"): [row("invoice", "I", physical="10"),
                               row("invoice", "I", physical="2"),
                               row("invoice", "I", physical="2")]}
        inv.update({(f"C{n}", "1"): [row("credit", "CM", "I")]
                    for n in range(7)})
        self.assertEqual(review(inv, {})["credit"],
                         {(f"C{n}", "1"): ("2", "10") for n in range(7)})

    def test_budget_exact_boundary_allows_fanout(self):
        inv = {("SRC", "1"): [row("invoice", "I", physical="2"),
                              row("invoice", "I", physical="3")]}
        inv.update({(f"X{n}", "1"): [row("credit", "C", "I")]
                    for n in range(5)})
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 10):
            self.assertEqual(len(review(inv, {})["credit"]), 5)

    def test_budget_one_below_rejects_before_any_materialization(self):
        inv = {("SRC", "1"): [row("invoice", "I", physical="2"),
                              row("invoice", "I", physical="3")]}
        inv.update({(f"X{n}", "1"): [row("credit", "C", "I")]
                    for n in range(5)})
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 9):
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                review(inv, {})

    def test_shared_budget_rejects_when_second_type_crosses_limit(self):
        inv = {("P", "1"): [row("invoice", "I", physical="2")],
               ("Q", "1"): [row("credit", "C", "I")]}
        rec = {("P", "1"): [row("receipt", "R", physical="4")],
               ("Q", "1"): [row("return", "RET", "R")]}
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 1):
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                review(inv, rec)

    def test_same_po_any_line_suppresses_foreign_target_even_with_other_po_original(self):
        inv = {("P", "1"): [row("invoice", "I", physical="2")],
               ("Q", "1"): [row("invoice", "I", physical="3")],
               ("Q", "9"): [row("credit", "C", "I")]}
        self.assertEqual(review(inv, {})["credit"], {})

    def test_foreign_groups_only_not_same_po_duplicate_lines(self):
        inv = {("P", "1"): [row("invoice", "I", physical="2")],
               ("P", "2"): [row("invoice", "I", physical="3"),
                             row("credit", "LOCAL", "I")],
               ("Q", "1"): [row("credit", "FOREIGN", "I")]}
        self.assertEqual(review(inv, {})["credit"], {("Q", "1"): ("2", "3")})

    def test_private_source_label_fails_with_fixed_redacted_exception(self):
        inv = {("P", "1"): [row("invoice", "I", physical="secret/private/file.csv")],
               ("Q", "1"): [row("credit", "C", "I")]}
        with self.assertRaises(ValueError) as caught:
            review(inv, {})
        self.assertEqual(str(caught.exception),
                         "Cross-order review requires numeric source row citations")
        self.assertIsNone(caught.exception.__cause__)

    def test_no_ref_or_no_original_is_not_an_alert(self):
        inv = {("P", "1"): [row("invoice", "I")],
               ("Q", "1"): [row("credit", "C", "NOMATCH"), row("credit", "D", "")]}
        self.assertEqual(review(inv, {}), {"credit": {}, "return": {}})

    def test_normalized_references_and_evidence_order(self):
        inv = {("P", "1"): [row("invoice", "INV-1", physical="02"),
                            row("invoice", "INV-1", physical="2")],
               ("Z", "1"): [row("credit", "C", "INV1")],
               ("A", "1"): [row("credit", "C", "INV1")]}
        got = review(inv, {}, lambda value: value.replace("-", ""))["credit"]
        self.assertEqual(list(got), [("A", "1"), ("Z", "1")])
        self.assertEqual(got[("A", "1")], ("2", "02"))

    def test_unrelated_original_types_cannot_satisfy_foreign_reference(self):
        inv = {("P", "1"): [row("invoice", "R")],
               ("Q", "1"): [row("credit", "C", "I")]}
        rec = {("P", "1"): [row("receipt", "I")],
               ("Q", "1"): [row("return", "RET", "R")]}
        self.assertEqual(review(inv, rec), {"credit": {}, "return": {}})

    def test_seeded_randomized_parity_with_reference_specification(self):
        rng = random.Random(480)
        for _ in range(140):
            inv, rec = {}, {}
            for group_index in range(rng.randrange(3, 13)):
                group = (f"P{group_index:02}", str(rng.randrange(1, 4)))
                inv[group] = [row(rng.choice(["invoice", "credit"]),
                                  rng.choice(["I0", "I1", "I2"]),
                                  rng.choice(["I0", "I1", "I2", ""]),
                                  str(group_index + 2)) for _ in range(rng.randrange(0, 4))]
                rec[group] = [row(rng.choice(["receipt", "return"]),
                                  rng.choice(["R0", "R1", "R2"]),
                                  rng.choice(["R0", "R1", "R2", ""]),
                                  str(group_index + 15)) for _ in range(rng.randrange(0, 4))]
            expected = {}
            for offset_kind, original_kind, source in (("credit", "invoice", inv),
                                                      ("return", "receipt", rec)):
                cited = {}
                originals = [(group[0], entry["document_id"], entry["row"])
                             for group, entries in source.items() for entry in entries
                             if entry["event_type"] == original_kind and entry["document_id"]]
                for group, entries in source.items():
                    for entry in entries:
                        if entry["event_type"] != offset_kind or not entry["related_document"]:
                            continue
                        same_po = any(po == group[0] and doc == entry["related_document"]
                                      for po, doc, _ in originals)
                        if same_po:
                            continue
                        rows = {physical for po, doc, physical in originals
                                if po != group[0] and doc == entry["related_document"]}
                        if rows:
                            cited.setdefault(group, set()).update(rows)
                expected[offset_kind] = {g: tuple(sorted(rows, key=index._source_row_sort_key))
                                          for g, rows in sorted(cited.items())}
            self.assertEqual(review(inv, rec), expected)


if __name__ == "__main__":
    unittest.main()
