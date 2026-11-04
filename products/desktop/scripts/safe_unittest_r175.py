"""R175 static no-skip LedgerDiff provenance custody gate; no financial values logged."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_bool_report_value_rejected",
    "test_decimal_report_value_rejected_without_coercion",
    "test_digest_newline_rejected",
    "test_digest_non_string_rejected",
    "test_digest_subclass_left_rejected_before_equality",
    "test_digest_subclass_right_rejected_before_equality",
    "test_digest_uppercase_rejected",
    "test_distinct_digest_values_bound_to_report",
    "test_empty_report_stays_empty",
    "test_empty_report_still_rejects_bad_digest",
    "test_forged_dict_methods_cannot_replace_amount",
    "test_forged_dict_methods_cannot_replace_rows",
    "test_hostile_non_string_key_rejected_before_rehash",
    "test_identical_digest_requires_human_review",
    "test_integer_report_value_rejected",
    "test_nested_mutable_report_value_rejected",
    "test_no_compliance_determination_added",
    "test_non_dict_row_rejected",
    "test_original_cents_and_row_refs_preserved",
    "test_original_row_not_mutated",
    "test_output_row_not_alias_to_input",
    "test_preexisting_digest_columns_are_overwritten",
    "test_private_text_not_leaked_in_validation_errors",
    "test_repeat_call_is_deterministic",
    "test_row_collection_subclass_rejected_before_iteration",
    "test_string_subclass_amount_rejected_before_str_hook",
    "test_string_subclass_status_rejected",
    "test_subclass_key_rejected_before_hashing",
    "test_tuple_collection_rejected",
    "test_two_distinct_rows_preserve_order",
    "test_unicode_plain_text_preserved",
    "test_untrusted_prior_digest_value_rejected_not_stringified",
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
            pattern="test_ledger_report_custody_r175.py",
        )
        loaded = list(cases(suite))
        methods = [case._testMethodName for case in loaded]
        if (len(loaded) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "LedgerReportCustodyR175"
                       for case in loaded)):
            raise ValueError("R175 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        good = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print("R175 LedgerDiff native report custody "
              + ("PASS" if good else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failed))
        return 0 if good else 1
    except Exception:
        print("R175 LedgerDiff native report custody HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
