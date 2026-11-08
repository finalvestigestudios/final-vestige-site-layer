"""Independent regression checks for optional R79 source-led, HOLD-only manuscripts."""
import json, pathlib, re, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
DIR = ROOT / "r79-proof-first-editions"
class R79EditorialQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((DIR/"SOURCE-AND-RELEASE.json").read_text(encoding="utf-8"))
        cls.docs={x:(DIR/x).read_text(encoding="utf-8") for x in ("04-apollo-1.md","03-zen12.md","05-total-focus.md")}
        cls.html=(DIR/"REVIEWER.html").read_text(encoding="utf-8")
        cls.txt=(DIR/"REVIEWER.txt").read_text(encoding="utf-8")
    def test_release_hold(self):
        self.assertEqual(self.manifest["status"],"HOLD_UNSENT")
        self.assertFalse(self.manifest["original_issues_changed"])
        self.assertEqual(self.manifest["founder_mix"],{"editorial":4,"commercial_reserved":2})
    def test_slot_mapping(self):
        self.assertEqual({x["slot"] for x in self.manifest["versions"]},{3,4,5})
        self.assertEqual(sum(bool(x["offer"]) for x in self.manifest["versions"]),2)
    def test_subjects_not_number_hype(self):
        ap=self.docs["04-apollo-1.md"].lower()
        self.assertIn("spark was never the whole story",ap)
        self.assertNotIn("fourteen seconds",ap)
        self.assertNotIn("seventeen seconds",ap)
    def test_nasa_sources(self):
        s=self.docs["04-apollo-1.md"]
        self.assertIn("sma.nasa.gov",s)
        self.assertIn("apollo-204-review-board",s)
        self.assertIn("specific ignition source",s)
        self.assertIn("hatch",s.lower())
    def test_issues_complete(self):
        for f,s in self.docs.items():
            with self.subTest(f=f):
                self.assertGreater(len(s.split()),480)
                self.assertIn("HOLD_UNSENT",s)
                self.assertIn("Proposed subject:",s)
                self.assertIn("Proposed custom Jetpack excerpt:",s)
                self.assertIn("One ",s)
    def test_commercial_scope(self):
        for n in ("03-zen12.md","05-total-focus.md"):
            s=self.docs[n]
            self.assertIn("HOLD_MERCHANT",s)
            self.assertIn("INACTIVE",s)
            self.assertIn("[[APPROVED_",s)
            self.assertIn("Commercial disclosure beside the reserved CTA",s)
            self.assertIn("commission",s.lower())
    def test_disclosure_first_55_in_custom_excerpt(self):
        for n in ("03-zen12.md","05-total-focus.md"):
            s=self.docs[n]
            m=re.search(r"\*\*Proposed custom Jetpack excerpt:\*\*\s*(.+)",s)
            self.assertIsNotNone(m)
            first=" ".join(m.group(1).split()[:55]).lower()
            self.assertIn("commercial disclosure",first)
            self.assertIn("commission",first)
            self.assertIn("no earning link is active",first)
    def test_no_bogus_claims(self):
        for n,s in self.docs.items():
            with self.subTest(n=n):
                self.assertNotIn("guaranteed to improve",s.lower())
                self.assertNotIn("clinically proven",s.lower())
                self.assertNotIn("buy now",s.lower())
    def test_merchant_named_and_boundaries(self):
        self.assertIn("Zen12",self.docs["03-zen12.md"])
        self.assertIn("seller",self.docs["03-zen12.md"].lower())
        self.assertIn("J. A. Amos",self.docs["05-total-focus.md"])
        self.assertIn("33 minutes",self.docs["05-total-focus.md"])
    def test_no_false_merchant_approval(self):
        c=self.manifest["channel_evidence"]
        for k in ("zen12_email_permission","total_focus_email_permission","zen12_published_guide","total_focus_published_guide","active_affiliate_link","founder_final_send_approval","genuine_received_email","functional_unsubscribe_verified","verified_publisher_postal","test_email_authorized"):
            with self.subTest(k=k): self.assertIs(c[k],False)
    def test_counts_not_inferred(self):
        c=self.manifest["channel_evidence"]
        self.assertEqual(c["status_counts"]["total"],2)
        self.assertEqual(c["followers_endpoint"]["email"],0)
        self.assertIsNone(c["true_email_eligible_audience"])
    def test_send_false(self):
        c=self.manifest["channel_evidence"]
        self.assertFalse(c["auto_new_posts_email"])
        self.assertEqual(c["actual_send_count"],0)
        self.assertEqual(c["email_format"],"excerpt")
    def test_reviewer_accessible(self):
        self.assertIn('lang="en"',self.html)
        self.assertIn('href="#content"',self.html)
        self.assertIn('role="presentation"',self.html)
        self.assertEqual(self.html.count('role="presentation"'),3)
        self.assertEqual(self.html.count("HOLD_UNSENT — REVIEWER"),1)
    def test_no_active_merchant_or_code_in_html(self):
        h=self.html.lower()
        for token in ("<script","<iframe","<form","href=\"https://zen12", "href=\"https://hypnosislive","utm_", "clickid", "track="):
            self.assertNotIn(token,h)
    def test_html_cites_sources(self):
        self.assertIn("https://sma.nasa.gov",self.html)
        self.assertIn("https://zen12.com/hnp",self.html)
        self.assertIn("https://hypnosislive.com/mental-skills/total-focus",self.html)
    def test_text_full_length(self):
        for x in ("APOLLO 1","Zen12","Total Focus","HOLD_UNSENT"):
            self.assertIn(x,self.txt)
        self.assertGreater(len(self.txt.split()),1500)
    def test_no_pii_in_manifest(self):
        s=json.dumps(self.manifest)
        self.assertNotRegex(s,r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    def test_all_sources_https(self):
        for item in self.manifest["versions"]:
            self.assertTrue(all(x.startswith("https://") for x in item["sources"]))
    def test_false_preheader_guarantee_avoided(self):
        self.assertIn("unverified control",self.txt.lower())
        self.assertIn("not delivered",self.txt.lower())
    def test_no_postal_address_in_preview(self):
        self.assertNotRegex(self.html,r"\b\d{5}(?:-\d{4})?\b")
        self.assertIn("Publisher address",self.html)
    def test_readme_clarity(self):
        readme=(DIR/"README.md").read_text(encoding="utf-8")
        for s in ("HOLD_UNSENT","PR #700","PR #692","first 55 words","postal address","founder"):
            self.assertIn(s,readme)
if __name__=="__main__": unittest.main()
