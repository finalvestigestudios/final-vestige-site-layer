"""R128 exact-method, zero-skip, privacy-redacted Win11 witness regression gate."""
from __future__ import annotations

import contextlib
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = frozenset((
    "test_plain_legacy_witness_remains_valid",
    "test_multilingual_visible_text_combining_accents_preserved",
    "test_tabs_newlines_and_ascii_spaces_remain_valid",
    "test_c1_controls_rejected",
    "test_bidirectional_and_zero_width_formats_rejected",
    "test_nonstandard_whitespace_rejected",
    "test_variation_selectors_rejected",
    "test_blank_filler_glyphs_rejected",
    "test_surrogate_and_tag_controls_rejected",
    "test_writer_refuses_invisible_input_without_new_evidence",
    "test_rehashed_existing_witness_cannot_hide_invisible_input",
    "test_premium_locked_witness_uses_same_guard",
    "test_privacy_safe_cli_error_on_invisible_witness",
    "test_no_asserts_in_validator",
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
            pattern="test_windows11_visible_observations_r128.py")
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
        print(f"R128 unambiguous reviewer testimony {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun} failed={len(bad)}")
        if bad:
            print("Source-owned failed methods: " +
                  ", ".join(name for name in bad if name in REQUIRED))
        return 0 if passed else 1
    except Exception:
        print("R128 reviewer testimony HOLD: source inventory or execution unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
