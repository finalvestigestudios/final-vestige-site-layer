"""Fail-closed R183 Policy Delta global physical-source custody gate (25 methods)."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_after_coordinates_descend_between_hunks_fails_closed",
    "test_after_rows_descend_inside_hunk_suppressed",
    "test_before_coordinates_descend_between_hunks_fails_closed",
    "test_before_rows_descend_inside_hunk_suppressed",
    "test_empty_hunk_between_valid_disjoint_hunks",
    "test_empty_side_does_not_erase_prior_after_checkpoint",
    "test_empty_side_does_not_erase_prior_before_checkpoint",
    "test_excess_hunk_collection_is_rejected",
    "test_existing_16_pair_bound_preserved",
    "test_locally_invalid_hunk_does_not_disable_global_gate",
    "test_locally_invalid_hunk_keeps_separate_valid_hunk",
    "test_long_after_row_does_not_hide_reused_line",
    "test_long_after_row_out_of_order_inside_hunk_suppressed",
    "test_long_before_row_does_not_hide_reused_line",
    "test_long_before_row_out_of_order_inside_hunk_suppressed",
    "test_long_valid_row_does_not_hide_short_pair",
    "test_lower_upper_boundary_lines_accepted",
    "test_output_is_stable_and_privacy_preserving",
    "test_reused_after_line_in_separate_hunks_fails_closed",
    "test_reused_before_line_in_separate_hunks_fails_closed",
    "test_reused_identical_rows_in_separate_hunks_fails_closed",
    "test_same_line_before_after_is_allowed",
    "test_unmatched_rows_still_enforce_cross_hunk_order",
    "test_valid_disjoint_hunks",
    "test_valid_single_hunk",
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
            pattern="test_policy_global_source_custody_r183.py",
        )
        cases = list(flatten(suite))
        actual = [case._testMethodName for case in cases]
        if (len(cases) != 25 or len(set(actual)) != 25
                or set(actual) != EXPECTED
                or any(type(case).__name__ != "PolicyGlobalSourceCustodyR183"
                       for case in cases)):
            raise ValueError("R183 exact method inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.testsRun == 25 and result.wasSuccessful()
                  and not result.skipped and not result.unexpectedSuccesses)
        print(f"R183 global source-coordinate custody {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; failures={len(result.failures)}; "
              f"errors={len(result.errors)}; skips={len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R183 HOLD: exact custody test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
