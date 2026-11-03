"""R158 strict, zero-skip independent SpendMap source-label evidence inventory."""
from __future__ import annotations

import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_plain_label_verified",
    "test_identical_labels_deduplicated",
    "test_ascii_case_variants_remain_visible",
    "test_punctuation_collision_order",
    "test_labels_per_category_not_whole_month",
    "test_labels_per_month_not_all_vendor_history",
    "test_trimmed_outer_spaces_and_duplicates",
    "test_literal_semicolon_is_not_list_separator",
    "test_source_backslash_remains_distinguishable",
    "test_actual_zero_width_vs_literal_escape_differ",
    "test_directional_override_is_visible",
    "test_nonbreaking_space_is_visible",
    "test_variation_selector_is_visible",
    "test_hangul_filler_is_visible",
    "test_supplementary_variation_selector_is_visible",
    "test_unicode_casefold_only_orders_does_not_merge",
    "test_formula_equals_prefix_is_neutralized",
    "test_formula_plus_prefix_is_neutralized",
    "test_formula_at_prefix_is_neutralized",
    "test_formula_minus_text_is_neutralized",
    "test_leading_combining_mark_is_neutralized",
    "test_quoted_multiline_source_preserves_snapshot",
    "test_tampered_label_suppression_holds",
    "test_tampered_label_reorder_holds",
    "test_semicolon_injection_holds",
    "test_unicode_escape_tamper_holds",
    "test_formula_quote_removed_holds",
    "test_wrong_category_label_holds",
    "test_missing_label_column_holds",
    "test_original_bytes_unchanged_after_verification",
    "test_private_cli_failure_does_not_expose_label",
    "test_helper_rejects_unsorted_lookalike_output",
    "test_no_network_or_report_generator_imports",
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
            pattern="test_spend_visible_labels_r158.py")
        cases = list(flatten(suite))
        names = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(names) != EXPECTED
                or any(type(case).__name__ != "SpendLabelR158" for case in cases)):
            raise ValueError("R158 strict test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        passed = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                  and not result.skipped and not result.unexpectedSuccesses)
        print(f"R158 SpendMap visible labels {'PASS' if passed else 'FAIL'}; "
              f"methods={result.testsRun}; issues="
              f"{len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if passed else 1
    except Exception:
        print("R158 SpendMap vendor labels HOLD: required tests unavailable")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
