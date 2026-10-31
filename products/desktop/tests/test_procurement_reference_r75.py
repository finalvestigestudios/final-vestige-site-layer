"""R75 financial document-reference identity regressions; synthetic data only."""
from __future__ import annotations

import unittest

from fvs_suite.procurement_reference import (
    has_original_spelling,
    source_document_spellings,
)


class OriginalProcurementDocumentIdentityR75(unittest.TestCase):
    def test_exact_original_spelling(self):
        self.assertTrue(has_original_spelling("INV-1", source_document_spellings(["INV-1"])))

    def test_ascii_case_only_equivalence(self):
        self.assertTrue(has_original_spelling("inv-A1", source_document_spellings(["INV-a1"])))

    def test_prefix_and_suffix_whitespace_compatibility(self):
        self.assertTrue(has_original_spelling("\t INV-1  ", source_document_spellings([" INV-1\n"])))

    def test_punctuation_normalization_is_not_original_identity(self):
        self.assertFalse(has_original_spelling("INV1", source_document_spellings(["INV-1"])))

    def test_credit_long_s_does_not_disappear_into_ascii_s(self):
        self.assertFalse(has_original_spelling("S1", source_document_spellings(["ſ1"])))

    def test_return_long_s_does_not_disappear_into_ascii_s(self):
        self.assertFalse(has_original_spelling("ſ1", source_document_spellings(["S1"])))

    def test_sharp_s_vs_ascii_ss_is_reviewable(self):
        self.assertFalse(has_original_spelling("SS-5", source_document_spellings(["ß-5"])))

    def test_sharp_s_reverse_is_reviewable(self):
        self.assertFalse(has_original_spelling("ß-5", source_document_spellings(["SS-5"])))

    def test_ligature_vs_ascii_ff_is_reviewable(self):
        self.assertFalse(has_original_spelling("FF9", source_document_spellings(["ﬀ9"])))

    def test_ligature_reverse_is_reviewable(self):
        self.assertFalse(has_original_spelling("ﬀ9", source_document_spellings(["FF9"])))

    def test_kelvin_sign_not_ordinary_k(self):
        self.assertFalse(has_original_spelling("K1", source_document_spellings(["K1"])))

    def test_micro_sign_not_greek_mu(self):
        self.assertFalse(has_original_spelling("μ1", source_document_spellings(["µ1"])))

    def test_dotted_turkish_capital_i_is_not_ascii_i(self):
        self.assertFalse(has_original_spelling("i1", source_document_spellings(["İ1"])))

    def test_combining_marks_are_preserved(self):
        self.assertFalse(has_original_spelling("é", source_document_spellings(["e\u0301"])))

    def test_zero_width_character_is_not_erased(self):
        self.assertFalse(has_original_spelling("INV1", source_document_spellings(["INV\u200b1"])))

    def test_exact_non_ascii_reference_remains_exact(self):
        self.assertTrue(has_original_spelling("ſßﬀ", source_document_spellings(["ſßﬀ"])))

    def test_other_originals_do_not_hide_mismatch(self):
        self.assertFalse(has_original_spelling("SS1", source_document_spellings(["ß1", "X2"])))

    def test_any_genuinely_present_original_matches(self):
        self.assertTrue(has_original_spelling("x2", source_document_spellings(["ß1", "X2"])))

    def test_duplicate_originals_are_stable(self):
        self.assertEqual(source_document_spellings(["A", "a", "A"]), frozenset(["a"]))

    def test_order_independent_source_fingerprints(self):
        a = source_document_spellings(["INV2", "ß1", "S1"])
        b = source_document_spellings(["S1", "INV2", "ß1"])
        self.assertEqual(a, b)

    def test_no_originals_cannot_match(self):
        self.assertFalse(has_original_spelling("INV1", source_document_spellings([])))

    def test_original_empty_reference_compatibility(self):
        self.assertTrue(has_original_spelling("", source_document_spellings([""])))

    def test_numeric_import_cells_keep_legacy_string_conversion(self):
        self.assertTrue(has_original_spelling("123", source_document_spellings([123])))

    def test_immutable_original_snapshot(self):
        values = ["A1"]
        snapshot = source_document_spellings(values)
        values.append("B2")
        self.assertTrue(has_original_spelling("A1", snapshot))
        self.assertFalse(has_original_spelling("B2", snapshot))

    def test_no_unexpected_logging_or_mutation(self):
        values = ["Client Secret — ß1"]
        snapshot = source_document_spellings(values)
        self.assertFalse(has_original_spelling("CLIENT SECRET — SS1", snapshot))
        self.assertEqual(values, ["Client Secret — ß1"])


if __name__ == "__main__":
    unittest.main()
