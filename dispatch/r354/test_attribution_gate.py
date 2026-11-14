import unittest
import copy
from attribution_gate import *

SOCIAL={'utm_source':'youtube','utm_medium':'organic_social','utm_campaign':'mind_pilot_2026_11','utm_content':'actual_yt_0042','asset_id':'actual_yt_0042','topic_cluster':'mind','publication_time':'2026-11-01T16:00:00Z','owner_verified_asset':True,'rights_qa_reference':'actual-source-record','public_post_url':'https://youtube.com/watch?v=actualasset','fv_landing_url':'https://finalvestige.com/focus/'}
SIGN={'provider':'jetpack','event_type':'subscription_confirmed','newsletter_permission':True,'unsubscribed':False,'consent_proof_ref':'opaque-proof','provider_confirmation_id':'confirmation_1234'}
MAIL={'utm_source':'dispatch','utm_medium':'email','utm_campaign':'dispatch_pilot_2026_11','utm_content':'issue_03','approved_live_cta':True,'founder_send_approval':True,'actually_delivered':True}
ORDER={'merchant_attested':True,'settlement_status':'settled','order_status':'paid','currency':'USD','order_token':'order_12345678','gross_cents':10000,'fees_cents':1000,'refund_cents':1000}

class GateTests(unittest.TestCase):
    def test_social_valid_is_only_qa_eligible(self): self.assertEqual(social_touch(SOCIAL).state,'QA_ELIGIBLE')
    def test_source_unknown(self): self.assertEqual(social_touch({**SOCIAL,'utm_source':'threads'}).state,'HOLD')
    def test_alias_social_rejected(self): self.assertIn('NONCANONICAL_SOCIAL_MEDIUM',social_touch({**SOCIAL,'utm_medium':'social'}).reasons)
    def test_paid_social_rejected(self): self.assertEqual(social_touch({**SOCIAL,'utm_medium':'paid_social'}).state,'HOLD')
    def test_wrong_campaign_month(self): self.assertEqual(social_touch({**SOCIAL,'utm_campaign':'mind_pilot_2026_12'}).state,'HOLD')
    def test_wrong_topic(self): self.assertEqual(social_touch({**SOCIAL,'topic_cluster':'productivity'}).state,'HOLD')
    def test_asset_mismatch(self): self.assertIn('ASSET_ID_MISMATCH',social_touch({**SOCIAL,'utm_content':'other_asset_id'}).reasons)
    def test_asset_approval_required(self): self.assertEqual(social_touch({**SOCIAL,'owner_verified_asset':False}).state,'HOLD')
    def test_asset_rights_required(self): self.assertEqual(social_touch({**SOCIAL,'rights_qa_reference':''}).state,'HOLD')
    def test_no_timestamp(self): self.assertEqual(social_touch({**SOCIAL,'publication_time':None}).state,'HOLD')
    def test_external_landing(self): self.assertEqual(social_touch({**SOCIAL,'fv_landing_url':'https://elsewhere.example/'}).state,'HOLD')
    def test_personal_url_params(self): self.assertEqual(social_touch({**SOCIAL,'fv_landing_url':'https://finalvestige.com/focus/?email=x'}).state,'HOLD')
    def test_no_social_evidence(self): self.assertEqual(social_touch(None).state,'HOLD')
    def test_counts_overlapping(self):
        v=provider_counts({'total':3,'confirmed':3,'unconfirmed':2,'wpcom_followers':3,'email_followers':0})
        self.assertEqual(v.state,'DIAGNOSTIC_ONLY');self.assertIsNone(v.details['eligible_recipients']);self.assertIn('OVERLAPPING_OR_INCONSISTENT_CATEGORIES',v.reasons)
    def test_counts_add_up_still_not_eligible(self): self.assertIsNone(provider_counts({'total':5,'confirmed':3,'unconfirmed':2,'wpcom_followers':3,'email_followers':0}).details['eligible_recipients'])
    def test_count_boolean_not_integer(self): self.assertEqual(provider_counts({'total':True,'confirmed':3,'unconfirmed':2,'wpcom_followers':3,'email_followers':0}).state,'HOLD')
    def test_signup_first_and_duplicate(self):
        seen=set(); self.assertEqual(confirmed_signup(SIGN,seen).state,'ACCEPT_ONE_CONFIRMED_LEAD');self.assertEqual(confirmed_signup(SIGN,seen).state,'HOLD')
    def test_signup_unconfirmed(self): self.assertEqual(confirmed_signup({**SIGN,'event_type':'subscription_requested'},set()).state,'HOLD')
    def test_signup_no_permission(self): self.assertEqual(confirmed_signup({**SIGN,'newsletter_permission':False},set()).state,'HOLD')
    def test_signup_unsubscribed(self): self.assertEqual(confirmed_signup({**SIGN,'unsubscribed':True},set()).state,'HOLD')
    def test_signup_missing_proof(self): self.assertEqual(confirmed_signup({**SIGN,'consent_proof_ref':''},set()).state,'HOLD')
    def test_signup_leaks_email(self): self.assertIn('PII_IN_ANALYTICS_EVENT',confirmed_signup({**SIGN,'email':'not-publish@example.test'},set()).reasons)
    def test_signup_wrong_provider(self): self.assertEqual(confirmed_signup({**SIGN,'provider':'mailchimp'},set()).state,'HOLD')
    def test_email_touch_valid_only_after_send(self): self.assertEqual(email_touch(MAIL).state,'ATTRIBUTABLE_LAST_TOUCH')
    def test_email_touch_needs_delivery(self): self.assertEqual(email_touch({**MAIL,'actually_delivered':False}).state,'HOLD')
    def test_email_touch_needs_permission(self): self.assertEqual(email_touch({**MAIL,'founder_send_approval':False}).state,'HOLD')
    def test_email_touch_rejects_social_medium(self): self.assertEqual(email_touch({**MAIL,'utm_medium':'social'}).state,'HOLD')
    def test_email_touch_invalid_issue(self): self.assertEqual(email_touch({**MAIL,'utm_content':'issue_07'}).state,'HOLD')
    def test_settled_order(self): self.assertEqual(paid_outcome(ORDER).state,'SETTLED_RECEIPT')
    def test_unsettled_order(self): self.assertEqual(paid_outcome({**ORDER,'settlement_status':'pending'}).state,'HOLD')
    def test_checkout_is_not_sale(self): self.assertEqual(paid_outcome({**ORDER,'order_status':'checkout_started'}).state,'HOLD')
    def test_wrong_currency(self): self.assertEqual(paid_outcome({**ORDER,'currency':'EUR'}).state,'HOLD')
    def test_negative_fees(self): self.assertEqual(paid_outcome({**ORDER,'fees_cents':-1}).state,'HOLD')
    def test_order_email_leak(self): self.assertEqual(paid_outcome({**ORDER,'customer_email':'fake@example.test'}).state,'HOLD')
    def test_no_real_sessions(self): self.assertEqual(revenue_per_1000(None,[ORDER],True).state,'NOT_COMPUTABLE')
    def test_nonsettled_does_not_compute(self): self.assertEqual(revenue_per_1000(100,[{**ORDER,'settlement_status':'pending'}],True).state,'NOT_COMPUTABLE')
    def test_duplicate_orders_do_not_compute(self): self.assertEqual(revenue_per_1000(100,[ORDER,copy.copy(ORDER)],True).state,'NOT_COMPUTABLE')
    def test_no_attestation(self): self.assertEqual(revenue_per_1000(100,[ORDER]).state,'NOT_COMPUTABLE')
    def test_net_rate_math_fixture_only(self):
        v=revenue_per_1000(100,[ORDER],True);self.assertEqual(v.details['net_revenue_per_1000_usd'],'800.00');self.assertTrue(v.details['tiny_sample'])
    def test_every_edition_held_even_if_gates_given(self):
        for i in range(1,7):self.assertEqual(edition_hold(i,{}).state,'HOLD_UNSENT')
    def test_commercial_extra_gates(self):
        self.assertIn('email_promotion_rights',edition_hold(3).reasons);self.assertIn('email_promotion_rights',edition_hold(5).reasons)
        self.assertNotIn('email_promotion_rights',edition_hold(4).reasons)
    def test_no_fake_issue_seven(self):self.assertEqual(edition_hold(7).state,'HOLD')
    def test_no_last_touch_claim_without_proof(self):self.assertEqual(email_touch(None).state,'HOLD')

if __name__ == '__main__': unittest.main()
