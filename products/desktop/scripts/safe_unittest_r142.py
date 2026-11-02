"""R142 strict, source-owned, zero-skip invoice candidate-evidence regression gate."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_exact_equal_same_day_measures_zero",
    "test_exact_amount_increase_is_signed_b_minus_a",
    "test_exact_amount_decrease_is_signed_b_minus_a",
    "test_positive_invoice_and_negative_credit_receive_review",
    "test_negative_credit_and_positive_invoice_receive_review",
    "test_zero_to_negative_is_not_opposing_signed_review",
    "test_negative_zero_not_reviewed_as_credit",
    "test_equal_negative_amounts_are_not_opposing",
    "test_near_candidate_has_zero_delta_and_seven_day_gap",
    "test_near_different_amount_not_misclassified",
    "test_near_opposing_amount_not_misclassified",
    "test_zero_day_window_preserves_same_day_measurements",
    "test_exact_gap_independent_of_zero_day_window",
    "test_distant_exact_review_respects_custom_window",
    "test_calendar_leap_day_gap",
    "test_source_half_cent_rounding_matches_display_delta",
    "test_maximum_amounts_retained_under_decimal_context",
    "test_hostile_decimal_precision_and_traps_do_not_change_delta",
    "test_multiline_physical_rows_and_source_sha",
    "test_report_repeats_identically_with_stable_candidate_ref",
    "test_formula_vendor_still_spreadsheet_escaped",
    "test_invalid_private_date_fails_before_report",
    "test_invalid_private_amount_fails_before_report",
    "test_rejected_window_never_writes",
    "test_header_schema_and_unchanged_provenance_tail",
    "test_normalized_invoice_review_flag_still_present",
    "test_opposite_sign_flag_combines_with_distant_date_review",
    "test_many_exact_identifiers_anchor_stays_stable",
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
            pattern="test_invoice_candidate_evidence_r142.py")
        actual = [case._testMethodName for case in flatten(suite)]
        if len(actual) != len(EXPECTED) or set(actual) != EXPECTED:
            raise ValueError("R142 invoice test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = result.wasSuccessful() and result.testsRun == len(EXPECTED) and (
            not result.skipped and not result.unexpectedSuccesses)
        print(f"R142 invoice review evidence {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R142 invoice review evidence HOLD: required tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
