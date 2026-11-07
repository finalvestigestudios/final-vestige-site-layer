import unittest
from consent_gate import evaluate

class FailClosed(unittest.TestCase):
    def setUp(self):
        self.base = {'provider_evidence': {'source': 'Jetpack Subscribers filtered Email subscription=Subscribed',
              'email_subscription_status':'Subscribed','eligible_recipient_count': 2,
              'authorized_read_only_review': True, 'deduplicated_by_provider':True},
             'received_fieldbook_welcome':True,
             'legal':{'actual_jetpack_preview_reviewed':True,'valid_fv_physical_postal_address_in_received_email':True,'working_unsubscribe_in_received_email':True},
             'founder_final_campaign_approval':True,
             'merchant': {k:True for k in ('named_fv_affiliate_acceptance','email_channel_permission',
                    'exact_issued_earning_link','buyer_guide_published_and_verified',
                    'seller_terms_checkout_verified','product_claims_qualified','near_link_disclosure_reviewed')},
             'settled_sale':{'source':'verified_affiliate_partner_report', 'order_reconciled':True,
                     'refunds_fees_reconciled':True,'merchant_identity_and_payout_verified':True},
             'qualified_human_sessions':50,'qualified_sessions_independently_validated':True}

    def test_empty_is_hold(self):
        a=evaluate({});self.assertEqual(a.audience,'UNKNOWN');self.assertEqual(a.commercial,'HOLD_MERCHANT_UNSENT')
    def test_aggregates_do_not_prove_email_consent(self):
        self.assertEqual(evaluate({'total':3,'confirmed':3,'unconfirmed':2,'wpcom_followers':3,'email_followers':0}).audience,'UNKNOWN')
    def test_only_reader_follower_is_not_email(self):
        a={**self.base,'provider_evidence':{'source':'Reader','email_subscription_status':'Not subscribed','eligible_recipient_count':3}};self.assertEqual(evaluate(a).audience,'UNKNOWN')
    def test_not_confirmed_not_email(self):
        a={**self.base,'provider_evidence':{**self.base['provider_evidence'],'email_subscription_status':'Not confirmed'}};self.assertEqual(evaluate(a).audience,'UNKNOWN')
    def test_zero_email_suppresses(self):
        a={**self.base,'provider_evidence':{**self.base['provider_evidence'],'eligible_recipient_count':0}};self.assertEqual(evaluate(a).audience,'UNKNOWN')
    def test_bool_is_not_integer(self):
        a={**self.base,'provider_evidence':{**self.base['provider_evidence'],'eligible_recipient_count':True}};self.assertEqual(evaluate(a).audience,'UNKNOWN')
    def test_browser_success_cannot_prove_signup(self):
        self.assertEqual(evaluate({'subscribe':'confirmed','pdf_panel_visible':True}).audience,'UNKNOWN')
    def test_welcome_missing_blocks_editorial(self):
        a={**self.base,'received_fieldbook_welcome':False};self.assertEqual(evaluate(a).editorial,'HOLD_UNSENT')
    def test_footer_missing_blocks_editorial(self):
        a={**self.base,'legal':{**self.base['legal'],'working_unsubscribe_in_received_email':False}};self.assertEqual(evaluate(a).editorial,'HOLD_UNSENT')
    def test_authorization_missing_blocks_commercial_only(self):
        a={**self.base,'merchant':{**self.base['merchant'],'email_channel_permission':False}};g=evaluate(a);self.assertEqual(g.editorial,'REVIEW_ONLY');self.assertEqual(g.commercial,'HOLD_MERCHANT_UNSENT')
    def test_guide_missing_blocks_commercial_only(self):
        a={**self.base,'merchant':{**self.base['merchant'],'buyer_guide_published_and_verified':False}};self.assertEqual(evaluate(a).commercial,'HOLD_MERCHANT_UNSENT')
    def test_founder_approval_missing_blocks_all(self):
        a={**self.base,'founder_final_campaign_approval':False};self.assertEqual(evaluate(a).editorial,'HOLD_UNSENT')
    def test_click_does_not_prove_sale(self):
        a={**self.base,'settled_sale':{'source':'outbound_click','order_reconciled':True,'refunds_fees_reconciled':True}};self.assertEqual(evaluate(a).revenue,'NOT_COMPUTABLE')
    def test_human_sessions_must_be_independently_verified(self):
        a={**self.base,'qualified_sessions_independently_validated':False};self.assertEqual(evaluate(a).revenue,'NOT_COMPUTABLE')
    def test_complete_synthetic_fixture_is_review_only(self):
        g=evaluate(self.base);self.assertEqual(g.audience,'EMAIL_ELIGIBLE_AGGREGATE_REVIEWED');self.assertEqual(g.commercial,'REVIEW_ONLY');self.assertEqual(g.revenue,'RECONCILABLE_ONLY')

if __name__ == '__main__':unittest.main()
