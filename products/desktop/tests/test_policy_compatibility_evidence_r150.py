"""R150 synthetic end-to-end NFKC-only policy compatibility review evidence.

Codepoint audits are navigation aids, not regulatory/compliance decisions.
Tests exercise stable source snapshots, deterministic publication and SHA custody.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import policy_diff


class PolicyCompatibilityEvidenceR150(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-policy-nfkc-r150-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.before = self.root / "before.txt"
        self.after = self.root / "after.txt"
        self.report = self.root / "evidence.txt"

    def compare(self, a: str | bytes, b: str | bytes) -> str:
        old = a.encode("utf-8") if isinstance(a, str) else a
        new = b.encode("utf-8") if isinstance(b, str) else b
        self.before.write_bytes(old)
        self.after.write_bytes(new)
        produced = policy_diff.compare_policy_files(
            self.before, self.after, self.root, lambda *_: self.report)
        self.assertEqual([self.report], produced)
        self.assertEqual(self.before.read_bytes(), old)
        self.assertEqual(self.after.read_bytes(), new)
        result = self.report.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(old).hexdigest(), result)
        self.assertIn(hashlib.sha256(new).hexdigest(), result)
        return result

    def assert_compatibility(self, text):
        self.assertIn("NFKC-compatibility-equivalent ONLY", text)
        self.assertIn("NOT legal or semantic equivalence", text)
        self.assertNotIn("NFC-normalization-equivalent", text)

    def assert_not_compatibility(self, text):
        self.assertNotIn("NFKC-compatibility-equivalent ONLY", text)
        self.assertNotIn("Compatibility-sensitive codepoints", text)

    def test_fullwidth_latin_to_ascii_flagged(self):
        text = self.compare("Role Ａ\n", "Role A\n")
        self.assert_compatibility(text)
        self.assertIn("U+FF21", text)
        self.assertIn("-Role Ａ\n+Role A\n", text)

    def test_ascii_to_fullwidth_flagged(self):
        text = self.compare("Role A\n", "Role Ａ\n")
        self.assert_compatibility(text)
        self.assertIn("U+FF21", text)

    def test_ligature_expanded_flagged(self):
        text = self.compare("oﬃce\n", "office\n")
        self.assert_compatibility(text)
        self.assertIn("U+FB03", text)

    def test_two_digit_circled_number_flagged(self):
        text = self.compare("Limit ⑩\n", "Limit 10\n")
        self.assert_compatibility(text)
        self.assertIn("U+2469", text)

    def test_superscript_digit_flagged(self):
        text = self.compare("x²\n", "x2\n")
        self.assert_compatibility(text)
        self.assertIn("U+00B2", text)

    def test_roman_numeral_flagged(self):
        text = self.compare("Phase Ⅳ\n", "Phase IV\n")
        self.assert_compatibility(text)
        self.assertIn("U+2163", text)

    def test_mathematical_bold_letter_flagged(self):
        text = self.compare("𝐀\n", "A\n")
        self.assert_compatibility(text)
        self.assertIn("U+1D400", text)

    def test_subscript_digit_flagged(self):
        text = self.compare("H₂O\n", "H2O\n")
        self.assert_compatibility(text)
        self.assertIn("U+2082", text)

    def test_katakana_halfwidth_flagged(self):
        text = self.compare("ｶ\n", "カ\n")
        self.assert_compatibility(text)
        self.assertIn("U+FF76", text)

    def test_multiple_compatibility_symbols_sorted(self):
        text = self.compare("⑩ Ａ\n", "10 A\n")
        self.assert_compatibility(text)
        self.assertLess(text.index("U+2469"), text.index("U+FF21"))

    def test_reordered_equal_counts_have_precise_fallback(self):
        text = self.compare("①1\n", "1①\n")
        self.assert_compatibility(text)
        self.assertIn("codepoint totals did not change", text)
        self.assertNotIn("codepoints with changed source counts", text)

    def test_bounded_inventory_does_not_dump_entire_policy(self):
        old = "".join(chr(0xFF01 + x) for x in range(17)) + "\n"
        new = "".join(chr(0x21 + x) for x in range(17)) + "\n"
        text = self.compare(old, new)
        self.assert_compatibility(text)
        self.assertIn("U+FF01", text)
        self.assertIn("U+FF10", text)
        self.assertNotIn("U+FF11", text)
        self.assertIn("(+1 more)", text)

    def test_canonical_accent_is_nfc_only(self):
        text = self.compare("Café\n", "Cafe\u0301\n")
        self.assert_not_compatibility(text)
        self.assertIn("NFC-normalization-equivalent", text)

    def test_kelvin_sign_is_canonical_not_compatibility_only(self):
        text = self.compare("K\n", "K\n")
        self.assert_not_compatibility(text)
        self.assertIn("NFC-normalization-equivalent", text)

    def test_identical_compatibility_text_not_flagged(self):
        text = self.compare("Ⅳ\n", "Ⅳ\n")
        self.assert_not_compatibility(text)
        self.assertIn("No textual differences found", text)

    def test_arbitrary_amount_change_never_flagged(self):
        text = self.compare("Limit $10\n", "Limit $20\n")
        self.assert_not_compatibility(text)

    def test_partial_compatibility_match_not_flagged(self):
        text = self.compare("Ａ B\n", "A C\n")
        self.assert_not_compatibility(text)

    def test_bom_only_not_flagged(self):
        text = self.compare(b"same\n", b"\xef\xbb\xbfsame\n")
        self.assert_not_compatibility(text)
        self.assertIn("decoded text is identical", text)

    def test_crlf_only_not_flagged(self):
        text = self.compare(b"same\r\n", b"same\n")
        self.assert_not_compatibility(text)

    def test_end_of_file_marker_preserved(self):
        text = self.compare("Ⅳ", "IV")
        self.assert_compatibility(text)
        self.assertIn("\\ No newline at end of file", text)

    def test_physical_line_index_preserved(self):
        text = self.compare("Header\nLimit ⑩\nFooter\n",
                            "Header\nLimit 10\nFooter\n")
        self.assert_compatibility(text)
        self.assertIn("Hunk 001: before L2; after L2; -1 +1;", text)

    def test_sha_provenance_matches_exact_original_bytes(self):
        text = self.compare("Quantity ²\n", "Quantity 2\n")
        self.assertIn(hashlib.sha256("Quantity ²\n".encode()).hexdigest(), text)
        self.assertIn(hashlib.sha256(b"Quantity 2\n").hexdigest(), text)

    def test_same_inputs_produce_byte_identical_report(self):
        a = self.compare("⑩\n", "10\n")
        self.report.unlink()
        b = self.compare("⑩\n", "10\n")
        self.assertEqual(a, b)

    def test_existing_report_not_overwritten(self):
        self.report.write_text("PRIOR EVIDENCE", encoding="utf-8")
        self.before.write_text("⑩\n", encoding="utf-8")
        self.after.write_text("10\n", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            policy_diff.compare_policy_files(
                self.before, self.after, self.root, lambda *_: self.report)
        self.assertEqual(self.report.read_text(encoding="utf-8"), "PRIOR EVIDENCE")

    def test_invalid_utf8_rejected_before_report(self):
        self.before.write_text("ok\n", encoding="utf-8")
        self.after.write_bytes(b"bad\xff\n")
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            policy_diff.compare_policy_files(
                self.before, self.after, self.root, lambda *_: self.report)
        self.assertFalse(self.report.exists())

    def test_bidi_override_rejected_before_report(self):
        self.before.write_text("ok\n", encoding="utf-8")
        self.after.write_text("override\u202e\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "control"):
            policy_diff.compare_policy_files(
                self.before, self.after, self.root, lambda *_: self.report)
        self.assertFalse(self.report.exists())

    def test_private_parent_directory_not_emitted(self):
        text = self.compare("x²\n", "x2\n")
        self.assertNotIn(str(self.root), text)
        self.assertIn('Before: "before.txt"', text)

    def test_no_automatic_compliance_decision(self):
        text = self.compare("Policy ⑩\n", "Policy 10\n")
        self.assertIn("Text differences only. Not legal advice", text)
        self.assertIn("human review.", text)
        self.assert_compatibility(text)

    def test_escaped_backslash_cannot_fake_evidence(self):
        text = self.compare("literal\\u2469\n", "⑩\n")
        self.assert_not_compatibility(text)
        self.assertIn("-literal\\\\u2469", text)

    def test_multiline_composition_not_mislabeled(self):
        text = self.compare("A\nﬁ\nZ\n", "A\nfi\nZ\n")
        self.assert_compatibility(text)
        self.assertIn("Hunk 001: before L2; after L2;", text)


if __name__ == "__main__":
    unittest.main()
