"""Native Python tests use synthetic fake records only, not subscriber PII."""
import unittest
from decimal import Decimal
from contract import snapshot_counts, new_confirmed_signup, release_reasons, net_per_1000


class AcceptanceTests(unittest.TestCase):
    def test_live_provider_bucket_math(self):
        self.assertEqual(snapshot_counts(dict(total=3, confirmed=3, unconfirmed=2, email_subscribed=3))["confirmed_email_eligible"], 3)

    def test_unconfirmed_not_falsely_totaled(self):
        self.assertEqual(snapshot_counts(dict(total=3, confirmed=3, unconfirmed=2, email_subscribed=3))["unconfirmed_excluded"], 2)

    def test_leads_not_inferred_from_inventory(self):
        self.assertIsNone(snapshot_counts(dict(total=3, confirmed=3, unconfirmed=2, email_subscribed=3))["independent_new_leads"])

    def test_reject_impossible_buckets(self):
        with self.assertRaises(ValueError):
            snapshot_counts(dict(total=3, confirmed=4, unconfirmed=2, email_subscribed=4))

    def test_reject_boolean_count(self):
        with self.assertRaises(ValueError):
            snapshot_counts(dict(total=True, confirmed=1, unconfirmed=0, email_subscribed=1))

    def test_real_provider_transition_only(self):
        witness = dict(origin="jetpack_provider", same_private_recipient=True, timestamp="2026-11-18T12:00Z")
        self.assertTrue(new_confirmed_signup(dict(status="Unconfirmed"), dict(status="Subscribed", email_subscriber=True), witness))
        self.assertFalse(new_confirmed_signup(dict(status="Subscribed", email_subscriber=True), dict(status="Subscribed", email_subscriber=True), witness))

    def test_browser_click_not_confirmation(self):
        self.assertFalse(new_confirmed_signup({}, dict(status="Subscribed", email_subscriber=True), dict(origin="cta_click", same_private_recipient=True, timestamp="t")))

    def test_reader_only_not_confirmation(self):
        self.assertFalse(new_confirmed_signup({}, dict(status="Subscribed", email_subscriber=False), dict(origin="jetpack_provider", same_private_recipient=True, timestamp="t")))

    def test_release_closed_without_proofs(self):
        self.assertIn("founder_final_campaign_approval", release_reasons(1, {"campaign_status":"HOLD_UNSENT"}))
        self.assertIn("email_channel_permission", release_reasons(3, {"campaign_status":"HOLD_UNSENT"}))

    def test_synthetic_all_true_still_no_send_action(self):
        from contract import SHARED_GATES, MERCHANT_GATES
        proofs={k:True for k in SHARED_GATES + MERCHANT_GATES}
        proofs.update(campaign_status="HOLD_UNSENT", merchant_product="Zen12")
        self.assertEqual(release_reasons(3, proofs), [])  # only a human review candidate; never a send API

    def test_wrong_merchant_name_rejected(self):
        self.assertIn("wrong_canonical_product", release_reasons(5, dict(campaign_status="HOLD_UNSENT",merchant_product="Total Focus")))

    def test_reject_unknown_issue(self):
        with self.assertRaises(ValueError): release_reasons(7, {})

    def test_non_audited_sessions_yield_unknown(self):
        self.assertIsNone(net_per_1000(dict(qualified_human_sessions=5, human_sessions_audited=False, settlement_report_verified=True)))

    def test_click_not_settlement(self):
        c=dict(qualified_human_sessions=10,human_sessions_audited=True,settlement_report_verified=True, window_days=7,source_window="W",settlement_window="W",orders=[dict(status="clicked",merchant_report_verified=True,commission="10",refunds="0",fees="0")])
        self.assertIsNone(net_per_1000(c))

    def test_synthetic_settled_calculation(self):
        c=dict(qualified_human_sessions=100,human_sessions_audited=True,settlement_report_verified=True, window_days=7,source_window="W",settlement_window="W",orders=[dict(status="settled",merchant_report_verified=True,commission="9.00",refunds="1.00",fees="2.00")])
        self.assertEqual(net_per_1000(c), Decimal("60.00"))

    def test_negative_and_nonfinite_rejected(self):
        c=dict(qualified_human_sessions=100,human_sessions_audited=True,settlement_report_verified=True, window_days=30,source_window="W",settlement_window="W",orders=[dict(status="settled",merchant_report_verified=True,commission="NaN",refunds="0",fees="0")])
        self.assertIsNone(net_per_1000(c))

    def test_window_mismatch_rejected(self):
        self.assertIsNone(net_per_1000(dict(qualified_human_sessions=100,human_sessions_audited=True,settlement_report_verified=True, window_days=7, source_window="A", settlement_window="B", orders=[])))

if __name__ == "__main__":
    unittest.main()
