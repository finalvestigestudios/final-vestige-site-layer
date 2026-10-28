"""High-risk financial import and exact binary-equivalent engine regression tests."""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path
from decimal import Decimal

from fvs_suite import engine
from fvs_suite.smoke import run_smoke


class ImportAndReconciliationSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fvs-test-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def make_csv(self, filename, headers, values):
        path = self.folder / filename
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(values)
        return str(path)

    @staticmethod
    def rows(path):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_duplicate_financial_headers_are_rejected(self):
        path = self.make_csv("duplicate.csv", ("id", "Amount", "amount"), [("X1", "1", "1000")])
        with self.assertRaisesRegex(ValueError, "duplicate normalized CSV header"):
            engine.table(path, ("id", "amount"))

    def test_blank_header_is_rejected(self):
        path = self.make_csv("blank.csv", ("id", "", "amount"), [("X1", "ignored", "10")])
        with self.assertRaisesRegex(ValueError, "blank or duplicate normalized CSV header"):
            engine.table(path, ("id", "amount"))

    def test_ledger_normalized_id_collision_is_not_marked_matched(self):
        left = self.make_csv("left.csv", ("id", "amount"), [("INV-100", "12.00")])
        right = self.make_csv("right.csv", ("id", "amount"), [("INV100", "12.00")])
        result = self.rows(engine.ledger_diff(left, right, self.folder)[0])
        self.assertEqual(result[0]["status"], "normalized_id_review")
        self.assertEqual(result[0]["difference"], "0.00")
        self.assertEqual(result[0]["left_rows"], "2")
        self.assertEqual(result[0]["right_rows"], "2")

    def test_ledger_normalized_collision_and_money_variance_both_visible(self):
        left = self.make_csv("left.csv", ("id", "amount"), [("AC-5", "12.00")])
        right = self.make_csv("right.csv", ("id", "amount"), [("AC5", "11.00")])
        report = self.rows(engine.ledger_diff(left, right, self.folder)[0])
        self.assertEqual(report[0]["status"], "normalized_id_review;variance")

    def test_same_id_with_case_difference_is_considered_the_same(self):
        left = self.make_csv("left.csv", ("id", "amount"), [("ABC", "12.00")])
        right = self.make_csv("right.csv", ("id", "amount"), [("abc", "12.00")])
        report = self.rows(engine.ledger_diff(left, right, self.folder)[0])
        self.assertEqual(report[0]["status"], "matched")

    def test_grant_normalized_id_collision_requires_review(self):
        claims = self.make_csv("claims.csv", ("id", "amount", "program"), [("C-17", "8", "G1")])
        ledger = self.make_csv("ledger.csv", ("id", "amount", "program"), [("C17", "8", "G1")])
        budgets = self.make_csv("budgets.csv", ("program", "budget"), [("G1", "100")])
        outputs = engine.grant_audit(claims, ledger, budgets, self.folder)
        report = self.rows(outputs[0])
        self.assertEqual(report[0]["status"], "normalized_id_review")

    def test_spreadsheet_formula_injection_is_neutralized(self):
        self.assertEqual(engine.safe_cell("=1+1"), "'=1+1")
        self.assertEqual(engine.safe_cell("  +SUM(A1)"), "'  +SUM(A1)")
        self.assertEqual(engine.safe_cell("@cmd"), "'@cmd")
        self.assertEqual(engine.safe_cell("-SUM(A1)"), "'-SUM(A1)")
        self.assertEqual(engine.safe_cell("-1.25"), "-1.25")

    def test_money_preserves_exact_decimal_and_rejects_nan(self):
        self.assertEqual(engine.money("$1,234.56"), Decimal("1234.56"))
        self.assertEqual(engine.money("(123.45)"), Decimal("-123.45"))
        for value in ("NaN", "sNaN", "Infinity", "-Infinity", "Not a number"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                engine.money(value)

    def test_all_six_offline_smoke_flows(self):
        for app in ("ledger", "invoices", "spend", "policy", "grants", "procurement"):
            with self.subTest(app=app):
                outputs = run_smoke(app)
                self.assertGreaterEqual(len(outputs), 1)

    def test_unknown_smoke_target_fails(self):
        with self.assertRaisesRegex(ValueError, "Unsupported application"):
            run_smoke("not-an-app")


if __name__ == "__main__":
    unittest.main()
