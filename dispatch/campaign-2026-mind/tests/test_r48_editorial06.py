"""R48 optional Pepys diary 06 source-only, no send authorization."""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/"r48-pepys-06"
CTA="https://finalvestige.com/focus/"
ADDR="[[VALID_POSTAL_ADDRESS_REQUIRED]]"
UNSUB="[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"
SUBJECT="He saw the fire. Then he went back to bed."
class LinkParser(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.h1=0; self.h2=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="a":self.links.append(a)
        if tag=="h1":self.h1+=1
        if tag=="h2":self.h2+=1
class R48(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md=(D/"candidate06.md").read_text(encoding="utf-8")
        cls.txt=(D/"candidate06.txt").read_text(encoding="utf-8")
        cls.em=(D/"candidate06-email.html").read_text(encoding="utf-8")
        cls.wp=(D/"candidate06-gutenberg.blocks.html").read_text(encoding="utf-8")
        cls.board=(D/"reviewer.html").read_text(encoding="utf-8")
        cls.doc=(D/"jetpack_delivery_decision.md").read_text(encoding="utf-8")
        cls.r=json.loads((D/"claim_register.json").read_text(encoding="utf-8"))
        cls.prod=json.loads((D/"read_only_20261101.json").read_text(encoding="utf-8"))
        cls.links=LinkParser();cls.links.feed(cls.em)
    def test_files(self):
        for p in ("candidate06.md","candidate06.txt","candidate06-email.html","candidate06-gutenberg.blocks.html","claim_register.json","read_only_20261101.json","jetpack_delivery_decision.md","reviewer.html","REVIEW_FIRST.md"):
            self.assertTrue((D/p).exists());self.assertGreater((D/p).stat().st_size,200)
    def test_parent(self):self.assertEqual(self.r["source_parent_sha"],"dd150154139d34c757fb111702c3ef1f180ca136")
    def test_hold(self):self.assertEqual(self.r["status"],"HOLD_UNSENT_OPTIONAL_ED06")
    def test_original_unchanged(self):self.assertTrue(self.r["canonical_six_issues_unchanged"])
    def test_founder_substitution_false(self):self.assertFalse(self.r["founder_approved_substitution"])
    def test_no_wp(self):self.assertFalse(self.r["wordpress_post_created"])
    def test_no_email(self):self.assertFalse(self.r["email_sent"])
    def test_no_receipt(self):self.assertFalse(self.r["real_received_email"])
    def test_no_jetpack_native(self):self.assertFalse(self.r["actual_jetpack_email_preview"])
    def test_no_verified_postal(self):self.assertFalse(self.r["mailing_address_verified"])
    def test_no_verified_unsub(self):self.assertFalse(self.r["unsubscribe_verified"])
    def test_no_verified_audience(self):self.assertFalse(self.r["consent_eligible_audience_reconciled"])
    def test_kind(self):self.assertEqual(self.r["kind"],"editorial")
    def test_four_two_hold(self):self.assertEqual(self.r["original_campaign_commercial_slots"],[3,5])
    def test_word_count(self):self.assertGreaterEqual(self.r["story_word_count"],600)
    def test_subject_all(self):
        for s in (self.md,self.txt,self.em,self.wp):self.assertIn(SUBJECT,s)
    def test_preview_proposal(self):
        for s in (self.md,self.txt,self.em):self.assertIn("A diary from 1666 shows why seeing, hearing and recording are three different things.",s)
    def test_non_native_preheader(self):self.assertTrue(self.r["proposed_preheader_not_jetpack_native"])
    def test_excerpt_uninstalled(self):self.assertTrue(self.r["proposed_custom_excerpt_not_installed"])
    def test_one_button(self):
        c=[x for x in self.links.links if x.get("class")=="fv-primary-cta"]
        self.assertEqual(len(c),1);self.assertEqual(c[0].get("href"),CTA)
    def test_first_party_cta(self):self.assertEqual(self.r["primary_cta_url"],CTA);self.assertEqual(self.r["primary_cta_wordpress_page_id"],1579)
    def test_no_merchant(self):
        for s in (self.md,self.txt,self.em,self.wp):
            for x in ("zen12.com","hypnosislive.com","inspire3.com","utm_source=","clickbank","javascript:"):self.assertNotIn(x,s.lower())
    def test_no_revenue(self):self.assertEqual(self.r["affiliate_links"],0)
    def test_legal_hold(self):
        for s in (self.md,self.txt,self.em,self.wp):self.assertIn(ADDR,s);self.assertIn(UNSUB,s)
    def test_no_scripts(self):
        for x in ("<script","<form","<img","<iframe","<video","<style","srcset="):self.assertNotIn(x,self.em.lower())
    def test_accessible_html(self):
        self.assertEqual(self.links.h1,1);self.assertGreater(self.links.h2,1);self.assertIn('lang="en"',self.em);self.assertIn('role="presentation"',self.em)
    def test_source_count(self):self.assertEqual(len(self.r["sources"]),5)
    def test_sources_in_html(self):
        for e in self.r["sources"]:self.assertIn(e["url"],self.em)
    def test_sources_https(self):
        for u in [s["url"] for s in self.r["sources"]]+[CTA]:self.assertEqual(urlparse(u).scheme,"https")
    def test_claim_count(self):self.assertEqual(len(self.r["evidence"]),6)
    def test_diary_framing(self):
        for s in (self.md,self.txt):self.assertIn("do not",s.lower());self.assertIn("exact hour",s.lower())
    def test_bmj_precision(self):
        for s in (self.md,self.txt):self.assertIn("90 percent",s);self.assertIn("11 percent",s);self.assertIn("20 percent",s)
    def test_no_generalized_bmj_claim(self):
        for s in (self.md,self.txt,self.em,self.wp):
            self.assertIn("These numbers do not measure memory accuracy in the general population.",s)
            self.assertNotIn("89 percent of everyone's memories are false",s)
    def test_no_mental_health_hype(self):
        for s in (self.md,self.txt,self.em):
            for x in ("100% effective","cures anxiety","guaranteed results","one hour in twelve minutes"):self.assertNotIn(x,s.lower())
    def test_snapshot_excerpt(self):self.assertEqual(self.prod["email_content_format"],"excerpt")
    def test_snapshot_no_auto(self):self.assertFalse(self.prod["email_new_posts_by_default"])
    def test_snapshot_nonadditive(self):self.assertEqual(self.prod["counters"],{"total":2,"confirmed":2,"unconfirmed":2});self.assertIsNone(self.prod["unique_eligible_people"])
    def test_snapshot_not_lifetime(self):self.assertTrue(self.prod["zero_lifetime_sends_not_established"])
    def test_snapshot_welcome_not_received(self):self.assertFalse(self.prod["welcome_receipt_verified"])
    def test_snapshot_merchant_not_ready(self):self.assertFalse(self.prod["commercial_email_permitted"]);self.assertFalse(self.prod["live_guides_for_03_05"])
    def test_docs_55_words_and_350_ambiguity(self):self.assertIn("55 words",self.doc);self.assertIn("350-character",self.doc);self.assertIn("could **not** be independently verified",self.doc)
    def test_docs_real_email_needed(self):self.assertIn("actual received MIME",self.doc);self.assertIn("NOT EXECUTED",self.doc)
    def test_not_actually_sent_in_review(self):self.assertIn("HOLD_UNSENT",self.board)
if __name__=="__main__":unittest.main()
