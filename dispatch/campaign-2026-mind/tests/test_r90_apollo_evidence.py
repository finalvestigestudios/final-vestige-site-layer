"""R90 Apollo 1 issue alternates: independent fail-closed and source-link audit."""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser
R = pathlib.Path(__file__).resolve().parents[1] / "r90-apollo-evidence"

class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.start_tags = []
        self.text = []
    def handle_starttag(self,tag,attrs):
        self.start_tags.append(tag)
        if tag == "a": self.links.append(dict(attrs).get("href", ""))
    def handle_data(self,data): self.text.append(data)
class ApolloProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((R/"source-ledger.json").read_text(encoding="utf-8"))
        cls.md=(R/"issue-04.md").read_text(encoding="utf-8")
        cls.txt=(R/"issue-04.txt").read_text(encoding="utf-8")
        cls.html=(R/"issue-04.html").read_text(encoding="utf-8")
        cls.parser=Reader();cls.parser.feed(cls.html)
    def test_editorial_only_not_approved(self):
        m=self.manifest
        self.assertEqual(m["send_status"],"HOLD_UNSENT")
        self.assertFalse(m["approved_replacement"])
        self.assertFalse(m["merchant_placement"])
        self.assertEqual(m["issue"],4)
        self.assertFalse(m["final_founder_send_approval"])
        self.assertEqual(m["subscriber_eligible_audience"],"UNKNOWN")
    def test_source_provenance_substantive(self):
        m=self.manifest
        self.assertGreaterEqual(len(m["claims"]),7)
        self.assertGreaterEqual(len(m["official_source_links"]),3)
        self.assertTrue(all(v["source"].startswith("https://") for v in m["claims"]))
        self.assertTrue(any(v["classification"]=="probable_not_certain" for v in m["claims"]))
        for url in m["official_source_links"]: self.assertIn(url,self.md)
    def test_no_unqualified_fourteen_seconds(self):
        for body in (self.md,self.txt,self.html):
            self.assertNotIn("Subject: Fourteen seconds",body)
            self.assertIn("fourteen seconds",body.lower())
            self.assertIn("not",body.lower())
            self.assertIn("electrical arc",body.lower())
            self.assertIn("16.7 psia",body)
    def test_exact_one_editorial_cta_and_no_merchant_links(self):
        m=self.manifest
        self.assertIn(m["cta"]["destination"],self.parser.links)
        self.assertEqual(self.parser.links.count(m["cta"]["destination"]),1)
        self.assertEqual(len(self.parser.links),4)
        self.assertTrue(all("zen12" not in s and "hypnosislive" not in s and "inspire3" not in s for s in self.parser.links))
        self.assertTrue(all(x.startswith("https://") for x in self.parser.links))
    def test_email_safe_review_only(self):
        self.assertIn('<html lang="en">',self.html)
        self.assertGreaterEqual(self.html.count('role="presentation"'),2)
        self.assertNotIn("<script",self.html.lower())
        self.assertNotIn("<img",self.html.lower())
        self.assertNotIn("<form",self.html.lower())
        self.assertNotIn("<iframe",self.html.lower())
        self.assertIn("REVIEW ONLY",self.html)
        for body in (self.md,self.txt,self.html):
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",body)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",body)
    def test_subject_preheader_parity(self):
        sub="The hatch was not the first failure"
        pre="Apollo 1, an uncertain ignition source, and six findings that changed the investigation."
        for body in (self.md,self.txt,self.html):
            self.assertIn(sub,body);self.assertIn(pre,body)
        self.assertLessEqual(len(sub),65);self.assertLessEqual(len(pre),100)
    def test_no_false_delivery_or_partner_authorization(self):
        m=self.manifest
        for x in ("actual_preheader_rendering_verified","received_jetpack_email_verified","welcome_receipt_verified","business_postal_verified","unsubscribe_render_verified"):
            self.assertIs(m[x],False,x)
        self.assertEqual(m["merchant_email_permissions_for_issue_03_05"],"UNVERIFIED")
        self.assertFalse(m["warmup_guides_published_for_issue_03_05"])
        self.assertFalse(m["auto_send_new_posts"])
    def test_no_actual_timing_as_individual_death_claim(self):
        self.assertIn("estimated",self.txt.lower())
        self.assertIn("not a stopwatch measurement",self.txt)
        self.assertIn("board",self.txt.lower())
        self.assertNotRegex(self.txt,re.compile(r"exactly (14|17) seconds",re.I))
if __name__=="__main__": unittest.main()
