"""End-to-end procurement review tests using actual CSV inputs/exports."""
from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine


class ProcurementIntegrationR5Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-procurement-r5-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)

    def source(self, name, headers, rows):
        path = self.folder / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
        return str(path)

    @staticmethod
    def report(path):
        with Path(path).open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def inputs(self, invoice_rows, receipt_rows, *,
               po_rows=(("P1", "1", "10", "5"),),
               invoice_headers=("po_number", "line", "quantity", "unit_price",
                                "event_type", "document_id", "related_document"),
               receipt_headers=("po_number", "line", "quantity", "event_type", "document_id")):
        po = self.source("po.csv", ("po_number", "line", "quantity", "unit_price"), po_rows)
        inv = self.source("inv.csv", invoice_headers, invoice_rows)
        rec = self.source("rec.csv", receipt_headers, receipt_rows)
        return po, inv, rec

    def run_report(self, *paths, policy_path=None):
        outputs = engine.procure_guard(*paths, self.folder, policy_path=policy_path)
        self.assertEqual(len(outputs), 2)
        self.assertTrue(outputs[1].exists())
        return self.report(outputs[0])[0], outputs[1]

    def test_legacy_invoice_and_receipt_csv_without_type_columns(self):
        paths = self.inputs([("P1", "1", "10", "5")],
                            [("P1", "1", "10")],
                            invoice_headers=("po_number","line","quantity","unit_price"),
                            receipt_headers=("po_number","line","quantity"))
        row, _ = self.run_report(*paths)
        self.assertEqual(row["status"], "matched")
        self.assertEqual(row["invoice_total"], "50.00")

    def test_legitimate_two_partial_invoices_with_distinct_ids(self):
        paths = self.inputs([
            ("P1","1","5","5","invoice","INV1",""),
            ("P1","1","5","5","invoice","INV2",""),
        ], [("P1","1","10","receipt","RC1")])
        row, _ = self.run_report(*paths)
        self.assertEqual(row["status"], "matched")
        self.assertEqual(row["invoice_documents"], "INV1; INV2")
        self.assertEqual(row["gross_invoice_qty"], "10")

    def test_partial_transaction_is_not_silently_matched(self):
        paths = self.inputs([("P1","1","4","5","invoice","INV1","")],
                            [("P1","1","4","receipt","RC1")])
        row, _ = self.run_report(*paths)
        self.assertIn("partial_invoice_review", row["status"])
        self.assertIn("partial_receipt_review", row["status"])
        self.assertEqual(row["invoiced_qty"], "4")

    def test_credit_and_return_have_separate_gross_and_net_quantities(self):
        paths = self.inputs([
            ("P1","1","10","5","invoice","INV1",""),
            ("P1","1","2","5","credit","CM1","INV1"),
        ], [
            ("P1","1","10","receipt","RC1"),
            ("P1","1","2","return","RT1"),
        ])
        row, manifest = self.run_report(*paths)
        self.assertEqual(row["gross_invoice_qty"], "10")
        self.assertEqual(row["credit_qty"], "2")
        self.assertEqual(row["invoiced_qty"], "8")
        self.assertEqual(row["gross_received_qty"], "10")
        self.assertEqual(row["returned_qty"], "2")
        self.assertEqual(row["received_qty"], "8")
        self.assertEqual(row["invoice_total"], "40.00")
        self.assertIn("credit_memo_review", row["status"])
        self.assertIn("return_review", row["status"])
        self.assertNotIn("unlinked_credit_review", row["status"])
        self.assertIn("SHA-256", manifest.read_text())

    def test_unlinked_credit_never_has_matched_status(self):
        paths = self.inputs([
            ("P1","1","10","5","invoice","INV1",""),
            ("P1","1","2","5","credit","CM1","MISSING"),
        ], [("P1","1","8","receipt","RC1")])
        row, _ = self.run_report(*paths)
        self.assertIn("unlinked_credit_review", row["status"])

    def test_r470_repeated_credit_memo_id_is_separate_review_flag(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "1", "1", "5", "credit", "CM1", "INV1"),
            ("P1", "1", "1", "5", "credit", "CM1", "INV1"),
        ], [("P1", "1", "8", "receipt", "RC1")])
        row, manifest = self.run_report(*paths)
        self.assertIn("repeated_credit_document_id_review", row["status"])
        self.assertIn("credit_memo_review", row["status"])
        self.assertEqual(row["invoiced_qty"], "8")
        self.assertEqual(row["invoice_total"], "40.00")
        self.assertEqual(row["credit_qty"], "2")
        self.assertEqual(row["invoice_rows"], "2;3;4")
        self.assertEqual(row["credit_source_line_links"].count('"offset_row"'), 2)
        self.assertIn("SHA-256", manifest.read_text())

    def test_r470_normalized_credit_id_collision_requires_review(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "1", "1", "5", "credit", "C-M1", "INV1"),
            ("P1", "1", "1", "5", "credit", "CM1", "INV1"),
        ], [("P1", "1", "8", "receipt", "RC1")])
        row, _ = self.run_report(*paths)
        self.assertIn("repeated_credit_document_id_review", row["status"])
        self.assertIn("C-M1", row["invoice_documents"])
        self.assertIn("CM1", row["invoice_documents"])

    def test_r470_distinct_credit_memos_are_not_marked_repeated(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "1", "1", "5", "credit", "CM1", "INV1"),
            ("P1", "1", "1", "5", "credit", "CM2", "INV1"),
        ], [("P1", "1", "8", "receipt", "RC1")])
        row, _ = self.run_report(*paths)
        self.assertNotIn("repeated_credit_document_id_review", row["status"])
        self.assertIn("credit_memo_review", row["status"])

    def test_r470_blank_credit_ids_do_not_fake_duplicate_identity(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "1", "1", "5", "credit", "", "INV1"),
            ("P1", "1", "1", "5", "credit", "", "INV1"),
        ], [("P1", "1", "8", "receipt", "RC1")])
        row, _ = self.run_report(*paths)
        self.assertIn("unlinked_credit_review", row["status"])
        self.assertNotIn("repeated_credit_document_id_review", row["status"])

    def test_r471_normalized_credit_memo_reuse_across_pos_has_source_rows(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "1", "1", "5", "credit", "C-M1", "INV1"),
            ("P2", "1", "10", "5", "invoice", "INV2", ""),
            ("P2", "1", "1", "5", "credit", "CM1", "INV2"),
        ], [
            ("P1", "1", "9", "receipt", "REC1"),
            ("P2", "1", "9", "receipt", "REC2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        outputs = engine.procure_guard(*paths, self.folder)
        rows = self.report(outputs[0])
        self.assertEqual([row["po"] for row in rows], ["P1", "P2"])
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertIn("credit_document_cross_po_review", row["status"])
            self.assertIn("credit_memo_review", row["status"])
            self.assertEqual(row["cross_po_credit_source_rows"], "3;5")
            self.assertEqual(row["invoiced_qty"], "9")
            self.assertEqual(row["invoice_total_exact"], "45")
            self.assertEqual(row["credit_value_exact"], "5")
        self.assertEqual(
            json.loads(rows[0]["credit_source_line_links"]),
            [{"offset_row": "3", "target_rows": ["2"]}],
        )
        self.assertIn("SHA-256", outputs[1].read_text())

    def test_r471_same_credit_spanning_two_lines_one_po_is_not_cross_po(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "1", "1", "5", "credit", "CM1", "INV1"),
            ("P1", "2", "10", "5", "invoice", "INV2", ""),
            ("P1", "2", "1", "5", "credit", "CM1", "INV2"),
        ], [
            ("P1", "1", "9", "receipt", "REC1"),
            ("P1", "2", "9", "receipt", "REC2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P1", "2", "10", "5")))
        outputs = engine.procure_guard(*paths, self.folder)
        rows = self.report(outputs[0])
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertNotIn("credit_document_cross_po_review", row["status"])
            self.assertNotIn("repeated_credit_document_id_review", row["status"])
            self.assertEqual(row["cross_po_credit_source_rows"], "")
            self.assertEqual(row["invoice_total_exact"], "45")

    def test_r471_distinct_credit_ids_across_pos_do_not_collide(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "1", "1", "5", "credit", "CM1", "INV1"),
            ("P2", "1", "10", "5", "invoice", "INV2", ""),
            ("P2", "1", "1", "5", "credit", "CM2", "INV2"),
        ], [
            ("P1", "1", "9", "receipt", "REC1"),
            ("P2", "1", "9", "receipt", "REC2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        rows = self.report(engine.procure_guard(*paths, self.folder)[0])
        for row in rows:
            self.assertNotIn("credit_document_cross_po_review", row["status"])
            self.assertEqual(row["cross_po_credit_source_rows"], "")

    def test_r471_missing_credit_ids_across_pos_stay_unlinked_not_shared(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "1", "1", "5", "credit", "", "INV1"),
            ("P2", "1", "10", "5", "invoice", "INV2", ""),
            ("P2", "1", "1", "5", "credit", "", "INV2"),
        ], [
            ("P1", "1", "9", "receipt", "REC1"),
            ("P2", "1", "9", "receipt", "REC2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        rows = self.report(engine.procure_guard(*paths, self.folder)[0])
        for row in rows:
            self.assertIn("unlinked_credit_review", row["status"])
            self.assertNotIn("credit_document_cross_po_review", row["status"])
            self.assertEqual(row["cross_po_credit_source_rows"], "")

    def test_r471_only_credit_kind_can_trigger_cross_po_review(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "CM1", ""),
            ("P2", "1", "10", "5", "invoice", "INV2", ""),
            ("P2", "1", "1", "5", "credit", "CM1", "INV2"),
        ], [
            ("P1", "1", "10", "receipt", "REC1"),
            ("P2", "1", "9", "receipt", "REC2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        rows = self.report(engine.procure_guard(*paths, self.folder)[0])
        for row in rows:
            self.assertNotIn("credit_document_cross_po_review", row["status"])
            self.assertEqual(row["cross_po_credit_source_rows"], "")

    def test_invalid_negative_quantity_does_not_write_report(self):
        paths = self.inputs([("P1","1","-1","5","credit","CM1","INV1")],
                            [("P1","1","10","receipt","RC1")])
        with self.assertRaisesRegex(ValueError, "(?i)quantity"):
            engine.procure_guard(*paths, self.folder)
        self.assertFalse(list(self.folder.glob("procurement-three-way-*.csv")))

    def test_invalid_event_type_does_not_write_report(self):
        paths = self.inputs([("P1","1","10","5","void","INV1","")],
                            [("P1","1","10","receipt","RC1")])
        with self.assertRaisesRegex(ValueError,"Unsupported invoice event_type"):
            engine.procure_guard(*paths, self.folder)
        self.assertFalse(list(self.folder.glob("procurement-three-way-*.csv")))

    def test_price_policy_source_appears_in_report_and_manifest(self):
        paths = self.inputs([("P1","1","10","5.20","invoice","INV1","")],
                            [("P1","1","10","receipt","RC1")])
        policy = self.folder / "policy.json"
        policy.write_text(json.dumps({"version":1,"price_absolute":"0.00",
                                      "price_fraction":"0.01"}),encoding="utf-8")
        row, manifest = self.run_report(*paths, policy_path=str(policy))
        self.assertIn("price_variance_above_policy", row["status"])
        expected = hashlib.sha256(policy.read_bytes()).hexdigest()
        self.assertEqual(row["price_policy_sha256"], expected)
        self.assertIn(expected, manifest.read_text())
        self.assertEqual(row["price_policy_fraction"], "0.01")

    def test_bad_policy_prevents_report(self):
        paths = self.inputs([("P1","1","10","5","invoice","INV1","")],
                            [("P1","1","10","receipt","RC1")])
        config = self.folder / "policy.json"
        config.write_text('{"version":1,"price_absolute":0.05,"price_fraction":"0.02"}')
        with self.assertRaisesRegex(ValueError,"decimal string"):
            engine.procure_guard(*paths, self.folder, policy_path=str(config))
        self.assertFalse(list(self.folder.glob("procurement-three-way-*.csv")))

    def test_duplicate_header_aliases_fail_closed(self):
        paths = self.inputs([("P1","1","10","5","invoice","INV1","")],
                            [("P1","1","10","receipt","RC1")])
        inv = self.source("inv-ambiguous.csv",(
            "po_number","line","quantity","unit_price","event_type","document_id",
            "invoice_number"),[("P1","1","10","5","invoice","A","B")])
        with self.assertRaisesRegex(ValueError, "ambiguous 'document_id' aliases"):
            engine.procure_guard(paths[0], inv, paths[2], self.folder)
        self.assertFalse(list(self.folder.glob("procurement-three-way-*.csv")))


if __name__ == "__main__":
    unittest.main()
