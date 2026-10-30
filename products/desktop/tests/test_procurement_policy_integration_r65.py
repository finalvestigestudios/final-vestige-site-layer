"""R65 whole-engine regressions: strict JSON tolerance policy and private row errors.

These require the complete fvs_suite checkout, not the isolated helper harness.
"""
from __future__ import annotations

import csv
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from fvs_suite import engine, procurement


class ProcureGuardPolicyIntegrationR65Tests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.out = self.root / "out"
        self.out.mkdir()
        self.po = self.root / "po.csv"
        self.invoice = self.root / "invoice.csv"
        self.receipt = self.root / "receipt.csv"
        self.policy = self.root / "policy.json"
        self.po.write_text(
            "po_number,line,quantity,unit_price\nPO-A,1,1,10.00\n", encoding="utf-8")
        self.invoice.write_text(
            "po_number,line,quantity,unit_price,event_type\nPO-A,1,1,10.00,invoice\n",
            encoding="utf-8")
        self.receipt.write_text(
            "po_number,line,quantity,event_type\nPO-A,1,1,receipt\n",
            encoding="utf-8")

    def policy_json(self, *, absolute="0.01", fraction="0.02"):
        self.policy.write_text(json.dumps({
            "version": 1, "price_absolute": absolute,
            "price_fraction": fraction,
        }), encoding="utf-8")

    def run_engine(self):
        return engine.procure_guard(self.po, self.invoice, self.receipt,
                                    self.out, policy_path=self.policy)

    def assert_no_partial_reports(self):
        self.assertFalse(list(self.out.rglob("*.csv")))
        self.assertFalse(list(self.out.rglob("evidence-manifest*")))

    def test_exponent_policy_rejected_before_any_report(self):
        self.policy_json(fraction="1e-2")
        with self.assertRaisesRegex(ValueError, "ASCII fixed-point"):
            self.run_engine()
        self.assert_no_partial_reports()

    def test_unicode_policy_digits_rejected_before_any_report(self):
        self.policy_json(absolute="٠.٠١")
        with self.assertRaisesRegex(ValueError, "ASCII fixed-point"):
            self.run_engine()
        self.assert_no_partial_reports()

    def test_overprecise_policy_rejected_before_any_report(self):
        self.policy_json(fraction="0.020000000")
        with self.assertRaisesRegex(ValueError, "at most eight places"):
            self.run_engine()
        self.assert_no_partial_reports()

    def test_bad_event_type_is_private_and_no_partial_reports(self):
        secret = "private-customer-name"
        self.invoice.write_text(
            "po_number,line,quantity,unit_price,event_type\nPO-A,1,1,10.00," + secret + "\n",
            encoding="utf-8")
        self.policy_json()
        with self.assertRaises(ValueError) as raised:
            self.run_engine()
        self.assertIn("invoice event_type at input physical row 2", str(raised.exception))
        self.assertNotIn(secret, str(raised.exception))
        self.assert_no_partial_reports()

    def test_receipt_bad_event_type_is_private(self):
        secret = "confidential-dock-person"
        self.receipt.write_text(
            "po_number,line,quantity,event_type\nPO-A,1,1," + secret + "\n",
            encoding="utf-8")
        self.policy_json()
        with self.assertRaises(ValueError) as raised:
            self.run_engine()
        self.assertIn("receipt event_type at input physical row 2", str(raised.exception))
        self.assertNotIn(secret, str(raised.exception))
        self.assert_no_partial_reports()

    def test_fixed_point_policy_preserves_provenance_and_review_only(self):
        self.policy_json(absolute="0.01", fraction="0.02")
        parsed = procurement.load_price_policy(self.policy)
        self.assertEqual(parsed.absolute, Decimal("0.01"))
        self.assertEqual(parsed.fraction, Decimal("0.02"))
        paths = self.run_engine()
        reports = [Path(p) for p in paths if "procurement-three-way" in Path(p).name]
        self.assertEqual(len(reports), 1)
        with reports[0].open(newline="", encoding="utf-8") as fp:
            rows = list(csv.DictReader(fp))
        self.assertEqual(len(rows), 1)
        self.assertIn(rows[0]["status"], {"matched", "price_variance_above_policy"})
        self.assertEqual(rows[0]["price_policy_sha256"], parsed.source_sha256)
        self.assertTrue(any("evidence-manifest" in Path(p).name for p in paths))


if __name__ == "__main__":
    unittest.main()
