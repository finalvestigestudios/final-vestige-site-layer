"""R59 isolated, deterministic SpendMap Lite provenance and spike tests.

Full CSV-engine integration tests live in test_spend_engine_integration_r59.py.
All test fixtures are synthetic.
"""
from __future__ import annotations

import re
import unittest
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from fvs_suite.spend_analysis import summarize_spend


def _normalize(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "", str(value).upper())


def _money(value: str) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _dollars(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), ".2f")


def _row(n, vendor="ACME", amount="10.00", month="2026-01-01", category="Parts"):
    return {"row": str(n), "vendor": vendor, "amount": amount, "date": month,
            "category": category}


def _summarize(rows):
    return summarize_spend(rows, normalize_vendor=_normalize,
                           parse_date=date.fromisoformat,
                           parse_money=_money, format_money=_dollars)


class SpendProvenanceR59(unittest.TestCase):
    def test_empty_input_gives_empty_report(self):
        self.assertEqual(_summarize([]), [])

    def test_preserves_original_source_rows_in_input_order(self):
        item = _summarize([_row(2), _row(4, amount="2.00"), _row(9, amount="3")])[0]
        self.assertEqual(item["source_rows"], "2;4;9")
        self.assertEqual(item["amount"], "15.00")

    def test_physical_multiline_line_numbers_are_not_renumbered(self):
        self.assertEqual(_summarize([_row(2), _row(6)])[0]["source_rows"], "2;6")

    def test_punctuation_normalization_collision_is_flagged(self):
        item = _summarize([_row(2, "A-CME"), _row(3, "ACME")])[0]
        self.assertEqual(item["flag"], "normalized_vendor_collision_review")
        self.assertEqual(item["source_vendor_labels"], "A-CME; ACME")
        self.assertEqual(item["vendor_label_variants"], "2")

    def test_case_only_variants_do_not_count_as_collision(self):
        item = _summarize([_row(2, "Acme"), _row(3, "aCmE")])[0]
        self.assertEqual(item["flag"], "")
        self.assertEqual(item["vendor_label_variants"], "1")
        self.assertIn("Acme", item["source_vendor_labels"])

    def test_cross_month_collision_flags_every_affected_bucket(self):
        output = _summarize([_row(2, "A-CME"), _row(3, "ACME", month="2026-02-01")])
        self.assertEqual(len(output), 2)
        self.assertTrue(all(r["flag"] == "normalized_vendor_collision_review" for r in output))
        self.assertEqual([r["source_rows"] for r in output], ["2", "3"])

    def test_other_vendor_never_receives_collision_flag(self):
        output = _summarize([_row(2, "A-CME"), _row(3, "ACME"), _row(4, "BETA")])
        lookup = {r["vendor_key"]: r for r in output}
        self.assertEqual(lookup["BETA"]["flag"], "")
        self.assertEqual(lookup["BETA"]["vendor_label_variants"], "1")

    def test_source_vendor_labels_are_local_to_bucket_not_quadratic(self):
        output = _summarize([_row(2, "A-CME"), _row(3, "ACME", month="2026-02-01")])
        self.assertEqual(output[0]["source_vendor_labels"], "A-CME")
        self.assertEqual(output[1]["source_vendor_labels"], "ACME")

    def test_monthly_total_includes_categories_but_bucket_amount_does_not(self):
        output = _summarize([_row(2, amount="3.01", category="Parts"),
                             _row(3, amount="2.02", category="Travel")])
        self.assertEqual({r["category"]: r["amount"] for r in output},
                         {"Parts": "3.01", "Travel": "2.02"})
        self.assertEqual({r["vendor_month_total"] for r in output}, {"5.03"})
        self.assertEqual([r["source_rows"] for r in output], ["2", "3"])

    def test_unclassified_is_explicit(self):
        self.assertEqual(_summarize([_row(2, category="")])[0]["category"], "Uncategorized")

    def test_exact_double_baseline_is_reviewed_after_three_prior_months(self):
        data = [_row(2, month="2026-01-01"), _row(3, month="2026-02-01"),
                _row(4, month="2026-03-01"), _row(5, amount="20", month="2026-04-01")]
        output = _summarize(data)
        self.assertEqual([r["history_months"] for r in output], ["0", "1", "2", "3"])
        self.assertEqual(output[-1]["baseline_median"], "10.00")
        self.assertEqual(output[-1]["flag"], "review_spike")

    def test_spike_below_exact_double_not_flagged(self):
        data = [_row(2, month="2026-01-01"), _row(3, month="2026-02-01"),
                _row(4, month="2026-03-01"), _row(5, amount="19.99", month="2026-04-01")]
        self.assertEqual(_summarize(data)[-1]["flag"], "")

    def test_baseline_is_exact_and_can_contain_half_cent(self):
        data = [_row(2, amount="10.00", month="2026-01-01"),
                _row(3, amount="10.01", month="2026-02-01"),
                _row(4, amount="10.00", month="2026-03-01"),
                _row(5, amount="10.02", month="2026-04-01"),
                _row(6, amount="20.01", month="2026-05-01")]
        output = _summarize(data)
        self.assertEqual(output[-1]["baseline_median"], "10.005")
        self.assertEqual(output[-1]["flag"], "review_spike")

    def test_zero_baseline_does_not_generate_spike(self):
        data = [_row(2, amount="0", month="2026-01-01"),
                _row(3, amount="0", month="2026-02-01"),
                _row(4, amount="0", month="2026-03-01"),
                _row(5, amount="100", month="2026-04-01")]
        self.assertEqual(_summarize(data)[-1]["flag"], "")

    def test_refund_subtracts_without_float_drift(self):
        item = _summarize([_row(2, amount="0.10"), _row(3, amount="0.20"),
                           _row(4, amount="-0.05")])[0]
        self.assertEqual(item["amount"], "0.25")
        self.assertEqual(item["vendor_month_total"], "0.25")

    def test_combined_spike_and_vendor_collision_remain_visible(self):
        data = [_row(2, month="2026-01-01"), _row(3, month="2026-02-01"),
                _row(4, month="2026-03-01"),
                _row(5, "A-CME", amount="30", month="2026-04-01")]
        self.assertEqual(_summarize(data)[-1]["flag"],
                         "review_spike;normalized_vendor_collision_review")

    def test_months_are_sorted_independent_of_input_row_order(self):
        data = [_row(2, amount="20", month="2026-04-01"),
                _row(3, month="2026-03-01"), _row(4, month="2026-01-01"),
                _row(5, month="2026-02-01")]
        output = _summarize(data)
        self.assertEqual([r["month"] for r in output],
                         ["2026-01", "2026-02", "2026-03", "2026-04"])
        self.assertEqual(output[-1]["flag"], "review_spike")
        self.assertEqual(output[-1]["source_rows"], "2")

    def test_blank_normalized_vendor_blocks_report(self):
        with self.assertRaisesRegex(ValueError, "Blank vendor at row 2"):
            _summarize([_row(2, "!!!")])

    def test_amount_parser_failure_is_not_swallowed(self):
        with self.assertRaises(Exception):
            _summarize([_row(2, amount="not-money")])

    def test_deterministic_reexecution(self):
        records = [_row(2, "A-CME"), _row(3, "ACME")]
        self.assertEqual(_summarize(records), _summarize(records))


if __name__ == "__main__":
    unittest.main()
