"""Synthetic, offline, adversarial tests. No media posts, real family data or commerce access."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE=Path(__file__).parents[1]/'tools'/'r157_preparedness_funnel_gate.py'
spec=importlib.util.spec_from_file_location('r157_guard',MODULE)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def proposal():
    return gate.proposed_contract()


class Contract(unittest.TestCase):
    def test_baseline_fails_closed(self):
        v=gate.admission(proposal())
        self.assertEqual(v['status'],'DRAFT_HARD_HOLD')
        self.assertFalse(v['creator_asset_observed'])
        self.assertFalse(v['public_release_allowed'])
        self.assertIsNone(v['confirmed_sales'])
    def test_known_creator_asset_still_holds(self):
        x=proposal()
        x['social']={'platform':'youtube','asset_id':'realasset_2026_11',
            'published_post_url':'https://www.youtube.com/watch?v=example',
            'cta_placement':'pinned_sources_comment','utm_campaign':'preparedness_pilot_2026_11'}
        self.assertTrue(gate.admission(x)['creator_asset_observed'])
        self.assertFalse(gate.admission(x)['marketing_allowed'])
    def test_safe_guide_card_paths(self):
        x=proposal()
        self.assertEqual(gate.safe_url(x['guide_url'],expected=gate.EXPECTED['guide']),gate.EXPECTED['guide'])
        self.assertEqual(gate.safe_url(x['card_url'],expected=gate.EXPECTED['card']),gate.EXPECTED['card'])
    def test_draft_metadata_and_source_report(self):
        report={'status':'DRAFT_HARD_HOLD','family_source_relationships':11,
                'family_citation_occurrences':16,'other_review_tasks_still_pending':64,
                'critical_source_scope':2,'blocked_retrieval_not_link_death':6,
                'source_safety_qd_approved':False,'public_release_allowed':False,'workorders':[{}]*11}
        self.assertEqual(gate.admission(proposal(),source_report=report,
                guide_meta={'slug':gate.GUIDE,'status':{'publish':'draft'}},
                card_meta={'slug':gate.CARD,'status':{'publish':'draft'}})['status'],'DRAFT_HARD_HOLD')
        for field,val in [('family_source_relationships',10),('public_release_allowed',True),
                          ('source_safety_qd_approved',True),('blocked_retrieval_not_link_death',5)]:
            y=copy.deepcopy(report);y[field]=val
            with self.subTest(field=field),self.assertRaises(ValueError):
                gate.admission(proposal(),source_report=y)
    def test_invalid_checkout_never_zero_exit(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(gate.main(['--repo',d]),2)
    def test_json_contract_round_trip(self):
        self.assertEqual(gate.admission(json.loads(json.dumps(proposal())))['status'],'DRAFT_HARD_HOLD')
    def test_source_blob_known(self):
        self.assertEqual(gate.blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_urls_fail_adversarial_cases(self):
        base='https://finalvestige.com'+gate.EXPECTED['guide']
        for bad in [base+'?email=foo',base+'#a','http://finalvestige.com'+gate.EXPECTED['guide'],
                    'https://evil.com'+gate.EXPECTED['guide'],'https://finalvestige.com//preparedness/',
                    'https://finalvestige.com/preparedness/%2e%2e/',
                    'https://finalvestige.com@attacker.example/preparedness/start-here/household-emergency-plan/',
                    base.replace('/start-here/','/water/'),'https://finalvestige.com/preparedness/start-here/household-emergency-plan',
                    42,None,'https://finalvestige.com/preparedness/']:
            x=proposal();x['guide_url']=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError):gate.admission(x)
    def test_sensitive_unsupported_mutations(self):
        patches=[('guide_requires_signup',True),('guide_requires_payment',True),
                 ('card_label','Guaranteed safe!'),('topic','water-treatment'),
                 ('audience','everyone'),('schema','altered')]
        for key,val in patches:
            x=proposal();x[key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):gate.admission(x)
    def test_social_partial_is_not_complete(self):
        for key,val in [('platform','youtube'),('asset_id','real_asset'),
                        ('published_post_url','https://youtube.com/watch?v=ok'),
                        ('utm_campaign','preparedness_pilot_2026_11'),('cta_placement','profile_bio')]:
            x=proposal();x['social'][key]=val
            with self.subTest(key=key),self.assertRaises(ValueError):gate.admission(x)
    def test_social_invalid_fields(self):
        good={'platform':'youtube','asset_id':'realasset_2026_11',
              'published_post_url':'https://youtube.com/watch?v=real',
              'cta_placement':'profile_bio','utm_campaign':'preparedness_pilot_2026_11'}
        for key,values in [('platform',['fake','twitter']),('asset_id',['guess','bad id',None]),
                           ('published_post_url',['http://youtube.com','https://finalvestige.com/preparedness/','https://evil@youtube.com/']),
                           ('cta_placement',['spoken_script','email_spam']),('utm_campaign',['random','preparedness_pilot_2026_10'])]:
            for value in values:
                x=proposal();x['social']=dict(good);x['social'][key]=value
                with self.subTest(key=key,value=value),self.assertRaises(ValueError):gate.admission(x)
    def test_paid_offer_forgery_rejected(self):
        for key,value in [('sku','fake-paid-pack'),('checkout_url','https://payhip.com/fake'),
                          ('paid_cta_enabled',True),('rights_verified',True),
                          ('listing_live_verified',True),('delivery_verified',True),('refund_terms_verified',True)]:
            x=proposal();x['merchant'][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):gate.admission(x)
    def test_approval_forgery_rejected(self):
        for key in proposal()['evidence']:
            x=proposal();x['evidence'][key]=True
            with self.subTest(key=key),self.assertRaises(ValueError):gate.admission(x)
    def test_false_metrics_rejected(self):
        for key in proposal()['metrics']:
            for value in (0,1,250.0,False):
                x=proposal();x['metrics'][key]=value
                with self.subTest(key=key,value=value),self.assertRaises(ValueError):gate.admission(x)
    def test_metadata_published_rejected(self):
        for key in ('draft', 'published','reviewed'):
            x={'slug':gate.GUIDE,'status':{'publish':key}}
            if key=='draft':self.assertEqual(gate.admission(proposal(),guide_meta=x)['status'],'DRAFT_HARD_HOLD')
            else:
                with self.assertRaises(ValueError):gate.admission(proposal(),guide_meta=x)
    def test_section_removal_fails(self):
        for section in ('social','merchant','evidence','metrics'):
            x=proposal();del x[section]
            with self.subTest(section=section),self.assertRaises(ValueError):gate.admission(x)


# Each named guard is materialized into a distinct unittest method for regression reporting.
for field in ['source_review_approved','independent_qd_pass','browser_privacy_print_pass','founder_release_approved']:
    def make(field=field):
        def t(self):
            x=proposal();x['evidence'][field]=True
            with self.assertRaises(ValueError):gate.admission(x)
        return t
    setattr(Contract,'test_individual_forged_'+field,make())
for field in ['qualified_human_sessions','verified_paid_orders','gross','fees','refunds','realized_net_revenue_per_1000']:
    def make(field=field):
        def t(self):
            x=proposal();x['metrics'][field]=0
            with self.assertRaises(ValueError):gate.admission(x)
        return t
    setattr(Contract,'test_individual_unverified_metric_'+field,make())
for field in ['sku','checkout_url','rights_verified','listing_live_verified','delivery_verified','refund_terms_verified','paid_cta_enabled']:
    def make(field=field):
        def t(self):
            x=proposal();x['merchant'][field]='unverified' if field in ('sku','checkout_url') else True
            with self.assertRaises(ValueError):gate.admission(x)
        return t
    setattr(Contract,'test_individual_unapproved_merchant_'+field,make())
for field in ['platform','asset_id','published_post_url','cta_placement','utm_campaign']:
    def make(field=field):
        def t(self):
            x=proposal();x['social'][field]='placeholder'
            with self.assertRaises(ValueError):gate.admission(x)
        return t
    setattr(Contract,'test_individual_partial_social_'+field,make())
for field in ['guide_requires_signup','guide_requires_payment','card_label','topic','audience','schema']:
    def make(field=field):
        def t(self):
            x=proposal();x[field]=True
            with self.assertRaises(ValueError):gate.admission(x)
        return t
    setattr(Contract,'test_individual_drift_'+field,make())

if __name__=='__main__':unittest.main()
