"""R156 zero-skip fixed test inventory for private SpendMap money recheck."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_single_positive_amount",
    "test_negative_only_credit",
    "test_zero_amount_is_not_an_offset",
    "test_net_zero_positive_and_negative",
    "test_cross_category_offset_totals",
    "test_multiple_months_and_vendors",
    "test_normalized_vendor_collisions",
    "test_spreadsheet_escaped_category",
    "test_exact_200_line_aggregate",
    "test_multiline_records_keep_money_and_line_membership",
    "test_ambient_low_precision_and_inexact_trap",
    "test_net_amount_tamper_hold",
    "test_gross_charge_tamper_hold",
    "test_gross_credit_tamper_hold",
    "test_vendor_month_total_tamper_hold",
    "test_vendor_month_charge_tamper_hold",
    "test_vendor_month_credit_tamper_hold",
    "test_same_category_offset_flag_tamper_hold",
    "test_vendor_month_offset_flag_tamper_hold",
    "test_cross_category_second_bucket_tamper_hold",
    "test_false_positive_offset_flag_hold",
    "test_noncanonical_money_format_hold",
    "test_required_monetary_header_removed_hold",
    "test_original_source_and_report_not_mutated",
    "test_private_cli_failure_does_not_echo_amount",
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
            pattern="test_spend_evidence_money_recheck_r156.py")
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED
                or any(type(case).__name__ != "SpendMoneyRecheckR156"
                       for case in cases)):
            raise ValueError("R156 strict test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        print(f"R156 SpendMap independent money recheck {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R156 SpendMap money recheck HOLD: required tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
