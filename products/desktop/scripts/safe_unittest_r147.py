"""R147 exact-source offline replay argument custody gate; zero skips/failures.

Source-owned named tests must run on both CI operating systems in regular and
optimized (-OO) Python. An empty or altered test set is a hard CI failure.
"""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_duplicate_kind_flag_rejected",
    "test_duplicate_kind_equals_rejected",
    "test_duplicate_report_flag_rejected",
    "test_duplicate_report_equals_rejected",
    "test_duplicate_window_days_rejected",
    "test_duplicate_left_match_mapping_rejected",
    "test_duplicate_right_match_mapping_rejected",
    "test_duplicate_left_amount_mapping_rejected",
    "test_duplicate_right_amount_mapping_rejected",
    "test_mixed_equals_first_report_rejected",
    "test_mixed_equals_second_kind_rejected",
    "test_abbreviated_kind_rejected",
    "test_abbreviated_report_rejected",
    "test_abbreviated_source_rejected",
    "test_abbreviated_window_rejected",
    "test_abbreviated_left_match_rejected",
    "test_abbreviated_left_amount_rejected",
    "test_secret_unknown_option_redacted",
    "test_mixed_long_help_with_secret_rejected",
    "test_mixed_short_help_with_secret_rejected",
    "test_double_dash_separator_rejected",
    "test_nonstr_argument_rejected",
    "test_standalone_help_is_static_without_source_reads",
    "test_two_explicit_sources_still_dispatch_for_ledger",
    "test_three_sources_for_spend_map_hold_before_engine",
    "test_real_spend_replay_valid_after_parser_hardening",
    "test_real_ledger_replay_allows_two_sources",
    "test_real_policy_replay_allows_two_sources",
    "test_rejected_duplicate_does_not_modify_originals",
    "test_real_subprocess_duplicate_report_does_not_leak",
    "test_parser_exception_never_contains_private_choice",
    "test_premium_kind_rejected_before_verifier",
    "test_missing_kind_never_reaches_verifier",
))


def flatten(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from flatten(case)
        else:
            yield case


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_replay_argv_custody_r147.py")
        cases = list(flatten(suite))
        named = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(named) != EXPECTED
                or any(type(case).__name__ != "ReplayArgvCustodyR147" for case in cases)):
            raise ValueError("R147 required named test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        clean = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                 and not result.skipped and not result.unexpectedSuccesses)
        print(f"R147 private replay argv custody {'PASS' if clean else 'FAIL'}; "
              f"methods={result.testsRun}; "
              f"issues={len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if clean else 1
    except Exception:
        print("R147 private replay argv custody HOLD: required tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
