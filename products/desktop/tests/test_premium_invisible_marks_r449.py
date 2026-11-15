"""R449 regression: premium evidence labels refuse invisible selection marks.

Only synthetic names are used; the tests don't authorize a release.
"""
from __future__ import annotations

import json
import unittest

from fvs_suite.evidence_label import canonical_evidence_label


class PremiumInvisibleEvidenceMarksR449(unittest.TestCase):
    def assertRefused(self, name):
        with self.assertRaisesRegex(ValueError, "Invalid evidence filename label"):
            canonical_evidence_label(name)

    def test_combining_grapheme_joiner_is_refused(self):
        for name in ("claim\u034f.csv", "\u034fclaim.csv", "claim.csv\u034f"):
            with self.subTest(label=repr(name)):
                self.assertRefused(name)

    def test_mongolian_variation_selector_range_is_refused(self):
        for point in range(0x180B, 0x1810):
            with self.subTest(codepoint=f"U+{point:04X}"):
                self.assertRefused(f"claim{chr(point)}.csv")

    def test_bmp_variation_selector_range_is_refused(self):
        for point in range(0xFE00, 0xFE10):
            with self.subTest(codepoint=f"U+{point:04X}"):
                self.assertRefused(f"report{chr(point)}.csv")

    def test_supplementary_variation_selector_range_is_refused(self):
        for point in (0xE0100, 0xE0101, 0xE0150, 0xE01EE, 0xE01EF):
            with self.subTest(codepoint=f"U+{point:06X}"):
                self.assertRefused(f"receipt{chr(point)}.csv")

    def test_selector_in_extension_is_refused(self):
        for mark in ("\ufe00", "\ufe0f", "\U000e0100"):
            with self.subTest(mark=ascii(mark)):
                self.assertRefused("evidence.c" + mark + "sv")

    def test_emoji_with_hidden_variation_selector_is_refused(self):
        self.assertRefused("📄\ufe0f-report.csv")

    def test_visible_combining_accent_remains_supported(self):
        for name in ("Cafe\u0301.csv", "A\u030angstro\u0308m.csv", "Café.csv"):
            with self.subTest(name=ascii(name)):
                result = canonical_evidence_label(name)
                self.assertEqual(json.loads('"' + result + '"'), name)

    def test_visible_international_names_and_plain_emoji_supported(self):
        for name in ("收据 東京.csv", "relatório.csv", "📄-report.csv"):
            with self.subTest(name=ascii(name)):
                self.assertEqual(json.loads('"' + canonical_evidence_label(name) + '"'), name)

    def test_ordinary_ascii_is_stable_and_json_canonical(self):
        for name in ("claim-1.csv", "grant report.csv", "invoice_2026-11.csv"):
            with self.subTest(name=name):
                self.assertEqual(canonical_evidence_label(name),
                                 json.dumps(name, ensure_ascii=True)[1:-1])

    def test_windows_device_and_path_defenses_still_hold(self):
        for name in ("CON.txt", "COM¹.csv", "AUX", "report:.csv", "x/y.csv",
                     "a\\b.csv", "a.csv.", "a.csv "):
            with self.subTest(name=ascii(name)):
                self.assertRefused(name)


if __name__ == "__main__":
    unittest.main()
