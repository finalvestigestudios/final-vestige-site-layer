"""R87 direct-API exact review math and linked-grant custody.

Synthetic offline fixtures only. These are committed integration tests, not
evidence of full-checkout CI or validated Windows binaries until actually run.
"""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from decimal import Decimal, Inexact, Rounded, ROUND_DOWN, localcontext
from pathlib import Path

from fvs_suite import engine, procurement
from fvs_suite.grant_allocations import reconcile_allocations
from fvs_suite.review import price_exceeds_tolerance, price_outside_tolerance


class PriceReviewContextR87(unittest.TestCase):
    def test_precise_default_price_variance(self):
        self.assertTrue(price_exceeds_tolerance(
            Decimal("102.02"), Decimal("100.01")))
        self.assertFalse(price_exceeds_tolerance(
            Decimal("102.0102"), Decimal("100.01")))
        self.assertTrue(price_exceeds_tolerance(
            Decimal("102.01020001"), Decimal("100.01")))
        self.assertFalse(price_exceeds_tolerance(
            Decimal("0.01"), Decimal("0.00")))

    def test_low_precision_cannot_hide_price_threshold(self):
        for precision in (1, 2, 3, 6, 28):
            with self.subTest(precision=precision), localcontext() as ctx:
                ctx.prec = precision
                ctx.rounding = ROUND_DOWN
                self.assertTrue(price_exceeds_tolerance(
                    Decimal("102.02"), Decimal("100.01")))
                self.assertFalse(price_exceeds_tolerance(
                    Decimal("102.0102"), Decimal("100.01")))
                self.assertEqual(ctx.prec, precision)
                self.assertEqual(ctx.rounding, ROUND_DOWN)

    def test_direct_policy_outside_matches_exact_legacy_threshold(self):
        policy = procurement.PricePolicy()
        for precision in (1, 2, 3, 6, 28):
            with self.subTest(precision=precision), localcontext() as ctx:
                ctx.prec = precision
                self.assertTrue(policy.outside(
                    Decimal("102.02"), Decimal("100.01")))
                self.assertFalse(policy.outside(
                    Decimal("102.0102"), Decimal("100.01")))

    def test_custom_policy_remains_review_only(self):
        strict = procurement.PricePolicy(
            absolute=Decimal("0.01"), fraction=Decimal("0.01"))
        wide = procurement.PricePolicy(
            absolute=Decimal("1"), fraction=Decimal("0.04"))
        with localcontext() as ctx:
            ctx.prec = 2
            self.assertTrue(strict.outside(
                Decimal("103"), Decimal("100")))
            self.assertFalse(wide.outside(
                Decimal("103"), Decimal("100")))
            self.assertTrue(wide.widened)

    def test_negative_price_comparison_is_symmetric(self):
        for precision in (1, 2, 28):
            with self.subTest(precision=precision), localcontext() as ctx:
                ctx.prec = precision
                self.assertTrue(price_exceeds_tolerance(
                    Decimal("-102.02"), Decimal("-100.01")))
                self.assertFalse(price_exceeds_tolerance(
                    Decimal("-102.0002"), Decimal("-100.01")))

    def test_extended_procurement_total_stays_in_domain(self):
        actual = Decimal("199999999999999998000.00000000000002")
        expected = Decimal("199999999999999998000.00000000000001")
        with localcontext() as ctx:
            ctx.prec = 2
            self.assertFalse(procurement.PricePolicy().outside(actual, expected))
        self.assertTrue(price_outside_tolerance(
            Decimal("210000000000000000000.00"),
            Decimal("200000000000000000000.00"),
            Decimal("0.01"), Decimal("0.02")))

    def test_caller_traps_and_flags_are_not_touched(self):
        with localcontext() as ctx:
            ctx.prec = 2
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            self.assertTrue(procurement.PricePolicy().outside(
                Decimal("102.02"), Decimal("100.01")))
            self.assertTrue(price_exceeds_tolerance(
                Decimal("102.02"), Decimal("100.01")))
            self.assertFalse(ctx.flags[Inexact])
            self.assertFalse(ctx.flags[Rounded])

    def test_reject_float_nonfinite_and_unbounded_inputs(self):
        for value in (1.0, float("nan"), Decimal("NaN"), Decimal("Infinity"),
                      Decimal("1e30")):
            with self.subTest(value=str(value)), self.assertRaises(ValueError):
                price_exceeds_tolerance(value, Decimal("100"))
        for threshold in (Decimal("-0.01"), Decimal("Infinity"), Decimal("1e30")):
            with self.subTest(threshold=str(threshold)), self.assertRaises(ValueError):
                price_outside_tolerance(
                    Decimal("10"), Decimal("10"), threshold, Decimal("0.02"))
        with self.assertRaises(ValueError):
            price_outside_tolerance(
                Decimal("10"), Decimal("10"), Decimal("0.01"), Decimal("1.1"))


