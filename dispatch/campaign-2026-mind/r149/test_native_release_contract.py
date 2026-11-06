import unittest
from native_release_contract import (ISSUES,REQUIRED_ALL,REQUIRED_MERCHANT,gate,
                                     evaluate_campaign,confirmed_signup,human_net_revenue_metric)

class ContractTests(unittest.TestCase):
    def test_six(self):self.assertEqual(len(evaluate_campaign({})),6)
    def test_mix(self):self.assertEqual(list(ISSUES.values()).count('editorial'),4);self.assertEqual(list(ISSUES.values()).count('commercial'),2)
    def test_default_hold(self):self.assertTrue(all('HOLD' in x.state for x in evaluate_campaign({})))
    def test_all_true_still_hold(self):
        d={k:True for k in REQUIRED_ALL+REQUIRED_MERCHANT}
        self.assertTrue(all('HOLD' in x.state for x in evaluate_campaign(d)))
    def test_commercial_never_unblocked(self):
        for n in (3,5):self.assertEqual(gate(n,{}).state,'HOLD_MERCHANT_AND_UNSENT')
    def test_editorial_no_merchant_requirements(self):
        self.assertNotIn('email_promotion_rights',gate(1,{}).blocked)
    def test_merchant_requires_email_rights(self):self.assertIn('email_promotion_rights',gate(3,{}).blocked)
    def test_merchant_requires_near_disclosure(self):self.assertIn('near_cta_disclosure_reviewed',gate(5,{}).blocked)
    def test_release_requires_address(self):self.assertIn('valid_publisher_postal_address',gate(2,{}).blocked)
    def test_release_requires_unsub(self):self.assertIn('working_unsubscribe_verified',gate(4,{}).blocked)
    def test_no_side_effects(self):self.assertTrue(all(d.sends==0 and d.subscribers_changed==0 for d in evaluate_campaign({})))
    def test_invalid_issue(self):
        for x in (0,7,True,'3'):
            with self.assertRaises(ValueError):gate(x,{})
    def test_missing_evidence_type(self):
        with self.assertRaises(TypeError):gate(1,[])
    def test_ui_success_not_provider(self):self.assertFalse(confirmed_signup({}, {'subscribe':'success'}))
    def test_unverified_provider(self):self.assertFalse(confirmed_signup({'provider':'jetpack_native','subscription_state':'confirmed','independently_verified':False}))
    def test_valid_synthetic_evidence_is_not_a_real_lead(self):
        e={'provider':'jetpack_native','subscription_state':'confirmed','consent_scope':'dispatch_newsletter',
           'independently_verified':True,'record_reference':'opaque-provider-ref:synthetic-test-123'}
        self.assertTrue(confirmed_signup(e)) # validator test only, never counted as a real signup
    def test_no_zero_assumption_for_missing_revenue(self):self.assertIsNone(human_net_revenue_metric(None,None))
    def test_clicks_are_not_sessions(self):self.assertIsNone(human_net_revenue_metric({'clicks':100},{'settled_orders':1}))
    def test_missing_settlement(self):self.assertIsNone(human_net_revenue_metric({'qualified_human_sessions':100,'independently_verified':True},{}))
    def test_valid_synthetic_math(self):
        a={'qualified_human_sessions':100,'independently_verified':True}
        b={'settled_orders':2,'gross_revenue_cents':5000,'refunds_cents':1000,'fees_cents':500,'independently_verified':True}
        self.assertEqual(human_net_revenue_metric(a,b),350.0)
    def test_tiny_sample_no_bogus_denominator(self):self.assertIsNone(human_net_revenue_metric({'qualified_human_sessions':0,'independently_verified':True},{'independently_verified':True,'settled_orders':0,'gross_revenue_cents':0,'refunds_cents':0,'fees_cents':0}))

if __name__=='__main__':unittest.main()
