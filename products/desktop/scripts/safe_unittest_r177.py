"""No-skip 30-method R177 regression gate; no private source values printed."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset(("test_key_trap_str", "test_key_forged_str", "test_key_trap_int", "test_key_trap_object", "test_key_native_int", "test_key_decimal", "test_key_boolean", "test_key_none", "test_key_bytes", "test_key_list", "test_date_trap_str", "test_date_forged_str", "test_date_trap_int", "test_date_trap_object", "test_date_native_int", "test_date_decimal", "test_date_boolean", "test_date_none", "test_date_bytes", "test_date_native_datetime", "test_date_invalid_leap", "test_date_unicode_digits", "test_date_formula_tail", "test_date_oversize", "test_key_ascii", "test_key_blank", "test_key_unicode_lossy", "test_date_iso", "test_date_us", "test_date_leap"))


def flatten(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from flatten(case)
        else:
            yield case


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_native_identity_date_r177.py")
        loaded = list(flatten(suite))
        names = [case._testMethodName for case in loaded]
        if (len(loaded) != 30 or set(names) != EXPECTED
                or len(set(names)) != 30
                or any(type(case).__name__ != "NativeIdentityDateR177" for case in loaded)):
            raise ValueError("R177 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == 30
                  and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({c._testMethodName for c, _ in
                         (*result.errors, *result.failures)})
        print("R177 native identity/date " + ("PASS" if passed else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failed))
        return 0 if passed else 1
    except Exception:
        print("R177 HOLD: exact test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
