"""R129 exact-method, zero-skip, privacy-redacted Win11 directory-custody regression gate."""
from __future__ import annotations

import contextlib
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset((
    "test_ordinary_directory_ancestors_are_stable",
    "test_ordinary_nested_private_file_remains_readable",
    "test_linked_ancestor_blocks_r9_source_read",
    "test_linked_review_parent_blocks_matrix_read",
    "test_linked_witness_parent_blocks_private_note_read",
    "test_linked_leaf_still_blocked",
    "test_linked_witness_folder_blocks_empty_matrix",
    "test_linked_witness_ancestor_blocks_empty_matrix",
    "test_linked_ancestor_blocks_existing_pass_evidence",
    "test_junction_ancestor_blocks_source_read_without_privilege",
    "test_reparse_point_attribute_rejected_without_platform_skip",
    "test_post_read_parent_identity_drift_fails_closed",
    "test_not_a_directory_parent_rejected",
    "test_valid_six_app_pending_matrix_remains_hard_hold",
    "test_valid_free_and_premium_notes_remain_source_bound",
    "test_no_assert_bypass_or_path_leak_in_cli",
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
                raise ValueError("Unknown test method")
            names.append(method)
    return names


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_windows11_parent_path_custody_r129.py")
        found = all_names(suite)
        if len(found) != len(REQUIRED) or set(found) != REQUIRED:
            raise ValueError("Missing, duplicate or unexpected test")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        bad = sorted({test._testMethodName for test, _ in
                      result.failures + result.errors + result.skipped}
                     | {test._testMethodName for test in result.unexpectedSuccesses})
        passed = result.wasSuccessful() and not result.skipped and result.testsRun == len(REQUIRED)
        print(f"R129 private parent-path custody {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun} failed={len(bad)}")
        if bad:
            print("Source-owned failed methods: " +
                  ", ".join(name for name in bad if name in REQUIRED))
        return 0 if passed else 1
    except Exception:
        print("R129 parent-path custody HOLD: source inventory or execution unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
