"""Fail-closed 30-method R185 canonical source custody gate; synthetic only."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_valid_pair",
    "test_mixed_change_valid",
    "test_two_hunks_valid_order",
    "test_reversed_before_fail_closed",
    "test_reversed_after_fail_closed",
    "test_duplicate_before_rejected",
    "test_duplicate_after_rejected",
    "test_cross_hunk_before_collision",
    "test_cross_hunk_after_collision",
    "test_long_before_row_still_blocks_reuse",
    "test_long_after_row_still_blocks_reuse",
    "test_long_pair_skips_navigation_without_text_leak",
    "test_long_then_short_still_cites_short",
    "test_line_zero_rejected",
    "test_bool_identity_rejected",
    "test_line_over_50000_rejected",
    "test_line_50000_accepted",
    "test_dict_subclass_rejected_without_hook",
    "test_list_subclass_rejected_without_iter",
    "test_row_tuple_subclass_rejected_without_iter",
    "test_text_subclass_rejected",
    "test_int_subclass_rejected",
    "test_ambiguous_duplicates_suppressed",
    "test_privacy_and_human_review",
    "test_deterministic",
    "test_extra_key_compatibility",
    "test_invalid_second_hunk_suppresses_first_evidence",
    "test_valid_gaps",
    "test_no_hunks",
    "test_invalid_hunk",
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
            pattern="test_policy_canonical_custody_r185.py",
        )
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != 30 or len(set(names)) != 30
                or set(names) != EXPECTED
                or any(type(case).__name__ != "CanonicalCustodyR185"
                       for case in cases)):
            raise ValueError("R185 exact test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.testsRun == 30 and result.wasSuccessful()
                  and not result.skipped and not result.unexpectedSuccesses)
        print(f"R185 canonical source custody {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; failures={len(result.failures)}; "
              f"errors={len(result.errors)}; skips={len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R185 HOLD: exact canonical source custody test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
