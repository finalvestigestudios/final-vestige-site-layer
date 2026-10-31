"""R74 complete-checkout financial CSV/GUI-engine regressions; synthetic fixtures.

Run only with the real fvs_suite package, verified source CSV snapshot reader,
report writer and grant/procurement engines. This is intentionally not a mock.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from fvs_suite import engine


class UnicodeIdentityEngineR74(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-unicode-identity-r74-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def source(self, name, headers, records):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(records)
        return path

    @staticmethod
    def report(path):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_ledger_equal_money_but_unicode_identifier_requires_review(self):
        left = self.source("left.csv", ("id", "amount"), [("ſ1", "10.00")])
        right = self.source("right.csv", ("id", "amount"), [("S1", "10.00")])
        result = self.report(engine.ledger_diff(left, right, self.root)[0])[0]
        self.assertEqual(result["status"], "normalized_id_review")
        self.assertEqual(result["difference"], "0.00")
        self.assertEqual(result["left_rows"], "2")
        self.assertEqual(result["right_rows"], "2")
        self.assertEqual(result["left_ids"], "ſ1")
        self.assertEqual(result["right_ids"], "S1")

    def test_invoice_unicode_vendor_and_invoice_expansions_both_flagged(self):
        source = self.source("invoice.csv", ("vendor", "invoice_number", "amount", "date"),
                             [("ß", "ﬀ", "0.10", "2026-01-01"),
                              ("SS", "FF", "0.10", "2026-01-02")])
        result = self.report(engine.invoice_twins(source, self.root)[0])[0]
        self.assertEqual(result["status"], "exact_invoice_key")
        self.assertEqual(result["review_flags"],
                         "normalized_vendor_key_review;normalized_invoice_key_review")
        self.assertEqual(result["amount_a"], "0.10")
        self.assertEqual(result["amount_b"], "0.10")
        self.assertEqual((result["row_a"], result["row_b"]), ("2", "3"))

    def test_spend_unicode_vendor_aggregation_preserves_variant_count(self):
        source = self.source("spend.csv", ("vendor", "amount", "date", "category"),
                             [("ß", "1.10", "2026-01-01", "Office"),
                              ("SS", "2.20", "2026-01-02", "Office")])
        result = self.report(engine.spend_map(source, self.root)[0])[0]
        self.assertEqual(result["vendor_key"], "SS")
        self.assertEqual(result["amount"], "3.30")
        self.assertEqual(result["flag"], "normalized_vendor_collision_review")
        self.assertEqual(result["vendor_label_variants"], "2")
        self.assertEqual(result["source_rows"], "2;3")

    def test_grant_unicode_program_key_prevents_silent_match(self):
        claims = self.source("claims.csv", ("id", "amount", "program"),
                             [("C1", "10.00", "ſ1")])
        ledger = self.source("ledger.csv", ("id", "amount", "program"),
                             [("C1", "10.00", "S1")])
        budgets = self.source("budgets.csv", ("program", "budget"), [("S1", "100")])
        outputs = engine.grant_audit(claims, ledger, budgets, self.root)
        exception = self.report(outputs[0])[0]
        budget = self.report(outputs[1])[0]
        self.assertEqual(exception["status"], "normalized_program_review")
        self.assertEqual(exception["difference"], "0.00")
        self.assertIn("normalized_budget_program_review", budget["status"])
        self.assertEqual(budget["claimed"], "10.00")

    def test_procurement_unicode_po_key_requires_human_review(self):
        po = self.source("po.csv", ("po_number", "line", "quantity", "unit_price"),
                         [("ſ1", "1", "2", "5.00")])
        invoices = self.source("invoice.csv", ("po_number", "line", "quantity", "unit_price"),
                               [("S1", "1", "2", "5.00")])
        receipts = self.source("receipts.csv", ("po_number", "line", "quantity"),
                               [("S1", "1", "2")])
        result = self.report(engine.procure_guard(po, invoices, receipts, self.root)[0])[0]
        self.assertIn("normalized_po_key_review", result["status"])
        self.assertEqual(result["po_unit_price"], "5.00")
        self.assertEqual(result["po_rows"], "2")
        self.assertEqual(result["invoice_rows"], "2")

    def test_ascii_case_only_ledger_remains_matched(self):
        left = self.source("left.csv", ("id", "amount"), [("Case1", "10.00")])
        right = self.source("right.csv", ("id", "amount"), [("CASE1", "10.00")])
        result = self.report(engine.ledger_diff(left, right, self.root)[0])[0]
        self.assertEqual(result["status"], "matched")


if __name__ == "__main__":
    unittest.main()
