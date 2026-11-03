"""R99: no second signup, no send, one first-party PDF CTA, truthful review footer.
Tests intentionally assess committed static assets. They do not grant legal compliance
or infer actual email delivery, subscriber eligibility or commercial permission.
"""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "r99-direct-fieldbook"
PDF = (
    "https://finalvestige.com/wp-content/uploads/2026/10/"
    "Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf"
)
POSTAL = "[[VALID_POSTAL_ADDRESS_REQUIRED]]"
UNSUB = "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"
SUBJECT = "What the first seven days can actually tell you"

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = []
        self.images = []
        self.scripts = []
        self.headings = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            self.anchors.append(attrs.get("href"))
        if tag == "img":
            self.images.append(attrs)
        if tag == "script":
            self.scripts.append(attrs)
        if tag == "h1":
            self.headings.append(tag)

class DirectFieldbookReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.markdown = (PKG / "06-no-repeat-signup-candidate.md").read_text(encoding="utf-8")
        cls.plaintext = (PKG / "06-no-repeat-signup-candidate.txt").read_text(encoding="utf-8")
        cls.html = (PKG / "06-no-repeat-signup-review.html").read_text(encoding="utf-8")
        cls.memo = (PKG / "R99-DECISION-AND-OFFER-SURFACE.md").read_text(encoding="utf-8")
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.parsed = Anchors()
        cls.parsed.feed(cls.html)

    def test_assets_present_and_nonempty(self):
        self.assertTrue(all(len(x) > 1200 for x in
            [self.markdown, self.plaintext, self.html, self.memo]))

    def test_original_six_issue_allocation_preserved(self):
        issues = self.manifest["issues"]
        self.assertEqual(len(issues), 6)
        self.assertEqual(sum(i["kind"] == "editorial" for i in issues), 4)
        self.assertEqual(sum(i["kind"] == "commercial-review-pending" for i in issues), 2)

    def test_original_campaign_not_preapproved(self):
        self.assertEqual(self.manifest["status"], "DRAFT_UNSENT_NO_SCHEDULING")
        self.assertTrue(all(i["publish_state"] == "hold" for i in self.manifest["issues"]))

    def test_original_issue_six_unchanged(self):
        self.assertEqual(self.manifest["issues"][5]["editorial_cta"], "https://finalvestige.com/focus/")
        original = (ROOT / "issues" / "06-the-evidence-log.md").read_text(encoding="utf-8")
        self.assertIn("What did seven days of attention reveal?", original)

    def test_candidate_subject_and_preheader_present(self):
        self.assertIn(SUBJECT, self.markdown)
        self.assertIn(SUBJECT, self.plaintext)
        self.assertIn(SUBJECT, self.html)
        self.assertIn("Preheader candidate:", self.markdown)
        self.assertIn("NOT NATIVE-JETPACK VERIFIED", self.plaintext)

    def test_subject_honesty_and_length(self):
        self.assertGreaterEqual(len(SUBJECT), 28)
        self.assertLessEqual(len(SUBJECT), 65)
        self.assertNotIn("guaranteed", SUBJECT.lower())
        self.assertNotIn("free money", SUBJECT.lower())

    def test_single_clickable_cta_in_static_email(self):
        self.assertEqual(self.parsed.anchors, [PDF])

    def test_cta_is_first_party_exact_pdf_without_tracking(self):
        url = urlsplit(self.parsed.anchors[0])
        self.assertEqual(url.scheme, "https")
        self.assertEqual(url.hostname, "finalvestige.com")
        self.assertTrue(url.path.endswith("Fieldbook_Complete_Edition.pdf"))
        self.assertEqual(url.query, "")
        self.assertEqual(url.fragment, "")

    def test_pdf_appears_in_both_text_variants(self):
        for body in [self.markdown, self.plaintext]:
            self.assertIn(PDF, body)

    def test_pdf_asset_identified_from_authenticated_wp(self):
        self.assertIn("1737", self.memo)
        self.assertIn("599,946", self.memo)
        self.assertIn(PDF, self.memo)

    def test_no_new_subscription_or_vendor_route(self):
        for body in [self.markdown, self.plaintext, self.html]:
            lower = body.lower()
            self.assertNotIn("subscribe now", lower)
            self.assertNotIn("sign up to download", lower)
            self.assertNotIn("affiliates.inspire3.com", lower)
            self.assertNotIn("zen12.com", lower)
            self.assertNotIn("hypnosislive.com", lower)

    def test_five_field_exercise(self):
        for phrase in ["Started", "Time", "Interruption", "Conditions", "adjustment"]:
            self.assertIn(phrase.lower(), self.markdown.lower())
            self.assertIn(phrase.lower(), self.html.lower())

    def test_not_claiming_clinical_effect(self):
        for body in [self.markdown, self.plaintext, self.html]:
            lower = body.lower()
            self.assertNotIn("clinically proven", lower)
            self.assertNotIn("brainwaves will", lower)
            self.assertNotIn("guaranteed results", lower)
            self.assertIn("not a clinical", lower)

    def test_all_formats_still_unsent(self):
        for body in [self.markdown, self.plaintext, self.html]:
            self.assertIn("UNSENT", body)

    def test_all_formats_have_unresolved_legal_footer(self):
        for body in [self.markdown, self.plaintext, self.html]:
            self.assertIn(POSTAL, body)
            self.assertIn(UNSUB, body)

    def test_preview_accessibility_baseline(self):
        html = self.html.lower()
        self.assertIn('lang="en"', html)
        self.assertIn('name="viewport"', html)
        self.assertIn('role="presentation"', html)
        self.assertGreaterEqual(html.count("<h1"), 1)
        self.assertGreaterEqual(html.count("<h2"), 1)

    def test_no_remote_media_or_script(self):
        self.assertEqual(self.parsed.images, [])
        self.assertEqual(self.parsed.scripts, [])

    def test_preview_does_not_claim_real_jetpack_mime(self):
        self.assertIn("not a Jetpack received-message preview", self.html)
        self.assertIn("Native Jetpack preheader handling is unverified", self.html)

    def test_memo_marks_all_external_approvals_unverified(self):
        for phrase in ["HOLD_UNSENT", "HOLD_MERCHANT", "UNKNOWN",
                       "NOT VERIFIED", "aggregate-only"]:
            self.assertIn(phrase, self.memo)

    def test_commercial_merchant_pages_quoted_as_sources_only(self):
        self.assertIn("https://zen12.com/getstarted", self.memo)
        self.assertIn("https://hypnosislive.com/mental-skills/total-focus", self.memo)
        self.assertIn("https://inspire3.com/privacy/", self.memo)
        self.assertIn("facts vs vendor assertions", self.memo)

    def test_separate_founder_approval_obligation(self):
        self.assertIn("founder's explicit final decision", self.markdown)
        self.assertIn("founder approval", self.memo.lower())

    def test_no_hidden_send_action(self):
        for body in [self.html, self.plaintext, self.markdown]:
            self.assertNotIn("send_subscriptions", body)
            self.assertNotIn("wpcom_jetpack_newsletter", body)
            self.assertNotIn("<form", body.lower())

if __name__ == "__main__":
    unittest.main()
