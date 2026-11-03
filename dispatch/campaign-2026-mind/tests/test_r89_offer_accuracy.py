"""R89 original-copy alternatives must remain unsent and merchant-inactive."""
import json, pathlib, re, unittest
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]/"r89-offer-accuracy"
class Links(HTMLParser):
    def __init__(self): super().__init__();self.links=[];self.visible=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a": self.links.append(dict(attrs).get("href",""))
    def handle_data(self,s): self.visible.append(s)
class OfferReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.snapshot=json.loads((ROOT/"offer_snapshot.json").read_text(encoding="utf-8"))
    def test_all_external_permissions_fail_closed(self):
        for k,v in self.snapshot.items():
            if k.endswith("_verified") or k=="founder_final_send_approval": self.assertIs(v,False,k)
        self.assertEqual(self.snapshot["all_six_campaign_send_status"],"HOLD_UNSENT")
        self.assertEqual(self.snapshot["issue_03_05_additional_status"],"HOLD_MERCHANT")
    def test_offers_exact_and_sources(self):
        offers=self.snapshot["exact_public_offer_pages"]
        self.assertEqual(len(offers),2)
        self.assertIn("zen12.com/hnp",offers[0]["source"])
        self.assertIn("total-focus",offers[1]["source"])
        self.assertTrue(all(len(x["unsupported_claims"])>=3 for x in offers))
    def test_docs_exist_and_are_bounded(self):
        for n in ("03","05"):
            md=(ROOT/("issue-"+n+".md")).read_text(encoding="utf-8")
            txt=(ROOT/("issue-"+n+".txt")).read_text(encoding="utf-8")
            html=(ROOT/("issue-"+n+".html")).read_text(encoding="utf-8")
            p=Links();p.feed(html)
            self.assertGreater(len(md),2000)
            self.assertIn("UNSENT DRAFT",md)
            self.assertIn("PREVIEW ONLY",html)
            self.assertIn('role="presentation"',html)
            self.assertIn('lang="en"',html)
            self.assertNotIn("<script",html.lower())
            self.assertNotIn("<img",html.lower())
            self.assertLess(html.lower().index("commercial disclosure:"),html.lower().index("unavailable until"))
            self.assertTrue(all("zen12.com" not in x and "hypnosislive.com" not in x and "affiliate" not in x for x in p.links))
            for x in (md,txt,html):
                self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",x)
                self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",x)
                self.assertIn("may earn a commission",x)
                self.assertNotRegex(x, r"(?i)guaranteed income|cures anxiety|clinical proof of brain reprogramming")
            self.assertIn("FTC",md)
            self.assertIn("Final Vestige",txt)
    def test_subjects_and_preheaders_are_consistent(self):
        for n in ("03","05"):
            txt=(ROOT/("issue-"+n+".txt")).read_text(encoding="utf-8")
            md=(ROOT/("issue-"+n+".md")).read_text(encoding="utf-8")
            html=(ROOT/("issue-"+n+".html")).read_text(encoding="utf-8")
            subject=re.search(r"^Subject: (.+)$",txt,re.M).group(1)
            pre=re.search(r"^Editorial preheader suggestion \(Jetpack feature not verified\): (.+)$",txt,re.M).group(1)
            self.assertLessEqual(len(subject),65);self.assertLessEqual(len(pre),100)
            self.assertIn(subject,md);self.assertIn(subject,html)
            self.assertIn(pre,md);self.assertIn(pre,html)
    def test_one_disabled_guide_cta_and_product_truth(self):
        for n,token in (("03","[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]"),("05","[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]")):
            md=(ROOT/("issue-"+n+".md")).read_text(encoding="utf-8")
            self.assertEqual(md.count("**Only proposed CTA — DISABLED:**"),1)
            self.assertIn(token,md)
            self.assertNotIn("https://zen12.com",md)
            self.assertNotIn("https://hypnosislive.com",md)
            self.assertNotIn("$24.44",md);self.assertNotIn("$67.77",md)
        self.assertIn("33-minute",(ROOT/"issue-05.md").read_text(encoding="utf-8"))
        self.assertIn("24-MP3",(ROOT/"issue-03.md").read_text(encoding="utf-8"))
if __name__=="__main__": unittest.main()
