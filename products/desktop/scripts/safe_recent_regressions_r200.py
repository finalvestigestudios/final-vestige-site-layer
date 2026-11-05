"""Fail-closed, privacy-safe offline R194-R199 desktop audit regression matrix.

Run in normal and -OO modes from the repository root. A test exception,
fixture path, imported-module output or skip reason must not reach CI logs.
Only static audited test filenames and numerical results are emitted.
"""
from __future__ import annotations

import contextlib
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TESTS = ROOT / "products" / "desktop" / "tests"
TARGETS = (
    ("test_spend_semantic_atomic_r194.py", 28),
    ("test_spend_output_custody_r195.py", 29),
    ("test_policy_hunk_key_custody_r196.py", 22),
    ("test_policy_real_file_matrix_r197.py", 21),
    ("test_policy_nfkc_custody_r198.py", 26),
    ("test_policy_nfkc_physical_utf8_r199.py", 22),
)


def _run_private(tests: Path, filename: str) -> tuple[int, unittest.TestResult]:
    """Discard Python-level test/import output, retaining only aggregate counts.

    Deliberately do not use TextTestRunner: its failure tracebacks, skip
    reasons and exception representations can contain private fixture data.
    """
    with open(os.devnull, "w", encoding="utf-8") as sink:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            suite = unittest.TestLoader().discover(
                str(tests), pattern=filename, top_level_dir=str(tests))
            count = suite.countTestCases()
            result = unittest.TestResult()
            suite.run(result)
    return count, result


def run_matrix(tests: Path = TESTS, targets=TARGETS) -> bool:
    """Enforce audited test counts without echoing test-generated evidence.

    No financial files, accounts, network access, downloads or builds are used
    by this runner. A skip is included in executed totals but explicitly
    recorded and never represented as a passing test.
    """
    if not tests.is_dir() or tests.is_symlink():
        print("HOLD: desktop tests directory missing or linked", file=sys.stderr)
        return False
    seen = set()
    total = 0
    for filename, minimum in targets:
        if (type(filename) is not str
                or re.fullmatch(r"test_[a-z0-9_]+\.py", filename) is None
                or filename in seen or type(minimum) is not int or minimum <= 0):
            print("HOLD: invalid or repeated audited test selector", file=sys.stderr)
            return False
        seen.add(filename)
        source = tests / filename
        if not source.is_file() or source.is_symlink():
            print(f"HOLD: audited test module absent or linked: {filename}", file=sys.stderr)
            return False
        try:
            count, result = _run_private(tests, filename)
        except Exception:
            # No exception text or traceback: they may contain customer data.
            print(f"HOLD: {filename}: private audit execution unavailable", file=sys.stderr)
            return False
        if count < minimum:
            print(f"HOLD: {filename}: discovered {count}, minimum {minimum}",
                  file=sys.stderr)
            return False
        skipped = len(result.skipped)
        if (not result.wasSuccessful() or result.testsRun != count
                or skipped == count):
            print(f"HOLD: {filename}: audit regressions failed or all skipped "
                  f"({skipped} skipped)", file=sys.stderr)
            return False
        total += result.testsRun
        print(f"R201: {filename}: {result.testsRun} executed, "
              f"{skipped} skipped (not counted as passes)")
    print(f"R201: {total} audit regression executions across {len(seen)} modules; "
          "no release or production approval implied")
    return True


if __name__ == "__main__":
    # In the committed repository this sets up imports of fvs_suite.*.
    sys.path.insert(0, str(ROOT / "products" / "desktop"))
    raise SystemExit(0 if run_matrix() else 1)
