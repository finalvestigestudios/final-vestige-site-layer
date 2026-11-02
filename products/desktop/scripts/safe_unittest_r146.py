"""Strict R146 Windows 11 reviewer privacy gate: exact named tests, no skips."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_r109_unknown_secret_option_is_redacted",
    "test_r109_secret_as_action_is_redacted",
    "test_r109_missing_review_is_redacted",
    "test_r109_duplicate_pin_is_rejected",
    "test_r109_duplicate_equals_dist_is_rejected",
    "test_r109_abbreviated_review_option_is_rejected",
    "test_r109_help_mixed_with_secret_is_hold",
    "test_r109_help_alone_is_static",
    "test_r122_unknown_secret_option_is_redacted",
    "test_r122_secret_app_choice_is_redacted",
    "test_r122_secret_state_choice_is_redacted",
    "test_r122_missing_observation_file_is_redacted",
    "test_r122_duplicate_pin_is_rejected",
    "test_r122_duplicate_app_is_rejected",
    "test_r122_abbreviated_observation_option_is_rejected",
    "test_r122_help_mixed_with_secret_is_hold",
    "test_r122_help_alone_is_static",
    "test_r123_unknown_secret_option_is_redacted",
    "test_r123_missing_witness_dir_is_redacted",
    "test_r123_duplicate_pin_is_rejected",
    "test_r123_duplicate_equals_report_is_rejected",
    "test_r123_abbreviated_review_option_is_rejected",
    "test_r123_unexpected_secret_positional_is_redacted",
    "test_r123_help_mixed_with_secret_is_hold",
    "test_r123_unicode_secret_flag_is_redacted",
    "test_r123_help_alone_is_static",
    "test_shared_parser_accepts_one_explicit_option",
    "test_shared_parser_rejects_duplicate_equals_forms",
    "test_shared_parser_never_embeds_rejected_choice_in_exception",
    "test_shared_parser_disables_prefix_abbreviations",
    "test_shared_parser_rejects_help_with_other_options",
    "test_valid_witness_writer_still_dispatches_to_record_one",
    "test_valid_progress_still_dispatches_to_inspect",
))


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_win11_private_review_cli_r146.py")
        names = [test._testMethodName for test in flatten(suite)]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError("R146 named review CLI test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        clean = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                 and not result.skipped and not result.unexpectedSuccesses)
        print(f"R146 private Win11 review CLI {'PASS' if clean else 'FAIL'}; "
              f"methods={result.testsRun}; "
              f"issues={len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if clean else 1
    except Exception:
        print("R146 private review CLI HOLD: required tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
