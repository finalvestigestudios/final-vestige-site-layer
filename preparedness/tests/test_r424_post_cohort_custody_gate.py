"""R424 isolated adversarial fixtures. No production content, checkout or API calls."""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import r424_post_cohort_custody_gate as gate

BASE = json.loads((ROOT/'reviews'/'r421_offer_funnel_hard_hold.json').read_text())
ASSET = 'grok_20261116_ABCDEF'
YT = 'https://www.youtube.com/watch?v=abcdefghijk'
CAMPAIGN = 'family_pilot_2026_11'

def proposed(post=YT, platform='youtube', asset=ASSET):
    x = copy.deepcopy(BASE)
    x['campaign'].update(status='PROPOSED_MATCH',topic='family-emergency-contacts',
        asset_id=asset,platform=platform,post_url=post,asset_rights_checked=True,
        hook_source_checked=True,
        mobile_destination=f'https://finalvestige.com/preparedness/?utm_source={platform}&utm_medium=organic_social&utm_campaign={CAMPAIGN}&utm_content={asset}',
        utm_campaign=CAMPAIGN,utm_content=asset)
    return x

def paid(post=YT,platform='youtube'):
    x=proposed(post,platform)
    x['paid_offer'].update(status='REVIEW_CANDIDATE',sku='fvs_prep_pack_001',
        seller='Final Vestige Studios',merchant_checkout='https://payhip.com/b/Good123',
        refund_terms_url='https://payhip.com/refunds',rights_receipt_sha256='a'*64,
        fulfillment_receipt_sha256='b'*64,merchant_confirmation_sha256='c'*64)
    return x

def cohort(days,sessions=10,orders=1,gross=1000,refund=0,fees=100,hashval=None):
    return dict(days=days,asset_id=ASSET,qualified_human_sessions=sessions,
        verified_paid_orders=orders,gross_cents=gross,refund_cents=refund,
        fees_cents=fees,merchant_receipt_sha256=hashval or ('a'*64 if days==7 else 'b'*64))

def held(tc, obj):
    r=gate.validate(obj)
    for k in ('eligible','publication_approved','safety_qd_approved','paid_activation_approved'):
        tc.assertIs(r[k],False,(k,r))
    tc.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    tc.assertIsNone(r['verified_paid_orders'])
    tc.assertIsNone(r['net_revenue_per_1000_qualified_humans'])
    return r

class Core(unittest.TestCase):
    def test_unmatched_valid_but_held(self):
        r=held(self,BASE)
        self.assertTrue(r['structural_integrity_ok'],r['errors'])
        self.assertIsNone(r['proposed_post_binding'])
    def test_matching_shape_always_unverified(self):
        r=held(self,proposed())
        self.assertTrue(r['structural_integrity_ok'],r['errors'])
        self.assertEqual(r['proposed_post_binding']['authentication'],'UNVERIFIED_REVIEW_ONLY')
        self.assertEqual(r['proposed_post_binding']['publisher_post_id'],'abcdefghijk')
        self.assertEqual(r['proposed_post_binding']['creator_asset_id'],ASSET)
    def test_candidate_receipt_never_releases(self):
        r=held(self,paid());self.assertTrue(r['structural_integrity_ok'],r['errors'])
        self.assertIn('R423_PAYHIP_SHAPE_IS_NOT_VERIFIED_SELLER_PRODUCT_OR_SETTLEMENT',r['holds'])
    def test_parent_accepted_six_char_youtube(self):
        x=proposed('https://youtu.be/ABC123')
        self.assertTrue(gate.r423.validate(x)['structural_integrity_ok'])
        self.assertIn('R424_PUBLISHER_POST_ID_INVALID_OR_UNEXTRACTABLE',held(self,x)['errors'])
    def test_parent_accepted_impossible_nested_cohorts(self):
        x=paid();x['cohorts']=[cohort(7,100,6,6000,200,300),cohort(30,40,2,2000,100,200)]
        self.assertTrue(gate.r423.validate(x)['structural_integrity_ok'])
        r=held(self,x)
        self.assertIn('R424_NESTED_7D_EXCEEDS_30D_QUALIFIED_HUMAN_SESSIONS',r['errors'])
        self.assertIn('R424_NESTED_7D_EXCEEDS_30D_VERIFIED_PAID_ORDERS',r['errors'])
        self.assertIn('R424_NESTED_7D_EXCEEDS_30D_GROSS_CENTS',r['errors'])
    def test_consistent_cohort_shape_still_held_not_sale(self):
        x=paid();x['cohorts']=[cohort(7),cohort(30,100,8,8000,100,700)]
        r=held(self,x);self.assertTrue(r['structural_integrity_ok'],r['errors'])
        self.assertIn('R424_UNDATED_COHORT_WINDOWS_AND_MERCHANT_SETTLEMENT_UNVERIFIED',r['holds'])
    def test_same_merchant_hash_not_receipt_verification(self):
        x=paid();x['cohorts']=[cohort(7),cohort(30,50,3,3000,300,250,'a'*64)]
        r=held(self,x);self.assertIn('R424_IDENTICAL_AGGREGATE_HASHES_REQUIRE_INDEPENDENT_REVIEW',r['holds'])
    def test_same_publisher_id_across_youtube_url_forms(self):
        urls=[YT,'https://youtu.be/abcdefghijk','https://www.youtube.com/shorts/abcdefghijk',
              'https://www.youtube.com/live/abcdefghijk']
        self.assertEqual({gate.publication_id('youtube',u) for u in urls},{'abcdefghijk'})
    def test_creator_id_is_distinct_from_publisher_id(self):
        x=proposed();r=held(self,x)
        self.assertNotEqual(r['proposed_post_binding']['creator_asset_id'],r['proposed_post_binding']['publisher_post_id'])
    def test_determinism_and_immutability(self):
        x=paid();copyx=copy.deepcopy(x)
        self.assertEqual(gate.validate(x),gate.validate(x))
        self.assertEqual(x,copyx)
    def test_digest_changes_on_grok_asset_change(self):
        a=held(self,proposed('https://youtu.be/abcdefghijk'))['proposed_post_binding']['candidate_binding_sha256']
        b=held(self,proposed('https://youtu.be/abcdefghijk',asset='grok_20261116_NEW123'))['proposed_post_binding']['candidate_binding_sha256']
        self.assertNotEqual(a,b)
    def test_digest_changes_on_landing_change(self):
        x=proposed();a=gate.binding_digest(x['campaign'],'abcdefghijk')
        x['campaign']['mobile_destination']+='&extra=1'
        self.assertNotEqual(a,gate.binding_digest(x['campaign'],'abcdefghijk'))
        self.assertFalse(held(self,x)['structural_integrity_ok'])
    def test_invalid_input_never_fails_open(self):
        for obj in (None, [], {}, 'x', 0, {'campaign':{'status':'PROPOSED_MATCH'}}):
            r=held(self,obj)
            self.assertFalse(r['structural_integrity_ok'],obj)
    def test_older_gate_not_modified(self):
        self.assertTrue(gate.r423.validate(BASE)['structural_integrity_ok'])
    def test_missing_source_verification_hold(self):
        self.assertIn('R424_FREE_GUIDE_OFFICIAL_LINKS_NOT_SOURCE_ADJUDICATED',held(self,proposed())['holds'])

