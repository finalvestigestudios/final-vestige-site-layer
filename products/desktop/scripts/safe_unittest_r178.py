"""No-skip 28-case R178 Policy Delta canonical evidence gate; no private text."""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_composed_decomposed", "test_decomposed_composed",
    "test_reordered_combining_marks", "test_hiragana_decomposition",
    "test_korean_hangul_composition", "test_true_policy_edit_not_paired",
    "test_nfkc_only_fullwidth_not_paired", "test_nfkc_only_ligature_not_paired",
    "test_same_text_not_paired", "test_only_added_not_paired",
    "test_only_removed_not_paired", "test_nothing_changed",
    "test_duplicate_old_normalized_text_suppresses_pair",
    "test_duplicate_new_normalized_text_suppresses_pair",
    "test_duplicates_in_both_sides_suppressed", "test_no_cross_hunk_pairing",
    "test_multiple_hunks_numbered_and_sorted", "test_two_pairs_in_one_hunk_physical_order",
    "test_mixed_substantive_change_retains_one_canonical_pair",
    "test_eof_difference_not_aliased_to_canonical_edit",
    "test_crlf_difference_not_aliased_to_canonical_edit",
    "test_sixteen_bounded_pairs", "test_seventeen_bounded_with_explicit_omission",
    "test_deterministic_multiple_candidates", "test_original_private_text_not_echoed",
    "test_human_review_caveat_present", "test_existing_unrelated_keys_ignored",
    "test_distinct_glyph_not_canonical_equivalence",
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
            start_dir=str(ROOT / "tests"), pattern="test_policy_local_canonical_r178.py")
        loaded = list(flatten(suite))
        names = [case._testMethodName for case in loaded]
        if (len(loaded) != 28 or set(names) != EXPECTED
                or len(set(names)) != 28
                or any(type(case).__name__ != "PolicyLocalCanonicalR178" for case in loaded)):
            raise ValueError("R178 test inventory drift")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == 28
                  and not result.skipped and not result.unexpectedSuccesses)
        failed = sorted({c._testMethodName for c, _ in
                         (*result.errors, *result.failures)})
        print("R178 canonical policy " + ("PASS" if passed else "FAIL")
              + f"; methods={result.testsRun}; issues="
              + str(len(result.errors) + len(result.failures) + len(result.skipped))
              + "; failed_methods=" + ",".join(failed))
        return 0 if passed else 1
    except Exception:
        print("R178 HOLD: exact test inventory unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
