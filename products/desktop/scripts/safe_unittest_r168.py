"""Fail-closed exact-inventory gate for R168 Invoice Twin direct API tests."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_reject_vendor_equality_alias",
    "test_reject_invoice_equality_alias",
    "test_reject_vendor_plain_subclass",
    "test_reject_invoice_plain_subclass",
    "test_reject_row_plain_subclass",
    "test_reject_row_equality_alias",
    "test_reject_decimal_plain_subclass",
    "test_reject_decimal_lying_comparison",
    "test_reject_decimal_lying_hash",
    "test_reject_decimal_classification_hook",
    "test_reject_decimal_tuple_hook",
    "test_reject_extra_subclass_field_name",
    "test_reject_row_field_name_subclass",
    "test_reject_alias_field_name_hash",
    "test_reject_vendor_field_name_subclass",
    "test_reject_amount_field_name_subclass",
    "test_no_subclassed_dict_hooks_executed",
    "test_rejection_does_not_mutate_input",
    "test_late_bad_vendor_fails_without_partial_result",
    "test_late_bad_money_fails_without_partial_result",
    "test_private_alias_not_reflected_in_error",
    "test_private_field_name_not_reflected_in_error",
    "test_plain_exact_group_is_preserved",
    "test_plain_near_group_is_preserved",
    "test_exact_subcent_decimal_and_hostile_context",
    "test_owned_snapshots_still_survive_original_mutation",
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
            start_dir=str(ROOT / "tests"), pattern="test_invoice_exact_primitives_r168.py")
        cases = list(_cases(suite))
        methods = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "InvoiceExactPrimitivesR168"
                       for case in cases)):
            raise ValueError("R168 regression inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        failures = sorted({case._testMethodName for case, _ in
                           (*result.errors, *result.failures)})
        print(f"R168 Invoice Twin exact primitive custody {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors) + len(result.failures) + len(result.skipped)}; "
              f"failed_methods={','.join(failures)}")
        return 0 if passed else 1
    except Exception:
        print("R168 Invoice Twin exact primitive custody HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
