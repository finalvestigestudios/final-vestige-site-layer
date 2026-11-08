"""R84 independent provenance and safety tests for the new live Issue 01 editorial CTA."""
import copy
import importlib.util
import json
import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/"r84-live-cta"
spec=importlib.util.spec_from_file_location("r84_route_audit",D/"route_audit.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
DATA=json.loads((D/"ROUTE-EVIDENCE.json").read_text(encoding="utf-8"))
MARKDOWN=(D/"ISSUE-01-ROUTE-PATCH.md").read_text(encoding="utf-8")
HTML=(D/"REVIEW.html").read_text(encoding="utf-8")
TXT=(D/"REVIEW.txt").read_text(encoding="utf-8")
README=(D/"README.md").read_text(encoding="utf-8")

class R84LiveCTAAudit(unittest.TestCase):
    def test_clean_data_passes(self):
        self.assertIn("HOLD_UNSENT",mod.validate(DATA))
    def test_master_not_replaced(self):
        self.assertEqual(DATA["source_control"]["master_pr"],175)
        self.assertEqual(DATA["source_control"]["stacked_parent_pr"],735)
        self.assertIn("NOT AN APPROVED REPLACEMENT",MARKDOWN)
    def test_issue_mix_four_two(self):
        self.assertEqual(DATA["campaign"]["mix"],{"editorial":["01","02","04","06"],"commercial_reserved":["03","05"]})
    def test_actual_live_post_source(self):
        self.assertEqual(DATA["live_pages"]["change_blindness"]["post_id"],1922)
        self.assertEqual(DATA["live_pages"]["change_blindness"]["status"],"publish")
        self.assertIn("Simons",MARKDOWN)
    def test_first_party_urls(self):
        self.assertEqual(len(DATA["issue01_cta_options"]),3)
        self.assertEqual(DATA["issue01_proposed"]["single_cta_url"],mod.EXPECTED_NEW_URL)
    def test_old_options_remain_live(self):
        self.assertEqual(DATA["live_pages"]["missing_caption"]["page_id"],1122)
        self.assertEqual(DATA["live_pages"]["puysegur"]["page_id"],1377)
    def test_no_send_or_approval(self):
        self.assertEqual(DATA["campaign"]["release"],"HOLD_UNSENT")
        self.assertFalse(DATA["campaign"]["founder_send_approval"])
        self.assertFalse(DATA["campaign"]["newsletter_test_send_approved"])
        self.assertFalse(DATA["campaign"]["mail_scheduled"])
    def test_original_demo_honesty(self):
        self.assertTrue(DATA["live_pages"]["change_blindness"]["interactive_test_requires_browser"])
        self.assertFalse(DATA["live_pages"]["change_blindness"]["original_lab_test_reproduction"])
        self.assertIn("not a replay",MARKDOWN.lower())
    def test_sender_and_subscriber_truth(self):
        self.assertEqual(DATA["channel"]["eligible_recipients"],"UNKNOWN")
        self.assertFalse(DATA["channel"]["auto_email_new_posts"])
        self.assertEqual(DATA["channel"]["email_content_format"],"excerpt")
    def test_law_gates_not_attested(self):
        self.assertFalse(DATA["channel"]["publisher_postal_verified"])
        self.assertFalse(DATA["channel"]["unsubscribe_rendered_and_tested"])
        self.assertFalse(DATA["channel"]["real_received_jetpack_email_verified"])
    def test_commmercial_holds_unverified(self):
        self.assertTrue(all(v is False for v in DATA["commercial_holds"].values()))
    def test_single_primary_cta(self):
        self.assertEqual(MARKDOWN.count("**One next step:**"),1)
        self.assertEqual(DATA["issue01_proposed"]["single_cta_text"],"Explore the change-blindness evidence and demo")
    def test_reviewer_has_accessibility(self):
        for fragment in ('lang="en"','<meta name="viewport"','<main','<h1','href="#main"','aria-labelledby=',':focus-visible'):
            self.assertIn(fragment,HTML)
    def test_reviewer_static_no_sending(self):
        for f in ("<script","<iframe","<form","?ref=","utm_", "mailto:"):
            self.assertNotIn(f,HTML.lower())
        self.assertIn("NOT A JETPACK EMAIL",HTML)
    def test_plaintext_preview_is_not_transport(self):
        self.assertIn("NOT A REAL JETPACK EMAIL",TXT)
        self.assertIn("HOLD_UNSENT",TXT)
    def test_no_private_recipient_data(self):
        for content in (HTML,TXT,README,MARKDOWN):
            self.assertNotRegex(content,r"(?i)[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}")
    def test_unobserved_not_zeroed(self):
        self.assertEqual(set(DATA["performance"].values()),{"UNOBSERVED"})
    def test_offline_report(self):
        out=mod.preview(DATA)
        self.assertIn(mod.EXPECTED_NEW_URL,out)
        self.assertIn("NOT A RECEIVED EMAIL",out)
        self.assertNotIn("SEND_APPROVED",out)
    def _bad(self,mutate):
        data=copy.deepcopy(DATA)
        mutate(data)
        with self.assertRaises(mod.EvidenceRejected):
            mod.validate(data)
    def test_reject_tracking(self):
        self._bad(lambda d:d["live_pages"]["change_blindness"].__setitem__("url",mod.EXPECTED_NEW_URL+"?utm_source=email"))
    def test_reject_merchant_host(self):
        self._bad(lambda d:d["issue01_cta_options"][2].__setitem__("destination","https://zen12.com/hnp"))
    def test_reject_fake_approval(self):
        self._bad(lambda d:d["campaign"].__setitem__("founder_send_approval",True))
    def test_reject_fake_email_recipient_count(self):
        self._bad(lambda d:d["channel"].__setitem__("eligible_recipients",2))
    def test_reject_sent_claim(self):
        self._bad(lambda d:d.__setitem__("actual_outbound_campaign_emails_sent",1))
    def test_reject_commercial_signoff(self):
        self._bad(lambda d:d["commercial_holds"].__setitem__("slot03_zen12_email_permission",True))
    def test_reject_dishonest_science(self):
        self._bad(lambda d:d["live_pages"]["change_blindness"].__setitem__("original_lab_test_reproduction",True))
    def test_reject_unauthorized_publication(self):
        self._bad(lambda d:d.__setitem__("analysis_not_publication",False))
    def test_reject_wrong_live_post_id(self):
        self._bad(lambda d:d["live_pages"]["change_blindness"].__setitem__("post_id",9999))
    def test_reject_fake_plaintext_delivery(self):
        self._bad(lambda d:d["channel"].__setitem__("real_received_jetpack_email_verified",True))
    def test_reject_unapproved_preheader(self):
        self._bad(lambda d:d["issue01_proposed"].__setitem__("preheader_status","NATIVE_VERIFIED"))
    def test_reject_synthetic_metrics(self):
        self._bad(lambda d:d["performance"].__setitem__("email_opens",3))

if __name__=="__main__":
    unittest.main()
