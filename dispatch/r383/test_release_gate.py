"""Native synthetic test suite; no subscriber PII, email or merchant requests."""
import unittest
from release_gate import release_decision, audience_snapshot, net_commission_per_1000, SHARED_PROOFS, MERCHANT_PROOFS

class GateTests(unittest.TestCase):
    def test_initial_six_hold(self):
        for issue in range(1, 7):
            self.assertEqual(release_decision(issue, {})['state'], 'HOLD_UNSENT')
    def test_four_editorial_and_two_commercial(self):
        self.assertEqual([n for n in range(1, 7) if release_decision(n, {})['merchant_hold']], [3, 5])
    def test_seller_page_cannot_authorize_email(self):
        self.assertIn('product_email_channel_permission', release_decision(3, {'public_seller_page': True})['missing_proofs'])
    def test_bool_only_no_truthy_string(self):
        self.assertIn('founder_final_approval', release_decision(1, {'founder_final_approval': 'true'})['missing_proofs'])
    def test_false_always_prevents_sending_even_all_attested(self):
        all_proof = {x: True for x in SHARED_PROOFS + MERCHANT_PROOFS}
        self.assertFalse(release_decision(3, all_proof)['automatic_send_authorized'])
    def test_email_rights_isolated_to_commercial(self):
        proof = {x: True for x in SHARED_PROOFS}
        self.assertFalse(release_decision(1, proof)['merchant_hold'])
        self.assertTrue(release_decision(3, proof)['merchant_hold'])
    def test_invalid_issue_rejected(self):
        for n in [0, 7, '3', True]:
            with self.assertRaises(ValueError): release_decision(n, {})
    def test_counts_not_added(self):
        a = audience_snapshot(3, 3, 2, 3, 0)
        self.assertIsNone(a['combined_audience'])
        self.assertIsNone(a['unique_eligible_inboxes'])
    def test_negative_count_rejected(self):
        with self.assertRaises(ValueError): audience_snapshot(3, 3, -2, 3, 0)
    def test_no_denominator_no_kpi(self):
        self.assertIsNone(net_commission_per_1000(None, []))
    def test_unverified_order_no_kpi(self):
        self.assertIsNone(net_commission_per_1000(1000, [{'publisher_commission':'99'}]))
    def test_settled_commission_less_refunds_fees(self):
        r = dict(opaque_order_id='opaque-01', merchant_report_verified=True, settlement_final=True, refunds_fees_final=True,
                 publisher_commission='12.50', refunds_and_clawbacks='2.00', publisher_fees='0.50')
        self.assertEqual(net_commission_per_1000(500, [r]), '20.00')
    def test_duplicate_rejected(self):
        r = dict(opaque_order_id='opaque-01', merchant_report_verified=True, settlement_final=True, refunds_fees_final=True,
                 publisher_commission='12.50', refunds_and_clawbacks='0', publisher_fees='0')
        self.assertIsNone(net_commission_per_1000(500, [r, r]))
    def test_retail_amount_not_commission(self):
        r = dict(opaque_order_id='opaque-01', merchant_report_verified=True, settlement_final=True, refunds_fees_final=True,
                 customer_retail_amount='87.99', refunds_and_clawbacks='0', publisher_fees='0')
        self.assertIsNone(net_commission_per_1000(500, [r]))
    def test_negative_and_non_numeric_rejected(self):
        r = dict(opaque_order_id='opaque-01', merchant_report_verified=True, settlement_final=True, refunds_fees_final=True,
                 publisher_commission='NaN', refunds_and_clawbacks='0', publisher_fees='0')
        self.assertIsNone(net_commission_per_1000(500, [r]))

if __name__ == '__main__': unittest.main()
