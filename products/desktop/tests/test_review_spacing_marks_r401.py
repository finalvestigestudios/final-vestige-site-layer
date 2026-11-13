"""R401 exact source identity display for spacing combining marks (Mc).

Only synthetic text is used. The renderer must not change imported identifiers,
physical source bytes, SHA-256 provenance, money, matching, or review state.
"""
from __future__ import annotations

from types import SimpleNamespace
import unicodedata
import unittest

from fvs_suite.audit_display import (
    visible_source_text, visible_identity_label, visible_source_label_list,
    visible_review_row,
)


class SpacingMarkIdentityEvidenceR401(unittest.TestCase):
    def test_bengali_composed_and_decomposed_labels_are_distinct(self):
        a, b = '\u0995\u09cb', '\u0995\u09c7\u09be'
        self.assertEqual(unicodedata.normalize('NFC', a),
                         unicodedata.normalize('NFC', b))
        self.assertNotEqual(a, b)
        self.assertEqual(visible_identity_label(a), r'ক\u09CB')
        self.assertEqual(visible_identity_label(b), r'ক\u09C7\u09BE')
        self.assertNotEqual(visible_identity_label(a), visible_identity_label(b))

    def test_odia_spacing_mark_decomposition(self):
        a, b = '\u0b15\u0b4b', '\u0b15\u0b47\u0b3e'
        self.assertEqual(unicodedata.normalize('NFC', a),
                         unicodedata.normalize('NFC', b))
        self.assertEqual(visible_identity_label(a), r'କ\u0B4B')
        self.assertEqual(visible_identity_label(b), r'କ\u0B47\u0B3E')

    def test_tamil_spacing_mark_decomposition(self):
        a, b = '\u0b95\u0bcb', '\u0b95\u0bc7\u0bbe'
        self.assertEqual(unicodedata.normalize('NFC', a),
                         unicodedata.normalize('NFC', b))
        self.assertNotEqual(visible_identity_label(a), visible_identity_label(b))

    def test_devanagari_spacing_mark(self):
        self.assertEqual(visible_identity_label('क\u093e'), r'क\u093E')

    def test_myanmar_spacing_mark(self):
        self.assertEqual(visible_identity_label('က\u102c'), r'က\u102C')

    def test_spacing_mark_at_start(self):
        self.assertEqual(visible_identity_label('\u09bePO'), r'\u09BEPO')

    def test_spacing_mark_at_end(self):
        self.assertEqual(visible_identity_label('ID\u09be'), r'ID\u09BE')

    def test_multiple_mark_categories(self):
        self.assertEqual(visible_identity_label('A\u0301\u09be\u20dd'),
                         r'A\u0301\u09BE\u20DD')

    def test_no_raw_unicode_marks_in_identity(self):
        value = 'A' + ''.join(chr(c) for c in
                              (0x0301, 0x09BE, 0x09CB, 0x093E, 0x20DD))
        rendered = visible_identity_label(value)
        self.assertFalse(any(unicodedata.category(ch) in {'Mn', 'Mc', 'Me'}
                             for ch in rendered))

    def test_plain_text_multilingual_readability_preserved(self):
        for value in ('বাংলা', 'தமிழ்', 'हिन्दी', 'မြန်မာ', 'العَرَبِيَّة'):
            with self.subTest(label=value):
                self.assertEqual(visible_source_text(value), value)

    def test_explicit_true_mode_reveals_spacing_marks(self):
        self.assertEqual(visible_source_text('X\u09be', reveal_combining=True),
                         r'X\u09BE')

    def test_explicit_false_mode_keeps_spacing_marks(self):
        self.assertEqual(visible_source_text('X\u09be', reveal_combining=False),
                         'X\u09be')

    def test_literal_escape_not_aliased(self):
        self.assertEqual(visible_identity_label(r'A\u09BE'), r'A\\u09BE')
        self.assertNotEqual(visible_identity_label('A\u09be'),
                            visible_identity_label(r'A\u09BE'))

    def test_list_retains_both_composed_and_decomposed_labels(self):
        a, b = '\u0995\u09cb', '\u0995\u09c7\u09be'
        rendered = visible_source_label_list([b, a, a])
        self.assertIn(r'\u09CB', rendered)
        self.assertIn(r'\u09C7\u09BE', rendered)
        self.assertEqual(len(rendered.split('; ')), 2)

    def test_list_order_independent(self):
        values = ['\u0995\u09cb', '\u0995\u09c7\u09be', ' A ', 'A;B', 'B']
        self.assertEqual(visible_source_label_list(values),
                         visible_source_label_list(reversed(values)))

    def test_list_preserves_distinct_raw_codepoints(self):
        values = ['\u0995\u09cb', '\u0995\u09c7\u09be']
        before = values.copy()
        visible_source_label_list(values)
        self.assertEqual(values, before)

    def test_whitespace_and_semicolon_markers_coexist(self):
        self.assertEqual(visible_identity_label(' \u09be; '),
                         r'\u0020\u09BE\u003B\u0020')

    def test_review_row_premium_displays_raw_identity_spelling(self):
        case = SimpleNamespace(report_row=12, source_key='\u0995\u09c7\u09be',
                               flags='flags\u093e')
        self.assertEqual(visible_review_row(case, 'pending'),
                         (12, r'ক\u09C7\u09BE', 'flags\u093e', 'pending'))
        self.assertEqual(case.source_key, '\u0995\u09c7\u09be')

    def test_review_queue_does_not_mutate_original(self):
        case = SimpleNamespace(report_row=1, source_key=' A\u09be ', flags='none')
        before = vars(case).copy()
        visible_review_row(case, 'needs_evidence')
        self.assertEqual(vars(case), before)

    def test_visible_source_rejects_string_subclass(self):
        class Hostile(str):
            def __iter__(self):
                raise AssertionError('PRIVATE')
        with self.assertRaises(TypeError) as err:
            visible_source_text(Hostile('A\u09be'), reveal_combining=True)
        self.assertIsNone(err.exception.__context__)

    def test_identity_rejects_other_native_type(self):
        with self.assertRaises(TypeError):
            visible_identity_label(b'A')

    def test_scaling_bounded(self):
        value = '\u09be' * 2048
        rendered = visible_identity_label(value)
        self.assertEqual(rendered, r'\u09BE' * 2048)
        self.assertEqual(len(rendered), 6 * 2048)

    def test_plain_ascii_label_compatibility(self):
        self.assertEqual(visible_identity_label('PO-1 / 12'), 'PO-1 / 12')

    def test_printable_precomposed_accent_compatibility(self):
        self.assertEqual(visible_identity_label('Café 東京'), 'Café 東京')


if __name__ == '__main__':
    unittest.main()
