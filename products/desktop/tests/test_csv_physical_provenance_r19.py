"""R19: source CSV physical-line provenance and strict structural parsing.

These are repository integration tests; separate from the 12 local isolated
parser checks. All input remains local; none of these outcomes approves a
payment, reimbursement, or compliance decision.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine


class CsvPhysicalProvenanceR19Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-csv-provenance-r19-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def write(self, name, headings, records):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headings)
            writer.writerows(records)
        return path

    @staticmethod
    def read(path):
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_multiline_and_blank_records_return_physical_start_lines(self):
        path = self.write(
            "input.csv", ("id", "amount", "notes"),
            (("A", "10", "first line\nsecond line"), (), ("B", "20", "ok")),
        )
        records = engine.table(path, ("id", "amount"))
        self.assertEqual([(r["id"], r["row"]) for r in records], [("A", "2"), ("B", "5")])

    def test_multiline_header_advances_first_source_row(self):
        path = self.write(
            "input.csv", ("id", "amount", "notes\nmetadata"), (("A", "10", "ok"),),
        )
        self.assertEqual(engine.table(path, ("id", "amount"))[0]["row"], "3")

    def test_empty_lines_are_skipped_not_misreported(self):
        path = self.write(
            "input.csv", ("id", "amount"), ((), (), ("A", "10"), (), ("B", "20")),
        )
        self.assertEqual(
            [r["row"] for r in engine.table(path, ("id", "amount"))], ["4", "6"]
        )

    def test_ledger_diff_source_references_survive_multiline_records(self):
        left = self.write(
            "left.csv", ("id", "amount", "notes"),
            (("A", "10", "first\nsecond"), (), ("B", "20", "ordinary")),
        )
        right = self.write(
            "right.csv", ("id", "amount"), (("A", "10"), ("B", "20")),
        )
        report = {r["id"]: r for r in self.read(engine.ledger_diff(left, right, self.root)[0])}
        self.assertEqual((report["A"]["left_rows"], report["B"]["left_rows"]), ("2", "5"))
        self.assertEqual((report["A"]["right_rows"], report["B"]["right_rows"]), ("2", "3"))
        self.assertEqual((report["A"]["status"], report["B"]["status"]), ("matched", "matched"))

    def test_invoice_twins_cites_physical_source_lines(self):
        source = self.write(
            "invoices.csv", ("vendor", "invoice_number", "amount", "date", "notes"),
            (
                ("ACME", "INV-7", "10", "2026-01-01", "part A\npart B"),
                (),
                ("Acme", "INV7", "10", "2026-01-02", "ok"),
            ),
        )
        report = self.read(engine.invoice_twins(source, self.root)[0])
        exact = [r for r in report if r["status"] == "exact_invoice_key"]
        self.assertEqual(len(exact), 1)
        self.assertEqual((exact[0]["row_a"], exact[0]["row_b"]), ("2", "5"))

    def test_grant_audit_cites_source_claim_physical_lines(self):
        claims = self.write(
            "claims.csv", ("id", "amount", "program", "notes"),
            (("C0", "1", "G1", "first\nsecond"), (), ("C1", "10", "G1", "ok")),
        )
        ledger = self.write(
            "ledger.csv", ("id", "amount", "program"),
            (("C0", "1", "G1"), ("C1", "10", "G1")),
        )
        budgets = self.write("budgets.csv", ("program", "budget"), (("G1", "100"),))
        report = {
            r["id"]: r for r in self.read(engine.grant_audit(claims, ledger, budgets, self.root)[0])
        }
        self.assertEqual((report["C0"]["claim_rows"], report["C1"]["claim_rows"]), ("2", "5"))
        self.assertEqual(report["C1"]["ledger_rows"], "3")

    def test_procurement_invoice_provenance_handles_embedded_newline(self):
        orders = self.write(
            "po.csv", ("po_number", "line", "quantity", "unit_price"),
            (("P1", "1", "1", "5"), ("P2", "1", "1", "5")),
        )
        invoices = self.write(
            "invoices.csv", ("po_number", "line", "quantity", "unit_price", "notes"),
            (("P1", "1", "1", "5", "first\nsecond"), (), ("P2", "1", "1", "5", "ok")),
        )
        receipts = self.write(
            "receipts.csv", ("po_number", "line", "quantity"),
            (("P1", "1", "1"), ("P2", "1", "1")),
        )
        report = {
            r["po"]: r for r in self.read(engine.procure_guard(orders, invoices, receipts, self.root)[0])
        }
        self.assertEqual((report["P1"]["invoice_rows"], report["P2"]["invoice_rows"]), ("2", "5"))

    def test_truncated_row_rejected_instead_of_silent_optional_blank(self):
        source = self.write(
            "spend.csv", ("vendor", "amount", "date", "category"),
            (("ACME", "10", "2026-01-01"),),
        )
        with self.assertRaisesRegex(ValueError, "malformed CSV record at physical line 2"):
            engine.spend_map(source, self.root)
        self.assertEqual(list(self.root.glob("spend-map-*.csv")), [])

    def test_excess_columns_rejected_before_ledger_output(self):
        left = self.write("left.csv", ("id", "amount"), (("A", "10", "unexpected"),))
        right = self.write("right.csv", ("id", "amount"), (("A", "10"),))
        with self.assertRaisesRegex(ValueError, "expected 2 columns, got 3"):
            engine.ledger_diff(left, right, self.root)
        self.assertEqual(list(self.root.glob("ledger-diff-*.csv")), [])

    def test_unterminated_quoted_record_rejected_before_output(self):
        source = self.root / "invoices.csv"
        source.write_text(
            'vendor,invoice_number,amount,date\nACME,INV1,10,"2026-01-01',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "invalid CSV near physical line"):
            engine.invoice_twins(source, self.root)
        self.assertEqual(list(self.root.glob("invoice-twins-*.csv")), [])

    def test_bom_and_alias_parsing_still_supported(self):
        source = self.root / "data.csv"
        source.write_text(
            "\ufefftransaction_id,paid\nA,10\n", encoding="utf-8"
        )
        rows = engine.table(source, ("id", "amount"))
        self.assertEqual(rows, [{"row": "2", "id": "A", "amount": "10"}])

    def test_duplicate_normalized_header_still_rejected(self):
        source = self.write("invoices.csv", ("id", "amount", "Amount"), (("A", "1", "2"),))
        with self.assertRaisesRegex(ValueError, "duplicate normalized CSV header"):
            engine.table(source, ("id", "amount"))


if __name__ == "__main__":
    unittest.main()
