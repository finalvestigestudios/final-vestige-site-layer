"""R136 Policy Delta change-index gate: exact inventory, zero skips, redacted logs."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_one_line_replacement_has_exact_before_after_citations",
    "test_insertion_at_start_has_no_changed_before_line",
    "test_insertion_at_end_cites_last_new_line",
    "test_deletion_at_start_has_no_changed_after_line",
    "test_deletion_at_end_cites_last_old_line",
    "test_mixed_one_for_two_preserves_independent_ranges",
    "test_distant_edits_are_two_numbered_hunks",
    "test_close_edits_group_without_inflating_change_counts",
    "test_context_lines_are_not_counted_as_changes",
    "test_completely_empty_before_source_indexes_addition",
    "test_identical_bytes_produce_zero_index_and_review_note",
    "test_utf8_bom_only_difference_indexes_zero_changes",
    "test_crlf_only_change_is_indexed_and_cr_escaped",
    "test_unterminated_last_lines_keep_index_and_eof_markers",
    "test_unicode_hidden_difference_visible_but_citations_stable",
    "test_original_source_sha_and_privacy_are_maintained",
    "test_same_inputs_generate_byte_identical_report",
    "test_disallowed_control_fails_without_partial_report",
    "test_existing_report_is_never_overwritten",
    "test_public_engine_entrypoint_produces_indexed_report",
))


def flatten(suite):
    for entry in suite:
        if isinstance(entry, unittest.TestSuite):
            yield from flatten(entry)
        else:
            yield entry


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_policy_change_index_r136.py",
        )
        names = [case._testMethodName for case in flatten(suite)]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError("R136 policy change-index test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R136 policy change index {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R136 policy change index HOLD: source tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
