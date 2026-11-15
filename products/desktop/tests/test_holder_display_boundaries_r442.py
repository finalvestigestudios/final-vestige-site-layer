"""R442: premium display identity refuses hidden separators and noncharacters."""
from __future__ import annotations

import unicodedata
import unittest

from fvs_suite.holder_identity import MAX_HOLDER_CODEPOINTS, valid_holder


class PoisonStr(str):
    def strip(self):
        raise AssertionError("str-subclass methods must not execute")


class HolderDisplayBoundariesR442(unittest.TestCase):
    def test_rejects_all_non_ascii_unicode_space_separators_inside_name(self):
        points = (0x00A0, 0x1680, *range(0x2000, 0x200B), 0x202F, 0x205F, 0x3000)
        for point in points:
            with self.subTest(point=hex(point)):
                self.assertEqual(unicodedata.category(chr(point)), "Zs")
                self.assertFalse(valid_holder("Acme" + chr(point) + "Ltd"))

    def test_rejects_each_reserved_bmp_noncharacter(self):
        for point in range(0xFDD0, 0xFDF0):
            with self.subTest(point=hex(point)):
                self.assertFalse(valid_holder("Acme" + chr(point) + "Ltd"))

    def test_rejects_both_noncharacters_at_end_of_all_seventeen_planes(self):
        for plane in range(17):
            for suffix in (0xFFFE, 0xFFFF):
                point = plane * 0x10000 + suffix
                with self.subTest(point=hex(point)):
                    self.assertFalse(valid_holder("Acme" + chr(point) + "Ltd"))

    def test_rejects_bmp_variation_selectors(self):
        for point in range(0xFE00, 0xFE10):
            with self.subTest(point=hex(point)):
                self.assertFalse(valid_holder("Acme" + chr(point) + "Ltd"))

    def test_rejects_supplementary_variation_selectors(self):
        for point in range(0xE0100, 0xE01F0):
            with self.subTest(point=hex(point)):
                self.assertFalse(valid_holder("Acme" + chr(point) + "Ltd"))

    def test_accepts_visible_language_names_and_regular_internal_spaces(self):
        for holder in ("Acme Ltd", "Acme  Ltd", "Société de recherche", "شركة الأبحاث",
                       "株式会社サンプル", "Ácme", "A\u0301cme", "A" * MAX_HOLDER_CODEPOINTS):
            with self.subTest(holder=holder):
                self.assertTrue(valid_holder(holder))

    def test_refuses_str_subclass_without_method_invocation(self):
        self.assertFalse(valid_holder(PoisonStr("Acme Ltd")))

    def test_limits_signed_holder_length_without_trim_or_rewrite(self):
        self.assertFalse(valid_holder("A" * (MAX_HOLDER_CODEPOINTS + 1)))
        self.assertFalse(valid_holder("Acme "))
        self.assertFalse(valid_holder(" Acme"))
        self.assertFalse(valid_holder(""))
        self.assertTrue(valid_holder("A\u0301cme"))
        self.assertTrue(valid_holder("Ácme"))

    def test_preserves_prior_directional_and_control_refusals(self):
        for char in ("\u202e", "\u2069", "\u200b", "\x85", "\u2028", "\ud800"):
            with self.subTest(char=ascii(char)):
                self.assertFalse(valid_holder("Acme" + char + "Ltd"))


if __name__ == "__main__":
    unittest.main()
