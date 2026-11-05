"""Native regression tests for truthful subscriber and send-state diagnostics."""
import copy
import unittest
from wp_status_audit import analyze


def payloads():
    settings = {"success": True,"action": "get_settings","blog_id": 256784396,
        "site_url": "https://finalvestige.com","as_of": "2026-11-05T12:32:30+00:00",
        "settings": {"subscriptions": True,"email_new_posts_by_default": False,
                     "email_content_format": "excerpt", "welcome_message": "Welcome, private user address: private@example.com"}}
    status = {"success": True,"action": "status","blog_id": 256784396,
        "site_url": "https://finalvestige.com","as_of": "2026-11-05T12:32:36+00:00",
        "site_can_send": True,
        "subscribers": {"total": 3,"confirmed": 3,"unconfirmed": 2,"suppressed": 0,
                        "paid": 0,"imported_last_24h": 1},
        "recent_sends": [{"post_id": 1926,"title": "private@example.com", "status": "never_sent_opted_out"}]}
    return settings, status


class TruthTests(unittest.TestCase):
    def setUp(self):
        self.s, self.t = payloads()

    def audit(self):
        return analyze(self.s,self.t)

    def test_current_configuration(self):
        r=self.audit(); self.assertTrue(r["newsletter_enabled"]); self.assertFalse(r["auto_send_default_enabled"])

    def test_excerpts_not_proven_delivered(self):
        r=self.audit(); self.assertEqual(r["delivery_format"],"excerpt"); self.assertIn("EXCERPT_CTA_RISK",str(r["warnings"]))

    def test_counts_never_additive(self):
        r=self.audit();self.assertEqual(r["aggregate_counters"]["total"],3);self.assertIn("NON_ADDITIVE_COUNTERS",str(r["warnings"]))

    def test_import_counter_not_identity(self):
        r=self.audit();self.assertEqual(r["aggregate_counters"]["imported_last_24h"],1);self.assertIn("REQUIRES_PRIVATE_RECONCILIATION",str(r["warnings"]))

    def test_zero_import_no_flag(self):
        self.t["subscribers"]["imported_last_24h"]=0;self.assertNotIn("IMPORT_ACTIVITY",str(self.audit()["warnings"]))

    def test_zero_delivery_proof(self):
        self.assertIn("NO_DELIVERY_PROOF",str(self.audit()["warnings"]))

    def test_send_status_does_not_prove_receipt(self):
        self.t["recent_sends"][0]["status"]="sent";self.assertIn("NOT_INBOX_RECEIPT",str(self.audit()["warnings"]))

    def test_email_recipients_are_unknown(self):
        self.assertIsNone(self.audit()["verified_email_recipients"])

    def test_confirmed_signup_events_unknown(self):
        self.assertIsNone(self.audit()["confirmed_signup_events"])

    def test_commercial_hold(self):
        r=self.audit();self.assertIn("MERCHANT",r["issue_decisions"]["03"]);self.assertIn("MERCHANT",r["issue_decisions"]["05"])

    def test_other_four_hold_unsent(self):
        r=self.audit();self.assertEqual([k for k,v in r["issue_decisions"].items() if v=="HOLD_UNSENT"],["01","02","04","06"])

    def test_no_revenue_derived(self):
        r=self.audit();self.assertIsNone(r["verified_paid_orders"]);self.assertIsNone(r["net_revenue_per_1000_qualified_sessions"])

    def test_holds_even_if_site_can_send(self):
        self.assertEqual(self.audit()["release_decision"],"HOLD_UNSENT")

    def test_source_leaks_no_pii(self):
        import json
        self.assertNotIn("private@example.com",json.dumps(self.audit()))

    def test_ignores_arbitrary_extra_pii_fields(self):
        import json
        self.t["subscribers"]["emails"]=["sensitive@example.com"];self.assertNotIn("sensitive@example.com",json.dumps(self.audit()))

    def test_wrong_site_rejected(self):
        self.t["site_url"]="https://example.net";self.assertRaises(ValueError,self.audit)

    def test_site_mismatch_rejected(self):
        self.t["blog_id"]=-1;self.assertRaises(ValueError,self.audit)

    def test_boolean_counter_rejected(self):
        self.t["subscribers"]["total"]=True;self.assertRaises(ValueError,self.audit)

    def test_negative_counter_rejected(self):
        self.t["subscribers"]["total"]=-3;self.assertRaises(ValueError,self.audit)

    def test_missing_counter_rejected(self):
        del self.t["subscribers"]["unconfirmed"];self.assertRaises(ValueError,self.audit)

    def test_invalid_settings_action_rejected(self):
        self.s["action"]="update_settings";self.assertRaises(ValueError,self.audit)

    def test_invalid_status_action_rejected(self):
        self.t["action"]="subscriber_import";self.assertRaises(ValueError,self.audit)

    def test_naive_time_rejected(self):
        self.t["as_of"]="2026-11-05T12:30:00";self.assertRaises(ValueError,self.audit)

    def test_missing_send_status_rejected(self):
        del self.t["recent_sends"][0]["status"];self.assertRaises(ValueError,self.audit)

    def test_partial_responses_rejected(self):
        self.s["success"]=False;self.assertRaises(ValueError,self.audit)

    def test_copied_input_unchanged(self):
        original=(copy.deepcopy(self.s),copy.deepcopy(self.t)); self.audit();self.assertEqual((self.s,self.t),original)

    def test_full_mode_still_needs_received_preview(self):
        self.s["settings"]["email_content_format"]="full";r=self.audit();self.assertEqual(r["shared_release_gates"]["received_jetpack_email_preview"],"NOT_VERIFIED")

    def test_auto_send_true_warning_held(self):
        self.s["settings"]["email_new_posts_by_default"]=True;self.assertEqual(self.audit()["release_decision"],"HOLD_UNSENT")


if __name__=="__main__":
    unittest.main()
