"""R46 optional Issue 01 editorial integrity; never authorizes sending."""
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "r46-archive-01"

class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.primary=0; self.images=0; self.scripts=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag == "a":
            self.links.append(a.get("href", ""))
            if a.get("data-role")=="primary-cta": self.primary+=1
        if tag=="img": self.images+=1
        if tag=="script": self.scripts+=1

class EditorialCandidateGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        cls.evidence=json.loads((BASE/"claim_register.json").read_text(encoding="utf-8"))
        cls.markdown=(BASE/"candidate01.md").read_text(encoding="utf-8")
        cls.plain=(BASE/"candidate01.txt").read_text(encoding="utf-8")
        cls.email=(BASE/"candidate01-email.html").read_text(encoding="utf-8")
        cls.gutenberg=(BASE/"candidate01-gutenberg.blocks.html").read_text(encoding="utf-8")
        cls.board=(BASE/"reviewer.html").read_text(encoding="utf-8")
        cls.links=Links();cls.links.feed(cls.email)

    def test_canonical_campaign_stays_six(self): self.assertEqual(len(self.manifest["issues"]),6)
    def test_canonical_4_2(self): self.assertEqual([v["kind"] for v in self.manifest["issues"]].count("commercial-review-pending"),2)
    def test_candidate_not_canonical(self): self.assertTrue(self.evidence["does_not_replace_canonical"])
    def test_candidate_not_approved(self): self.assertFalse(self.evidence["compliance"]["founder_final_send_approval"])
    def test_commercial_offers_absent(self): self.assertEqual(self.evidence["compliance"]["affiliate_offers"],0)
    def test_active_affiliate_hrefs_absent(self):
        self.assertEqual(self.evidence["compliance"]["affiliate_links"],0)
        self.assertFalse(any("zen12.com" in h or "hypnosislive.com" in h or "inspire3.com" in h for h in self.links.links))
    def test_only_one_primary_cta(self): self.assertEqual(self.links.primary,1)
    def test_primary_cta_is_verified_page(self): self.assertEqual(self.evidence["primary_cta"],"https://finalvestige.com/the-missing-caption/")
    def test_source_links_in_all_formats(self):
        for s in self.evidence["claims"][:3]:
            for content in (self.markdown,self.plain,self.email,self.gutenberg):
                self.assertIn(s["source"],content)
    def test_core_analytic_claim_in_all(self):
        for content in (self.markdown,self.plain,self.email,self.gutenberg):
            self.assertIn("Only half the pedestrians detected the swap",content)
            self.assertIn("Observation:",content)
            self.assertIn("Hypothesis:",content)
            self.assertIn("Cross-check:",content)
    def test_preheader_not_provider_verified(self): self.assertFalse(self.evidence["jetpack_preheader_control_verified"])
    def test_no_markup_scripts_or_pixels(self): self.assertEqual((self.links.scripts,self.links.images),(0,0))
    def test_email_accessible_structure(self):
        self.assertIn('<html lang="en">',self.email)
        self.assertIn('role="presentation"',self.email)
        self.assertIn('<h1 ',self.email)
    def test_sensitive_placeholder_gate(self):
        for content in (self.markdown,self.plain,self.email,self.gutenberg):
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",content)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",content)
    def test_no_active_form_in_board(self):
        self.assertNotIn("<form",self.board.lower());self.assertNotIn("<script",self.board.lower())
    def test_all_restrictions_false(self):
        c=self.evidence["compliance"]
        for k in ("actual_jetpack_received_email_verified","physical_postal_address_verified","functional_unsubscribe_verified","unique_subscriber_consent_verified","founder_final_send_approval"):
            self.assertIs(c[k],False)
    def test_core_promise_is_limited(self):
        self.assertIn("neither a universal eyewitness error rate",self.markdown)
        self.assertIn("analogy only", (BASE/"REVIEW_FIRST.md").read_text(encoding="utf-8"))

if __name__=="__main__": unittest.main()
