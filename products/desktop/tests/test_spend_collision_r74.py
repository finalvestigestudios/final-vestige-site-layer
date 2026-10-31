"""R74: SpendMap's variant counts and alerts agree under Unicode folds."""
from __future__ import annotations

import re
import unittest
from datetime import date
from decimal import Decimal

from fvs_suite.spend_analysis import summarize_spend

DIGEST = "a" * 64


def record(row: int, vendor: str, amount="1.10", date_text="2026-10-30", category="Office"):
    return {"row": str(row), "vendor": vendor, "amount": amount,
            "date": date_text, "category": category}


def summarize(records):
    return summarize_spend(
        records, normalize_vendor=lambda s: re.sub(r"[^A-Z0-9]+", "", s.upper()),
        parse_date=date.fromisoformat, parse_money=Decimal,
        format_money=lambda x: format(x.quantize(Decimal("0.01")), ".2f"),
        source_sha256=DIGEST,
    )


class SpendCollisionR74(unittest.TestCase):
    def test_sharp_s_and_ss_same_bucket_require_review_and_two_variants(self):
        rows = summarize([record(2,"ß", "1.10"), record(3,"SS", "2.20")])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["amount"], "3.30")
        self.assertEqual(rows[0]["vendor_key"], "SS")
        self.assertEqual(rows[0]["flag"], "normalized_vendor_collision_review")
        self.assertEqual(rows[0]["vendor_label_variants"], "2")
        self.assertEqual(rows[0]["source_rows"], "2;3")
        self.assertIn("ß", rows[0]["source_vendor_labels"])
        self.assertIn("SS", rows[0]["source_vendor_labels"])

    def test_long_s_source_across_months_flags_every_bucket(self):
        rows = summarize([record(2,"ſ1", date_text="2026-01-01"),
                          record(3,"S1", date_text="2026-02-01")])
        self.assertEqual([r["flag"] for r in rows], ["normalized_vendor_collision_review"] * 2)
        self.assertEqual([r["vendor_label_variants"] for r in rows], ["2", "2"])
        self.assertEqual([r["amount"] for r in rows], ["1.10", "1.10"])

    def test_ligature_and_ascii_ff_are_reviewed(self):
        rows = summarize([record(2,"ﬀ", "1.00"), record(3,"FF", "2.00")])
        self.assertEqual(rows[0]["vendor_label_variants"], "2")
        self.assertEqual(rows[0]["flag"], "normalized_vendor_collision_review")

    def test_ascii_case_only_is_still_one_variant(self):
        rows = summarize([record(2,"AcMe"), record(3,"ACME")])
        self.assertEqual(rows[0]["vendor_label_variants"], "1")
        self.assertEqual(rows[0]["flag"], "")

    def test_punctuation_ambiguity_still_flagged(self):
        rows = summarize([record(2,"A-CME"), record(3,"ACME")])
        self.assertEqual(rows[0]["vendor_label_variants"], "2")
        self.assertEqual(rows[0]["flag"], "normalized_vendor_collision_review")

    def test_unicode_collision_and_spike_flags_both_survive(self):
        rows = summarize([
            record(2,"ſ1", "10", "2026-01-01"),
            record(3,"S1", "10", "2026-02-01"),
            record(4,"S1", "10", "2026-03-01"),
            record(5,"S1", "30", "2026-04-01"),
        ])
        self.assertEqual(rows[-1]["flag"], "review_spike;normalized_vendor_collision_review")
        self.assertEqual(rows[-1]["baseline_median"], "10")
        self.assertEqual(rows[-1]["vendor_label_variants"], "2")

    def test_source_sha_is_preserved_without_rehashing(self):
        rows = summarize([record(2, "S1", "0.01")])
        self.assertEqual(rows[0]["source_sha256"], DIGEST)

    def test_duplicate_physical_row_rejected_before_report(self):
        with self.assertRaisesRegex(ValueError,"Duplicate spend physical CSV row"):
            summarize([record(2,"S1"), record(2,"ſ1")])


if __name__ == "__main__":
    unittest.main()
