"""Strict R150 30-method suite, with private fail-closed output."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_fullwidth_latin_to_ascii_flagged",
    "test_ascii_to_fullwidth_flagged",
    "test_ligature_expanded_flagged",
    "test_two_digit_circled_number_flagged",
    "test_superscript_digit_flagged",
    "test_roman_numeral_flagged",
    "test_mathematical_bold_letter_flagged",
    "test_subscript_digit_flagged",
    "test_katakana_halfwidth_flagged",
    "test_multiple_compatibility_symbols_sorted",
    "test_reordered_equal_counts_have_precise_fallback",
    "test_bounded_inventory_does_not_dump_entire_policy",
    "test_canonical_accent_is_nfc_only",
    "test_kelvin_sign_is_canonical_not_compatibility_only",
    "test_identical_compatibility_text_not_flagged",
    "test_arbitrary_amount_change_never_flagged",
    "test_partial_compatibility_match_not_flagged",
    "test_bom_only_not_flagged",
    "test_crlf_only_not_flagged",
    "test_end_of_file_marker_preserved",
    "test_physical_line_index_preserved",
    "test_sha_provenance_matches_exact_original_bytes",
    "test_same_inputs_produce_byte_identical_report",
    "test_existing_report_not_overwritten",
    "test_invalid_utf8_rejected_before_report",
    "test_bidi_override_rejected_before_report",
    "test_private_parent_directory_not_emitted",
    "test_no_automatic_compliance_decision",
    "test_escaped_backslash_cannot_fake_evidence",
    "test_multiline_composition_not_mislabeled",
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
            pattern="test_policy_compatibility_evidence_r150.py")
        cases = list(flatten(suite))
        methods = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(methods) != EXPECTED or
                any(type(case).__name__ != "PolicyCompatibilityEvidenceR150"
                    for case in cases)):
            raise ValueError("R150 required method inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        clean = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                 and not result.skipped and not result.unexpectedSuccesses)
        print(f"R150 Policy Delta compatibility review {'PASS' if clean else 'FAIL'}; "
              f"methods={result.testsRun}; "
              f"issues={len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if clean else 1
    except Exception:
        print("R150 Policy Delta compatibility review HOLD: required tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
