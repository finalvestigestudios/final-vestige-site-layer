"""High-risk cross-file financial matching behavior and provenance regressions."""
from __future__ import annotations

import csv
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from fvs_suite import engine
from fvs_suite.review import (
    normalized_collision, reconciliation_status, price_exceeds_tolerance, raw_values
)


class FinancialIntegrityR3Tests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix="fvs-financial-r3-")
        self.addCleanup(temp.cleanup)
        self.root=Path(temp.name)

    def csv(self, name, headers, rows):
        path=self.root/name
        with path.open("w",encoding="utf-8",newline="") as stream:
            writer=csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
        return str(path)

    @staticmethod
    def rows(path):
        with path.open(encoding="utf-8-sig",newline="") as stream:
            return list(csv.DictReader(stream))

    def test_alias_conflicts_fail_closed_for_money(self):
        path=self.csv("ambiguous.csv",("id","amount","paid"),(("A","10","100000"),))
        with self.assertRaisesRegex(ValueError,"ambiguous 'amount' aliases"):
            engine.table(path,("id","amount"))

    def test_alias_conflicts_fail_closed_for_identifiers(self):
        path=self.csv("ambiguous.csv",("transaction_id","id","amount"),(("A","B","100"),))
        with self.assertRaisesRegex(ValueError,"ambiguous 'id' aliases"):
            engine.table(path,("id","amount"))

    def test_optional_alias_conflicts_also_fail_closed(self):
        path=self.csv("ambiguous.csv",("vendor","amount","date","category","spend_category"),(
            ("ACME","5","2026-01-01","A","B"),))
        with self.assertRaisesRegex(ValueError,"ambiguous 'category' aliases"):
            engine.table(path,("vendor","amount","date"),("category",))

    def test_ledger_duplicate_and_amount_variance_both_reported(self):
        left=self.csv("left.csv",("id","amount"),(("X","2"),("X","3")))
        right=self.csv("right.csv",("id","amount"),(("X","4"),))
        report=self.rows(engine.ledger_diff(left,right,self.root)[0])[0]
        self.assertEqual(report["status"],"duplicate_id_review;variance")
        self.assertEqual(report["difference"],"1.00")
        self.assertEqual(report["left_rows"],"2;3")

    def test_ledger_original_identifiers_are_visible(self):
        left=self.csv("left.csv",("id","amount"),(("A-1","5"),))
        right=self.csv("right.csv",("id","amount"),(("A1","5"),))
        report=self.rows(engine.ledger_diff(left,right,self.root)[0])[0]
        self.assertEqual(report["status"],"normalized_id_review")
        self.assertEqual(report["left_ids"],"A-1")
        self.assertEqual(report["right_ids"],"A1")

    def test_grant_program_normalization_and_budget_must_be_reviewed(self):
        claims=self.csv("claims.csv",("id","amount","program"),(("C1","10","G-1"),))
        ledger=self.csv("ledger.csv",("id","amount","program"),(("C1","10","G1"),))
        budgets=self.csv("budgets.csv",("program","budget"),(("G1","100"),))
        outputs=engine.grant_audit(claims,ledger,budgets,self.root)
        report=self.rows(outputs[0])[0]
        summary=self.rows(outputs[1])[0]
        self.assertEqual(report["status"],"normalized_program_review")
        self.assertEqual(report["claim_programs"],"G-1")
        self.assertEqual(report["ledger_programs"],"G1")
        self.assertEqual(summary["status"],"within_budget;normalized_budget_program_review")
        self.assertIn("G-1",summary["source_programs"])
        self.assertIn("G1",summary["source_programs"])

    def test_grant_duplicate_and_variance_are_separate_findings(self):
        claims=self.csv("claims.csv",("id","amount","program"),(("C1","4","G1"),("C1","4","G1")))
        ledger=self.csv("ledger.csv",("id","amount","program"),(("C1","7","G1"),))
        budgets=self.csv("budgets.csv",("program","budget"),(("G1","100"),))
        report=self.rows(engine.grant_audit(claims,ledger,budgets,self.root)[0])[0]
        self.assertEqual(report["status"],"duplicate_id_review;variance")
        self.assertEqual(report["difference"],"1.00")

    def test_grant_only_case_diff_is_not_collision(self):
        claims=self.csv("claims.csv",("id","amount","program"),(("C1","10","G1"),))
        ledger=self.csv("ledger.csv",("id","amount","program"),(("c1","10","g1"),))
        budgets=self.csv("budgets.csv",("program","budget"),(("G1","100"),))
        outputs=engine.grant_audit(claims,ledger,budgets,self.root)
        self.assertEqual(self.rows(outputs[0])[0]["status"],"matched")
        self.assertEqual(self.rows(outputs[1])[0]["status"],"within_budget")

    def procure(self,po_rows,invoice_rows,receipt_rows):
        po=self.csv("po.csv",("po_number","line","quantity","unit_price"),po_rows)
        inv=self.csv("invoices.csv",("po_number","line","quantity","unit_price"),invoice_rows)
        receipts=self.csv("receipts.csv",("po_number","line","quantity"),receipt_rows)
        return self.rows(engine.procure_guard(po,inv,receipts,self.root)[0])[0]

    def test_po_normalization_collision_cannot_be_matched(self):
        r=self.procure((("PO-100","1","2","5"),),
                       (("PO100","1","2","5"),),
                       (("PO-100","1","2"),))
        self.assertEqual(r["status"],"normalized_po_key_review")
        self.assertEqual(r["po_ids"],"PO-100")
        self.assertEqual(r["invoice_po_ids"],"PO100")

    def test_po_line_normalization_collision_cannot_be_matched(self):
        r=self.procure((("P1","L-1","2","5"),),
                       (("P1","L1","2","5"),),
                       (("P1","l-1","2"),))
        self.assertEqual(r["status"],"normalized_line_key_review")
        self.assertIn("L-1",r["line_labels"])
        self.assertIn("L1",r["line_labels"])

    def test_potential_duplicate_invoice_lines_flagged(self):
        r=self.procure((("P1","1","10","5"),),
                       (("P1","1","5","5"),("P1","1","5","5")),
                       (("P1","1","10"),))
        self.assertEqual(r["status"],"possible_duplicate_invoice_line")

    def test_offsetting_invoice_price_errors_still_flagged(self):
        r=self.procure((("P1","1","10","10"),),
                       (("P1","1","5","5"),("P1","1","5","15")),
                       (("P1","1","10"),))
        self.assertIn("price_variance_above_2pct",r["status"])
        self.assertEqual(r["invoice_total"],"100.00")

    def test_negative_unit_price_needs_review(self):
        r=self.procure((("P1","1","1","5"),),
                       (("P1","1","1","-5"),),
                       (("P1","1","1"),))
        self.assertIn("negative_unit_price_review",r["status"])

    def test_exact_procurement_still_matches(self):
        r=self.procure((("P1","1","2","5"),),
                       (("p1","1","2","5"),),
                       (("P1","1","2"),))
        self.assertEqual(r["status"],"matched")

    def test_shared_review_helpers(self):
        self.assertTrue(normalized_collision(({"id":"X-1"},{"id":"X1"}),"id"))
        self.assertFalse(normalized_collision(({"id":"X1"},{"id":"x1"}),"id"))
        self.assertEqual(raw_values(({"id":"X-1"},{"id":"X1"}),"id"),("X-1","X1"))
        self.assertTrue(price_exceeds_tolerance(Decimal("15"),Decimal("10")))
        self.assertEqual(
            reconciliation_status([{"id":"X"},{"id":"X"}],[{"id":"X"}],
                                  Decimal("5"),Decimal("4"),
                                  missing_left="left",missing_right="right"),
            "duplicate_id_review;variance")


if __name__=="__main__":
    unittest.main()
