"""Synthetic native-Python tests only; no live provider data or outbound network calls."""
import unittest
from verification_contract import (
    classify_subscription_counts, summarize_confirmed_signup,
    validate_owned_utm, revenue_per_1000, release_decision,
)

PROOF = dict(kind='provider_confirmed_transition', provider='jetpack',
             origin='authenticated_provider_read', previous_status='pending',
             current_status='confirmed', private_ephemeral_key='synthetic-A',
             provider_proof_ref='provider-proof:synthetic',
             confirmed_at='2026-11-08T21:00:00Z')
URL = ('https://finalvestige.com/mind/zen12-guide/'
       '?utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11'
       '&utm_content=issue_03_zen12')
TX = dict(source='merchant_authenticated_statement', status='settled',
          transaction_ref='synthetic_order_001', gross_commission_or_sale='15.00',
          refunded_amount='0.00', fees='3.00')

class TestContract(unittest.TestCase):
    def test_nonadditive_counts(self):
        got = classify_subscription_counts(dict(total=3, confirmed=3, unconfirmed=2,
                                               wpcom_followers=3, email_followers=0))
        self.assertIsNone(got['recipient_eligible_count'])
        self.assertTrue(got['do_not_sum'])
        self.assertEqual(got['reported']['unconfirmed'], 2)

    def test_invalid_count(self):
        for bad in (-1, True, 3.5, '3'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                classify_subscription_counts({'confirmed': bad})

    def test_proof_one(self):
        got = summarize_confirmed_signup([PROOF])
        self.assertEqual(got['structurally_supported_new_confirmations'], 1)
        self.assertFalse(got['actual_provider_confirmations_verified_by_this_code'])
        self.assertFalse(got['identifiers_emitted'])

    def test_double_confirmation_deduplicated(self):
        got = summarize_confirmed_signup([PROOF, PROOF])
        self.assertEqual(got['structurally_supported_new_confirmations'], 1)
        self.assertEqual(got['rejection_reasons']['duplicate'], 1)

    def test_browser_and_follower_not_counted(self):
        fake = [dict(kind=x) for x in ('attempt', 'gift_visible', 'reader_follow', 'welcome_configured', 'welcome_receipt')]
        got = summarize_confirmed_signup(fake)
        self.assertEqual(got['structurally_supported_new_confirmations'], 0)

    def test_no_confirmation_email_required_for_wp_user(self):
        # The provider-confirmed status transition is authoritative, not receipt of a confirmation email.
        got = summarize_confirmed_signup([dict(PROOF, signup_method='existing_wpcom_login')])
        self.assertEqual(got['structurally_supported_new_confirmations'], 1)

    def test_reject_preexisting(self):
        got = summarize_confirmed_signup([dict(PROOF, previous_status='confirmed')])
        self.assertEqual(got['structurally_supported_new_confirmations'], 0)

    def test_reject_no_provider_origin(self):
        for change in ({'provider':'browser'}, {'origin':'screenshot'}, {'provider_proof_ref':'foo'},
                       {'private_ephemeral_key':''}, {'confirmed_at':'yesterday'},
                       {'confirmed_at':'2026-11-08T21:00:00'}):
            with self.subTest(change=change):
                got=summarize_confirmed_signup([dict(PROOF,**change)])
                self.assertEqual(got['structurally_supported_new_confirmations'],0)

    def test_different_proofs_count_separately(self):
        got = summarize_confirmed_signup([PROOF, dict(PROOF,private_ephemeral_key='synthetic-B')])
        self.assertEqual(got['structurally_supported_new_confirmations'],2)

    def test_valid_utm(self):
        got = validate_owned_utm(URL)
        self.assertEqual(got['attribution']['utm_content'],'issue_03_zen12')

    def test_bad_utm(self):
        variants = [URL.replace('https:','http:'),
                    URL.replace('finalvestige.com','merchant.example'),
                    URL+'&utm_campaign=dup', URL.replace('utm_medium=email','utm_medium=organic_social'),
                    URL.replace('issue_03_zen12','alice@example.com'),URL+'#section',
                    URL.replace('&utm_content=issue_03_zen12',''),
                    URL.replace('dispatch','partner',1)]
        for bad in variants:
            with self.subTest(url=bad), self.assertRaises(ValueError):
                validate_owned_utm(bad)

    def test_no_settlements(self):
        self.assertEqual(revenue_per_1000(100, [], True)['status'],'NOT_COMPUTABLE')
        self.assertEqual(revenue_per_1000(0, [TX], True)['status'],'NOT_COMPUTABLE')
        self.assertEqual(revenue_per_1000(100, [TX], False)['status'],'NOT_COMPUTABLE')

    def test_settled_values(self):
        out = revenue_per_1000(100, [TX], True)
        self.assertEqual(out['net_revenue'],'12.00')
        self.assertEqual(out['net_per_1000_qualified_sessions'],'120.00')

    def test_negative_revenue_visible(self):
        out = revenue_per_1000(100,[dict(TX, refunded_amount='20.00')],True)
        self.assertEqual(out['net_revenue'],'-8.00')

    def test_unsettled_and_duplicates(self):
        for rows in ([dict(TX,status='pending')],[dict(TX,source='website_click')],
                     [TX,TX],[dict(TX,fees='')], [dict(TX,fees='NaN')],
                     [dict(TX,fees=3.2)], [dict(TX,transaction_ref='')]):
            with self.subTest(rows=rows):
                self.assertEqual(revenue_per_1000(100,rows,True)['status'],'NOT_COMPUTABLE')

    def test_fail_closed_send(self):
        self.assertFalse(release_decision({})['send_authorized'])
        self.assertEqual(release_decision({})['all_six'],'HOLD_UNSENT')
        self.assertEqual(release_decision({})['issues_03_05'],'HOLD_MERCHANT')

    def test_even_all_true_cannot_send(self):
        required=release_decision({})['missing_evidence']
        got=release_decision({k:True for k in required})
        self.assertEqual(got['missing_evidence'],[])
        self.assertFalse(got['send_authorized'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
