"""Privacy-safe exact-module diagnostics: never print exception text or paths.

Run the R119 synthetic 19-method suite in one interpreter. Only source-known
method names and aggregate results reach CI logs; test output is discarded.
"""
from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path
import unittest


EXPECTED_METHODS = 19
MODULE = "test_sealed_tamper_matrix_r119"


def main():
    tests = Path(__file__).resolve().parents[1] / "tests"
    sys.path.insert(0, str(tests))
    try:
        __import__(MODULE)
        suite = unittest.defaultTestLoader.loadTestsFromName(
            MODULE + ".AllEntryTamperR119Tests")
        if suite.countTestCases() != EXPECTED_METHODS:
            print("R119 HOLD: focused test inventory changed")
            return 1
        capture_stdout, capture_stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(capture_stdout), contextlib.redirect_stderr(capture_stderr):
            result = unittest.TestResult()
            suite.run(result)
        errors = result.failures + result.errors + result.unexpectedSuccesses
        failed = set()
        for item in errors:
            case = item[0] if isinstance(item, tuple) else item
            name = getattr(case, "_testMethodName", "")
            # Source-known method labels only; private failure values are never printed.
            if isinstance(name, str) and name.startswith("test_") and name.isidentifier():
                failed.add(name)
            else:
                failed.add("unknown_method")
        if result.testsRun != EXPECTED_METHODS or result.skipped:
            # Platform-unsupported symlinks are an allowed skip, but explicitly reported.
            if result.testsRun != EXPECTED_METHODS:
                failed.add("inventory_incomplete")
        if failed:
            print("R119 HOLD: failed source-owned methods: " + ", ".join(sorted(failed)))
            return 1
        print("R119 PASS: " + str(result.testsRun) + " synthetic methods; " +
              str(len(result.skipped)) + " platform skips; no private tracebacks")
        return 0
    except (Exception, SystemExit):
        print("R119 HOLD: focused test invocation unavailable; details redacted")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
