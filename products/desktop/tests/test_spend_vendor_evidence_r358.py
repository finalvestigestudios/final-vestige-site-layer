"""R358 Unicode-safe SpendMap vendor provenance, synthetic inputs only."""
from __future__ import annotations

import unittest

from fvs_suite.spend_vendor_evidence_r358 import spend_vendor_evidence


def vendors(*names):
    return [{"vendor": name} for name in names]


class SpendVendorEvidenceR358(unittest.TestCase):
    def test_normal_ascii_case_does_not_flag_collision(self):
        collision, count, labels = spend_vendor_evidence(vendors("ACME", "acme"))
        self.assertFalse(collision)
        self.assertEqual(count, 1)
        self.assertIn("ACME", labels)
        self.assertIn("acme", labels)

    def test_ascii_boundary_whitespace_compatibility(self):
        collision, count, labels = spend_vendor_evidence(vendors(" \tACME\r", "ACME"))
        self.assertFalse(collision)  # Matching still ignores ordinary ASCII boundary whitespace.
        self.assertEqual(count, 1)
        self.assertIn(r"\u0020\u0009ACME\u000D", labels)
        self.assertIn("ACME", labels)

    def test_nbsp_is_distinct(self):
        collision, count, labels = spend_vendor_evidence(vendors("ACME", "\u00a0ACME"))
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn(r"\u00A0ACME", labels)

    def test_figure_space_is_distinct(self):
        collision, count, labels = spend_vendor_evidence(vendors("ACME", "ACME\u2007"))
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn(r"ACME\u2007", labels)

    def test_narrow_nbsp_is_distinct(self):
        collision, count, labels = spend_vendor_evidence(vendors("ACME", "ACME\u202f"))
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn(r"ACME\u202F", labels)

    def test_unicode_format_character_is_distinct(self):
        collision, count, labels = spend_vendor_evidence(vendors("AB", "A\u200dB"))
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn(r"A\u200DB", labels)

    def test_preserves_only_source_unicode_label(self):
        collision, count, labels = spend_vendor_evidence(vendors("\u00a0ACME"))
        self.assertFalse(collision)
        self.assertEqual(count, 1)
        self.assertEqual(labels, r"\u00A0ACME")

    def test_source_escape_literal_distinct_from_character(self):
        collision, count, labels = spend_vendor_evidence(vendors("\u00a0ACME", r"\u00A0ACME"))
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn(r"\u00A0ACME", labels)
        self.assertIn(r"\\u00A0ACME", labels)

    def test_semicolons_cannot_forge_labels(self):
        collision, count, labels = spend_vendor_evidence(vendors("A;B", "AB"))
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn(r"A\u003BB", labels)

    def test_deterministic_across_source_order(self):
        names = ["\u00a0ACME", "Acme", "ACME", "B;B"]
        self.assertEqual(spend_vendor_evidence(vendors(*names)),
                         spend_vendor_evidence(vendors(*reversed(names))))

    def test_duplicate_label_does_not_inflate_count(self):
        self.assertEqual(spend_vendor_evidence(vendors("ACME", "ACME")),
                         (False, 1, "ACME"))

    def test_non_native_source_rejected(self):
        class SourceStr(str):
            def strip(self, *args):
                raise AssertionError("do not call source methods")
        with self.assertRaises(ValueError):
            spend_vendor_evidence(vendors(SourceStr("ACME")))

    def test_invalid_source_error_has_no_source_text(self):
        with self.assertRaises(ValueError) as ctx:
            spend_vendor_evidence([{"vendor": None}])
        self.assertNotIn("None", str(ctx.exception))

    def test_empty_rows(self):
        self.assertEqual(spend_vendor_evidence([]), (False, 0, ""))

    def test_unicode_disambiguation_without_normalizing_source(self):
        collision, count, labels = spend_vendor_evidence(vendors("Cafe", "Caf\u00e9"))
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn("Caf\u00e9", labels)

    def test_control_character_is_visible(self):
        collision, count, labels = spend_vendor_evidence(vendors("ACME", "A\u0001CME"))
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn(r"A\u0001CME", labels)


if __name__ == "__main__":
    unittest.main()
