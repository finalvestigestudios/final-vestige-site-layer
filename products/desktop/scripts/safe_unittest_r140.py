"""R140 exact no-skip, two-mode, source-owned LedgerDiff amount-header mappings tests."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_default_amount_alias_is_recorded_per_side",
    "test_independent_explicit_amount_headers",
    "test_left_only_override_preserves_right_auto",
    "test_right_only_override_preserves_left_auto",
    "test_override_and_match_headers_can_both_differ",
    "test_ambiguous_auto_amount_aliases_fail_closed",
    "test_override_disambiguates_amount_aliases",
    "test_explicit_amount_missing_fails_before_report",
    "test_choosing_identity_as_amount_rejected",
    "test_choosing_amount_as_identity_rejected",
    "test_invalid_override_values_are_generic_and_private",
    "test_non_ascii_override_rejected",
    "test_case_and_space_normalization_preserves_actual_header",
    "test_duplicate_normalized_headers_rejected",
    "test_source_physical_line_provenance_multiline",
    "test_exact_negative_money_and_variance",
    "test_invalid_money_still_fails_closed",
    "test_unmatched_rows_do_not_get_fabricated_citations",
    "test_identical_source_bytes_still_require_review",
    "test_header_only_reports_have_schema_and_no_fabrication",
    "test_sources_unchanged_after_export",
    "test_table_original_tuple_contract_unchanged",
    "test_ledger_layout_maps_all_four_optional_headers",
    "test_gui_wires_both_amount_headers_and_does_not_unlock_premium",
))

def flatten(suite):
    for member in suite:
        if isinstance(member, unittest.TestSuite):
            yield from flatten(member)
        else:
            yield member

def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_ledger_amount_headers_r140.py")
        names = [case._testMethodName for case in flatten(suite)]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError("R140 test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R140 LedgerDiff amount header custody {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R140 LedgerDiff amount header custody HOLD: tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
