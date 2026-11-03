"""R151 end-to-end Policy Delta local compatibility substitution evidence.

All sample files are synthetic. There is no legal or compliance determination.
"""
from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from fvs_suite import policy_diff


class PolicyLocalCompatibilityR151(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="fvs-policy-local-r151-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.before = self.root / "old.txt"
        self.after = self.root / "new.txt"
        self.report = self.root / "report.txt"

    def compare(self, old: str | bytes, new: str | bytes) -> str:
        a = old.encode("utf-8") if isinstance(old, str) else old
        b = new.encode("utf-8") if isinstance(new, str) else new
        self.before.write_bytes(a)
        self.after.write_bytes(b)
        paths = policy_diff.compare_policy_files(
            self.before, self.after, self.root, lambda *_: self.report)
        self.assertEqual(paths, [self.report])
        self.assertEqual(self.before.read_bytes(), a)
        self.assertEqual(self.after.read_bytes(), b)
        body = self.report.read_text(encoding="utf-8")
        self.assertIn(hashlib.sha256(a).hexdigest(), body)
        self.assertIn(hashlib.sha256(b).hexdigest(), body)
        return body

    def test_mixed_unrelated_change_still_cites_compatibility_pair(self):
        body = self.compare("Limit ⑩\nOwner: Old\n", "Limit 10\nOwner: New\n")
        self.assertNotIn("NFKC-compatibility-equivalent ONLY", body)
        self.assertIn("LOCAL REVIEW: NFKC-only", body)
        self.assertIn("Local hunk 001: before L1; after L1;", body)
        self.assertIn("U+2469", body)
        self.assertIn("Owner: New", body)

    def test_other_sentence_edits_in_distinct_hunk(self):
        a = "Limit ⑩\n" + "untouched\n" * 9 + "Owner: A\n"
        b = "Limit 10\n" + "untouched\n" * 9 + "Owner: B\n"
        body = self.compare(a, b)
        self.assertIn("Local hunk 001: before L1; after L1;", body)
        self.assertIn("Hunk 002:", body)

    def test_fullwidth_compatibility_pair(self):
        body = self.compare("Role Ａ\n", "Role A\n")
        self.assertIn("U+FF21", body)
        self.assertIn("Local hunk 001: before L1; after L1;", body)

    def test_superscript_compatibility_pair(self):
        body = self.compare("Area m²\n", "Area m2\n")
        self.assertIn("U+00B2", body)

    def test_ligature_compatibility_pair(self):
        body = self.compare("oﬃce\n", "office\n")
        self.assertIn("U+FB03", body)

    def test_math_bold_compatibility_pair(self):
        body = self.compare("𝐀\n", "A\n")
        self.assertIn("U+1D400", body)

    def test_roman_compatibility_pair(self):
        body = self.compare("IV = Ⅳ\n", "IV = IV\n")
        self.assertIn("U+2163", body)

    def test_two_unique_pairs_one_hunk(self):
        body = self.compare("Alpha Ａ\nBudget ⑩\n",
                            "Alpha A\nBudget 10\n")
        self.assertIn("Local hunk 001: before L1; after L1;", body)
        self.assertIn("Local hunk 001: before L2; after L2;", body)

    def test_newline_missing_still_reports(self):
        body = self.compare("Limit ⑩", "Limit 10")
        self.assertIn("Local hunk 001: before L1; after L1;", body)
        self.assertIn("No newline at end of file", body)

    def test_source_line_numbers_not_diff_display_indices(self):
        body = self.compare("Same\nSame\nLimit ⑩\n",
                            "Same\nSame\nLimit 10\n")
        self.assertIn("Local hunk 001: before L3; after L3;", body)

    def test_reorder_with_equal_codepoint_counts_cited(self):
        body = self.compare("①1\n", "1①\n")
        self.assertIn("Local hunk 001: before L1; after L1;", body)
        self.assertIn("codepoint totals did not change", body)

    def test_no_pair_for_real_numeric_change(self):
        body = self.compare("Limit 10\n", "Limit 20\n")
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)

    def test_no_pair_for_mixed_real_and_unicode_same_line(self):
        body = self.compare("Limit ⑩ was 2025\n",
                            "Limit 10 was 2026\n")
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)

    def test_no_pair_for_canonical_nfc_composition(self):
        body = self.compare("Café\n", "Cafe\u0301\n")
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)
        self.assertIn("NFC-normalization-equivalent", body)

    def test_no_pair_for_kelvin_canonical_character(self):
        body = self.compare("K\n", "K\n")
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)

    def test_no_pair_for_cyrillic_latin_lookalike(self):
        body = self.compare("A\n", "А\n")  # Cyrillic capital A
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)

    def test_no_pair_for_addition_without_removal(self):
        body = self.compare("Existing\n", "Existing\nLimit ⑩\n")
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)

    def test_no_pair_for_removal_without_addition(self):
        body = self.compare("Existing\nLimit ⑩\n", "Existing\n")
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)

    def test_identical_policy_no_local_review(self):
        body = self.compare("Limit ⑩\n", "Limit ⑩\n")
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)
        self.assertIn("No textual differences found", body)

    def test_bom_only_no_local_review(self):
        body = self.compare(b"Same\n", b"\xef\xbb\xbfSame\n")
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)

    def test_crlf_only_no_local_review(self):
        body = self.compare(b"Same\r\n", b"Same\n")
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)

    def test_ambiguous_duplicate_folded_lines_not_paired(self):
        body = self.compare("⑩\n⑩\n", "10\n10\n")
        self.assertNotIn("LOCAL REVIEW: NFKC-only", body)
        self.assertIn("NFKC-compatibility-equivalent ONLY", body)

    def test_bounded_to_sixteen_pairs(self):
        a = "".join(f"{i:02d} Ａ\n" for i in range(17))
        b = "".join(f"{i:02d} A\n" for i in range(17))
        body = self.compare(a, b)
        self.assertEqual(body.count("NFKC-only candidate;"), 16)
        self.assertIn("+1 additional unique candidate pair(s) omitted", body)

    def test_deterministic_replay(self):
        a = self.compare("Limit ⑩\nOther: A\n", "Limit 10\nOther: B\n")
        self.report.unlink()
        b = self.compare("Limit ⑩\nOther: A\n", "Limit 10\nOther: B\n")
        self.assertEqual(a, b)

    def test_originals_and_private_paths_not_emitted(self):
        body = self.compare("Budget ⑩\n", "Budget 10\n")
        self.assertIn('Before: "old.txt"', body)
        self.assertNotIn(str(self.root), body)
        self.assertIn("SHA-256:", body)

    def test_human_review_not_compliance_authorization(self):
        body = self.compare("Grant ⑩\n", "Grant 10\n")
        self.assertIn("NOT legal or semantic equivalence", body)
        self.assertIn("Not legal advice or a compliance determination", body)

    def test_existing_report_not_overwritten(self):
        self.before.write_text("Budget ⑩\n", encoding="utf-8")
        self.after.write_text("Budget 10\n", encoding="utf-8")
        self.report.write_text("PRIOR", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            policy_diff.compare_policy_files(
                self.before, self.after, self.root, lambda *_: self.report)
        self.assertEqual(self.report.read_text(encoding="utf-8"), "PRIOR")

    def test_invalid_utf8_rejects_without_report(self):
        self.before.write_text("ok\n", encoding="utf-8")
        self.after.write_bytes(b"bad\xff")
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            policy_diff.compare_policy_files(
                self.before, self.after, self.root, lambda *_: self.report)
        self.assertFalse(self.report.exists())

    def test_bidi_control_rejects_without_report(self):
        self.before.write_text("ok\n", encoding="utf-8")
        self.after.write_text("bad\u202e\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "control"):
            policy_diff.compare_policy_files(
                self.before, self.after, self.root, lambda *_: self.report)
        self.assertFalse(self.report.exists())


if __name__ == "__main__":
    unittest.main()
