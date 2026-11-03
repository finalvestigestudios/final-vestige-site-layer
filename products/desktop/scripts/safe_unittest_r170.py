"""Privacy-redacted, fail-closed exact R170 regression inventory (normal / -OO)."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_conflicting_same_orientation_exact_first",
    "test_conflicting_same_orientation_near_first",
    "test_conflicting_reverse_orientation_exact_first",
    "test_conflicting_reverse_orientation_near_first",
    "test_identical_status_same_direction_still_rejected",
    "test_identical_status_reverse_still_rejected",
    "test_near_only_duplicate_still_rejected",
    "test_conflict_after_other_distinct_pairs",
    "test_conflict_separated_by_other_status",
    "test_distinct_pairs_with_different_statuses_permitted",
    "test_distinct_pairs_with_shared_one_source_row_permitted",
    "test_distinct_pairs_with_same_status_permitted",
    "test_no_input_mutation_when_conflict_rejected",
    "test_no_input_mutation_on_valid_return",
    "test_standalone_status_ref_remains_deterministic",
    "test_standalone_statuses_have_distinct_refs",
    "test_pair_order_does_not_change_locator_for_same_row",
    "test_source_digest_still_binds_reference",
    "test_supplied_fake_refs_are_overwritten",
    "test_underlying_storage_drives_conflict_not_forged_getter",
    "test_private_values_are_not_echoed_on_conflict",
    "test_input_order_variation_always_rejects",
))


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_invoice_conflicting_pair_r170.py",
        )
        loaded = list(cases(suite))
        methods = [case._testMethodName for case in loaded]
        if (len(loaded) != len(EXPECTED) or set(methods) != EXPECTED
                or len(set(methods)) != len(EXPECTED)
                or any(type(case).__name__ != "InvoiceConflictingPairR170"
                       for case in loaded)):
            raise ValueError("R170 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        good = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({case._testMethodName for case, _ in
                         (*result.errors, *result.failures)})
        print("R170 conflicting invoice pair custody "
              + ("PASS" if good else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failed))
        return 0 if good else 1
    except Exception:
        print("R170 conflicting invoice pair custody HOLD: test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
