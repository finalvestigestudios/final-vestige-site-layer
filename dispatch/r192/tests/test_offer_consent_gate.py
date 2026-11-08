import sys, pathlib, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from offer_consent_gate import evaluate, confirmed_signup, dedup_confirmed, paid_conversion, safe_revenue_report, REQUIRED

REF='github-issue:174#comment-999999'

class R192Tests(unittest.TestCase):
    def test_all_six_are_unsent(self):
        for k in ('01','02','03','04','05','06'):
            with self.subTest(k=k):
                g=evaluate({},k)
                self.assertEqual(g['status'],'HOLD')
                self.assertFalse(g['send_authorized'])
    def test_4_2_mix(self):
        self.assertEqual(sum(evaluate({},str(i).zfill(2))['kind']=='commercial' for i in range(1,7)),2)
    def test_invalid_issue(self):
        with self.assertRaises(ValueError): evaluate({},'07')
    def test_booleans_not_evidence(self):
        self.assertEqual(evaluate({k:True for k in REQUIRED['common']},'01')['status'],'HOLD')
    def test_forged_placeholder(self):
        self.assertFalse(confirmed_signup({'event':'confirmed_signup','source':'jetpack_authoritative','state_before':'unconfirmed','state_after':'subscribed','evidence_ref':'placeholder','opaque_transition_id':'abcde12345abc'}))
    def test_editorial_can_be_candidate_not_authorized(self):
        x=evaluate({k:REF for k in REQUIRED['common']},'01')
        self.assertEqual(x['status'],'HUMAN_REVIEW_CANDIDATE_ONLY')
        self.assertFalse(x['send_authorized'])
    def test_commercial_extra_gate(self):
        x=evaluate({k:REF for k in REQUIRED['common']},'03')
        self.assertEqual(x['status'],'HOLD')
        self.assertEqual(set(x['missing']),set(REQUIRED['commercial']))
    def test_all_commercial_proofs_still_only_candidate(self):
        x=evaluate({k:REF for k in REQUIRED['common']+REQUIRED['commercial']},'05')
        self.assertEqual(x['status'],'HUMAN_REVIEW_CANDIDATE_ONLY')
        self.assertFalse(x['send_authorized'])
    def test_query_parameter_not_confirmation(self):
        self.assertFalse(confirmed_signup({'subscribe':'success','event':'confirmed_signup'}))
    def test_follower_not_confirmation(self):
        e={'event':'confirmed_signup','source':'wpcom_followers','state_before':'unconfirmed','state_after':'subscribed','evidence_ref':REF,'opaque_transition_id':'abcde12345abc'}
        self.assertFalse(confirmed_signup(e))
    def test_dedupe_and_provider_transition(self):
        e={'event':'confirmed_signup','source':'jetpack_authoritative','state_before':'unconfirmed','state_after':'subscribed','evidence_ref':REF,'opaque_transition_id':'abcde12345abc'}
        self.assertTrue(confirmed_signup(e))
        self.assertEqual(len(dedup_confirmed([e,e])),1)
    def test_click_is_not_sale(self):
        self.assertFalse(paid_conversion({'state':'click','gross_cents':100,'fee_cents':0,'refund_cents':0}))
    def test_unsettled_not_sale(self):
        r=self.sale();r['state']='pending';self.assertFalse(paid_conversion(r))
    def test_float_and_bool_amounts_fail(self):
        for v in (1.7,True,-3,'100'):
            r=self.sale();r['gross_cents']=v;self.assertFalse(paid_conversion(r))
    def test_fee_refund_required(self):
        r=self.sale();del r['fee_cents'];self.assertFalse(paid_conversion(r))
    def test_no_unverified_denominator(self):
        self.assertEqual(safe_revenue_report([self.sale()],100,'')['status'],'NOT_COMPUTABLE')
    def test_no_implicit_zero_sales(self):
        self.assertEqual(safe_revenue_report([],0,REF)['status'],'NOT_COMPUTABLE')
    def test_empty_order_input_does_not_fabricate_zero_revenue(self):
        self.assertEqual(safe_revenue_report([],100,REF)['status'],'NOT_COMPUTABLE')
    def test_duplicate_sale_fails_closed(self):
        r=self.sale();self.assertEqual(safe_revenue_report([r,r],100,REF)['status'],'NOT_COMPUTABLE')
    def test_synthetic_math_review_only(self):
        r=self.sale(); x=safe_revenue_report([r],100,REF)
        self.assertEqual(x['status'],'REVIEW_ONLY')
        self.assertEqual(x['net_cents'],700)
        self.assertEqual(x['net_cents_per_1000_qualified_human_sessions'],7000)
    def sale(self):
        return {'state':'settled','source':'merchant-settlement','settlement_evidence_ref':REF,
        'opaque_order_id':'settlement_123456','gross_cents':1000,'refund_cents':200,'fee_cents':100}

if __name__=='__main__': unittest.main()
