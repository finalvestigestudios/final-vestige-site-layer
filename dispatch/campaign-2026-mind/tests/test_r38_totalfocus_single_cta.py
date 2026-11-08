"""R38 read-only source QA: verify new review candidate cannot slip into live send."""
import pathlib,json,unittest
from html.parser import HTMLParser
R=pathlib.Path(__file__).resolve().parents[1]
D=R/"r38-totalfocus-single-cta"
class Links(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            self.links += [v for k,v in attrs if k=="href" and v]
class Candidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md=(D/"ISSUE_05_REVIEW_CANDIDATE.md").read_text(encoding="utf-8")
        cls.html=(D/"ISSUE_05_REVIEW_CANDIDATE.html").read_text(encoding="utf-8")
        cls.txt=(D/"ISSUE_05_REVIEW_CANDIDATE.txt").read_text(encoding="utf-8")
        cls.wp=(D/"ISSUE_05_REVIEW_CANDIDATE.blocks.html").read_text(encoding="utf-8")
        cls.ledger=json.loads((D/"SOURCE_AND_ACTION_EVIDENCE.json").read_text(encoding="utf-8"))
        cls.manifest=json.loads((R/"manifest.json").read_text(encoding="utf-8"))
        cls.original=(R/"issues"/"05-before-you-press-play.md").read_text(encoding="utf-8")
    def candidates(self): return (self.md,self.html,self.txt,self.wp)
    def test_01_mix_preserved(self):
        self.assertEqual([x["kind"] for x in self.manifest["issues"]].count("editorial"),4)
        self.assertEqual([x["kind"] for x in self.manifest["issues"]].count("commercial-review-pending"),2)
    def test_02_all_six_held(self):
        self.assertEqual(self.manifest["status"],"DRAFT_UNSENT_NO_SCHEDULING")
        self.assertTrue(all(x["publish_state"]=="hold" for x in self.manifest["issues"]))
    def test_03_original_has_two_actions(self):
        self.assertIn("https://finalvestige.com/focus/",self.original)
        self.assertIn("[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]",self.original)
    def test_04_subject(self):
        for x in self.candidates(): self.assertIn("Before you press play on a hypnosis audio",x)
    def test_05_preheader_planned_only(self):
        for x in (self.md,self.html,self.txt): self.assertIn("A free three-minute check, then a clearer look at the claims.",x)
        self.assertIn("NOT VERIFIED IN JETPACK",self.md)
    def test_06_no_second_fieldbook_cta(self):
        for x in self.candidates(): self.assertNotIn("https://finalvestige.com/focus/",x)
    def test_07_one_proposed_action_each(self):
        for x in self.candidates(): self.assertEqual(x.count("Only proposed next step:"),1)
    def test_08_guide_deliberately_inactive(self):
        for x in self.candidates(): self.assertIn("[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]",x)
        self.assertFalse(self.ledger["candidate_issue05"]["action_live"])
    def test_09_no_direct_merchant_link(self):
        for x in self.candidates():
            self.assertNotIn("https://hypnosislive.com/",x)
            self.assertNotIn("https://affiliates.inspire3.com/",x)
            self.assertNotIn("hop.clickbank.net",x)
    def test_10_original_sources(self):
        for x in self.candidates():
            self.assertIn("https://www.nccih.nih.gov/health/hypnosis",x)
            self.assertIn("https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/",x)
    def test_11_advertised_specs(self):
        for x in self.candidates(): self.assertIn("33-minute",x); self.assertIn("47 MB",x)
    def test_12_efficacy_disclaimed(self):
        for x in self.candidates(): self.assertIn("not independently verified",x.lower())
    def test_13_disclosure_before_action(self):
        for x in self.candidates(): self.assertLess(x.index("Commercial disclosure:"),x.index("Only proposed next step:"))
    def test_14_no_fixed_price(self):
        for x in self.candidates():
            for s in ("$2","$17.95","$22.95","$29.95"): self.assertNotIn(s,x)
    def test_15_no_fake_product_trial(self):
        for x in self.candidates(): self.assertNotIn("I tested Total Focus",x)
    def test_16_html_two_source_anchors_only(self):
        h=Links();h.feed(self.html);self.assertEqual(set(h.links),{"https://www.nccih.nih.gov/health/hypnosis","https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"})
    def test_17_postal_placeholder(self):
        for x in self.candidates(): self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",x)
    def test_18_unsubscribe_placeholder(self):
        for x in self.candidates(): self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",x)
    def test_19_fails_closed(self):
        self.assertEqual(self.ledger["all_six"],"HOLD_UNSENT")
        self.assertEqual(self.ledger["issue05"],"HOLD_MERCHANT")
    def test_20_no_final_approval(self):
        self.assertFalse(self.ledger["controls"]["final_founder_campaign_send_approval"])
    def test_21_affiliate_rights_unverified(self):
        self.assertEqual(self.ledger["controls"]["partner_specific_email_rights"],"NOT_VERIFIED")
    def test_22_guide_not_published(self):
        self.assertEqual(self.ledger["candidate_issue05"]["live_vetted_guide"],"NOT_VERIFIED")
    def test_23_no_affiliate_tracked_link(self):
        self.assertEqual(self.ledger["candidate_issue05"]["earning_links_active"],0)
    def test_24_jetpack_is_excerpt(self):
        self.assertEqual(self.ledger["newsletter_2026_11_01_0731_utc"]["content_format"],"excerpt")
    def test_25_auto_email_off(self):
        self.assertFalse(self.ledger["newsletter_2026_11_01_0731_utc"]["auto_new_post_emails"])
    def test_26_subscriber_counters_nonadditive(self):
        a=self.ledger["newsletter_2026_11_01_0731_utc"]; self.assertEqual((a["subscriber_total"],a["confirmed"],a["unconfirmed"]),(2,2,2))
        self.assertEqual(a["unique_consent_eligible"],"UNKNOWN")
    def test_27_no_media_or_scripts(self):
        for x in (self.html,self.wp):
            for s in ("<script","<iframe","<img"): self.assertNotIn(s,x.lower())
    def test_28_semantic_email_markup(self):
        self.assertIn('lang="en"',self.html);self.assertIn('role="presentation"',self.html)
    def test_29_gutenberg_hold_banner(self):
        self.assertIn("DO NOT PUBLISH OR EMAIL",self.wp)
    def test_30_plaintext_is_text(self):
        self.assertNotIn("<p",self.txt);self.assertIn("THREE-MINUTE ATTENTION CHECK",self.txt)
    def test_31_board_is_review_only(self):
        v=(D/"REVIEW_BOARD.html").read_text(encoding="utf-8")
        self.assertIn("not an actual WordPress email preview",v)
        self.assertIn("HOLD_UNSENT",v)
    def test_32_mandatory_real_email_proof_missing(self):
        self.assertEqual(self.ledger["candidate_issue05"]["actual_jetpack_email"],"NOT_VERIFIED")
    def test_33_no_eml(self):
        self.assertFalse(list(D.glob("*.eml")))
if __name__=="__main__":unittest.main()
