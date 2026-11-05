import unittest
from signup_truth import audit_projection, classify_signup_ui, count_verified_new_leads, email_reachable_aggregate

ANCHOR_523 = '''<div class="wp-block-jetpack-subscriptions__supports-newline wp-block-jetpack-subscriptions"><div><p><a href="https://finalvestige.com/?post_type=page&#038;p=523">Subscribe</a></p></div></div>'''
ANCHOR_1579 = '''<div class="wp-block-jetpack-subscriptions__supports-newline wp-block-jetpack-subscriptions"><div><p><a href="https://finalvestige.com/?post_type=page&#038;p=1579">Send me the fieldbook</a></p></div></div>'''
FORM = '''<div class="wp-block-jetpack-subscriptions"><form><label>Email<input type="email" required></label><button>Subscribe</button></form></div>'''
UID = 'sub_' + 'a'*32

class TestSourceAndConsent(unittest.TestCase):
    def test_dispatch_cms_anchor(self):
        x = audit_projection(ANCHOR_523, 523)
        self.assertEqual(x['state'], 'LINK_TO_SAME_PAGE_IN_CMS_PROJECTION')
        self.assertFalse(x['actual_signed_out_dom_verified'])
    def test_focus_cms_anchor(self):
        self.assertTrue(audit_projection(ANCHOR_1579,1579)['same_page_subscribe_link'])
    def test_present_input_does_not_prove_live(self):
        x = audit_projection(FORM,523)
        self.assertEqual(x['email_input_count'], 1)
        self.assertEqual(x['state'], "INPUT_PRESENT_IN_CMS_PROJECTION_NOT_LIVE_PROOF")
        self.assertFalse(x['actual_signed_out_dom_verified'])
    def test_no_block(self):
        self.assertEqual(audit_projection('<p>hello</p>',523)['state'],'SUBSCRIBE_BLOCK_NOT_PRESENT_IN_PROJECTION')
    def test_known_submission_token_does_not_prove_confirmed(self):
        x=classify_signup_ui('https://finalvestige.com/focus/?subscribe=success')
        self.assertTrue(x['show_public_download_prompt'])
        self.assertFalse(x['confirmed_signup'])
        self.assertIsNone(x['email_reachable'])
    def test_forged_tokens_fail_closed(self):
        for t in ['pending','false','unsubscribed','already','successs','error','blocked','anything']:
            with self.subTest(t=t):
                x=classify_signup_ui('https://finalvestige.com/focus/?subscribe='+t)
                self.assertFalse(x['show_public_download_prompt'])
    def test_repeated_success_token_fail_closed(self):
        self.assertFalse(classify_signup_ui('https://finalvestige.com/focus/?subscribe=success&subscribe=error')['show_public_download_prompt'])
    def test_ui_marker_not_email_eligibility(self):
        x=classify_signup_ui('https://finalvestige.com/focus/',native_subscriber_class=True)
        self.assertFalse(x['confirmed_signup'])
        self.assertIsNone(x['email_reachable'])
    def test_client_success_only_not_lead(self):
        self.assertEqual(count_verified_new_leads([{'event':'confirmed_signup','source':'url_query','opaque_subscription_key':UID}])['verified_new_leads'],0)
    def test_duplicate_real_transitions(self):
        e={'event':'confirmed_signup','source':'native_jetpack_subscriber_status','previous_status':'not_confirmed','new_status':'subscribed','consent_provenance_checked':True,'opaque_subscription_key':UID}
        x=count_verified_new_leads([e,e]); self.assertEqual(x['verified_new_leads'],1)
        self.assertEqual(x['rejected_by_reason'].get('duplicate'),1)
    def test_prior_status_unknown_not_new(self):
        e={'event':'confirmed_signup','source':'native_jetpack_subscriber_status','previous_status':'unknown','new_status':'subscribed','consent_provenance_checked':True,'opaque_subscription_key':UID}
        self.assertEqual(count_verified_new_leads([e])['verified_new_leads'],0)
    def test_pii_or_short_identifiers_rejected(self):
        e={'event':'confirmed_signup','source':'native_jetpack_subscriber_status','previous_status':'not_confirmed','new_status':'subscribed','consent_provenance_checked':True,'opaque_subscription_key':'test@example.com'}
        self.assertEqual(count_verified_new_leads([e])['verified_new_leads'],0)
    def test_counts_not_additive(self):
        self.assertIsNone(email_reachable_aggregate({'total':3,'confirmed':3,'unconfirmed':2})['eligible_email_recipients'])
    def test_native_subscribed_count_only(self):
        x=email_reachable_aggregate({'source':'native_email_subscription_filter','subscribed':2,'paused':1,'unconfirmed':2})
        self.assertEqual(x['eligible_email_recipients'],2)
        self.assertEqual(x['status'],'PROVIDER_REPORTED_NOT_DELIVERY_PROOF')
    def test_boolean_count_rejected(self):
        self.assertIsNone(email_reachable_aggregate({'source':'native_email_subscription_filter','subscribed':True})['eligible_email_recipients'])
    def test_missing_evidence_is_unknown(self):
        self.assertIsNone(email_reachable_aggregate(None)['eligible_email_recipients'])

if __name__ == '__main__': unittest.main()
