"""R137 GrantAudit budget custody gate: exact inventory, zero skips, redacted logs."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_legacy_source_rows_and_digests",
    "test_linked_source_rows_and_digests",
    "test_legacy_multiline_claim_physical_lines",
    "test_linked_credit_claim_rows",
    "test_multiple_budget_programs_keep_distinct_lines",
    "test_missing_budget_has_no_invented_row",
    "test_budget_only_program_has_no_claim_rows",
    "test_legacy_output_is_deterministic",
    "test_linked_output_is_deterministic",
    "test_sources_remain_byte_identical",
    "test_budget_digest_matches_manifest",
    "test_ledger_digest_matches_manifest",
    "test_linked_direct_api_has_same_custody",
    "test_normalization_review_survives_citations",
    "test_low_decimal_precision_keeps_exact_total",
    "test_duplicate_budget_fails_without_any_reports",
    "test_bom_claim_and_quoted_newline_preserve_lines",
    "test_existing_reports_are_not_overwritten",
))


def flatten(suite):
    for entry in suite:
        if isinstance(entry, unittest.TestSuite):
            yield from flatten(entry)
        else:
            yield entry


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_grant_budget_custody_r137.py",
        )
        names = [case._testMethodName for case in flatten(suite)]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError("R136 policy change-index test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R137 grant budget custody {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R137 grant budget custody HOLD: source tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
