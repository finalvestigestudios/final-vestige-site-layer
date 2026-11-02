"""R69 trust-preserving source-controlled tests. Never contact network/list."""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parents[1]
DOCS=["README.md","release_brief.md","subscriber-privacy.md","merchant-authorization.md","received-mail-check.md"]
class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__();self.tags=[];self.attrs=[] 
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag);self.attrs.extend(attrs)
class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/"release_choices.json").read_text(encoding="utf-8"))
        cls.docs={x:(ROOT/x).read_text(encoding="utf-8") for x in DOCS}
        cls.html=(ROOT/"review.html").read_text(encoding="utf-8")
    def test_six_roles(self):
        self.assertEqual(len(self.data["issues"]),6)
        self.assertEqual([x["id"] for x in self.data["issues"]],list(range(1,7)))
        self.assertEqual(sum(i["role"]=="editorial" for i in self.data["issues"]),4)
        self.assertEqual(sum(i["role"]=="commercial-reserved" for i in self.data["issues"]),2)
    def test_source_immutable(self):
        self.assertEqual(self.data["original_sha"],"d57ccdba3aee8f065e143e101c2945f4f3d01647")
        self.assertEqual(self.data["parent_sha"],"4068e3feaa50aee8174d0f169e9bd05aa3a2c42f")
        self.assertFalse(self.data["founder_final_version_approved"])
        self.assertTrue(all(x["final_approved_blob"] is None for x in self.data["issues"]))
    def test_channel_no_send(self):
        self.assertFalse(self.data["word_press"]["automatic_new_posts"])
        self.assertEqual(self.data["word_press"]["email_content_format"],"excerpt")
        self.assertIsNone(self.data["delivery_method_approved"])
        self.assertFalse(self.data["final_send_approved"])
        self.assertFalse(self.data["newsletter_send_authorized"])
    def test_subscriber_nonadditive(self):
        sub=self.data["word_press"]["subscriber_counts"]
        self.assertEqual((sub["total"],sub["confirmed"],sub["unconfirmed"]),(2,2,2))
        self.assertIsNone(self.data["word_press"]["actual_unique_email_eligible"])
        self.assertIsNone(self.data["word_press"]["all_time_send_count"])
        self.assertIn("Subscribed",self.docs["subscriber-privacy.md"])
    def test_received_email_not_verified(self):
        wp=self.data["word_press"]
        for field in ("welcome_received_verified","native_preview_verified","received_mime_verified","valid_publisher_postal_address_verified","unsubscribe_verified"):
            self.assertFalse(wp[field],field)
    def test_no_activated_commission(self):
        for i in self.data["issues"]:
            self.assertTrue(i["release"].startswith("HOLD_UNSENT"))
            if i["role"]=="commercial-reserved":
                self.assertIsNone(i["cta"])
                self.assertIsNone(i["verified_earning_url"])
                self.assertFalse(i["guide_live_approved"])
                self.assertFalse(i["email_channel_permission"])
                self.assertFalse(i["merchant_affiliate_approval"])
        self.assertFalse(self.data["tracking_enabled"])
    def test_no_fake_business_data(self):
        for k in ("actual_open_rate","actual_conversion_rate","actual_revenue"):
            self.assertIsNone(self.data[k])
        self.assertFalse(self.data["subscriber_pii_included"])
    def test_apollo_conflict(self):
        four=self.data["issues"][3]
        self.assertIn("Fourteen",four["subject_original"])
        self.assertIn("Seventeen",four["subject_stacked"])
        self.assertIn("nonnumeric",self.docs["release_brief.md"])
    def test_user_informed(self):
        for x in ("preheader","excerpt","HOLD_UNSENT","approved","postal","unsubscribe","WordPress"):
            self.assertTrue(any(x.lower() in s.lower() for s in self.docs.values()),x)
    def test_html_safe(self):
        self.assertIn('lang="en"',self.html)
        self.assertIn('name="viewport"',self.html)
        self.assertIn(":focus-visible",self.html)
        p=LinkParser();p.feed(self.html)
        self.assertNotIn("script",p.tags)
        for ban in ("iframe","form","input","img","video","audio","button"):
            self.assertNotIn(ban,p.tags)
        links=[v for k,v in p.attrs if k=="href"]
        self.assertTrue(all(not any(t in (v or "").lower() for t in ["zen12.com","hypnosislive.com","?utm_","mailto:"]) for v in links))
    def test_text_no_secret(self):
        corpus="\n".join(self.docs.values())+self.html
        for x in ("sk_live_","AKIA","eyJhbGciOi","https://wordpress.com/email-unsubscribe/"):
            self.assertNotIn(x,corpus)
    def test_public_source_links(self):
        d=self.docs
        self.assertIn("https://wordpress.com/support/subscribers/",d["subscriber-privacy.md"])
        self.assertIn("https://zen12.com/hnp",d["merchant-authorization.md"])
        self.assertIn("https://hypnosislive.com/mental-skills/total-focus",d["merchant-authorization.md"])
        self.assertIn("https://www.ftc.gov/",d["received-mail-check.md"])
    def test_release_both_hold(self):
        for n in (3,5):
            self.assertIn("HOLD_MERCHANT",self.data["issues"][n-1]["release"])
        self.assertTrue(all("HOLD_MERCHANT" not in self.data["issues"][n-1]["release"] for n in (1,2,4,6)))
    def test_no_future_claim(self):
        self.assertFalse(self.data["word_press"]["welcome_received_verified"])
        self.assertIn("NOT AUTHORIZED",self.docs["received-mail-check.md"])
        self.assertIn("not native python execution",self.docs["README.md"].lower())
if __name__=="__main__":unittest.main()
