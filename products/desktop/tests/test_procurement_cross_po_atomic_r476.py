"""R476: no cross-PO citation allocation until every typed stream fits."""
from __future__ import annotations

import random
import unittest
from collections import defaultdict
from unittest.mock import patch

from fvs_suite import procurement_cross_po_r471 as index


def _two(kind, document):
    return {
        ("P1", "1"): [{"row": "2", "event_type": kind, "document_id": document}],
        ("P2", "1"): [{"row": "3", "event_type": kind, "document_id": document}],
    }


def _run(invoices, receipts):
    return index.cross_po_all_document_source_rows(
        invoices, receipts, document_key=lambda v: v,
        invoice_event_type=lambda r: r["event_type"],
        receipt_event_type=lambda r: r["event_type"])


def _legacy_oracle(groups, kind):
    """Independent R475-style unbounded set expansion for small valid cases."""
    documents = defaultdict(list)
    for group, rows in groups.items():
        for row in rows:
            if row["event_type"] == kind and row["document_id"]:
                documents[row["document_id"]].append((group, row["row"]))
    expected = defaultdict(set)
    for occurrences in documents.values():
        if len({g[0] for g, _ in occurrences}) < 2:
            continue
        rows = {r for _, r in occurrences}
        for group, _ in occurrences:
            expected[group].update(rows)
    return {group: tuple(sorted(rows, key=int)) for group, rows in expected.items()}


class AtomicCitationPreflightR476Tests(unittest.TestCase):
    def test_later_type_budget_overflow_does_not_expand_first_type(self):
        # R475 expanded invoice evidence (four cells) before discovering that
        # receipt's four additional cells exceed the shared budget of seven.
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 7), \
                patch.object(index, "_materialize_index") as expand:
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                _run(_two("invoice", "PRIVATE_INVOICE"), _two("receipt", "PRIVATE_RECEIPT"))
            expand.assert_not_called()

    def test_second_document_overflow_does_not_expand_first_document(self):
        # A second ID in the SAME typed stream also fails before any output.
        entries = {
            ("P1", "1"): [
                {"row": "2", "event_type": "invoice", "document_id": "A"},
                {"row": "3", "event_type": "invoice", "document_id": "B"}],
            ("P2", "1"): [
                {"row": "4", "event_type": "invoice", "document_id": "A"},
                {"row": "5", "event_type": "invoice", "document_id": "B"}],
        }
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 7), \
                patch.object(index, "_materialize_index") as expand:
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                _run(entries, {})
            expand.assert_not_called()

    def test_at_exact_boundary_all_four_typed_results_are_correct(self):
        invoice = {
            ("P1", "1"): [
                {"row": "2", "event_type": "invoice", "document_id": "I"},
                {"row": "3", "event_type": "credit", "document_id": "C"}],
            ("P2", "1"): [
                {"row": "4", "event_type": "invoice", "document_id": "I"},
                {"row": "5", "event_type": "credit", "document_id": "C"}],
        }
        receipt = {
            ("P1", "1"): [
                {"row": "2", "event_type": "receipt", "document_id": "R"},
                {"row": "3", "event_type": "return", "document_id": "T"}],
            ("P2", "1"): [
                {"row": "4", "event_type": "receipt", "document_id": "R"},
                {"row": "5", "event_type": "return", "document_id": "T"}],
        }
        # 4 citations each × four types = exactly 16.
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 16), \
                patch.object(index, "_materialize_index", wraps=index._materialize_index) as expand:
            result = _run(invoice, receipt)
            self.assertEqual(expand.call_count, 4)
        for kind, rows in (("invoice", ("2", "4")), ("credit", ("3", "5")),
                           ("receipt", ("2", "4")), ("return", ("3", "5"))):
            self.assertEqual(result[kind][("P1", "1")], rows)
            self.assertEqual(result[kind][("P2", "1")], rows)

    def test_one_below_exact_boundary_fails_before_any_type_expansion(self):
        invoice = _two("invoice", "IN")
        receipt = _two("return", "RE")
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 7), \
                patch.object(index, "_materialize_index") as expand:
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                _run(invoice, receipt)
            expand.assert_not_called()

    def test_never_leaks_private_document_or_po_in_error(self):
        invoices = _two("invoice", "SENSITIVE-CUSTOMER-REF")
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 3):
            with self.assertRaises(ValueError) as caught:
                _run(invoices, {})
        self.assertEqual(str(caught.exception),
                         "Cross-order document review exceeds citation budget")
        self.assertNotIn("SENSITIVE-CUSTOMER-REF", str(caught.exception))
        self.assertNotIn("P1", str(caught.exception))

    def test_same_po_multiple_lines_do_not_consume_budget(self):
        invoices = {("P1", str(i)): [
            {"row": str(i + 2), "event_type": "invoice", "document_id": "SAME"}]
            for i in range(100)}
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 0):
            self.assertEqual(_run(invoices, {})["invoice"], {})

    def test_direct_typed_api_preflights_before_any_expansion(self):
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 3), \
                patch.object(index, "_materialize_index") as expand:
            with self.assertRaisesRegex(ValueError, "exceeds citation budget"):
                index.cross_po_invoice_source_rows(
                    _two("invoice", "PRIVATE"),
                    document_key=lambda value: value,
                    event_type=lambda row: row["event_type"])
            expand.assert_not_called()

    def test_seeded_250_cases_match_original_four_type_index(self):
        rng = random.Random(476)
        for case in range(250):
            streams = {kind: {} for kind in ("invoice", "credit", "receipt", "return")}
            for po in range(rng.randrange(1, 7)):
                for kind in streams:
                    if rng.randrange(4) == 0:
                        continue
                    key = (f"PO{po}", str(rng.randrange(1, 4)))
                    streams[kind].setdefault(key, []).append({
                        "row": str(rng.randrange(2, 50)),
                        "event_type": kind,
                        "document_id": rng.choice(["", "X", "Y", "Z"]),
                    })
            invoices = {}
            receipts = {}
            for kind, table in streams.items():
                out = invoices if kind in ("invoice", "credit") else receipts
                for key, rows in table.items():
                    out.setdefault(key, []).extend(rows)
            actual = _run(invoices, receipts)
            for kind, groups in (("invoice", invoices), ("credit", invoices),
                                 ("receipt", receipts), ("return", receipts)):
                with self.subTest(case=case, kind=kind):
                    self.assertEqual(actual[kind], _legacy_oracle(groups, kind))


if __name__ == "__main__":
    unittest.main()
