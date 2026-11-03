"""R149: policy Unicode codepoint evidence with synthetic local documents only.

No legal interpretation is made. Raw SHA-256 and original bytes are authoritative;
this suite tests the actual snapshot reader, diff renderer and atomic publisher.
"""
from __future__ import annotations

import hashlib
import tempfile
import unicodedata
import unittest
from pathlib import Path

from fvs_suite import policy_diff


class PolicyNormalizationEvidenceR149(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="fvs-policy-nfc-r149-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.old = self.root / "old.txt"
        self.new = self.root / "new.txt"
        self.output = self.root / "policy-delta-r149.txt"

    def compare(self, before: str | bytes, after: str | bytes) -> str:
        original = before.encode("utf-8") if isinstance(before, str) else before
        revised = after.encode("utf-8") if isinstance(after, str) else after
        self.old.write_bytes(original)
        self.new.write_bytes(revised)
        paths = policy_diff.compare_policy_files(
            self.old, self.new, self.root,
            lambda folder, stem, suffix: self.output)
        self.assertEqual(paths, [self.output])
        self.assertEqual(self.old.read_bytes(), original)
        self.assertEqual(self.new.read_bytes(), revised)
        text = self.output.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(original).hexdigest(), text)
        self.assertIn(hashlib.sha256(revised).hexdigest(), text)
        return text

    def no_report(self):
        self.assertFalse(self.output.exists())
        self.assertFalse(list(self.root.glob("*.partial")))

    def test_composed_to_decomposed_accent_reveals_codepoint(self):
        report = self.compare("Café\n", "Cafe\u0301\n")
        self.assertIn("-Café\n+Cafe\\u0301\n", report)
        self.assertNotIn("\u0301", report)
        self.assertIn("NFC-normalization-equivalent", report)

    def test_decomposed_to_composed_accent_is_reversible(self):
        report = self.compare("Cafe\u0301\n", "Café\n")
        self.assertIn("-Cafe\\u0301\n+Café\n", report)
        self.assertIn("NFC-normalization-equivalent", report)

    def test_canonically_reordered_diacritics_are_flagged(self):
        old = "e\u0301\u0323\n"
        new = "e\u0323\u0301\n"
        self.assertEqual(unicodedata.normalize("NFC", old),
                         unicodedata.normalize("NFC", new))
        report = self.compare(old, new)
        self.assertIn("-e\\u0301\\u0323\n+e\\u0323\\u0301\n", report)
        self.assertIn("NFC-normalization-equivalent", report)

    def test_identical_decomposed_text_does_not_fabricate_change(self):
        report = self.compare("Cafe\u0301\n", "Cafe\u0301\n")
        self.assertIn("No textual differences found.", report)
        self.assertNotIn("NFC-normalization-equivalent", report)

    def test_accent_removed_is_not_mislabeled_canonically_equal(self):
        report = self.compare("Cafe\u0301\n", "Cafe\n")
        self.assertIn("-Cafe\\u0301\n+Cafe\n", report)
        self.assertNotIn("NFC-normalization-equivalent", report)

    def test_hiragana_decomposition_is_visible(self):
        report = self.compare("が\n", "か\u3099\n")
        self.assertIn("-が\n+か\\u3099\n", report)
        self.assertIn("NFC-normalization-equivalent", report)

    def test_hebrew_nonspacing_mark_is_explicit(self):
        report = self.compare("ab\u05b0cd\n", "abcd\n")
        self.assertIn("-ab\\u05b0cd\n+abcd\n", report)

    def test_arabic_nonspacing_mark_is_explicit(self):
        report = self.compare("ab\u064ecd\n", "abcd\n")
        self.assertIn("-ab\\u064ecd\n+abcd\n", report)

    def test_devanagari_nukta_is_explicit(self):
        report = self.compare("ab\u093ccd\n", "abcd\n")
        self.assertIn("-ab\\u093ccd\n+abcd\n", report)

    def test_thai_nonspacing_mark_is_explicit(self):
        report = self.compare("ab\u0e31cd\n", "abcd\n")
        self.assertIn("-ab\\u0e31cd\n+abcd\n", report)

    def test_enclosing_circle_mark_is_explicit(self):
        report = self.compare("Clause\u20dd\n", "Clause\n")
        self.assertIn("-Clause\\u20dd\n+Clause\n", report)

    def test_supplementary_combining_mark_uses_eight_digits(self):
        report = self.compare("Note\U0001d185\n", "Note\n")
        self.assertIn("-Note\\U0001d185\n+Note\n", report)
        self.assertNotIn("\U0001d185", report)

    def test_plain_multilingual_letters_remain_readable(self):
        report = self.compare("Café 東京 שלום\n", "Café 京都 שלום\n")
        self.assertIn("-Café 東京 שלום\n+Café 京都 שלום\n", report)

    def test_spacing_combining_mark_remains_readable(self):
        # Mc vowel signs are visible spacing marks, unlike Mn/Me overlays.
        report = self.compare("क\u093e\n", "क\n")
        self.assertIn("-का\n+क\n", report)
        self.assertNotIn("\\u093e", report)

    def test_literal_escape_cannot_impersonate_actual_accent(self):
        report = self.compare("mark\\u0301\n", "mark\u0301\n")
        self.assertIn("-mark\\\\u0301\n+mark\\u0301\n", report)
        self.assertNotIn("NFC-normalization-equivalent", report)

    def test_unchanged_context_marks_are_escaped(self):
        report = self.compare("Title\u0301\nOld\n", "Title\u0301\nNew\n")
        self.assertIn(" Title\\u0301\n-Old\n+New\n", report)

    def test_change_index_keeps_exact_physical_citations(self):
        report = self.compare("Context\nCafe\u0301\nEnd\n",
                              "Context\nCafé\nEnd\n")
        self.assertIn("Hunk 001: before L2; after L2; -1 +1;", report)
        self.assertIn("@@ -1,3 +1,3 @@", report)

    def test_bom_only_does_not_claim_normalization_difference(self):
        report = self.compare(b"same\n", b"\xef\xbb\xbfsame\n")
        self.assertIn("Source bytes differ but decoded text is identical", report)
        self.assertNotIn("NFC-normalization-equivalent", report)

    def test_crlf_only_is_not_unicode_normalization_difference(self):
        report = self.compare(b"same\r\n", b"same\n")
        self.assertIn("-same\\r\n+same\n", report)
        self.assertNotIn("NFC-normalization-equivalent", report)

    def test_original_source_sha256_and_inputs_are_authoritative(self):
        old, new = "A\u0301\n", "Á\n"
        report = self.compare(old, new)
        self.assertIn(hashlib.sha256(old.encode()).hexdigest(), report)
        self.assertIn(hashlib.sha256(new.encode()).hexdigest(), report)
        self.assertEqual(self.old.read_bytes(), old.encode())
        self.assertEqual(self.new.read_bytes(), new.encode())

    def test_same_sources_generate_byte_identical_reports(self):
        first = self.compare("e\u0301\n", "é\n")
        self.output.unlink()
        second = self.compare("e\u0301\n", "é\n")
        self.assertEqual(first, second)

    def test_existing_report_is_never_overwritten(self):
        self.output.write_text("PRIOR AUDIT EVIDENCE", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.compare("e\u0301\n", "é\n")
        self.assertEqual(self.output.read_text(encoding="utf-8"),
                         "PRIOR AUDIT EVIDENCE")
        self.assertFalse(list(self.root.glob("*.partial")))

    def test_invalid_utf8_rejected_before_publication(self):
        self.old.write_bytes(b"good\n")
        self.new.write_bytes(b"bad\xff\n")
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            policy_diff.compare_policy_files(
                self.old, self.new, self.root, lambda *_: self.output)
        self.no_report()

    def test_bidi_override_still_rejected_before_publication(self):
        self.old.write_text("fine\n", encoding="utf-8")
        self.new.write_text("approve\u202e deny\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "control"):
            policy_diff.compare_policy_files(
                self.old, self.new, self.root, lambda *_: self.output)
        self.no_report()

    def test_private_path_is_not_repeated_in_report(self):
        report = self.compare("e\u0301\n", "é\n")
        self.assertNotIn(str(self.root), report)
        self.assertIn('Before: "old.txt"', report)
        self.assertIn('After: "new.txt"', report)

    def test_report_declares_combining_display_contract(self):
        report = self.compare("e\u0301\n", "é\n")
        self.assertIn("Unicode nonspacing/enclosing combining marks display as", report)
        self.assertIn("Not legal advice or a compliance determination.", report)

    def test_nfkc_only_equivalence_is_not_misclassified(self):
        # Fullwidth A normalizes under NFKC, NOT NFC.
        report = self.compare("Ａ\n", "A\n")
        self.assertNotIn("NFC-normalization-equivalent", report)
        self.assertIn("-Ａ\n+A\n", report)

    def test_unterminated_last_line_preserves_source_eof_markers(self):
        report = self.compare("e\u0301", "é")
        self.assertIn("-e\\u0301\n\\ No newline at end of file\n", report)
        self.assertIn("+é\n\\ No newline at end of file\n", report)

    def test_mark_only_insert_is_visible_and_not_canonical_equivalence(self):
        report = self.compare("Refund\n", "Refund\u0301\n")
        self.assertIn("-Refund\n+Refund\\u0301\n", report)
        self.assertNotIn("NFC-normalization-equivalent", report)

    def test_large_synthetic_context_preserves_audit_index(self):
        before = ("Context\u0301\n" * 800) + "Old\n"
        after = ("Context\u0301\n" * 800) + "New\n"
        report = self.compare(before, after)
        self.assertIn("Hunk 001: before L801; after L801;", report)
        self.assertIn(" Context\\u0301\n-Old\n+New\n", report)


if __name__ == "__main__":
    unittest.main()
