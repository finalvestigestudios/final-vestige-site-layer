"""R103 read-only Apollo 1 source and email-safe candidate QA. No WP or network actions."""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser
HERE = pathlib.Path(__file__).resolve().parents[1] / "r103-apollo-risk-review"
ROOT = HERE.parent
MASTER = ROOT / "manifest.json"
class Links(HTMLParser):
    def __init__(self):
        super().__init__(); self.urls=[]; self.scripts=0; self.forms=0; self.images=0
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag=="a": self.urls.append(d.get("href",""))
        if tag in ("script","iframe","form","img","video","audio"): setattr(self,"scripts",self.scripts+1)
class R103(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=(HERE/"04-apollo-risk-review.md").read_text(encoding="utf8")
        cls.t=(HERE/"04-apollo-risk-review.txt").read_text(encoding="utf8")
        cls.h=(HERE/"04-apollo-review.html").read_text(encoding="utf8")
        cls.j=json.loads((HERE/"claim_and_release_ledger.json").read_text(encoding="utf8"))
        cls.master=json.loads(MASTER.read_text(encoding="utf8"))
    def test_original_campaign_held(self):
        self.assertEqual(self.master["status"],"DRAFT_UNSENT_NO_SCHEDULING")
        self.assertEqual([x["number"] for x in self.master["issues"]],[1,2,3,4,5,6])
    def test_original_mix_preserved(self):
        self.assertEqual([x["number"] for x in self.master["issues"] if x["kind"]=="commercial-review-pending"],[3,5])
        self.assertEqual(self.master["issues"][3]["subject"],"Seventeen seconds. A much longer explanation.")
    def test_no_activated_offer(self):
        self.assertEqual(self.j["affiliate_links"],[])
        self.assertFalse(self.j["merchant_approved"])
        self.assertFalse(self.j["founder_final_campaign_approval"])
    def test_subject_parity(self):
        for s in (self.m,self.t,self.h): self.assertIn(self.j["post_title_candidate"],s)
    def test_preheader_not_jetpack_claim(self):
        self.assertEqual(self.j["preheader_native_supported"],"UNVERIFIED")
        for s in (self.m,self.t): self.assertIn("Jetpack",s)
    def test_historical_nonhazardous_provenance(self):
        for phrase in ("unfueled","nonhazardous","90 seconds","ignition source"):
            self.assertIn(phrase,self.m.lower())
    def test_no_claim_exact_ignition(self):
        self.assertIn("did not identify a specific ignition source",self.m)
        self.assertNotIn("the ignition source was",self.m.lower())
    def test_no_unsupported_14_second_claim(self):
        for s in (self.m,self.t,self.h): self.assertNotIn("fourteen seconds",s.lower())
    def test_one_primary_cta(self):
        self.assertEqual(self.m.count("Read the Apollo 1 evidence trail:"),1)
        self.assertEqual(self.t.count("Read the Apollo 1 evidence trail:"),1)
        self.assertEqual(self.j["only_primary_cta"],"https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/")
    def test_source_domains(self):
        self.assertEqual(len(self.j["source_urls"]),4)
        self.assertTrue(all(x.startswith(("https://www.nasa.gov/","https://sma.nasa.gov/")) for x in self.j["source_urls"]))
    def test_no_embedded_sends(self):
        for s in (self.m,self.t,self.h):
            self.assertIn("UNSENT",s)
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",s)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",s)
    def test_never_impersonate_received_email(self):
        self.assertFalse(self.j["wordpress"]["received_email_verified"])
        self.assertIsNone(self.j["wordpress"]["actual_eligible_email_recipients"])
        self.assertFalse(self.j["wordpress"]["valid_fv_postal_address_verified"])
        self.assertFalse(self.j["wordpress"]["unsubscribe_function_verified"])
    def test_safe_html(self):
        p=Links();p.feed(self.h); self.assertEqual(p.scripts,0)
        self.assertIn('role="presentation"',self.h)
        self.assertIn('<meta name="viewport"',self.h)
        self.assertIn("NOT A JETPACK EMAIL",self.h)
        self.assertEqual(p.urls.count(self.j["only_primary_cta"]),1)
        self.assertEqual(len(p.urls),5)
        self.assertTrue(all(u.startswith(("https://finalvestige.com/","https://www.nasa.gov/","https://sma.nasa.gov/")) for u in p.urls))
    def test_no_authorized_send_state(self):
        self.assertEqual(self.j["status"],"HOLD_UNSENT")
        self.assertFalse(self.j["wordpress"]["email_new_posts_by_default"])
        self.assertEqual(self.j["wordpress"]["email_content_format"],"excerpt")
if __name__=="__main__": unittest.main()
