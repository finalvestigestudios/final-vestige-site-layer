"""R135: SpendMap separate category outlier evidence; synthetic real CSV coverage."""
from __future__ import annotations

import csv
import hashlib
import tempfile
import unittest
from decimal import Decimal, Inexact, Rounded, localcontext
from pathlib import Path

from fvs_suite import engine
from fvs_suite.spend_analysis import summarize_spend


def item(vendor, amount, month, category="Parts", *, day=1, note=""):
    return (vendor, amount, f"2026-{month:02d}-{day:02d}", category, note)


class SpendCategoryBaselineR135(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-r135-spend-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source_path = self.root / "synthetic-spend.csv"

    def source(self, items):
        with self.source_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(items)
        return self.source_path

    def report(self):
        path = engine.spend_map(self.source_path, self.root)[0]
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return list(reader), tuple(reader.fieldnames)

    @staticmethod
    def pick(rows, month, category="Parts", vendor="ACME"):
        matching = [row for row in rows if row["vendor_key"] == vendor
                    and row["month"] == f"2026-{month:02d}"
                    and row["category"] == category]
        if len(matching) != 1:
            raise AssertionError("Expected one synthetic SpendMap report bucket")
        return matching[0]

    def test_category_spike_masked_by_other_category(self):
        self.source([
            entry
            for month in (1, 2, 3)
            for entry in (item("ACME", "10", month, "Parts"),
                          item("ACME", "90", month, "Services"))
        ] + [item("ACME", "30", 4, "Parts"),
             item("ACME", "70", 4, "Services")])
        rows, _ = self.report()
        parts = self.pick(rows, 4, "Parts")
        self.assertEqual(parts["flag"], "")
        self.assertEqual(parts["category_review_flag"], "review_category_spike")
        self.assertEqual(parts["category_baseline_median"], "10.00")
        self.assertEqual(parts["category_history_months"], "3")
        self.assertEqual(parts["vendor_month_total"], "100.00")
        self.assertEqual(self.pick(rows, 4, "Services")["category_review_flag"], "")

    def test_vendor_spike_does_not_imply_category_spike(self):
        self.source([item("ACME", "10", month) for month in (1, 2, 3)]
                    + [item("ACME", "10", 4), item("ACME", "40", 4, "New")])
        rows, _ = self.report()
        parts, new = self.pick(rows, 4), self.pick(rows, 4, "New")
        self.assertEqual(parts["flag"], "review_spike")
        self.assertEqual(parts["category_review_flag"], "")
        self.assertEqual(new["category_review_flag"], "")
        self.assertEqual(new["category_history_months"], "0")
        self.assertEqual(new["category_baseline_median"], "")

    def test_two_categories_have_independent_history(self):
        self.source([
            row for month in (1, 2, 3)
            for row in (item("ACME", "10", month),
                        item("ACME", "1", month, "Other"))
        ] + [item("ACME", "10", 4), item("ACME", "3", 4, "Other")])
        rows, _ = self.report()
        self.assertEqual(self.pick(rows, 4, "Parts")["category_review_flag"], "")
        other = self.pick(rows, 4, "Other")
        self.assertEqual(other["category_review_flag"], "review_category_spike")
        self.assertEqual(other["flag"], "")
        self.assertEqual(other["category_baseline_median"], "1.00")

    def test_vendor_isolation_with_identical_category(self):
        self.source([
            row for month in (1, 2, 3)
            for row in (item("ACME", "10", month),
                        item("OTHER", "50", month))
        ] + [item("ACME", "20", 4), item("OTHER", "60", 4)])
        rows, _ = self.report()
        self.assertEqual(self.pick(rows, 4)["category_review_flag"], "review_category_spike")
        self.assertEqual(self.pick(rows, 4, vendor="OTHER")["category_review_flag"], "")
        self.assertEqual(self.pick(rows, 4, vendor="OTHER")["category_baseline_median"],
                         "50.00")

    def test_insufficient_category_history_despite_vendor_history(self):
        self.source([item("ACME", "10", 1),
                     item("ACME", "2", 2, "Other"),
                     item("ACME", "10", 3),
                     item("ACME", "50", 4)])
        rows, _ = self.report()
        fourth = self.pick(rows, 4)
        self.assertEqual(fourth["history_months"], "3")
        self.assertEqual(fourth["category_history_months"], "2")
        self.assertEqual(fourth["category_baseline_median"], "")
        self.assertEqual(fourth["category_review_flag"], "")

    def test_exact_half_cent_boundary_qualifies(self):
        self.source([item("ACME", amount, i)
                     for i, amount in enumerate(
                         ("10.00", "10.01", "10.00", "10.01", "20.01"), 1)])
        rows, _ = self.report()
        last = self.pick(rows, 5)
        self.assertEqual(last["category_baseline_median"], "10.005")
        self.assertEqual(last["category_history_months"], "4")
        self.assertEqual(last["category_review_flag"], "review_category_spike")

    def test_one_cent_below_exact_boundary_is_not_flagged(self):
        self.source([item("ACME", amount, i)
                     for i, amount in enumerate(
                         ("10.00", "10.01", "10.00", "10.01", "20.00"), 1)])
        rows, _ = self.report()
        last = self.pick(rows, 5)
        self.assertEqual(last["category_baseline_median"], "10.005")
        self.assertEqual(last["category_review_flag"], "")

    def test_nonpositive_prior_baseline_suppresses_spike(self):
        self.source([item("ACME", amount, i)
                     for i, amount in enumerate(("-10", "0", "-1", "100"), 1)])
        rows, _ = self.report()
        last = self.pick(rows, 4)
        self.assertEqual(last["category_baseline_median"], "-1.00")
        self.assertEqual(last["category_review_flag"], "")

    def test_sparse_calendar_does_not_invent_months(self):
        self.source([item("ACME", "10", month) for month in (1, 3, 5)]
                    + [item("ACME", "21", 12)])
        rows, _ = self.report()
        last = self.pick(rows, 12)
        self.assertEqual(last["category_history_months"], "3")
        self.assertEqual(last["category_baseline_median"], "10.00")
        self.assertEqual(last["category_review_flag"], "review_category_spike")

    def test_case_distinct_category_labels_are_not_silently_merged(self):
        self.source([item("ACME", "10", month) for month in (1, 2, 3)]
                    + [item("ACME", "30", 4, "parts")])
        rows, _ = self.report()
        new = self.pick(rows, 4, "parts")
        self.assertEqual(new["category_history_months"], "0")
        self.assertEqual(new["category_review_flag"], "")
        self.assertEqual(new["category_baseline_median"], "")

    def test_legacy_vendor_flag_remains_unchanged(self):
        self.source([item("ACME", "10", m) for m in (1, 2, 3)]
                    + [item("ACME", "30", 4)])
        rows, _ = self.report()
        last = self.pick(rows, 4)
        self.assertEqual(last["flag"], "review_spike")
        self.assertEqual(last["category_review_flag"], "review_category_spike")

    def test_vendor_normalization_collision_stays_reviewable(self):
        self.source([item("A-CME", "10", 1), item("ACME", "10", 2),
                     item("ACME", "10", 3), item("ACME", "30", 4)])
        rows, _ = self.report()
        last = self.pick(rows, 4)
        self.assertEqual(last["flag"],
                         "review_spike;normalized_vendor_collision_review")
        self.assertEqual(last["category_review_flag"], "review_category_spike")
        self.assertEqual(last["vendor_label_variants"], "2")

    def test_preserves_physical_rows_and_original_source_sha(self):
        self.source([item("ACME", "1.25", 1, note="two\nphysical lines"),
                     item("ACME", "1.75", 1)])
        original = self.source_path.read_bytes()
        rows, _ = self.report()
        self.assertEqual(rows[0]["source_rows"], "2;4")
        self.assertEqual(rows[0]["source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(self.source_path.read_bytes(), original)

    def test_result_is_deterministic_across_runs(self):
        self.source([item("ACME", "10", i) for i in (1, 2, 3, 4)])
        first, columns = self.report()
        second, columns2 = self.report()
        self.assertEqual(first, second)
        self.assertEqual(columns, columns2)

    def test_invalid_money_leaves_no_partial_report(self):
        self.source([item("ACME", "1", 1), item("ACME", "NaN", 2)])
        with self.assertRaises(ValueError):
            engine.spend_map(self.source_path, self.root)
        self.assertEqual(list(self.root.glob("spend-map-*.csv")), [])

    def test_empty_report_has_complete_new_schema(self):
        self.source([])
        rows, columns = self.report()
        self.assertEqual(rows, [])
        self.assertEqual(columns, (
            "vendor_key", "month", "category", "amount", "flag",
            "vendor_month_total", "baseline_median", "history_months",
            "category_history_months", "category_baseline_median", "category_review_flag",
            "gross_charges", "gross_credits", "credit_offset_review",
            "vendor_month_evidence_rows", "vendor_month_evidence_count",
            "vendor_month_evidence_omitted",
            "vendor_month_gross_charges", "vendor_month_gross_credits",
            "vendor_month_offset_review",
            "source_rows", "source_vendor_labels", "vendor_label_variants",
            "source_sha256",
        ))

    def test_hostile_decimal_context_preserves_evidence(self):
        self.source([item("ACME", amount, i)
                     for i, amount in enumerate(
                         ("10.00", "10.01", "10.00", "10.01", "20.01"), 1)])
        with localcontext() as ctx:
            ctx.prec = 3
            ctx.traps[Inexact] = True
            ctx.traps[Rounded] = True
            rows, _ = self.report()
            self.assertEqual(ctx.prec, 3)
        self.assertEqual(self.pick(rows, 5)["category_baseline_median"], "10.005")
        self.assertEqual(self.pick(rows, 5)["category_review_flag"], "review_category_spike")


if __name__ == "__main__":
    unittest.main()
