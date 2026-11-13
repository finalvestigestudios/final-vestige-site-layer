"""R347 regression and adversarial tests: no source, social, commerce or CMS writes."""
from __future__ import annotations
from copy import deepcopy
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / 'tools' / 'r347_preparedness_offer_funnel_evidence_hold.py'
spec = spec_from_file_location('r347evidence', PATH)
r = module_from_spec(spec)
spec.loader.exec_module(r)


def campaign():
    return {
        'topic': r.TOPIC, 'asset_id': 'abc123DEF_-',
        'published_post_url': 'https://www.youtube.com/shorts/abc123DEF_-',
        'published_at_utc': '2026-11-10T19:00:00Z', 'platform': 'youtube',
        'utm_campaign': 'family_contacts_pilot_2026_11',
        'utm_content': 'abc123DEF_-', 'landing_url': r.ARCHIVE,
        'free_guide': {'slug': r.GUIDE, 'release_state': 'PRIVATE_QD_HOLD'},
        'optional_tool': {'slug': r.TOOL, 'release_state': 'PRIVATE_QD_HOLD'},
        'product': None,
    }


def cohort(w=7):
    return {
        'window_days': w, 'as_of_date': '2026-11-12',
        'qualified_human_sessions': 120, 'landing_visits': 100,
        'relevant_cta_clicks': 20, 'confirmed_leads': 5,
        'merchant_confirmed_orders': 2, 'gross_usd': '18.00',
        'refunds_usd': '1.00', 'fees_usd': '0.89',
        'asset_id': 'abc123DEF_-', 'utm_campaign': 'family_contacts_pilot_2026_11',
        'evidence_refs': {
            'session_qualification': 'test_session_report_001',
            'consented_measurement': 'test_consent_report_001',
            'lead_confirmation': 'test_lead_report_001',
            'merchant_order_report': 'test_merchant_report_001',
            'merchant_refund_fee_report': 'test_merchant_fees_001',
            'deduplication_method': 'test_dedupe_method_001',
        },
    }


class TestBasics(unittest.TestCase):
    def test_non_empty_safe_fixture_always_hard_hold(self):
        x = r.review(campaign(), [cohort(7),cohort(30)])
        self.assertEqual(x['state'],'STRUCTURAL_EVIDENCE_ONLY_HARD_HOLD')
        self.assertEqual(x['errors'],[])
        for k, v in r.NEVER_PUBLISH.items(): self.assertIs(x[k],v)
        self.assertIsNone(x['kpi_net_revenue_per_1000_qualified_sessions'])
        self.assertFalse(x['externally_authenticated_social_asset'])
        self.assertFalse(x['independently_authenticated_evidence_receipts'])

    def test_no_inputs_hard_hold(self):
        x = r.review()
        self.assertEqual(x['state'],'INVALID_HARD_HOLD')
        self.assertFalse(x['may_publish'])

    def test_absent_cohorts_still_not_verified(self):
        x = r.review(campaign())
        self.assertTrue(x['structural_acceptance'])
        self.assertEqual(x['cohorts_checked'],0)
        self.assertFalse(x['merchant_settled_orders_authenticated'])

    def test_mock_product_remains_unverified(self):
        c = campaign()
        c['product'] = {'candidate_sku':'SAMPLE_HELD_SKU',
                        'candidate_url':'https://payhip.com/b/example',
                        'release_state':'UNAUTHENTICATED_HOLD','rights_review':'UNVERIFIED',
                        'fulfillment_review':'UNVERIFIED','refund_review':'UNVERIFIED'}
        x=r.review(c)
        self.assertTrue(x['structural_acceptance'])
        self.assertFalse(x['owned_preparedness_product_authenticated'])

    def test_native_incomplete_checkout_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            x=r.native_audit(Path(d))
        self.assertEqual(x['state'],'INVALID_HARD_HOLD')
        self.assertTrue(x['errors'])
        self.assertFalse(x['qualified_qd_pass'])

    def test_structural_proof_is_not_proven_revenue(self):
        x = r.review(campaign(),[cohort()])
        self.assertNotIn('gross_usd',x)
        self.assertNotIn('asset_id',x)
        self.assertFalse(x['realized_net_revenue_verified'])

    def test_safe_url(self):
        self.assertTrue(r.safe_url('https://finalvestige.com/preparedness/'))
        self.assertFalse(r.safe_url('https://finalvestige.com/preparedness/?email=alice'))


class TestMutations(unittest.TestCase):
    pass


