"""R34 accessible static reviewer-board invariants; no browser/client claims."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "r34-live-cta-evidence" / "STATIC_REVIEW.html"
EVIDENCE = ROOT / "r34-live-cta-evidence" / "LIVE_ROUTE_EVIDENCE.json"
MANIFEST = ROOT / "manifest.json"

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.hrefs = []
        self.attrs = {}
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        fields = dict(attrs)
        if tag == "a":
            self.hrefs.append(fields.get("href"))
        self.attrs.setdefault(tag, []).append(fields)

class StaticReviewBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = BOARD.read_text(encoding="utf-8")
        cls.data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.parser = Inspect()
        cls.parser.feed(cls.html)

    def test_has_single_clear_main(self):
        self.assertEqual(self.parser.tags.count("main"), 1)

    def test_html_declares_language(self):
        self.assertEqual(self.parser.attrs["html"][0]["lang"], "en")

    def test_one_visible_h1(self):
        self.assertEqual(self.parser.tags.count("h1"), 1)

    def test_six_review_cards(self):
        self.assertEqual(self.parser.tags.count("article"), 6)

    def test_viewport_present(self):
        self.assertIn('name="viewport"', self.html)

    def test_keyboard_focus_visible_rule(self):
        self.assertIn(":focus-visible", self.html)

    def test_mobile_single_column_layout(self):
        self.assertRegex(self.html, r"@media\s*\(max-width:720px\)")
        self.assertIn("grid-template-columns:1fr", self.html)

    def test_status_alert_uses_semantics(self):
        self.assertIn('role="status"', self.html)
        self.assertIn("HOLD_UNSENT", self.html)
        self.assertIn("HOLD_MERCHANT", self.html)

    def test_no_javascript_or_remote_asset(self):
        self.assertNotIn("<script", self.html.lower())
        self.assertNotIn("<iframe", self.html.lower())
        self.assertNotIn("<img", self.html.lower())

    def test_only_four_first_party_editorial_destination_links(self):
        expected = {r["url"] for r in self.data["routes"] if r["kind"] == "editorial"}
        actual = {href for href in self.parser.hrefs if href and href.startswith("https://finalvestige.com/")}
        self.assertEqual(actual, expected)

    def test_commercial_links_not_fabricated(self):
        self.assertNotIn("zen12.com/", self.html)
        self.assertNotIn("hypnosislive.com/", self.html)
        self.assertNotIn("affiliates.inspire3.com", self.html)

    def test_static_board_denies_actual_inbox_proof(self):
        self.assertIn("not a delivered email", self.html)
        self.assertIn("none verified", self.html.lower())

    def test_all_evidence_editorial_urls_match_manifest(self):
        links = {issue["editorial_cta"] for issue in self.manifest["issues"] if issue["kind"] == "editorial"}
        self.assertEqual({r["url"] for r in self.data["routes"] if r["kind"] == "editorial"}, links)

if __name__ == "__main__":
    unittest.main()
