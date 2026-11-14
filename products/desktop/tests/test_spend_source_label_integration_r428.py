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


class BoundedSourceVendorLabelsIntegrationR429(unittest.TestCase):
    def test_high_cardinality_report_is_bounded_without_changing_financial_facts(self):
        records = [row(i + 2, f"SOURCE{i:03}", "1.00") for i in range(100)]
        report = run(records, normalize=lambda value: "ONEVENDOR")
        self.assertEqual(len(report), 1)
        item = report[0]
        self.assertEqual(item["amount"], "100.00")
        self.assertEqual(item["gross_charges"], "100.00")
        self.assertEqual(item["gross_credits"], "0")
        self.assertEqual(item["source_sha256"], _SOURCE)
        self.assertEqual(item["vendor_label_variants"], "100")
        self.assertIn("normalized_vendor_collision_review", item["flag"])
        self.assertEqual(item["vendor_month_evidence_count"], "100")
        self.assertLessEqual(len(item["source_vendor_labels"]), 8192)
        self.assertIn(r"\u[PREVIEW_ONLY:shown=32:omitted=68:sha256=",
                      item["source_vendor_labels"])

    def test_long_original_vendor_label_keeps_a_verifiable_review_marker(self):
        original = "A" * 3000
        item = run([row(2, original)], normalize=lambda value: "ONEVENDOR")[0]
        self.assertEqual(item["amount"], "10.00")
        self.assertEqual(item["vendor_label_variants"], "1")
        self.assertEqual(item["source_rows"], "2")
        self.assertTrue(item["source_vendor_labels"].startswith(
            "A" * 64 + r"\u[LABEL_PREFIX_ONLY]"))
        self.assertIn(r"\u[PREVIEW_ONLY:shown=1:omitted=0:sha256=",
                      item["source_vendor_labels"])

    def test_high_cardinality_digest_and_review_stable_across_row_order(self):
        records = [row(i + 2, f"V{i:03}", "1.25") for i in range(40)]
        forward = run(records, normalize=lambda value: "ONEVENDOR")
        reverse = run(list(reversed(records)), normalize=lambda value: "ONEVENDOR")
        self.assertEqual(forward, reverse)
        self.assertEqual(forward[0]["amount"], "50.00")
        self.assertEqual(forward[0]["vendor_label_variants"], "40")
