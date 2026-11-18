import unittest
from decimal import Decimal
from audience_contract import AuditError, reconcile, confirmed_signup_transition, release_decision, revenue_per_1000

N={'total':3,'confirmed':3,'unconfirmed':2}
S={'all_total':3,'email_eligible':3,'unconfirmed_total':2}
F={'total':3,'email':0,'wpcom':3,'partial':False}
I=[{'type': t, 'founder_selected':False} for t in ('editorial','editorial','commercial','editorial','commercial','editorial')]

class ReconciliationTests(unittest.TestCase):
    def test_live_counts_distinct_not_five(self):
        a=reconcile(N,S,F); self.assertEqual(a['confirmed_email_eligible_records'],3); self.assertEqual(a['unconfirmed_records_excluded'],2)
    def test_follower_email_zero_does_not_override_three_subscribers(self):
        a=reconcile(N,S,F); self.assertTrue(a['source_count_disagreement']); self.assertIsNone(a['proven_new_external_leads'])
    def test_partial_follower_feed_rejected(self):
        with self.assertRaises(AuditError): reconcile(N,S,{**F,'partial':True})
    def test_mismatched_unconfirmed_rejected(self):
        with self.assertRaises(AuditError): reconcile(N,{**S,'unconfirmed_total':4},F)
    def test_mismatched_confirmed_rejected(self):
        with self.assertRaises(AuditError): reconcile({**N,'confirmed':2},S,F)
    def test_eligible_gt_total_rejected(self):
        with self.assertRaises(AuditError): reconcile(N,{**S,'email_eligible':4},F)
    def test_negative_or_float_rejected(self):
        with self.assertRaises(AuditError): reconcile({**N,'total':3.0},S,F)
    def test_existing_subscriber_not_new(self):
        self.assertFalse(confirmed_signup_transition({'status':'Subscribed','email_subscriber':True},{'status':'Subscribed','email_subscriber':True},{'provider_confirmation_record':True,'timestamped_first_confirmation':True}))
    def test_confirmed_transition_requires_provider_proof(self):
        self.assertFalse(confirmed_signup_transition({'status':'Not confirmed','email_subscriber':True},{'status':'Subscribed','email_subscriber':True},{}))
    def test_real_confirmed_transition_only(self):
        self.assertTrue(confirmed_signup_transition({'status':'Not confirmed','email_subscriber':True},{'status':'Subscribed','email_subscriber':True},{'provider_confirmation_record':True,'timestamped_first_confirmation':True}))
    def test_reader_only_excluded(self):
        self.assertFalse(confirmed_signup_transition(None,{'status':'Subscribed','email_subscriber':False},{'newly_created_provider_record':True,'provider_confirmation_record':True,'timestamped_first_confirmation':True}))
    def test_new_signup_needs_new_provider_record(self):
        self.assertFalse(confirmed_signup_transition(None,{'status':'Subscribed','email_subscriber':True},{'provider_confirmation_record':True,'timestamped_first_confirmation':True}))
    def test_six_hold_with_no_approvals(self):
        r=release_decision(I,{}); self.assertTrue(r['all_held']); self.assertEqual([i['type'] for i in r['issues']].count('commercial'),2)
    def test_cannot_recast_issue_five_as_editorial(self):
        with self.assertRaises(AuditError): release_decision([*I[:4],{'type':'editorial'},I[5]],{})
    def test_editorial_gates_do_not_need_merchant_proof(self):
        p={k:True for k in ('founder_final_send_approval','native_jetpack_preview_witness','verified_publisher_postal','rendered_functional_unsubscribe','consent_and_delivery_evidence')}
        j=[{**x,'founder_selected':True} for x in I];r=release_decision(j,p);self.assertEqual(r['issues'][0]['release'],'REVIEW_ELIGIBLE_NOT_SENT');self.assertEqual(r['issues'][2]['release'],'HOLD_UNSENT')
    def test_no_revenue_without_denominator(self):
        self.assertIsNone(revenue_per_1000(None,[])); self.assertIsNone(revenue_per_1000(0,[]))
    def test_missing_ledger_is_unknown_not_zero(self):
        self.assertIsNone(revenue_per_1000(200,None))
    def test_click_as_payment_rejected(self):
        with self.assertRaises(AuditError): revenue_per_1000(100,[{'status':'clicked','gross':2,'fees':0,'refunds':0,'independently_reported':True}],denominator_verified=True,ledger_verified=True)
    def test_verified_zero_vs_unknown(self):
        self.assertIsNone(revenue_per_1000(100,[])); self.assertEqual(revenue_per_1000(100,[],denominator_verified=True,ledger_verified=True),Decimal('0.00'))
    def test_valid_net_settlement(self):
        self.assertEqual(revenue_per_1000(200,[{'status':'settled','gross':'15','fees':'2','refunds':'3','independently_reported':True}],denominator_verified=True,ledger_verified=True),Decimal('50.00'))
    def test_missing_fee_rejected(self):
        with self.assertRaises(AuditError): revenue_per_1000(100,[{'status':'settled','gross':15,'refunds':0,'independently_reported':True}],denominator_verified=True,ledger_verified=True)

if __name__=='__main__': unittest.main()
