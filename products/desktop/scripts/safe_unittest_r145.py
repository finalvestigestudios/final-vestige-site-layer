"""R145 exact, mandatory source-snapshot custody tests; zero skips or xfails."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_spend_reads_independent_private_copy",
    "test_ledger_reads_two_distinct_copy_directories",
    "test_invoice_reads_copy_not_original",
    "test_policy_copy_preserves_filenames",
    "test_policy_same_basename_across_directories",
    "test_ledger_same_basename_across_directories",
    "test_policy_bom_bytes_preserved",
    "test_spend_snapshot_mismatched_digest_holds_before_engine",
    "test_policy_snapshot_mismatched_digest_holds_before_engine",
    "test_copy_corrupted_after_write_holds_before_engine",
    "test_original_changes_during_replay_holds",
    "test_report_tamper_holds",
    "test_sources_and_report_preserved",
    "test_published_folder_has_no_new_files",
    "test_temp_copy_removed_after_success",
    "test_temp_copy_removed_after_failure",
    "test_ledger_custom_decimal_and_columns",
    "test_invoice_window_still_bound",
    "test_header_only_financial_report_still_holds",
    "test_premium_kind_rejected_before_snapshot",
    "test_snapshot_failure_cli_redacts_confidential_value",
    "test_repeated_replays_have_identical_receipts",
    "test_directory_masquerading_as_csv_rejected",
))


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_replay_source_snapshots_r145.py")
        names = [test._testMethodName for test in flatten(suite)]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError("R145 required test inventory has changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        clean = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                 and not result.skipped and not result.unexpectedSuccesses)
        print(f"R145 private source snapshot custody {'PASS' if clean else 'FAIL'}; "
              f"methods={result.testsRun}; "
              f"issues={len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if clean else 1
    except Exception:
        print("R145 source snapshot custody HOLD: required tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
