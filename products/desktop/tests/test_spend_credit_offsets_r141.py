"""R141 SpendMap: gross-charge/credit netting visibility, real synthetic CSV only.

No customer information, no network dependency and no compliance automation.
All exported findings require independent human review.
"""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from decimal import Inexact, Rounded, localcontext
from pathlib import Path

from fvs_suite import engine


class SpendCreditOffsetR141(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="fvs-r141-spend-")
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.input = self.root / "synthetic-spend.csv"

    def source(self, rows):
        with self.input.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(rows)
        return self.input

    def report(self):
        output = engine.spend_map(self.input, self.root)[0]
        with output.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return list(reader), tuple(reader.fieldnames)

    @staticmethod
    def row(amount, month="01", category="Parts", vendor="ACME", note=""):
        return (vendor, amount, f"2026-{month}-01", category, note)

    @staticmethod
    def pick(rows, *, month="2026-01", category="Parts", vendor="ACME"):
        matches = [r for r in rows if (r["vendor_key"], r["month"], r["category"])
                   == (vendor, month, category)]
        if len(matches) != 1:
            raise AssertionError("Expected one synthetic vendor/month/category bucket")
        return matches[0]

    def test_mixed_sign_bucket_reports_exact_gross_and_net(self):
        self.source([self.row("150.00"), self.row("-140.00")])
        item = self.pick(self.report()[0])
        self.assertEqual((item["amount"], item["gross_charges"], item["gross_credits"]),
                         ("10.00", "150.00", "140.00"))
        self.assertEqual(item["credit_offset_review"], "review_mixed_sign_offset")

    def test_zero_net_no_longer_hides_two_sided_activity(self):
        self.source([self.row("250"), self.row("-250")])
        item = self.pick(self.report()[0])
        self.assertEqual(item["amount"], "0.00")
        self.assertEqual(item["gross_charges"], "250.00")
        self.assertEqual(item["gross_credits"], "250.00")
        self.assertEqual(item["credit_offset_review"], "review_mixed_sign_offset")

    def test_all_positive_rows_do_not_flag_offsets(self):
        self.source([self.row("1.20"), self.row("2.30")])
        item = self.pick(self.report()[0])
        self.assertEqual((item["amount"], item["gross_charges"],
                          item["gross_credits"], item["credit_offset_review"]),
                         ("3.50", "3.50", "0.00", ""))

    def test_all_negative_credit_only_not_mislabeled_mixed(self):
        self.source([self.row("-1.20"), self.row("-2.30")])
        item = self.pick(self.report()[0])
        self.assertEqual((item["amount"], item["gross_charges"],
                          item["gross_credits"], item["credit_offset_review"]),
                         ("-3.50", "0.00", "3.50", ""))

    def test_zero_only_neutral_no_false_flag(self):
        self.source([self.row("0"), self.row("0.00")])
        item = self.pick(self.report()[0])
        self.assertEqual((item["gross_charges"], item["gross_credits"],
                          item["credit_offset_review"]), ("0.00", "0.00", ""))

    def test_negative_zero_is_not_a_credit(self):
        self.source([self.row("-0.00"), self.row("2.00")])
        item = self.pick(self.report()[0])
        self.assertEqual(item["gross_charges"], "2.00")
        self.assertEqual(item["gross_credits"], "0.00")
        self.assertEqual(item["credit_offset_review"], "")

    def test_multiple_rows_gross_sum_is_exact(self):
        self.source([self.row("19.99"), self.row("0.01"), self.row("-4.99"),
                     self.row("-0.01"), self.row("0.00")])
        item = self.pick(self.report()[0])
        self.assertEqual((item["gross_charges"], item["gross_credits"], item["amount"]),
                         ("20.00", "5.00", "15.00"))

    def test_credits_do_not_leak_into_another_month(self):
        self.source([self.row("50.00", "01"), self.row("-10.00", "02")])
        rows, _ = self.report()
        jan = self.pick(rows, month="2026-01")
        feb = self.pick(rows, month="2026-02")
        self.assertEqual((jan["gross_credits"], feb["gross_charges"]), ("0.00", "0.00"))
        self.assertEqual((jan["credit_offset_review"], feb["credit_offset_review"]), ("", ""))

    def test_credits_do_not_leak_into_another_category(self):
        self.source([self.row("100", category="Parts"),
                     self.row("-90", category="Services")])
        rows, _ = self.report()
        parts = self.pick(rows, category="Parts")
        services = self.pick(rows, category="Services")
        self.assertEqual((parts["gross_credits"], services["gross_charges"]),
                         ("0.00", "0.00"))
        self.assertEqual(parts["credit_offset_review"], "")
        self.assertEqual(services["credit_offset_review"], "")

    def test_credits_do_not_leak_into_another_vendor(self):
        self.source([self.row("30", vendor="ACME"),
                     self.row("-25", vendor="OTHER")])
        rows, _ = self.report()
        self.assertEqual(self.pick(rows)["gross_credits"], "0.00")
        self.assertEqual(self.pick(rows, vendor="OTHER")["gross_charges"], "0.00")

    def test_normalized_vendor_collision_remains_a_review_flag(self):
        self.source([self.row("100", vendor="A-CME"),
                     self.row("-90", vendor="ACME")])
        item = self.pick(self.report()[0])
        self.assertEqual(item["gross_credits"], "90.00")
        self.assertEqual(item["credit_offset_review"], "review_mixed_sign_offset")
        self.assertEqual(item["flag"], "normalized_vendor_collision_review")
        self.assertEqual(item["vendor_label_variants"], "2")

    def test_existing_spike_flags_survive_netting(self):
        self.source([self.row("10.00", month) for month in ("01", "02", "03")]
                    + [self.row("50.00", "04"), self.row("-20.00", "04")])
        rows, _ = self.report()
        item = self.pick(rows, month="2026-04")
        self.assertEqual((item["amount"], item["flag"], item["category_review_flag"]),
                         ("30.00", "review_spike", "review_category_spike"))
        self.assertEqual(item["credit_offset_review"], "review_mixed_sign_offset")

    def test_category_spike_baseline_remains_net_based(self):
        self.source([self.row("10.00", month) for month in ("01", "02", "03")]
                    + [self.row("50.00", "04"), self.row("-40.00", "04")])
        item = self.pick(self.report()[0], month="2026-04")
        self.assertEqual(item["category_baseline_median"], "10.00")
        self.assertEqual(item["category_review_flag"], "")
        self.assertEqual(item["credit_offset_review"], "review_mixed_sign_offset")

    def test_monthly_vendor_total_still_uses_nets_across_categories(self):
        self.source([self.row("50.00", category="Parts"),
                     self.row("-20.00", category="Parts"),
                     self.row("10.00", category="Services")])
        rows, _ = self.report()
        self.assertEqual(self.pick(rows)["vendor_month_total"], "40.00")
        self.assertEqual(self.pick(rows, category="Services")["vendor_month_total"],
                         "40.00")

    def test_multiline_csv_physical_source_lines_and_sha_are_unchanged(self):
        self.source([self.row("100", note="two\nphysical lines"),
                     self.row("-90", note="one line")])
        original = self.input.read_bytes()
        item = self.pick(self.report()[0])
        self.assertEqual(item["source_rows"], "2;4")
        self.assertEqual(item["source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(self.input.read_bytes(), original)

    def test_one_trillion_bound_aggregates_without_float_rounding(self):
        self.source([self.row("1000000000000.00"),
                     self.row("-999999999999.99")])
        item = self.pick(self.report()[0])
        self.assertEqual((item["amount"], item["gross_charges"], item["gross_credits"]),
                         ("0.01", "1000000000000.00", "999999999999.99"))

    def test_very_low_trapping_decimal_context_does_not_corrupt_money(self):
        self.source([self.row("1000000000000.00"),
                     self.row("-999999999999.99")])
        with localcontext() as ctx:
            ctx.prec = 2
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            item = self.pick(self.report()[0])
            self.assertEqual(ctx.prec, 2)
        self.assertEqual(item["amount"], "0.01")
        self.assertEqual(item["gross_credits"], "999999999999.99")

    def test_invalid_money_fails_before_creating_report(self):
        self.source([self.row("10"), self.row("1e999")])
        with self.assertRaises(ValueError):
            engine.spend_map(self.input, self.root)
        self.assertEqual(list(self.root.glob("spend-map-*.csv")), [])

    def test_private_invalid_source_value_not_in_exception(self):
        private = "secret-amount-123456789"
        self.source([self.row(private)])
        with self.assertRaises(ValueError) as caught:
            engine.spend_map(self.input, self.root)
        self.assertNotIn(private, str(caught.exception))
        self.assertEqual(list(self.root.glob("spend-map-*.csv")), [])

    def test_export_headers_declare_all_new_review_columns(self):
        self.source([])
        rows, cols = self.report()
        self.assertEqual(rows, [])
        self.assertEqual(cols, (
            "vendor_key", "month", "category", "amount", "flag",
            "vendor_month_total", "baseline_median", "history_months",
            "category_history_months", "category_baseline_median", "category_review_flag",
            "gross_charges", "gross_credits", "credit_offset_review",
            "vendor_month_evidence_rows", "vendor_month_evidence_count",
            "vendor_month_evidence_omitted",
            "vendor_month_gross_charges", "vendor_month_gross_credits",
            "vendor_month_offset_review",
            "source_rows", "source_vendor_labels", "vendor_label_variants", "source_sha256",
        ))

    def test_results_repeat_deterministically(self):
        self.source([self.row("50"), self.row("-10"), self.row("2")])
        first, cols_a = self.report()
        second, cols_b = self.report()
        self.assertEqual(first, second)
        self.assertEqual(cols_a, cols_b)

    def test_formula_vendor_label_still_escaped(self):
        self.source([self.row("8.00", vendor="=ACME"),
                     self.row("-2.00", vendor="=ACME")])
        item = self.pick(self.report()[0])
        self.assertEqual(item["source_vendor_labels"], "'=ACME")
        self.assertEqual(item["credit_offset_review"], "review_mixed_sign_offset")

    def test_uncategorized_bucket_still_retains_offsets(self):
        self.source([self.row("4.00", category=""),
                     self.row("-1.00", category="")])
        item = self.pick(self.report()[0], category="Uncategorized")
        self.assertEqual(item["amount"], "3.00")
        self.assertEqual(item["credit_offset_review"], "review_mixed_sign_offset")


if __name__ == "__main__":
    unittest.main()