class PublisherGood(unittest.TestCase):pass
GOOD=[
    ('youtube','https://www.youtube.com/watch?v=abcdefghijk','abcdefghijk'),
    ('youtube','https://www.youtube.com/watch?v=abcdefghijk&t=20','abcdefghijk'),
    ('youtube','https://youtu.be/abcdefghijk?si=TRK123','abcdefghijk'),
    ('youtube','https://www.youtube.com/shorts/abcdefghijk','abcdefghijk'),
    ('youtube','https://www.youtube.com/live/abcdefghijk','abcdefghijk'),
    ('youtube','https://m.youtube.com/watch?v=abcdefghijk','abcdefghijk'),
    ('tiktok','https://www.tiktok.com/@finalvestige/video/7345678901234567890','7345678901234567890'),
    ('tiktok','https://www.tiktok.com/@finalvestige/video/7345678901234567890?lang=en','7345678901234567890'),
    ('instagram','https://www.instagram.com/reel/ABCDEFG1234/','ABCDEFG1234'),
    ('instagram','https://www.instagram.com/p/ABCDEFG1234?igsh=abc','ABCDEFG1234'),
    ('facebook','https://www.facebook.com/watch/?v=1234567891234','1234567891234'),
    ('facebook','https://www.facebook.com/reel/1234567891234','1234567891234'),
    ('facebook','https://www.facebook.com/finalvestigestudios/videos/1234567891234','1234567891234'),
]
for i,(platform,url,media) in enumerate(GOOD):
    def test(self,p=platform,u=url,m=media):
        self.assertEqual(gate.publication_id(p,u),m)
        r=held(self,proposed(u,p))
        self.assertTrue(r['structural_integrity_ok'],r['errors'])
        self.assertEqual(r['proposed_post_binding']['publisher_post_id'],m)
    setattr(PublisherGood,'test_accepted_%02d'%i,test)

