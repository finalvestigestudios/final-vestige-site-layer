"""No connections, no emails, no writes. Structural/negative R143 tests."""
import unittest
import copy
from runtime_truth import assess, safe_attribution

S = {'as_of':'2026-11-05T18:30:53Z', 'settings':{
    'subscriptions':True,'email_new_posts_by_default':False,
    'email_content_format':'full','from_name':'Final Vestige Studios', 'reply_to':'no-reply'},
    'status':{'subscribers':{'total':3,'confirmed':3,'unconfirmed':2,'imported_last_24h':1}},
    'previous_reported':{'email_content_format':'excerpt','from_name':'Final Vestige'}}
M={'issues':[{'number':i,'kind':'commercial-review-pending' if i in (3,5) else 'editorial',
               'merchant_affiliate_url':None} for i in range(1,7)]}
B={i:'UNSENT DRAFT [[VALID_POSTAL_ADDRESS_REQUIRED]] [[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]' +
     (' Commercial disclosure: [[APPROVED_GUIDE_REQUIRED]]' if i in (3,5) else '') for i in range(1,7)}

class R143Tests(unittest.TestCase):
    def setUp(self): self.r=assess(copy.deepcopy(S),copy.deepcopy(M),copy.deepcopy(B))
    def test_hold_all(self): self.assertEqual(self.r['all_send_permissions'],'HOLD_UNSENT')
    def test_count_nonadditive(self):
        self.assertEqual(self.r['reported_nonadditive_counters']['total'],3)
        self.assertIsNone(self.r['email_eligible_unique_recipients'])
    def test_mode_full(self): self.assertEqual(self.r['delivery_mode_authenticated'],'full')
    def test_detect_drift(self): self.assertIn('email_content_format', self.r['previous_reported_drift'])
    def test_sender_drift(self): self.assertIn('from_name',self.r['previous_reported_drift'])
    def test_no_actor_inference(self): self.assertEqual(self.r['previous_reported_drift']['from_name']['change_actor_and_time'],'UNKNOWN_OR_UNVERIFIED')
    def test_four_editorial_two_commercial(self):
        self.assertEqual([i['type'] for i in self.r['issues']].count('commercial'),2)
    def test_both_commercial_held(self): self.assertEqual([i['status'] for i in self.r['issues'] if i['type']=='commercial'],['HOLD_MERCHANT_AND_SHARED']*2)
    def test_all_legal_placeholders(self): self.assertTrue(all('LEGAL_FOOTER_PLACEHOLDERS_IN_SOURCE' in x['findings'] for x in self.r['issues']))
    def test_all_native_preview_unknown(self): self.assertTrue(all(not x['native_inbox_preview_verified'] for x in self.r['issues']))
    def test_full_mode_risk_each_issue(self): self.assertTrue(all('FULL_POST_MAY_DELIVER_ALL_UNREDACTED_CONTENT_AND_LINKS' in x['findings'] for x in self.r['issues']))
    def test_full_mode_excerpt_mode_change(self):
        s=copy.deepcopy(S);s['settings']['email_content_format']='excerpt';r=assess(s,M,B)
        self.assertTrue(all('EXCERPT_MAY_NOT_INCLUDE_INLINE_CTA_OR_DISCLOSURE' in x['findings'] for x in r['issues']))
    def test_unknown_mode_stays_hold(self):
        s=copy.deepcopy(S);s['settings']['email_content_format']='mystery';r=assess(s,M,B)
        self.assertEqual(r['delivery_mode_authenticated'],'UNKNOWN_OR_UNVERIFIED')
        self.assertEqual(r['all_send_permissions'],'HOLD_UNSENT')
    def test_missing_manuscript(self):
        b=copy.deepcopy(B);b.pop(4);r=assess(S,M,b)
        self.assertIn('NO_CANONICAL_MANUSCRIPT',r['issues'][3]['findings'])
    def test_nonverified_conversion(self):
        self.assertIsNone(self.r['attributed_paid_orders']);self.assertIsNone(self.r['net_revenue_per_1000_qualified_sessions'])
    def test_no_revenue_from_clicks_or_subs(self): self.assertIsNone(safe_attribution(200,None,0,0))
    def test_no_revenue_without_sessions(self): self.assertIsNone(safe_attribution(0,[50],2,3))
    def test_no_revenue_without_fees(self): self.assertIsNone(safe_attribution(200,[50],2,None))
    def test_no_revenue_without_refunds(self): self.assertIsNone(safe_attribution(200,[50],None,3))
    def test_no_revenue_from_negative_transactions(self): self.assertIsNone(safe_attribution(200,[-100],0,0))
    def test_no_revenue_with_boolean_sessions(self): self.assertIsNone(safe_attribution(True,[50],0,0))
    def test_verified_hypothetical_arithmetic_only(self): self.assertEqual(safe_attribution(200,[50,30],10,5),325.0)
    def test_critical_duplicate_first_click(self):self.assertIn('CTA_REPEATS_ISSUE_02_DESPITE_DIFFERENT_TOPIC',self.r['issues'][0]['findings'])
    def test_critical_repeat_signup(self):self.assertIn('RETURN_SUBSCRIBER_CTA_TO_SIGNUP_PAGE',self.r['issues'][5]['findings'])
    def test_original_unsupported_subject(self):self.assertIn('FOURTEEN_SECOND_SUBJECT_REQUIRES_SOURCE_REVIEW',self.r['issues'][3]['findings'])
    def test_no_send_if_site_can_send(self):
        s=copy.deepcopy(S);s['status']['site_can_send']=True
        self.assertEqual(assess(s,M,B)['all_send_permissions'],'HOLD_UNSENT')

if __name__=='__main__':unittest.main()
