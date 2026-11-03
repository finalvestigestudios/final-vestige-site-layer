"""R98 no-send review checks. Never calls WordPress, email or network."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CAND = ROOT / "r98-first-issue"

class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.scripts = []
        self.lang = None
        self.tables = 0
        self.tables_presentation = 0
        self.headings = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = a.get("lang")
        if tag == "a": self.links.append(a.get("href", ""))
        if tag == "img": self.images.append(a)
        if tag == "script": self.scripts.append(a)
        if tag == "table":
            self.tables += 1
            self.tables_presentation += int(a.get("role") == "presentation")
        if tag == "h1": self.headings += 1

class R98ReviewGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md = (CAND / "01-door-study-candidate.md").read_text(encoding="utf-8")
        cls.txt = (CAND / "01-door-study-candidate.txt").read_text(encoding="utf-8")
        cls.html = (CAND / "01-door-study-candidate.html").read_text(encoding="utf-8")
        cls.audit = (CAND / "R98-CONVERSION-AND-SOURCE-AUDIT.md").read_text(encoding="utf-8")
        cls.consent = (CAND / "R98-CONSENT-AND-FOOTER-DECISION.md").read_text(encoding="utf-8")
        cls.doc = Inspect()
        cls.doc.feed(cls.html)
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

    def test_original_remains_six_unsent_issues(self):
        self.assertEqual(self.manifest["status"], "DRAFT_UNSENT_NO_SCHEDULING")
        self.assertEqual(len(self.manifest["issues"]), 6)

    def test_original_four_to_two_plan_untouched(self):
        kinds = [i["kind"] for i in self.manifest["issues"]]
        self.assertEqual(kinds.count("editorial"), 4)
        self.assertEqual(kinds.count("commercial-review-pending"), 2)

    def test_original_issue_one_has_not_been_overwritten(self):
        self.assertEqual(self.manifest["issues"][0]["subject"], "The mind is not a camera")

    def test_subject_is_honest_and_consistent(self):
        subject = "The stranger changed. The conversation didn't."
        self.assertIn(subject, self.md)
        self.assertIn(subject, self.txt)
        self.assertIn(subject, self.html)

    def test_preheader_is_not_claimed_native(self):
        self.assertIn("NOT a verified Jetpack setting", self.md)
        self.assertIn("not confirmed Jetpack capability", self.txt)

    def test_real_published_primary_destination(self):
        target = "https://finalvestige.com/2026/11/02/change-blindness/"
        self.assertIn(target, self.md)
        self.assertIn(target, self.txt)
        self.assertEqual(self.doc.links.count(target), 1)

    def test_exactly_one_primary_cta_in_email_html(self):
        site_links = [u for u in self.doc.links if u.startswith("https://finalvestige.com/")]
        self.assertEqual(len(site_links), 1)

    def test_primary_sources_identified_in_all_formats(self):
        for source in ("https://doi.org/10.3758/BF03208840",
                       "https://doi.org/10.1111/j.1467-9280.1997.tb00427.x"):
            for body in (self.md, self.txt, self.html):
                self.assertIn(source, body)

    def test_no_population_extrapolation(self):
        for body in (self.md, self.txt, self.html):
            self.assertIn("half", body.lower())
            self.assertNotIn("50% of all people", body.lower())
            self.assertNotIn("proves all memory", body.lower())

    def test_no_merchants_or_checkout(self):
        for body in (self.md, self.txt, self.html):
            for forbidden in ("affiliates.inspire3.com/", "checkout", "utm_", "ref=", "buy now", "limited-time"):
                self.assertNotIn(forbidden, body.lower())

    def test_no_preapproved_release(self):
        for body in (self.md, self.txt, self.html, self.audit, self.consent):
            self.assertTrue(any(x in body.lower() for x in ("hold_unsent", "do not send", "unsent", "not deployed")))

    def test_footer_blockers_present_in_all_preview_formats(self):
        for body in (self.md, self.txt, self.html):
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", body)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", body)

    def test_html_is_static_and_accessible_baseline(self):
        self.assertEqual(self.doc.lang, "en")
        self.assertGreaterEqual(self.doc.headings, 1)
        self.assertEqual(self.doc.scripts, [])
        self.assertEqual(self.doc.images, [])
        self.assertEqual(self.doc.tables, self.doc.tables_presentation)
        self.assertIn('name="viewport"', self.html)
        self.assertIn("role=\"note\"", self.html)

    def test_html_no_form_or_auto_tracking(self):
        for forbidden in ("<form", "pixel", "<iframe", "http-equiv=\"refresh\"", "data-track", "javascript:"):
            self.assertNotIn(forbidden, self.html.lower())

    def test_consent_proposal_is_not_live_change(self):
        for text in ("NOT DEPLOYED", "one", "/dispatch/", "/focus/", "affiliate"):
            self.assertIn(text.lower(), self.consent.lower())
        self.assertIn("do not modify homepage", self.consent.lower())

    def test_subscriber_counts_are_not_asserted_as_recipients(self):
        self.assertIn("UNKNOWN", self.audit)
        self.assertIn("total=2", self.audit)
        self.assertIn("confirmed=2", self.audit)
        self.assertIn("unconfirmed=2", self.audit)

    def test_email_receipt_not_equated_to_configuration(self):
        self.assertIn("configuration is not receipt", self.audit.lower())
        self.assertIn("received jetpack email", self.consent.lower())

    def test_merchant_issues_stay_held(self):
        self.assertIn("HOLD_MERCHANT", self.audit)
        self.assertIn("Written", self.consent) if "Written" in self.consent else self.assertIn("written", self.consent)

if __name__ == "__main__":
    unittest.main()
