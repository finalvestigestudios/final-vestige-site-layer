"""Offline safety checks for the proposed unpublished Mind & Perception hub."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MindHubSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "page-mind-hub.blocks.html").read_text(encoding="utf-8")
        cls.catalog = json.loads((ROOT / "affiliate-offers.json").read_text(encoding="utf-8"))

    def test_single_accessible_primary_heading(self):
        self.assertEqual(len(re.findall(r"<h1\\b", self.html)), 1)
        self.assertIn('id="fv-mind-title"', self.html)
        self.assertIn('aria-labelledby="fv-mind-title"', self.html)

    def test_real_existing_conversation_paths(self):
        self.assertIn('href="/focus/"', self.html)
        self.assertIn('href="/free-resources/puysegurs-animal-magnetism-files/"', self.html)
        self.assertIn('href="/editorial-standards/"', self.html)
        self.assertIn('href="/affiliate-disclosure/"', self.html)

    def test_no_affiliate_links_before_approval(self):
        self.assertTrue(self.catalog["entries"])
        self.assertTrue(all(e["affiliate_url"] is None for e in self.catalog["entries"]))
        self.assertFalse(re.search(r'href="https?://', self.html), "No unapproved external merchant URLs")
        self.assertNotIn("Buy now", self.html)

    def test_no_seller_claims_as_site_guarantees(self):
        for forbidden in ("guaranteed wealth", "cures anxiety", "scientifically proven to reprogram",
                          "results guaranteed", "instant transformation"):
            self.assertNotIn(forbidden, self.html.lower())

    def test_no_duplicate_offer_identity(self):
        ids = [entry["id"] for entry in self.catalog["entries"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_reduced_motion_and_focus_support(self):
        self.assertIn("prefers-reduced-motion:reduce", self.html)
        self.assertIn(":focus-visible", self.html)
        self.assertIn("@media(max-width:520px)", self.html)


if __name__ == "__main__":
    unittest.main()
