"""Fail-closed, offline R194-R199 desktop audit regression matrix.

Run with normal Python and again with -OO from the repository root. Each
pattern is an exact filename and must discover at least the audited number
of tests; a zero-test unittest discovery must NEVER count as a pass.
"""
from __future__ import annotations

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


def run_matrix(tests: Path = TESTS, targets=TARGETS) -> bool:
    """Execute all named modules without swallowing missing or failing tests.

    No financial files, accounts, network access, downloads or builds are used.
    A platform-specific unittest skip remains visible in stderr and is not
    misrepresented as a passed case; the native Windows gate is separate.
    """
    if not tests.is_dir():
        print("HOLD: desktop tests directory missing", file=sys.stderr)
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
        suite = unittest.TestLoader().discover(str(tests), pattern=filename,
                                               top_level_dir=str(tests))
        count = suite.countTestCases()
        if count < minimum:
            print(f"HOLD: {filename}: discovered {count}, minimum {minimum}",
                  file=sys.stderr)
            return False
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        if (not result.wasSuccessful() or result.testsRun != count
                or len(result.skipped) == count):
            print(f"HOLD: {filename}: audit regressions failed or all skipped "
                  f"({len(result.skipped)} skipped)", file=sys.stderr)
            return False
        total += result.testsRun
        print(f"R200: {filename}: {result.testsRun} executed, "
              f"{len(result.skipped)} skipped (platform-specific skips are not passes)")
    print(f"R200: {total} audit regression executions across {len(seen)} modules; "
          "no release or production approval implied")
    return True


if __name__ == "__main__":
    # In the committed repository this sets up imports of fvs_suite.*.
    sys.path.insert(0, str(ROOT / "products" / "desktop"))
    raise SystemExit(0 if run_matrix() else 1)
