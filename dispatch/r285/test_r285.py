"""R285 source-control acceptance checks; no network, sending or WordPress changes."""
from pathlib import Path
from html.parser import HTMLParser
import json
import re
import unittest

ROOT = Path(__file__).resolve().parent
SUBJECT = "Can a 33-minute recording improve focus?"
PREHEADER = "One seller promise, three practical checks, and what the evidence does not show."
HARD_STOPS = ("[[APPROVED_TOTAL_FOCUS_GUIDE_URL_REQUIRED]]",
              "[[VALID_POSTAL_ADDRESS_REQUIRED]]",
              "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]")

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "a":
            self.urls.append(dict(attrs).get("href", ""))

class SourceGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = [(ROOT / file).read_text(encoding="utf8") for file in
                    ("ISSUE05_TOTAL_FOCUS_REVIEW_ONLY.md", "issue05_plaintext.txt", "issue05_email_preview.html")]
        cls.claims = json.loads((ROOT / "merchant_claim_matrix.json").read_text(encoding="utf8"))
        cls.evidence = json.loads((ROOT / "release_evidence.json").read_text(encoding="utf8"))
        cls.plan = (ROOT / "CONVERSION_AND_CONSENT_PLAN.md").read_text(encoding="utf8")
        cls.parser = Links()
        cls.parser.feed(cls.docs[2])

    def test_subject_preheader_same_in_all_formats(self):
        for doc in self.docs:
            self.assertIn(SUBJECT, doc)
            self.assertIn(PREHEADER, doc)

    def test_hard_stop_placeholders_in_all_formats(self):
        for doc in self.docs:
            for stopper in HARD_STOPS:
                self.assertIn(stopper, doc)
            self.assertIn("DO NOT SEND", doc)

    def test_exactly_four_source_links_and_no_buyer_link(self):
        self.assertEqual(len(self.parser.urls), 4)
        self.assertTrue(all(x.startswith("https://") for x in self.parser.urls))
        self.assertTrue(any("nccih.nih.gov" in x for x in self.parser.urls))
        self.assertTrue(any("hypnosislive.com/faq" in x for x in self.parser.urls))

    def test_no_affiliate_tracking_or_personal_tokens(self):
        for url in self.parser.urls:
            for forbidden in ("utm_", "affiliate", "subscriber=", "email=", "ref="):
                self.assertNotIn(forbidden, url.lower())
        self.assertNotIn("href=\"[[APPROVED_", self.docs[2])

    def test_email_safe_html(self):
        for bad_tag in ("script", "form", "iframe", "object", "embed", "video", "audio", "input"):
            self.assertNotIn(bad_tag, self.parser.tags)
        self.assertIn('role="presentation"', self.docs[2])
        self.assertIn('lang="en"', self.docs[2])
        self.assertIn('width="100%"', self.docs[2])

    def test_seller_claims_do_not_become_proven_ones(self):
        m = self.claims
        self.assertFalse(m["affiliate_email_permission_verified"])
        self.assertFalse(m["earning_link_issued"])
        self.assertFalse(m["approved_affiliate_creative_reviewed"])
        self.assertTrue(any(row["class"] == "seller promise only" and not row["reproduce_in_email"] for row in m["claim_rows"]))
        for d in self.docs:
            self.assertNotIn("$17.95", d)
            self.assertNotIn("$22.95", d)
            self.assertNotIn("100% razor-sharp", d)

    def test_merchant_sources_are_specific(self):
        self.assertIn("/mental-skills/total-focus", self.claims["official_seller_sales_url"])
        self.assertIn("/faq", self.claims["official_seller_refund_faq"])
        self.assertIn("nccih.nih.gov", self.claims["independent_research_overview"])

    def test_explicit_founder_hold_and_unverified_eligibility(self):
        e=self.evidence
        self.assertEqual(e["status"], "HOLD_UNSENT")
        self.assertFalse(e["founder_final_send_approval"])
        self.assertFalse(e["email_channel_affiliate_permission_verified"])
        self.assertFalse(e["actual_fv_physical_postal_address_verified"])
        self.assertFalse(e["unsubscribe_in_real_jetpack_email_verified"])
        self.assertIsNone(e["actual_email_eligible_recipients"])
        self.assertIsNone(e["realized_net_revenue"])

    def test_original_four_two_allocation_not_replaced(self):
        self.assertEqual(self.evidence["commercial_issues_reserved"], [3,5])
        self.assertFalse(self.evidence["alternative_adopted"])
        self.assertEqual(self.evidence["original_campaign_pr"], 175)

    def test_conversion_requires_provider_consent_and_paid_settlement(self):
        for phrase in ("confirmed_signup","qualified-human sessions","not additive","paid and settled","NOT COMPUTABLE"):
            self.assertIn(phrase.lower(),self.plan.lower())
        self.assertIn("No duplicate pixels",self.plan)

if __name__=="__main__":
    unittest.main()
