"""Native CPython regression and mutation tests for R171's non-sending contract."""
import copy
import unittest
from dispatch_truth_gate import inspect

SAMPLE = {
  "newsletter_settings": {"subscriptions": True, "email_new_posts_by_default": False,
      "welcome_message": "Your 52 page guide: Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf"},
  "newsletter_status": {"subscribers": {"total":3,"confirmed":3,"unconfirmed":2},
      "recent_sends": [{"status":"never_sent_opted_out","post_id":1926}]},
  "pages": {
    "dispatch": {"raw":"<!-- wp:jetpack/subscriptions /-->",
                 "rendered":"<a href='https://finalvestige.com/?post_type=page&p=523'>Subscribe</a>"},
    "focus": {"raw":"var q=new URLSearchParams(window.location.search).get('subscribe');if(q){show();} var c='is-subscriber';new MutationObserver(check);"}},
  "proof":{"subscriber_email":"MUST NEVER BE REFLECTED", "email_permission":True}
}

class TruthGateTests(unittest.TestCase):
    def report(self, data=None): return inspect(copy.deepcopy(data or SAMPLE))
    def f(self,r,name): return next(x["status"] for x in r["findings"] if x["code"]==name)
    def test_release_is_hold(self): self.assertEqual(self.report()["release"],"HOLD_UNSENT")
    def test_commercial_both_held(self):
        r=self.report();self.assertEqual(r["commercial_issue_03"],"HOLD_MERCHANT");self.assertEqual(r["commercial_issue_05"],"HOLD_MERCHANT")
    def test_six_issues_preserved(self): self.assertEqual(self.report()["allocation"],{"editorial":4,"commercial":2})
    def test_settings_configuration_only(self): self.assertEqual(self.f(self.report(),"NEWSLETTER_CONFIG"),"PASS_CONFIG_ONLY")
    def test_auto_send_disabled(self): self.assertEqual(self.f(self.report(),"POST_AUTO_SEND"),"PASS")
    def test_auto_send_on_is_failure(self):
        s=copy.deepcopy(SAMPLE);s["newsletter_settings"]["email_new_posts_by_default"]=True
        self.assertEqual(self.f(self.report(s),"POST_AUTO_SEND"),"FAIL")
    def test_native_wp_block_present(self): self.assertEqual(self.f(self.report(),"DISPATCH_NATIVE_BLOCK"),"PASS_SOURCE")
    def test_native_wp_block_missing(self):
        s=copy.deepcopy(SAMPLE);s["pages"]["dispatch"]["raw"]=""
        self.assertEqual(self.f(self.report(s),"DISPATCH_NATIVE_BLOCK"),"FAIL")
    def test_rendered_self_link_needs_browser(self): self.assertEqual(self.f(self.report(),"DISPATCH_RENDERED_GUEST_FORM"),"BROWSER_CHECK_REQUIRED")
    def test_focus_unsafe_success_recognized(self): self.assertEqual(self.f(self.report(),"FOCUS_FALSE_SUCCESS"),"REPRODUCIBLE_SOURCE_RISK")
    def test_focus_source_removed_no_false_pass(self):
        s=copy.deepcopy(SAMPLE);s["pages"]["focus"]["raw"]="safe placeholder"
        self.assertEqual(self.f(self.report(s),"FOCUS_FALSE_SUCCESS"),"NOT_SEEN_IN_EXCERPT")
    def test_welcome_config_only(self): self.assertEqual(self.f(self.report(),"WELCOME_PDF_CONFIG"),"PASS_CONFIG_ONLY")
    def test_welcome_missing(self):
        s=copy.deepcopy(SAMPLE);s["newsletter_settings"]["welcome_message"]="empty"
        self.assertEqual(self.f(self.report(s),"WELCOME_PDF_CONFIG"),"FAIL")
    def test_counts_not_added(self):
        r=self.report();self.assertEqual(r["counted_subscribers"],3);self.assertEqual(r["unconfirmed_pending"],2)
        self.assertIsNone(r["email_eligible_recipients"])
    def test_no_personal_data_echo(self): self.assertNotIn("MUST NEVER BE REFLECTED",str(self.report()))
    def test_false_permission_not_promoted(self): self.assertEqual(self.f(self.report(),"NAMED_MERCHANT_EMAIL_PERMISSION"),"NOT_VERIFIED")
    def test_paid_conversion_not_inferred(self): self.assertEqual(self.report()["net_revenue_per_1000_qualified_sessions"],"NOT_COMPUTABLE")
    def test_never_sent_scope(self): self.assertEqual(self.f(self.report(),"RECENT_SEND_EVIDENCE"),"NEVER_SENT_REPORTED")
    def test_missing_snapshot_fails_closed(self):
        r=self.report({"newsletter_settings":{},"pages":{},"newsletter_status":{}})
        self.assertEqual(self.f(r,"NEWSLETTER_CONFIG"),"FAIL")
        self.assertEqual(r["release"],"HOLD_UNSENT")
    def test_synthetic_green_does_not_release(self):
        s=copy.deepcopy(SAMPLE)
        s["proof"]={k:True for k in ["native_email_eligibility","received_welcome","jetpack_native_preview","publisher_postal","functional_unsubscribe","named_email_permission","approved_affiliate_link","approved_live_guide","paid_settlement"]}
        self.assertEqual(self.report(s)["release"],"HOLD_UNSENT")
        self.assertEqual(self.f(self.report(s),"PUBLISHER_POSTAL_ADDRESS"),"NOT_VERIFIED")

if __name__ == "__main__": unittest.main()
