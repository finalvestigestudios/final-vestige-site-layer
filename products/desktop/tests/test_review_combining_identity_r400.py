"""R400: review display distinguishes normalization-equivalent source IDs.

Synthetic text only; no filesystem, network, compliance or payment operations.
Preserve legacy plain-text rendering while showing the exact source spellings
in all shared financial source identity and premium review labels.
"""
from __future__ import annotations

from types import SimpleNamespace
import unicodedata
import unittest

from fvs_suite.audit_display import (
    visible_source_text, visible_identity_label, visible_source_label_list,
    visible_review_row,
)


class CombiningSourceEvidenceR400(unittest.TestCase):
    def test_nfc_nfd_identifiers_are_explicitly_distinguishable(self):
        nfc, nfd = 'Caf\u00e9', 'Cafe\u0301'
        self.assertEqual(unicodedata.normalize('NFC', nfc),
                         unicodedata.normalize('NFC', nfd))
        self.assertEqual(visible_identity_label(nfc), nfc)
        self.assertEqual(visible_identity_label(nfd), r'Cafe\u0301')
        self.assertNotEqual(visible_identity_label(nfc), visible_identity_label(nfd))

    def test_nonspacing_mark_at_start_is_visible(self):
        self.assertEqual(visible_identity_label('\u0301INVOICE'), r'\u0301INVOICE')

    def test_enclosing_mark_is_visible(self):
        self.assertEqual(visible_identity_label('PO\u20dd2'), r'PO\u20DD2')

    def test_multiple_marks_are_individually_visible(self):
        self.assertEqual(visible_identity_label('A\u0301\u0327'), r'A\u0301\u0327')

    def test_original_literal_escape_remains_distinct(self):
        self.assertEqual(visible_identity_label(r'A\u0301'), r'A\\u0301')
        self.assertNotEqual(visible_identity_label('A\u0301'),
                            visible_identity_label(r'A\u0301'))

    def test_multilingual_plain_source_text_contract_preserved(self):
        for label in ('e\u0301vidence', 'किराया', 'مُراجعة'):
            with self.subTest(label=label):
                self.assertEqual(visible_source_text(label), label)

    def test_review_flags_plain_text_contract_preserved(self):
        case = SimpleNamespace(report_row=7, source_key='A\u0301',
                               flags='flag\u0301')
        self.assertEqual(visible_review_row(case, 'pending'),
                         (7, r'A\u0301', 'flag\u0301', 'pending'))
        self.assertEqual(case.source_key, 'A\u0301')

    def test_list_displays_both_normalization_variants(self):
        labels = visible_source_label_list(('Cafe\u0301', 'Caf\u00e9'))
        self.assertIn(r'Cafe\u0301', labels)
        self.assertIn('Caf\u00e9', labels)
        self.assertEqual(len(labels.split('; ')), 2)

    def test_list_is_deterministic(self):
        labels = ('A\u0301', 'A', 'A\u0301', 'A\u20dd')
        self.assertEqual(visible_source_label_list(labels),
                         visible_source_label_list(reversed(labels)))

    def test_list_does_not_modify_source_data(self):
        labels = ['\u0301A', 'A\u20dd']
        before = labels.copy()
        visible_source_label_list(labels)
        self.assertEqual(labels, before)

    def test_semicolon_boundary_space_and_marks_combine(self):
        self.assertEqual(visible_identity_label(' A;\u0301 '),
                         r'\u0020A\u003B\u0301\u0020')

    def test_existing_bidi_and_supplementary_escape_preserved(self):
        self.assertEqual(visible_identity_label('PO\u202e\U000E0100'),
                         r'PO\u202E\U000E0100')

    def test_no_raw_nonspacing_or_enclosing_marks_in_identity_display(self):
        sample = 'A' + ''.join(chr(cp) for cp in
                              (0x0300, 0x0301, 0x034F, 0x0488, 0x20DD, 0x3099))
        rendered = visible_identity_label(sample)
        self.assertFalse(any(unicodedata.category(ch) in ('Mn', 'Me')
                             for ch in rendered))

    def test_no_unnecessary_escaping_of_spacing_accents(self):
        self.assertEqual(visible_identity_label('é 東京'), 'é 東京')

    def test_exact_native_text_required_for_untrusted_display(self):
        class Hostile(str):
            def __iter__(self):
                raise AssertionError('CUSTOMER_SECRET')
            def __str__(self):
                raise AssertionError('CUSTOMER_SECRET')
        for reveal in (True, False):
            with self.subTest(reveal=reveal):
                with self.assertRaises(TypeError) as raised:
                    visible_source_text(Hostile('test'), reveal_combining=reveal)
                self.assertNotIn('CUSTOMER_SECRET', str(raised.exception))
                self.assertIsNone(raised.exception.__context__)

    def test_other_non_text_values_rejected_without_source_echo(self):
        for obj in (None, b'private', 5):
            with self.subTest(obj_type=type(obj).__name__):
                with self.assertRaises(TypeError) as raised:
                    visible_source_text(obj)
                self.assertNotIn('private', str(raised.exception))

    def test_premium_review_case_is_not_changed(self):
        case = SimpleNamespace(report_row=4, source_key='GR\u0301-4', flags='variance')
        original = vars(case).copy()
        self.assertEqual(visible_review_row(case, 'needs_evidence')[1],
                         r'GR\u0301-4')
        self.assertEqual(vars(case), original)

    def test_raw_input_utf8_is_unmodified(self):
        value = 'Café / Cafe\u0301'
        fingerprint = value.encode('utf-8')
        visible_identity_label(value)
        self.assertEqual(value.encode('utf-8'), fingerprint)

    def test_large_label_is_bounded_to_linear_escape_expansion(self):
        value = 'A' * 4096 + '\u0301' * 500
        rendered = visible_identity_label(value)
        self.assertEqual(len(rendered), 4096 + 6 * 500)
        self.assertEqual(rendered.count(r'\u0301'), 500)


if __name__ == '__main__':
    unittest.main()
