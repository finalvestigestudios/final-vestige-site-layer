"""R167 source-owned, no-skip Invoice Twin stored-items test gate."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_reject_stored_invalid_row",
    "test_reject_stored_header_row",
    "test_reject_stored_unicode_row",
    "test_reject_stored_row_with_leading_zero",
    "test_reject_stored_duplicate_rows",
    "test_reject_stored_date_string",
    "test_reject_stored_datetime",
    "test_reject_stored_float_money",
    "test_reject_stored_nan_money",
    "test_reject_stored_over_limit_money",
    "test_reject_stored_scale_overflow",
    "test_reject_stored_vendor_lowercase",
    "test_reject_stored_vendor_unicode",
    "test_reject_stored_invoice_empty",
    "test_reject_stored_missing_key",
    "test_valid_stored_data_ignores_bad_forged_views",
    "test_stored_exact_group_anchor",
    "test_stored_near_match_not_forged_exact",
    "test_stored_amount_groups_not_forged",
    "test_forged_row_order_cannot_swap_anchor",
    "test_stored_amount_sign_review",
    "test_snapshot_owned_after_source_changed",
    "test_failure_has_no_private_values",
    "test_validate_before_generating_candidates",
    "test_plain_dict_still_works",
    "test_no_original_view_method_called",
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
            start_dir=str(ROOT / "tests"), pattern="test_invoice_stored_items_r167.py")
        cases = list(_cases(suite))
        methods = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "InvoiceStoredItemsCustodyR167"
                       for case in cases)):
            raise ValueError("R167 regression inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        failures = sorted({case._testMethodName for case, _ in
                           (*result.errors, *result.failures)})
        print(f"R167 invoice stored-items custody {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors) + len(result.failures) + len(result.skipped)}; "
              f"failed_methods={','.join(failures)}")
        return 0 if passed else 1
    except Exception:
        print("R167 invoice stored-items custody HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