class PublisherBad(unittest.TestCase):pass
BAD=[
 ('youtube','https://www.youtube.com/watch?v=ABC123'),
 ('youtube','https://www.youtube.com/watch?v=ABCDEFGHIJKL'),
 ('youtube','https://youtu.be/123456'),
 ('youtube','https://youtu.be/12345678901234567890'),
 ('youtube','https://www.youtube.com/shorts/abc'),
 ('youtube','https://www.youtube.com/live/AAAAAAAAAAAA'),
 ('youtube','https://www.youtube.com/watch?v=abcdefghijk&redirect=evil'),
 ('youtube','https://www.youtube.com/watch?v=abcdefghijk&email=a@b.com'),
 ('youtube','https://www.youtube.com/watch?v=abcdefghijk&v=12345678901'),
 ('youtube','https://www.youtube.com/watch?v=abcdefghijk#frag'),
 ('tiktok','https://www.tiktok.com/@x/video/7'),
 ('tiktok','https://www.tiktok.com/@finalvestige/video/fakevideoid'),
 ('tiktok','https://www.tiktok.com/@finalvestige/video/7345678901234567890?email=me'),
 ('instagram','https://www.instagram.com/reel/X/'),
 ('instagram','https://www.instagram.com/reel/XYZ1234567/redirect'),
 ('facebook','https://www.facebook.com/watch/?v=X'),
 ('facebook','https://www.facebook.com/reel/ABCDEF'),
 ('facebook','https://www.facebook.com/watch/?v=1234567891234&token=secret'),
 ('facebook','https://www.facebook.com/videos/1234567891234'),
]
for i,(p,u) in enumerate(BAD):
    def test(self,platform=p,url=u):
        self.assertIsNone(gate.publication_id(platform,url))
        r=held(self,proposed(url,platform))
        self.assertFalse(r['structural_integrity_ok'],(platform,url,r))
        self.assertIn('R424_PUBLISHER_POST_ID_INVALID_OR_UNEXTRACTABLE',r['errors'])
    setattr(PublisherBad,'test_rejected_%02d'%i,test)

class CohortContradictions(unittest.TestCase):pass
FIELDS=gate.MEASURES
for i,field in enumerate(FIELDS):
    def test(self,f=field):
        a,b=cohort(7,10,1,1000,0,100),cohort(30,100,10,10000,0,1000)
        a[f]=b[f]+1
        # If a 7d measure exceeds the 30d measure, the claimed common-end
        # cohort contract is contradicted independent of asserted hashes.
        x=paid();x['cohorts']=[a,b]
        r=held(self,x)
        self.assertIn('R424_NESTED_7D_EXCEEDS_30D_'+f.upper(),r['errors'])
    setattr(CohortContradictions,'test_7d_exceeds_%02d'%i,test)

class Cli(unittest.TestCase):
    def execute(self,path):
        return subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r424_post_cohort_custody_gate.py'),str(path)],
                              capture_output=True,text=True,timeout=10)
    def test_baseline_exit_2_hard_hold(self):
        p=self.execute(ROOT/'reviews'/'r421_offer_funnel_hard_hold.json')
        self.assertEqual(p.returncode,2,p.stderr)
        self.assertTrue(json.loads(p.stdout)['structural_integrity_ok'])
        self.assertIsNone(json.loads(p.stdout)['proposed_post_binding'])
    def test_valid_synthetic_draft_exit_2(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'d.json';path.write_text(json.dumps(proposed()))
            p=self.execute(path);self.assertEqual(p.returncode,2,p.stderr)
            self.assertTrue(json.loads(p.stdout)['structural_integrity_ok'])
    def test_duplicate_key_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'d.json';p.write_text('{"schema":1,"schema":2}')
            r=self.execute(p);self.assertEqual(r.returncode,2)
            self.assertIn('R424_READ_FAILED_ValueError',json.loads(r.stdout)['errors'])
    def test_nan_infinite_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            for literal in ('NaN','Infinity','-Infinity'):
                p=Path(t)/'d.json';p.write_text('{"cohorts":['+literal+']}')
                r=self.execute(p);self.assertEqual(r.returncode,2)
                self.assertIn('R424_READ_FAILED_ValueError',json.loads(r.stdout)['errors'])
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'d.json';path.symlink_to(ROOT/'reviews'/'r421_offer_funnel_hard_hold.json')
            r=self.execute(path);self.assertEqual(r.returncode,2)
            self.assertIn('R424_READ_FAILED_ValueError',json.loads(r.stdout)['errors'])
    def test_hardlink_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'d.json';os.link(ROOT/'reviews'/'r421_offer_funnel_hard_hold.json',path)
            r=self.execute(path);self.assertEqual(r.returncode,2)
            self.assertIn('R424_READ_FAILED_ValueError',json.loads(r.stdout)['errors'])
    def test_oversized_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'d.json';path.write_text('x'*100001)
            r=self.execute(path);self.assertEqual(r.returncode,2)
            self.assertIn('R424_READ_FAILED_ValueError',json.loads(r.stdout)['errors'])
    def test_directory_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            r=self.execute(Path(t));self.assertEqual(r.returncode,2)
            self.assertIn('R424_READ_FAILED_ValueError',json.loads(r.stdout)['errors'])
    def test_missing_path_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            r=self.execute(Path(t)/'missing.json');self.assertEqual(r.returncode,2)
            self.assertIn('R424_READ_FAILED_FileNotFoundError',json.loads(r.stdout)['errors'])
    def test_null_and_extra_data_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            for data in ('null','{}{}','{', ''):
                path=Path(t)/'d.json';path.write_text(data)
                r=self.execute(path);self.assertEqual(r.returncode,2)
                self.assertFalse(json.loads(r.stdout)['structural_integrity_ok'])

if __name__=='__main__':unittest.main()
