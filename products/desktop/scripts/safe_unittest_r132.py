"""R132 strict privacy-redacted LedgerDiff native accessibility test gate."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_ledger_has_two_visible_key_entry_tab_stops",
    "test_original_free_app_tab_order_unchanged",
    "test_ledger_five_entry_native_snapshot_is_valid",
    "test_legacy_ledger_tab_order_is_no_longer_sufficient",
    "test_reversed_ledger_match_key_tab_order_blocks",
    "test_missing_optional_ledger_entry_blocks",
    "test_extra_ledger_entry_blocks",
    "test_missing_left_key_label_blocks",
    "test_missing_right_key_label_blocks",
    "test_ledger_key_labels_do_not_leak_into_other_free_apps",
    "test_source_owned_ledger_shortcuts_remain_required",
    "test_scaled_ledger_five_entries_three_browse_at_both_scales",
    "test_scaled_ledger_rejects_old_three_entry_inventory",
    "test_scaled_ledger_rejects_missing_browse",
    "test_scaled_other_free_apps_still_need_one_output_entry",
    "test_scaled_entry_bool_is_not_a_count",
    "test_ledger_cancel_events_still_require_no_engine_calls",
    "test_premium_apps_rejected_by_all_three_native_contracts",
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
            pattern="test_ledger_native_access_r132.py")
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
        print(f"R132 native ledger access {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R132 native ledger access HOLD: source tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
