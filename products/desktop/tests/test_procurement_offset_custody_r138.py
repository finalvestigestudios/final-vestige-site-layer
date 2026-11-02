"""R138 synthetic real-CSV ProcureGuard custody and offset candidate regressions."""
from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from decimal import Context, localcontext
from pathlib import Path
from unittest.mock import patch
from fvs_suite import engine

PO = ("P1", "1", "10", "5")
INV = ("P1", "1", "10", "5", "invoice", "INV1", "")
REC = ("P1", "1", "10", "receipt", "RC1", "")
PH = ("po_number", "line", "quantity", "unit_price")
IH = PH + ("event_type", "document_id", "related_document")
RH = ("po_number", "line", "quantity", "event_type", "document_id", "related_document")


class ProcureOffsetCustodyR138Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="fvs-procure-r138-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.dest = self.root / "out"
        self.dest.mkdir()
        self.sources = self.make_sources()

    def csv(self, name, headers, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)
        return path

    def make_sources(self, *, po=None, invoices=None, receipts=None):
        return (
            self.csv("po.csv", PH, [PO] if po is None else po),
            self.csv("invoices.csv", IH, [INV] if invoices is None else invoices),
            self.csv("receipts.csv", RH, [REC] if receipts is None else receipts),
        )

    def report(self, *, policy=None):
        outputs = engine.procure_guard(
            *(str(path) for path in self.sources), self.dest,
            policy_path=None if policy is None else str(policy))
        self.assertEqual(len(outputs), 2)
        self.assertEqual(outputs[0].parent, outputs[1].parent)
        with outputs[0].open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        return rows, outputs

    def links(self, row, key):
        return json.loads(row[key])

    def assert_digests(self, row):
        for field, path in zip(
            ("po_source_sha256", "invoice_source_sha256", "receipt_source_sha256"),
            self.sources,
        ):
            self.assertEqual(row[field], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_source_digest_columns_bind_all_three_parsed_inputs(self):
        rows, _ = self.report()
        self.assertEqual(len(rows), 1)
        self.assert_digests(rows[0])

    def test_source_digest_columns_match_published_manifest(self):
        rows, files = self.report()
        inventory = files[1].read_text(encoding="utf-8")
        for field, path in zip(
            ("po_source_sha256", "invoice_source_sha256", "receipt_source_sha256"),
            self.sources,
        ):
            self.assertIn(path.name + "\t" + rows[0][field] + "\n", inventory)

    def test_no_offsets_explicitly_report_empty_candidate_arrays(self):
        rows, _ = self.report()
        self.assertEqual(rows[0]["status"], "matched")
        self.assertEqual(self.links(rows[0], "credit_source_line_links"), [])
        self.assertEqual(self.links(rows[0], "return_source_line_links"), [])

    def test_credit_links_back_to_invoice_source_line(self):
        self.sources = self.make_sources(invoices=[
            INV, ("P1", "1", "2", "5", "credit", "CM1", "INV1")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "credit_source_line_links"),
                         [{"offset_row": "3", "target_rows": ["2"]}])
        self.assertIn("credit_memo_review", rows[0]["status"])

    def test_return_links_back_to_receipt_source_line(self):
        self.sources = self.make_sources(receipts=[
            REC, ("P1", "1", "2", "return", "RT1", "RC1")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "return_source_line_links"),
                         [{"offset_row": "3", "target_rows": ["2"]}])
        self.assertIn("return_review", rows[0]["status"])

    def test_both_types_are_separately_traceable_without_money_changes(self):
        self.sources = self.make_sources(
            invoices=[INV, ("P1", "1", "2", "5", "credit", "CM1", "INV1")],
            receipts=[REC, ("P1", "1", "2", "return", "RT1", "RC1")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "credit_source_line_links")[0]["target_rows"], ["2"])
        self.assertEqual(self.links(rows[0], "return_source_line_links")[0]["target_rows"], ["2"])
        self.assertEqual(rows[0]["invoice_total_exact"], "40")

    def test_multiple_credit_events_preserve_source_order(self):
        self.sources = self.make_sources(invoices=[
            INV, ("P1", "1", "1", "5", "credit", "CM1", "INV1"),
            ("P1", "1", "1", "5", "credit", "CM2", "INV1")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "credit_source_line_links"),
                         [{"offset_row": "3", "target_rows": ["2"]},
                          {"offset_row": "4", "target_rows": ["2"]}])

    def test_duplicate_invoice_ids_keep_all_candidates_and_review_flag(self):
        self.sources = self.make_sources(invoices=[
            INV, ("P1", "1", "10", "5", "invoice", "INV1", ""),
            ("P1", "1", "1", "5", "credit", "CM1", "INV1")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "credit_source_line_links"),
                         [{"offset_row": "4", "target_rows": ["2", "3"]}])
        self.assertIn("repeated_invoice_document_id_review", rows[0]["status"])

    def test_duplicate_receipt_ids_keep_all_candidates_and_review_flag(self):
        self.sources = self.make_sources(receipts=[
            REC, ("P1", "1", "10", "receipt", "RC1", ""),
            ("P1", "1", "1", "return", "RT1", "RC1")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "return_source_line_links"),
                         [{"offset_row": "4", "target_rows": ["2", "3"]}])
        self.assertIn("repeated_receipt_document_id_review", rows[0]["status"])

    def test_unlinked_credit_has_no_invented_target(self):
        self.sources = self.make_sources(invoices=[
            INV, ("P1", "1", "1", "5", "credit", "CM1", "MISSING")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "credit_source_line_links"),
                         [{"offset_row": "3", "target_rows": []}])
        self.assertIn("unlinked_credit_review", rows[0]["status"])

    def test_unlinked_return_has_no_invented_target(self):
        self.sources = self.make_sources(receipts=[
            REC, ("P1", "1", "1", "return", "RT1", "MISSING")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "return_source_line_links"),
                         [{"offset_row": "3", "target_rows": []}])
        self.assertIn("unlinked_return_review", rows[0]["status"])

    def test_normalized_credit_link_still_flags_review(self):
        self.sources = self.make_sources(invoices=[
            ("P1", "1", "10", "5", "invoice", "INV-1", ""),
            ("P1", "1", "1", "5", "credit", "CM1", "INV1")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "credit_source_line_links")[0]["target_rows"], ["2"])
        self.assertIn("normalized_credit_link_review", rows[0]["status"])

    def test_normalized_return_link_still_flags_review(self):
        self.sources = self.make_sources(receipts=[
            ("P1", "1", "10", "receipt", "RC-1", ""),
            ("P1", "1", "1", "return", "RT1", "RC1")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "return_source_line_links")[0]["target_rows"], ["2"])
        self.assertIn("normalized_return_link_review", rows[0]["status"])

    def test_bom_and_quoted_newline_keep_original_invoice_lines(self):
        self.sources = self.make_sources(invoices=[
            ("P1", "1", "10", "5", "invoice", "INV\n1", ""),
            ("P1", "1", "1", "5", "credit", "CM1", "INV\n1")])
        source = self.sources[1]
        source.write_bytes(b"\xef\xbb\xbf" + source.read_bytes())
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "credit_source_line_links"),
                         [{"offset_row": "4", "target_rows": ["2"]}])
        self.assertEqual(rows[0]["invoice_rows"], "2;4")
        self.assert_digests(rows[0])

    def test_quoted_newline_keeps_original_receipt_lines(self):
        self.sources = self.make_sources(receipts=[
            ("P1", "1", "10", "receipt", "RC\n1", ""),
            ("P1", "1", "1", "return", "RT1", "RC\n1")])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "return_source_line_links"),
                         [{"offset_row": "4", "target_rows": ["2"]}])
        self.assertEqual(rows[0]["receipt_rows"], "2;4")

    def test_absent_invoice_and_receipt_remain_source_bound(self):
        self.sources = self.make_sources(invoices=[], receipts=[])
        rows, _ = self.report()
        self.assertEqual(self.links(rows[0], "credit_source_line_links"), [])
        self.assertEqual(self.links(rows[0], "return_source_line_links"), [])
        self.assertIn("missing_invoice", rows[0]["status"])
        self.assertIn("missing_receipt", rows[0]["status"])
        self.assert_digests(rows[0])

    def test_custom_price_policy_retains_all_original_fingerprints(self):
        policy = self.root / "rules.json"
        policy.write_text('{"version":1,"price_absolute":"0.01","price_fraction":"0.02"}',
                          encoding="utf-8")
        rows, files = self.report(policy=policy)
        self.assert_digests(rows[0])
        policy_digest = hashlib.sha256(policy.read_bytes()).hexdigest()
        self.assertEqual(rows[0]["price_policy_sha256"], policy_digest)
        self.assertIn(policy_digest, files[1].read_text(encoding="utf-8"))

    def test_repeat_exports_are_byte_identical_and_originals_unchanged(self):
        originals = [p.read_bytes() for p in self.sources]
        _, first = self.report()
        _, second = self.report()
        self.assertNotEqual(first[0], second[0])
        self.assertEqual(first[0].read_bytes(), second[0].read_bytes())
        self.assertEqual(originals, [p.read_bytes() for p in self.sources])

    def test_mutation_after_parse_aborts_without_partial_evidence(self):
        original = engine.manifest
        def mutate(*args, **kwargs):
            source = self.sources[1]
            source.write_bytes(source.read_bytes().replace(b"10,5", b"11,5"))
            return original(*args, **kwargs)
        with patch("fvs_suite.engine.manifest", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "Source bytes changed"):
                self.report()
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_negative_credit_quantity_cannot_publish_evidence(self):
        self.sources = self.make_sources(invoices=[
            ("P1", "1", "-1", "5", "credit", "CM1", "INV1")])
        with self.assertRaises(ValueError):
            self.report()
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_low_caller_decimal_precision_preserves_exact_totals(self):
        self.sources = self.make_sources(
            po=[("P1", "1", "2", "9999999999.99")],
            invoices=[("P1", "1", "2", "9999999999.99", "invoice", "INV1", "")],
            receipts=[("P1", "1", "2", "receipt", "RC1", "")])
        with localcontext(Context(prec=4)):
            rows, _ = self.report()
        self.assertEqual(rows[0]["invoice_total_exact"], "19999999999.98")
        self.assert_digests(rows[0])

    def test_links_cannot_cross_purchase_orders(self):
        self.sources = self.make_sources(
            po=[("P1", "1", "1", "5"), ("P2", "1", "1", "5")],
            invoices=[("P1", "1", "1", "5", "invoice", "INV1", ""),
                      ("P2", "1", "1", "5", "credit", "CM2", "INV1")],
            receipts=[("P1", "1", "1", "receipt", "RC1", ""),
                      ("P2", "1", "1", "receipt", "RC2", "")])
        rows, _ = self.report()
        self.assertEqual([r["po"] for r in rows], ["P1", "P2"])
        self.assertEqual(self.links(rows[1], "credit_source_line_links"),
                         [{"offset_row": "3", "target_rows": []}])
        self.assertIn("unlinked_credit_review", rows[1]["status"])


if __name__ == "__main__":
    unittest.main()
