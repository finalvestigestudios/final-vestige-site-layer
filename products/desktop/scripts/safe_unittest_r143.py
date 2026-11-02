"""R143 exact test-inventory, two-mode replay evidence gate (zero skipped)."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset(('test_ledger_replay_and_receipt','test_ledger_custom_columns_require_matching_options','test_ledger_report_tamper_holds','test_ledger_source_tamper_holds','test_ledger_header_only_holds','test_invoice_replay_candidate_and_digest','test_invoice_review_window_bound','test_invoice_report_tamper_holds','test_invoice_source_tamper_holds','test_invoice_zero_candidates_holds','test_spend_replay_offset_report','test_spend_report_tamper_holds','test_spend_source_tamper_holds','test_policy_replay_exact','test_policy_reverse_sources_holds','test_policy_report_tamper_holds','test_missing_report_holds','test_invalid_kind_and_premium_holds','test_wrong_source_count_holds','test_cross_product_options_holds','test_cli_verified_digest_no_filename','test_cli_hold_redacts_private_filename','test_verifier_leaves_original_folder_intact',))

def flatten(suite):
    for member in suite:
        if isinstance(member, unittest.TestSuite):
            yield from flatten(member)
        else:
            yield member

def main():
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_report_replay_r143.py")
        names = [case._testMethodName for case in flatten(suite)]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError("R143 mandatory test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R143 offline exact report replay {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; "
              f"issues={len(result.failures)+len(result.errors)+len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R143 replay evidence HOLD: required tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
