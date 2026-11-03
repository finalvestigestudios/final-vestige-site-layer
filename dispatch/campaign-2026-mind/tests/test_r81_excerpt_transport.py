"""R81 independently enforces static transport-copy truth, not actual delivery or legal compliance."""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIR = ROOT / "r81-transport-truth"

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        for name,value in attrs:
            if tag=="a" and name=="href": self.hrefs.append(value)

class R81TransportTruth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obj=json.loads((DIR/"ISSUE-CARDS.json").read_text(encoding="utf-8"))
        cls.cards=cls.obj["cards"]
        cls.html=(DIR/"PREVIEW.html").read_text(encoding="utf-8")
        cls.txt=(DIR/"PREVIEW.txt").read_text(encoding="utf-8")
        cls.audit=(DIR/"TRANSPORT-AND-LEGAL-AUDIT.md").read_text(encoding="utf-8")
        cls.parser=Anchors(); cls.parser.feed(cls.html)
    def test_six_issue_cards(self):
        self.assertEqual([r["id"] for r in self.cards],["01","02","03","04","05","06"])
    def test_exact_mix(self):
        self.assertEqual([r["id"] for r in self.cards if r["kind"]=="editorial"],["01","02","04","06"])
        self.assertEqual([r["id"] for r in self.cards if r["kind"]=="commercial_reserved"],["03","05"])
    def test_master_unmodified(self):
        self.assertEqual(self.obj["master_pr"],175)
        self.assertEqual(self.obj["parent_pr"],715)
        self.assertEqual(self.obj["status"],"HOLD_UNSENT")
        self.assertTrue(self.obj["review_only"])
    def test_no_release_gates_open(self):
        self.assertGreaterEqual(len(self.obj["release_gates"]),12)
        self.assertTrue(all(v is False for v in self.obj["release_gates"].values()))
    def test_no_commercial_destination(self):
        for r in self.cards:
            if r["kind"]=="commercial_reserved":
                self.assertIsNone(r["destination"])
                self.assertIn("RESERVED",r["cta"])
                self.assertIn("unpublished",r["cta"])
    def test_only_public_editorial_destination(self):
        for r in self.cards:
            if r["kind"]=="editorial":
                self.assertTrue(r["destination"].startswith("https://finalvestige.com/"))
                self.assertNotIn("utm_",r["destination"])
    def test_each_excerpt_short_and_readable(self):
        for r in self.cards:
            self.assertGreaterEqual(len(r["excerpt"].split()),32)
            self.assertLessEqual(len(r["excerpt"].split()),55)
            self.assertLessEqual(len(r["excerpt"]),350)
    def test_preheader_not_claimed_as_native(self):
        self.assertEqual(self.obj["custom_preheader_supported"],"UNVERIFIED")
        self.assertIn("UNVERIFIED AS JETPACK FIELD",self.txt)
    def test_commercial_disclosure_first(self):
        for r in self.cards:
            if r["kind"]=="commercial_reserved":
                self.assertTrue(r["excerpt"].startswith("Commercial disclosure:"))
                self.assertIn("may earn a commission",r["excerpt"].split(".")[0])
                self.assertIn("No buying link is active",r["excerpt"])
    def test_commercial_source_urls_not_active_destinations(self):
        self.assertNotIn("https://zen12.com/hnp",self.parser.hrefs)
        self.assertNotIn("https://hypnosislive.com/mental-skills/total-focus",self.parser.hrefs)
        for url in self.parser.hrefs:
            self.assertFalse(re.search(r"(?:zen12|hypnosislive|inspire3|bit\.ly)",url,re.I),url)
    def test_safe_static_review(self):
        self.assertNotIn("script",self.parser.tags)
        self.assertNotIn("form",self.parser.tags)
        self.assertNotIn("iframe",self.parser.tags)
        self.assertNotIn("img",self.parser.tags)
        self.assertIn('lang="en"',self.html)
        self.assertIn('name="viewport"',self.html)
        self.assertIn('class="skip"',self.html)
    def test_html_accessible_all_issues(self):
        for r in self.cards:
            self.assertIn('id="issue-'+r["id"]+'"',self.html)
            self.assertIn(r["subject"].replace("'","&#39;") if False else r["subject"].replace("&","&amp;"),self.html)
    def test_plaintext_all_excerpts_verbatim(self):
        for r in self.cards:
            self.assertIn(r["excerpt"],self.txt)
            self.assertIn(r["primary_source"],self.txt)
    def test_transport_snapshot_current_and_conservative(self):
        s=self.obj["production_snapshot"]
        self.assertEqual(s["email_content_format"],"excerpt")
        self.assertFalse(s["automatic_new_post_emails"])
        self.assertEqual(s["recent_sends"],0)
        self.assertEqual(s["eligible_recipients"],"UNKNOWN")
        self.assertEqual(s["reply_to"],"no-reply")
    def test_counters_never_added(self):
        s=self.obj["production_snapshot"]["counts"]
        self.assertEqual(s,{"newsletter_total":2,"newsletter_confirmed":2,"newsletter_unconfirmed":2,"followers_email":0,"followers_wpcom":2})
    def test_welcome_not_proven_received(self):
        s=self.obj["production_snapshot"]
        self.assertTrue(s["welcome_52_page_fieldbook_configured"])
        self.assertFalse(s["welcome_actual_receipt_verified"])
    def test_both_signup_pages_same_list_but_different_claims(self):
        s=self.obj["production_snapshot"]
        self.assertTrue(s["dispatch_page_published"] and s["focus_page_published"])
        self.assertFalse(s["dispatch_signup_mentions_possible_affiliate_recommendations"])
        self.assertTrue(s["focus_signup_mentions_possible_affiliate_recommendations"])
    def test_merchant_sources_specific(self):
        byid={r["id"]:r for r in self.cards}
        self.assertEqual(byid["03"]["primary_source"],"https://zen12.com/hnp")
        self.assertEqual(byid["05"]["primary_source"],"https://hypnosislive.com/mental-skills/total-focus")
    def test_live_editorial_sources_not_seller_spam(self):
        for r in self.cards:
            self.assertTrue(r["primary_source"].startswith("https://"))
            self.assertFalse(r["subject"].lower().startswith(("buy","free gift","guaranteed")))
    def test_audit_distinguishes_preview_vs_test_send(self):
        self.assertIn("Preview email",self.audit)
        self.assertIn("Send test email",self.audit)
        self.assertIn("requires authorization",self.audit)
    def test_audit_address_and_unsub_require_verification(self):
        for phrase in ("qualifying physical postal address","actual opt-out","no-reply","Automattic"):
            self.assertIn(phrase,self.audit)
    def test_audit_merchant_email_rights_required(self):
        self.assertIn("email-promotion",self.audit)
        self.assertIn("No approved tracked link",self.audit)
    def test_audit_notes_no_real_mail(self):
        for phrase in ("NOT established","UNKNOWN","No campaigns should be reported"):
            self.assertIn(phrase,self.audit)
    def test_no_personal_data_or_live_tracking(self):
        blob=self.html+self.txt+(DIR/"ISSUE-CARDS.json").read_text(encoding="utf-8")
        self.assertNotRegex(blob,r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
        self.assertNotRegex(blob,r"https?://[^\s\"<>]*[?&](?:token|key|utm_source|aff_id)=")
    def test_no_html_unsafe_merchant_link(self):
        self.assertNotIn("mailto:",self.html)
        self.assertNotIn("pixel",self.html.lower())
    def test_every_offer_first_350_chars(self):
        for r in self.cards:
            if r["kind"]=="commercial_reserved":
                self.assertLess(r["excerpt"].find("may earn a commission"),100)
    def test_disclosures_do_not_misstate_approval(self):
        self.assertEqual(self.obj["merchant_permissions"],"UNVERIFIED")
        self.assertFalse(self.obj["commercial_destinations_published"])
    def test_snapshot_does_not_claim_real_preview(self):
        self.assertIn("NOT A RECEIVED JETPACK EMAIL",self.html)
        self.assertIn("NOT A RECEIVED JETPACK EMAIL",self.txt)
        self.assertIn("HOLD_UNSENT",self.html)
if __name__ == "__main__": unittest.main()
