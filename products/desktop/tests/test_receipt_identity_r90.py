"""R90: receiving document evidence must be reviewable even when quantities match.

All source records are synthetic. The local engine never approves purchases;
these flags only request human inspection of physical receiving/return records.
"""
from __future__ import annotations

import copy
import csv
from decimal import Decimal, Inexact, Overflow, ROUND_DOWN, Rounded, localcontext
from pathlib import Path
import tempfile
import unittest

from fvs_suite import engine, procurement


def receiving(quantity, document, *, kind="receipt", related=""):
    return {
        "quantity": str(quantity),
        "event_type": kind,
        "document_id": document,
        "related_document": related,
    }


class ReceiptDocumentIdentityR90(unittest.TestCase):
    def review(self, receipt_rows, *, invoice_quantity="10", order_quantity="10"):
        ordered = [{"quantity": order_quantity, "unit_price": "5.00"}]
        invoices = [{
            "quantity": invoice_quantity, "unit_price": "5.00",
            "event_type": "invoice", "document_id": "INV-10",
        }]
        return procurement.review_line(
            ordered, invoices, receipt_rows, quantity=engine.qty,
            unit_cost=engine.unit_cost, identifier=engine.key,
            policy=procurement.PricePolicy(),
        )

    def test_two_distinct_receipts_still_match(self):
        metrics, flags = self.review([receiving(5, "RCPT-1"),
                                      receiving(5, "RCPT-2")])
        self.assertEqual(flags, [])
        self.assertEqual(metrics["received_qty"], "10")
        self.assertEqual(metrics["receipt_documents"], "RCPT-1; RCPT-2")
        self.assertEqual(metrics["return_documents"], "")

    def test_same_receipt_id_requires_review_despite_equal_quantities(self):
        metrics, flags = self.review([receiving(5, "RCPT-1"),
                                      receiving(5, "RCPT-1")])
        self.assertEqual(flags, ["repeated_receipt_document_id_review"])
        self.assertEqual(metrics["received_qty"], "10")
        self.assertEqual(metrics["receipt_documents"], "RCPT-1")

    def test_punctuation_normalized_receipt_collision_requires_review(self):
        metrics, flags = self.review([receiving(5, "RCPT-1"),
                                      receiving(5, "RCPT1")])
        self.assertIn("repeated_receipt_document_id_review", flags)
        self.assertEqual(metrics["receipt_documents"], "RCPT-1; RCPT1")

    def test_ascii_case_receipt_collision_requires_review(self):
        _, flags = self.review([receiving(5, "rcpt-1"),
                                receiving(5, "RCPT-1")])
        self.assertIn("repeated_receipt_document_id_review", flags)

    def test_invisible_unicode_receipt_source_is_unambiguous_in_display(self):
        metrics, flags = self.review([receiving(5, "RCPT\u202E1"),
                                      receiving(5, "RCPT\\u202E1")])
        self.assertNotIn("repeated_receipt_document_id_review", flags)
        self.assertIn(r"RCPT\u202E1", metrics["receipt_documents"])
        self.assertIn(r"RCPT\\u202E1", metrics["receipt_documents"])

    def test_empty_optional_receipt_ids_do_not_conflate_documents(self):
        metrics, flags = self.review([receiving(5, ""), receiving(5, "")])
        self.assertNotIn("repeated_receipt_document_id_review", flags)
        self.assertEqual(metrics["receipt_documents"], "")

    def test_many_distinct_receipts_keep_deterministic_totals(self):
        receipts = [receiving(1, f"RCPT-{i:04d}") for i in range(500)]
        metrics, flags = self.review(receipts, invoice_quantity="500",
                                     order_quantity="500")
        self.assertEqual(flags, [])
        self.assertEqual(metrics["received_qty"], "500")
        self.assertEqual(len(metrics["receipt_documents"].split("; ")), 500)

    def test_repeated_return_document_requires_review(self):
        receipts = [receiving(10, "REC-1"),
                    receiving(2, "RET-1", kind="return", related="REC-1"),
                    receiving(3, "RET1", kind="return", related="REC-1")]
        metrics, flags = self.review(receipts, invoice_quantity="5")
        self.assertIn("repeated_return_document_id_review", flags)
        self.assertIn("return_review", flags)
        self.assertEqual(metrics["return_documents"], "RET-1; RET1")
        self.assertEqual(metrics["returned_qty"], "5")

    def test_return_reusing_receipt_id_requires_review(self):
        receipts = [receiving(8, "REC-1"),
                    receiving(3, "REC-1", kind="return", related="REC-1")]
        metrics, flags = self.review(receipts, invoice_quantity="5")
        self.assertIn("reused_receipt_document_id_review", flags)
        self.assertNotIn("repeated_receipt_document_id_review", flags)
        self.assertEqual(metrics["receipt_documents"], "REC-1")
        self.assertEqual(metrics["return_documents"], "REC-1")

    def test_return_with_distinct_document_does_not_reuse_receipt(self):
        receipts = [receiving(8, "REC-1"),
                    receiving(3, "RET-1", kind="return", related="REC-1")]
        _, flags = self.review(receipts, invoice_quantity="5")
        self.assertNotIn("reused_receipt_document_id_review", flags)
        self.assertNotIn("repeated_return_document_id_review", flags)
        self.assertIn("return_review", flags)

    def test_blank_return_document_keeps_existing_review_flag(self):
        _, flags = self.review([receiving(8, "REC-1"),
                                receiving(3, "", kind="return", related="REC-1")],
                               invoice_quantity="5")
        self.assertIn("unidentified_return_review", flags)
        self.assertNotIn("reused_receipt_document_id_review", flags)

    def test_identical_call_is_deterministic_and_does_not_mutate_inputs(self):
        receipts = [receiving(5, "RCPT-1"), receiving(5, "RCPT1")]
        snapshot = copy.deepcopy(receipts)
        first = self.review(receipts)
        second = self.review(receipts)
        self.assertEqual(first, second)
        self.assertEqual(receipts, snapshot)

    def test_caller_decimal_context_does_not_change_identity_flags(self):
        receipts = [receiving(5, "RCPT-1"), receiving(5, "RCPT-1")]
        expected = self.review(receipts)
        with localcontext() as caller:
            caller.prec = 3
            caller.Emax = 6
            caller.Emin = -6
            caller.rounding = ROUND_DOWN
            for signal in (Inexact, Rounded, Overflow):
                caller.traps[signal] = True
            before = caller.copy()
            actual = self.review(receipts)
            self.assertEqual(caller.traps, before.traps)
            self.assertEqual(caller.flags, before.flags)
        self.assertEqual(actual, expected)

    def test_receipt_reuse_not_confused_with_invoice_document_id(self):
        _, flags = self.review([receiving(5, "INV-10"),
                                receiving(5, "REC-2")])
        self.assertEqual(flags, [])


