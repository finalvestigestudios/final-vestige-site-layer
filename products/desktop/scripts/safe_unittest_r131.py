"""R131 strict, privacy-redacted executable test gate for per-side ledger keys."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_default_aliases_remain_compatible_and_cited",
    "test_distinct_explicit_left_and_right_match_headers",
    "test_override_disambiguates_two_auto_id_aliases",
    "test_case_and_space_normalize_to_exact_imported_header",
    "test_only_one_side_explicit_uses_other_auto_id_alias",
    "test_unmatched_selected_keys_never_claim_match",
    "test_missing_explicit_header_fails_before_save",
    "test_amount_cannot_be_reused_as_identity",
    "test_dangerous_or_private_header_name_is_never_echoed",
    "test_duplicate_normalized_headers_remain_rejected",
    "test_physical_line_citations_survive_quoted_multiline",
    "test_header_only_report_exposes_mapping_schema_without_fabricated_rows",
    "test_invalid_money_and_missing_keys_still_fail_closed",
    "test_original_inputs_are_never_modified",
    "test_existing_table_tuple_shapes_stay_compatible",
))


def _flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _flatten(item)
        else:
            yield item


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_ledger_custom_match_r131.py")
        actual = [item._testMethodName for item in _flatten(suite)]
        if len(actual) != len(EXPECTED) or set(actual) != EXPECTED:
            raise ValueError("Missing, duplicated or unexpected ledger regression")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and not result.skipped
                  and not result.unexpectedSuccesses
                  and result.testsRun == len(EXPECTED))
        print(f"R131 configurable ledger keys {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R131 configurable ledger keys HOLD: source tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
