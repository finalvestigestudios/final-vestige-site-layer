"""Dispatch R47 offline test suite for optional edition 02. Never authorizes mail."""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/"r47-replication-02"
CTA="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"
ADDR="[[VALID_POSTAL_ADDRESS_REQUIRED]]"
UNSUB="[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.hs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="a":self.links.append(a)
        if tag in ("h1","h2"):self.hs.append(tag)

class Edition47(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md=(D/"candidate02.md").read_text(encoding="utf-8")
        cls.txt=(D/"candidate02.txt").read_text(encoding="utf-8")
        cls.em=(D/"candidate02-email.html").read_text(encoding="utf-8")
        cls.wp=(D/"candidate02-gutenberg.blocks.html").read_text(encoding="utf-8")
        cls.r=json.loads((D/"claim_register.json").read_text(encoding="utf-8"))
        cls.links=Links();cls.links.feed(cls.em)
    def test_all_files(self):
        for p in ("candidate02.md","candidate02.txt","candidate02-email.html","candidate02-gutenberg.blocks.html","claim_register.json","reviewer.html","REVIEW_FIRST.md"):
            self.assertTrue((D/p).exists());self.assertGreater((D/p).stat().st_size,250)
    def test_head_identity(self):self.assertEqual(self.r["source_parent_sha"],"a9f523fdbc2b6b43cd6760cae03245d4b16a3b92")
    def test_hard_hold(self):self.assertEqual(self.r["status"],"HOLD_UNSENT_OPTIONAL_ED02")
    def test_original_unchanged(self):self.assertTrue(self.r["canonical_issue_02_unchanged"])
    def test_founder_not_approved(self):self.assertFalse(self.r["founder_approved_substitution"])
    def test_no_wp_post(self):self.assertFalse(self.r["wordpress_post_created"])
    def test_no_email_sent(self):self.assertFalse(self.r["email_sent"])
    def test_no_email_receipt(self):self.assertFalse(self.r["actual_email_receipt"])
    def test_no_verified_audience(self):self.assertFalse(self.r["subscriber_eligibility_verified"])
    def test_no_postal_or_unsub_verified(self):self.assertFalse(self.r["postal_address_verified"]);self.assertFalse(self.r["unsubscribe_verified"])
    def test_one_primary_html_link(self):
        c=[x for x in self.links.links if x.get("class")=="fv-primary-cta"]
        self.assertEqual(len(c),1);self.assertEqual(c[0]["href"],CTA)
    def test_published_first_party_cta(self):self.assertEqual(self.r["primary_cta_url"],CTA);self.assertEqual(self.r["primary_cta_wp_page"],1377)
    def test_subject_all_formats(self):
        for s in (self.md,self.txt,self.em,self.wp):self.assertIn("The book he did not want everyone to read",s)
    def test_preview_not_native(self):self.assertIn("not native Jetpack preheader",self.md)
    def test_preview_all_review_formats(self):
        for s in (self.md,self.txt,self.em):self.assertIn("Puységur wanted witnesses, not just believers. The 1784 record explains why.",s)
    def test_word_count(self):self.assertGreaterEqual(self.r["story_word_count"],600)
    def test_fifty_not_verified(self):
        for s in (self.md,self.txt):self.assertIn("not evidence that fifty successful independent replications",s)
    def test_two_books_distinct(self):
        for s in (self.md,self.txt):self.assertIn("Détail des cures",s);self.assertIn("Mémoires",s)
    def test_no_seller_domains(self):
        for s in (self.md,self.txt,self.em,self.wp):
            for bad in ("zen12.com","hypnosislive.com","inspire3.com","utm_source=","clickbank","javascript:"):self.assertNotIn(bad,s.lower())
    def test_no_fake_commerce(self):self.assertEqual(self.r["commerce_links"],0);self.assertEqual(self.r["commercial_slots_in_original_pilot"],[3,5])
    def test_footer_hardstop(self):
        for s in (self.md,self.txt,self.em,self.wp):self.assertIn(ADDR,s);self.assertIn(UNSUB,s)
    def test_no_executable_html(self):
        for s in ("<script","<iframe","<form","<img","<video","<style","srcset="):self.assertNotIn(s,self.em.lower())
    def test_email_accessible_heading(self):self.assertEqual(self.links.hs.count("h1"),1);self.assertIn('lang="en"',self.em);self.assertIn('role="presentation"',self.em)
    def test_five_primary_bibliography_links(self):self.assertEqual(len(self.r["sources"]),5)
    def test_sources_in_html(self):
        for u in self.r["sources"]:self.assertIn(u,self.em)
    def test_source_https(self):
        for u in self.r["sources"]+[CTA]:self.assertEqual(urlparse(u).scheme,"https")
    def test_disclosure_each(self):
        for s in (self.md,self.txt,self.em,self.wp):self.assertIn("affiliate",s.lower())
    def test_no_guarantees(self):
        for s in (self.md,self.txt,self.em):
            for b in ("guaranteed cure","clinically proven","buy now before midnight","100% effective"):self.assertNotIn(b,s.lower())

if __name__=="__main__":unittest.main()
