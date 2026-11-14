"""Synthetic-only negative tests. No live data, accounts, emails or external API."""
import unittest
from funnel_truth import safe_counts, classify_receipts, hypothetical_net_per_thousand, release_state

S = {'subscribers': {'total':3,'confirmed':3,'unconfirmed':2,'suppressed':0},'site_can_send': True}

def event(id, kind, **kwargs): return {'event_id':id,'kind':kind, **kwargs}

class ReconciliationTests(unittest.TestCase):
    def test_counts_do_not_add(self): self.assertTrue(safe_counts(S)['labels_nonadditive'])
    def test_overlap_flag(self): self.assertTrue(safe_counts(S)['total_less_than_confirmed_plus_unconfirmed'])
    def test_no_eligible_count_inferred(self): self.assertIsNone(safe_counts(S)['verified_eligible_email_recipients'])
    def test_can_send_not_permission(self): self.assertEqual(safe_counts(S)['release'],'HOLD_UNSENT')
    def test_missing_counts(self):
        with self.assertRaises(ValueError): safe_counts({'subscribers':{},'site_can_send':True})
    def test_boolean_not_count(self):
        with self.assertRaises(ValueError): safe_counts({'subscribers':dict(S['subscribers'],total=True),'site_can_send':True})
    def test_negative_rejected(self):
        with self.assertRaises(ValueError): safe_counts({'subscribers':dict(S['subscribers'],total=-1),'site_can_send':True})
    def test_send_string_rejected(self):
        with self.assertRaises(ValueError): safe_counts({'subscribers':S['subscribers'],'site_can_send':'true'})

class ReceiptTests(unittest.TestCase):
    def test_empty(self): self.assertIsNone(classify_receipts([])['verified_paid_orders'])
    def test_download_not_confirmed(self): self.assertNotIn('provider_labelled_confirmation_candidates',classify_receipts([event('e001','pdf_download')])['counts'])
    def test_signup_attempt_not_confirmed(self): self.assertNotIn('provider_labelled_confirmation_candidates',classify_receipts([event('e002','signup_attempt')])['counts'])
    def test_welcome_not_confirmed(self): self.assertNotIn('provider_labelled_confirmation_candidates',classify_receipts([event('e003','welcome_received')])['counts'])
    def test_claimed_signup_without_provider(self): self.assertIn('no_provider_confirmation_receipt',classify_receipts([event('e004','confirmed_signup')])['rejections'])
    def test_provider_candidate_not_verified(self):
        r=classify_receipts([event('e005','confirmed_signup',source_system='jetpack',provider_receipt_key='private123')]);self.assertEqual(r['counts']['provider_labelled_confirmation_candidates'],1);self.assertIsNone(r['verified_confirmed_signups'])
    def test_provider_duplicate(self):
        r=classify_receipts([event('e005','confirmed_signup',source_system='jetpack',provider_receipt_key='private123'),event('e006','confirmed_signup',source_system='jetpack',provider_receipt_key='private123')]);self.assertEqual(r['counts']['provider_labelled_confirmation_candidates'],1);self.assertEqual(r['rejections']['duplicate_provider_confirmation'],1)
    def test_duplicate_event_id(self): self.assertIn('missing_or_duplicate_event_id',classify_receipts([event('e005','pdf_download'),event('e005','pdf_download')])['rejections'])
    def test_unknown_event(self): self.assertIn('invalid_kind',classify_receipts([event('e005','sale')])['rejections'])
    def test_canonical_social(self): self.assertEqual(classify_receipts([event('e005','landing_view',utm_medium='organic_social',utm_source='tiktok',asset_id='real-asset')])['counts']['canonical_social_tagged_landing_candidates'],1)
    def test_wrong_social_medium(self): self.assertEqual(classify_receipts([event('e005','landing_view',utm_medium='social',utm_source='tiktok',asset_id='real-asset')])['counts']['unattributed_landing_candidates'],1)
    def test_fake_social_platform(self): self.assertEqual(classify_receipts([event('e005','landing_view',utm_medium='organic_social',utm_source='madeup',asset_id='a')])['counts']['unattributed_landing_candidates'],1)
    def test_order_claim_not_sale(self):
        r=classify_receipts([event('e005','order_claim',gross_cents=100000,claimed_verified=True)]);self.assertEqual(r['counts']['unverified_order_claims'],1);self.assertIsNone(r['recognized_net_revenue'])
    def test_no_identifiers_output(self):
        r=str(classify_receipts([event('e005','confirmed_signup',source_system='jetpack',provider_receipt_key='PRIVATE_RECIPIENT_VALUE',email='person@example.com')]));self.assertNotIn('PRIVATE_RECIPIENT_VALUE',r);self.assertNotIn('person@example.com',r)
    def test_nonlist_rejected(self):
        with self.assertRaises(ValueError): classify_receipts('yes')

class CommercialTests(unittest.TestCase):
    def test_valid_hypothetical(self): self.assertEqual(hypothetical_net_per_thousand(1000,10000,1000,500),'85.00')
    def test_no_sessions(self): self.assertIsNone(hypothetical_net_per_thousand(0,10000,0,0))
    def test_missing_sales(self): self.assertIsNone(hypothetical_net_per_thousand(1000,None,0,0))
    def test_refunds_gt_gross(self): self.assertIsNone(hypothetical_net_per_thousand(1000,100,200,0))
    def test_boolean_not_numeric(self): self.assertIsNone(hypothetical_net_per_thousand(True,1000,0,0))
    def test_negative_net_allowed(self): self.assertEqual(hypothetical_net_per_thousand(1000,100,0,200),'-1.00')
    def test_offer_allocation(self): self.assertEqual(release_state()['merchant_slots'],[3,5])
    def test_all_hold(self): self.assertEqual(release_state()['all_six'],'HOLD_UNSENT')
    def test_no_conversion_claim(self): self.assertEqual(release_state()['report_revenue'],'NOT_COMPUTABLE')

if __name__=='__main__':unittest.main()
