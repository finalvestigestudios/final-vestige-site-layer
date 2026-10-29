"""R25: bounded local financial CSV intake and fail-closed NUL/UTF-8 handling.

Synthetic fixtures only. No test authorizes payments or grants.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fvs_suite import engine


class CsvImportBoundsR25(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-import-bounds-r25-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def csvfile(self, name, headings, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as output:
            writer = csv.writer(output)
            writer.writerow(headings)
            writer.writerows(rows)
        return path

    def no_report(self, stem):
        self.assertEqual(list(self.root.glob(stem + "-*.csv")), [])
        self.assertEqual(list(self.root.glob("evidence-manifest-*.txt")), [])

    def test_standard_bom_and_quoted_multiline_rows_keep_physical_citation(self):
        path = self.root / "ordinary.csv"
        path.write_text("\ufeffid,amount,notes\nA,10,\"one\ntwo\"\n", encoding="utf-8")
        records = engine.table(path, ("id", "amount"))
        self.assertEqual(records, [{"row": "2", "id": "A", "amount": "10"}])

    def test_unused_non_nul_column_remains_accepted(self):
        path = self.csvfile("ordinary.csv", ("id", "amount", "notes"),
                            (("A", "10", "free-form narrative"),))
        self.assertEqual(engine.table(path, ("id", "amount"))[0]["id"], "A")

    def test_multilingual_non_nul_text_is_not_erased(self):
        path = self.csvfile("ordinary.csv", ("vendor", "amount"),
                            (("Café 東京", "10.00"),))
        self.assertEqual(engine.table(path, ("vendor", "amount"))[0]["vendor"],
                         "Café 東京")

    def test_nul_header_rejected_before_column_resolution(self):
        path = self.csvfile("bad.csv", ("id", "am\x00ount"), (("A", "10"),))
        with self.assertRaisesRegex(ValueError, "header contains a NUL"):
            engine.table(path, ("id", "amount"))

    def test_nul_in_unused_column_still_rejects_whole_file(self):
        secret = "PRIVATE_INVOICE_NOTE"
        path = self.csvfile("bad.csv", ("id", "amount", "notes"),
                            (("A", "10", secret + "\x00suffix"),))
        source_bytes = path.read_bytes()
        with self.assertRaises(ValueError) as caught:
            engine.table(path, ("id", "amount"))
        self.assertIn("NUL character", str(caught.exception))
        self.assertNotIn(secret, str(caught.exception))
        self.assertEqual(path.read_bytes(), source_bytes)

    def test_nul_in_required_amount_rejected(self):
        path = self.csvfile("bad.csv", ("id", "amount"), (("A", "1\x00.00"),))
        with self.assertRaisesRegex(ValueError, "NUL character"):
            engine.table(path, ("id", "amount"))

    def test_sized_file_rejected_before_parsing_even_if_sparse(self):
        path = self.root / "large.csv"
        with path.open("wb") as output:
            output.write(b"id,amount\n")
            output.truncate(engine.MAX_IMPORT_BYTES + 1)
        with self.assertRaisesRegex(ValueError, "64 MiB file-size limit"):
            engine.table(path, ("id", "amount"))

    def test_exact_byte_boundary_is_accepted_and_one_less_rejected(self):
        path = self.root / "boundary.csv"
        path.write_bytes(b"id,amount\nA,10\n")
        byte_count = path.stat().st_size
        with patch.object(engine, "MAX_IMPORT_BYTES", byte_count):
            self.assertEqual(engine.table(path, ("id", "amount"))[0]["id"], "A")
        with patch.object(engine, "MAX_IMPORT_BYTES", byte_count - 1):
            with self.assertRaisesRegex(ValueError, "file-size limit"):
                engine.table(path, ("id", "amount"))

    def test_invalid_utf8_in_header_reports_generic_error(self):
        path = self.root / "bad.csv"
        path.write_bytes(b"id,am\xffount\nA,1\n")
        with self.assertRaisesRegex(ValueError, "invalid CSV header"):
            engine.table(path, ("id", "amount"))

    def test_invalid_utf8_in_row_reports_generic_error(self):
        path = self.root / "bad.csv"
        path.write_bytes(b"id,amount\nA,\xff\n")
        # TextIOWrapper may decode the entire small file while fetching the
        # header, so the safe error may be labeled header or record.
        with self.assertRaisesRegex(ValueError, "invalid CSV"):
            engine.table(path, ("id", "amount"))

    def test_ledger_diff_rejects_oversized_second_file_without_export(self):
        left = self.csvfile("left.csv", ("id", "amount"), (("A", "10"),))
        right = self.root / "right.csv"
        with right.open("wb") as output:
            output.write(b"id,amount\n")
            output.truncate(engine.MAX_IMPORT_BYTES + 1)
        with self.assertRaisesRegex(ValueError, "file-size limit"):
            engine.ledger_diff(left, right, self.root)
        self.no_report("ledger-diff")

    def test_invoice_twins_rejects_nul_in_unused_note_without_export(self):
        path = self.csvfile(
            "invoice.csv", ("vendor", "invoice_number", "amount", "date", "notes"),
            (("Vendor", "INV-1", "10", "2026-10-28", "notes\x00hidden"),))
        with self.assertRaisesRegex(ValueError, "NUL character"):
            engine.invoice_twins(path, self.root)
        self.no_report("invoice-twins")

    def test_spend_map_rejects_nul_in_category_without_export(self):
        path = self.csvfile("spend.csv", ("vendor", "amount", "date", "category"),
                            (("Vendor", "10", "2026-10-28", "office\x00hidden"),))
        with self.assertRaisesRegex(ValueError, "NUL character"):
            engine.spend_map(path, self.root)
        self.no_report("spend-map")

    def test_grant_audit_rejects_nul_in_unused_claim_note_without_export(self):
        claims = self.csvfile(
            "claims.csv", ("id", "amount", "program", "notes"),
            (("C1", "10", "G1", "x\x00y"),))
        ledger = self.csvfile("ledger.csv", ("id", "amount", "program"),
                              (("C1", "10", "G1"),))
        budgets = self.csvfile("budgets.csv", ("program", "budget"),
                               (("G1", "100"),))
        with self.assertRaisesRegex(ValueError, "NUL character"):
            engine.grant_audit(claims, ledger, budgets, self.root)
        self.no_report("grant-audit-exceptions")
        self.no_report("grant-budget-check")

    def test_procurement_rejects_nul_in_receipt_note_without_export(self):
        po = self.csvfile("po.csv", ("po_number", "line", "quantity", "unit_price"),
                          (("P1", "1", "1", "10"),))
        invoices = self.csvfile(
            "invoices.csv", ("po_number", "line", "quantity", "unit_price"),
            (("P1", "1", "1", "10"),))
        receipts = self.csvfile("receipts.csv",
                                ("po_number", "line", "quantity", "notes"),
                                (("P1", "1", "1", "x\x00y"),))
        with self.assertRaisesRegex(ValueError, "NUL character"):
            engine.procure_guard(po, invoices, receipts, self.root)
        self.no_report("procurement-three-way")


if __name__ == "__main__":
    unittest.main()
