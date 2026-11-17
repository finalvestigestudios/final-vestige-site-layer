"""R411 standalone fail-closed release truth checks (no network and no sending)."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent

class TestReleaseTruth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = json.loads((ROOT / "CONSOLIDATED_HOLD_LEDGER.json").read_text(encoding="utf-8"))
        cls.md = (ROOT / "ISSUE02_FRANKLIN_OPTIONAL.md").read_text(encoding="utf-8")
        cls.plain = (ROOT / "ISSUE02_FRANKLIN_OFFLINE.txt").read_text(encoding="utf-8")
        cls.html = (ROOT / "ISSUE02_FRANKLIN_OFFLINE.html").read_text(encoding="utf-8")

    def test_six_slots_and_ratio(self):
        self.assertEqual([x["number"] for x in self.d["issues"]], list(range(1,7)))
        self.assertEqual(sum(x["kind"]=="editorial" for x in self.d["issues"]),4)
        self.assertEqual([x["number"] for x in self.d["issues"] if x["kind"]=="commercial-review-pending"],[3,5])

    def test_every_issue_held(self):
        self.assertFalse(self.d["send_allowed"])
        self.assertFalse(self.d["founder_final_approval"])
        self.assertEqual(self.d["decision"],"HOLD_UNSENT")
        self.assertTrue(all(x["issue_state"].startswith("HOLD") for x in self.d["issues"]))

    def test_no_fake_leads_or_sales(self):
        n=self.d["newsletter"]; c=self.d["conversion"]
        self.assertIsNone(n["distinct_eligible_recipients"])
        self.assertEqual((n["total"],n["confirmed"],n["unconfirmed"]),(3,3,2))
        for k in ("realized_revenue_usd","qualified_human_sessions","net_revenue_per_1000_qualified_human_sessions"):
            self.assertIsNone(c[k])
        self.assertFalse(c["affiliate_email_authorized"])
        self.assertFalse(c["issued_affiliate_link_verified"])

    def test_commercial_ctas_inactive(self):
        for x in self.d["issues"]:
            if x["number"] in (3,5):
                self.assertEqual(x["cta"],"INACTIVE_GUIDE_PENDING")
                self.assertIs(x["commercial_partner_email_permitted"],False)
            else:
                self.assertEqual(x["cta"],"LIVE_FIRST_PARTY")

    def test_optional_franklin_not_adopted(self):
        self.assertIn("NOT_ADOPTED",self.md)
        self.assertIn("HOLD_UNSENT",self.md)
        self.assertIn("NOT ADOPTED",self.plain)
        self.assertIn("DRAFT ONLY",self.html)
        self.assertNotIn("AFFILIATE_TRACKING_URL",self.html)

    def test_source_and_cta_parity(self):
        url="https://finalvestige.com/2026/11/02/mesmerism/"
        self.assertEqual(self.html.count('href="'+url+'"'),1)
        self.assertEqual(self.md.count("]("+url+")"),1)
        self.assertEqual(self.plain.count(url),1)
        for u in ("https://wellcomecollection.org/works/qaa7fryp","https://wellcomecollection.org/works/enhgscmf"):
            for s in (self.md,self.plain,self.html):
                self.assertIn(u,s)

    def test_email_safe_offline(self):
        h=self.html.lower()
        for pattern in ("<script","<form","<iframe","<img","<video","<style"):
            self.assertNotIn(pattern,h)
        self.assertIn('lang="en"',h)
        self.assertIn('role="presentation"',h)
        self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",self.html)
        self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",self.html)
        self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",self.md)
        self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",self.plain)

    def test_no_confused_vendor_claims(self):
        email=" ".join((self.md,self.plain,self.html)).lower()
        for phrase in ("hour of meditation in just 12 minutes","guaranteed anxiety relief","100% razor-sharp concentration","buy now","coupon code"):
            self.assertNotIn(phrase,email)

if __name__ == "__main__":
    unittest.main()