class ReceiptSourceToManifestR90(unittest.TestCase):
    def run_csv(self, receipt_text, *, po_qty="10", invoice_qty="10"):
        with tempfile.TemporaryDirectory(prefix="fvs-r90-") as temp:
            folder = Path(temp)
            contents = {
                "po.csv": "po_number,line,quantity,unit_price\nPO-A,1," + po_qty + ",5.00\n",
                "inv.csv": ("po_number,line,quantity,unit_price,document_id\n"
                            "PO-A,1," + invoice_qty + ",5.00,INV-10\n"),
                "rec.csv": receipt_text,
            }
            paths = []
            for filename, data in contents.items():
                path = folder / filename
                path.write_text(data, encoding="utf-8", newline="")
                paths.append(path)
            originals = [p.read_bytes() for p in paths]
            reports = engine.procure_guard(*(str(path) for path in paths),
                                            str(folder))
            self.assertEqual(len(reports), 2)
            self.assertTrue(reports[1].is_file())
            with reports[0].open("r", encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual([p.read_bytes() for p in paths], originals)
            self.assertEqual(len(rows), 1)
            return rows[0]

    def test_csv_duplicate_receipt_stays_reviewable_and_cites_physical_rows(self):
        row = self.run_csv(
            "po_number,line,quantity,document_id\n"
            "PO-A,1,5,REC-1\nPO-A,1,5,REC-1\n"
        )
        self.assertIn("repeated_receipt_document_id_review", row["status"])
        self.assertEqual(row["receipt_rows"], "2;3")
        self.assertEqual(row["received_qty"], "10")
        self.assertEqual(row["receipt_documents"], "REC-1")
        self.assertIn("return_documents", row)

    def test_csv_receipt_number_alias_is_checked(self):
        row = self.run_csv(
            "po_number,line,quantity,receipt_number\n"
            "PO-A,1,5,REC-1\nPO-A,1,5,REC1\n"
        )
        self.assertIn("repeated_receipt_document_id_review", row["status"])

    def test_csv_unique_receipts_stay_matched(self):
        row = self.run_csv(
            "po_number,line,quantity,document_id\n"
            "PO-A,1,5,REC-1\nPO-A,1,5,REC-2\n"
        )
        self.assertEqual(row["status"], "matched")
        self.assertEqual(row["receipt_documents"], "REC-1; REC-2")

    def test_csv_return_reusing_receipt_document_remains_flagged(self):
        row = self.run_csv(
            "po_number,line,quantity,event_type,document_id,related_document\n"
            "PO-A,1,8,receipt,REC-1,\n"
            "PO-A,1,3,return,REC-1,REC-1\n", invoice_qty="5"
        )
        self.assertIn("reused_receipt_document_id_review", row["status"])
        self.assertEqual(row["received_qty"], "5")
        self.assertEqual(row["return_documents"], "REC-1")

    def test_invalid_receipt_type_does_not_publish_partial_bundle(self):
        with tempfile.TemporaryDirectory(prefix="fvs-r90-invalid-") as temp:
            root = Path(temp)
            sources = {
                "po.csv": "po_number,line,quantity,unit_price\nPO-A,1,1,5.00\n",
                "inv.csv": "po_number,line,quantity,unit_price\nPO-A,1,1,5.00\n",
                "rec.csv": "po_number,line,quantity,event_type\nPO-A,1,1,unknown\n",
            }
            for name, content in sources.items():
                (root / name).write_text(content, encoding="utf-8")
            with self.assertRaises(ValueError):
                engine.procure_guard(*(str(root / x) for x in sources), str(root))
            self.assertFalse(list(root.glob("procurement-evidence-*")))


if __name__ == "__main__":
    unittest.main()
