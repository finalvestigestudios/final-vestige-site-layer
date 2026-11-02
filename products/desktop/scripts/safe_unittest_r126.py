"""R126 privacy-safe, source-owned, exact-inventory zero-skip capture-time gate."""
from __future__ import annotations

import contextlib
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset((
    "test_writer_records_v2_capture_utc_and_no_release",
    "test_capture_time_distinct_from_session_anchor",
    "test_capture_time_of_two_checks_can_differ",
    "test_v2_missing_capture_time_holds",
    "test_v2_unexpected_field_holds",
    "test_v2_backdated_before_session_holds_even_if_resealed",
    "test_v2_future_capture_holds_even_if_resealed",
    "test_v2_offset_timezone_holds",
    "test_v2_invalid_calendar_date_holds",
    "test_v2_nonstring_capture_holds",
    "test_v2_future_session_anchor_prevents_write",
    "test_v2_capture_mutation_without_resigning_holds",
    "test_v1_legacy_note_remains_verifiable",
    "test_v1_rejects_injected_v2_field",
    "test_unknown_witness_version_holds",
    "test_no_asserts_in_witness_admission_code",
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
            pattern="test_windows11_capture_clock_r126.py")
        found = all_names(suite)
        if len(found) != len(REQUIRED) or set(found) != REQUIRED:
            raise ValueError("Missing, duplicate or unexpected R126 method")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        bad = sorted({test._testMethodName for test, _ in
                      result.failures + result.errors + result.skipped}
                     | {test._testMethodName for test in result.unexpectedSuccesses})
        passed = (result.wasSuccessful() and not result.skipped
                  and result.testsRun == len(REQUIRED))
        print(f"R126 per-check capture provenance {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun} failed={len(bad)}")
        if bad:
            print("Source-owned failed methods: " +
                  ", ".join(name for name in bad if name in REQUIRED))
        return 0 if passed else 1
    except Exception:
        print("R126 capture provenance HOLD: source inventory or execution unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
