"""R15: fail-closed guards for the UNSENT Total Focus copy repair.

These assertions protect a draft, not authorization to mail it.
They run under the existing campaign QA unittest-discover command.
"""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TotalFocusCopyGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.record = next(i for i in cls.manifest["issues"] if i["number"] == 5)
        cls.md = (ROOT / "issues/05-before-you-press-play.md").read_text(encoding="utf-8")
        cls.html = (ROOT / "previews/05-before-you-press-play.html").read_text(encoding="utf-8")
        cls.plain = (ROOT / "previews/05-before-you-press-play.txt").read_text(encoding="utf-8")

    def test_original_campaign_mix_and_hold(self):
        self.assertEqual(self.manifest["status"], "DRAFT_UNSENT_NO_SCHEDULING")
        self.assertEqual(len(self.manifest["issues"]), 6)
        self.assertEqual(sum(i["kind"] == "editorial" for i in self.manifest["issues"]), 4)
        self.assertEqual(sum(i["kind"] == "commercial-review-pending" for i in self.manifest["issues"]), 2)
        self.assertEqual(self.record["publish_state"], "hold")
        self.assertIsNone(self.record["merchant_affiliate_url"])

    def test_subject_preheader_preserved(self):
        self.assertIn("**Subject:** " + self.record["subject"], self.md)
        self.assertIn("**Preheader:** " + self.record["preheader"], self.md)

    def test_exact_sku_and_seller_described_format(self):
        for text in (self.md, self.html, self.plain):
            self.assertIn("Total Focus", text)
            self.assertIn("33 minutes", text)
            self.assertIn("47 MB", text)

    def test_no_old_catalog_or_volatile_terms(self):
        for text in (self.md, self.html, self.plain):
            self.assertNotIn("more than 200", text)
            self.assertNotIn("five sessions per year", text)
            self.assertNotIn("most individual sessions", text)
            self.assertNotRegex(text, r"(?i)93% off|\$2\b|\$29\.95|buy before midnight")

    def test_claims_not_treated_as_independently_proven(self):
        for text in (self.md, self.html, self.plain):
            self.assertIn("not independently", text.lower())
            self.assertIn("NIH", text)

    def test_no_merchant_affiliate_or_direct_checkout_link(self):
        for text in (self.md, self.html, self.plain):
            self.assertNotIn("https://hypnosislive.com/", text)
            self.assertNotIn("affiliates.inspire3.com", text)
            self.assertNotRegex(text, r"(?i)\b(?:utm_source|affiliate_id|refid|aff_id)=")

    def test_disclosure_next_to_pending_one_primary_cta(self):
        a = self.md.index("**Commercial disclosure:**")
        b = self.md.index("**Review the Total Focus evidence and purchase questions:**")
        self.assertLess(a, b)
        self.assertLess(b - a, 750)
        for text in (self.md, self.html, self.plain):
            self.assertIn("APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED", text)
            self.assertIn("commission", text.lower())
        self.assertNotIn('href="[[APPROVED_', self.html)

    def test_legal_holds_cannot_disappear(self):
        for item in ("[[VALID_POSTAL_ADDRESS_REQUIRED]]",
                     "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"):
            self.assertIn(item, self.md)
            self.assertIn(item, self.plain)
        self.assertIn("NOT A SENT EMAIL", self.html)
        self.assertIn("UNSENT DRAFT", self.md)

    def test_source_link_and_independent_free_alternative(self):
        self.assertIn("https://www.nccih.nih.gov/health/hypnosis", self.md)
        self.assertIn("https://finalvestige.com/focus/", self.md)
        self.assertIn("https://www.nccih.nih.gov/health/hypnosis", self.html)
        self.assertIn("https://finalvestige.com/focus/", self.plain)


if __name__ == "__main__":
    unittest.main()
