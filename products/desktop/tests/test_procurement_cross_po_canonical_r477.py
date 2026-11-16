"""R477: cross-PO source evidence is deterministic across hashes and input orders.

These are helper-contract tests; no payment or compliance finding is automatic.
"""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import procurement_cross_po_r471 as index


def _row(kind: str, source_row: str, document: str = "SHARED") -> dict[str, str]:
    return {"event_type": kind, "row": source_row, "document_id": document}


def _all(invoice_groups, receipt_groups):
    return index.cross_po_all_document_source_rows(
        invoice_groups, receipt_groups,
        document_key=lambda value: str(value),
        invoice_event_type=lambda row: row["event_type"],
        receipt_event_type=lambda row: row["event_type"])


class CanonicalCrossPoCitationR477Tests(unittest.TestCase):
    def test_numeric_row_ties_have_explicit_textual_tiebreak(self):
        # Noncanonical numeric spellings are a defensive direct-helper case.
        # The real CSV reader supplies ordinary physical row numbers.
        documents = {"K": [
            (("P2", "1"), "02"), (("P1", "2"), "2"),
            (("P3", "1"), "3")]}
        evidence, remaining = index._bounded_index(documents, 9)
        self.assertEqual(remaining, 0)
        self.assertEqual(list(evidence), [("P1", "2"), ("P2", "1"), ("P3", "1")])
        for rows in evidence.values():
            self.assertEqual(rows, ("2", "02", "3"))

    def test_different_document_expansions_merge_in_canonical_row_order(self):
        documents = {
            "K2": [(("Z", "1"), "12"), (("A", "2"), "2")],
            "K1": [(("Z", "1"), "3"), (("A", "2"), "0003")],
        }
        evidence, remaining = index._bounded_index(documents, 8)
        self.assertEqual(remaining, 0)
        self.assertEqual(list(evidence), [("A", "2"), ("Z", "1")])
        self.assertEqual(evidence[("A", "2")], ("2", "3", "0003", "12"))

    def test_all_four_typed_streams_have_canonical_group_order(self):
        invoices = {
            ("Z", "2"): [_row("invoice", "2"), _row("credit", "3")],
            ("A", "1"): [_row("invoice", "4"), _row("credit", "5")],
        }
        receipts = {
            ("Z", "2"): [_row("receipt", "8"), _row("return", "9")],
            ("A", "1"): [_row("receipt", "6"), _row("return", "7")],
        }
        result = _all(invoices, receipts)
        self.assertEqual(list(result), ["invoice", "credit", "receipt", "return"])
        for kind in result:
            self.assertEqual(list(result[kind]), [("A", "1"), ("Z", "2")])
        self.assertEqual(result["invoice"][("A", "1")], ("2", "4"))
        self.assertEqual(result["return"][("Z", "2")], ("7", "9"))

    def test_direct_typed_legacy_wrapper_canonicalizes_too(self):
        groups = {
            ("Z", "1"): [_row("credit", "03")],
            ("A", "2"): [_row("credit", "3")],
            ("M", "1"): [_row("credit", "4")],
        }
        result = index.cross_po_credit_source_rows(
            groups, document_key=lambda value: str(value),
            event_type=lambda row: row["event_type"])
        self.assertEqual(list(result), [("A", "2"), ("M", "1"), ("Z", "1")])
        self.assertEqual(result[("Z", "1")], ("3", "03", "4"))

    def test_seeded_125_input_permutations_produce_identical_serialization(self):
        events = [
            (("Z", "2"), _row("invoice", "11", "A"), True),
            (("B", "1"), _row("invoice", "3", "A"), True),
            (("A", "2"), _row("invoice", "2", "A"), True),
            (("Z", "2"), _row("invoice", "4", "B"), True),
            (("A", "2"), _row("invoice", "5", "B"), True),
            (("Z", "2"), _row("credit", "6", "A"), True),
            (("B", "1"), _row("credit", "7", "A"), True),
            (("Z", "2"), _row("receipt", "9", "A"), False),
            (("A", "2"), _row("receipt", "08", "A"), False),
            (("B", "1"), _row("receipt", "8", "A"), False),
            (("Z", "2"), _row("return", "10", "A"), False),
            (("B", "1"), _row("return", "12", "A"), False),
        ]
        rng = random.Random(477)
        baseline = None
        for _ in range(125):
            shuffled = events[:]
            rng.shuffle(shuffled)
            invoices, receipts = {}, {}
            for group, row, is_invoice in shuffled:
                destination = invoices if is_invoice else receipts
                destination.setdefault(group, []).append(row)
            output = _all(invoices, receipts)
            snapshot = json.dumps([
                (kind, [(group, rows) for group, rows in values.items()])
                for kind, values in output.items()], separators=(",", ":"))
            if baseline is None:
                baseline = snapshot
            self.assertEqual(snapshot, baseline)

    def test_distinct_python_hash_seeds_produce_identical_serialization(self):
        script = """
import json, os, sys
sys.path.insert(0, os.environ["DESKTOP_SOURCE_ROOT"])
from fvs_suite import procurement_cross_po_r471 as p
g = {
    ("Z", "2"): [{"event_type":"invoice","row":"02","document_id":"A"}],
    ("B", "1"): [{"event_type":"invoice","row":"2","document_id":"A"}],
    ("A", "3"): [{"event_type":"invoice","row":"3","document_id":"A"}],
    ("D", "1"): [{"event_type":"invoice","row":"4","document_id":"A"}],
}
out = p.cross_po_all_document_source_rows(
    g, {}, document_key=str,
    invoice_event_type=lambda row: row["event_type"],
    receipt_event_type=lambda row: row["event_type"])
print(json.dumps([(kind,[(group,rows) for group,rows in vals.items()])
                  for kind,vals in out.items()], separators=(",",":")))
"""
        root = str(Path(__file__).resolve().parents[1])
        snapshots = []
        for seed in ("0", "1", "7", "23", "47", "71", "127", "477"):
            env = dict(os.environ)
            env.update(DESKTOP_SOURCE_ROOT=root, PYTHONHASHSEED=seed,
                       PYTHONDONTWRITEBYTECODE="1")
            child = subprocess.run(
                [sys.executable, "-c", script], env=env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
                timeout=15)
            self.assertEqual(child.returncode, 0, child.stderr)
            snapshots.append(child.stdout)
        self.assertEqual(len(set(snapshots)), 1)
        self.assertEqual(json.loads(snapshots[0])[0][1][0][0], ["A", "3"])

    def test_same_po_multiple_lines_remain_not_cross_po(self):
        source = {
            ("A", "2"): [_row("invoice", "03")],
            ("A", "1"): [_row("invoice", "3")],
        }
        self.assertEqual(_all(source, {})["invoice"], {})

    def test_budget_fail_closed_before_materialization_and_without_private_ids(self):
        source = {
            ("PRIVATE_PO_ONE", "2"): [_row("invoice", "2", "PRIVATE-ID")],
            ("PRIVATE_PO_TWO", "1"): [_row("invoice", "3", "PRIVATE-ID")],
        }
        with patch.object(index, "_MAX_CROSS_PO_CITATIONS", 3), \
                patch.object(index, "_materialize_index") as expand:
            with self.assertRaises(ValueError) as captured:
                _all(source, {})
            expand.assert_not_called()
        self.assertEqual(str(captured.exception),
                         "Cross-order document review exceeds citation budget")


if __name__ == "__main__":
    unittest.main()
