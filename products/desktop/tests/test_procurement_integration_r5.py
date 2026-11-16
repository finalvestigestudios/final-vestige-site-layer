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

    def test_r472_normalized_invoice_id_across_pos_is_flagged_with_source_rows(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "I-NV1", ""),
            ("P2", "1", "10", "5", "invoice", "INV1", ""),
        ], [
            ("P1", "1", "10", "receipt", "R1"),
            ("P2", "1", "10", "receipt", "R2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        outputs = engine.procure_guard(*paths, self.folder)
        rows = self.report(outputs[0])
        self.assertEqual([row["po"] for row in rows], ["P1", "P2"])
        for item in rows:
            self.assertIn("invoice_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_invoice_source_rows"], "2;3")
            self.assertEqual(item["invoiced_qty"], "10")
            self.assertEqual(item["invoice_total_exact"], "50")
            self.assertEqual(item["credit_qty"], "0")
            self.assertEqual(len(item["invoice_source_sha256"]), 64)
        self.assertIn("SHA-256", outputs[1].read_text())

    def test_r472_multi_line_invoice_one_po_not_cross_po(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "2", "10", "5", "invoice", "INV1", ""),
        ], [
            ("P1", "1", "10", "receipt", "R1"),
            ("P1", "2", "10", "receipt", "R2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P1", "2", "10", "5")))
        for item in self.report(engine.procure_guard(*paths, self.folder)[0]):
            self.assertNotIn("invoice_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_invoice_source_rows"], "")

    def test_r472_distinct_invoice_ids_across_pos_not_cross_po(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P2", "1", "10", "5", "invoice", "INV2", ""),
        ], [
            ("P1", "1", "10", "receipt", "R1"),
            ("P2", "1", "10", "receipt", "R2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        for item in self.report(engine.procure_guard(*paths, self.folder)[0]):
            self.assertNotIn("invoice_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_invoice_source_rows"], "")

    def test_r472_blank_invoice_ids_do_not_create_duplicate_identity(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "", ""),
            ("P2", "1", "10", "5", "invoice", "", ""),
        ], [
            ("P1", "1", "10", "receipt", "R1"),
            ("P2", "1", "10", "receipt", "R2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        for item in self.report(engine.procure_guard(*paths, self.folder)[0]):
            self.assertNotIn("invoice_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_invoice_source_rows"], "")

    def test_r472_invoice_and_credit_ids_are_separate_document_types(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "SAME1", ""),
            ("P2", "1", "10", "5", "invoice", "INV2", ""),
            ("P2", "1", "1", "5", "credit", "SAME1", "INV2"),
        ], [
            ("P1", "1", "10", "receipt", "R1"),
            ("P2", "1", "9", "receipt", "R2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        for item in self.report(engine.procure_guard(*paths, self.folder)[0]):
            self.assertNotIn("invoice_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_invoice_source_rows"], "")


    def test_r473_normalized_receipt_document_reuse_across_pos_cites_rows(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P2", "1", "10", "5", "invoice", "INV2", ""),
        ], [
            ("P1", "1", "10", "receipt", "R-C1"),
            ("P2", "1", "10", "receipt", "RC1"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        outputs = engine.procure_guard(*paths, self.folder)
        rows = self.report(outputs[0])
        self.assertEqual([row["po"] for row in rows], ["P1", "P2"])
        for item in rows:
            self.assertIn("receipt_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_receipt_source_rows"], "2;3")
            self.assertEqual(item["cross_po_return_source_rows"], "")
            self.assertEqual(item["received_qty"], "10")
            self.assertEqual(item["invoice_total_exact"], "50")
            self.assertEqual(len(item["receipt_source_sha256"]), 64)
        self.assertIn("SHA-256", outputs[1].read_text())

    def test_r473_normalized_return_document_reuse_across_pos_cites_rows(self):
        paths = self.inputs([
            ("P1", "1", "9", "5", "invoice", "INV1", ""),
            ("P2", "1", "9", "5", "invoice", "INV2", ""),
        ], [
            ("P1", "1", "10", "receipt", "RC1"),
            ("P1", "1", "1", "return", "R-T1"),
            ("P2", "1", "10", "receipt", "RC2"),
            ("P2", "1", "1", "return", "RT1"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        outputs = engine.procure_guard(*paths, self.folder)
        rows = self.report(outputs[0])
        for item in rows:
            self.assertIn("return_document_cross_po_review", item["status"])
            self.assertIn("return_review", item["status"])
            self.assertEqual(item["cross_po_return_source_rows"], "3;5")
            self.assertEqual(item["cross_po_receipt_source_rows"], "")
            self.assertEqual(item["returned_qty"], "1")
            self.assertEqual(item["received_qty"], "9")
            self.assertEqual(item["invoice_total_exact"], "45")
        self.assertIn("SHA-256", outputs[1].read_text())

    def test_r473_receipt_same_po_multiple_lines_not_cross_po(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "2", "10", "5", "invoice", "INV2", ""),
        ], [
            ("P1", "1", "10", "receipt", "RC1"),
            ("P1", "2", "10", "receipt", "RC1"),
        ], po_rows=(("P1", "1", "10", "5"), ("P1", "2", "10", "5")))
        for item in self.report(engine.procure_guard(*paths, self.folder)[0]):
            self.assertNotIn("receipt_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_receipt_source_rows"], "")

    def test_r473_return_same_po_multiple_lines_not_cross_po(self):
        paths = self.inputs([
            ("P1", "1", "9", "5", "invoice", "INV1", ""),
            ("P1", "2", "9", "5", "invoice", "INV2", ""),
        ], [
            ("P1", "1", "10", "receipt", "RC1"),
            ("P1", "1", "1", "return", "RT1"),
            ("P1", "2", "10", "receipt", "RC2"),
            ("P1", "2", "1", "return", "RT1"),
        ], po_rows=(("P1", "1", "10", "5"), ("P1", "2", "10", "5")))
        for item in self.report(engine.procure_guard(*paths, self.folder)[0]):
            self.assertNotIn("return_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_return_source_rows"], "")

    def test_r473_distinct_receipt_and_return_documents_do_not_collide(self):
        paths = self.inputs([
            ("P1", "1", "9", "5", "invoice", "INV1", ""),
            ("P2", "1", "9", "5", "invoice", "INV2", ""),
        ], [
            ("P1", "1", "10", "receipt", "RC1"),
            ("P1", "1", "1", "return", "RT1"),
            ("P2", "1", "10", "receipt", "RC2"),
            ("P2", "1", "1", "return", "RT2"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        for item in self.report(engine.procure_guard(*paths, self.folder)[0]):
            self.assertNotIn("receipt_document_cross_po_review", item["status"])
            self.assertNotIn("return_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_receipt_source_rows"], "")
            self.assertEqual(item["cross_po_return_source_rows"], "")

    def test_r473_blank_receipt_ids_are_not_shared_document_evidence(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P2", "1", "10", "5", "invoice", "INV2", ""),
        ], [
            ("P1", "1", "10", "receipt", ""),
            ("P2", "1", "10", "receipt", ""),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        for item in self.report(engine.procure_guard(*paths, self.folder)[0]):
            self.assertNotIn("receipt_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_receipt_source_rows"], "")

    def test_r473_receipt_and_return_id_namespaces_are_separate(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P2", "1", "9", "5", "invoice", "INV2", ""),
        ], [
            ("P1", "1", "10", "receipt", "SAME1"),
            ("P2", "1", "10", "receipt", "RC2"),
            ("P2", "1", "1", "return", "SAME1"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        for item in self.report(engine.procure_guard(*paths, self.folder)[0]):
            self.assertNotIn("receipt_document_cross_po_review", item["status"])
            self.assertNotIn("return_document_cross_po_review", item["status"])

    def test_r473_invoice_and_receipt_reuse_are_independent_custody(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "I-NV1", ""),
            ("P2", "1", "10", "5", "invoice", "INV1", ""),
        ], [
            ("P1", "1", "10", "receipt", "R-C1"),
            ("P2", "1", "10", "receipt", "RC1"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        rows = self.report(engine.procure_guard(*paths, self.folder)[0])
        for item in rows:
            self.assertIn("invoice_document_cross_po_review", item["status"])
            self.assertIn("receipt_document_cross_po_review", item["status"])
            self.assertEqual(item["cross_po_invoice_source_rows"], "2;3")
            self.assertEqual(item["cross_po_receipt_source_rows"], "2;3")
            self.assertEqual(item["cross_po_return_source_rows"], "")


    def test_r474_all_four_typed_cross_po_reviews_preserve_decimal_custody(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "I-A", ""),
            ("P1", "1", "1", "5", "credit", "C-A", "I-A"),
            ("P2", "1", "10", "5", "invoice", "IA", ""),
            ("P2", "1", "1", "5", "credit", "CA", "IA"),
        ], [
            ("P1", "1", "10", "receipt", "R-A"),
            ("P1", "1", "1", "return", "T-A"),
            ("P2", "1", "10", "receipt", "RA"),
            ("P2", "1", "1", "return", "TA"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        outputs = engine.procure_guard(*paths, self.folder)
        for item in self.report(outputs[0]):
            for flag in ("invoice_document_cross_po_review",
                         "credit_document_cross_po_review",
                         "receipt_document_cross_po_review",
                         "return_document_cross_po_review"):
                self.assertIn(flag, item["status"])
            self.assertEqual(item["cross_po_invoice_source_rows"], "2;4")
            self.assertEqual(item["cross_po_credit_source_rows"], "3;5")
            self.assertEqual(item["cross_po_receipt_source_rows"], "2;4")
            self.assertEqual(item["cross_po_return_source_rows"], "3;5")
            self.assertEqual(item["invoiced_qty"], "9")
            self.assertEqual(item["received_qty"], "9")
            self.assertEqual(item["invoice_total_exact"], "45")
            for column in ("po_source_sha256", "invoice_source_sha256",
                           "receipt_source_sha256"):
                self.assertEqual(len(item[column]), 64)
        self.assertIn("SHA-256", outputs[1].read_text())

    def test_r474_same_id_across_different_event_types_is_not_cross_po(self):
        paths = self.inputs([
            ("P1", "1", "10", "5", "invoice", "SAME1", ""),
            ("P2", "1", "10", "5", "invoice", "INV2", ""),
            ("P2", "1", "1", "5", "credit", "SAME1", "INV2"),
        ], [
            ("P1", "1", "10", "receipt", "SAME1"),
            ("P2", "1", "10", "receipt", "RC2"),
            ("P2", "1", "1", "return", "SAME1"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5")))
        for item in self.report(engine.procure_guard(*paths, self.folder)[0]):
            for kind in ("invoice", "credit", "receipt", "return"):
                self.assertNotIn(kind + "_document_cross_po_review", item["status"])
                self.assertEqual(item["cross_po_" + kind + "_source_rows"], "")

    def test_r474_multi_document_cross_po_citations_not_cross_contaminated(self):
        paths = self.inputs([
            ("P1", "1", "5", "5", "invoice", "A-A", ""),
            ("P1", "1", "5", "5", "invoice", "B-B", ""),
            ("P2", "1", "10", "5", "invoice", "AA", ""),
            ("P3", "1", "10", "5", "invoice", "BB", ""),
        ], [
            ("P1", "1", "10", "receipt", "RC1"),
            ("P2", "1", "10", "receipt", "RC2"),
            ("P3", "1", "10", "receipt", "RC3"),
        ], po_rows=(("P1", "1", "10", "5"), ("P2", "1", "10", "5"),
                    ("P3", "1", "10", "5")))
        rows = {r["po"]: r for r in self.report(engine.procure_guard(*paths, self.folder)[0])}
        self.assertEqual(rows["P1"]["cross_po_invoice_source_rows"], "2;3;4;5")
        self.assertEqual(rows["P2"]["cross_po_invoice_source_rows"], "2;4")
        self.assertEqual(rows["P3"]["cross_po_invoice_source_rows"], "3;5")
        for item in rows.values():
            self.assertEqual(item["cross_po_credit_source_rows"], "")
            self.assertIn("invoice_document_cross_po_review", item["status"])
            self.assertEqual(item["invoice_total_exact"], "50")

    def test_r474_single_pass_classifier_call_count_and_legacy_parity(self):
        from fvs_suite.procurement_cross_po_r471 import (
            cross_po_all_document_source_rows, cross_po_invoice_source_rows,
            cross_po_credit_source_rows, cross_po_receipt_source_rows,
            cross_po_return_source_rows,
        )
        invoices = {
            ("P1", "1"): [
                {"row": "2", "event_type": "invoice", "document_id": "I-A"},
                {"row": "3", "event_type": "credit", "document_id": "C-A"},
            ],
            ("P2", "1"): [
                {"row": "4", "event_type": "invoice", "document_id": "IA"},
                {"row": "5", "event_type": "credit", "document_id": "CA"},
            ],
        }
        receipts = {
            ("P1", "1"): [
                {"row": "2", "event_type": "receipt", "document_id": "R-A"},
                {"row": "3", "event_type": "return", "document_id": "T-A"},
            ],
            ("P2", "1"): [
                {"row": "4", "event_type": "receipt", "document_id": "RA"},
                {"row": "5", "event_type": "return", "document_id": "TA"},
            ],
        }
        counts = {"invoice": 0, "receipt": 0}

        def key(value):
            return value.replace("-", "")

        def invoice_kind(row):
            counts["invoice"] += 1
            return row["event_type"]

        def receipt_kind(row):
            counts["receipt"] += 1
            return row["event_type"]

        all_refs = cross_po_all_document_source_rows(
            invoices, receipts, document_key=key,
            invoice_event_type=invoice_kind, receipt_event_type=receipt_kind)
        self.assertEqual(counts, {"invoice": 4, "receipt": 4})
        for kind, wrapper, groups in (
            ("invoice", cross_po_invoice_source_rows, invoices),
            ("credit", cross_po_credit_source_rows, invoices),
            ("receipt", cross_po_receipt_source_rows, receipts),
            ("return", cross_po_return_source_rows, receipts),
        ):
            self.assertEqual(all_refs[kind], wrapper(
                groups, document_key=key, event_type=lambda row: row["event_type"]))

    def test_r474_index_evidence_invariant_under_input_order(self):
        from fvs_suite.procurement_cross_po_r471 import cross_po_all_document_source_rows
        invoices = {
            ("P2", "2"): [
                {"row": "12", "event_type": "invoice", "document_id": "I1"},
                {"row": "8", "event_type": "credit", "document_id": "CM1"},
            ],
            ("P1", "1"): [
                {"row": "3", "event_type": "credit", "document_id": "CM1"},
                {"row": "2", "event_type": "invoice", "document_id": "I1"},
            ],
        }
        receipts = {
            ("P2", "2"): [{"row": "13", "event_type": "receipt", "document_id": "RC1"}],
            ("P1", "1"): [{"row": "4", "event_type": "receipt", "document_id": "RC1"}],
        }
        keyword = {
            "document_key": lambda value: value,
            "invoice_event_type": lambda row: row["event_type"],
            "receipt_event_type": lambda row: row["event_type"],
        }
        normal = cross_po_all_document_source_rows(invoices, receipts, **keyword)
        reverse = lambda groups: {
            key: list(reversed(rows)) for key, rows in reversed(list(groups.items()))
        }
        changed = cross_po_all_document_source_rows(
            reverse(invoices), reverse(receipts), **keyword)
        self.assertEqual(normal, changed)
        self.assertEqual(normal["invoice"][("P1", "1")], ("2", "12"))
        self.assertEqual(normal["credit"][("P2", "2")], ("3", "8"))


    def test_r475_cross_order_fanout_fails_before_csv_publication(self):
        # One valid 1,001-row source can imply >1,000,000 repeated citations.
        # Reject the entire review instead of emitting truncated audit evidence.
        po_rows = [(f"PO{i:04d}", "1", "1", "5") for i in range(1001)]
        invoices = [(po, line, qty, price, "invoice", "PRIVATE_INVOICE", "")
                    for po, line, qty, price in po_rows]
        receipts = [(po, line, qty, "receipt", f"RC{i:04d}")
                    for i, (po, line, qty, _) in enumerate(po_rows)]
        paths = self.inputs(invoices, receipts, po_rows=po_rows)
        with self.assertRaisesRegex(ValueError, "exceeds citation budget") as error:
            engine.procure_guard(*paths, self.folder)
        self.assertNotIn("PRIVATE_INVOICE", str(error.exception))
        self.assertFalse(list(self.folder.glob("procurement-three-way*")))


if __name__ == "__main__":
    unittest.main()
