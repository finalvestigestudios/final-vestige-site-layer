"""R144 exact test-inventory, two-mode replay evidence gate (zero skipped)."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset(("test_invalid_product_value_redacted", "test_invalid_integer_window_redacted", "test_unknown_option_name_redacted", "test_unknown_option_value_redacted", "test_orphan_positional_value_redacted", "test_missing_product_redacted", "test_missing_report_redacted", "test_missing_source_redacted", "test_source_option_missing_value_redacted", "test_option_shaped_source_value_redacted", "test_premium_product_name_redacted", "test_unicode_control_value_redacted", "test_noninteger_boolean_text_window_redacted", "test_integer_outside_window_bound_holds", "test_inapplicable_mapping_option_holds", "test_empty_argument_list_holds_without_usage", "test_double_dash_stray_private_position_holds", "test_bad_arguments_leave_original_bytes_unchanged", "test_valid_spend_replay_keeps_success_contract", "test_native_python_module_invalid_option_redacted"))

def flatten(suite):
    for member in suite:
        if isinstance(member, unittest.TestSuite):
            yield from flatten(member)
        else:
            yield member

def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_replay_private_cli_r144.py")
        names = [case._testMethodName for case in flatten(suite)]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError("R144 mandatory test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R144 redacted replay CLI parsing {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; "
              f"issues={len(result.failures)+len(result.errors)+len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R144 replay evidence HOLD: required tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
