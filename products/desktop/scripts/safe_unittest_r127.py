"""R127 privacy-safe, exact-method, zero-skip human observation custody gate."""
from __future__ import annotations

import contextlib
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset((
    "test_stable_standalone_note_passes_without_release",
    "test_oversized_note_fails_without_new_witness",
    "test_invalid_utf8_note_fails_closed",
    "test_note_reusing_raw_r9_report_path_is_rejected",
    "test_previous_valid_witness_cannot_be_recycled_as_next_observation",
    "test_direct_note_symlink_is_rejected_without_following",
    "test_note_parent_symlink_is_rejected_before_reading",
    "test_hardlinked_note_is_not_accepted",
    "test_replaced_note_before_open_is_rejected_even_if_bytes_identical",
    "test_changed_note_after_open_is_rejected_on_both_platforms",
    "test_nonregular_file_is_rejected_without_blocking",
    "test_redacted_cli_error_contains_no_private_observation_or_path",
    "test_no_assertions_in_observation_gate_or_writer",
))
METHOD = re.compile(r"test_[a-z][a-z0-9_]{0,100}$")


def all_names(suite):
    names = []
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            names.extend(all_names(test))
        else:
            method = getattr(test, "_testMethodName", None)
            if type(method) is not str or METHOD.fullmatch(method) is None:
                raise ValueError("Unknown test identity")
            names.append(method)
    return names


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_windows11_observation_input_r127.py")
        found = all_names(suite)
        if len(found) != len(REQUIRED) or set(found) != REQUIRED:
            raise ValueError("Missing, duplicate or unexpected R127 method")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        bad = sorted({test._testMethodName for test, _ in
                      result.failures + result.errors + result.skipped}
                     | {test._testMethodName for test in result.unexpectedSuccesses})
        passed = (result.wasSuccessful() and not result.skipped
                  and result.testsRun == len(REQUIRED))
        print(f"R127 per-check private observation custody {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun} failed={len(bad)}")
        if bad:
            print("Source-owned failed methods: " +
                  ", ".join(name for name in bad if name in REQUIRED))
        return 0 if passed else 1
    except Exception:
        print("R127 private observation custody HOLD: source inventory or execution unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
