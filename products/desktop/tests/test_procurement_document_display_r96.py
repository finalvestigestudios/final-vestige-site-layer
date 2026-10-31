"""R96 full procurement review/source-to-report tests (pending complete CI).

All inputs are synthetic; flags require human inspection, never authorize pay.
"""
from __future__ import annotations

import copy
import csv
from pathlib import Path
import tempfile
import unittest

from fvs_suite import engine, procurement


class ProcurementDocumentDisplayR96(unittest.TestCase):
    @staticmethod
    def review(ordered=None, invoices=None, receipts=None):
        if ordered is None:
            ordered = [{"quantity": "9", "unit_price": "5.00"}]
        if invoices is None:
            invoices = [{"quantity": "10", "unit_price": "5.00",
                         "event_type": "invoice", "document_id": "INV\u202e7"},
                        {"quantity": "1", "unit_price": "5.00",
                         "event_type": "credit", "document_id": "CR;7",
                         "related_document": "INV\u202e7"}]
        if receipts is None:
            receipts = [{"quantity": "10", "event_type": "receipt",
                         "document_id": "REC\u00a07"},
                        {"quantity": "1", "event_type": "return",
                         "document_id": "RET\u28007",
                         "related_document": "REC\u00a07"}]
        return procurement.review_line(
            ordered, invoices, receipts, quantity=engine.qty,
            unit_cost=engine.unit_cost, identifier=engine.key,
            policy=procurement.PricePolicy())

    def test_all_five_human_display_columns_escape_source_hazards(self):
        metrics, flags = self.review()
        self.assertEqual(metrics["invoice_documents"], r"CR\u003B7; INV\u202E7")
        self.assertEqual(metrics["credit_references"], r"INV\u202E7")
        self.assertEqual(metrics["return_references"], r"REC\u00A07")
        self.assertEqual(metrics["receipt_documents"], r"REC\u00A07")
        self.assertEqual(metrics["return_documents"], r"RET\u28007")
        self.assertIn("credit_memo_review", flags)
        self.assertIn("return_review", flags)
        self.assertEqual(metrics["invoiced_qty"], "9")
        self.assertEqual(metrics["received_qty"], "9")

    def test_literal_source_escape_distinct_from_hidden_character(self):
        invoices = [{"quantity": "9", "unit_price": "5.00",
                     "event_type": "invoice", "document_id": r"INV\u202E7"}]
        metrics, _ = self.review(invoices=invoices, receipts=[
            {"quantity": "9", "event_type": "receipt", "document_id": r"REC\u202E7"}])
        self.assertEqual(metrics["invoice_documents"], r"INV\\u202E7")
        self.assertEqual(metrics["receipt_documents"], r"REC\\u202E7")

    def test_no_mutation_and_repeat_determinism(self):
        inv = [{"quantity": "9", "unit_price": "5.00",
                "event_type": "invoice", "document_id": "A; B"}]
        rec = [{"quantity": "9", "event_type": "receipt", "document_id": "R\u202e1"}]
        original = copy.deepcopy((inv, rec))
        first = self.review(invoices=inv, receipts=rec)
        self.assertEqual(first, self.review(invoices=inv, receipts=rec))
        self.assertEqual((inv, rec), original)
        self.assertEqual(first[0]["invoice_documents"], r"A\u003B B")

    def test_plain_document_ids_and_money_still_match(self):
        m, flags = self.review(
            invoices=[{"quantity": "9", "unit_price": "5.00",
                       "event_type": "invoice", "document_id": "INV-9"}],
            receipts=[{"quantity": "9", "event_type": "receipt",
                       "document_id": "REC-9"}])
        self.assertEqual(m["invoice_documents"], "INV-9")
        self.assertEqual(m["receipt_documents"], "REC-9")
        self.assertEqual(m["invoice_total"], "45.00")
        self.assertEqual(flags, [])

    def test_csv_source_bytes_unchanged_and_display_columns_present(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r96-procure-") as temp:
            root = Path(temp)
            data = {
                "po.csv": "po_number,line,quantity,unit_price\nPO-1,1,9,5.00\n",
                "invoices.csv": ("po_number,line,quantity,unit_price,document_id\n"
                                 "PO-1,1,9,5.00,INV\u202e7\n"),
                "receipts.csv": ("po_number,line,quantity,document_id\n"
                                 "PO-1,1,9,REC;7\n"),
            }
            paths = []
            for name, content in data.items():
                path = root / name
                path.write_text(content, encoding="utf-8", newline="")
                paths.append(path)
            before = [p.read_bytes() for p in paths]
            outputs = engine.procure_guard(*(str(p) for p in paths), str(root))
            self.assertEqual(len(outputs), 2)
            with outputs[0].open(encoding="utf-8-sig", newline="") as reader:
                rows = list(csv.DictReader(reader))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["invoice_documents"], r"INV\u202E7")
            self.assertEqual(rows[0]["receipt_documents"], r"REC\u003B7")
            self.assertEqual(rows[0]["status"], "matched")
            self.assertTrue(outputs[1].exists())
            self.assertEqual([p.read_bytes() for p in paths], before)


if __name__ == "__main__":
    unittest.main()
