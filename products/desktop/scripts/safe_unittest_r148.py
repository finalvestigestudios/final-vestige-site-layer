"""R148 source-owned LedgerDiff gross-flow method gate: zero skips/failures."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_simple_identical_charge_remains_matched",
    "test_simple_identical_credit_remains_matched",
    "test_hidden_left_offset_is_explicit_review_not_matched",
    "test_hidden_right_offset_is_explicit_review",
    "test_zero_net_cancellation_cannot_appear_matched",
    "test_equal_net_both_sides_different_gross",
    "test_equal_gross_reordered_transactions_do_not_flag",
    "test_same_positive_gross_different_row_counts_does_not_flag",
    "test_missing_left_is_not_misclassified_as_gross_mismatch",
    "test_missing_right_is_not_misclassified_as_gross_mismatch",
    "test_unequal_net_preserves_variance_without_duplicate_gross_flag",
    "test_unequal_net_duplicates_preserve_existing_flags",
    "test_negative_zero_is_not_credit_movement",
    "test_zero_plus_charge_does_not_change_gross",
    "test_cent_precision_is_exact_across_credits",
    "test_one_trillion_boundary_keeps_decimal_cents",
    "test_low_precision_and_rounding_traps_do_not_corrupt_gross",
    "test_multiline_source_physical_rows_preserved",
    "test_original_source_sha256_and_files_preserved",
    "test_repeat_reports_have_deterministic_content",
    "test_header_only_inputs_publish_unfabricated_schema",
    "test_cross_keys_do_not_share_gross_flows",
    "test_explicit_amount_mapping_retains_gross_evidence",
    "test_invalid_money_fails_before_any_report_publication",
    "test_rejected_private_money_not_reflected_in_error",
    "test_normalized_identity_collision_still_requires_review",
    "test_output_source_identical_hash_flag_unchanged",
    "test_formula_like_transaction_identity_stays_escaped",
))

def flatten(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from flatten(case)
        else:
            yield case

def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_ledger_gross_flow_r148.py")
        cases = list(flatten(suite))
        observed = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(observed) != EXPECTED
                or any(type(case).__name__ != "LedgerGrossFlowR148" for case in cases)):
            raise ValueError("Required LedgerDiff gross-flow inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        clean = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                 and not result.skipped and not result.unexpectedSuccesses)
        print(f"R148 LedgerDiff gross-flow review {'PASS' if clean else 'FAIL'}; "
              f"methods={result.testsRun}; "
              f"issues={len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if clean else 1
    except Exception:
        print("R148 LedgerDiff gross-flow HOLD: required tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
