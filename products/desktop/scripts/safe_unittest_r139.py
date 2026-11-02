"""R139 exact no-skip, two-mode, source-owned spreadsheet formula boundary tests."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_formula_operator_boundaries",
    "test_negative_expressions_escaped",
    "test_negative_money_stays_numeric",
    "test_ascii_spaced_formula_escaped",
    "test_leading_ascii_controls_escaped",
    "test_bidi_control_prefixes_escaped",
    "test_zero_width_prefixes_escaped",
    "test_exotic_unicode_whitespace_prefixes_escaped",
    "test_variation_selector_prefixes_escaped",
    "test_combining_prefixes_escaped",
    "test_private_use_and_unassigned_prefixes_escaped",
    "test_benign_multilingual_text_stays_visible",
    "test_nonleading_hidden_text_not_rewritten",
    "test_real_csv_roundtrip_including_exact_money",
    "test_existing_report_never_overwritten",
    "test_failed_conversion_keeps_no_partial_artifact",
    "test_ledger_source_formula_label_still_traces_digests",
    "test_invoice_vendor_hidden_prefix_is_escaped",
    "test_spend_vendor_formula_label_is_escaped",
    "test_money_writer_safe_values_not_rounded_or_replaced",
))

def flatten(suite):
    for member in suite:
        if isinstance(member, unittest.TestSuite):
            yield from flatten(member)
        else:
            yield member

def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_spreadsheet_prefix_guard_r139.py")
        names = [case._testMethodName for case in flatten(suite)]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError("R139 test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R139 invisible-prefix CSV guard {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R139 invisible-prefix CSV guard HOLD: tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
