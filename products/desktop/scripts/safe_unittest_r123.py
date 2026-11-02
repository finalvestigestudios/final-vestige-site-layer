"""R123 exact-source-owned, privacy-redacted Win11 progress CI gate."""
from __future__ import annotations

import contextlib
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset((
    "test_zero_checks_is_hold_with_first_next_step",
    "test_one_pass_moves_next_check_without_approval",
    "test_one_fail_remains_a_release_hold",
    "test_per_app_queue_preserves_six_product_order",
    "test_orphan_witness_blocks_even_empty_matrix",
    "test_extra_witness_blocks_even_with_valid_pass",
    "test_extra_directory_blocks_progress",
    "test_prior_witness_tampering_blocks_progress",
    "test_changed_candidate_sha_blocks_progress",
    "test_preexisting_writer_lock_blocks_even_if_empty",
    "test_wrong_native_windows_build_blocks_progress",
    "test_missing_external_pin_fails_before_custody",
    "test_non_windows_machine_fails_before_custody",
    "test_review_in_candidate_directory_rejected",
    "test_progress_never_exposes_private_observation_or_pin",
    "test_cli_failure_is_redacted",
    "test_all_46_synthetic_pass_claims_still_uncertified",
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
                raise ValueError("Invalid R123 test method")
            output.append(name)
    return output


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_windows11_review_progress_r123.py")
        inventory = names(suite)
        if len(inventory) != len(REQUIRED) or set(inventory) != REQUIRED:
            raise ValueError("R123 required regression absent or duplicated")
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
        print(f"R123 private progress regression {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun} failed={len(bad)}")
        if bad:
            print("Source-owned failed method names: " + ", ".join(bad))
        return 0 if passed else 1
    except Exception:
        print("R123 private progress regression HOLD: inventory or execution unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
