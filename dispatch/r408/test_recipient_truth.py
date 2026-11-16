import copy
import json
import pathlib
import unittest
from recipient_truth import audit

ROOT=pathlib.Path(__file__).resolve().parent
BASE=json.loads((ROOT/'WP_JETPACK_READONLY_20261116.json').read_text())

class TestRecipientTruth(unittest.TestCase):
    def one(self): return copy.deepcopy(BASE)
    def test_snapshot_holds(self):
        q=audit(self.one()); self.assertEqual(q['status'],'HOLD_UNSENT');self.assertFalse(q['mail_allowed'])
    def test_no_per_recipient_inference(self):self.assertIsNone(audit(self.one())['confirmed_signup_v1'])
    def test_no_revenue_without_settlements(self):self.assertIsNone(audit(self.one())['net_revenue_per_1000_qualified_sessions'])
    def test_overlap_not_additive(self):self.assertIn('COUNT_UNIVERSES_OVERLAP_OR_DIFFER: do not add totals',audit(self.one())['notes'])
    def test_email_zero_not_zero_recipients(self):self.assertIsNone(audit(self.one())['unique_receivers'])
    def test_email_disagreement_flagged(self):self.assertTrue(any('CONFIRMED_VS_DIRECT_EMAIL' in x for x in audit(self.one())['notes']))
    def test_platform_send_not_permission(self):self.assertTrue(any('NOT_CAMPAIGN_PERMISSION' in x for x in audit(self.one())['notes']))
    def test_no_pii_in_output(self):self.assertNotIn('@',json.dumps(audit(self.one())))
    def test_no_recent_sends(self):self.assertEqual(set(self.one()['newsletter']['recent_send_statuses']),{'never_sent_opted_out'})
    def test_automatic_sends_still_off(self):self.assertFalse(self.one()['newsletter']['email_new_posts_by_default'])
    def test_welcome_gap(self):self.assertIn('WELCOME_RECEIPT_UNPROVEN',audit(self.one())['blockers'])
    def test_file_delivery_gap(self):self.assertIn('FIELDBOOK_RECEIPT_UNPROVEN',audit(self.one())['blockers'])
    def test_postal_gap(self):self.assertIn('PUBLISHER_ADDRESS_UNVERIFIED',audit(self.one())['blockers'])
    def test_unsub_gap(self):self.assertIn('UNSUBSCRIBE_UNVERIFIED',audit(self.one())['blockers'])
    def test_preview_gap(self):self.assertIn('NATIVE_JETPACK_PREVIEW_MISSING',audit(self.one())['blockers'])
    def test_merchant_gap(self):self.assertTrue(any('COMMERCIAL_' in x for x in audit(self.one())['blockers']))
    def test_approved_merchant_not_send_authorization(self):
        p=self.one();p['proof']['inspire3_named_email_authorization']=True;self.assertFalse(audit(p)['mail_allowed'])
    def test_even_all_verified_does_not_send(self):
        p=self.one(); p['proof']={k:(4 if k in ('unique_email_eligible','deduped_confirmed_signup_events') else True) for k in p['proof']}
        self.assertEqual(audit(p)['status'],'HOLD_UNSENT');self.assertFalse(audit(p)['mail_allowed'])
    def test_newpost_on_blocks(self):
        p=self.one();p['newsletter']['email_new_posts_by_default']=True;self.assertIn('AUTOMATIC_POST_EMAILS_ENABLED_UNEXPECTEDLY',audit(p)['blockers'])
    def test_subscriptions_disabled_blocks(self):
        p=self.one();p['newsletter']['subscriptions']=False;self.assertIn('NEWSLETTER_DISABLED',audit(p)['blockers'])
    def test_partial_followers_blocks(self):
        p=self.one();p['followers']['partial']=True;self.assertIn('FOLLOWER_SNAPSHOT_PARTIAL',audit(p)['blockers'])
    def test_confirmed_above_total_blocks(self):
        p=self.one();p['newsletter']['confirmed']=20;self.assertIn('CONFIRMED_EXCEEDS_TOTAL',audit(p)['blockers'])
    def test_missing_snapshot_data_rejected(self):
        p=self.one();del p['followers'];self.assertRaises(ValueError,audit,p)
    def test_extra_top_key_rejected(self):
        p=self.one();p['subscriber_email']='private';self.assertRaises(ValueError,audit,p)
    def test_extra_nested_pii_rejected(self):
        p=self.one();p['proof']['email']='private';self.assertRaises(ValueError,audit,p)
    def test_missing_merchant_key_rejected(self):
        p=self.one();del p['proof']['inspire3_named_email_authorization'];self.assertRaises(ValueError,audit,p)
    def test_negative_counts_rejected(self):
        p=self.one();p['newsletter']['confirmed']=-1;self.assertRaises(ValueError,audit,p)
    def test_boolean_cannot_replace_int(self):
        p=self.one();p['newsletter']['confirmed']=True;self.assertRaises(ValueError,audit,p)
    def test_pii_in_array_rejected(self):
        p=self.one();p['newsletter']['send_blockers']=[{ 'email':'x' }];self.assertRaises(ValueError,audit,p)
    def test_nonbool_autosend_rejected(self):
        p=self.one();p['newsletter']['email_new_posts_by_default']='false';self.assertRaises(ValueError,audit,p)
    def test_proof_bool_not_string(self):
        p=self.one();p['proof']['welcome_received']='verified';self.assertRaises(ValueError,audit,p)
    def test_proof_count_nonnegative(self):
        p=self.one();p['proof']['unique_email_eligible']=-1;self.assertRaises(ValueError,audit,p)
    def test_email_follower_not_assumed_eligible(self):
        p=self.one();p['followers']['email']=3;self.assertIsNone(audit(p)['unique_receivers'])
    def test_zero_confirmed_signup_not_inferred(self):
        p=self.one();p['newsletter']['confirmed']=0;self.assertIsNone(audit(p)['confirmed_signup_v1'])
    def test_true_merchant_but_unsub_false_still_holds(self):
        p=self.one();p['proof']['inspire3_named_email_authorization']=True;p['proof']['unsubscribe_rendered_and_operational']=False;self.assertFalse(audit(p)['mail_allowed'])
    def test_valid_zero_attested_count_not_a_sale(self):
        p=self.one();p['proof']['deduped_confirmed_signup_events']=0;self.assertIsNone(audit(p)['net_revenue_per_1000_qualified_sessions'])
    def test_no_total_addition(self):self.assertEqual(audit(self.one())['counts']['total'],3)
    def test_no_unapproved_url(self):self.assertNotIn('http',json.dumps(audit(self.one())))

if __name__=='__main__':unittest.main()
