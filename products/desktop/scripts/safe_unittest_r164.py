"""Strict no-skip private R164 action-key camouflage method inventory."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_six_canonical_keys_accepted",
    "test_approved_comment_suffix_accepted",
    "test_unquoted_key_space_before_colon_rejected",
    "test_single_quoted_key_rejected",
    "test_double_quoted_key_rejected",
    "test_inline_map_rejected",
    "test_inline_quoted_map_rejected",
    "test_unicode_escape_key_rejected",
    "test_hex_escape_key_rejected",
    "test_long_unicode_escape_key_rejected",
    "test_explicit_yaml_key_rejected",
    "test_merge_mapping_rejected",
    "test_missing_key_rejected",
    "test_duplicate_known_key_rejected",
    "test_unexpected_indent_rejected",
    "test_unexpected_top_level_key_rejected",
    "test_shell_script_camouflage_rejected",
    "test_embedded_nested_value_key_rejected",
    "test_null_and_tab_rejected",
    "test_non_string_rejected",
    "test_oversized_input_rejected",
))


def _cases(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from _cases(case)
        else:
            yield case


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_action_key_custody_r164.py")
        cases = list(_cases(suite))
        methods = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "ActionKeyCustodyR164" for case in cases)):
            raise ValueError("R164 strict test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        failures = sorted({case._testMethodName for case, _ in
                           (*result.errors, *result.failures)})
        print(f"R164 action-key custody {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors) + len(result.failures) + len(result.skipped)}; "
              f"failed_methods={','.join(failures)}")
        return 0 if passed else 1
    except Exception:
        print("R164 action-key custody HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
