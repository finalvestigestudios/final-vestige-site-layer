"""Unpublished Zen12 guide: content, disclosure and affiliate safety gates."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Zen12DraftGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (ROOT / "page-zen12-guide.blocks.html").read_text(encoding="utf-8")
        cls.m = json.loads((ROOT / "claim-matrix.json").read_text(encoding="utf-8"))
        cls.article = (ROOT / "article-attentional-blink.md").read_text(encoding="utf-8")
        cls.video = (ROOT / "video" / "40-second-film.md").read_text(encoding="utf-8")
        cls.vtt = (ROOT / "video" / "captions.vtt").read_text(encoding="utf-8")

    def test_wordpress_wrapper_and_hierarchy(self):
        self.assertIn("<!-- wp:html -->", self.page)
        self.assertIn("<!-- /wp:html -->", self.page)
        self.assertEqual(len(re.findall(r"<h1\b", self.page)), 1)
        self.assertIn('aria-labelledby="fvz12-title"', self.page)

    def test_no_live_affiliate_link_or_checkout_cta(self):
        self.assertIsNone(self.m["affiliate_url"])
        self.assertFalse(self.m["affiliate_approval_verified"])
        self.assertNotIn("href=\"https://affiliates.inspire3.com", self.page)
        self.assertNotIn("href=\"https://zen12.com/getstarted\" class=\"fvz12__button", self.page)
        self.assertIn('data-fv-offer-state="unverified"', self.page)

    def test_near_link_disclosure_content(self):
        self.assertIn("Commercial disclosure:", self.page)
        self.assertIn("Final Vestige may receive a commission", self.page)
        self.assertIn('data-fv-offer-slot="zen12-primary"', self.page)

    def test_accessibility_and_no_js_dependence(self):
        for token in ('@media(max-width:900px)', '@media(max-width:650px)',
                      'prefers-reduced-motion:reduce', ':focus-visible', '<details', '<summary>'):
            self.assertIn(token, self.page)
        self.assertNotIn("<script", self.page)
        self.assertNotIn("autoplay", self.page)

    def test_five_published_internal_routes(self):
        for route in ('/focus/', '/editorial-standards/', '/affiliate-disclosure/',
                      '/free-resources/puysegurs-animal-magnetism-files/'):
            self.assertIn(f'href="{route}"', self.page)

    def test_claim_matrix_reviewed_and_null_excluded_claims(self):
        self.assertEqual(len(self.m["claims"]), 15)
        for claim in self.m["claims"]:
            if claim["status"] in ("unsubstantiated_product_specific",
                                   "unsubstantiated_health_claim",
                                   "contradicted_by_research_uncertainty"):
                self.assertIsNone(claim.get("fv_copy"), claim["id"])
        self.assertFalse(self.m["product_efficacy_independently_verified"])

    def test_actual_comparative_evidence(self):
        for token in ('https://pubmed.ncbi.nlm.nih.gov/37205669/',
                      'https://pubmed.ncbi.nlm.nih.gov/24395196/'):
            self.assertIn(token, self.page)
        for token in ('https://pubmed.ncbi.nlm.nih.gov/1500880/',
                      'https://pubmed.ncbi.nlm.nih.gov/8189198/'):
            self.assertIn(token, self.article)

    def test_video_release_gated_and_captioned(self):
        self.assertIn("WEBVTT", self.vtt)
        self.assertIn("00:00:40.000", self.vtt)
        self.assertIn("Video production is pending", self.page)
        self.assertIn("spoken plus on-screen", self.video)

    def test_no_vendor_product_guarantees_as_fact(self):
        lower = self.page.lower()
        for phrase in ("1 hour of meditation in 12 minutes",
                       "cures anxiety", "guaranteed instant results",
                       "meditates for you!", "clinically proven zen12"):
            self.assertNotIn(phrase, lower)

if __name__ == "__main__":
    unittest.main()
