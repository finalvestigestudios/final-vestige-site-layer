import copy
import unittest
from settlement_truth import evaluate, UnsafeLedger

T = '2026-11-05T19:30:00Z'


def event(kind, n, **kw):
    result = dict(id=f'evid{n:03d}', kind=kind, ts='2026-11-02T19:30:00Z', journey='journey0001', evidence_ref='report/export/2026-11-05/0001')
    result.update(kw)
    return result


def landing(n=1):
    return event('landing', n, asset_id='grok_asset_0001', utm_source='tiktok', utm_medium='organic_social', utm_content='grok_asset_0001', utm_campaign='mind_pilot_2026_11', human_evidence_type='reviewed_bot_filtered_session_export')


def signup(n=3):
    return event('confirmed_signup', n, evidence_type='native_provider_confirmed_subscription')


def order(n=4):
    return event('paid_order', n, order_key='opaqueorder001', evidence_type='independent_order_report')


def settlement(n=5):
    return event('settlement', n, order_key='opaqueorder001', evidence_type='independent_payment_or_affiliate_settlement', gross_usd='20.00', fees_usd='1.25', refunds_usd='4.50')


def coverage(complete=True):
    return {k: dict(status='independently_reconciled' if complete else 'unverified', evidence_ref='report/export/2026-11-05/full') for k in ('qualified_session_feed','orders_feed','settlements_feed','native_consent_feed')}


class CohortAudit(unittest.TestCase):
    def setUp(self): self.ledger = dict(events=[landing(), event('cta', 2), signup(), order(), settlement()], coverage=coverage())
    def report(self): return evaluate(self.ledger, T)

    def test_synthetic_revenue(self):
        c=self.report()['cohorts']['7']; self.assertEqual(c['net_realized_usd'],'14.25');self.assertEqual(c['net_usd_per_1000_qualified_human_sessions'],'14250.00')

    def test_two_cohorts(self):
        r=self.report()['cohorts'];self.assertEqual(r['30']['qualified_human_sessions'],1);self.assertEqual(r['7']['confirmed_signup_journeys'],1)

    def test_missing_coverage_is_unknown_not_zero(self):
        self.ledger['coverage']=coverage(False);self.assertIsNone(self.report()['cohorts']['7']['net_realized_usd'])

    def test_empty_complete_cohort_zero_but_no_rate(self):
        self.ledger['events']=[]; c=self.report()['cohorts']['7'];self.assertEqual(c['net_realized_usd'],'0.00');self.assertIsNone(c['net_usd_per_1000_qualified_human_sessions'])

    def test_double_count_exact_event_replay(self):
        self.ledger['events'].append(copy.deepcopy(self.ledger['events'][-1]));self.assertEqual(self.report()['cohorts']['7']['independently_settled_orders'],1)

    def test_inconsistent_duplicate_fails_evidence(self):
        e=copy.deepcopy(self.ledger['events'][-1]);e['gross_usd']='30.00';self.ledger['events'].append(e);self.assertIn('conflicting_duplicate_event_id',self.report()['rejected_codes'])

    def test_duplicate_order_other_event_does_not_double_count(self):
        e=settlement(8);self.ledger['events'].append(e);r=self.report();self.assertIn('duplicate_settlement_order',r['rejected_codes']);self.assertIsNone(r['cohorts']['7']['independently_settled_orders'])

    def test_broken_native_confirmation_rejected(self):
        self.ledger['events'][2]['evidence_type']='browser_success_banner';r=self.report();self.assertIsNone(r['cohorts']['7']['confirmed_signup_journeys']);self.assertIn('unsupported_confirmed_signup_evidence',r['rejected_codes'])

    def test_click_is_not_sale(self):
        self.ledger['events']=[landing(),event('affiliate_click',7)];r=self.report();self.assertEqual(r['cohorts']['7']['net_realized_usd'],'0.00')

    def test_order_without_settlement_not_paid(self):
        self.ledger['events'].pop();r=self.report();self.assertEqual(r['cohorts']['7']['independently_settled_orders'],0)

    def test_settlement_without_order_not_paid(self):
        self.ledger['events'].pop(-2);r=self.report();self.assertEqual(r['cohorts']['7']['independently_settled_orders'],0)

    def test_large_fake_utm_mismatch(self):
        self.ledger['events'][0]['utm_content']='different_asset';r=self.report();self.assertIn('invalid_asset_attribution',r['rejected_codes'])

    def test_wrong_medium(self):
        self.ledger['events'][0]['utm_medium']='paid';self.assertIn('invalid_social_source',self.report()['rejected_codes'])

    def test_bot_unreviewed(self):
        self.ledger['events'][0]['human_evidence_type']='self_reported';self.assertIn('human_session_not_independently_reviewed',self.report()['rejected_codes'])

    def test_no_checkout_only_price_as_revenue(self):
        self.ledger['events']=[landing(),event('cta',2),event('affiliate_click',6)];self.assertEqual(self.report()['cohorts']['7']['independently_settled_orders'],0)

    def test_no_email_addresses(self):
        self.ledger['email']='person@example.com';self.assertRaises(UnsafeLedger,self.report)

    def test_nested_leak(self):
        self.ledger['details']={'recipient':'secret'};self.assertRaises(UnsafeLedger,self.report)

    def test_no_ip(self):
        self.ledger['metadata']='192.168.1.1';self.assertRaises(UnsafeLedger,self.report)

    def test_no_raw_url(self):
        self.ledger['events'][0]['raw_url']='https://finalvestige.com';self.assertRaises(UnsafeLedger,self.report)

    def test_bad_money(self):
        self.ledger['events'][-1]['gross_usd']='NaN';self.assertIn('unverifiable_settlement_amount',self.report()['rejected_codes'])

    def test_refund_exceeds_receipts(self):
        self.ledger['events'][-1]['refunds_usd']='21.00';self.assertIn('unverifiable_settlement_amount',self.report()['rejected_codes'])

    def test_future_event(self):
        self.ledger['events'][-1]['ts']='2099-01-01T00:00:00Z';self.assertIn('future_event',self.report()['rejected_codes'])

    def test_expired_cohort(self):
        self.ledger['events'][0]['ts']='2026-09-01T19:30:00Z';c=self.report()['cohorts']['30'];self.assertEqual(c['qualified_human_sessions'],0)

    def test_native_consent_not_covered(self):
        self.ledger['coverage']['native_consent_feed']['status']='unverified';c=self.report()['cohorts']['7'];self.assertIsNone(c['confirmed_signup_journeys'])

    def test_no_events_current_unknown(self):
        self.ledger={'events':[], 'coverage':{}};self.assertIsNone(self.report()['cohorts']['7']['qualified_human_sessions'])

    def test_malformed_schema_rejected(self):
        self.ledger['events'].append({'kind':'cta'});self.assertIn('invalid_event_schema',self.report()['rejected_codes'])

    def test_timestamp_requires_timezone(self):
        self.ledger['events'][0]['ts']='2026-11-01T09:00:00';self.assertIn('invalid_time',self.report()['rejected_codes'])

    def test_seller_claim_not_proof(self):
        self.ledger['events'][4]['evidence_type']='seller_promise';self.assertIn('unsupported_settlement_evidence',self.report()['rejected_codes'])

    def test_any_invalid_record_invalidates_all_metrics(self):
        self.ledger['events'].append({'id': 'bad'})
        r = self.report()
        self.assertFalse(r['feed_coverage_independently_attested'])
        self.assertTrue(all(value is None for value in r['cohorts']['30'].values()))

if __name__ == '__main__':unittest.main()
