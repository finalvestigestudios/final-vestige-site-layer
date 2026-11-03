"""R157 zero-skip inventory: independent SpendMap review-history verification."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_first_observed_month_has_no_baseline",
    "test_three_observed_months_do_not_have_baseline",
    "test_fourth_observed_month_detects_spike",
    "test_below_double_threshold_is_not_spike",
    "test_exact_double_threshold_is_review",
    "test_negative_median_does_not_create_spike_flag",
    "test_four_prior_months_keep_half_cent_median",
    "test_missing_calendar_months_are_not_interpolated",
    "test_unsorted_source_dates_use_chronological_baseline",
    "test_category_spike_hidden_by_flat_vendor_total",
    "test_category_only_two_prior_months_no_baseline",
    "test_vendor_collision_across_months",
    "test_ascii_case_does_not_invent_collision",
    "test_collision_and_spike_flags_are_both_required",
    "test_three_distinct_vendor_spellings_keep_variant_count",
    "test_history_count_tamper_holds",
    "test_median_tamper_holds",
    "test_vendor_spike_suppression_holds",
    "test_forged_vendor_spike_holds",
    "test_category_history_count_tamper_holds",
    "test_category_median_tamper_holds",
    "test_category_spike_suppression_holds",
    "test_forged_category_review_holds",
    "test_variant_count_tamper_holds",
    "test_missing_required_review_column_holds",
    "test_external_decimal_precision_cannot_suppress_spike",
    "test_multiline_csv_preserves_history_and_source_custody",
    "test_input_and_report_bytes_not_rewritten",
    "test_cli_holds_without_leaking_customer_amount_or_name",
))


def flatten(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from flatten(case)
        else:
            yield case


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_spend_review_history_r157.py")
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED
                or any(type(case).__name__ != "SpendReviewR157" for case in cases)):
            raise ValueError("R157 strict test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        print(f"R157 SpendMap independent review history {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R157 SpendMap historical review HOLD: required tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
