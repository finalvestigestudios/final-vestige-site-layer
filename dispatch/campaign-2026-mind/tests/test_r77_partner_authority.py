"""Adversarial tests for R77's public-only partner/channel proof ledger."""
import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1] / "r77-partner-authority"
S = importlib.util.spec_from_file_location("r77_readiness", ROOT / "readiness.py")
mod = importlib.util.module_from_spec(S)
S.loader.exec_module(mod)

class R77AuthorityGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed = json.loads((ROOT / "evidence_snapshot.json").read_text(encoding="utf-8"))
    def case(self):
        return copy.deepcopy(self.seed)
    def test_latest_snapshot_is_all_false(self):
        s=self.case()
        self.assertFalse(any(s["common_gates"].values()))
        for entry in s["offers"].values():
            self.assertFalse(any(entry[g] for g in mod.OFFER_GATES))
    def test_six_original_issues_still_held(self):
        r=mod.report(self.case())
        self.assertEqual([x["number"] for x in r["issues"]],list(mod.ORDER))
        self.assertTrue(all(x["release_status"]=="HOLD_UNSENT" for x in r["issues"]))
    def test_two_commercial_four_editorial(self):
        r=mod.report(self.case())
        self.assertEqual(sum(x["classification"]=="commercial" for x in r["issues"]),2)
        self.assertEqual(sum(x["classification"]=="editorial" for x in r["issues"]),4)
    def test_product_specific_holds(self):
        r=mod.report(self.case())
        self.assertEqual(r["offers"]["zen12"]["review_status"],"HOLD_MERCHANT")
        self.assertEqual(r["offers"]["total_focus"]["review_status"],"HOLD_MERCHANT")
    def test_total_is_not_four(self):
        r=mod.report(self.case())
        self.assertEqual(r["reported_subscriber_total"],2)
        self.assertTrue(r["nonadditive_subscriber_counts"])
        self.assertIsNone(r["email_eligible_count"])
    def test_no_invented_buyer_metrics(self):
        self.assertNotIn("sales",mod.report(self.case()))
        self.assertNotIn("conversion_rate",mod.report(self.case()))
    def test_send_never_authorized(self):
        self.assertIs(mod.report(self.case())["send_authorized"], False)
    def test_even_true_attestations_do_not_authorize(self):
        s=self.case()
        for key in s["common_gates"]: s["common_gates"][key]=True
        for entry in s["offers"].values():
            for key in mod.OFFER_GATES:entry[key]=True
        r=mod.report(s)
        self.assertIs(r["send_authorized"],False)
        self.assertEqual(r["campaign_status"],"HOLD_UNSENT")
        self.assertEqual(r["offers"]["zen12"]["review_status"],"HOLD_EXTERNAL_AUTHENTICITY")
    def test_future_guide_does_not_unlock_other_offer(self):
        s=self.case()
        s["offers"]["zen12"]["published_guide_url_verified"]=True
        r=mod.report(s)
        self.assertIn("published_guide_url_verified",r["offers"]["total_focus"]["unverified_gates"])
        self.assertEqual(r["offers"]["total_focus"]["review_status"],"HOLD_MERCHANT")
    def test_product_email_gate_not_inherited(self):
        s=self.case()
        s["offers"]["zen12"]["email_channel_permission"]=True
        r=mod.report(s)
        self.assertIn("email_channel_permission",r["offers"]["total_focus"]["unverified_gates"])
    def test_partner_flag_is_not_email_permission(self):
        s=self.case()
        s["offers"]["zen12"]["partner_accepted"]=True
        self.assertIn("email_channel_permission",mod.report(s)["offers"]["zen12"]["unverified_gates"])
    def test_no_email_addresses_in_source(self):
        raw=(ROOT/"evidence_snapshot.json").read_text(encoding="utf-8")
        self.assertNotIn("@",raw)
        self.assertNotIn("http",raw)
        self.assertNotIn("token",raw.lower())
    def test_schema_rejects_extra_recipient_key(self):
        s=self.case()
        s["subscriber_email"]="private@example.com"
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_schema_rejects_unexpected_link(self):
        s=self.case()
        s["offers"]["zen12"]["affiliate_url"]="https://example.com/?token=x"
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_schema_rejects_extra_buyer_data(self):
        s=self.case()
        s["offers"]["zen12"]["buyer_name"]="unapproved"
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_schema_rejects_missing_common_gate(self):
        s=self.case()
        del s["common_gates"]["working_unsubscribe"]
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_schema_rejects_missing_product(self):
        s=self.case()
        del s["offers"]["total_focus"]
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_schema_rejects_wrong_product_issue(self):
        s=self.case()
        s["offers"]["total_focus"]["issue"]="03"
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_schema_rejects_wrong_product_pr(self):
        s=self.case()
        s["offers"]["zen12"]["draft_pr"]=692
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_schema_rejects_wrong_blob(self):
        s=self.case()
        s["offers"]["zen12"]["guide_blob"]="0"*40
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_schema_rejects_string_boolean(self):
        s=self.case()
        s["common_gates"]["founder_send_approval"]="true"
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_schema_rejects_integer_as_boolean(self):
        s=self.case()
        s["offers"]["zen12"]["partner_accepted"]=1
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_rejects_negative_counts(self):
        s=self.case()
        s["newsletter"]["counts"]["confirmed"]=-1
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_rejects_bool_counts(self):
        s=self.case()
        s["newsletter"]["counts"]["confirmed"]=False
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_rejects_nondated_evidence(self):
        s=self.case()
        s["observed_utc"]="recently"
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_rejects_fake_schema(self):
        s=self.case()
        s["schema"]="send-approved"
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_rejects_improper_sender(self):
        s=self.case()
        s["newsletter"]["sender_name"]="Other sender"
        with self.assertRaises(mod.EvidenceError):mod.report(s)
    def test_text_is_redacted_and_holds(self):
        out=mod.plain(mod.report(self.case()))
        self.assertIn("HOLD_UNSENT",out)
        self.assertIn("UNKNOWN",out)
        self.assertNotIn("@",out)
        self.assertNotIn("http",out)
    def test_html_accessible_safe(self):
        out=mod.html_report(mod.report(self.case()))
        self.assertIn('lang="en"',out)
        self.assertIn('name="viewport"',out)
        self.assertIn("<caption>",out)
        self.assertIn("HOLD_UNSENT",out)
        self.assertNotIn("<script",out)
        self.assertNotIn("http",out)
    def test_cli_can_render_json_privately(self):
        p=subprocess.run([sys.executable,str(ROOT/"readiness.py"),"--format","json"],capture_output=True,text=True,check=True)
        obj=json.loads(p.stdout)
        self.assertFalse(obj["send_authorized"])
        self.assertIsNone(obj["email_eligible_count"])
        self.assertNotIn("@",p.stdout)
    def test_cli_invalid_input_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            target=pathlib.Path(temp)/"attest.json"
            x=self.case();x["recipient"]="private@example.com"
            target.write_text(json.dumps(x),encoding="utf-8")
            p=subprocess.run([sys.executable,str(ROOT/"readiness.py"),"--input",str(target)],
                             capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertNotIn("private@example.com",p.stderr)
    def test_static_reviewer_has_no_active_merchant_cta(self):
        page=(ROOT/"REVIEWER.html").read_text(encoding="utf-8")
        self.assertIn("HOLD_UNSENT",page)
        self.assertIn("HOLD_MERCHANT",page)
        self.assertNotIn("zen12.com/getstarted",page)
        self.assertNotIn("hypnosislive.com/mental-skills/total-focus",page)
        self.assertNotIn("<script",page)
    def test_static_reviewer_mentions_no_native_email_receipt(self):
        page=(ROOT/"REVIEWER.html").read_text(encoding="utf-8")
        self.assertIn("NOT a received Jetpack email",page)
        self.assertIn("Final Vestige",page)

if __name__ == "__main__":
    unittest.main()
