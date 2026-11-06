import copy
import unittest
from confirmed_signup_checkpoint import reconcile

EVT1='evt_ABCDEFGHIJKLMNOP'
EVT2='evt_QRSTUVWXYZ123456'
REC={'event_key': EVT1, 'before':'Not confirmed', 'after':'Subscribed', 'proof_ref':'proof:review1234', 'observed_via':'provider_status_change'}
BASE={'source':'Jetpack Subscriber Email subscription column','observation':'read_only_provider_status_change','environment':'manually_attested','records':[REC]}

class SignupCheckpointTests(unittest.TestCase):
 def test_first_transition_candidate_only(self):
  r,cp=reconcile(copy.deepcopy(BASE)); self.assertEqual(r['reviewed_new_provider_transitions'],1); self.assertIsNone(r['measured_site_signups']);self.assertEqual(r['release'],'HOLD_UNSENT');self.assertEqual(len(cp['seen']),1)
 def test_replay_same_batch(self):
  r,cp=reconcile(BASE); q,_=reconcile(BASE,cp); self.assertEqual(q['reviewed_new_provider_transitions'],0);self.assertEqual(q['duplicate_events_suppressed'],1)
 def test_duplicate_in_single_batch(self):
  b=copy.deepcopy(BASE);b['records']*=2;r,_=reconcile(b);self.assertEqual(r['reviewed_new_provider_transitions'],1);self.assertEqual(r['duplicate_events_suppressed'],1)
 def test_incremental_new_event(self):
  r,cp=reconcile(BASE);b=copy.deepcopy(BASE);b['records'][0]['event_key']=EVT2;q,state=reconcile(b,cp);self.assertEqual(q['reviewed_new_provider_transitions'],1);self.assertEqual(len(state['seen']),2)
 def test_reader_only_to_email_eligible(self):
  b=copy.deepcopy(BASE);b['records'][0]['before']='Not subscribed';r,_=reconcile(b);self.assertEqual(r['reviewed_new_provider_transitions'],1)
 def test_paused_to_subscribed_is_candidate_not_confirmation(self):
  b=copy.deepcopy(BASE);b['records'][0]['before']='Emails paused';r,_=reconcile(b);self.assertEqual(r['reviewed_new_provider_transitions'],0);self.assertEqual(r['previous_subscribers_resuming_email'],1);self.assertIsNone(r['measured_site_signups'])
 def test_non_transition_rejected(self):
  b=copy.deepcopy(BASE);b['records'][0]['after']='Not subscribed';r,_=reconcile(b);self.assertEqual(r['reviewed_new_provider_transitions'],0);self.assertEqual(r['other_events_excluded'],1)
 def test_missing_source(self):
  b=copy.deepcopy(BASE);b['source']='URL query';self.assertRaises(ValueError,reconcile,b)
 def test_page_only_observation(self):
  b=copy.deepcopy(BASE);b['observation']='query_param';self.assertRaises(ValueError,reconcile,b)
 def test_unattested_environment(self):
  b=copy.deepcopy(BASE);b['environment']='synthetic';self.assertRaises(ValueError,reconcile,b)
 def test_false_observed_via(self):
  b=copy.deepcopy(BASE);b['records'][0]['observed_via']='visitor_clicked';r,_=reconcile(b);self.assertEqual(r['other_events_excluded'],1)
 def test_email_value(self):
  b=copy.deepcopy(BASE);b['records'][0]['event_key']='alice@example.org';self.assertRaises(ValueError,reconcile,b)
 def test_email_in_misc_field(self):
  b=copy.deepcopy(BASE);b['records'][0]['extra']='alice@example.org';self.assertRaises(ValueError,reconcile,b)
 def test_raw_subscriber_identifier_rejected(self):
  b=copy.deepcopy(BASE);b['records'][0]['subscriber_id']='123';self.assertRaises(ValueError,reconcile,b)
 def test_raw_name_rejected(self):
  b=copy.deepcopy(BASE);b['name']='Jane';self.assertRaises(ValueError,reconcile,b)
 def test_bad_opaque_event(self):
  b=copy.deepcopy(BASE);b['records'][0]['event_key']='evt_short';self.assertRaises(ValueError,reconcile,b)
 def test_bad_proof(self):
  b=copy.deepcopy(BASE);b['records'][0]['proof_ref']='';self.assertRaises(ValueError,reconcile,b)
 def test_duplicate_checkpoint_corrupt(self):
  _,s=reconcile(BASE);s['seen']*=2;self.assertRaises(ValueError,reconcile,BASE,s)
 def test_checkpoint_raw_key_rejected(self):
  self.assertRaises(ValueError,reconcile,BASE,{'version':1,'seen':[EVT1]})
 def test_revenue_not_imputed(self):
  r,_=reconcile(BASE);self.assertIsNone(r['customer_orders']);self.assertIsNone(r['net_revenue'])
 def test_zero_record_no_sales_or_signup(self):
  b=copy.deepcopy(BASE);b['records']=[];r,_=reconcile(b);self.assertEqual(r['reviewed_new_provider_transitions'],0);self.assertIsNone(r['measured_site_signups'])
 def test_no_addresses_or_proof_refs_reported(self):
  r,s=reconcile(BASE);self.assertNotIn('proof:review1234',str(r)+str(s));self.assertNotIn(EVT1,str(r)+str(s))
 def test_missing_record_fields(self):
  b=copy.deepcopy(BASE);b['records'][0].pop('proof_ref');self.assertRaises(ValueError,reconcile,b)
 def test_initial_checkpoint_does_not_persist_raw_events(self):
  _,cp=reconcile(BASE);self.assertEqual(len(cp['seen'][0]),64);self.assertNotIn(EVT1,str(cp))

if __name__=='__main__':unittest.main()