MUTATORS = [
    ('topic',lambda c: c.__setitem__('topic','unrelated-history-object')),
    ('asset-id-short',lambda c: c.__setitem__('asset_id','a')),
    ('asset-id-empty',lambda c: c.__setitem__('asset_id','')),
    ('asset-id-newline',lambda c: c.__setitem__('asset_id','abc\nBAD')),
    ('asset-id-unicode',lambda c: c.__setitem__('asset_id','猫怪物')),
    ('asset-id-float',lambda c: c.__setitem__('asset_id',4.2)),
    ('utm-asset',lambda c: c.__setitem__('utm_content','wrongasset')),
    ('utm-short',lambda c: c.__setitem__('utm_campaign','bad')),
    ('utm-space',lambda c: c.__setitem__('utm_campaign','bad scheme')),
    ('utm-uppercase',lambda c: c.__setitem__('utm_campaign','Campaign_01')),
    ('unapproved-landing',lambda c: c.__setitem__('landing_url','https://finalvestige.com/family-reunification-card/')),
    ('water-retired',lambda c: c.__setitem__('landing_url','https://finalvestige.com/water-resilience/')),
    ('external-landing',lambda c: c.__setitem__('landing_url','https://payhip.com/b/n1RhV')),
    ('guide-publish',lambda c: c['free_guide'].__setitem__('release_state','LIVE')),
    ('guide-slug',lambda c: c['free_guide'].__setitem__('slug','unreviewed-tool')),
    ('tool-live',lambda c: c['optional_tool'].__setitem__('release_state','PUBLIC')),
    ('tool-confusion',lambda c: c['optional_tool'].__setitem__('slug','reunification-plan')),
    ('product-approved',lambda c: c.__setitem__('product',{'candidate_sku':'PAID_SKU_123','candidate_url':'https://payhip.com/b/example','release_state':'ACTIVE','rights_review':'APPROVED','fulfillment_review':'PASSED','refund_review':'UNVERIFIED'})),
    ('product-missing-fields',lambda c: c.__setitem__('product',{'candidate_sku':'PAID_SKU_123'})),
    ('product-http',lambda c: c.__setitem__('product',{'candidate_sku':'PAID_SKU_123','candidate_url':'http://payhip.com/b/abc','release_state':'UNAUTHENTICATED_HOLD','rights_review':'UNVERIFIED','fulfillment_review':'UNVERIFIED','refund_review':'UNVERIFIED'})),
    ('product-sku-short',lambda c: c.__setitem__('product',{'candidate_sku':'x','candidate_url':'https://payhip.com/b/abc','release_state':'UNAUTHENTICATED_HOLD','rights_review':'UNVERIFIED','fulfillment_review':'UNVERIFIED','refund_review':'UNVERIFIED'})),
    ('false-approval',lambda c: c.__setitem__('qd_pass',True)),
    ('revenue-fake',lambda c: c.__setitem__('revenue_per_1000',1000)),
    ('extra-key',lambda c: c.__setitem__('extra','x')),
    ('missing-key',lambda c: c.pop('platform')),
    ('platform-other',lambda c: c.__setitem__('platform','telegram')),
    ('post-mismatch',lambda c: c.__setitem__('published_post_url','https://www.youtube.com/shorts/DifferentId')),
    ('post-channel',lambda c: c.__setitem__('published_post_url','https://www.youtube.com/@somechannel')),
    ('post-host',lambda c: c.__setitem__('published_post_url','https://github.com/shorts/abc123DEF_-')),
    ('post-tiktok-platform',lambda c: c.__setitem__('platform','tiktok')),
    ('post-query-email',lambda c: c.__setitem__('published_post_url','https://www.youtube.com/shorts/abc123DEF_-?email=me')),
    ('post-insecure',lambda c: c.__setitem__('published_post_url','http://www.youtube.com/shorts/abc123DEF_-')),
    ('post-userinfo',lambda c: c.__setitem__('published_post_url','https://user:pass@www.youtube.com/shorts/abc123DEF_-')),
    ('post-port',lambda c: c.__setitem__('published_post_url','https://www.youtube.com:8443/shorts/abc123DEF_-')),
    ('post-future',lambda c: c.__setitem__('published_at_utc','2099-01-01T00:00:00Z')),
    ('post-local-date',lambda c: c.__setitem__('published_at_utc','2026-11-10T10:00:00-08:00')),
    ('post-date-invalid',lambda c: c.__setitem__('published_at_utc','2026-14-10T10:00:00Z')),
    ('post-pretend-publish',lambda c: c.__setitem__('published_at_utc','')),
    ('pii-key',lambda c: c.__setitem__('user_email','test@example.com')),
]
for i,(label,fn) in enumerate(MUTATORS):
    def test(self, mutate=fn):
        c=campaign();mutate(c)
        result=r.review(c)
        self.assertEqual(result['state'],'INVALID_HARD_HOLD')
        self.assertTrue(result['errors'])
        self.assertFalse(result['may_publish'])
    setattr(TestMutations,'test_campaign_mutation_%02d_%s'%(i,label.replace('-','_')),test)


class TestCohortMutations(unittest.TestCase):
    pass

