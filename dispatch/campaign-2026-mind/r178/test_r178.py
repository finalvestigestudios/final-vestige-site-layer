"""Source-level fail-closed checks for R178 optional UNSENT editorial letter."""
import json, pathlib, re, unittest
D = pathlib.Path(__file__).resolve().parent
class Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=(D/"ISSUE_04_CANDIDATE.md").read_text(encoding="utf-8")
        cls.p=(D/"ISSUE_04_PLAINTEXT.txt").read_text(encoding="utf-8")
        cls.h=(D/"ISSUE_04_PREVIEW.html").read_text(encoding="utf-8")
        cls.j=json.loads((D/"RELEASE_LEDGER.json").read_text(encoding="utf-8"))
    def test_holds(self):
        assert self.j["release"]["decision"]=="HOLD_UNSENT"
        assert self.j["commercial"]["offer_cta_activated"] is False
        assert self.j["release"]["email_or_test_sent"] is False
        assert self.j["replaces_original"] is False
        assert self.j["campaign_ratio"]=={"editorial":4,"commercial_held":2}
    def test_subject_and_preheader(self):
        for s in (self.m,self.p,self.h):
            self.assertIn(self.j["subject"],s)
            self.assertIn(self.j["proposed_preheader"],s)
        self.assertLessEqual(len(self.j["subject"]),60)
        self.assertLessEqual(len(self.j["proposed_preheader"]),100)
    def test_legal_holds_are_unequivocal(self):
        for s in (self.m,self.p,self.h):
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",s)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",s)
            self.assertRegex(s,"(?i)unsent")
    def test_no_external_earning_links(self):
        for s in (self.m,self.p,self.h):
            for suspect in ("awin1.com","clickbank.net","hop.clickbank","affiliates.inspire3.com","checkout","utm_content=fake"):
                self.assertNotIn(suspect,s.lower())
        self.assertIsNone(self.j["commercial"]["merchant_earning_url"])
    def test_editorial_cta_and_source_trace(self):
        for s in (self.m,self.p,self.h):
            self.assertIn(self.j["cta"]["url"],s)
            for src in self.j["sources"]:
                self.assertIn(src["url"],s)
        self.assertEqual(self.j["cta"]["type"],"FIRST_PARTY_EDITORIAL")
        self.assertEqual(len(self.j["sources"]),3)
    def test_html_is_email_safe_static_review(self):
        self.assertIn('lang="en"',self.h)
        self.assertIn('role="presentation"',self.h)
        self.assertIn("<h1",self.h)
        for tag in ("<script","<iframe","<form","<input","<video","<audio","autofocus"):
            self.assertNotIn(tag,self.h.lower())
    def test_no_fake_conversion(self):
        att=self.j["attribution"]
        self.assertIsNone(att["qualified_human_sessions"])
        self.assertIsNone(att["verified_paid_orders"])
        self.assertIsNone(att["realized_net_revenue"])
        self.assertEqual(att["net_revenue_per_1000_qualified_sessions"],"NOT_COMPUTABLE")
    def test_same_one_primary_cta(self):
        self.assertEqual(self.h.count("Explore the Lycurgus Cup evidence →</a>"),1)
        self.assertEqual(self.p.count("EXPLORE THE EVIDENCE"),1)
    def test_all_unresolved_permissions(self):
        self.assertEqual(self.j["commercial"]["affiliate_approval"],"UNVERIFIED")
        self.assertEqual(self.j["commercial"]["email_permission"],"UNVERIFIED")
        self.assertEqual(self.j["release"]["native_jetpack_preview"],"UNVERIFIED")
if __name__=="__main__": unittest.main()
