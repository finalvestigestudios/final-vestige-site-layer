"""R112 synthetic, isolated and fail-closed source/offer/measurement tests."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

MOD = Path(__file__).resolve().parents[1] / 'tools' / 'r112_preparedness_conversion_hold.py'
spec = importlib.util.spec_from_file_location('r112', MOD)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

BODY = '<section class="pa-act"><h2>What to do now</h2><p>Follow local officials.{{cite:one}}{{cite:two}}{{cite:three}}</p></section>'
META = {'slug':'household-emergency-plan','section':'start-here','track':'modern',
        'status':{'editorial':'drafted','publish':'draft'},
        'safety_review':{'state':'pending'},
        'source_use':{'one':'scope 1','two':'scope 2','three':'scope 3'}}
TAX = {'base_path':'/preparedness/','slate':[{'slug':'household-emergency-plan','section':'start-here','gate':True}]}
CAM = {'asset_id':'FV-grok_20261103_01','utm_source':'youtube','utm_medium':'organic_social',
       'utm_campaign':'preparedness_pilot_2026_11','utm_content':'FV-grok_20261103_01',
       'landing_url':g.LANDING,'post_url':'https://www.youtube.com/watch?v=abc123','posted':True}
OFFER = {'sku':'FV-HOME-01','ownership':'FINAL_VESTIGE_STUDIOS','offer_kind':'owned_digital_pack',
         'checkout_url':'https://payhip.com/b/123abc',
         'receipts':{k:{'reviewed':True,'evidence_id':'seller/verified-001'} for k in g.REQUIRED_PROOFS},
         'core_emergency_info_free':True,'matches_household_plan':True,
         'disclosure':'Optional paid download; the emergency guide is free.'}
COHORT={'window_days':7,'human_qualification_method':'documented_approved',
        'merchant_origin':'payhip_export_confirmed',
        'attribution_method':'same_asset_id_campaign_confirmed',
        'qualified_sessions':100,'paid_orders':4,'refunded_orders':1,
        'gross_paid_usd':'100.00','refunds_usd':'25.00','fees_usd':'5.00',
        **{k+'_source_verified':True for k in g.RECEIPT_FIELDS}}

def params():
    return (copy.deepcopy(META), BODY, copy.deepcopy(TAX), copy.deepcopy(CAM), copy.deepcopy(OFFER))

class Baseline(unittest.TestCase):
    def test_draft_only_even_complete_forged_reviewer_attestations(self):
        result=g.evaluate(*params())
        self.assertTrue(result['candidate_for_manual_draft_review'])
        self.assertFalse(result['buyer_click_target_enabled'])
        self.assertFalse(result['may_publish'])
        self.assertFalse(result['checkout_verified_by_tool'])
        self.assertEqual(result['release_state'],'HOLD')
    def test_realistic_unverified_offer_holds(self):
        a=list(params());a[-1]={}
        result=g.evaluate(*a)
        self.assertFalse(result['candidate_for_manual_draft_review'])
        self.assertIn('SELLER_SKU_NOT_VERIFIED',result['hold_reasons'])
    def test_grok_asset_not_assigned_holds(self):
        a=list(params());a[3]['asset_id']='PENDING'
        self.assertIn('GROK_ASSET_ID_NOT_ACKNOWLEDGED',g.evaluate(*a)['hold_reasons'])
    def test_article_not_human_safe(self):
        self.assertEqual(g.article_gate(META,BODY,TAX)['current_release_state'],
                         'DRAFT_PENDING_QUALIFIED_SAFETY_REVIEW')
    def test_repeatability_and_inputs_unchanged(self):
        a=params();b=copy.deepcopy(a)
        self.assertEqual(g.evaluate(*a),g.evaluate(*a))
        self.assertEqual(a,b)
    def test_real_utm_source_scope_and_separation(self):
        self.assertIn('merchant_confirmed_paid_order',g.evaluate(*params())['events'])
        self.assertNotIn('affiliate_click_as_sale',g.evaluate(*params())['events'])
    def test_valid_synthetic_paid_math(self):
        x=g.cohort_metrics(COHORT)
        self.assertEqual(x['realized_net_usd'],'70.00')
        self.assertEqual(x['net_usd_per_1000_qualified_sessions'],'700.00')
        self.assertTrue(x['small_sample_warning'])
        self.assertEqual(x['source_confirmation'],'REVIEWER_REPORTED_NOT_INDEPENDENTLY_OBSERVED')
    def test_medium_sample_warning(self):
        c=copy.deepcopy(COHORT);c.update(qualified_sessions=500,paid_orders=20,refunded_orders=1)
        self.assertFalse(g.cohort_metrics(c)['small_sample_warning'])
    def test_cannot_compute_n_a_from_zero_sessions(self):
        c=copy.deepcopy(COHORT);c.update(qualified_sessions=0,paid_orders=0,refunded_orders=0)
        with self.assertRaises(g.Hold):g.cohort_metrics(c)
    def test_no_personal_data_fields_in_outputs(self):
        result=g.evaluate(*params()); self.assertNotIn('buyer_email',str(result))
        self.assertNotIn('post_url',str(result))

# Distinct adversarial mutations are each an independently counted unittest.
ARTICLE_BAD = [
  ('slug', lambda a:a[0].update(slug='other')),
  ('section',lambda a:a[0].update(section='water')),
  ('track',lambda a:a[0].update(track='lost-ways')),
  ('status_published',lambda a:a[0]['status'].update(publish='published')),
  ('status_reviewed',lambda a:a[0]['status'].update(editorial='approved')),
  ('safety_fake_approval',lambda a:a[0]['safety_review'].update(state='approved')),
  ('sources_drop',lambda a:a[0].update(source_use={'one':'x'})),
  ('sources_empty',lambda a:a[0]['source_use'].update(three='')),
  ('slate_missing',lambda a:a[2].update(slate=[])),
  ('slate_duplicate',lambda a:a[2]['slate'].append(copy.deepcopy(a[2]['slate'][0]))),
  ('slate_ungated',lambda a:a[2]['slate'][0].update(gate=False)),
  ('slate_wrong_section',lambda a:a[2]['slate'][0].update(section='food')),
  ('slate_bad_base',lambda a:a[2].update(base_path='/')),
]
for name, mutate in ARTICLE_BAD:
    def make(m):
        def test(self):
            a=list(params());m(a)
            with self.assertRaises(g.Hold):g.evaluate(*a)
        return test
    setattr(Baseline,'test_article_tamper_'+name,make(mutate))

CAMPAIGN_BAD = [
 ('no_asset', 'asset_id', None, 'GROK_ASSET_ID_NOT_ACKNOWLEDGED'),
 ('short_asset', 'asset_id', 'FV-z', 'GROK_ASSET_ID_NOT_ACKNOWLEDGED'),
 ('bad_asset', 'asset_id', 'abc', 'GROK_ASSET_ID_NOT_ACKNOWLEDGED'),
 ('other_platform', 'utm_source', 'reddit', 'PLATFORM_NOT_CONFIRMED'),
 ('paid_source', 'utm_medium', 'paid_search', 'MEDIUM_CONTRACT_MISMATCH'),
 ('utm_wrong_campaign', 'utm_campaign', 'pilot', 'CAMPAIGN_CONTRACT_MISMATCH'),
 ('utm_wrong_month', 'utm_campaign', 'preparedness_pilot_2026_13', 'CAMPAIGN_CONTRACT_MISMATCH'),
 ('asset_mismatch', 'utm_content', 'FV-other', 'UTM_ASSET_ID_MISMATCH'),
 ('alternate_landing', 'landing_url', '/preparedness/', 'NONCANONICAL_OR_UNVERIFIED_LANDING'),
 ('query_in_landing', 'landing_url', g.LANDING+'?utm_source=ad', 'NONCANONICAL_OR_UNVERIFIED_LANDING'),
 ('no_post', 'post_url', None, 'POST_URL_NOT_SUPPLIED'),
 ('insecure_post', 'post_url', 'http://youtube.com/a', 'POST_URL_INVALID'),
 ('creds_post', 'post_url', 'https://user:pass@youtube.com/a', 'POST_URL_INVALID'),
 ('not_posted', 'posted', False, 'GROK_POST_NOT_VERIFIED'),
]
for name,key,value,reason in CAMPAIGN_BAD:
    def make(k,v,why):
        def test(self):
            a=list(params());a[3][k]=v
            x=g.evaluate(*a)
            self.assertIn(why,x['hold_reasons'])
            self.assertFalse(x['candidate_for_manual_draft_review'])
        return test
    setattr(Baseline,'test_campaign_'+name,make(key,value,reason))

OFFER_BAD = [
 ('sku_none','sku',None,'SELLER_SKU_NOT_VERIFIED'),
 ('sku_bad','sku','X','SELLER_SKU_NOT_VERIFIED'),
 ('seller','ownership','third_party','SELLER_OWNERSHIP_UNVERIFIED'),
 ('affiliate','offer_kind','affiliate','INAPPROPRIATE_OR_UNAPPROVED_OFFER'),
 ('url_external','checkout_url','https://evil.example/checkout','PAYHIP_MERCHANT_URL_UNVERIFIED'),
 ('url_http','checkout_url','http://payhip.com/b/123abc','PAYHIP_MERCHANT_URL_UNVERIFIED'),
 ('url_fake','checkout_url','https://payhip.com.evil.example/b/123abc','PAYHIP_MERCHANT_URL_UNVERIFIED'),
 ('url_creds','checkout_url','https://u:p@payhip.com/b/123abc','PAYHIP_MERCHANT_URL_UNVERIFIED'),
 ('url_query','checkout_url','https://payhip.com/b/123abc?email=a','PAYHIP_MERCHANT_URL_UNVERIFIED'),
 ('url_fragment','checkout_url','https://payhip.com/b/123abc#x','PAYHIP_MERCHANT_URL_UNVERIFIED'),
 ('url_space','checkout_url','https://payhip.com/b/ab c','PAYHIP_MERCHANT_URL_UNVERIFIED'),
 ('free_gated','core_emergency_info_free',False,'ESSENTIAL_SAFETY_CONTENT_CANNOT_BE_GATED'),
 ('wrong_product','matches_household_plan',False,'AUDIENCE_OFFER_MISMATCH'),
 ('weak_disclosure','disclosure','Download now','PAID_OPTION_DISCLOSURE_MISSING'),
]
for name,key,value,reason in OFFER_BAD:
    def make(k,v,why):
        def test(self):
            a=list(params());a[4][k]=v
            x=g.evaluate(*a);self.assertIn(why,x['hold_reasons'])
        return test
    setattr(Baseline,'test_offer_'+name,make(key,value,reason))

for proof_key in g.REQUIRED_PROOFS:
    def make(k):
        def test(self):
            a=list(params());a[4]['receipts'][k]['reviewed']=False
            self.assertIn('EVIDENCE_MISSING_'+k.upper(),g.evaluate(*a)['hold_reasons'])
        return test
    setattr(Baseline,'test_receipt_unapproved_'+proof_key,make(proof_key))

COHORT_BAD = [
 ('window', 'window_days',14),('method','human_qualification_method','guess'),
 ('merchant','merchant_origin','clicks'),('attribution','attribution_method','view_through_guess'),
 ('order_more_than_session','paid_orders',101),('refund_count','refunded_orders',5),
 ('refund_gt_gross','refunds_usd','125.00'),('fees_gt_gross','fees_usd','126.00'),
 ('negative_gross','gross_paid_usd','-1'),('nonfinite','fees_usd','NaN'),
 ('float_count','paid_orders',1.3),('fractional_count','paid_orders','1.1'),
 ('precision','fees_usd','1.123'),('bad_number','fees_usd','abc')]
for name,key,value in COHORT_BAD:
    def make(k,v):
        def test(self):
            c=copy.deepcopy(COHORT);c[k]=v
            with self.assertRaises(g.Hold):g.cohort_metrics(c)
        return test
    setattr(Baseline,'test_cohort_reject_'+name,make(key,value))

for name in g.RECEIPT_FIELDS:
    def make(k):
        def test(self):
            c=copy.deepcopy(COHORT);c[k+'_source_verified']=False
            with self.assertRaises(g.Hold):g.cohort_metrics(c)
        return test
    setattr(Baseline,'test_cohort_no_merchant_proof_'+name,make(name))

if __name__=='__main__': unittest.main()
