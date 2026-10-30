"""Fail-closed static review for unpublished Hypnosis Live landing-page source."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HypnosisLiveReviewGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (ROOT / "page-hypnosis-live-guide.blocks.html").read_text(encoding="utf-8")
        cls.article = (ROOT / "article-suggestion-without-magic.md").read_text(encoding="utf-8")
        cls.matrix = json.loads((ROOT / "claim-matrix.json").read_text(encoding="utf-8"))
        cls.message = (ROOT / "offer-message-map.md").read_text(encoding="utf-8")
        cls.release = (ROOT / "attribution-and-release.md").read_text(encoding="utf-8")
        cls.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_wordpress_custom_html_and_one_h1(self):
        self.assertIn("<!-- wp:html -->", self.page)
        self.assertIn("<!-- /wp:html -->", self.page)
        self.assertEqual(len(re.findall(r"<h1\\b", self.page)), 1)
        self.assertIn('aria-labelledby="fvhl-title"', self.page)

    def test_no_live_affiliate_destination(self):
        self.assertIsNone(self.matrix["affiliate_url"])
        self.assertNotIn('href="https://hypnosislive.com/mental-skills/total-focus"', self.page)
        self.assertNotIn('href="https://affiliates.inspire3.com/', self.page)
        self.assertEqual(self.page.count('data-fv-offer-state="unverified"'), 2)

    def test_two_near_slot_disclosures(self):
        self.assertEqual(self.page.count('class="fvhl__disclosure"'), 2)
        self.assertEqual(self.page.count("Commercial disclosure:"), 2)
        slots = re.findall(r'<aside class="fvhl__commerce"[\\s\\S]*?</aside>', self.page)
        self.assertEqual(len(slots), 2)
        for slot in slots:
            self.assertIn('data-fv-offer-state="unverified"', slot)
            self.assertIn("may receive a commission", slot)
            self.assertIn("Commercial disclosure:", slot)

    def test_no_js_autoplay_signup_or_forced_popup(self):
        for token in ("<script", "autoplay", "data-email", "onsubmit=", "onload="):
            self.assertNotIn(token, self.page.lower())
        self.assertIn("No newsletter subscription", self.page)

    def test_reduced_motion_mobile_keyboard(self):
        for token in ("prefers-reduced-motion:reduce", "@media(max-width:900px)",
                      "@media(max-width:640px)", ":focus-visible", "min-height:48px"):
            self.assertIn(token, self.page)

    def test_existing_internal_routes_no_dead_mind_link(self):
        for route in ("/focus/", "/free-resources/puysegurs-animal-magnetism-files/",
                      "/editorial-standards/", "/affiliate-disclosure/"):
            self.assertIn('href="' + route + '"', self.page)
        self.assertNotIn('href="/mind/', self.page)

    def test_page_has_real_content_and_product_specificity(self):
        clean = re.sub(r"<style>[\\s\\S]*?</style>", "", self.page)
        clean = re.sub(r"<[^>]+>", " ", clean)
        self.assertGreater(len(clean.split()), 1150)
        for t in ("Total Focus", "33-minute", "47 MB", "fourteen-day",
                  "five refunded sessions", "2026"):
            self.assertIn(t, clean)

    def test_merchant_links_account_hold(self):
        for k in ("affiliate_approval_verified", "merchant_email_permission_verified",
                  "tracking_terms_verified", "commercial_tracking_active",
                  "product_audio_personally_tested", "product_specific_efficacy_verified",
                  "price_verified_at_link_destination"):
            self.assertIs(self.matrix[k], False, k)
        self.assertIn('data-fv-release-state="draft-unpublished"', self.page)

    def test_22_claims_unique_and_source_bounded(self):
        claims = self.matrix["claims"]
        self.assertEqual(self.matrix["claim_count"], 22)
        self.assertEqual(len(claims), 22)
        self.assertEqual(len({x["id"] for x in claims}), 22)
        self.assertTrue(all(x["source"].startswith("https://") for x in claims))

    def test_bad_claims_can_never_have_approved_copy(self):
        blocked = ("unsubstantiated_", "invalid_", "volatile_price_", "not_verified_")
        for claim in self.matrix["claims"]:
            if claim["status"].startswith(blocked):
                self.assertIsNone(claim["fv_copy"], claim["id"])

    def test_independent_evidence_not_product_trial(self):
        for u in ("https://www.nccih.nih.gov/health/hypnosis",
                  "https://pubmed.ncbi.nlm.nih.gov/37399315/",
                  "https://pubmed.ncbi.nlm.nih.gov/41595048/"):
            self.assertIn(u, self.matrix["source_urls"].values())
        self.assertIn("not product-specific", self.article.lower())

    def test_original_history_and_live_archive(self):
        self.assertGreater(len(self.article.split()), 1600)
        self.assertIn("https://doi.org/10.1002/jhbs.21974", self.article)
        self.assertIn("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/", self.article)
        self.assertIn("consent", self.article.lower())

    def test_privacy_event_contract_whitelist(self):
        self.assertIn("source_bucket", self.release)
        self.assertIn("No", self.release)
        for t in ("mind_guide_view", "mind_offer_click", "IP", "raw referrer URLs"):
            self.assertIn(t, self.release)
        self.assertNotIn("<script", self.page)

    def test_editorial_and_commercial_responsibilities_separated(self):
        self.assertNotIn("affiliate commission", self.article.lower())
        self.assertIn("The Dispatch", self.message)
        self.assertIn("founder approval", self.release.lower())
        self.assertIn("No WordPress", self.readme)

if __name__ == "__main__":
    unittest.main()
