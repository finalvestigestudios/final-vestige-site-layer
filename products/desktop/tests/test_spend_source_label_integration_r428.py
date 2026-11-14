"""R428 actual SpendMap summarizer regression: exact raw vendor-label review.

Synthetic financial rows only; supplied SHA is not proof of source authenticity.
"""
from __future__ import annotations
from datetime import date
from decimal import Decimal
from hashlib import sha256
import unittest

from fvs_suite.spend_analysis import summarize_spend

_SOURCE = sha256(b"R428 synthetic CSV snapshot").hexdigest()
_ASCII = " \t\r\n\v\f"

def row(n, vendor, amount="10.00", category="Supplies"):
    return {"row": str(n), "vendor": vendor, "date": "2026-11-02",
            "amount": amount, "category": category}

def run(records, normalize=None):
    if normalize is None:
        normalize = lambda vendor: vendor.strip(_ASCII).upper()
    return summarize_spend(
        records, normalize_vendor=normalize,
        parse_date=date.fromisoformat, parse_money=Decimal,
        format_money=lambda money: format(money, "f"),
        source_sha256=_SOURCE)

class OriginalLabelIntegrationR428(unittest.TestCase):
    def test_real_summary_keeps_exact_boundary_spacing(self):
        report = run([row(2, " ACME"), row(3, "ACME ")])
        self.assertEqual(len(report), 1)
        item = report[0]
        self.assertEqual(item["amount"], "20.00")
        self.assertEqual(item["vendor_key"], "ACME")
        self.assertEqual(item["source_rows"], "2;3")
        self.assertIn(r"\u0020ACME", item["source_vendor_labels"])
        self.assertIn(r"ACME\u0020", item["source_vendor_labels"])
        self.assertEqual(item["vendor_label_variants"], "1")
        self.assertNotIn("normalized_vendor_collision_review", item["flag"])

    def test_real_summary_keeps_controls_as_visible_evidence(self):
        item = run([row(2, "\tACME\r")])[0]
        self.assertEqual(item["source_vendor_labels"], r"\u0009ACME\u000D")
        self.assertEqual(item["vendor_key"], "ACME")

    def test_real_summary_deterministic_when_records_permuted(self):
        records = [row(4, " ACME", "15.00"), row(2, "ACME ", "-5.00")]
        self.assertEqual(run(records), run(list(reversed(records))))

    def test_real_summary_keeps_money_and_review_status(self):
        item = run([row(2, " ACME", "10.00"), row(3, "ACME ", "-5.00")])[0]
        self.assertEqual(item["amount"], "5.00")
        self.assertEqual(item["gross_charges"], "10.00")
        self.assertEqual(item["gross_credits"], "5.00")
        self.assertEqual(item["credit_offset_review"], "review_mixed_sign_offset")
        self.assertEqual(item["source_sha256"], _SOURCE)

    def test_real_summary_nonascii_boundary_collision_still_requires_review(self):
        normalize = lambda value: value.replace("\u00a0", "").strip(_ASCII).upper()
        item = run([row(2, " ACME"), row(3, "\u00a0ACME")], normalize)[0]
        self.assertIn("normalized_vendor_collision_review", item["flag"])
        self.assertEqual(item["vendor_label_variants"], "2")
        self.assertIn(r"\u0020ACME", item["source_vendor_labels"])
        self.assertIn(r"\u00A0ACME", item["source_vendor_labels"])
