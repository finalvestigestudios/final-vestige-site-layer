"""Fail-closed R182 Policy Delta source-coordinate custody test gate (38 methods)."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_boolean_source_line_rejected",
    "test_dict_subclass_not_accessed",
    "test_duplicate_after_line_rejected",
    "test_duplicate_before_line_rejected",
    "test_exact_limit_permitted",
    "test_float_source_line_rejected",
    "test_integer_subclass_not_executed",
    "test_invalid_after_suppresses_otherwise_valid_candidate",
    "test_invalid_before_suppresses_otherwise_valid_candidate",
    "test_invalid_hunk_does_not_suppress_independent_valid_hunk",
    "test_legacy_ambiguous_skeletons_still_suppressed",
    "test_legacy_bounded_codepoint_count",
    "test_legacy_bounded_pair_count",
    "test_list_row_rejected",
    "test_list_subclass_is_not_iterated",
    "test_list_subclass_rows_not_iterated",
    "test_long_line_skipped_without_suppressing_short_candidate",
    "test_missing_added_sources",
    "test_missing_removed_sources",
    "test_negative_source_line_rejected",
    "test_no_hunks",
    "test_non_dict_hunk_fails_closed",
    "test_non_list_hunk_collection_fails_closed",
    "test_numeric_and_spoken_cues_preserved",
    "test_object_text_rejected",
    "test_over_limit_after_line_rejected",
    "test_over_limit_before_line_rejected",
    "test_private_source_content_not_repeated",
    "test_source_rows_unchanged",
    "test_string_source_line_rejected",
    "test_text_subclass_rejected_without_iteration",
    "test_triple_row_rejected",
    "test_tuple_rows_rejected",
    "test_tuple_subclass_row_not_unpacked",
    "test_two_hunks_remain_distinct",
    "test_valid_before_after_source_coordinates",
    "test_zero_length_row_rejected",
    "test_zero_source_line_rejected",
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
            pattern="test_policy_confusable_source_custody_r182.py",
        )
        cases = list(flatten(suite))
        actual = [case._testMethodName for case in cases]
        if (len(cases) != 38 or len(set(actual)) != 38
                or set(actual) != EXPECTED
                or any(type(case).__name__ != "PolicyConfusableSourceCustodyR182"
                       for case in cases)):
            raise ValueError("R182 exact method inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.testsRun == 38 and result.wasSuccessful()
                  and not result.skipped and not result.unexpectedSuccesses)
        print(f"R182 source-coordinate custody {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; failures={len(result.failures)}; "
              f"errors={len(result.errors)}; skips={len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R182 HOLD: exact custody test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
