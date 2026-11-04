"""Strict, no-skip R176 shared financial parser gate; no customer values logged."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_money_rejects_forged_str",
    "test_money_rejects_trap_str_before_conversion",
    "test_money_rejects_forged_int",
    "test_money_rejects_trap_int_before_conversion",
    "test_money_rejects_forged_decimal",
    "test_money_rejects_trap_decimal_before_conversion",
    "test_money_rejects_arbitrary_object",
    "test_money_rejects_float_and_bool",
    "test_unit_cost_rejects_forged_str",
    "test_unit_cost_rejects_trap_str_before_conversion",
    "test_unit_cost_rejects_forged_int",
    "test_unit_cost_rejects_trap_int_before_conversion",
    "test_unit_cost_rejects_forged_decimal",
    "test_unit_cost_rejects_trap_decimal_before_conversion",
    "test_unit_cost_rejects_arbitrary_object",
    "test_unit_cost_rejects_float_and_bool",
    "test_quantity_rejects_forged_str",
    "test_quantity_rejects_trap_str_before_conversion",
    "test_quantity_rejects_forged_int",
    "test_quantity_rejects_trap_int_before_conversion",
    "test_quantity_rejects_forged_decimal",
    "test_quantity_rejects_trap_decimal_before_conversion",
    "test_quantity_rejects_arbitrary_object",
    "test_quantity_rejects_float_and_bool",
    "test_money_valid_native_strings_ints_and_decimals",
    "test_unit_cost_valid_native_strings_ints_and_decimals",
    "test_quantity_valid_native_strings_ints_and_decimals",
    "test_native_huge_integer_fails_before_conversion_limit",
    "test_exact_decimal_boundaries_unchanged",
    "test_scientific_notation_remains_rejected",
))


def cases(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from cases(case)
        else:
            yield case


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_shared_financial_primitives_r176.py",
        )
        loaded = list(cases(suite))
        methods = [case._testMethodName for case in loaded]
        if (len(loaded) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "SharedPrimitiveCustodyR176"
                       for case in loaded)):
            raise ValueError("R176 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        good = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print("R176 shared numeric primitive custody "
              + ("PASS" if good else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failed))
        return 0 if good else 1
    except Exception:
        print("R176 shared numeric primitive custody HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
