"""R133 privacy-redacted, no-skip exact-inventory LedgerDiff layout gate."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_exact_two_input_row_plan",
    "test_each_rendered_control_gets_its_own_row",
    "test_first_controls_preserve_native_tab_creation_order",
    "test_actions_and_hint_follow_every_editable_control",
    "test_title_and_disclaimer_rows_are_not_overwritten",
    "test_bool_float_and_changed_file_inventory_fail_closed",
    "test_repeat_has_identical_rows",
    "test_mutating_returned_map_does_not_modify_future_layout",
    "test_production_ui_selects_stacked_ledger_only",
    "test_other_apps_stay_in_original_tiers",
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
            pattern="test_ledger_responsive_layout_r133.py")
        actual = [item._testMethodName for item in _flatten(suite)]
        if len(actual) != len(EXPECTED) or set(actual) != EXPECTED:
            raise ValueError("Incomplete or unexpected responsive-layout inventory")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and not result.skipped
                  and not result.unexpectedSuccesses
                  and result.testsRun == len(EXPECTED))
        print(f"R133 LedgerDiff 400% responsive reflow {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R133 LedgerDiff responsive layout HOLD: source tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
