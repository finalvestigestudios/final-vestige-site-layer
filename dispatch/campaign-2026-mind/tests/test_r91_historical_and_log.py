"""Native offline regression guards for R91 optional editorial issues; never permit send."""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlparse
ROOT = pathlib.Path(__file__).resolve().parents[1] / "r91-historical-witness-and-seven-day-log"
LEDGER = json.loads((ROOT / "source-and-release-ledger.json").read_text(encoding="utf-8"))
class ReviewHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == "a":
            self.links.append(dict(attrs).get("href"))
class R91Guards(unittest.TestCase):
    def test_six_mixture_unchanged(self):
        self.assertEqual(LEDGER["mix"], {"editorial":4,"commercial_reserved":2})
        self.assertFalse(LEDGER["approved_substitution"])
    def test_fail_closed(self):
        for k in ("merchant_email_permission_verified","real_jetpack_received_email_verified","verified_publisher_postal_address","eligible_email_recipients_verified","founder_final_send_approval"):
            self.assertIs(LEDGER[k], False, k)
        self.assertFalse(any(LEDGER["actions"].values()))
    def test_two_optional_editions(self):
        self.assertEqual({i["number"] for i in LEDGER["issues"]}, {2,6})
        self.assertTrue(all(i["kind"] == "editorial" and i["release_state"] == "HOLD_UNSENT" for i in LEDGER["issues"]))
    def test_preheader_not_promised(self):
        self.assertTrue(all(i["preheader_real_jetpack_control"] == "NOT_VERIFIED" for i in LEDGER["issues"]))
    def test_dates_from_distinct_catalogs(self):
        src = {c["source"] for c in LEDGER["claims"]}
        self.assertIn("https://catalogue.bnf.fr/ark:/12148/cb31160297p",src)
        self.assertIn("https://www.ncbi.nlm.nih.gov/nlmcatalog/440836",src)
        s=(ROOT/"issue-02.md").read_text(encoding="utf-8")
        self.assertIn("1784–1785",s)
        self.assertIn("1784 [i.e. 1785]",s)
        self.assertIn("February 4, 1785",s)
    def test_provenance_without_miracle(self):
        s=(ROOT/"issue-02.md").read_text(encoding="utf-8").lower()
        for v in ("not an independently verified test","not a controlled re-creation","different studies answer different questions"):
            self.assertIn(v,s)
    def test_focus_five_fields(self):
        s=(ROOT/"issue-06.md").read_text(encoding="utf-8").lower()
        for v in ("whether you started","approximate minutes","main interruption","starting easier or harder","small change"):
            self.assertIn(v,s)
    def test_not_medical_trial(self):
        s=(ROOT/"issue-06.md").read_text(encoding="utf-8").lower()
        for v in ("cannot establish","medical or scientific efficacy claim","seven-day"):
            self.assertIn(v,s)
    def test_all_formats_exist(self):
        for n in ("02","06"):
            for ext in ("md","txt","html"):
                self.assertGreater((ROOT/f"issue-{n}.{ext}").stat().st_size,1000)
    def test_subjects_and_cta_align(self):
        for i in LEDGER["issues"]:
            n=f'{i["number"]:02d}'
            for ext in ("md","txt","html"):
                content=(ROOT/f"issue-{n}.{ext}").read_text(encoding="utf-8")
                self.assertIn(i["subject"],content)
                self.assertIn(i["cta"],content)
    def test_legal_hard_stops(self):
        for n in ("02","06"):
            for ext in ("md","txt","html"):
                c=(ROOT/f"issue-{n}.{ext}").read_text(encoding="utf-8")
                for marker in LEDGER["legal_hard_stop_placeholders"]:
                    self.assertIn(marker,c)
    def test_html_accessibility_and_email_style(self):
        for n in ("02","06"):
            c=(ROOT/f"issue-{n}.html").read_text(encoding="utf-8")
            p=ReviewHTML();p.feed(c)
            self.assertIn("lang=\"en\"",c)
            self.assertIn('name="viewport"',c)
            self.assertIn("role=\"presentation\"",c)
            self.assertIn("<h1",c)
            self.assertIn("<h2",c)
            self.assertNotIn("<script",c.lower())
            self.assertNotIn("<iframe",c.lower())
            self.assertNotIn("<form",c.lower())
            self.assertGreaterEqual(len(p.links),2)
    def test_merchant_domains_absent_from_preview(self):
        for n in ("02","06"):
            c=(ROOT/f"issue-{n}.html").read_text(encoding="utf-8")
            p=ReviewHTML();p.feed(c)
            for link in p.links:
                host=urlparse(link).hostname
                self.assertNotIn(host,("zen12.com","hypnosislive.com","inspire3.com"))
    def test_exactly_one_primary_cta(self):
        for i in LEDGER["issues"]:
            n=f'{i["number"]:02d}'
            c=(ROOT/f"issue-{n}.html").read_text(encoding="utf-8")
            self.assertEqual(c.count('href="'+i["cta"]+'"'),1)
    def test_excerpts_are_not_claimed_actual_received(self):
        r=(ROOT/"README.md").read_text(encoding="utf-8").lower()
        self.assertIn("not jetpack output",r)
        self.assertIn("no emails or test messages sent",r)
    def test_no_recipient_pii_in_artifacts(self):
        for f in ROOT.iterdir():
            if not f.is_file():continue
            c=f.read_text(encoding="utf-8")
            self.assertNotRegex(c, r'(?i)\b[a-z0-9._%+-]+@(?!example\.)[a-z0-9.-]+\.[a-z]{2,}\b')
    def test_official_claims_scope(self):
        claims={x["id"]:x for x in LEDGER["claims"]}
        self.assertEqual(claims["C03"]["status"],"witness_claim_not_independently_verified")
        self.assertEqual(claims["C08"]["status"],"PERMISSION_NOT_VERIFIED")
        self.assertEqual(claims["C09"]["status"],"VENDOR_CLAIM_ONLY")
    def test_wp_counts_not_summed(self):
        wp=LEDGER["wordpress"]
        self.assertEqual(wp["eligible_actual"],"UNKNOWN")
        self.assertEqual((wp["subscriber_summary"]["total"],wp["subscriber_summary"]["confirmed"],wp["subscriber_summary"]["unconfirmed"]),(2,2,2))
    def test_full_source_urls_present(self):
        for i in LEDGER["issues"]:
            n=f'{i["number"]:02d}'
            for url in i["source_refs"]:
                for ext in ("md","txt","html"):
                    self.assertIn(url,(ROOT/f"issue-{n}.{ext}").read_text(encoding="utf-8"))
    def test_unmodified_master(self):
        self.assertEqual(LEDGER["master_pr"],175)
        self.assertEqual(LEDGER["parent_pr"],782)
if __name__=="__main__":
    unittest.main()
