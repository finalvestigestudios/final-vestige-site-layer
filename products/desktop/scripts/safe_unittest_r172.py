"""R172 strict, privacy-redacted premium event regression inventory for both OSes."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_procurement_stored_credit_overrides_fake_invoice_get",
    "test_procurement_stored_return_overrides_fake_receipt_get",
    "test_grant_stored_credit_overrides_fake_claim_get",
    "test_procurement_hostile_views_do_not_change_credit",
    "test_procurement_hostile_views_do_not_change_return",
    "test_grant_hostile_views_do_not_change_credit",
    "test_native_data_is_not_mutated",
    "test_procurement_rejects_non_dict_mapping_before_get",
    "test_grant_rejects_non_dict_mapping_before_get",
    "test_procurement_rejects_forged_field_key",
    "test_grant_rejects_forged_field_key",
    "test_procurement_rejects_hostile_type_value_without_hooks",
    "test_grant_rejects_hostile_type_value_without_hooks",
    "test_procurement_rejects_str_subclass_without_hooks",
    "test_grant_rejects_str_subclass_without_hooks",
    "test_procurement_rejects_numeric_and_boolean_types",
    "test_grant_rejects_numeric_and_boolean_types",
    "test_both_preserve_missing_blank_none_legacy_defaults",
    "test_both_preserve_casefold_and_whitespace",
    "test_whitespace_only_remains_invalid",
    "test_source_stream_failure_precedes_untrusted_mapping_access",
    "test_procurement_untrusted_citation_is_sanitized",
    "test_grant_untrusted_citation_is_sanitized",
    "test_canonical_physical_citation_still_visible",
    "test_actual_procurement_credit_affects_review_totals",
    "test_actual_grant_credit_stored_in_linked_allocation",
    "test_private_unknown_event_values_never_escape",
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
            pattern="test_premium_event_custody_r172.py",
        )
        loaded = list(cases(suite))
        methods = [case._testMethodName for case in loaded]
        if (len(loaded) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "PremiumEventNativeCustodyR172"
                       for case in loaded)):
            raise ValueError("R172 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        good = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print("R172 premium movement native custody "
              + ("PASS" if good else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failed))
        return 0 if good else 1
    except Exception:
        print("R172 premium movement custody HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
