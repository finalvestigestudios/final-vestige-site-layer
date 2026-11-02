"""R141 strict source-owned, no-skip SpendMap credit-offset regression gate."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_mixed_sign_bucket_reports_exact_gross_and_net",
    "test_zero_net_no_longer_hides_two_sided_activity",
    "test_all_positive_rows_do_not_flag_offsets",
    "test_all_negative_credit_only_not_mislabeled_mixed",
    "test_zero_only_neutral_no_false_flag",
    "test_negative_zero_is_not_a_credit",
    "test_multiple_rows_gross_sum_is_exact",
    "test_credits_do_not_leak_into_another_month",
    "test_credits_do_not_leak_into_another_category",
    "test_credits_do_not_leak_into_another_vendor",
    "test_normalized_vendor_collision_remains_a_review_flag",
    "test_existing_spike_flags_survive_netting",
    "test_category_spike_baseline_remains_net_based",
    "test_monthly_vendor_total_still_uses_nets_across_categories",
    "test_multiline_csv_physical_source_lines_and_sha_are_unchanged",
    "test_one_trillion_bound_aggregates_without_float_rounding",
    "test_very_low_trapping_decimal_context_does_not_corrupt_money",
    "test_invalid_money_fails_before_creating_report",
    "test_private_invalid_source_value_not_in_exception",
    "test_export_headers_declare_all_new_review_columns",
    "test_results_repeat_deterministically",
    "test_formula_vendor_label_still_escaped",
    "test_uncategorized_bucket_still_retains_offsets",
))


def flatten(suite):
    for member in suite:
        if isinstance(member, unittest.TestSuite):
            yield from flatten(member)
        else:
            yield member


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_spend_credit_offsets_r141.py",
        )
        actual = [case._testMethodName for case in flatten(suite)]
        if len(actual) != len(EXPECTED) or set(actual) != EXPECTED:
            raise ValueError("R141 source regression test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R141 SpendMap credit offsets {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R141 SpendMap credit offsets HOLD: required tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
