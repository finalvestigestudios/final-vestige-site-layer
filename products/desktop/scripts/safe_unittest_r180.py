"""Fail-closed 34-method Policy Delta confusable evidence gate; synthetic only."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
UNIT = frozenset((
    "test_latin_to_cyrillic_a", "test_cyrillic_to_latin_a",
    "test_greek_omicron_to_latin_o", "test_latin_o_to_cyrillic_o",
    "test_cyrillic_to_greek_same_shape", "test_two_substitutions_in_one_line",
    "test_substantive_change_not_paired", "test_changed_case_not_paired",
    "test_canonical_accent_not_paired", "test_nfkc_fullwidth_not_paired",
    "test_unchanged_text_not_paired", "test_no_cross_hunk_paired",
    "test_duplicate_old_suppressed", "test_duplicate_new_suppressed",
    "test_only_added_or_removed", "test_private_source_not_duplicated",
    "test_caveat_and_human_review", "test_deterministic_sorted_physical_lines",
    "test_two_hunks_kept_separate", "test_max_sixteen_pairs",
    "test_max_eight_codepoint_changes", "test_long_line_not_explored",
    "test_short_line_limit_exact", "test_invalid_line_number_skipped",
    "test_str_subclass_not_executed", "test_regular_cyrillic_language_no_flag",
    "test_no_hunks",
))
INTEGRATION = frozenset((
    "test_before_after_source_coordinates_and_codepoints",
    "test_mixed_substantive_revision_still_cites_local_pair",
    "test_disjoint_hunks_have_correct_physical_coordinates",
    "test_ambiguous_duplicate_lines_never_paired",
    "test_regular_substantive_change_not_mislabeled",
    "test_no_overwrite_of_existing_evidence",
    "test_failing_unsafe_input_creates_no_report",
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
            pattern="test_policy_confusables*_r180.py")
        methods = list(flatten(suite))
        found = {
            "PolicyConfusableR180": set(),
            "PolicyConfusableIntegrationR180": set(),
        }
        for method in methods:
            cls = type(method).__name__
            if cls not in found or method._testMethodName in found[cls]:
                raise ValueError("unexpected R180 test or duplicate")
            found[cls].add(method._testMethodName)
        if len(methods) != 34 or found != {
            "PolicyConfusableR180": UNIT,
            "PolicyConfusableIntegrationR180": INTEGRATION,
        }:
            raise ValueError("R180 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.testsRun == 34 and result.wasSuccessful() and
                  not result.skipped and not result.unexpectedSuccesses)
        failures = sorted({case._testMethodName for case, _ in
                           (*result.errors, *result.failures)})
        print("R180 policy look-alike " + ("PASS" if passed else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failures))
        return 0 if passed else 1
    except Exception:
        print("R180 HOLD: exact test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
