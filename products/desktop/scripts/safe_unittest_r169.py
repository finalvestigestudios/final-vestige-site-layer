"""Fail-closed exact-inventory gate for R169 Invoice Twin direct API tests."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_exact_candidate_id_stable",
    "test_near_candidate_id_stable",
    "test_pair_orientation_changes_reference",
    "test_digest_changes_reference",
    "test_reject_digest_str_subclass",
    "test_reject_digest_equality_alias",
    "test_reject_list_subclass_hooks",
    "test_reject_row_a_subclass",
    "test_reject_row_b_subclass",
    "test_reject_row_a_equality_alias",
    "test_reject_row_b_equality_alias",
    "test_reject_status_subclass",
    "test_reject_status_equality_alias",
    "test_reject_extra_subclass_field_name",
    "test_reject_row_a_field_name_alias",
    "test_native_storage_ignores_forged_getter",
    "test_native_storage_ignores_forged_items_and_iteration",
    "test_reject_invalid_stored_row_despite_forged_getter",
    "test_reject_invalid_stored_status_despite_forged_getter",
    "test_reject_same_stored_row_despite_forged_getter",
    "test_reject_reverse_duplicate_without_returning_partial",
    "test_reject_late_invalid_without_returning_partial",
    "test_input_rows_are_not_mutated",
    "test_return_values_are_snapshot_owned",
    "test_existing_untrusted_reference_fields_overwritten",
    "test_private_field_name_never_echoed_in_error",
    "test_empty_report_still_checks_digest",
    "test_opaque_review_columns_preserved",
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
            start_dir=str(ROOT / "tests"), pattern="test_invoice_report_snapshot_r169.py")
        cases = list(_cases(suite))
        methods = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "InvoiceReportSnapshotCustodyR169"
                       for case in cases)):
            raise ValueError("R169 regression inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        failures = sorted({case._testMethodName for case, _ in
                           (*result.errors, *result.failures)})
        print(f"R169 Invoice Twin report snapshot custody {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors) + len(result.failures) + len(result.skipped)}; "
              f"failed_methods={','.join(failures)}")
        return 0 if passed else 1
    except Exception:
        print("R169 Invoice Twin report snapshot custody HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
