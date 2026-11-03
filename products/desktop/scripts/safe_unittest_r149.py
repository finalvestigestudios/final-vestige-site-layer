"""R149 exact-inventory source-owned Unicode policy evidence gate; private output."""
from __future__ import annotations
import contextlib
import os
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = frozenset((
    "test_composed_to_decomposed_accent_reveals_codepoint",
    "test_decomposed_to_composed_accent_is_reversible",
    "test_canonically_reordered_diacritics_are_flagged",
    "test_identical_decomposed_text_does_not_fabricate_change",
    "test_accent_removed_is_not_mislabeled_canonically_equal",
    "test_hiragana_decomposition_is_visible",
    "test_hebrew_nonspacing_mark_is_explicit",
    "test_arabic_nonspacing_mark_is_explicit",
    "test_devanagari_nukta_is_explicit",
    "test_thai_nonspacing_mark_is_explicit",
    "test_enclosing_circle_mark_is_explicit",
    "test_supplementary_combining_mark_uses_eight_digits",
    "test_plain_multilingual_letters_remain_readable",
    "test_spacing_combining_mark_remains_readable",
    "test_literal_escape_cannot_impersonate_actual_accent",
    "test_unchanged_context_marks_are_escaped",
    "test_change_index_keeps_exact_physical_citations",
    "test_bom_only_does_not_claim_normalization_difference",
    "test_crlf_only_is_not_unicode_normalization_difference",
    "test_original_source_sha256_and_inputs_are_authoritative",
    "test_same_sources_generate_byte_identical_reports",
    "test_existing_report_is_never_overwritten",
    "test_invalid_utf8_rejected_before_publication",
    "test_bidi_override_still_rejected_before_publication",
    "test_private_path_is_not_repeated_in_report",
    "test_report_declares_combining_display_contract",
    "test_nfkc_only_equivalence_is_not_misclassified",
    "test_unterminated_last_line_preserves_source_eof_markers",
    "test_mark_only_insert_is_visible_and_not_canonical_equivalence",
    "test_large_synthetic_context_preserves_audit_index",
))

def flatten(suite):
    for case in suite:
        if isinstance(case, unittest.TestSuite):
            yield from flatten(case)
        else:
            yield case

def main() -> int:
    try:
        suite = unittest.defaultTestLoader.discover(
            start_dir=str(ROOT / "tests"),
            pattern="test_policy_normalization_evidence_r149.py")
        cases = list(flatten(suite))
        observed = [case._testMethodName for case in cases]
        if (len(cases) != len(EXPECTED) or set(observed) != EXPECTED
                or any(type(case).__name__ != "PolicyNormalizationEvidenceR149" for case in cases)):
            raise ValueError("Required Policy Delta Unicode test inventory changed")
        result = unittest.TestResult()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                suite.run(result)
        clean = (result.wasSuccessful() and result.testsRun == len(EXPECTED)
                 and not result.skipped and not result.unexpectedSuccesses)
        print(f"R149 Policy Delta Unicode evidence {'PASS' if clean else 'FAIL'}; "
              f"methods={result.testsRun}; "
              f"issues={len(result.errors)+len(result.failures)+len(result.skipped)}")
        return 0 if clean else 1
    except Exception:
        print("R149 Policy Delta Unicode evidence HOLD: required tests unavailable")
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
