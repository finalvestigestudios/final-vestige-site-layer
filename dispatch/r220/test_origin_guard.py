import unittest
from origin_guard import classify_lead, safe_attribution, summarize_public_sources, guarded_cohort, utc_time

SNAPSHOT = {"newsletter_enabled": True, "default_auto_send": False, "post_end_subscribe": True,
 "comment_site_subscribe": True, "comment_reply_notifications": True, "focus_has_form": True,
 "dispatch_has_form": True, "newsletter_categories_enabled": False,
 "total": 3, "confirmed": 3, "unconfirmed": 2, "followers_wpcom": 3, "followers_email": 0}
GOOD = {"kind":"provider_subscription_transition", "entrypoint":"focus_form",
 "source":"authenticated_jetpack_provider", "new_status":"subscribed", "old_status":"not_confirmed",
 "provider_private_ref":"private-only:synthetic-not-real", "at":"2026-11-08T19:00:00Z"}
SOCIAL = "https://finalvestige.com/focus/?utm_source=youtube&utm_medium=organic_social&utm_campaign=perception_pilot&utm_content=asset_123sample"
DISPATCH = "https://finalvestige.com/2026/11/02/change-blindness/?utm_source=dispatch&utm_medium=email&utm_campaign=pilot_2026&utm_content=issue_01"

class TestOriginGuard(unittest.TestCase):
 def test_four_distinct_site_entrypoints(self):
  a=summarize_public_sources(SNAPSHOT)
  self.assertEqual(len(a['observable_subscription_entrypoints']),4)
  self.assertIn('comment_subscribe_checkbox',a['observable_subscription_entrypoints'])
  self.assertIsNone(a['attributed_focus_confirmed_signups'])
  self.assertIsNone(a['eligible_email_recipient_count'])
  self.assertFalse(a['newsletter_sends_authorized'])
 def test_comment_notification_separate(self):
  self.assertTrue(summarize_public_sources(SNAPSHOT)['comment_notification_is_not_newsletter_signup'])
 def test_nonadditive_counts(self):
  a=summarize_public_sources(SNAPSHOT)
  self.assertEqual(a['source_counts_nonadditive']['unconfirmed'],2)
  self.assertIsNone(a['actual_qualifying_paid_sales'])
 def test_boolean_not_number(self):
  for key in ('newsletter_enabled','comment_site_subscribe','post_end_subscribe'):
   with self.subTest(key=key),self.assertRaises(ValueError):
    summarize_public_sources({**SNAPSHOT,key:1})
 def test_counter_validation(self):
  for key in ('total','confirmed','unconfirmed','followers_wpcom','followers_email'):
   with self.subTest(key=key),self.assertRaises(ValueError):
    summarize_public_sources({**SNAPSHOT,key:-1})
 def test_synthetic_provider_claim_not_real_proof(self):
  a=classify_lead(GOOD)
  self.assertEqual(a['stage'],'PROVIDER_RECORD_SHAPED_UNAUTHENTICATED')
  self.assertFalse(a['countable_real_lead'])
  self.assertFalse(a['attributable_to_focus'])
 def test_unqualified_nonleads(self):
  for k in ('pdf_view','gift_visible','form_submit','subscribe_url','comment_notification','reader_follow','cta_click','affiliate_click'):
   with self.subTest(k=k): self.assertEqual(classify_lead({'kind':k})['stage'],'NON_LEAD')
 def test_invalid_or_unknown_origin(self):
  self.assertEqual(classify_lead({**GOOD,'entrypoint':'external_form'})['stage'],'INVALID_ENTRYPOINT')
  self.assertEqual(classify_lead({**GOOD,'entrypoint':'wordpress_reader'})['attributable_to_focus'],False)
 def test_wrong_transition(self):
  for patch in ({'old_status':'subscribed'},{'new_status':'paused'}, {'source':'browser'}):
   with self.subTest(patch=patch):self.assertEqual(classify_lead({**GOOD,**patch})['stage'],'PROVIDER_PROOF_MISSING')
 def test_unverifiable_reference(self):
  self.assertEqual(classify_lead({**GOOD,'provider_private_ref':'not-private'})['stage'],'PROVIDER_PROOF_MISSING')
 def test_invalid_timestamp(self):
  self.assertEqual(classify_lead({**GOOD,'at':'2026-11-08 19:00:00'})['stage'],'INVALID_TIME')
 def test_no_pii_allowed(self):
  for key in ('email','email_hash','ip','phone','subscriber_name','cookie','token'):
   with self.subTest(key=key),self.assertRaises(ValueError):classify_lead({**GOOD,key:'fake'})
 def test_url_owned_social(self):
  a=safe_attribution(SOCIAL,'grok');self.assertEqual(a['owned_path'],'/focus/');self.assertFalse(a['verified_live_asset'])
 def test_url_owned_email(self):
  self.assertEqual(safe_attribution(DISPATCH,'dispatch')['tags']['utm_medium'],'email')
 def test_cross_channel_spoof(self):
  with self.assertRaises(ValueError):safe_attribution(SOCIAL,'dispatch')
  with self.assertRaises(ValueError):safe_attribution(DISPATCH,'grok')
 def test_domain_attacks(self):
  for url in (SOCIAL.replace('finalvestige.com','evil.com'),SOCIAL.replace('https://','http://'),SOCIAL.replace('/focus/','/foo//bar/'),SOCIAL+'#fragment',SOCIAL.replace('finalvestige.com','finalvestige.com:443')):
   with self.subTest(url=url),self.assertRaises(ValueError):safe_attribution(url,'grok')
 def test_bad_utm(self):
  for url in (SOCIAL+'&utm_source=tiktok',SOCIAL.replace('asset_123sample','joe@example.com'),SOCIAL.replace('asset_123sample','notasset'),SOCIAL.replace('utm_source=youtube','utm_source=search')):
   with self.subTest(url=url),self.assertRaises(ValueError):safe_attribution(url,'grok')
 def test_no_identity_leak_in_result(self):
  self.assertNotIn('private-only',str(classify_lead(GOOD)))
 def test_no_revenue_from_fake_events(self):
  a=guarded_cohort([GOOD,{'kind':'affiliate_click'},{'kind':'pdf_view'}],7)
  self.assertEqual(a['status'],'NOT_COMPUTABLE');self.assertIsNone(a['paid_orders']);self.assertFalse(a['can_send'])
 def test_30_day_cohort(self):
  self.assertEqual(guarded_cohort([],30)['cohort_days'],30)
 def test_bad_cohort(self):
  with self.assertRaises(ValueError):guarded_cohort([],90)
 def test_time_explicit(self):
  with self.assertRaises(ValueError):utc_time('2026-11-08')

if __name__=='__main__':unittest.main()
