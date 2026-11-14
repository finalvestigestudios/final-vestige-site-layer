"""Native Python unit tests use SYNTHETIC records only; no real subscriber or order data."""
import unittest, json
from pathlib import Path
from release_gate import (SHARED, MERCHANT, pii_paths, count_confirmed, revenue_report,
                          validate_attribution, evaluate)
ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT.parent / 'campaign-2026-mind/manifest.json').read_text())
PROOFS = {'shared': {}, 'merchant': {'03': {}, '05': {}},
          'provider_aggregate': {'total': 3, 'confirmed': 3, 'unconfirmed': 2}}

class GateTests(unittest.TestCase):
    def test_required_shared_nine(self): self.assertEqual(len(SHARED), 9)
    def test_required_merchant_eight(self): self.assertEqual(len(MERCHANT), 8)
    def test_missing_shared_rejected(self):
        self.assertEqual(set(evaluate(PROOFS, MANIFEST)['shared_missing']), set(SHARED))
    def test_hold_regardless(self): self.assertEqual(evaluate(PROOFS, MANIFEST)['all_issues'], 'HOLD_UNSENT')
    def test_merchant_hold(self): self.assertEqual(evaluate(PROOFS, MANIFEST)['commercial_03'], 'HOLD_MERCHANT')
    def test_merchant_05_hold(self): self.assertEqual(evaluate(PROOFS, MANIFEST)['commercial_05'], 'HOLD_MERCHANT')
    def test_campaign_shape(self): self.assertTrue(evaluate(PROOFS, MANIFEST)['campaign_source_valid'])
    def test_bad_campaign_shape(self):
        m = dict(MANIFEST); m['status'] = 'READY'
        self.assertFalse(evaluate(PROOFS, m)['campaign_source_valid'])
    def test_nonadditive_counts(self): self.assertTrue(evaluate(PROOFS, MANIFEST)['provider_totals_overlap'])
    def test_recipient_unknown(self): self.assertIsNone(evaluate(PROOFS, MANIFEST)['eligible_recipients'])
    def test_no_mailing_authority(self): self.assertTrue(evaluate(PROOFS, MANIFEST)['cannot_authorize_send'])
    def test_synthetic_ready_not_release(self):
        x = {'verified': True, 'source_ref': 'signed_owner_evidence_ref', 'source_kind': 'signed_contract'}
        p = {'shared': {k: x for k in SHARED},
             'merchant': {'03': {k: x for k in MERCHANT}, '05': {k: x for k in MERCHANT}}}
        self.assertEqual(evaluate(p, MANIFEST)['all_issues'], 'HOLD_UNSENT')
    def test_count_duplicate_confirmation_once(self):
        a = {'kind': 'confirmed_signup', 'provider_status': 'confirmed',
             'provider_proof': True, 'marketing_consent': True, 'provider_source': 'jetpack',
             'provider_receipt_ref': 'jetpack_confirmed_001', 'opaque_subscriber_id': 'opaque_abc_123'}
        self.assertEqual(count_confirmed([a, a]), 1)
    def test_no_signup_attempt_as_lead(self): self.assertEqual(count_confirmed([{'kind': 'signup_attempt'}]), 0)
    def test_no_unconfirmed_as_lead(self):
        self.assertEqual(count_confirmed([{'kind': 'confirmed_signup', 'provider_status': 'unconfirmed'}]), 0)
    def test_no_consent_as_lead(self):
        self.assertEqual(count_confirmed([{'kind': 'confirmed_signup', 'provider_status': 'confirmed',
                                          'provider_proof': True, 'opaque_subscriber_id': 'opaque_abc_123'}]), 0)
    def test_real_email_forbidden(self):
        self.assertIn('records[0].email', pii_paths({'records': [{'email': 'dummy@example.invalid'}]}))
    def test_personal_address_forbidden(self): self.assertIn('street_address', pii_paths({'street_address': 'x'}))
    def test_social_correct_tag(self):
        self.assertTrue(validate_attribution({'kind': 'social_visit', 'utm_source': 'youtube',
                          'utm_medium': 'organic_social', 'utm_content': 'asset_001',
                          'published_asset_proof': True}))
    def test_social_old_tag_rejected(self):
        self.assertFalse(validate_attribution({'kind': 'social_visit', 'utm_source': 'youtube',
                           'utm_medium': 'social', 'utm_content': 'asset_001',
                           'published_asset_proof': True}))
    def test_unpublished_asset_rejected(self):
        self.assertFalse(validate_attribution({'kind': 'social_visit', 'utm_source': 'youtube',
                           'utm_medium': 'organic_social', 'utm_content': 'asset_001'}))
    def test_unsent_email_click_rejected(self):
        self.assertFalse(validate_attribution({'kind': 'dispatch_guide_click', 'utm_source': 'dispatch',
                           'utm_medium': 'email', 'issue': 3, 'actually_sent': False,
                           'recipient_permission_verified': True}))
    def test_click_requires_perm(self):
        self.assertFalse(validate_attribution({'kind': 'dispatch_guide_click', 'utm_source': 'dispatch',
                           'utm_medium': 'email', 'issue': 3, 'actually_sent': True}))
    def test_click_valid_synthetic(self):
        self.assertTrue(validate_attribution({'kind': 'dispatch_guide_click', 'utm_source': 'dispatch',
                           'utm_medium': 'email', 'issue': 3, 'actually_sent': True,
                           'recipient_permission_verified': True}))
    def test_unsold_not_revenue(self):
        self.assertEqual(revenue_report([{'status': 'checkout_started'}])['confirmed_orders'], 0)
    def test_unattested_order_rejected(self):
        self.assertEqual(revenue_report([{'status': 'settled', 'opaque_order_id': 'order_12345678',
                                         'gross': 10, 'fees': 1, 'refunds': 0}])['confirmed_orders'], 0)
    def test_rejected_infinite_amount(self):
        self.assertEqual(revenue_report([{'status': 'settled', 'independent_receipt': True, 'receipt_source': 'merchant_settlement_report',
                   'independent_receipt_ref': 'merchant_settlement_001',
                   'opaque_order_id': 'order_12345678', 'gross': 'Infinity',
                   'fees': 0, 'refunds': 0}])['confirmed_orders'], 0)
    def test_negative_fee_rejected(self):
        self.assertEqual(revenue_report([{'status': 'settled', 'independent_receipt': True, 'receipt_source': 'merchant_settlement_report',
                   'independent_receipt_ref': 'merchant_settlement_001',
                   'opaque_order_id': 'order_12345678', 'gross': 10,
                   'fees': -1, 'refunds': 0}])['confirmed_orders'], 0)
    def test_fee_exceeds_sale_rejected(self):
        self.assertEqual(revenue_report([{'status': 'settled', 'independent_receipt': True, 'receipt_source': 'merchant_settlement_report',
                   'independent_receipt_ref': 'merchant_settlement_001',
                   'opaque_order_id': 'order_12345678', 'gross': 10,
                   'fees': 11, 'refunds': 0}])['confirmed_orders'], 0)
    def test_dedup_order(self):
        a = {'status': 'settled', 'independent_receipt': True, 'receipt_source': 'merchant_settlement_report',
                   'independent_receipt_ref': 'merchant_settlement_001',
             'opaque_order_id': 'order_12345678', 'gross': 10, 'fees': 2, 'refunds': 1}
        r = revenue_report([a, a], 100, {'source_kind': 'first_party_analytics', 'source_ref': 'qualified_traffic_receipt_001'})
        self.assertEqual(r['confirmed_orders'], 1)
        self.assertEqual(r['net'], '7')
        self.assertEqual(r['net_per_1000_verified_human_sessions'], '70.00')
    def test_zero_denominator_not_computable(self):
        a = {'status': 'settled', 'independent_receipt': True, 'receipt_source': 'merchant_settlement_report',
                   'independent_receipt_ref': 'merchant_settlement_001',
             'opaque_order_id': 'order_12345678', 'gross': 10, 'fees': 2, 'refunds': 1}
        self.assertIsNone(revenue_report([a], 0)['net_per_1000_verified_human_sessions'])
    def test_no_orders_ratio_not_verified(self): self.assertFalse(revenue_report([], 100)['ratio_computable'])
    def test_boolean_denominator_invalid(self):
        self.assertIsNone(revenue_report([], True)['net_per_1000_verified_human_sessions'])

