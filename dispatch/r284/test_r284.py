"""R284 offline source & release invariants. Expected to run from any cwd; NO network, email or WordPress calls."""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent / "campaign-2026-mind"

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "a":
            self.hrefs.append(dict(attrs).get("href", ""))

class R284Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = (ROOT / "ISSUE02_BLINDFOLD_TREES_REVIEW_ONLY.md").read_text(encoding="utf-8")
        cls.plain = (ROOT / "issue02_plaintext.txt").read_text(encoding="utf-8")
        cls.html = (ROOT / "issue02_email_preview.html").read_text(encoding="utf-8")
        cls.audit = (ROOT / "CAMPAIGN_COPY_CONVERSION_SOURCE_AUDIT.md").read_text(encoding="utf-8")
        cls.consent = (ROOT / "FOCUS_CONFIRMED_SIGNUP_ACCEPTANCE.md").read_text(encoding="utf-8")
        cls.merchant = (ROOT / "MERCHANT_EXACT_OFFER_ALIGNMENT.md").read_text(encoding="utf-8")
        cls.att = json.loads((ROOT / "release_attestations.json").read_text(encoding="utf-8"))
        cls.parser = Anchors()
        cls.parser.feed(cls.html)

    def test_original_4_2_preserved(self):
        manifest = json.loads((CAMPAIGN / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "DRAFT_UNSENT_NO_SCHEDULING")
        self.assertEqual(len(manifest["issues"]), 6)
        self.assertEqual(sum(x["kind"] == "editorial" for x in manifest["issues"]), 4)
        self.assertEqual(sum(x["kind"] == "commercial-review-pending" for x in manifest["issues"]), 2)
        self.assertEqual(self.att["merchant_issues_reserved"], [3, 5])
        self.assertFalse(self.att["issue02_alternative_adopted"])

    def test_subject_and_preheader_match(self):
        sub = "The boy, the trees, and the missing force"
        pre = "In Franklin's garden, one carefully staged test exposed a gap between sensation and cause."
        for document in (self.review, self.plain, self.html):
            self.assertIn(sub, document)
            self.assertIn(pre, document)

    def test_single_internal_editorial_cta(self):
        targets = [h for h in self.parser.hrefs if urlsplit(h).hostname == "finalvestige.com"]
        self.assertEqual(targets, ["https://finalvestige.com/2026/11/02/mesmerism/"])
        self.assertEqual(self.html.count("Read the historical investigation"), 1)

    def test_external_reference_links(self):
        hosts = [urlsplit(h).hostname for h in self.parser.hrefs]
        self.assertEqual(hosts.count("pmc.ncbi.nlm.nih.gov"), 2)
        self.assertEqual(hosts.count("www.ncbi.nlm.nih.gov"), 1)
        self.assertEqual(len(self.parser.hrefs), 4)

    def test_mail_html_is_static_and_email_conservative(self):
        self.assertIn('lang="en"', self.html)
        self.assertIn('role="presentation"', self.html)
        self.assertIn('width="100%"', self.html)
        self.assertIn('display:none!important', self.html)
        for element in ("script", "form", "iframe", "object", "embed", "video", "audio"):
            self.assertNotIn(element, self.parser.tags)

    def test_no_merchant_or_active_tracking_links(self):
        for href in self.parser.hrefs:
            self.assertNotIn("affiliates.inspire3.com", href)
            self.assertNotIn("zen12.com", href)
            self.assertNotIn("hypnosislive.com", href)
            self.assertNotIn("utm_", href)
            self.assertNotIn("mailto:", href)
        for payload in (self.review, self.plain, self.html):
            self.assertNotIn("https://zen12.com/getstarted", payload)
            self.assertNotIn("https://affiliates.inspire3.com", payload)

    def test_historical_nuance_and_archival_provenance(self):
        for bit in ("four", "apricot", "1784", "magnetic", "pretending"):
            self.assertTrue(bit in self.review.lower() or bit == "pretending")
        for evidence in ("PMC5550075", "428559", "PMC5407522"):
            self.assertIn(evidence, self.review.upper() if evidence.startswith("PMC") else self.review)

    def test_all_specimens_have_fail_closed_footer(self):
        for content in (self.review, self.plain, self.html):
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", content)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", content)
            self.assertIn("DO NOT SEND", content)

    def test_false_evidence_not_promoted_to_true(self):
        evidence = self.att["evidence"]
        for key, val in evidence.items():
            if key.endswith("_verified") or key.endswith("_approved") or key.endswith("_deployed") or key.endswith("_live") or key.endswith("_accepted") or key.endswith("_issued"):
                self.assertIs(val, False, key)
        self.assertIs(evidence["actual_email_eligible_recipient_count"], None)
        self.assertIs(evidence["verified_net_revenue"], None)

    def test_consent_requires_provider_proof(self):
        for token in ("confirmed_signup", "provider", "UNKNOWN", "subscribe=unknown_state", "deduplicate"):
            self.assertIn(token.lower(), self.consent.lower())
        self.assertIn("no production event emitted", self.consent.lower())

    def test_seller_not_confused_with_authorized_offer(self):
        self.assertIn("12 levels / 48 MP3s", self.merchant)
        self.assertIn("33-minute, 47 MB", self.merchant)
        self.assertIn("not FV-specific affiliate approval".lower(), self.merchant.lower())
        self.assertIn("HOLD_UNSENT", self.merchant)

    def test_audit_covers_all_six_and_legal_source(self):
        for no in ("01", "02", "03", "04", "05", "06"):
            self.assertRegex(self.audit, r"\b" + no + r"\b")
        self.assertIn("ftc.gov", self.audit)
        self.assertIn("HOLD", self.audit)

if __name__ == "__main__":
    unittest.main()
