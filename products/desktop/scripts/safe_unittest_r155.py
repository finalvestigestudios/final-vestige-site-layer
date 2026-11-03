"""R155 fixed-inventory zero-skip gate; no client data leaves the workstation."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_single_group_verified_with_two_pins",
    "test_multiple_months_and_vendors",
    "test_cross_category_monthly_proof",
    "test_thirty_three_citations_with_omission",
    "test_two_hundred_line_members",
    "test_multiline_source_physical_line_numbers",
    "test_normalization_collision_group",
    "test_safe_csv_export_category",
    "test_tampered_membership_hash_hold",
    "test_tampered_source_pin_hold",
    "test_tampered_preview_hold",
    "test_tampered_count_hold",
    "test_tampered_omitted_hold",
    "test_tampered_category_lines_hold",
    "test_renamed_bucket_hold",
    "test_duplicate_bucket_hold",
    "test_missing_bucket_hold",
    "test_original_source_modified_after_export_hold",
    "test_header_only_financial_source_hold",
    "test_report_source_not_modified_by_verification",
    "test_cli_success_no_private_path",
    "test_cli_bad_source_no_leak",
    "test_cli_duplicate_report_hold",
    "test_cli_unexpected_option_hold",
    "test_symlink_source_rejected_when_supported",
    "test_report_without_evidence_columns_hold",
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
            pattern="test_spend_evidence_independent_verify_r155.py")
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED or
                any(type(case).__name__ != "SpendIndependentMembershipR155"
                    for case in cases)):
            raise ValueError("R155 fixed regression inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R155 SpendMap independent membership {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R155 SpendMap membership HOLD: required tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
