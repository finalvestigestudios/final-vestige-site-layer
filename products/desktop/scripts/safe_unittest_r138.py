"""R138 ProcureGuard offset custody: exact methods, zero skips, redacted logs."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_source_digest_columns_bind_all_three_parsed_inputs",
    "test_source_digest_columns_match_published_manifest",
    "test_no_offsets_explicitly_report_empty_candidate_arrays",
    "test_credit_links_back_to_invoice_source_line",
    "test_return_links_back_to_receipt_source_line",
    "test_both_types_are_separately_traceable_without_money_changes",
    "test_multiple_credit_events_preserve_source_order",
    "test_duplicate_invoice_ids_keep_all_candidates_and_review_flag",
    "test_duplicate_receipt_ids_keep_all_candidates_and_review_flag",
    "test_unlinked_credit_has_no_invented_target",
    "test_unlinked_return_has_no_invented_target",
    "test_normalized_credit_link_still_flags_review",
    "test_normalized_return_link_still_flags_review",
    "test_bom_and_quoted_newline_keep_original_invoice_lines",
    "test_quoted_newline_keeps_original_receipt_lines",
    "test_absent_invoice_and_receipt_remain_source_bound",
    "test_custom_price_policy_retains_all_original_fingerprints",
    "test_repeat_exports_are_byte_identical_and_originals_unchanged",
    "test_mutation_after_parse_aborts_without_partial_evidence",
    "test_negative_credit_quantity_cannot_publish_evidence",
    "test_low_caller_decimal_precision_preserves_exact_totals",
    "test_links_cannot_cross_purchase_orders",
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
            pattern="test_procurement_offset_custody_r138.py",
        )
        names = [case._testMethodName for case in flatten(suite)]
        if len(names) != len(EXPECTED) or set(names) != EXPECTED:
            raise ValueError("R138 procurement offset custody test inventory mismatch")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        okay = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        print(f"R138 procurement offset custody {'PASS' if okay else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.failures) + len(result.errors) + len(result.skipped)}")
        return 0 if okay else 1
    except Exception:
        print("R138 procurement offset custody HOLD: source tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
