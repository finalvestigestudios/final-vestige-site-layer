"""R165 strict source-owned no-skip Invoice Twin snapshot regression runner."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_recycled_generator_two_near_rows",
    "test_recycled_generator_three_near_rows",
    "test_recycled_generator_exact_invoice_anchor",
    "test_recycled_generator_keeps_vendors_separate",
    "test_recycled_generator_keeps_amounts_separate",
    "test_recycled_generator_retains_precise_decimals",
    "test_recycled_generator_preserves_distinct_original_labels",
    "test_distinct_result_mappings_after_reused_generator",
    "test_result_records_do_not_alias_original_list",
    "test_mutating_input_after_candidates_does_not_change_evidence",
    "test_original_labels_stable_after_input_mutation",
    "test_provenance_candidate_ref_binds_original_source_lines",
    "test_recycled_input_matches_independent_dict_records",
    "test_out_of_order_recycled_source_is_numeric",
    "test_bad_later_row_blocks_all_results",
    "test_recycled_duplicate_physical_line_rejected",
    "test_recycled_generator_fails_closed_at_candidate_cap",
    "test_list_inputs_remain_unchanged_by_snapshot",
    "test_hostile_decimal_context_preserves_source_snapshot",
    "test_empty_recycled_generator_has_no_candidates",
))


def _cases(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from _cases(case)
        else:
            yield case


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"), pattern="test_invoice_snapshot_r165.py")
        cases = list(_cases(suite))
        methods = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "InvoiceSnapshotR165" for case in cases)):
            raise ValueError("R165 regression inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        failures = sorted({case._testMethodName for case, _ in
                           (*result.errors, *result.failures)})
        print(f"R165 invoice input snapshots {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors) + len(result.failures) + len(result.skipped)}; "
              f"failed_methods={','.join(failures)}")
        return 0 if passed else 1
    except Exception:
        print("R165 invoice input snapshots HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
