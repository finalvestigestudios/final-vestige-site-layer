"""R135 SpendMap category-baseline gate: exact methods, zero skips, redacted logs."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_category_spike_masked_by_other_category",
    "test_vendor_spike_does_not_imply_category_spike",
    "test_two_categories_have_independent_history",
    "test_vendor_isolation_with_identical_category",
    "test_insufficient_category_history_despite_vendor_history",
    "test_exact_half_cent_boundary_qualifies",
    "test_one_cent_below_exact_boundary_is_not_flagged",
    "test_nonpositive_prior_baseline_suppresses_spike",
    "test_sparse_calendar_does_not_invent_months",
    "test_case_distinct_category_labels_are_not_silently_merged",
    "test_legacy_vendor_flag_remains_unchanged",
    "test_vendor_normalization_collision_stays_reviewable",
    "test_preserves_physical_rows_and_original_source_sha",
    "test_result_is_deterministic_across_runs",
    "test_invalid_money_leaves_no_partial_report",
    "test_empty_report_has_complete_new_schema",
    "test_hostile_decimal_context_preserves_evidence",
))


def flatten(suite):
    for entry in suite:
        if isinstance(entry, unittest.TestSuite):
            yield from flatten(entry)
        else:
            yield entry


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_spend_category_baselines_r135.py",
        )
        names = [case._testMethodName for case in flatten(suite)]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError("R135 test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R135 spend category baselines {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R135 spend category baselines HOLD: source tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
