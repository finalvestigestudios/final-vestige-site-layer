"""R134 strict Invoice Twin review-window regression inventory, with redacted output."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_window_parser_accepts_canonical_limits",
    "test_window_parser_rejects_malformed",
    "test_window_parser_rejects_nontext",
    "test_zero_day_window_same_day_candidate",
    "test_zero_day_window_rejects_next_day",
    "test_default_seven_day_window",
    "test_custom_fourteen_day_window",
    "test_365_day_boundary",
    "test_exact_anchor_survives_zero_window",
    "test_distant_dates_review_tracks_chosen_window",
    "test_report_declares_window_even_for_exact",
    "test_empty_report_still_declares_header",
    "test_candidate_refs_remain_stable_for_shared_pair",
    "test_invalid_engine_window_never_writes",
    "test_snapshot_checksum_and_original_unchanged",
    "test_invoice_gui_and_native_focus_contract",
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
            start_dir=str(ROOT / "tests"), pattern="test_invoice_window_r134.py")
        methods = [item._testMethodName for item in flatten(suite)]
        if len(methods) != len(EXPECTED) or set(methods) != EXPECTED:
            raise ValueError("Missing or duplicated invoice day-window tests")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R134 invoice review window {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures)+len(result.errors)+len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R134 invoice review window HOLD: source tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
