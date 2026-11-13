"""R399: local-first, deterministic source-label presentation for human review.

Synthetic values only. Does not approve compliance decisions or publish EXEs.
"""
from __future__ import annotations

from types import SimpleNamespace
import unittest

from fvs_suite.audit_display import (
    visible_identity_label, visible_source_label_list, visible_review_row,
    visible_source_text,
)


class DisplayBoundaryCustodyR399(unittest.TestCase):
    def test_plain_identity_unmodified(self):
        self.assertEqual(visible_identity_label('PO-1'), 'PO-1')

    def test_leading_space_escaped(self):
        self.assertEqual(visible_identity_label(' PO-1'), r'\u0020PO-1')

    def test_trailing_space_escaped(self):
        self.assertEqual(visible_identity_label('PO-1 '), r'PO-1\u0020')

    def test_boundary_spaces_count_preserved(self):
        self.assertEqual(visible_identity_label('  PO-1   '), r'\u0020\u0020PO-1\u0020\u0020\u0020')

    def test_whitespace_only_is_evidence(self):
        self.assertEqual(visible_identity_label('   '), r'\u0020\u0020\u0020')

    def test_interior_space_unchanged(self):
        self.assertEqual(visible_identity_label('PO  1'), 'PO  1')

    def test_unicode_blank_escaped(self):
        self.assertEqual(visible_identity_label('PO\u00a0-1'), r'PO\u00A0-1')

    def test_bidi_and_tab_escaped(self):
        self.assertEqual(visible_identity_label(' A\u202e\t'), r'\u0020A\u202E\u0009')

    def test_semicolon_source_separator_escaped(self):
        self.assertEqual(visible_identity_label('A;B'), r'A\u003BB')

    def test_literal_backslash_cannot_impersonate_marker(self):
        self.assertNotEqual(visible_identity_label(r'\u0020A'), visible_identity_label(' A'))
        self.assertEqual(visible_identity_label(r'\u0020A'), r'\\u0020A')

    def test_list_preserves_source_variants(self):
        self.assertEqual(visible_source_label_list((' PO-1', 'PO-1')),
                         r'\u0020PO-1; PO-1')

    def test_list_retains_whitespace_only(self):
        self.assertEqual(visible_source_label_list(('', '  ', '')),
                         r'\u0020\u0020')

    def test_list_ignores_only_empty_values(self):
        self.assertEqual(visible_source_label_list(('', '', '')), '')

    def test_list_is_deterministic_and_deduplicated(self):
        values = ('b', ' A', 'A ', 'b', 'A')
        self.assertEqual(visible_source_label_list(values),
                         visible_source_label_list(reversed(values)))
        self.assertEqual(visible_source_label_list(values),
                         r'\u0020A; A; A\u0020; b')

    def test_list_literal_semicolon_distinct(self):
        self.assertEqual(visible_source_label_list(('A;B', 'A')),
                         r'A; A\u003BB')

    def test_list_preserves_original_values(self):
        source = [' A ', 'A']
        snapshot = list(source)
        visible_source_label_list(source)
        self.assertEqual(source, snapshot)

    def test_hostile_str_subclass_rejected_without_hooks(self):
        class Hostile(str):
            def __hash__(self):
                raise AssertionError('PRIVATE_SOURCE')
            def lstrip(self, _):
                raise AssertionError('PRIVATE_SOURCE')
        for func, value in ((visible_identity_label, Hostile('A')),
                            (visible_source_label_list, [Hostile('A')])):
            with self.subTest(func=func.__name__):
                with self.assertRaises(TypeError) as raised:
                    func(value)
                self.assertNotIn('PRIVATE_SOURCE', str(raised.exception))
                self.assertIsNone(raised.exception.__cause__)

    def test_nonnative_type_fails_without_str_hook(self):
        class Hostile:
            def __str__(self):
                raise AssertionError('PRIVATE_SOURCE')
        with self.assertRaises(TypeError):
            visible_identity_label(Hostile())
        with self.assertRaises(TypeError):
            visible_source_label_list([Hostile()])

    def test_review_queue_shows_boundary_spelling(self):
        case = SimpleNamespace(report_row=3, source_key=' PO-9 ', flags='pending')
        self.assertEqual(visible_review_row(case, 'needs_evidence'),
                         (3, r'\u0020PO-9\u0020', 'pending', 'needs_evidence'))
        self.assertEqual(case.source_key, ' PO-9 ')

    def test_review_queue_keeps_existing_unicode_contract(self):
        case = SimpleNamespace(report_row=2, source_key='PO\u202e-1', flags='review\u200b_needed')
        self.assertEqual(visible_review_row(case, 'pending'),
                         (2, r'PO\u202E-1', r'review\u200B_needed', 'pending'))

    def test_review_queue_preserves_interior_spaces(self):
        case = SimpleNamespace(report_row=11, source_key='PO-1 / 2', flags='review')
        self.assertEqual(visible_review_row(case, 'pending')[1], 'PO-1 / 2')

    def test_plain_unicode_source_text_remains_unchanged(self):
        self.assertEqual(visible_source_text(' A '), ' A ')


if __name__ == '__main__':
    unittest.main()
