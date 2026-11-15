"""Portable, exact-source R441 validation of premium holder display custody."""
import unittest
from fvs_suite.holder_identity import valid_holder, MAX_HOLDER_CODEPOINTS


class NoMethods(str):
    def strip(self, *a, **k):
        raise AssertionError('Must not invoke str-subclass methods')


class HolderIdentityR441(unittest.TestCase):
    def test_accepts_realistic_visible_international_names(self):
        for name in ('Test Org', 'Société de recherche', 'شركة الأبحاث', '株式会社サンプル', 'Grant & Procurement 2026', 'A' * MAX_HOLDER_CODEPOINTS):
            with self.subTest(name=name):
                self.assertTrue(valid_holder(name))

    def test_rejects_unicode_control_and_directional_spoofing(self):
        for codepoint in ('\x00', '\n', '\x7f', '\x85', '\u200e', '\u200f', '\u202a', '\u202e', '\u2066', '\u2069', '\u200b', '\u200d', '\u2028', '\u2029', '\ud800'):
            with self.subTest(codepoint=ascii(codepoint)):
                self.assertFalse(valid_holder('Acme'+codepoint+'Ltd'))

    def test_refuses_empty_boundaries_and_wrong_types(self):
        for name in ('', ' ', ' Acme', 'Acme ', '\u00a0Acme', 'Acme\u00a0', 'X' * 121, b'Acme', None, NoMethods('Acme')):
            with self.subTest(type=type(name).__name__, name=repr(name)):
                self.assertFalse(valid_holder(name))

    def test_does_not_rewrite_or_conflate_visible_text(self):
        for name in ('Ácme', 'A\u0301cme', 'شركة أبحاث', 'Société / Research'):
            self.assertTrue(valid_holder(name))

if __name__ == '__main__':
    unittest.main()
