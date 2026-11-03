"""R83 release-desk checks: no send authorization, source drift, or invented audience."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / "r83-release-clearance"
DATA = json.loads((ROOT / "evidence.json").read_text(encoding="utf-8"))
HTML = (ROOT / "REVIEW.html").read_text(encoding="utf-8")
TXT = (ROOT / "REVIEW.txt").read_text(encoding="utf-8")
BRIEF = (ROOT / "RELEASE-BRIEF.md").read_text(encoding="utf-8")
VENDOR = (ROOT / "MERCHANT-REVIEW.md").read_text(encoding="utf-8")

class R83ReleaseDesk(unittest.TestCase):
    def test_review_only(self):
        self.assertTrue(DATA["review_only"])
        self.assertEqual(DATA["release_decision"], "HOLD_UNSENT")
    def test_authoritative_source_chain(self):
        self.assertEqual(DATA["source_control"]["master_pr"], 175)
        self.assertEqual(DATA["source_control"]["first_gate_pr"], 201)
        self.assertEqual(DATA["source_control"]["previous_pr"], 732)
        self.assertEqual(len(DATA["source_control"]["original_master_sha"]), 40)
    def test_six_four_two(self):
        self.assertEqual([x["id"] for x in DATA["issues"]], ["01","02","03","04","05","06"])
        self.assertEqual(sum(x["kind"] == "editorial" for x in DATA["issues"]), 4)
        self.assertEqual(sum(x["kind"] == "commercial_reserved" for x in DATA["issues"]), 2)
    def test_all_held(self):
        self.assertTrue(all(x["release"].startswith("HOLD_UNSENT") for x in DATA["issues"]))
    def test_commercial_independent_hold(self):
        for x in DATA["issues"]:
            if x["kind"] == "commercial_reserved":
                self.assertEqual(x["release"], "HOLD_UNSENT_HOLD_MERCHANT")
                self.assertIsNone(x["primary_cta"])
                self.assertIsNone(x["affiliate_link"])
                self.assertFalse(x["merchant_authorized_email"])
                self.assertFalse(x["buyer_guide_live"])
    def test_editorial_cta_is_first_party_https(self):
        for x in DATA["issues"]:
            if x["kind"] == "editorial":
                self.assertTrue(x["primary_cta"].startswith("https://finalvestige.com/"))
    def test_no_unsafe_numerical_subject(self):
        self.assertFalse(any("Fourteen seconds" in x["recommended_subject"] for x in DATA["issues"]))
    def test_source_links(self):
        for x in DATA["issues"]:
            self.assertTrue(x["source"].startswith("https://"))
    def test_no_attribution_fabrication(self):
        self.assertEqual(DATA["rules"]["unobserved_metrics"], "UNOBSERVED")
        self.assertTrue(DATA["rules"]["no_synthetic_performance"])
    def test_site_email_default_safe(self):
        v = DATA["verified_wordpress"]
        self.assertTrue(v["newsletter_on"])
        self.assertFalse(v["automatic_new_post_email"])
        self.assertEqual(v["format"], "excerpt")
        self.assertEqual(v["reply_to"], "no-reply")
        self.assertEqual(v["email_eligible_count"], "UNKNOWN")
    def test_nonautadditive_counts(self):
        v = DATA["verified_wordpress"]
        self.assertEqual(v["newsletter_counts"], {"total":2,"confirmed":2,"unconfirmed":2,"suppressed":0})
        self.assertEqual(v["follower_counts"], {"total":2,"email":0,"wpcom":2,"partial":False})
        self.assertIn("Do not combine metrics", HTML)
    def test_all_five_non_sends(self):
        v = DATA["verified_wordpress"]
        self.assertEqual([x["id"] for x in v["recent_posts"]], [1926,1924,1922,1920,1917])
        self.assertTrue(all(x["status"] == "never_sent_opted_out" for x in v["recent_posts"]))
    def test_welcome_unverified(self):
        v = DATA["verified_wordpress"]
        self.assertTrue(v["welcome_fieldbook_52_pages_configured"])
        self.assertFalse(v["welcome_received_verified"])
    def test_signup_mismatch_visible(self):
        v = DATA["verified_wordpress"]
        self.assertFalse(v["dispatch_mentions_potential_affiliate"])
        self.assertTrue(v["focus_mentions_potential_affiliate"])
        self.assertIn("different expectations", HTML)
    def test_release_attestations_all_false(self):
        self.assertTrue(all(x is False for x in DATA["release_attestations"].values()))
    def test_merchant_attestations_all_false(self):
        for merchant in DATA["merchant_review"].values():
            self.assertTrue(all(merchant[k] is False for k in (
                "independent_named_product_efficacy_verified",
                "merchant_account_accepted_verified",
                "named_product_email_promotional_rights_verified",
                "affiliate_link_format_verified",
                "authorized_creatives_verified",
                "price_checkout_refund_verified",
                "current_buyer_guide_published")))
    def test_no_sending_or_import(self):
        for k in ("no_send_or_test_email","no_post_or_site_changes","no_subscriber_import_or_export",
                  "no_merchant_contact","no_offer_urls","home_page_pr49_untouched"):
            self.assertTrue(DATA["rules"][k])
    def test_public_pages_and_source_links(self):
        for s in ("https://zen12.com/hnp","https://hypnosislive.com/mental-skills/total-focus",
                  "https://inspire3.com/privacy/","https://www.ftc.gov/","https://wordpress.com/support/newsletter/"):
            self.assertTrue(s in BRIEF + VENDOR + HTML)
    def test_static_html_accessible(self):
        for s in ('lang="en"', '<meta name="viewport"', '<main>', '<h1>',
                  '<caption>', 'scope="col"', 'scope="row"', 'aria-label=', ':focus-visible'):
            self.assertIn(s, HTML)
        for s in ('<script','<form','<iframe','mailto:', 'https://affiliates.inspire3.com/'):
            self.assertNotIn(s, HTML)
    def test_no_false_transport_preview(self):
        self.assertIn("NOT a native email preview", HTML)
        self.assertIn("REVIEW ONLY", TXT)
        self.assertIn("HOLD_UNSENT", TXT)
    def test_no_recipient_or_affiliate_secret_in_review(self):
        self.assertNotIn("unsubscribe?", HTML + TXT + BRIEF)
        self.assertNotIn("ref=", HTML + TXT + BRIEF)
        self.assertNotRegex(HTML + TXT, r"(?i)[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}")
    def test_named_merchant_email_permissions_explicit(self):
        self.assertIn("Zen12 email", VENDOR)
        self.assertIn("Total Focus email", VENDOR)
        self.assertIn("NOT SENT", VENDOR)
    def test_no_fixed_current_price_in_copy(self):
        self.assertNotRegex(HTML + TXT, r"\$\d{2}(?:\.\d\d)?")
    def test_no_sending_approval_implied(self):
        self.assertIn("founder_final_campaign_send_approval", json.dumps(DATA))
        self.assertFalse(DATA["release_attestations"]["founder_final_campaign_send_approval"])

if __name__ == "__main__":
    unittest.main()
