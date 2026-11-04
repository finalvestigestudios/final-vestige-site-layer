"""Fail-closed 24-method Policy Delta Unicode evidence gate (no private data)."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_composed_accent_replaced_with_combining_mark",
    "test_reverse_accent_counts",
    "test_hangul_counts",
    "test_japanese_combining_mark_counts",
    "test_reordered_marks_explicitly_report_same_counts",
    "test_identical_raw_lines_no_codepoint_cue",
    "test_substantive_only_change_not_mislabeled",
    "test_nfkc_only_change_not_mislabeled",
    "test_private_source_text_not_echoed",
    "test_human_review_notice_retained",
    "test_numeric_metadata_ignores_unchanged_ascii",
    "test_numeric_metadata_repeated_counts",
    "test_supplementary_nonascii_codepoint_format",
    "test_only_after_has_nonascii", "test_only_before_has_nonascii",
    "test_twelve_distinct_changes_within_limit",
    "test_thirteen_distinct_changes_are_truncated",
    "test_exactly_64_distinct_unicode_points_accepted",
    "test_65_distinct_before_fail_closed_on_detail",
    "test_65_distinct_after_fail_closed_on_detail",
    "test_multiple_hunks_have_independent_counts",
    "test_omitted_hunk_has_no_extra_detail",
    "test_reordered_hunk_storage_produces_deterministic_report",
    "test_line_endings_not_confused_with_normalization",
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
            start_dir=str(ROOT / "tests"), pattern="test_policy_unicode_codepoints_r179.py")
        loaded = list(flatten(suite))
        names = [case._testMethodName for case in loaded]
        if (len(names) != 24 or len(set(names)) != 24 or set(names) != EXPECTED
                or any(type(case).__name__ != "PolicyCodepointNavigationR179" for case in loaded)):
            raise ValueError("R179 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.testsRun == 24 and result.wasSuccessful()
                  and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print("R179 Unicode codepoints " + ("PASS" if passed else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failed))
        return 0 if passed else 1
    except Exception:
        print("R179 HOLD: exact test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
