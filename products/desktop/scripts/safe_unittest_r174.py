"""R174 strict, privacy-redacted SpendMap source custody inventory on both OSes."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_plain_rows_preserve_exact_cents_and_month",
    "test_original_plain_records_are_unmodified",
    "test_result_owns_independent_dictionary",
    "test_spoofed_get_cannot_replace_physical_row",
    "test_spoofed_get_cannot_replace_amount",
    "test_spoofed_get_cannot_replace_vendor",
    "test_spoofed_get_cannot_replace_category",
    "test_spoofed_keys_items_getitem_and_iter_never_called",
    "test_callback_mutation_cannot_change_current_row_provenance",
    "test_no_original_record_mapped_source_changed_by_copy",
    "test_list_subclass_cannot_override_iteration",
    "test_list_subclass_cannot_override_length",
    "test_custom_nonstring_key_rejected_before_display",
    "test_string_subclass_key_rejected_before_hashing",
    "test_source_row_string_subclass_rejected_without_hooks",
    "test_source_vendor_string_subclass_rejected_without_hooks",
    "test_source_amount_string_subclass_rejected_without_hooks",
    "test_source_date_string_subclass_rejected_without_hooks",
    "test_source_category_string_subclass_rejected_without_hooks",
    "test_vendor_normalizer_subclass_rejected_before_equality_hash",
    "test_money_parser_decimal_subclass_rejected_before_arithmetic",
    "test_float_parser_not_accepted_as_money",
    "test_normal_plain_negative_credit_stays_exact",
    "test_missing_category_still_uncategorized",
    "test_callback_receives_stored_not_forged_values",
    "test_duplicate_rows_still_rejected",
    "test_caller_decimal_traps_stay_unchanged",
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
            pattern="test_spend_native_custody_r174.py",
        )
        loaded = list(cases(suite))
        methods = [case._testMethodName for case in loaded]
        if (len(loaded) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "SpendNativeCustodyR174"
                       for case in loaded)):
            raise ValueError("R174 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        good = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print("R174 SpendMap native source custody "
              + ("PASS" if good else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failed))
        return 0 if good else 1
    except Exception:
        print("R174 SpendMap native source custody HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
