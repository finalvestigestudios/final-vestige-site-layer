"""Full CSV ProcureGuard integration checks for R479 foreign offset targets.

Native Windows packaging and hosted six-app CI still require separate gates.
"""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine


class ProcureGuardForeignOffsetIntegrationR479Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-foreign-offset-r479-")
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name)

    def write_source(self, name, headers, rows):
        path = self.directory / name
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            writer.writerows(rows)
        return path

    def report(self, po_rows, invoice_rows, receipt_rows):
        po = self.write_source(
            "po.csv", ("po_number", "line", "quantity", "unit_price"), po_rows)
        invoice = self.write_source(
            "invoice.csv", ("po_number", "line", "quantity", "unit_price",
                            "event_type", "document_id", "related_document"),
            invoice_rows)
        receipt = self.write_source(
            "receipt.csv", ("po_number", "line", "quantity", "event_type",
                            "document_id", "related_document"), receipt_rows)
        outputs = engine.procure_guard(str(po), str(invoice), str(receipt),
                                      str(self.directory / "reports"))
        self.assertEqual(len(outputs), 2)
        self.assertTrue(outputs[1].exists())
        with outputs[0].open("r", newline="", encoding="utf-8-sig") as handle:
            rows = {row["po"]: row for row in csv.DictReader(handle)}
        # Existing input custody remains a SHA-256 of the parsed source bytes.
        for row in rows.values():
            self.assertEqual(row["invoice_source_sha256"],
                             hashlib.sha256(invoice.read_bytes()).hexdigest())
            self.assertEqual(row["receipt_source_sha256"],
                             hashlib.sha256(receipt.read_bytes()).hexdigest())
        return rows

    def test_credit_reference_elsewhere_is_reviewed_with_invoice_source_row(self):
        rows = self.report(
            [("P1", "1", "10", "5"), ("P2", "1", "10", "5")],
            [("P1", "1", "10", "5", "invoice", "INV-A", ""),
             ("P2", "1", "10", "5", "invoice", "INV-B", ""),
             ("P2", "1", "2", "5", "credit", "CM-B", "INV-A")],
            [("P1", "1", "10", "receipt", "RC-A", ""),
             ("P2", "1", "8", "receipt", "RC-B", "")])
        self.assertIn("credit_reference_cross_po_review", rows["P2"]["status"])
        self.assertIn("unlinked_credit_review", rows["P2"]["status"])
        self.assertEqual(rows["P2"]["cross_po_credit_target_rows"], "2")
        self.assertEqual(rows["P2"]["invoice_total_exact"], "40")
        self.assertEqual(rows["P1"]["cross_po_credit_target_rows"], "")
        self.assertNotIn("credit_reference_cross_po_review", rows["P1"]["status"])

    def test_return_reference_elsewhere_is_reviewed_with_receipt_source_row(self):
        rows = self.report(
            [("P1", "1", "10", "5"), ("P2", "1", "10", "5")],
            [("P1", "1", "10", "5", "invoice", "INV-A", ""),
             ("P2", "1", "8", "5", "invoice", "INV-B", "")],
            [("P1", "1", "10", "receipt", "RC-A", ""),
             ("P2", "1", "10", "receipt", "RC-B", ""),
             ("P2", "1", "2", "return", "RT-B", "RC-A")])
        self.assertIn("return_reference_cross_po_review", rows["P2"]["status"])
        self.assertIn("unlinked_return_review", rows["P2"]["status"])
        self.assertEqual(rows["P2"]["cross_po_return_target_rows"], "2")
        self.assertEqual(rows["P2"]["received_qty"], "8")
        self.assertNotIn("return_reference_cross_po_review", rows["P1"]["status"])

    def test_local_original_suppresses_foreign_link_but_keeps_other_review_flags(self):
        rows = self.report(
            [("P1", "1", "10", "5"), ("P2", "1", "10", "5")],
            [("P1", "1", "10", "5", "invoice", "INV-A", ""),
             ("P2", "1", "10", "5", "invoice", "INV-A", ""),
             ("P2", "1", "2", "5", "credit", "CM-B", "INV-A")],
            [("P1", "1", "10", "receipt", "R-A", ""),
             ("P2", "1", "8", "receipt", "R-B", "")])
        self.assertEqual(rows["P2"]["cross_po_credit_target_rows"], "")
        self.assertNotIn("credit_reference_cross_po_review", rows["P2"]["status"])
        self.assertIn("invoice_document_cross_po_review", rows["P2"]["status"])

    def test_unlinked_reference_with_no_foreign_original_does_not_fabricate_evidence(self):
        rows = self.report(
            [("P1", "1", "10", "5")],
            [("P1", "1", "10", "5", "invoice", "INV-A", ""),
             ("P1", "1", "2", "5", "credit", "CM-A", "UNKNOWN")],
            [("P1", "1", "8", "receipt", "R-A", "")])
        self.assertIn("unlinked_credit_review", rows["P1"]["status"])
        self.assertEqual(rows["P1"]["cross_po_credit_target_rows"], "")
        self.assertEqual(rows["P1"]["cross_po_return_target_rows"], "")
        self.assertNotIn("credit_reference_cross_po_review", rows["P1"]["status"])


if __name__ == "__main__":
    unittest.main()