class LinkedGrantContextR87(unittest.TestCase):
    def setUp(self):
        working = tempfile.TemporaryDirectory(prefix="fvs-r87-")
        self.addCleanup(working.cleanup)
        self.root = Path(working.name)

    def source(self, name, headers, values):
        path = self.root / name
        with path.open("w", encoding="utf-8", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(headers)
            writer.writerows(values)
        return str(path)

    def fixtures(self, claims, ledger, budgets):
        return (
            self.source("claims.csv",
                ("claim_id", "amount", "program", "ledger_reference",
                 "claim_type", "related_claim"), claims),
            self.source("ledger.csv", ("transaction_id", "amount", "program"), ledger),
            self.source("budgets.csv", ("program", "budget"), budgets),
        )

    def read(self, file):
        with Path(file).open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def test_direct_split_claims_exact_under_hostile_context(self):
        paths = self.fixtures(
            (("C1", "999999999999.99", "G1", "T1", "claim", ""),
             ("C2", "999999999999.99", "G1", "T1", "claim", "")),
            (("T1", "999999999999.99", "G1"),
             ("T1", "999999999999.99", "G1")),
            (("G1", "999999999999.99"),))
        originals = [Path(source).read_bytes() for source in paths]
        with localcontext() as ctx:
            ctx.prec = 2
            ctx.rounding = ROUND_DOWN
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            reports = reconcile_allocations(*paths, str(self.root))
            self.assertEqual(ctx.prec, 2)
            self.assertFalse(ctx.flags[Inexact])
        line = self.read(reports[0])[0]
        budget = self.read(reports[1])[0]
        self.assertEqual(line["gross_claim_amount"], "1999999999999.98")
        self.assertEqual(line["net_claim_amount"], "1999999999999.98")
        self.assertEqual(line["ledger_amount"], "1999999999999.98")
        self.assertEqual(line["difference"], "0.00")
        self.assertIn("duplicate_ledger_id_review", line["status"])
        self.assertEqual(budget["claimed"], "1999999999999.98")
        self.assertIn("over_budget_review", budget["status"])
        self.assertTrue(Path(reports[2]).is_file())
        self.assertEqual([Path(source).read_bytes() for source in paths], originals)

    def test_linked_credit_net_preserves_cents_under_low_precision(self):
        paths = self.fixtures(
            (("C1", "999999999999.99", "G1", "T1", "claim", ""),
             ("CR", "0.01", "G1", "T1", "credit", "C1")),
            (("T1", "999999999999.98", "G1"),),
            (("G1", "999999999999.99"),))
        with localcontext() as ctx:
            ctx.prec = 1
            reports = reconcile_allocations(*paths, str(self.root))
        line = self.read(reports[0])[0]
        summary = self.read(reports[1])[0]
        self.assertEqual(line["gross_claim_amount"], "999999999999.99")
        self.assertEqual(line["credit_amount"], "0.01")
        self.assertEqual(line["net_claim_amount"], "999999999999.98")
        self.assertEqual(line["difference"], "0.00")
        self.assertIn("credit_memo_review", line["status"])
        self.assertEqual(summary["claimed"], "999999999999.98")

    def test_engine_linked_route_preserves_audit_review(self):
        paths = self.fixtures(
            (("C1", "100", "G1", "T1", "claim", ""),
             ("CR1", "10", "G1", "T1", "credit", "C1")),
            (("T1", "90", "G1"),), (("G1", "200"),))
        with localcontext() as ctx:
            ctx.prec = 2
            reports = engine.grant_audit(*paths, str(self.root))
        line = self.read(reports[0])[0]
        self.assertEqual(line["net_claim_amount"], "90.00")
        self.assertIn("credit_memo_review", line["status"])
        self.assertNotIn("unlinked_credit_review", line["status"])

    def test_direct_invalid_source_does_not_publish_reports(self):
        paths = self.fixtures(
            (("C1", "-100", "G1", "T1", "claim", ""),),
            (("T1", "100", "G1"),), (("G1", "200"),))
        with localcontext() as ctx:
            ctx.prec = 1
            with self.assertRaises(ValueError):
                reconcile_allocations(*paths, str(self.root))
        self.assertFalse(list(self.root.glob("grant-audit-exceptions-*.csv")))
        self.assertFalse(list(self.root.glob("grant-budget-check-*.csv")))


if __name__ == "__main__":
    unittest.main()
