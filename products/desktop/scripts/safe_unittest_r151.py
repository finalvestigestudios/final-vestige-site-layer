"""Fail-closed R151 29-method synthetic suite with privacy-safe diagnostics."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_mixed_unrelated_change_still_cites_compatibility_pair",
    "test_other_sentence_edits_in_distinct_hunk",
    "test_fullwidth_compatibility_pair",
    "test_superscript_compatibility_pair",
    "test_ligature_compatibility_pair",
    "test_math_bold_compatibility_pair",
    "test_roman_compatibility_pair",
    "test_two_unique_pairs_one_hunk",
    "test_newline_missing_still_reports",
    "test_source_line_numbers_not_diff_display_indices",
    "test_reorder_with_equal_codepoint_counts_cited",
    "test_no_pair_for_real_numeric_change",
    "test_no_pair_for_mixed_real_and_unicode_same_line",
    "test_no_pair_for_canonical_nfc_composition",
    "test_no_pair_for_kelvin_canonical_character",
    "test_no_pair_for_cyrillic_latin_lookalike",
    "test_no_pair_for_addition_without_removal",
    "test_no_pair_for_removal_without_addition",
    "test_identical_policy_no_local_review",
    "test_bom_only_no_local_review",
    "test_crlf_only_no_local_review",
    "test_ambiguous_duplicate_folded_lines_not_paired",
    "test_bounded_to_sixteen_pairs",
    "test_deterministic_replay",
    "test_originals_and_private_paths_not_emitted",
    "test_human_review_not_compliance_authorization",
    "test_existing_report_not_overwritten",
    "test_invalid_utf8_rejects_without_report",
    "test_bidi_control_rejects_without_report",
))

def flatten(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from flatten(case)
        else:
            yield case

def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_policy_local_compatibility_r151.py")
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED or
                any(type(case).__name__ != "PolicyLocalCompatibilityR151"
                    for case in cases)):
            raise ValueError("R151 required test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        clean = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                 and not result.skipped and not result.unexpectedSuccesses)
        print(f"R151 Policy Delta local compatibility PASS; methods={result.testsRun}; "
              f"issues=0" if clean else
              f"R151 Policy Delta local compatibility FAIL; methods={result.testsRun}; "
              f"issues={len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if clean else 1
    except Exception:
        print("R151 Policy Delta local compatibility HOLD: required tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
