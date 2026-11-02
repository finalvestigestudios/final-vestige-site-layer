"""Deterministic offline QA: R65 optional editorials and actual-delivery contract."""
import json
import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
NEW=ROOT/"r65-editorial-endcaps"
ISSUES=(1,6)
class R65Endcaps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.status=json.loads((NEW/"manifest.json").read_text(encoding="utf-8"))
        cls.canonical=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))

    def read(self,n,suffix):
        return (NEW/f"issue{n:02d}-{suffix}").read_text(encoding="utf-8")

    def test_sources_preserved(self):
        self.assertEqual(len(self.canonical["issues"]),6)
        self.assertEqual(self.canonical["mix"]["editorial"],4)
        self.assertEqual(self.canonical["mix"]["commercial_review_pending"],2)

    def test_six_holds(self):
        self.assertEqual(len(self.status["issues_release"]),6)
        self.assertTrue(all("HOLD_UNSENT" in x for x in self.status["issues_release"]))
        self.assertIn("HOLD_MERCHANT",self.status["issues_release"][2])
        self.assertIn("HOLD_MERCHANT",self.status["issues_release"][4])

    def test_no_send_or_automation(self):
        self.assertFalse(self.status["current_newsletter_settings"]["email_new_posts_by_default"])
        self.assertEqual(self.status["current_newsletter_settings"]["email_content_format"],"excerpt")
        self.assertFalse(self.status["analytics_collection_enabled"])
        self.assertFalse(self.status["affiliate_links_active"])
        self.assertFalse(self.status["tracking_pixels_active"])

    def test_all_gate_proofs_false(self):
        self.assertGreaterEqual(len(self.status["pending_proofs"]),8)
        self.assertFalse(any(self.status["pending_proofs"].values()))
        self.assertFalse(self.status["current_newsletter_settings"]["welcome_receipt_verified"])

    def test_subscriber_counts_not_additive(self):
        b=self.status["subscribed_counts"]
        self.assertEqual((b["total"],b["confirmed"],b["unconfirmed"]),(2,2,2))
        self.assertTrue(b["distinct_email_eligible_unknown"])

    def test_essential_metadata(self):
        self.assertEqual(self.status["source_master_pr"],175)
        self.assertEqual(self.status["source_gate_pr"],201)
        self.assertEqual(len(self.status["alternatives"]),2)
        self.assertEqual({x["issue"] for x in self.status["alternatives"]},{1,6})

    def test_full_draft_length_and_planning_preamble(self):
        for n in ISSUES:
            s=self.read(n,"original.md")
            self.assertGreater(len(s.split()),420)
            self.assertIn("HOLD_UNSENT",s)
            self.assertIn("NOT APPROVED TO SUBSTITUTE",s)
            self.assertIn("Planning-only preheader",s)

    def test_primary_studies_exactly_attributed(self):
        a=self.read(1,"original.md")
        self.assertIn("10.3758/BF03208840",a)
        self.assertIn("10.1068/p281059",a)
        self.assertIn("social group",a.lower())
        self.assertIn("not interchangeable",a.lower())
        b=self.read(6,"original.md")
        for value in ("90%","11%","20%","2002","80 patients"):
            self.assertIn(value,b)
        self.assertIn("not a forecast",b)

    def test_no_efficacy_overclaim(self):
        for n in ISSUES:
            s=self.read(n,"original.md").lower()
            for prohibited in ("clinically proven", "guaranteed to cure", "unlocks your brain", "magic audio"):
                self.assertNotIn(prohibited,s)

    def test_one_editorial_cta_per_draft(self):
        for n in ISSUES:
            s=self.read(n,"original.md")
            self.assertEqual(s.count("**One "),1)
            self.assertEqual(s.count("https://finalvestige.com/"),1)

    def test_active_product_links_absent(self):
        for n in ISSUES:
            for suffix in ("original.md","review.html","review.txt"):
                s=self.read(n,suffix)
                self.assertNotIn("https://zen12.com/",s)
                self.assertNotIn("https://hypnosislive.com/",s)
                self.assertNotIn("https://affiliates.inspire3.com/",s)

    def test_footer_placeholders_block_send(self):
        for n in ISSUES:
            for suffix in ("original.md","review.html","review.txt"):
                s=self.read(n,suffix)
                self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",s)
                self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",s)

    def test_html_is_nojs_and_email_compatible(self):
        for n in ISSUES:
            s=self.read(n,"review.html").lower()
            self.assertIn('lang="en"',s)
            self.assertIn('role="presentation"',s)
            self.assertIn('width="100%"',s)
            self.assertIn("max-width:640px",s)
            self.assertNotRegex(s,r"<(?:script|form|iframe|video|img|svg)\b")
            self.assertNotIn("http-equiv=\"refresh\"",s)
            self.assertNotIn("utm_",s)
            self.assertNotIn("pixel.gif",s)

    def test_html_and_text_contain_complete_story(self):
        for n in ISSUES:
            html=self.read(n,"review.html")
            txt=self.read(n,"review.txt")
            self.assertGreater(len(html),2400)
            self.assertGreater(len(txt),2300)
            self.assertIn("Research record",txt) if n==6 else self.assertIn("Research records",txt)
            self.assertIn("UNSENT OFFLINE",html)
            self.assertIn("OFFLINE REVIEW",txt)

    def test_no_private_data(self):
        for n in ISSUES:
            for suffix in ("original.md","review.html","review.txt"):
                x=self.read(n,suffix)
                self.assertNotRegex(x,r"(?i)unsubscribe\?token=")
                self.assertNotRegex(x,r"(?i)email=[^&\\s]+@")
                self.assertNotIn("Bryan",x)

    def test_no_literal_postal_address(self):
        for n in ISSUES:
            self.assertNotIn("Automattic, Inc.",self.read(n,"review.html"))
            self.assertNotIn("Inspire3 Ltd",self.read(n,"review.txt"))

    def test_source_ledger(self):
        s=(NEW/"source-ledger.md").read_text(encoding="utf-8")
        for x in ("10.3758/BF03208840","10.1068/p281059","bmj.com/content/324/7347/1193"):
            self.assertIn(x,s)

    def test_channel_contract(self):
        s=(NEW/"channel-and-consent.md").read_text(encoding="utf-8")
        for x in ("excerpt","55 words","/dispatch/","/focus/","not a promised delivered field"):
            # Case-insensitive check: publisher draft uses deliberate emphasis.
            self.assertIn(x.lower(),s.lower())
        self.assertIn("NO changes applied",s)

    def test_first_party_destinations(self):
        self.assertEqual(self.status["alternatives"][0]["cta"],"https://finalvestige.com/the-missing-caption/")
        self.assertEqual(self.status["alternatives"][1]["cta"],"https://finalvestige.com/focus/")
        self.assertTrue(all(x["affiliate_url"] is None for x in self.status["alternatives"]))

    def test_no_approval_by_test(self):
        s=(NEW/"README.md").read_text(encoding="utf-8")
        self.assertIn("not inbox deliverability",s)
        self.assertIn("HOLD_MERCHANT",s)

if __name__=="__main__":
    unittest.main()
