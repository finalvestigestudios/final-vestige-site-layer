"""R160 strict, fixed-inventory, zero-skip spend category custody test gate."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_plain_category_roundtrip",
    "test_single_equal_formula_roundtrip",
    "test_multiple_distinct_formula_categories_roundtrip",
    "test_literal_apostrophe_category_roundtrip",
    "test_duplicate_identical_formula_category_aggregates",
    "test_same_display_other_vendor_allowed",
    "test_same_display_other_month_allowed",
    "test_negative_numeric_and_quoted_negative_distinct",
    "test_mixed_credit_totals_unchanged",
    "test_multiline_record_roundtrip",
    "test_normal_source_bytes_unmodified",
    "test_case_sensitive_distinct_labels_roundtrip",
    "test_equal_sign_collision_rejected",
    "test_plus_formula_collision_rejected",
    "test_at_sign_collision_rejected",
    "test_negative_formula_collision_rejected",
    "test_zero_width_category_collision_rejected",
    "test_bidi_isolate_category_collision_rejected",
    "test_combining_prefix_category_collision_rejected",
    "test_quoted_comma_formula_collision_rejected",
    "test_normalized_vendor_alias_collision_rejected",
    "test_rejection_creates_no_report",
    "test_collision_keeps_original_source_unchanged",
    "test_collision_error_does_not_echo_private_category",
    "test_independent_verifier_rejects_legacy_ambiguous_export",
    "test_independent_verifier_rejects_hidden_category_collision",
    "test_verifier_cli_redacts_ambiguous_source",
    "test_verifier_accepts_noncolliding_formula_categories",
    "test_report_schema_still_exact_25",
    "test_generated_report_retains_physical_source_citations",
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
            pattern="test_spend_category_collision_r160.py")
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED
                or any(type(case).__name__ != "SpendCategoryR160" for case in cases)):
            raise ValueError("R160 strict test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        # Print ONLY static test method names, never an exception traceback,
        # synthetic client cell, source path or user's financial information.
        failed_names = sorted({case._testMethodName
                               for case, _ in (*result.errors, *result.failures)})
        print(f"R160 SpendMap category display custody {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors)+len(result.failures)+len(result.skipped)}; "
              f"failed_methods={','.join(failed_names)}")
        return 0 if passed else 1
    except Exception:
        print("R160 SpendMap category display custody HOLD: required tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
