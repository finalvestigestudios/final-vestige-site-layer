"""R354 genuine ProcureGuard original-spelling custody tests (synthetic only).

Run with: PYTHONPATH=products/desktop python -m unittest discover -s
products/desktop/tests -p test_procurement_unicode_original_r354.py
No test authorizes compliance decisions, payments, or binary distribution.
"""
from __future__ import annotations

import unittest

from fvs_suite.procurement_reference import (
    has_original_spelling, source_document_spellings,
)


class UnicodeOriginalSpellingR354(unittest.TestCase):
    UNICODE_BOUNDARIES = (
        '\u00a0',  # non-breaking space
        '\u2007',  # figure space
        '\u202f',  # narrow no-break space
        '\u3000',  # ideographic space
        '\u2002',  # en space
        '\u2003',  # em space
        '\u2028',  # line separator
        '\u2029',  # paragraph separator
        '\u0085',  # next-line character
    )

    def test_each_unicode_prefix_does_not_equal_plain_reference(self):
        for separator in self.UNICODE_BOUNDARIES:
            with self.subTest(separator=ord(separator)):
                self.assertFalse(has_original_spelling(
                    'INV1', source_document_spellings([separator + 'INV1'])))

    def test_each_unicode_suffix_does_not_equal_plain_reference(self):
        for separator in self.UNICODE_BOUNDARIES:
            with self.subTest(separator=ord(separator)):
                self.assertFalse(has_original_spelling(
                    'INV1', source_document_spellings(['INV1' + separator])))

    def test_plain_original_does_not_equal_unicode_prefix_reference(self):
        for separator in self.UNICODE_BOUNDARIES:
            with self.subTest(separator=ord(separator)):
                self.assertFalse(has_original_spelling(
                    separator + 'INV1', source_document_spellings(['INV1'])))

    def test_plain_original_does_not_equal_unicode_suffix_reference(self):
        for separator in self.UNICODE_BOUNDARIES:
            with self.subTest(separator=ord(separator)):
                self.assertFalse(has_original_spelling(
                    'INV1' + separator, source_document_spellings(['INV1'])))

    def test_same_unicode_character_remains_identical(self):
        for separator in self.UNICODE_BOUNDARIES:
            with self.subTest(separator=ord(separator)):
                original = separator + 'INV1' + separator
                self.assertTrue(has_original_spelling(
                    original, source_document_spellings([original])))

    def test_distinct_unicode_boundary_spaces_remain_distinct(self):
        characters = self.UNICODE_BOUNDARIES
        for left, right in zip(characters, characters[1:]):
            with self.subTest(left=ord(left), right=ord(right)):
                self.assertFalse(has_original_spelling(
                    left + 'INV1', source_document_spellings([right + 'INV1'])))

    def test_ascii_boundary_space_compatibility_retained(self):
        self.assertTrue(has_original_spelling(
            '\t \nINV-1\r\v\f', source_document_spellings(['  inv-1  '])))

    def test_ascii_boundary_control_whitespace_remains_compatible(self):
        for separator in ' \t\r\n\v\f':
            with self.subTest(separator=ord(separator)):
                self.assertTrue(has_original_spelling(
                    separator + 'inv1' + separator, source_document_spellings(['INV1'])))

    def test_ascii_case_only_compatibility_retained(self):
        self.assertTrue(has_original_spelling('inv-a1', source_document_spellings(['INV-A1'])))

    def test_no_unicode_casefolding(self):
        self.assertFalse(has_original_spelling('ss', source_document_spellings(['\u00df'])))

    def test_zero_width_space_already_distinct(self):
        self.assertFalse(has_original_spelling('INV1', source_document_spellings(['\u200bINV1'])))

    def test_nonascii_source_spelling_is_not_mutated(self):
        originals = ['\u00a0INV1\u202f']
        result = source_document_spellings(originals)
        self.assertEqual(result, frozenset(['\u00a0inv1\u202f']))
        self.assertEqual(originals, ['\u00a0INV1\u202f'])

    def test_ascii_and_unicode_variants_coexist(self):
        original = source_document_spellings([' INV1 ', '\u00a0INV1'])
        self.assertEqual(original, frozenset(['inv1', '\u00a0inv1']))
        self.assertTrue(has_original_spelling('INV1', original))
        self.assertTrue(has_original_spelling('\u00a0INV1', original))

    def test_non_ascii_suffix_with_ascii_boundary_around_it(self):
        original = source_document_spellings(['\tINV1\u00a0\r'])
        self.assertTrue(has_original_spelling('INV1\u00a0', original))
        self.assertFalse(has_original_spelling('INV1', original))

    def test_native_integer_compatibility(self):
        self.assertTrue(has_original_spelling('100', source_document_spellings([100])))

    def test_empty_original_and_ascii_whitespace_compatibility(self):
        self.assertTrue(has_original_spelling(' \t\n', source_document_spellings([''])))

    def test_reject_forged_source_object_without_conversion(self):
        class Forged(str):
            def __str__(self):
                raise AssertionError('PRIVATE_CUSTOMER_PATH')
        with self.assertRaises(ValueError) as caught:
            source_document_spellings([Forged('INV1')])
        self.assertNotIn('PRIVATE', str(caught.exception))

    def test_reject_forged_reference_without_conversion(self):
        class Forged(str):
            def __str__(self):
                raise AssertionError('PRIVATE_CUSTOMER_PATH')
        with self.assertRaises(ValueError) as caught:
            has_original_spelling(Forged('INV1'), source_document_spellings(['INV1']))
        self.assertNotIn('PRIVATE', str(caught.exception))

    def test_snapshot_stable_and_order_independent(self):
        a = source_document_spellings(['\u00a0INV1', 'INV1', '\u2007INV1'])
        b = source_document_spellings(['\u2007INV1', '\u00a0INV1', 'INV1'])
        self.assertEqual(a, b)
        self.assertEqual(len(a), 3)

    def test_empty_collection_never_claims_original_identity(self):
        self.assertFalse(has_original_spelling('INV1', source_document_spellings([])))


if __name__ == '__main__':
    unittest.main()
