"""Static guards for a deliberately unsent campaign package."""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class CampaignGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.issue_files = sorted((ROOT / "issues").glob("*.md"))

    def test_six_issues_not_scheduled(self):
        self.assertEqual(len(self.issue_files), 6)
        self.assertEqual(self.manifest["status"], "DRAFT_UNSENT_NO_SCHEDULING")
        self.assertEqual(len(self.manifest["issues"]), 6)

    def test_primarily_editorial(self):
        kinds = [i["kind"] for i in self.manifest["issues"]]
        self.assertEqual(kinds.count("editorial"), 4)
        self.assertEqual(kinds.count("commercial-review-pending"), 2)

    def test_links_not_activated(self):
        self.assertTrue(all(i["merchant_affiliate_url"] is None for i in self.manifest["issues"]))
        for entry, file in zip(self.manifest["issues"], self.issue_files):
            body = file.read_text(encoding="utf-8")
            self.assertIn(entry["subject"], body)
            self.assertIn(entry["preheader"], body)
            self.assertIn("UNSENT DRAFT", body)

    def test_commercial_copy_has_disclosure(self):
        for file in self.issue_files:
            body = file.read_text(encoding="utf-8")
            if "commercial-review-pending" in body:
                self.assertIn("Commercial disclosure:", body)
                self.assertIn("APPROVED_", body)
                self.assertIn("pending", body.lower())

    def test_legal_gate_requires_footer_verification(self):
        for file in self.issue_files:
            body = file.read_text(encoding="utf-8")
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", body)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", body)

    def test_no_invented_commercial_promise(self):
        banned = ("guaranteed income", "cures anxiety", "clinically proven to reprogram",
                  "100% guaranteed to work", "buy now before midnight")
        for file in self.issue_files:
            content = file.read_text(encoding="utf-8").lower()
            for phrase in banned:
                self.assertNotIn(phrase, content)

if __name__ == "__main__":
    unittest.main()
