"""R173 strict, privacy-redacted policy/stream primitive test inventory for both OSes."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_string_subclass_lies_about_stored_absolute",
    "test_string_subclass_lies_about_stored_fraction",
    "test_integer_subclass_lies_about_stored_absolute",
    "test_integer_subclass_lies_about_stored_fraction",
    "test_subclass_string_hook_cannot_run",
    "test_subclass_integer_hook_cannot_run",
    "test_subclass_private_string_not_printed",
    "test_subclass_private_integer_not_printed",
    "test_spoofed_str_equality_hooks_not_run",
    "test_spoofed_int_equality_hooks_not_run",
    "test_bool_subclass_family_rejected",
    "test_exact_string_absolute_preserved",
    "test_exact_int_absolute_preserved",
    "test_exact_string_fraction_preserved",
    "test_exact_zero_integer_preserved",
    "test_exact_upper_bound_preserved",
    "test_out_of_bounds_string_fails",
    "test_out_of_bounds_integer_fails",
    "test_negative_integer_fails",
    "test_exponent_string_fails",
    "test_overprecision_string_fails",
    "test_non_ascii_digits_fail",
    "test_nonprimitive_numeric_rejected",
    "test_source_string_subclass_no_hash_called",
    "test_source_object_no_hash_called",
    "test_source_integer_no_hash_called",
    "test_source_unknown_plain_rejected",
    "test_invoice_stream_retains_credit",
    "test_receipt_stream_retains_return",
    "test_grant_classification_unchanged",
    "test_all_error_messages_hide_private_cells",
))


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_procure_policy_primitive_r173.py",
        )
        loaded = list(cases(suite))
        methods = [case._testMethodName for case in loaded]
        if (len(loaded) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "ProcurePolicyNativePrimitiveR173"
                       for case in loaded)):
            raise ValueError("R173 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        good = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print("R173 procurement policy native primitives "
              + ("PASS" if good else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failed))
        return 0 if good else 1
    except Exception:
        print("R173 procurement policy native primitives HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
