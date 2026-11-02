"""R130 zero-skip exact-method, redacted regression gate for finite JSON custody."""
from __future__ import annotations

import contextlib
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset((
    "test_valid_r9_json_is_accepted",
    "test_valid_fraction_and_exponent_json_are_finite",
    "test_r9_nan_constant_is_rejected",
    "test_r9_positive_infinity_constant_is_rejected",
    "test_r9_negative_infinity_constant_is_rejected",
    "test_scientific_overflow_is_rejected",
    "test_negative_scientific_overflow_is_rejected",
    "test_nested_nonfinite_token_is_rejected",
    "test_matrix_nonfinite_token_is_rejected",
    "test_duplicate_key_rejection_is_preserved",
    "test_direct_r9_nan_duration_is_rejected",
    "test_direct_r9_positive_infinity_duration_is_rejected",
    "test_direct_r9_negative_infinity_duration_is_rejected",
    "test_direct_r9_valid_int_and_float_durations",
    "test_rehashed_witness_nan_token_fails_closed",
    "test_rehashed_witness_overflow_number_fails_closed",
    "test_six_app_pending_and_one_witness_still_hold",
    "test_cli_errors_are_redacted_no_assert_bypass",
))
METHOD = re.compile(r"test_[a-z][a-z0-9_]{0,100}$")


def all_names(suite):
    names = []
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            names.extend(all_names(test))
        else:
            method = getattr(test, "_testMethodName", None)
            if type(method) is not str or METHOD.fullmatch(method) is None:
                raise ValueError("Unknown regression method")
            names.append(method)
    return names


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_windows11_nonfinite_intake_r130.py")
        found = all_names(suite)
        if len(found) != len(REQUIRED) or set(found) != REQUIRED:
            raise ValueError("Missing, duplicate or unexpected regression")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        bad = sorted({test._testMethodName for test, _ in
                      result.failures + result.errors + result.skipped}
                     | {test._testMethodName for test in result.unexpectedSuccesses})
        passed = result.wasSuccessful() and not result.skipped and result.testsRun == len(REQUIRED)
        print(f"R130 finite-only private review {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun} failed={len(bad)}")
        if bad:
            print("Source-owned failed methods: " +
                  ", ".join(name for name in bad if name in REQUIRED))
        return 0 if passed else 1
    except Exception:
        print("R130 private evidence HOLD: source inventory or execution unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
