"""R122 source-owned, redacted, exact-24 method CI gate; normal and -OO."""
from __future__ import annotations

import contextlib
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset((
    "test_one_observed_pass_updates_exact_check_only",
    "test_fail_state_remains_a_hold",
    "test_two_different_checks_are_reproducible",
    "test_already_recorded_check_never_overwritten",
    "test_preexisting_unreferenced_note_is_not_overwritten",
    "test_short_observation_fails_before_witness",
    "test_bidi_observation_is_rejected",
    "test_invalid_app_rejected",
    "test_invalid_check_rejected",
    "test_unperformed_conclusion_rejected",
    "test_missing_external_pin_rejected_before_load",
    "test_windows11_required_before_source_custody",
    "test_reported_build_must_match_native_build",
    "test_invalid_existing_witness_blocks_additional_notes",
    "test_symlink_witness_folder_rejected",
    "test_witness_directory_inside_executables_rejected",
    "test_review_under_executable_directory_rejected",
    "test_duplicate_review_json_keys_rejected",
    "test_cooperative_lock_existing_rejected",
    "test_atomic_review_failure_removes_new_note",
    "test_failed_write_releases_own_empty_lock",
    "test_do_not_clear_nonempty_modified_lock",
    "test_redacted_cli_failure_never_prints_observation",
    "test_no_asserts_in_production_gate",
))
NAME = re.compile(r"test_[a-z][a-z0-9_]{0,100}$")


def names(suite):
    output = []
    for child in suite:
        if isinstance(child, unittest.TestSuite):
            output.extend(names(child))
        else:
            name = getattr(child, "_testMethodName", "")
            if type(name) is not str or NAME.fullmatch(name) is None:
                raise ValueError("Invalid test inventory")
            output.append(name)
    return output


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_windows11_witness_writer_r122.py")
        inventory = names(suite)
        if len(inventory) != len(REQUIRED) or set(inventory) != REQUIRED:
            raise ValueError("R122 required regression is absent or duplicated")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        bad = sorted({case._testMethodName for case, _ in
                      result.failures + result.errors + result.skipped}
                     | {case._testMethodName for case in result.unexpectedSuccesses})
        if not set(bad).issubset(REQUIRED):
            raise ValueError("Untrusted test method")
        passed = (result.wasSuccessful() and not result.skipped
                  and result.testsRun == len(REQUIRED))
        print(f"R122 private witness source regression {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun} failed={len(bad)}")
        if bad:
            print("Source-owned failed method names: " + ", ".join(bad))
        return 0 if passed else 1
    except Exception:
        print("R122 private witness source regression HOLD: inventory or execution unavailable")
        return 2


if __name__ == "__main__":
    sys.exit(main())
