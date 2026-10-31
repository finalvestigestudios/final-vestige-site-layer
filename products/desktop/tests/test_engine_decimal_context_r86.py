"""R86 shared Decimal parser and legacy aggregation custody (synthetic data only).

No test result establishes payment authority, compliance, or release readiness.
"""
from __future__ import annotations

import csv
import tempfile
import unittest
from decimal import Decimal, Inexact, Rounded, ROUND_DOWN, localcontext
from pathlib import Path

from fvs_suite import engine


class SharedDecimalContextR86(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-context-r86-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def csv(self, name, columns, rows):
        target = self.root / name
        with target.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            writer.writerows(rows)
        return str(target)

    def rows(self, path):
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def hostile(self):
        context = localcontext()
        return context

    def test_signed_negative_source_is_exact_at_low_precision(self):
        for precision in (1, 3, 6, 28):
            with self.subTest(precision=precision), localcontext() as ctx:
                ctx.prec = precision
                ctx.rounding = ROUND_DOWN
                self.assertEqual(engine.unit_cost("-999999999999.12345678"),
                                 Decimal("-999999999999.12345678"))
                self.assertEqual(engine.unit_cost("($999,999,999,999.12345678)"),
                                 Decimal("-999999999999.12345678"))

    def test_parsed_money_is_context_independent_and_half_up(self):
        for precision in (1, 3, 6, 28):
            with self.subTest(precision=precision), localcontext() as ctx:
                ctx.prec = precision
                ctx.rounding = ROUND_DOWN
                ctx.traps[Inexact] = True
                ctx.traps[Rounded] = True
                self.assertEqual(engine.money("999999999999.995"),
                                 Decimal("1000000000000.00"))
                self.assertEqual(engine.money("($999,999,999,999.99)"),
                                 Decimal("-999999999999.99"))
                self.assertEqual(engine.money("0.005"), Decimal("0.01"))
                self.assertEqual(ctx.prec, precision)
                self.assertTrue(ctx.traps[Inexact])
                self.assertTrue(ctx.traps[Rounded])
                self.assertFalse(ctx.flags[Inexact])

    def test_fractional_scale_validates_actual_digits_without_normalize(self):
        for precision in (1, 3, 28):
            with self.subTest(precision=precision), localcontext() as ctx:
                ctx.prec = precision
                ctx.traps[Inexact] = True
                ctx.traps[Rounded] = True
                self.assertEqual(engine.qty("999999999.12345678"),
                                 Decimal("999999999.12345678"))
                self.assertEqual(engine.qty("1.000000000000000"),
                                 Decimal("1.000000000000000"))
                self.assertEqual(engine.unit_cost("0.000000010000"),
                                 Decimal("0.000000010000"))
                for parser, source in (
                    (engine.qty, "1.000000001000"),
                    (engine.qty, "0.000000001"),
                    (engine.unit_cost, "1.000000001000"),
                    (engine.unit_cost, "0.000000001"),
                ):
                    with self.subTest(source=source, parser=parser.__name__):
                        with self.assertRaises(ValueError):
                            parser(source)

    def test_signed_zero_and_long_zero_fraction_preserved(self):
        with localcontext() as ctx:
            ctx.prec = 2
            self.assertEqual(engine.money("($0.00)"), Decimal("-0.00"))
            self.assertEqual(engine.qty("0.000000000000000000"),
                             Decimal("0.000000000000000000"))
            self.assertEqual(engine.unit_cost("0.000000000000000000"),
                             Decimal("0.000000000000000000"))

    def test_dollars_large_total_never_uses_caller_rounding(self):
        with localcontext() as ctx:
            ctx.prec = 2
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            self.assertEqual(engine.dollars(Decimal("200000000000000000.005")),
                             "200000000000000000.01")
            self.assertEqual(engine.dollars(Decimal("-0.005")), "-0.01")
            self.assertEqual(ctx.prec, 2)
            self.assertFalse(ctx.flags[Inexact])

    def test_invalid_private_amount_is_not_echoed(self):
        secret = "PRIVATE_CLIENT_ACCOUNT_1245"
        with localcontext() as ctx:
            ctx.prec = 2
            with self.assertRaises(ValueError) as caught:
                engine.money(secret)
        self.assertNotIn(secret, str(caught.exception))

    def test_ledger_multirow_sum_keeps_every_cent_under_hostile_context(self):
        left = self.csv("ledger-left.csv", ("id", "amount"),
                        (("A", "999999999999.99"), ("A", "999999999999.99")))
        right = self.csv("ledger-right.csv", ("id", "amount"),
                         (("A", "1000000000000"),))
        with localcontext() as ctx:
            ctx.prec = 2
            ctx.rounding = ROUND_DOWN
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            row = self.rows(engine.ledger_diff(left, right, self.root)[0])[0]
            self.assertEqual(ctx.prec, 2)
            self.assertFalse(ctx.flags[Inexact])
        self.assertEqual(row["left_amount"], "1999999999999.98")
        self.assertEqual(row["right_amount"], "1000000000000.00")
        self.assertEqual(row["difference"], "999999999999.98")
        self.assertIn("duplicate_id_review", row["status"])
        self.assertIn("variance", row["status"])
        self.assertEqual(row["left_rows"], "2;3")
        self.assertEqual(len(row["left_source_sha256"]), 64)

    def test_ledger_signed_variance_never_rounds_away(self):
        left = self.csv("ledger-left.csv", ("id", "amount"),
                        (("A", "-999999999999.99"),))
        right = self.csv("ledger-right.csv", ("id", "amount"),
                         (("A", "-999999999999.98"),))
        with localcontext() as ctx:
            ctx.prec = 3
            row = self.rows(engine.ledger_diff(left, right, self.root)[0])[0]
        self.assertEqual(row["status"], "variance")
        self.assertEqual(row["difference"], "-0.01")

    def test_legacy_grant_budget_totals_are_exact_and_review_only(self):
        claims = self.csv("claims.csv", ("id", "amount", "program"),
                          (("A", "999999999999.99", "G1"),
                           ("B", "999999999999.99", "G1")))
        ledger = self.csv("grant-ledger.csv", ("id", "amount", "program"),
                          (("A", "999999999999.99", "G1"),
                           ("B", "999999999999.99", "G1")))
        budget = self.csv("budget.csv", ("program", "budget"),
                          (("G1", "1000000000000"),))
        with localcontext() as ctx:
            ctx.prec = 2
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            checks, summary, inventory = engine.grant_audit(
                claims, ledger, budget, self.root)
            report = self.rows(summary)[0]
            self.assertEqual(ctx.prec, 2)
        self.assertEqual(report["claimed"], "1999999999999.98")
        self.assertEqual(report["budget"], "1000000000000.00")
        self.assertEqual(report["status"], "over_budget_review")
        self.assertTrue(checks.is_file())
        self.assertTrue(inventory.is_file())

    def test_invoice_candidate_amounts_are_exact_at_low_precision(self):
        invoices = self.csv("invoices.csv",
                            ("vendor", "invoice_number", "amount", "date"),
                            (("ACME", "A1", "999999999999.99", "2026-01-01"),
                             ("Acme", "A1", "999999999999.99", "2026-01-02")))
        with localcontext() as ctx:
            ctx.prec = 2
            rows = self.rows(engine.invoice_twins(invoices, self.root)[0])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "exact_invoice_key")
        self.assertEqual(rows[0]["amount_a"], "999999999999.99")
        self.assertEqual(rows[0]["amount_b"], "999999999999.99")

    def test_spendmap_preserves_exact_large_month_under_low_precision(self):
        source = self.csv("spend.csv", ("vendor", "amount", "date", "category"),
                          (("ACME", "999999999999.99", "2026-01-01", "A"),
                           ("ACME", "999999999999.99", "2026-01-02", "A")))
        with localcontext() as ctx:
            ctx.prec = 2
            rows = self.rows(engine.spend_map(source, self.root)[0])
        self.assertEqual(rows[0]["amount"], "1999999999999.98")
        self.assertEqual(rows[0]["source_rows"], "2;3")
        self.assertEqual(len(rows[0]["source_sha256"]), 64)

    def test_procurement_exact_price_unchanged_at_hostile_context(self):
        po = self.csv("po.csv", ("po_number", "line", "quantity", "unit_price"),
                      (("P1", "1", "1", "999999999999.12345678"),))
        invoices = self.csv("invoices.csv",
                            ("po_number", "line", "quantity", "unit_price"),
                            (("P1", "1", "1", "999999999999.12345678"),))
        receipts = self.csv("receipts.csv", ("po_number", "line", "quantity"),
                            (("P1", "1", "1"),))
        with localcontext() as ctx:
            ctx.prec = 2
            row = self.rows(engine.procure_guard(
                po, invoices, receipts, self.root)[0])[0]
        self.assertEqual(row["invoice_total"], "999999999999.12")
        self.assertEqual(row["invoice_total_exact"], "999999999999.12345678")
        self.assertEqual(row["status"], "matched")


if __name__ == "__main__":
    unittest.main()
