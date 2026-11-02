"""R125 privacy-safe exact-inventory zero-skip file-identity gate."""
from __future__ import annotations

import contextlib
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset((
    "test_clean_record_is_human_only",
    "test_owned_note_rollback_after_replace_error",
    "test_replaced_identical_note_survives_failed_write",
    "test_replaced_different_note_survives_failed_write",
    "test_identical_review_replacement_causes_hold",
    "test_symlinked_review_matrix_rejected",
    "test_hardlinked_review_matrix_rejected",
    "test_directory_matrix_rejected",
    "test_missing_matrix_rejected",
    "test_production_module_has_no_assert_statements",
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
                raise ValueError("Invalid source method")
            output.append(name)
    return output


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_windows11_witness_identity_r125.py")
        found = names(suite)
        if len(found) != len(REQUIRED) or set(found) != REQUIRED:
            raise ValueError("Missing, duplicate or unexpected R125 method")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        bad = sorted({case._testMethodName for case, _ in
                      result.failures + result.errors + result.skipped}
                     | {case._testMethodName for case in result.unexpectedSuccesses})
        if not set(bad).issubset(REQUIRED):
            raise ValueError("Unknown failed method")
        passed = (result.wasSuccessful() and not result.skipped
                  and result.testsRun == len(REQUIRED))
        print(f"R125 witness identity regression {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun} failed={len(bad)}")
        if bad:
            print("Source-owned failed methods: " + ", ".join(bad))
        return 0 if passed else 1
    except Exception:
        print("R125 witness identity HOLD: source inventory or execution unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
