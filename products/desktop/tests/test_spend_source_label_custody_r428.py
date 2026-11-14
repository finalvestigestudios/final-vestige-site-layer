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


# R429 extends the already configured Ubuntu/Windows normal and -OO CI gate.
from hashlib import sha256


class BoundedVendorLabelPreviewR429(unittest.TestCase):
    def test_32_short_labels_remain_complete(self):
        labels = [f"ACME{i:03}" for i in range(32)]
        collision, count, output = evidence(*labels)
        self.assertTrue(collision)
        self.assertEqual(count, 32)
        self.assertNotIn("PREVIEW_ONLY", output)
        self.assertEqual(output, "; ".join(labels))

    def test_33rd_label_marked_as_omitted(self):
        labels = [f"ACME{i:03}" for i in range(33)]
        collision, count, output = evidence(*labels)
        self.assertTrue(collision)
        self.assertEqual(count, 33)
        self.assertIn("ACME031", output)
        self.assertNotIn("ACME032;", output)
        self.assertIn(r"\u[PREVIEW_ONLY:shown=32:omitted=1:sha256=", output)

    def test_omission_digest_64_lowercase_hex(self):
        labels = [f"S{i:03}" for i in range(34)]
        output = evidence(*labels)[2]
        self.assertRegex(output, r"\\u\[PREVIEW_ONLY:shown=32:omitted=2:sha256=[0-9a-f]{64}\]$")

    def test_preview_independent_of_input_order(self):
        labels = [f"A{i:03}" for i in range(100)]
        self.assertEqual(evidence(*labels), evidence(*reversed(labels)))

    def test_duplicates_do_not_inflate_preview_or_hash(self):
        labels = [f"A{i:03}" for i in range(40)]
        self.assertEqual(evidence(*labels), evidence(*(labels + labels)))

    def test_long_ascii_label_prefix_and_hash(self):
        label = "S" * 10_000
        collision, count, output = evidence(label)
        self.assertFalse(collision)
        self.assertEqual(count, 1)
        self.assertTrue(output.startswith("S" * 64 + r"\u[LABEL_PREFIX_ONLY]"))
        self.assertIn(r"\u[PREVIEW_ONLY:shown=1:omitted=0:sha256=", output)
        self.assertLessEqual(len(output), 8192)

    def test_1024_ascii_chars_remain_unabridged(self):
        label = "Q" * 1024
        self.assertEqual(evidence(label), (False, 1, label))

    def test_1025_ascii_chars_require_marked_prefix(self):
        label = "Q" * 1025
        self.assertIn(r"\u[LABEL_PREFIX_ONLY]", evidence(label)[2])

    def test_control_expansion_is_bounded(self):
        label = "\u200d" * 500
        output = evidence(label)[2]
        self.assertIn(r"\u[LABEL_PREFIX_ONLY]", output)
        self.assertLessEqual(len(output), 8192)

    def test_repeated_in_large_vendor_group_has_absolute_bound(self):
        labels = [f"V{i:05}" + "Q" * 900 for i in range(2_000)]
        collision, count, output = evidence(*labels)
        self.assertTrue(collision)
        self.assertEqual(count, 2000)
        self.assertIn("PREVIEW_ONLY", output)
        self.assertLessEqual(len(output), 8192)

    def test_boundary_whitespace_still_unambiguous_in_preview(self):
        label = " " + "Z" * 1800 + " "
        output = evidence(label)[2]
        self.assertTrue(output.startswith(r"\u0020"))
        self.assertIn("LABEL_PREFIX_ONLY", output)

    def test_source_marker_lookalike_does_not_forge_metadata(self):
        label = r"\u[PREVIEW_ONLY:shown=1:omitted=0:sha256=bad]"
        output = evidence(label)[2]
        self.assertTrue(output.startswith(r"\\u[PREVIEW_ONLY"))
        self.assertNotIn(r"; \u[PREVIEW_ONLY", output)

    def test_digest_changes_if_only_omitted_label_changes(self):
        first = [f"V{i:03}" for i in range(40)]
        second = first[:-1] + ["V999"]
        self.assertNotEqual(evidence(*first)[2].split("sha256=")[-1],
                            evidence(*second)[2].split("sha256=")[-1])

    def test_digest_distinguishes_framed_labels(self):
        first = ["a", "bc"] + [f"X{i:03}" for i in range(40)]
        second = ["ab", "c"] + [f"X{i:03}" for i in range(40)]
        self.assertNotEqual(evidence(*first)[2].split("sha256=")[-1],
                            evidence(*second)[2].split("sha256=")[-1])

    def test_invalid_utf8_in_digest_is_refused_without_data(self):
        bad = "CUSTOMER_SECRET" + "\ud800" * 1030
        with self.assertRaises(ValueError) as ctx:
            evidence(bad)
        self.assertNotIn("CUSTOMER_SECRET", str(ctx.exception))
        self.assertIsNone(ctx.exception.__context__)
        self.assertIsNone(ctx.exception.__cause__)

    def test_manual_digest_matches_framed_full_source_values(self):
        labels = [f"S{i:03}" for i in range(40)]
        digest = sha256(b"FVS-SPEND-RAW-VENDOR-LABELS-v1\n")
        for label in labels:
            data = label.encode("utf-8")
            digest.update(len(data).to_bytes(8, "big"))
            digest.update(data)
        self.assertTrue(evidence(*labels)[2].endswith("sha256=" + digest.hexdigest() + "]"))

    def test_mixed_collisions_and_case_counts_unchanged_with_preview(self):
        labels = [f"A{i:03}" for i in range(40)] + ["acme", "ACME"]
        collision, count, output = evidence(*labels)
        self.assertTrue(collision)
        self.assertEqual(count, 41)
        self.assertIn("PREVIEW_ONLY", output)
