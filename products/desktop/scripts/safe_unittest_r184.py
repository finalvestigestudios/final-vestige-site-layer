"""Fail-closed source-order compatibility regression gate; 20 synthetic methods."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_50000_line_limit_valid_and_overflow_fails",
    "test_after_only_intermediate_hunk_retains_checkpoint",
    "test_ambiguous_skeleton_suppressed_without_guessing",
    "test_backward_moving_after_hunk_rejected",
    "test_backward_moving_before_hunk_rejected",
    "test_before_only_intermediate_hunk_retains_checkpoint",
    "test_long_unmatched_after_row_still_blocks_reuse",
    "test_long_unmatched_before_row_still_blocks_reuse",
    "test_ordered_pairs_have_deterministic_physical_order",
    "test_oversize_lines_skipped_but_short_candidate_remains",
    "test_reusing_after_coordinate_in_later_hunk_rejected",
    "test_reusing_before_coordinate_in_later_hunk_rejected",
    "test_reversed_after_rows_with_match_fail_closed",
    "test_reversed_before_rows_with_match_fail_closed",
    "test_sensitive_line_text_never_repeated_in_navigation",
    "test_three_valid_pairs_sorted_on_source_coordinates",
    "test_two_disjoint_hunks_are_ordered",
    "test_untrusted_hunk_dict_subclass_rejected_without_get",
    "test_untrusted_row_tuple_subclass_rejected_without_iteration",
    "test_valid_gaps_between_rows_do_not_create_fake_citations",
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
            pattern="test_policy_source_order_contract_r184.py",
        )
        cases = list(flatten(suite))
        found = [case._testMethodName for case in cases]
        if (len(cases) != 20 or len(set(found)) != 20
                or set(found) != EXPECTED
                or any(type(case).__name__ != "PolicySourceOrderContractR184"
                       for case in cases)):
            raise ValueError("R184 exact method inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.testsRun == 20 and result.wasSuccessful()
                  and not result.skipped and not result.unexpectedSuccesses)
        print(f"R184 historical source order {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; failures={len(result.failures)}; "
              f"errors={len(result.errors)}; skips={len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R184 HOLD: exact source-order test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
