"""R171 strict fail-closed test inventory; redacted output; runs normal and -OO."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_reject_integer_display",
    "test_reject_decimal_display",
    "test_reject_float_display",
    "test_reject_boolean_display",
    "test_reject_none_display",
    "test_reject_bytes_display",
    "test_reject_list_display",
    "test_reject_dict_display",
    "test_reject_tuple_display",
    "test_reject_set_display",
    "test_reject_object_display",
    "test_reject_str_subclass_display",
    "test_hostile_value_string_hooks_are_not_called",
    "test_hostile_string_equality_is_not_called",
    "test_mutable_nested_value_cannot_be_returned",
    "test_late_invalid_candidate_aborts_whole_report",
    "test_late_invalid_after_multiple_valid_candidates",
    "test_private_value_not_in_rejection_message",
    "test_valid_display_text_preserved",
    "test_custom_plain_text_column_preserved",
    "test_unicode_text_unchanged",
    "test_untrusted_reference_placeholders_are_overwritten",
    "test_source_digest_still_binds_reference",
    "test_physical_row_error_contract_unchanged",
    "test_status_error_contract_unchanged",
    "test_source_rows_not_mutated_by_valid_report",
    "test_malicious_dict_subclass_cannot_hide_bad_display_value",
    "test_normalized_result_uses_only_plain_strings",
    "test_text_columns_do_not_affect_stable_locator",
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
            pattern="test_invoice_report_value_custody_r171.py",
        )
        loaded = list(cases(suite))
        methods = [case._testMethodName for case in loaded]
        if (len(loaded) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "InvoiceReportValueCustodyR171"
                       for case in loaded)):
            raise ValueError("R171 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        good = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print("R171 Invoice Twin report value custody "
              + ("PASS" if good else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failed))
        return 0 if good else 1
    except Exception:
        print("R171 Invoice Twin value custody HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
