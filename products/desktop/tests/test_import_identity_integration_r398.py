"""R398 real six-suite source-import integration (requires complete Git checkout).

Synthetic financial CSVs only. Checks visible review evidence and source-byte
immutability; does not approve any payment or release an executable.
"""
from __future__ import annotations

import csv
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from fvs_suite import engine


class OriginalCSVIdentityIntegrationR398(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r398-identity-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def source(self, name, headers, rows):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
        return path

    def read(self, path):
        with Path(path).open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_import_retains_original_id_and_program_spelling(self):
        path = self.source("identity.csv", ("id", "amount", "program"),
                           ((" C1 ", " 10.00 ", " G1 "),))
        before = path.read_bytes()
        records, digest = engine.table(path, ("id", "amount", "program"),
                                       include_digest=True)
        self.assertEqual(records[0]["id"], " C1 ")
        self.assertEqual(records[0]["program"], " G1 ")
        self.assertEqual(records[0]["amount"], "10.00")
        self.assertEqual(digest, sha256(before).hexdigest())
        self.assertEqual(path.read_bytes(), before)

    def test_import_does_not_trim_identifier_fields(self):
        for field in ("id", "program", "vendor", "invoice_number",
                      "po_number", "line", "document_id", "related_document",
                      "ledger_reference", "related_claim"):
            with self.subTest(field=field):
                self.assertEqual(engine._import_cell_text(field, " X "), " X ")

    def test_legacy_nonnumeric_cleanup_remains(self):
        for field in ("amount", "date", "category", "quantity",
                      "unit_price", "budget", "claim_type"):
            with self.subTest(field=field):
                self.assertEqual(engine._import_cell_text(field, " X "), "X")

    def test_ledger_marks_equal_amount_boundary_alias_as_review(self):
        a = self.source("ledger-left.csv", ("id", "amount"), ((" A-1", "5.00"),))
        b = self.source("ledger-right.csv", ("id", "amount"), (("A-1", "5.00"),))
        original = (a.read_bytes(), b.read_bytes())
        result = self.read(engine.ledger_diff(a, b, self.root)[0])[0]
        self.assertEqual(result["status"], "normalized_id_review")
        self.assertEqual(result["left_ids"], r"\u0020A-1")
        self.assertEqual(result["right_ids"], "A-1")
        self.assertEqual(result["difference"], "0.00")
        self.assertEqual((a.read_bytes(), b.read_bytes()), original)

    def test_grant_legacy_program_collision_remains_human_review(self):
        claim = self.source("grant-claim.csv", ("id", "amount", "program"), (("C1", "5", " G1"),))
        ledger = self.source("grant-ledger.csv", ("id", "amount", "program"), (("C1", "5", "G1"),))
        budget = self.source("grant-budget.csv", ("program", "budget"), (("G1", "100"),))
        results = engine.grant_audit(claim, ledger, budget, self.root)
        record = self.read(results[0])[0]
        self.assertEqual(record["status"], "normalized_program_review")
        self.assertEqual(record["claim_programs"], r"\u0020G1")
        self.assertEqual(record["ledger_programs"], "G1")
        summary = self.read(results[1])[0]
        self.assertIn("normalized_budget_program_review", summary["status"])

    def test_invoice_same_key_leading_space_has_explicit_review_flag(self):
        source = self.source("invoice.csv", ("vendor", "invoice_number", "amount", "date"), (
            (" ACME", " INV-1", "10.00", "2026-01-01"),
            ("ACME", "INV-1", "10.00", "2026-01-02"),
        ))
        items = self.read(engine.invoice_twins(source, self.root)[0])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["status"], "exact_invoice_key")
        self.assertIn("normalized_vendor_key_review", items[0]["review_flags"])
        self.assertIn("normalized_invoice_key_review", items[0]["review_flags"])

    def test_spend_source_variants_visible_in_report(self):
        source = self.source("spend.csv", ("vendor", "amount", "date", "category"), (
            (" ACME", "5", "2026-01-01", "Ops"),
            ("ACME", "5", "2026-01-02", "Ops"),
        ))
        rows = self.read(engine.spend_map(source, self.root)[0])
        self.assertEqual(len(rows), 1)
        self.assertIn("normalized_vendor_collision_review", rows[0]["flag"])
        self.assertIn("ACME", rows[0]["source_vendor_labels"])
        self.assertIn("10.00", rows[0]["amount"])

    def test_procurement_po_boundary_alias_is_not_auto_approved(self):
        po = self.source("po.csv", ("po_number", "line", "quantity", "unit_price"),
                         ((" PO-1", "1", "2", "5"),))
        invoice = self.source("pi.csv", ("po_number", "line", "quantity", "unit_price"),
                              (("PO-1", "1", "2", "5"),))
        receipt = self.source("receipt.csv", ("po_number", "line", "quantity"),
                              (("PO-1", "1", "2"),))
        rows = self.read(engine.procure_guard(po, invoice, receipt, self.root)[0])
        self.assertEqual(len(rows), 1)
        self.assertIn("normalized_po_key_review", rows[0]["status"])
        self.assertIn(r"\u0020PO-1", rows[0]["po_ids"])

    def test_source_whitespace_not_silently_accepted_as_identifier(self):
        left = self.source("blank.csv", ("id", "amount"), (("   ", "1"),))
        right = self.source("filled.csv", ("id", "amount"), (("A", "1"),))
        before = set(self.root.iterdir())
        with self.assertRaises(ValueError):
            engine.ledger_diff(left, right, self.root)
        self.assertEqual(set(self.root.iterdir()), before)

    def test_ordinary_matching_without_ambiguity_is_unchanged(self):
        a = self.source("normal-left.csv", ("id", "amount"), (("ACME", "5.00"),))
        b = self.source("normal-right.csv", ("id", "amount"), (("acme", "5.00"),))
        record = self.read(engine.ledger_diff(a, b, self.root)[0])[0]
        self.assertEqual(record["status"], "matched")


if __name__ == "__main__":
    unittest.main()
