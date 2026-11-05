import copy
import json
import unittest
from pathlib import Path
from journey_gate import assess

BASE = json.loads((Path(__file__).parent / 'snapshot.json').read_text(encoding='utf-8'))

class JourneyTests(unittest.TestCase):
    def change(self, **changes):
        d = copy.deepcopy(BASE)
        d.update(changes)
        return d

    def test_live_observation_fails_closed(self):
        v = assess(BASE)
        self.assertEqual(v['release'], 'HOLD_UNSENT')
        self.assertEqual(v['editorial_gate'], 'HOLD_EVIDENCE')
        self.assertEqual(v['commercial_gate'], 'HOLD_MERCHANT_AND_EVIDENCE')
        self.assertIsNone(v['verified_email_reachable'])
        self.assertIsNone(v['realized_net_revenue_per_1000_qualified_human_sessions'])

    def test_nonadditive_diagnostics(self):
        self.assertTrue(assess(BASE)['confirmed_and_unconfirmed_are_not_additive'])
        self.assertEqual(BASE['wordpress']['counts']['total'], 3)
        self.assertEqual(BASE['wordpress']['counts']['unconfirmed'], 2)

    def test_denies_auto_sends(self):
        d = copy.deepcopy(BASE); d['wordpress']['email_new_posts_by_default'] = True
        with self.assertRaises(ValueError): assess(d)

    def test_denies_fake_browser_proof(self):
        d = copy.deepcopy(BASE); d['wordpress']['cta_observation_status'] = 'native_verified'
        with self.assertRaises(ValueError): assess(d)

    def test_missing_native_signup_provenance(self):
        with self.assertRaises(ValueError): assess(self.change(native_confirmed_signup_evidence=True))

    def test_missing_native_recipient_provenance(self):
        d = copy.deepcopy(BASE); d['wordpress']['native_email_eligible'] = 2; d['native_recipient_filter_evidence'] = True
        with self.assertRaises(ValueError): assess(d)

    def test_unconfirmed_not_counted_as_eligible(self):
        d = copy.deepcopy(BASE); d['wordpress']['native_email_eligible'] = 5
        with self.assertRaises(ValueError): assess(d)

    def test_eligible_with_authoritative_filter(self):
        d = copy.deepcopy(BASE); d['wordpress']['native_email_eligible'] = 2
        d['native_recipient_filter_evidence'] = True
        d['recipient_filter_provenance'] = 'native WordPress subscriber filter reviewed privately'
        self.assertEqual(assess(d)['verified_email_reachable'], 2)

    def test_rejects_email_address_field(self):
        with self.assertRaises(ValueError): assess(self.change(recipient_email='someone@example.test'))

    def test_rejects_secret_field(self):
        with self.assertRaises(ValueError): assess(self.change(api_key='should-never-store'))

    def test_prevents_partner_permission_without_evidence(self):
        d = copy.deepcopy(BASE); d['offer']['email_promotion_permission'] = True
        with self.assertRaises(ValueError): assess(d)

    def test_denies_fake_paid_sale(self):
        d = copy.deepcopy(BASE); d['paid_outcomes']['confirmed_orders'] = 1
        with self.assertRaises(ValueError): assess(d)

    def test_denies_net_without_reconciliation(self):
        d = copy.deepcopy(BASE); d['paid_outcomes']['realized_net_revenue_usd'] = 15.5
        with self.assertRaises(ValueError): assess(d)

    def test_no_zero_denominator_arithmetic(self):
        d = copy.deepcopy(BASE); d['paid_outcomes'].update({'qualified_human_sessions': 0, 'realized_net_revenue_usd': 0, 'settled_order_reconciliation_evidence': 'synthetic test fixture only'})
        self.assertIsNone(assess(d)['realized_net_revenue_per_1000_qualified_human_sessions'])

    def test_synthetic_settled_order_arithmetic_only(self):
        d = copy.deepcopy(BASE); d['paid_outcomes'].update({'confirmed_orders': 1, 'qualified_human_sessions': 200, 'realized_net_revenue_usd': 16, 'settled_order_reconciliation_evidence': 'synthetic fixture only'})
        self.assertEqual(assess(d)['realized_net_revenue_per_1000_qualified_human_sessions'], 80)
        self.assertEqual(assess(d)['release'], 'HOLD_UNSENT')

    def test_cannot_auto_authorize_even_if_all_gates_true(self):
        d = copy.deepcopy(BASE)
        d['wordpress']['native_email_eligible'] = 2
        d['native_recipient_filter_evidence'] = True
        d['recipient_filter_provenance'] = 'synthetic'
        d['native_confirmed_signup_evidence'] = True
        d['native_signup_provenance'] = 'synthetic'
        for key in ('received_welcome_evidence', 'fieldbook_received_evidence', 'native_email_preview_evidence','publisher_postal_address_rendered','unsubscribe_mechanism_verified','explicit_founder_send_approval'): d[key] = True
        d['offer']['evidence_records'] = ['synthetic']
        for key in ('named_partner_approval', 'email_promotion_permission','verified_link_format','exact_sku_guide_live','seller_claims_reviewed','current_checkout_terms_reviewed','merchant_consent_separate'): d['offer'][key] = True
        v = assess(d)
        self.assertEqual(v['editorial_gate'], 'REVIEW_ELIGIBLE_NOT_AUTHORIZED')
        self.assertEqual(v['commercial_gate'], 'REVIEW_ELIGIBLE_NOT_AUTHORIZED')
        self.assertEqual(v['release'], 'HOLD_UNSENT')

if __name__ == '__main__': unittest.main()
