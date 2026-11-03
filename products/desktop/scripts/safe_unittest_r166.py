"""R166 strict no-skip source-owned test inventory for Invoice Twin custody."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_reject_unstored_malformed_physical_line",
    "test_reject_unstored_header_line",
    "test_reject_unstored_leading_zero_line",
    "test_reject_unstored_unicode_digit_line",
    "test_reject_unstored_too_large_line",
    "test_reject_duplicate_held_physical_rows",
    "test_reject_unstored_date_text",
    "test_reject_unstored_datetime",
    "test_reject_unstored_float_money",
    "test_reject_unstored_nonfinite_money",
    "test_reject_unstored_infinite_money",
    "test_reject_unstored_excess_money",
    "test_reject_unstored_precision_money",
    "test_reject_unstored_vendor_case",
    "test_reject_unstored_vendor_unicode",
    "test_reject_unstored_invoice_punctuation",
    "test_reject_unstored_empty_invoice",
    "test_reject_unstored_missing_key",
    "test_valid_stored_row_ignores_forged_get",
    "test_no_get_side_effect_invoked",
    "test_two_row_pair_binds_stored_values",
    "test_owned_copy_not_input_alias",
    "test_private_bad_value_not_in_error",
    "test_hostile_decimal_context_remains_exact",
    "test_valid_normal_input_regression",
    "test_no_partial_result_on_late_spoof",
))


def _cases(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from _cases(case)
        else:
            yield case


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_invoice_validation_custody_r166.py")
        cases = list(_cases(suite))
        methods = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "InvoiceValidationCustodyR166" for case in cases)):
            raise ValueError("R166 regression inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        failures = sorted({case._testMethodName for case, _ in
                           (*result.errors, *result.failures)})
        print(f"R166 invoice validated snapshots {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors) + len(result.failures) + len(result.skipped)}; "
              f"failed_methods={','.join(failures)}")
        return 0 if passed else 1
    except Exception:
        print("R166 invoice validated snapshots HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
