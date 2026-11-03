"""R154 fail-closed, private-output, fixed-inventory source regression gate."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_basic_digest_matches_independent_reference",
    "test_digest_contains_lowercase_hex_only",
    "test_domain_separator_prevents_unqualified_line_hash",
    "test_one_contributor",
    "test_exact_thirty_two_are_all_in_digest",
    "test_thirty_three_includes_first_omitted_line",
    "test_seventy_includes_all_hidden_line_references",
    "test_many_categories_share_complete_group_digest",
    "test_category_local_source_rows_not_replaced",
    "test_cross_category_credits_have_same_digest",
    "test_zeros_contribute_to_hash_even_without_gross_flows",
    "test_multiline_csv_reference_uses_start_lines",
    "test_vendor_separation",
    "test_month_separation",
    "test_normalized_vendor_collision_still_uses_shared_group",
    "test_source_digest_changes_when_source_note_changes",
    "test_original_sha_is_not_replaced_by_group_digest",
    "test_full_source_bytes_are_not_modified",
    "test_repeated_exports_are_deterministic",
    "test_empty_source_has_new_schema_and_no_digest_rows",
    "test_digest_does_not_change_prior_terminal_export_columns",
    "test_direct_summarizer_ignores_record_iteration_order_for_hash",
    "test_direct_summarizer_source_pin_changes_digest",
    "test_direct_summarizer_member_change_changes_digest",
    "test_decimal_traps_do_not_change_digest_or_money",
    "test_invalid_private_amount_does_not_publish_digest",
    "test_source_pin_does_not_echo_source_labels",
    "test_five_hundred_records_include_all_without_long_preview",
))


def flatten(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from flatten(case)
        else:
            yield case


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_spend_complete_evidence_digest_r154.py")
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED or
                any(type(case).__name__ != "SpendCompleteDigestR154" for case in cases)):
            raise ValueError("R154 fixed regression inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R154 SpendMap complete evidence digest {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R154 SpendMap evidence digest HOLD: required tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
