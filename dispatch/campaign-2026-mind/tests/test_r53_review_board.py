"""Static reviewer UI source-integrity checks. Not actual browser/Jetpack email QA."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"r53-release-evidence"
HTML=(PACK/"review.html").read_text(encoding="utf-8")
MANIFEST=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))

class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.tags=[]
        self.attrs=[]
        self.ids=set()
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        self.tags.append(tag)
        self.attrs.append((tag,d))
        if tag=="a":self.links.append(d.get("href",""))
        if "id" in d:self.ids.add(d["id"])

class R53ReviewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui=Inspector()
        cls.ui.feed(HTML)

    def test_01_language_and_responsive_meta(self):
        self.assertIn('<html lang="en">',HTML)
        self.assertIn('name="viewport"',HTML)

    def test_02_one_h1(self):
        self.assertEqual(self.ui.tags.count("h1"),1)

    def test_03_keyboard_skip_target(self):
        self.assertIn("#main",self.ui.links)
        self.assertIn("main",self.ui.ids)

    def test_04_no_scripts_or_forms(self):
        self.assertFalse({"script","form","iframe","img","video","audio"}&set(self.ui.tags))

    def test_05_no_merchant_clickable_destination(self):
        self.assertFalse(any("zen12.com" in x or "hypnosislive.com" in x or "inspire3.com" in x for x in self.ui.links))

    def test_06_no_live_affiliate_tracking(self):
        # Assert on real clickable URLs, not harmless source prose mentioning tracking pixels.
        self.assertFalse(any(re.search(r"(?i)(hop\.clickbank|affiliate_id=|utm_source=)", url)
                             for url in self.ui.links))

    def test_07_all_six_canonical_subjects(self):
        for entry in MANIFEST["issues"]:
            with self.subTest(issue=entry["number"]):
                self.assertIn(entry["subject"],HTML)

    def test_08_merchant_hold_labels(self):
        self.assertIn("HOLD_MERCHANT",HTML)
        self.assertIn("03",HTML)
        self.assertIn("05",HTML)

    def test_09_readonly_private_audience(self):
        self.assertIn("total 2 / confirmed 2 / unconfirmed 2",HTML)
        self.assertIn("Unique consent-eligible audience",HTML)

    def test_10_native_provider_missing(self):
        self.assertIn("not",HTML.lower())
        self.assertIn("RFC 5322",HTML)
        self.assertIn("accidental-send",HTML)

    def test_11_no_false_success_label(self):
        self.assertNotIn("APPROVED_TO_SEND",HTML)
        self.assertNotIn("SEND_READY",HTML)

    def test_12_sources_and_owner_issues(self):
        self.assertIn("pull/175",HTML)
        self.assertIn("issues/174",HTML)
        self.assertIn("issues/171",HTML)

    def test_13_reduced_motion(self):
        self.assertIn("prefers-reduced-motion",HTML)

    def test_14_table_scopes(self):
        self.assertIn('scope="col"',HTML)

    def test_15_no_old_frozen_homepage_modifications(self):
        path=str(PACK).lower()
        self.assertNotIn("/homepage/",path)
        self.assertNotIn("pr-49",path)

    def test_16_legal_not_certified(self):
        self.assertIn("no real email proof",HTML.lower())
        self.assertIn("functioning unsubscribe",HTML.lower())

if __name__=="__main__":
    unittest.main()