COHORT_MUTATIONS=[
 ('window',lambda x:x.__setitem__('window_days',14)),
 ('window_bool',lambda x:x.__setitem__('window_days',True)),
 ('window_string',lambda x:x.__setitem__('window_days','7')),
 ('future_date',lambda x:x.__setitem__('as_of_date','2099-01-01')),
 ('bad_date',lambda x:x.__setitem__('as_of_date','2026-11-35')),
 ('bad_timestamp',lambda x:x.__setitem__('as_of_date','2026/11/12')),
 ('sessions_negative',lambda x:x.__setitem__('qualified_human_sessions',-1)),
 ('sessions_float',lambda x:x.__setitem__('qualified_human_sessions',4.8)),
 ('sessions_boolean',lambda x:x.__setitem__('qualified_human_sessions',True)),
 ('landing_over_sessions',lambda x:x.__setitem__('landing_visits',121)),
 ('clicks_over_landing',lambda x:x.__setitem__('relevant_cta_clicks',101)),
 ('lead_over_click',lambda x:x.__setitem__('confirmed_leads',21)),
 ('orders_over_click',lambda x:x.__setitem__('merchant_confirmed_orders',22)),
 ('orders_no_report',lambda x:x['evidence_refs'].__setitem__('merchant_order_report',None)),
 ('leads_no_report',lambda x:x['evidence_refs'].__setitem__('lead_confirmation',None)),
 ('sessions_no_report',lambda x:x['evidence_refs'].__setitem__('session_qualification',None)),
 ('fees_no_report',lambda x:x['evidence_refs'].__setitem__('merchant_refund_fee_report',None)),
 ('gross_no_orders',lambda x:x.__setitem__('merchant_confirmed_orders',0)),
 ('fees_over_gross',lambda x:x.__setitem__('fees_usd','19.00')),
 ('refunds_over_gross',lambda x:x.__setitem__('refunds_usd','19.00')),
 ('negative_revenue',lambda x:x.__setitem__('gross_usd','-1.00')),
 ('numeric_revenue',lambda x:x.__setitem__('gross_usd',18)),
 ('one_decimal',lambda x:x.__setitem__('gross_usd','18.0')),
 ('too_many_digits',lambda x:x.__setitem__('gross_usd','1000000000000.00')),
 ('claim_verified',lambda x:x.__setitem__('verified_revenue',True)),
 ('cohort_email',lambda x:x.__setitem__('buyer_email','test@example.com')),
 ('reference_url',lambda x:x['evidence_refs'].__setitem__('merchant_order_report','https://example.com')),
 ('reference_empty',lambda x:x['evidence_refs'].__setitem__('merchant_order_report','')),
 ('reference_missing',lambda x:x['evidence_refs'].pop('deduplication_method')),
 ('asset_mismatch',lambda x:x.__setitem__('asset_id','notasset')),
 ('campaign_mismatch',lambda x:x.__setitem__('utm_campaign','something_else')),
 ('missing_key',lambda x:x.pop('refunds_usd')),
 ('bogus_order_leads',lambda x:x.__setitem__('confirmed_leads',10000)),
 ('zero_gross_with_orders',lambda x:x.__setitem__('gross_usd','0.00')),
]
for i,(label,fn) in enumerate(COHORT_MUTATIONS):
    def test(self, mutate=fn):
        x=cohort();mutate(x)
        result=r.review(campaign(),[x])
        self.assertEqual(result['state'],'INVALID_HARD_HOLD')
        self.assertTrue(result['errors'])
        self.assertIsNone(result.get('kpi_net_revenue_per_1000_qualified_sessions'))
    setattr(TestCohortMutations,'test_cohort_mutation_%02d_%s'%(i,label),test)


class TestCrossCohort(unittest.TestCase):
    def test_duplicate_7_day(self):
        self.assertIn('INVALID_OR_DUPLICATE_COHORT_WINDOW',r.review(campaign(),[cohort(),cohort()])['errors'])
    def test_more_than_two(self):
        self.assertIn('ONLY_7_AND_30_DAY_COHORTS',r.review(campaign(),[cohort(7),cohort(30),cohort(7)])['errors'])
    def test_non_list(self):
        self.assertIn('COHORTS_MUST_BE_LIST',r.review(campaign(),'oops')['errors'])
    def test_non_dict(self):
        self.assertIn('INVALID_OR_SENSITIVE_COHORT',r.review(campaign(),[None])['errors'])
    def test_two_distinct_windows(self):
        self.assertEqual(r.review(campaign(),[cohort(7),cohort(30)])['errors'],[])
    def test_30_day_window_fewer_sessions(self):
        a,b=cohort(7),cohort(30)
        b['qualified_human_sessions']=119
        self.assertIn('LONGER_WINDOW_FEWER_EVENTS:qualified_human_sessions',r.review(campaign(),[a,b])['errors'])
    def test_30_day_window_fewer_orders(self):
        a,b=cohort(7),cohort(30)
        b['merchant_confirmed_orders']=1
        self.assertIn('LONGER_WINDOW_FEWER_EVENTS:merchant_confirmed_orders',r.review(campaign(),[a,b])['errors'])
    def test_mismatched_cohort_dates(self):
        a,b=cohort(7),cohort(30)
        b['as_of_date']='2026-11-11'
        self.assertIn('CROSS_WINDOW_AS_OF_DATE_MISMATCH',r.review(campaign(),[a,b])['errors'])
    def test_only_30_day_window(self):
        self.assertEqual(r.review(campaign(),[cohort(30)])['errors'],[])
    def test_empty_cohort_list(self):
        self.assertEqual(r.review(campaign(),[])['errors'],[])


if __name__ == '__main__': unittest.main()
