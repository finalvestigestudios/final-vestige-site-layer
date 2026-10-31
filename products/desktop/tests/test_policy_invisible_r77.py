"""R77: Unicode format/variation visibility in source-fingerprinted policy diffs.

Uses exact policy_diff, csv_snapshot and atomic_text sources, genuine local
file snapshots and atomic reports. All documents and reviewer labels synthetic.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import policy_diff as pd


class InvisiblePolicyDiffR77(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.old = self.root / "prior.txt"
        self.new = self.root / "revised.txt"
        self.out = self.root / "policy-report.txt"

    def report(self, before: str | bytes, after: str | bytes) -> str:
        raw_old = before.encode("utf-8") if isinstance(before, str) else before
        raw_new = after.encode("utf-8") if isinstance(after, str) else after
        self.old.write_bytes(raw_old)
        self.new.write_bytes(raw_new)
        def output(folder, stem, suffix):
            self.assertEqual((Path(folder), stem, suffix),
                             (self.root, "policy-delta", ".txt"))
            return self.out
        self.assertEqual(pd.compare_policy_files(self.old, self.new,
                                                 self.root, output), [self.out])
        text = self.out.read_bytes().decode("utf-8")
        self.assertEqual(self.old.read_bytes(), raw_old)
        self.assertEqual(self.new.read_bytes(), raw_new)
        self.assertIn(hashlib.sha256(raw_old).hexdigest(), text)
        self.assertIn(hashlib.sha256(raw_new).hexdigest(), text)
        return text

    def test_zero_width_space_is_not_visually_silent(self):
        text = self.report("Approve\u200b payment\n", "Approve payment\n")
        self.assertIn("-Approve\\u200b payment\n+Approve payment\n", text)
        self.assertNotIn("\u200b", text)

    def test_soft_hyphen_is_visible(self):
        text = self.report("re\u00adview\n", "review\n")
        self.assertIn("-re\\u00adview\n+review\n", text)
        self.assertNotIn("\u00ad", text)

    def test_zero_width_nonjoiner_is_visible(self):
        text = self.report("policy\u200cA\n", "policyA\n")
        self.assertIn("-policy\\u200cA\n", text)

    def test_zero_width_joiner_is_visible(self):
        text = self.report("policy\u200dA\n", "policyA\n")
        self.assertIn("-policy\\u200dA\n", text)

    def test_word_joiner_is_visible(self):
        text = self.report("one\u2060two\n", "onetwo\n")
        self.assertIn("-one\\u2060two\n", text)

    def test_mongolian_vowel_separator_is_visible(self):
        text = self.report("ab\u180ecd\n", "abcd\n")
        self.assertIn("-ab\\u180ecd\n", text)

    def test_combining_grapheme_joiner_is_visible(self):
        text = self.report("ab\u034fcd\n", "abcd\n")
        self.assertIn("-ab\\u034fcd\n", text)

    def test_mongolian_variation_selector_is_visible(self):
        text = self.report("ab\u180bcd\n", "abcd\n")
        self.assertIn("-ab\\u180bcd\n", text)

    def test_bmp_variation_selector_is_visible(self):
        text = self.report("Reject\ufe0f\n", "Reject\n")
        self.assertIn("-Reject\\ufe0f\n", text)
        self.assertNotIn("\ufe0f", text)

    def test_supplementary_variation_selector_is_visible(self):
        text = self.report("Reject\U000e0100\n", "Reject\n")
        self.assertIn("-Reject\\U000e0100\n", text)
        self.assertNotIn("\U000e0100", text)

    def test_last_supplementary_variation_selector_is_visible(self):
        text = self.report("Reject\U000e01ef\n", "Reject\n")
        self.assertIn("-Reject\\U000e01ef\n", text)

    def test_literal_backslash_u_remains_distinct(self):
        text = self.report("mark\\u200b\n", "mark\u200b\n")
        self.assertIn("-mark\\\\u200b\n+mark\\u200b\n", text)
        self.assertNotIn("\u200b", text)

    def test_literal_backslash_capital_u_remains_distinct(self):
        text = self.report("mark\\U000e0100\n", "mark\U000e0100\n")
        self.assertIn("-mark\\\\U000e0100\n+mark\\U000e0100\n", text)

    def test_hidden_character_in_context_is_displayed(self):
        text = self.report("Reference\u200b line\nold\n", "Reference\u200b line\nnew\n")
        self.assertIn(" Reference\\u200b line\n-old\n+new\n", text)
        self.assertIn("@@ -1,2 +1,2 @@", text)

    def test_headers_and_hunk_positions_unchanged(self):
        old = [f"Row {i}\n" for i in range(20)]
        new = old[:]
        old[0] = "Approve\u200b\n"
        new[0] = "Approve\n"
        new[19] = "Change end\n"
        text = self.report("".join(old), "".join(new))
        self.assertEqual(text.count("@@ -"), 2)
        self.assertIn('--- before "prior.txt"\n', text)
        self.assertIn('+++ after "revised.txt"\n', text)

    def test_report_declares_non_patch_display_encoding(self):
        text = self.report("a\u200b\n", "a\n")
        self.assertIn("Invisible Unicode format and variation characters display as \\uXXXX or \\UXXXXXXXX.", text)
        self.assertIn("Text differences only. Not legal advice", text)

    def test_unicode_plain_letters_are_not_escaped(self):
        text = self.report("café 東京\n", "café 京都\n")
        self.assertIn("-café 東京\n+café 京都\n", text)

    def test_emoji_plain_codepoint_not_escaped(self):
        text = self.report("ready ✅\n", "ready ❌\n")
        self.assertIn("-ready ✅\n+ready ❌\n", text)

    def test_original_cr_tab_backslash_escaping_preserved(self):
        text = self.report(b"Review\t\\u200b\r\n", b"Review\t\xe2\x80\x8b\n")
        self.assertIn("-Review\\t\\\\u200b\\r\n+Review\\t\\u200b\n", text)
        self.assertNotIn("\r", text)
        self.assertNotIn("\t", text)

    def test_identical_source_bytes_still_request_review(self):
        text = self.report("unchanged\u200b\n", "unchanged\u200b\n")
        self.assertIn("Both source files have identical bytes", text)
        self.assertIn("No textual differences found.", text)

    def test_bom_only_change_still_requests_review(self):
        text = self.report(b"unchanged\n", b"\xef\xbb\xbfunchanged\n")
        self.assertIn("Source bytes differ but decoded text is identical", text)

    def test_unsafe_bidi_override_still_rejected_no_report(self):
        self.old.write_bytes(b"safe\n")
        self.new.write_bytes("unsafe\u202etext\n".encode("utf-8"))
        with self.assertRaisesRegex(ValueError, "unsupported control"):
            pd.compare_policy_files(self.old, self.new, self.root, lambda *_: self.out)
        self.assertFalse(self.out.exists())

    def test_ansi_escape_still_rejected_no_report(self):
        self.old.write_bytes(b"safe\n")
        self.new.write_bytes(b"unsafe\x1b[31mtext\n")
        with self.assertRaisesRegex(ValueError, "unsupported control"):
            pd.compare_policy_files(self.old, self.new, self.root, lambda *_: self.out)
        self.assertFalse(self.out.exists())

    def test_no_existing_report_is_overwritten(self):
        self.out.write_text("PREEXISTING VERIFIED EVIDENCE", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.report("A\u200b\n", "A\n")
        self.assertEqual(self.out.read_text(encoding="utf-8"), "PREEXISTING VERIFIED EVIDENCE")
        self.assertFalse(any(self.root.glob("*.partial")))

    def test_no_partial_files_after_success(self):
        self.report("A\u200b\n", "A\n")
        self.assertFalse(any(self.root.glob("*.partial")))

    def test_large_bounded_synthetic_context(self):
        old = ("Context\u200b\n" * 1200) + "old\n"
        new = ("Context\u200b\n" * 1200) + "new\n"
        text = self.report(old, new)
        self.assertIn(" Context\\u200b\n-old\n+new\n", text)
        self.assertNotIn("\u200b", text)

    def test_invalid_utf8_does_not_publish(self):
        self.old.write_bytes(b"Good\n")
        self.new.write_bytes(b"Bad \xff\n")
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            pd.compare_policy_files(self.old, self.new, self.root, lambda *_: self.out)
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
