"""Static no-send checks for the six faithful source-derived R309 email review artifacts.
Run: python -I -m unittest discover -s dispatch/r309/tests -v
This is NOT native Jetpack, inbox, unsubscribe or authorization validation.
"""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest
ROOT = Path(__file__).resolve().parents[1]
LEDGER = json.loads((ROOT / "provenance.json").read_text(encoding="utf8"))

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.links, self.attrs = [], [], []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append((tag, dict(attrs)))
        if tag == "a":
            self.links.append(dict(attrs).get("href", ""))

class R309Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.issues = LEDGER["issues"]

    def test_six_issue_pairs(self):
        self.assertEqual(len(self.issues), 6)
        self.assertEqual(len(list((ROOT / "html").glob("*.html"))), 6)
        self.assertEqual(len(list((ROOT / "text").glob("*.txt"))), 6)

    def test_original_mix_and_no_release(self):
        self.assertEqual([i["kind"] for i in self.issues].count("editorial"), 4)
        self.assertEqual([i["kind"] for i in self.issues].count("commercial-review-pending"), 2)
        self.assertEqual(LEDGER["status"], "HOLD_UNSENT")
        self.assertFalse(LEDGER["partner_authorization_verified"])

    def test_subject_and_preheader_exact_in_both(self):
        for i in self.issues:
            html = (ROOT / i["html"]).read_text(encoding="utf8")
            txt = (ROOT / i["plaintext"]).read_text(encoding="utf8")
            self.assertIn(i["subject"].replace("&","&amp;"), html)
            self.assertIn(i["preheader"].replace("&","&amp;"), html)
            self.assertIn("SUBJECT: " + i["subject"], txt)
            self.assertIn(i["preheader"], txt)

    def test_mandatory_holds_preserved(self):
        for i in self.issues:
            for key in ("html", "plaintext"):
                s = (ROOT / i[key]).read_text(encoding="utf8")
                self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", s)
                self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", s)
                self.assertIn("UNSENT", s)

    def test_safe_html_and_first_party_links_only(self):
        for i in self.issues:
            html = (ROOT / i["html"]).read_text(encoding="utf8")
            p = Tags(); p.feed(html)
            for forbidden in ("script", "img", "form", "iframe", "video", "audio"):
                self.assertNotIn(forbidden, p.tags, (i["number"],forbidden))
            self.assertIn("table", p.tags)
            self.assertIn("h1", p.tags)
            self.assertIn(("html", {"lang": "en"}), p.attrs)
            for u in p.links:
                self.assertTrue(u.startswith("https://finalvestige.com/"), u)
            self.assertNotIn("utm_", html)

    def test_commercial_placeholders_not_links(self):
        for i in self.issues:
            if i["kind"] == "commercial-review-pending":
                html=(ROOT / i["html"]).read_text(encoding="utf8")
                txt=(ROOT / i["plaintext"]).read_text(encoding="utf8")
                self.assertIn("Commercial disclosure:", html)
                self.assertIn("Commercial disclosure:", txt)
                self.assertIn("[[APPROVED_", html)
                self.assertIn("[[APPROVED_", txt)
                self.assertNotIn("affiliates.inspire3.com", html)

    def test_truthful_known_subject_holds(self):
        self.assertEqual(self.issues[3]["subject"], "Fourteen seconds. A much longer explanation.")
        self.assertEqual(self.issues[3]["review_status"], "HOLD_UNSENT")

if __name__=="__main__":
    unittest.main()
