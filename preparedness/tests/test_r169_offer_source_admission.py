"""Synthetic-only adversarial admission tests; cannot confer source or sale approval."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import r169_offer_source_admission as g


def baseline():
    candidate={'schema':g.SCHEMA,'topic':g.TOPIC,
        'guide':{'slug':g.GUIDE,'route':'/preparedness/start-here/household-emergency-plan/',
                 'ungated':True,'price_usd':0,'cta':g.CTA},
        'tool':{'name':'Family Reunification Card','state':g.HOLD,
                'public_url':None,'paid':False},
        'paid_product':None,'social':None,
        'measurement':dict.fromkeys(('qualified_human_sessions','confirmed_leads',
          'merchant_confirmed_orders','affiliate_confirmed_sales',
          'realized_net_usd','cohort_7d','cohort_30d'))}
    metadata={'slug':g.GUIDE,'section':'start-here','status':{'publish':'draft'},
              'source_use':{'ready-gov-plan':'Original author interpretation, not audited.'}}
    custody={'state':g.HOLD,'articles':35,'routes':35,
             'publication_authorized':False,'independent_qd_pass':False}
    return candidate,metadata,custody


def paid():
    return {'sku':'prep-pack-001','offer_name':'Family Readiness Pack',
        'listing':'https://payhip.com/b/prep001',
        'rights_receipt':'a'*64,'delivery_receipt':'b'*64,'refund_receipt':'c'*64}


def social():
    return {'asset_id':'fv-prep-001','platform':'youtube',
        'post_url':'https://www.youtube.com/watch?v=abc123',
        'destination':'https://finalvestige.com/preparedness/start-here/household-emergency-plan/',
        'utms':{'utm_source':'youtube','utm_medium':'organic_social',
                'utm_campaign':'preparedness_pilot_2026_11','utm_content':'fv-prep-001'}}


class TestApprovedScopeStillHardHold(unittest.TestCase):
    def test_empty_receipts_remain_hold(self):
        c,m,k=baseline(); r=g.evaluate(c,m,k)
        self.assertEqual(r['state'],g.HOLD)
        self.assertIsNone(r['realized_net_per_1000_qualified_sessions'])
        self.assertFalse(r['paid_cta_authorized'])
        self.assertTrue(r['synthetic_fixture'])
    def test_paid_evidence_submission_not_approved(self):
        c,m,k=baseline();c['paid_product']=paid();r=g.evaluate(c,m,k)
        self.assertEqual(r['merchant_evidence'],'SUBMITTED_UNVERIFIED')
        self.assertFalse(r['checkout_verified'])
        self.assertFalse(r['paid_cta_authorized'])
    def test_social_evidence_submission_not_verified(self):
        c,m,k=baseline();c['social']=social();r=g.evaluate(c,m,k)
        self.assertEqual(r['social_evidence'],'SUBMITTED_UNVERIFIED')
        self.assertFalse(r['attributed_sales_verified'])
    def test_both_submissions_still_hard_hold(self):
        c,m,k=baseline();c['paid_product']=paid();c['social']=social()
        self.assertFalse(g.evaluate(c,m,k)['publication_authorized'])
    def test_no_creators_or_skus_exposed_in_output(self):
        c,m,k=baseline();c['paid_product']=paid();c['social']=social()
        out=json.dumps(g.evaluate(c,m,k))
        self.assertNotIn('prep-pack-001',out)
        self.assertNotIn('fv-prep-001',out)
    def test_missing_repo_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'proposal.json';f.write_text(json.dumps(baseline()[0]))
            with redirect_stdout(StringIO()) as buf:
                rc=g.main(['--repo',d,'--candidate',str(f)])
            self.assertEqual(rc,2)
            o=json.loads(buf.getvalue());self.assertEqual(o['state'],'INVALID_HARD_HOLD')
            self.assertFalse(o['paid_cta_authorized'])
    def test_unsafe_candidate_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'real.json';src.write_text(json.dumps(baseline()[0]))
            target=Path(d)/'alias.json';target.symlink_to(src)
            with redirect_stdout(StringIO()) as buf:rc=g.main(['--candidate',str(target)])
            self.assertEqual(rc,2)
            self.assertEqual(json.loads(buf.getvalue())['state'],'INVALID_HARD_HOLD')


BAD = [
 ('top_schema',('schema',),'fv-preparedness-r169-v2'),
 ('wrong_topic',('topic',),'mind-perception'),
 ('topic_bool',('topic',),True),
 ('guide_slug',('guide','slug'),'other'),
 ('guide_route',('guide','route'),'/preparedness/other/'),
 ('guide_url_query',('guide','route'),'/preparedness/start-here/household-emergency-plan/?utm_campaign=x'),
 ('guide_gated',('guide','ungated'),False),
 ('guide_price',('guide','price_usd'),5),
 ('guide_price_bool',('guide','price_usd'),True),
 ('guide_cta_safety',('guide','cta'),'This will keep your children safe.'),
 ('guide_cta_sales',('guide','cta'),'Buy now'),
 ('card_visible',('tool','public_url'),'https://finalvestige.com/printable/'),
 ('card_paid',('tool','paid'),True),
 ('card_live',('tool','state'),'LIVE'),
 ('card_approved',('tool','state'),'QD_PASS'),
 ('card_replaced',('tool','name'),'Resilience Pack'),
 ('measure_sessions',('measurement','qualified_human_sessions'),100),
 ('measure_subscribers',('measurement','confirmed_leads'),5),
 ('measure_orders',('measurement','merchant_confirmed_orders'),1),
 ('measure_affiliates',('measurement','affiliate_confirmed_sales'),3),
 ('measure_net',('measurement','realized_net_usd'),450),
 ('measure_7d',('measurement','cohort_7d'),{'count':2}),
 ('measure_30d',('measurement','cohort_30d'),{'count':3}),
 ('measure_forged_zero',('measurement','merchant_confirmed_orders'),0),
 ('measure_fake_nan',('measurement','realized_net_usd'),float('nan')),
]
BAD_PAID = [
 ('paid_retired',('paid_product','offer_name'),'Water Resilience Field Manual'),
 ('paid_old_manual',('paid_product','offer_name'),'old water field manual'),
 ('paid_sku_space',('paid_product','sku'),'bad sku'),
 ('paid_sku_path',('paid_product','sku'),'../private'),
 ('paid_sku_upper',('paid_product','sku'),'SKU123'),
 ('paid_sku_bool',('paid_product','sku'),True),
 ('paid_missing_rights',('paid_product','rights_receipt'),None),
 ('paid_bad_rights',('paid_product','rights_receipt'),'unverified'),
 ('paid_short_rights',('paid_product','rights_receipt'),'a'*20),
 ('paid_bad_delivery',('paid_product','delivery_receipt'),'a'*63),
 ('paid_bad_refund',('paid_product','refund_receipt'),'f'*65),
 ('paid_http',('paid_product','listing'),'http://payhip.com/b/item'),
 ('paid_lookalike',('paid_product','listing'),'https://payhip.com.evil.test/b/item'),
 ('paid_auth',('paid_product','listing'),'https://user:pass@payhip.com/b/item'),
 ('paid_query',('paid_product','listing'),'https://payhip.com/b/item?private=1'),
 ('paid_fragment',('paid_product','listing'),'https://payhip.com/b/item#promo'),
 ('paid_not_product',('paid_product','listing'),'https://payhip.com/home'),
 ('paid_backslash',('paid_product','listing'),'https://payhip.com\\@evil.test/b/item'),
]
BAD_SOCIAL = [
 ('social_bad_platform',('social','platform'),'threads'),
 ('social_bad_asset',('social','asset_id'),'not my id'),
 ('social_bad_id',('social','asset_id'),'../../etc'),
 ('social_empty_id',('social','asset_id'),''),
 ('social_bad_host',('social','post_url'),'https://youtube.com.evil.test/watch'),
 ('social_http',('social','post_url'),'http://www.youtube.com/watch?v=abc123'),
 ('social_url_query',('social','post_url'),'https://www.youtube.com/watch?v=abc123&x=1'),
 ('social_wrong_tiktok',('social','post_url'),'https://www.tiktok.com/@creator'),
 ('social_redirect',('social','destination'),'https://example.com/preparedness/'),
 ('social_unguarded_route',('social','destination'),'https://finalvestige.com/'),
 ('social_injected_utm',('social','utms','utm_source'),'google'),
 ('social_utm_paid',('social','utms','utm_medium'),'paid_social'),
 ('social_utm_date',('social','utms','utm_campaign'),'preparedness_pilot_2026_12'),
 ('social_utm_mismatch',('social','utms','utm_content'),'another-video'),
]
BAD_META = [
 ('meta_slug',('slug',),'unsafe'),
 ('meta_section',('section',),'food'),
 ('meta_live',('status','publish'),'publish'),
 ('meta_pending',('status','publish'),None),
 ('meta_missing_sources',('source_use',),{}),
]
BAD_CUSTODY = [
 ('custody_34',('articles',),34),
 ('custody_36',('routes',),36),
 ('custody_safety_pass',('independent_qd_pass',),True),
 ('custody_published',('publication_authorized',),True),
 ('custody_invalid',('state',),'VERIFIED'),
]


def setpath(d,path,value):
    cur=d
    for k in path[:-1]:cur=cur[k]
    cur[path[-1]]=value


def build_test(name,path,value,object_type):
    def test(self):
        c,m,k=baseline()
        if object_type=='paid':c['paid_product']=paid()
        if object_type=='social':c['social']=social()
        target={'candidate':c,'paid':c,'social':c,'meta':m,'custody':k}[object_type]
        setpath(target,path,value)
        with self.assertRaises(ValueError):g.evaluate(c,m,k)
    test.__name__='test_reject_'+name
    return test

for name,path,value in BAD:
    setattr(TestApprovedScopeStillHardHold,'test_reject_'+name,build_test(name,path,value,'candidate'))
for name,path,value in BAD_PAID:
    setattr(TestApprovedScopeStillHardHold,'test_reject_'+name,build_test(name,path,value,'paid'))
for name,path,value in BAD_SOCIAL:
    setattr(TestApprovedScopeStillHardHold,'test_reject_'+name,build_test(name,path,value,'social'))
for name,path,value in BAD_META:
    setattr(TestApprovedScopeStillHardHold,'test_reject_'+name,build_test(name,path,value,'meta'))
for name,path,value in BAD_CUSTODY:
    setattr(TestApprovedScopeStillHardHold,'test_reject_'+name,build_test(name,path,value,'custody'))

if __name__=='__main__':unittest.main()
