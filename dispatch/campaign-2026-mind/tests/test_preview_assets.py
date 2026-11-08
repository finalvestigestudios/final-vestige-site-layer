"""Tests for source-aligned email preview snapshots. Run with Python stdlib only."""
import html
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PREVIEWS = ROOT / "previews"
ISSUES = ROOT / "issues"

class DispatchPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_six_and_two_review_holds(self):
        self.assertEqual(len(self.manifest["issues"]), 6)
        self.assertEqual(sum(x["kind"] == "commercial-review-pending" for x in self.manifest["issues"]), 2)

    def test_snapshot_presence_and_copy_alignment(self):
        for entry in self.manifest["issues"]:
            name = f"{entry['number']:02d}-{entry['slug']}"
            html_doc = (PREVIEWS / f"{name}.html").read_text(encoding="utf-8")
            txt_doc = (PREVIEWS / f"{name}.txt").read_text(encoding="utf-8")
            md = (ISSUES / f"{name}.md").read_text(encoding="utf-8")
            self.assertIn(html.escape(entry["subject"]), html_doc)
            self.assertIn(entry["subject"], txt_doc)
            self.assertIn(f"**Subject:** {entry['subject']}", md)
            self.assertIn(f"**Preheader:** {entry['preheader']}", md)
            self.assertIn("NOT A SENT EMAIL", html_doc)
            self.assertIn("UNSENT DRAFT", txt_doc)

    def test_all_html_offline_and_not_live_merchant_affiliate(self):
        for file in PREVIEWS.glob("*.html"):
            data = file.read_text(encoding="utf-8")
            self.assertNotRegex(data, r"(?i)<script\b")
            self.assertNotRegex(data, r"(?i)<img\b")
            self.assertNotIn('href="[[APPROVED_', data)
            self.assertNotIn("utm_campaign=", data)
            self.assertNotIn("clickid=", data)

    def test_legal_hold_and_offer_disclosure(self):
        for entry in self.manifest["issues"]:
            name = f"{entry['number']:02d}-{entry['slug']}"
            html_doc = (PREVIEWS / f"{name}.html").read_text(encoding="utf-8")
            txt_doc = (PREVIEWS / f"{name}.txt").read_text(encoding="utf-8")
            self.assertIn("BUSINESS POSTAL ADDRESS REQUIRED", html_doc)
            self.assertIn("UNSUBSCRIBE", html_doc)
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", txt_doc)
            self.assertIsNone(entry["merchant_affiliate_url"])
            if entry["kind"] == "commercial-review-pending":
                self.assertIn("Commercial disclosure:", txt_doc)
                self.assertIn("[[APPROVED_", txt_doc)
                self.assertLess(txt_doc.index("Commercial disclosure:"), txt_doc.index("[[APPROVED_"))

    def test_corrected_historical_facts(self):
        second = (ISSUES / "02-before-hypnosis-had-a-name.md").read_text(encoding="utf-8")
        fourth = (ISSUES / "04-the-hatch-and-the-spark.md").read_text(encoding="utf-8")
        self.assertIn("In 1784", second)
        self.assertNotIn("In 1785", second)
        self.assertIn("Seventeen seconds", fourth)
        self.assertNotIn("Fourteen seconds", fourth)

    def test_index_contains_links_to_all_six_issues(self):
        index = (PREVIEWS / "index.html").read_text(encoding="utf-8")
        for entry in self.manifest["issues"]:
            slug = f"{entry['number']:02d}-{entry['slug']}"
            self.assertIn(f'{slug}.html', index)
            self.assertIn(f'{slug}.txt', index)
        self.assertIn("REVIEW-ONLY", index)

if __name__ == "__main__":
    unittest.main()
