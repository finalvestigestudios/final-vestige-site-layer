"""R428 offline original SpendMap vendor-label provenance regressions."""
from __future__ import annotations
import unittest
from fvs_suite.spend_vendor_evidence_r358 import spend_vendor_evidence

def evidence(*labels):
    return spend_vendor_evidence([{"vendor": label} for label in labels])

class OriginalVendorLabelCustodyR428(unittest.TestCase):
    def test_single_leading_ascii_space_is_visible(self):
        self.assertEqual(evidence(" ACME"), (False, 1, r"\u0020ACME"))
    def test_multiple_leading_ascii_spaces_are_distinguishable(self):
        self.assertEqual(evidence("  ACME"), (False, 1, r"\u0020\u0020ACME"))
    def test_trailing_ascii_space_is_visible(self):
        self.assertEqual(evidence("ACME "), (False, 1, r"ACME\u0020"))
    def test_mixed_boundary_spaces_retained(self):
        self.assertEqual(evidence(" ACME "), (False, 1, r"\u0020ACME\u0020"))
    def test_tab_and_cr_stay_literal_escape_labels(self):
        self.assertEqual(evidence("\tACME\r"), (False, 1, r"\u0009ACME\u000D"))
    def test_original_aliases_remain_visible_but_not_collisions(self):
        collision, count, display = evidence(" ACME", "ACME")
        self.assertFalse(collision)
        self.assertEqual(count, 1)
        self.assertIn(r"\u0020ACME", display)
        self.assertIn("ACME", display)
    def test_original_ascii_case_remains_distinct_display(self):
        collision, count, display = evidence("ACME", "acme", " ACME ")
        self.assertFalse(collision)
        self.assertEqual(count, 1)
        self.assertIn(r"\u0020ACME\u0020", display)
        self.assertIn("acme", display)
    def test_semicolon_always_escaped(self):
        self.assertEqual(evidence(" A;B "), (False, 1, r"\u0020A\u003BB\u0020"))
    def test_literal_backslash_escape_is_not_original_space(self):
        collision, count, display = evidence(" ACME", r"\u0020ACME")
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn(r"\u0020ACME", display)
        self.assertIn(r"\\u0020ACME", display)
    def test_leading_unicode_nbsp_still_distinct(self):
        collision, count, display = evidence(" ACME", "\u00a0ACME")
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn(r"\u00A0ACME", display)
    def test_combining_mark_is_revealed(self):
        collision, count, display = evidence("A\u0301", "A")
        self.assertTrue(collision)
        self.assertEqual(count, 2)
        self.assertIn(r"A\u0301", display)
    def test_whitespace_only_label_suppressed(self):
        self.assertEqual(evidence(" \t\r "), (False, 0, ""))
    def test_empty_label_suppressed(self):
        self.assertEqual(evidence(""), (False, 0, ""))
    def test_independent_of_input_permutation(self):
        labels=[" ACME", "ACME ", "acme", "\u00a0ACME", "A;B"]
        self.assertEqual(evidence(*labels), evidence(*reversed(labels)))
    def test_duplicates_preserve_one_display_label(self):
        self.assertEqual(evidence(" ACME", " ACME"), (False, 1, r"\u0020ACME"))
    def test_reject_untrusted_source_subclass(self):
        class Spy(str):
            def strip(self,*a): raise AssertionError("CUSTOMER_PRIVATE")
        with self.assertRaisesRegex(ValueError,"native source text"):
            evidence(Spy(" ACME"))
    def test_no_private_source_in_type_error(self):
        class Spy:
            def __str__(self): raise AssertionError("CUSTOMER_PRIVATE")
        with self.assertRaises(ValueError) as cm:
            evidence(Spy())
        self.assertNotIn("CUSTOMER_PRIVATE",str(cm.exception))
    def test_non_ascii_boundary_not_removed(self):
        self.assertEqual(evidence("\u202fACME"), (False, 1, r"\u202FACME"))
