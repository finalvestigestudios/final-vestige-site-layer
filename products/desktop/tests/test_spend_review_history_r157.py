"""R157 synthetic tests: historical spikes and vendor-collision review custody.

No customer records. Every report is generated from real, temporary CSV files.
"""
from __future__ import annotations

import contextlib
import csv
import io
import tempfile
import unittest
from decimal import Inexact, getcontext, setcontext
from pathlib import Path

from fvs_suite import engine
from fvs_suite.spend_evidence_verify import main, verify_membership


class SpendReviewR157(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="fvs-r157-synthetic-")
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.source = self.folder / "source.csv"
        self.report = self.folder / "report.csv"

    @staticmethod
    def row(amount="10.00", vendor="ACME", month=1, category="Parts", note=""):
        return (vendor, amount, f"2026-{month:02d}-01", category, note)

    def write(self, rows):
        with self.source.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("vendor", "amount", "date", "category", "note"))
            writer.writerows(rows)
        self.report = Path(engine.spend_map(self.source, self.folder)[0])
        return verify_membership(self.source, self.report)

    def report_rows(self):
        with self.report.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            return list(reader.fieldnames), list(reader)

    def modify(self, field, value, index=0, remove_header=False):
        fields, rows = self.report_rows()
        if remove_header:
            fields.remove(field)
        else:
            rows[index][field] = value
        with self.report.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def review_rows(self, rows):
        self.write(rows)
        return { (r["vendor_key"], r["month"], r["category"]): r
                 for r in self.report_rows()[1] }

    def test_first_observed_month_has_no_baseline(self):
        rows = self.review_rows([self.row()])
        row = next(iter(rows.values()))
        self.assertEqual((row["history_months"], row["baseline_median"], row["flag"]), ("0", "", ""))

    def test_three_observed_months_do_not_have_baseline(self):
        rows = self.review_rows([self.row("10", month=m) for m in (1, 2, 3)])
        self.assertTrue(all(r["baseline_median"] == "" for r in rows.values()))
        self.assertTrue(all(r["flag"] == "" for r in rows.values()))

    def test_fourth_observed_month_detects_spike(self):
        rows = self.review_rows([self.row("10", month=m) for m in (1, 2, 3)] +
                                [self.row("20", month=4)])
        self.assertEqual(rows["ACME", "2026-04", "Parts"]["flag"], "review_spike")

    def test_below_double_threshold_is_not_spike(self):
        rows = self.review_rows([self.row("10", month=m) for m in (1, 2, 3)] +
                                [self.row("19.99", month=4)])
        self.assertEqual(rows["ACME", "2026-04", "Parts"]["flag"], "")

    def test_exact_double_threshold_is_review(self):
        rows = self.review_rows([self.row("10", month=m) for m in (1, 2, 3)] +
                                [self.row("20", month=4)])
        self.assertEqual(rows["ACME", "2026-04", "Parts"]["baseline_median"], "10.00")

    def test_negative_median_does_not_create_spike_flag(self):
        rows = self.review_rows([self.row("-10", month=m) for m in (1, 2, 3)] +
                                [self.row("150", month=4)])
        self.assertEqual(rows["ACME", "2026-04", "Parts"]["flag"], "")

    def test_four_prior_months_keep_half_cent_median(self):
        rows = self.review_rows([self.row(amount, month=m) for m, amount in
                                 enumerate(("0.01", "0.01", "0.02", "0.02", "0.03"), start=1)])
        final = rows["ACME", "2026-05", "Parts"]
        self.assertEqual(final["baseline_median"], "0.015")
        self.assertEqual(final["category_baseline_median"], "0.015")
        self.assertEqual(final["category_review_flag"], "review_category_spike")

    def test_missing_calendar_months_are_not_interpolated(self):
        rows = [
            ("ACME", "10", "2024-01-01", "Parts", ""),
            ("ACME", "10", "2024-07-01", "Parts", ""),
            ("ACME", "10", "2025-04-01", "Parts", ""),
            ("ACME", "20", "2026-12-01", "Parts", ""),
        ]
        result = self.review_rows(rows)
        self.assertEqual(result["ACME", "2026-12", "Parts"]["history_months"], "3")

    def test_unsorted_source_dates_use_chronological_baseline(self):
        rows = self.review_rows([self.row("20", month=4)] +
                                [self.row("10", month=m) for m in (3, 1, 2)])
        self.assertEqual(rows["ACME", "2026-04", "Parts"]["flag"], "review_spike")

    def test_category_spike_hidden_by_flat_vendor_total(self):
        records = []
        for month in (1, 2, 3, 4):
            records.extend([self.row("30" if month == 4 else "10", month=month, category="Parts"),
                            self.row("70" if month == 4 else "90", month=month, category="Services")])
        rows = self.review_rows(records)
        final = rows["ACME", "2026-04", "Parts"]
        self.assertEqual(final["flag"], "")
        self.assertEqual(final["category_review_flag"], "review_category_spike")

    def test_category_only_two_prior_months_no_baseline(self):
        records = [self.row("10", month=1, category="Parts"),
                   self.row("10", month=2, category="Other"),
                   self.row("10", month=3, category="Parts"),
                   self.row("20", month=4, category="Parts")]
        rows = self.review_rows(records)
        self.assertEqual(rows["ACME", "2026-04", "Parts"]["category_history_months"], "2")
        self.assertEqual(rows["ACME", "2026-04", "Parts"]["category_review_flag"], "")

    def test_vendor_collision_across_months(self):
        rows = self.review_rows([self.row(vendor="A-CME", month=1),
                                 self.row(vendor="ACME", month=2)])
        self.assertTrue(all("normalized_vendor_collision_review" in r["flag"]
                            for r in rows.values()))

    def test_ascii_case_does_not_invent_collision(self):
        rows = self.review_rows([self.row(vendor="AcMe", month=1),
                                 self.row(vendor="aCmE", month=2)])
        self.assertTrue(all(r["vendor_label_variants"] == "1" for r in rows.values()))

    def test_collision_and_spike_flags_are_both_required(self):
        rows = self.review_rows([self.row("10", vendor="A-CME", month=m) for m in (1, 2, 3)]
                                + [self.row("20", vendor="ACME", month=4)])
        final = rows["ACME", "2026-04", "Parts"]
        self.assertEqual(final["flag"], "review_spike;normalized_vendor_collision_review")

    def test_three_distinct_vendor_spellings_keep_variant_count(self):
        rows = self.review_rows([self.row(vendor="A-CME", month=1),
                                 self.row(vendor="ACME", month=2),
                                 self.row(vendor="AC.ME", month=3)])
        self.assertTrue(all(r["vendor_label_variants"] == "3" for r in rows.values()))

    def test_history_count_tamper_holds(self):
        self.write([self.row("10", month=m) for m in (1, 2, 3, 4)])
        self.modify("history_months", "0", index=3)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_median_tamper_holds(self):
        self.write([self.row("10", month=m) for m in (1, 2, 3, 4)])
        self.modify("baseline_median", "0", index=3)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_vendor_spike_suppression_holds(self):
        self.write([self.row("10", month=m) for m in (1, 2, 3)] +
                   [self.row("20", month=4)])
        self.modify("flag", "", index=3)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_forged_vendor_spike_holds(self):
        self.write([self.row()])
        self.modify("flag", "review_spike")
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_category_history_count_tamper_holds(self):
        self.write([self.row("10", month=m) for m in (1, 2, 3, 4)])
        self.modify("category_history_months", "999", index=3)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_category_median_tamper_holds(self):
        self.write([self.row("10", month=m) for m in (1, 2, 3, 4)])
        self.modify("category_baseline_median", "1.00", index=3)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_category_spike_suppression_holds(self):
        self.write([self.row("10", month=m) for m in (1, 2, 3)] +
                   [self.row("20", month=4)])
        self.modify("category_review_flag", "", index=3)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_forged_category_review_holds(self):
        self.write([self.row()])
        self.modify("category_review_flag", "review_category_spike")
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_variant_count_tamper_holds(self):
        self.write([self.row()])
        self.modify("vendor_label_variants", "9")
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_missing_required_review_column_holds(self):
        self.write([self.row()])
        self.modify("category_review_flag", "", remove_header=True)
        with self.assertRaises(ValueError):
            verify_membership(self.source, self.report)

    def test_external_decimal_precision_cannot_suppress_spike(self):
        self.write([self.row("100.01", month=m) for m in (1, 2, 3)] +
                   [self.row("200.02", month=4)])
        previous = getcontext().copy()
        try:
            getcontext().prec = 3
            getcontext().traps[Inexact] = True
            self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 4)
        finally:
            setcontext(previous)

    def test_multiline_csv_preserves_history_and_source_custody(self):
        self.write([self.row("10", month=1, note="line 1\nline 2")] +
                   [self.row("10", month=m) for m in (2, 3)] +
                   [self.row("20", month=4)])
        self.assertEqual(verify_membership(self.source, self.report).buckets_verified, 4)

    def test_input_and_report_bytes_not_rewritten(self):
        self.write([self.row("10", month=m) for m in (1, 2, 3, 4)])
        before = (self.source.read_bytes(), self.report.read_bytes())
        verify_membership(self.source, self.report)
        self.assertEqual((self.source.read_bytes(), self.report.read_bytes()), before)

    def test_cli_holds_without_leaking_customer_amount_or_name(self):
        self.write([self.row("987654.32", vendor="PRIVATE-CLIENT-873")])
        self.modify("flag", "review_spike")
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(["--source", str(self.source), "--report", str(self.report)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("HOLD", stderr.getvalue())
        self.assertNotIn("PRIVATE-CLIENT", stderr.getvalue())
        self.assertNotIn("987654", stderr.getvalue())
        self.assertNotIn(str(self.folder), stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