class SourceProofTests(unittest.TestCase):
    def test_boolean_only_lead_not_provider_confirmation(self):
        event = {'kind': 'confirmed_signup', 'provider_status': 'confirmed',
                 'provider_proof': True, 'marketing_consent': True,
                 'opaque_subscriber_id': 'opaque_abc_123'}
        self.assertEqual(count_confirmed([event]), 0)
    def test_boolean_only_purchase_not_independent_settlement(self):
        sale = {'status': 'settled', 'independent_receipt': True,
                'opaque_order_id': 'order_12345678', 'gross': 10, 'fees': 1, 'refunds': 0}
        self.assertEqual(revenue_report([sale], 100)['confirmed_orders'], 0)
    def test_qualified_session_receipt_needed_for_revenue_ratio(self):
        sale = {'status': 'settled', 'independent_receipt': True,
                'receipt_source': 'merchant_settlement_report',
                'independent_receipt_ref': 'merchant_settlement_001',
                'opaque_order_id': 'order_12345678', 'gross': 10, 'fees': 1, 'refunds': 0}
        self.assertEqual(revenue_report([sale], 100)['confirmed_orders'], 1)
        self.assertIsNone(revenue_report([sale], 100)['net_per_1000_verified_human_sessions'])

if __name__ == '__main__': unittest.main()
