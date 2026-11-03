"""R78 synthetic + exact count regression; no recipient addresses or sends."""
import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]/"r78-audience-cross-api"
spec=importlib.util.spec_from_file_location("r78_audit",ROOT/"audit.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class R78CrossApiGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads((ROOT/"source_snapshot.json").read_text(encoding="utf-8"))
    def data(self):return copy.deepcopy(self.source)
    def test_source_reconstructs_20261102_snapshot(self):
        a=self.data()
        self.assertEqual(a["newsletter_status"]["total"],2)
        self.assertEqual(a["newsletter_status"]["confirmed"],2)
        self.assertEqual(a["newsletter_status"]["unconfirmed"],2)
        self.assertEqual(a["jetpack_followers"]["email"],0)
        self.assertEqual(a["jetpack_followers"]["wpcom"],2)
    def test_cross_api_disagreement_is_not_zero_recipients(self):
        r=m.report(self.data())
        self.assertTrue(r["newsletter_status_vs_followers_email_mismatch"])
        self.assertIsNone(r["eligible_recipients"])
        self.assertIn("NOT_PROOF_OF_ZERO",r["interpretation"])
    def test_not_four_and_not_two(self):
        r=m.report(self.data())
        self.assertNotEqual(r["eligible_recipients"],4)
        self.assertNotEqual(r["eligible_recipients"],2)
    def test_not_zero(self):self.assertIsNone(m.report(self.data())["eligible_recipients"])
    def test_when_counters_match_still_no_audience_proof(self):
        s=self.data();s["jetpack_followers"].update({"email":2,"wpcom":0,"total":2})
        r=m.report(s)
        self.assertFalse(r["newsletter_status_vs_followers_email_mismatch"])
        self.assertIsNone(r["eligible_recipients"])
    def test_even_private_count_does_not_permit_send(self):
        s=self.data()
        s["private_operator_attestations"]["email_subscribed_and_sending_count"]=2
        for k in s["private_operator_attestations"]:
            if s["private_operator_attestations"][k] is False:s["private_operator_attestations"][k]=True
        s["named_product_permissions"]={"zen12_email":True,"total_focus_email":True}
        r=m.report(s)
        self.assertFalse(r["send_authorized"])
        self.assertEqual(r["campaign_status"],"HOLD_UNSENT")
    def test_both_merchant_holds(self):
        r=m.report(self.data())
        self.assertEqual(r["offer_03"],"HOLD_MERCHANT")
        self.assertEqual(r["offer_05"],"HOLD_MERCHANT")
    def test_no_tracking_or_email_in_snapshot(self):
        t=(ROOT/"source_snapshot.json").read_text()
        self.assertNotIn("@",t)
        self.assertNotIn("token",t.lower())
    def test_reject_unknown_root_pii(self):
        s=self.data();s["subscriber_email"]="secret@example.com"
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_nesting_pii(self):
        s=self.data();s["jetpack_followers"]["recipient"]="secret@example.com"
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_extra_partner_url(self):
        s=self.data();s["named_product_permissions"]["tracking_url"]="https://example.com/?private=1"
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_boolean_counts(self):
        s=self.data();s["newsletter_status"]["total"]=True
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_negative_counts(self):
        s=self.data();s["jetpack_followers"]["email"]=-1
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_bad_follower_aggregation(self):
        s=self.data();s["jetpack_followers"]["total"]=4
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_wrong_sender(self):
        s=self.data();s["newsletter_settings"]["from_name"]="unknown"
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_string_boolean(self):
        s=self.data();s["private_operator_attestations"]["founder_final_send_approval"]="true"
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_invalid_verified_count(self):
        s=self.data();s["private_operator_attestations"]["email_subscribed_and_sending_count"]="2"
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_missing_named_product(self):
        s=self.data();del s["named_product_permissions"]["total_focus_email"]
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_invalid_source_provenance(self):
        s=self.data();s["observed_source"]="somewhere"
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_reject_wrong_schema(self):
        s=self.data();s["schema"]="send-yes"
        with self.assertRaises(m.EvidenceError):m.report(s)
    def test_html_accessible_no_script_no_recipient(self):
        h=m.html_report(m.report(self.data()))
        self.assertIn('lang="en"',h)
        self.assertIn("<caption>",h)
        self.assertIn("HOLD_UNSENT",h)
        self.assertNotIn("<script",h)
        self.assertNotRegex(h, r"[A-Za-z0-9_.+\\-]+@[A-Za-z0-9.\\-]+\\.[A-Za-z]{2,}")
    def test_report_text_makes_no_send_claim(self):
        t=m.text_report(m.report(self.data()))
        self.assertIn("HOLD_UNSENT",t)
        self.assertIn("not 0, not 2, not 4",t)
        self.assertNotIn("@",t)
    def test_cli_outputs_hard_hold(self):
        p=subprocess.run([sys.executable,str(ROOT/"audit.py"),"--format","json"],capture_output=True,text=True,check=True)
        r=json.loads(p.stdout)
        self.assertFalse(r["send_authorized"])
        self.assertIsNone(r["eligible_recipients"])
    def test_cli_fails_closed_and_redacts_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=pathlib.Path(tmp)/"test.json"
            s=self.data();s["private_email"]="private@example.com"
            path.write_text(json.dumps(s))
            p=subprocess.run([sys.executable,str(ROOT/"audit.py"),"--input",str(path)],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertNotIn("private@example.com",p.stderr)
    def test_guide_readonly_and_4_to_2(self):
        t=(ROOT/"RUNBOOK.md").read_text(encoding="utf-8")
        for phrase in ("four editorial", "two commercial", "HOLD_UNSENT", "HOLD_MERCHANT"):
            self.assertIn(phrase,t)
    def test_live_snapshot_never_authorizes_preview(self):
        r=m.report(self.data())
        self.assertFalse(r["previewed_jetpack_email"])
        self.assertFalse(r["received_jetpack_email_verified"])
        self.assertFalse(r["unsubscribe_verified"])
    def test_generated_html_no_purchase_link(self):
        h=m.html_report(m.report(self.data()))
        self.assertNotIn("zen12.com",h)
        self.assertNotIn("hypnosislive.com",h)
        self.assertNotIn("Buy now",h)

if __name__=="__main__":
    unittest.main()
