"""R153 fail-closed, quiet, fixed-inventory SpendMap custody regression gate."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_cross_category_cites_both_sources",
    "test_category_only_source_rows_remain_distinct",
    "test_same_category_two_lines",
    "test_multiline_csv_records_reference_physical_start",
    "test_numeric_line_order_beyond_nine",
    "test_one_record_count",
    "test_exact_32_limit_has_no_omission",
    "test_35_records_report_three_omissions",
    "test_70_records_keep_earliest_32",
    "test_31_records_are_not_truncated",
    "test_month_count_not_multiplied_by_categories",
    "test_month_isolation",
    "test_vendor_isolation",
    "test_colliding_normalized_vendors_cited_and_flagged",
    "test_uncategorized_credit_is_cited",
    "test_zero_amounts_still_contribute_source_evidence",
    "test_existing_exact_gross_net_totals_unchanged",
    "test_original_sha256_preserved",
    "test_original_source_never_mutated",
    "test_formula_like_vendor_labels_still_escaped",
    "test_invalid_money_fails_closed_without_report",
    "test_repeated_reports_deterministic",
    "test_schema_precedes_existing_gross_columns",
    "test_legacy_last_seven_columns_unmodified",
    "test_many_categories_keep_bounded_references",
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
            pattern="test_spend_evidence_custody_r153.py")
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED or
                any(type(case).__name__ != "SpendEvidenceCustodyR153" for case in cases)):
            raise ValueError("R153 fixed regression inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R153 SpendMap cross-category provenance {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R153 SpendMap provenance HOLD: required tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
