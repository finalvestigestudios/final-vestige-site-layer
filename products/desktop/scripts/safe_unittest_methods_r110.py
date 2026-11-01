"""Privacy-safe diagnostic runner for R109/R110 synthetic acceptance tests.

Only static unittest method names and aggregate counts may reach GitHub logs.
Never print captured tracebacks, file names, exception values or test output.
"""
from __future__ import annotations

import contextlib
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = "test_windows11_manual_acceptance_r109.py"
SAFE_NAME = re.compile(r"test_[a-z][a-z0-9_]{0,100}\\Z")


def collect_names(cases):
    names = []
    for one in cases:
        if isinstance(one, unittest.TestSuite):
            names.extend(collect_names(one))
        else:
            method = getattr(one, "_testMethodName", None)
            if type(method) is not str or SAFE_NAME.fullmatch(method) is None:
                raise ValueError("Unrecognized source test name")
            names.append(method)
    return names


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern=PATTERN)
        admitted = collect_names(suite)
        if len(admitted) < 55 or len(set(admitted)) != len(admitted):
            raise ValueError("Missing or duplicate synthetic test methods")
        result = unittest.TestResult()
        # A failing test may otherwise leak customer file paths in a traceback
        # or exception, even when the test uses only synthetic private fixtures.
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        failed = sorted({x._testMethodName for x, _ in
                         (result.failures + result.errors + result.unexpectedSuccesses)})
        skipped = sorted({x._testMethodName for x, _ in result.skipped})
        if not set(failed + skipped).issubset(set(admitted)):
            raise ValueError("Unrecognized test result")
        status = "PASS" if result.wasSuccessful() and not skipped else "FAIL"
        print(f"R110 synthetic suite {status}; ran={result.testsRun} expected={len(admitted)} "
              f"failures={len(result.failures)} errors={len(result.errors)} "
              f"skipped={len(skipped)}")
        if failed or skipped:
            print("Static failing/skipped method IDs: " +
                  ", ".join(failed + skipped))
        return 0 if status == "PASS" else 1
    except (ValueError, OSError, ImportError, RuntimeError):
        print("R110 synthetic suite HOLD: static test inventory or execution unavailable")
        return 2


if __name__ == "__main__":
    sys.exit(main())
