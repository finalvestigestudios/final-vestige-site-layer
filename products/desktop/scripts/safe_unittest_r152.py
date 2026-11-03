"""R152 source-owned, no-skip, privacy-safe fixed-inventory SpendMap gate."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_cross_category_offset_now_visible_both_rows",
    "test_matching_net_and_hidden_cross_category_gross",
    "test_single_category_mixed_sign_keeps_existing_flag",
    "test_positive_only_has_no_monthly_offset",
    "test_credit_only_has_no_monthly_offset",
    "test_zero_only_has_no_monthly_offset",
    "test_negative_zero_not_a_credit",
    "test_multiple_categories_sum_exactly",
    "test_vendor_isolation",
    "test_month_isolation",
    "test_category_month_offset_does_not_create_bucket_offset",
    "test_normalized_vendor_rows_are_reviewable",
    "test_uncategorized_credit_is_included",
    "test_vendor_net_baseline_preserved",
    "test_category_spike_logic_preserved",
    "test_sha256_matches_original_import",
    "test_import_is_not_modified",
    "test_physical_csv_lines_with_multiline_field",
    "test_large_decimal_money_exact_and_signed",
    "test_hostile_decimal_context_does_not_round",
    "test_deterministic_report_content",
    "test_invalid_amount_fails_without_report",
    "test_formula_like_vendor_label_is_escaped",
    "test_schema_includes_three_explicit_monthly_evidence_fields",
    "test_no_premium_approval_or_fraud_claim_in_signal",
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
            pattern="test_spend_vendor_month_r152.py")
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED or
                any(type(case).__name__ != "SpendVendorMonthR152"
                    for case in cases)):
            raise ValueError("R152 fixed regression inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R152 SpendMap vendor-month gross {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R152 SpendMap vendor-month gross HOLD: required tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
