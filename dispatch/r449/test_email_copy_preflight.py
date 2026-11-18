"""Purely synthetic fixtures: no subscriber records, network, WordPress or merchant actions."""
import pathlib
import tempfile
import unittest

from email_copy_preflight import SOURCE_PAIRS, analyze_text, git_blob_sha, scan

SUBJECT = "**Subject:** The evidence remains incomplete\n**Preheader:** A safer next step.\n"
EDITORIAL = SUBJECT + "Read the source. [[POSTAL_REQUIRED]] [[UNSUBSCRIBE_REQUIRED]] postal unsubscribe."
COMMERCIAL = EDITORIAL + " Commercial disclosure: our future guide may earn us commission."


class PreflightTests(unittest.TestCase):
    def test_git_blob_format(self):
        self.assertEqual(git_blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_six_pairs_twelve_files(self):
        self.assertEqual(len(SOURCE_PAIRS), 6)
        self.assertEqual(len(set(sum(([a,b] for a,b in SOURCE_PAIRS), []))), 12)

    def test_missing_subject_preheader(self):
        result = analyze_text(1, "original", "[[POSTAL]] unsubscribe postal")
        self.assertIn("MISSING_SUBJECT_OR_PREHEADER", result["review_required"])

    def test_commercial_disclosure_gate(self):
        result = analyze_text(3, "original", EDITORIAL)
        self.assertIn("MISSING_COMMERCIAL_DISCLOSURE", result["review_required"])
        self.assertIn("NAMED_AFFILIATE_EMAIL_PERMISSION_MISSING", result["review_required"])

    def test_editorial_does_not_inherit_commercial_blockers(self):
        result = analyze_text(2, "alternate", EDITORIAL)
        self.assertNotIn("NAMED_AFFILIATE_EMAIL_PERMISSION_MISSING", result["review_required"])
        self.assertEqual(result["release"], "HOLD_UNSENT")

    def test_buyer_guide_is_not_authorized_by_disclosure_alone(self):
        result = analyze_text(5, "original", COMMERCIAL)
        self.assertIn("LIVE_APPROVED_GUIDE_AND_EARNING_URL_MISSING", result["review_required"])

    def test_catches_r440_reviewers_footnotes(self):
        result = analyze_text(5, "alternate", COMMERCIAL + "\nSUBSCRIBER-FACING CANDIDATE COPY ENDS\nReviewer internal")
        self.assertIn("REVIEWER_NOTES_OUTSIDE_EMAIL_BODY_MUST_BE_EXCLUDED", result["review_required"])

    def test_source_drift(self):
        result = analyze_text(1, "original", EDITORIAL, "0000")
        self.assertIn("SOURCE_CHANGED_REVIEW_REQUIRED", result["review_required"])

    def test_correct_source_pin(self):
        sha = git_blob_sha(EDITORIAL.encode("utf-8"))
        self.assertNotIn("SOURCE_CHANGED_REVIEW_REQUIRED", analyze_text(1, "original", EDITORIAL, sha)["review_required"])

    def test_missing_legal_proof(self):
        result = analyze_text(2, "original", SUBJECT)
        self.assertIn("LEGAL_WITNESS_NOT_EXPLICIT", result["review_required"])

    def test_static_scan_does_not_send(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            for original, alternate in SOURCE_PAIRS:
                for p in (original, alternate):
                    f = root / p
                    f.parent.mkdir(parents=True, exist_ok=True)
                    f.write_text(COMMERCIAL if "03-" in p or "05-" in p or "ISSUE03_" in p or "ISSUE_05_" in p else EDITORIAL, encoding="utf-8")
            result = scan(root)
            self.assertEqual(result["source_files_found"], 12)
            self.assertFalse(result["send_authorized"])
            self.assertEqual(result["release"], "HOLD_UNSENT")

    def test_missing_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            result = scan(pathlib.Path(folder))
            self.assertEqual(result["source_files_found"], 0)
            self.assertEqual(len(result["source_files_missing"]), 12)
            self.assertFalse(result["send_authorized"])

    def test_source_links_are_not_paid_sales(self):
        result = analyze_text(3, "alternate", COMMERCIAL + " https://zen12.com/secret/ https://finalvestige.com/focus/")
        self.assertEqual(result["url_count"], 2)
        self.assertEqual(result["external_url_count"], 1)
        self.assertEqual(result["release"], "HOLD_UNSENT")


if __name__ == "__main__":
    unittest.main()
