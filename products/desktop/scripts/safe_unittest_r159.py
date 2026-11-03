"""R159 strict zero-skip SpendMap report-envelope test inventory."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_generated_schema_has_exact_25_fields",
    "test_unsorted_import_yields_verified_native_order",
    "test_native_formula_safe_categories_verified",
    "test_mixed_credit_export_verified",
    "test_quoted_multiline_source_verified",
    "test_schema_contract_does_not_import_generator",
    "test_added_payment_approved_column_holds",
    "test_added_compliance_verdict_column_holds",
    "test_added_fraud_determination_column_holds",
    "test_added_blank_notes_column_holds",
    "test_added_zero_width_claim_column_holds",
    "test_embedded_bom_header_holds",
    "test_swapped_amount_and_flag_headers_holds",
    "test_reversed_headers_holds",
    "test_duplicate_header_holds",
    "test_missing_flag_header_holds",
    "test_blank_extra_header_holds",
    "test_space_suffix_vendor_header_holds",
    "test_uppercase_vendor_header_holds",
    "test_unicode_confusable_amount_header_holds",
    "test_two_category_rows_swapped_holds",
    "test_two_month_rows_swapped_holds",
    "test_different_vendor_rows_swapped_holds",
    "test_middle_row_reordered_holds",
    "test_unchanged_files_after_success",
    "test_failed_extra_column_cli_redacts_private_value",
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
            pattern="test_spend_report_envelope_r159.py")
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED
                or any(type(case).__name__ != "SpendEnvelopeR159" for case in cases)):
            raise ValueError("R159 strict test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        print(f"R159 SpendMap report envelope {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R159 SpendMap report envelope HOLD: required tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
