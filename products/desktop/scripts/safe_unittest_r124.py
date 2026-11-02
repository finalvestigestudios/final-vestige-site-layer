"""R124 source-owned, privacy-safe, zero-skip witness-inventory CI gate."""
from __future__ import annotations

import contextlib
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset((
    "test_empty_inventory_accepts_zero_expected",
    "test_clean_existing_inventory_accepts_next_record",
    "test_orphan_other_app_prevents_first_record",
    "test_orphan_other_check_prevents_next_record",
    "test_directory_entry_prevents_record",
    "test_hidden_temp_entry_prevents_record",
    "test_unreferenced_same_target_prevents_record",
    "test_missing_referenced_note_raises_hold",
    "test_hardlinked_referenced_note_raises_hold",
    "test_symlinked_referenced_note_raises_hold",
    "test_injected_orphan_during_commit_rolls_back",
    "test_witness_and_review_folder_co_location_rejected",
    "test_cleared_orphan_allows_record_after_human_review",
    "test_inventory_does_not_mutate_existing_private_evidence",
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
                raise ValueError("Invalid R124 method")
            output.append(name)
    return output


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_windows11_witness_inventory_r124.py")
        found = names(suite)
        if len(found) != len(REQUIRED) or set(found) != REQUIRED:
            raise ValueError("Missing, duplicate or unexpected R124 method")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        bad = sorted({case._testMethodName for case, _ in
                      result.failures + result.errors + result.skipped}
                     | {case._testMethodName for case in result.unexpectedSuccesses})
        if not set(bad).issubset(REQUIRED):
            raise ValueError("Unknown failed R124 method")
        passed = (result.wasSuccessful() and not result.skipped
                  and result.testsRun == len(REQUIRED))
        print(f"R124 witness inventory regression {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun} failed={len(bad)}")
        if bad:
            print("Source-owned failed methods: " + ", ".join(bad))
        return 0 if passed else 1
    except Exception:
        print("R124 witness inventory HOLD: inventory or execution unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
