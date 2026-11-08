"""All tests synthetic. No WordPress calls, email sends or subscriber exports."""
import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from gate import (load_contract, net_revenue_per_thousand,
                  unique_confirmations, valid_asset_utm, validate_contract)


class ConsentAndCommerceGates(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()
        self.synthetic = dict(event="confirmed_signup", source="jetpack_authoritative_transition",
                              prior_state="unconfirmed", new_state="confirmed", consent_recorded=True,
                              site_id="fixture-site", internal_subscription_id="fixture-A", suppressed=False,
                              unsubscribed=False)

    def test_frozen_contract(self):
        self.assertEqual(validate_contract(self.contract), [])

    def test_fails_open_send(self):
        c = copy.deepcopy(self.contract)
        c["release"]["result"] = "READY"
        self.assertTrue(validate_contract(c))

    def test_must_preserve_4_to_2(self):
        c = copy.deepcopy(self.contract)
        c["source_campaign"]["editorial"] = 5
        self.assertTrue(validate_contract(c))

    def test_no_unverified_purchases(self):
        c = copy.deepcopy(self.contract)
        c["revenue_offer"]["paid_orders_reported"] = 1
        self.assertTrue(validate_contract(c))

    def test_no_inferred_lead(self):
        c = copy.deepcopy(self.contract)
        c["authoritative_confirmed_signup"]["count_from_form_submit"] = True
        self.assertTrue(validate_contract(c))

    def test_no_false_recipient_count(self):
        c = copy.deepcopy(self.contract)
        c["observed_state"]["reachable_recipient_count"] = 2
        self.assertTrue(validate_contract(c))

    def test_three_signup_attempts_not_a_confirmation(self):
        self.assertEqual(unique_confirmations([dict(event="signup_attempt") for _ in range(3)]), 0)

    def test_confirmed_transition_deduplicated(self):
        self.assertEqual(unique_confirmations([self.synthetic] * 3), 1)

    def test_out_of_order_confirmation_ignored(self):
        self.assertEqual(unique_confirmations([{**self.synthetic, "prior_state": "confirmed"}]), 0)

    def test_unsubscribed_or_suppressed_not_counted(self):
        self.assertEqual(unique_confirmations([{**self.synthetic, "unsubscribed": True},
                                               {**self.synthetic, "suppressed": True}]), 0)

    def test_unconfirmed_or_invalid_source_not_counted(self):
        self.assertEqual(unique_confirmations([{**self.synthetic, "new_state": "unconfirmed"},
                                               {**self.synthetic, "source": "client_form"}]), 0)

    def test_no_exported_id_required_in_response(self):
        count = unique_confirmations([self.synthetic])
        self.assertEqual(count, 1)
        self.assertIsInstance(count, int)

    def test_two_independent_confirmations(self):
        self.assertEqual(unique_confirmations([self.synthetic,
            {**self.synthetic, "internal_subscription_id": "fixture-B"}]), 2)

    def test_no_signup_without_consent_record(self):
        self.assertEqual(unique_confirmations([{**self.synthetic, "consent_recorded": False}]), 0)

    def test_valid_utm(self):
        self.assertTrue(valid_asset_utm(dict(utm_source="youtube", utm_medium="organic_social",
            utm_campaign="mind_pilot_2026_11", utm_content="grok-asset-0001")))

    def test_reject_unknown_platform(self):
        self.assertFalse(valid_asset_utm(dict(utm_source="telepathy", utm_medium="organic_social",
            utm_campaign="mind_pilot_2026_11", utm_content="asset-0001")))

    def test_reject_email_or_pii_as_asset(self):
        self.assertFalse(valid_asset_utm(dict(utm_source="youtube", utm_medium="organic_social",
            utm_campaign="mind_pilot_2026_11", utm_content="realperson@example.com")))

    def test_reject_unapproved_utm_campaign(self):
        self.assertFalse(valid_asset_utm(dict(utm_source="tiktok", utm_medium="organic_social",
            utm_campaign="buy_now", utm_content="asset-1234")))

    def test_unknown_sessions_is_not_zero_revenue_claim(self):
        self.assertIsNone(net_revenue_per_thousand(None, []))

    def test_unknown_orders_is_not_zero_revenue_claim(self):
        self.assertIsNone(net_revenue_per_thousand(100, None))

    def test_zero_sessions_returns_na(self):
        self.assertIsNone(net_revenue_per_thousand(0, []))

    def test_click_does_not_make_paid_order(self):
        self.assertIsNone(net_revenue_per_thousand(100, [dict(source="affiliate_outbound", payment_status="paid",
                                                            order_id="o-1", earned=5, fees=1, refunds=0)]))

    def test_valid_paid_receipt_in_synthetic_fixture(self):
        self.assertEqual(str(net_revenue_per_thousand(500, [dict(source="payhip_confirmed_paid_order",
                    payment_status="paid", refund_status="none", order_id="fixture-paid-1",
                    earned="20", fees="2", refunds="0")])), "36.00")

    def test_refund_deducted(self):
        self.assertEqual(str(net_revenue_per_thousand(1000, [dict(source="affiliate_confirmed_paid_conversion",
                    payment_status="paid", refund_status="partial", order_id="fixture-aff-1",
                    earned="10", fees="1", refunds="5")])), "4.00")

    def test_missing_refund_status_is_not_sufficient(self):
        self.assertIsNone(net_revenue_per_thousand(1000, [dict(source="payhip_confirmed_paid_order",
                    payment_status="paid", order_id="fixture-paid-1", earned=10, fees=0, refunds=0)]))

    def test_duplicate_order_is_not_double_counted(self):
        o=dict(source="payhip_confirmed_paid_order",payment_status="paid",refund_status="none",
               order_id="fixture-paid-1",earned=20,fees=2,refunds=0)
        self.assertIsNone(net_revenue_per_thousand(100, [o, o]))

    def test_negative_fee_rejected(self):
        self.assertIsNone(net_revenue_per_thousand(100, [dict(source="payhip_confirmed_paid_order",
                    payment_status="paid", refund_status="none", order_id="fixture-paid-1",
                    earned=10, fees=-1, refunds=0)]))

    def test_unsafe_asset_identifiers_rejected(self):
        a=dict(utm_source="youtube",utm_medium="organic_social",utm_campaign="mind_pilot_2026_11")
        for token in ["a b c d", "?uid=1234", "@jon", "ab", "abc@example.com", "a/b/c"]:
            self.assertFalse(valid_asset_utm({**a, "utm_content": token}))


if __name__ == "__main__":
    unittest.main()
