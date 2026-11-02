"""Accessible static reviewer BOARD; never confuse with actual received email."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOC = (ROOT / "r55-primary-purpose/review.html").read_text(encoding="utf-8")
MANIFEST = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.anchor_targets = []
        self.ids = set()
        self.article_count = 0
        self.skip_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "article":
            self.article_count += 1
        if tag == "a":
            self.anchor_targets.append(attrs.get("href", ""))
            if attrs.get("class") == "skip":
                self.skip_count += 1


class OfflineBoard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = Collector()
        cls.parser.feed(DOC)

    def test_01_six_cards(self):
        self.assertEqual(self.parser.article_count, 6)

    def test_02_real_subjects_not_stale(self):
        for entry in MANIFEST["issues"]:
            self.assertIn(entry["subject"].replace("&","&amp;"), DOC)

    def test_03_no_forms_or_tracking_scripts(self):
        self.assertFalse(set(self.parser.tags) & {"script", "form", "iframe", "video"})

    def test_04_no_hypnosis_or_zen12_earning_links(self):
        for href in self.parser.anchor_targets:
            self.assertNotIn("zen12.com", href)
            self.assertNotIn("hypnosislive.com", href)
            self.assertNotIn("inspire3.com", href)

    def test_05_review_proof_sources_are_official(self):
        self.assertIn("ftc.gov/business-guidance/resources/can-spam-act", DOC)
        self.assertIn("ftc.gov/business-guidance/resources/ftcs-endorsement", DOC)

    def test_06_inert_and_noindex(self):
        self.assertIn('content="noindex,nofollow,noarchive"', DOC)
        self.assertIn("not</strong> a Jetpack email preview", DOC)

    def test_07_accessible_skip_and_main(self):
        self.assertEqual(self.parser.skip_count, 1)
        self.assertIn("#main", self.parser.anchor_targets)
        self.assertIn("main", self.parser.ids)

    def test_08_scope_and_separation(self):
        self.assertIn("HOLD_UNSENT", DOC)
        self.assertIn("HOLD_MERCHANT", DOC)
        self.assertIn("Four editorial editions", DOC)

    def test_09_mobile_and_reduced_motion_css(self):
        self.assertIn("@media(max-width:760px)", DOC)
        self.assertIn("prefers-reduced-motion", DOC)

    def test_10_no_client_side_exfiltration(self):
        for term in ("fetch(", "XMLHttpRequest", "navigator.sendBeacon",
                     "googletagmanager", "pixel.gif", "<input", "mailto:"):
            self.assertNotIn(term, DOC)

    def test_11_postal_is_hold_not_invented(self):
        self.assertIn("legitimate Final Vestige physical postal address", DOC)
        self.assertIn("received", DOC)

    def test_12_audience_count_does_not_fake_four_people(self):
        self.assertIn("total 2, confirmed 2, unconfirmed 2", DOC)
        self.assertNotIn("four unique subscribers", DOC)


if __name__ == "__main__":
    unittest.main()
