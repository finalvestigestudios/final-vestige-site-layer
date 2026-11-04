"""Strict R181 gate: exactly 25 synthetic character-name tests; no skips."""
from __future__ import annotations
import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_latin_capital_to_cyrillic_capital", "test_cyrillic_to_latin",
    "test_greek_to_latin", "test_cyrillic_to_greek", "test_latin_to_greek",
    "test_lowercase_reverse", "test_two_characters_independent_names",
    "test_preserve_machine_numeric_citations", "test_no_source_text_repeated",
    "test_no_name_when_no_change", "test_no_name_when_substantive_change",
    "test_not_canonical_unicode_folding", "test_not_fullwidth_compatibility_folding",
    "test_direct_function_rejects_non_native_text", "test_exact_eight_names_shown",
    "test_nine_names_bounded", "test_eighteen_pairs_limit",
    "test_private_unicode_source_does_not_appear", "test_readable_caution_retained",
    "test_zero_hunks", "test_unsupported_cyrillic_unpaired",
    "test_output_repeatability", "test_limit_long_source_lines",
    "test_no_duplicate_ambiguous_pair", "test_names_are_ascii_only",
))


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_policy_character_names_r181.py")
        def flatten(group):
            for test in group:
                if isinstance(test, unittest.TestSuite):
                    yield from flatten(test)
                else:
                    yield test
        actual = list(flatten(suite))
        found = [test._testMethodName for test in actual]
        if (len(found) != 25 or set(found) != EXPECTED or
                any(type(test).__name__ != "PolicyCharacterNamesR181" for test in actual)):
            raise ValueError("R181 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.testsRun == 25 and result.wasSuccessful() and
                  not result.skipped and not result.unexpectedSuccesses)
        print(f"R181 character names {'PASS' if passed else 'FAIL'}; methods={result.testsRun}; "
              f"failures={len(result.failures)}; errors={len(result.errors)}; "
              f"skips={len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R181 HOLD: expected tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
