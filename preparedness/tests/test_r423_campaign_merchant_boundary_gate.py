"""R423 regression cases; entirely synthetic, no commerce or public release."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import r423_campaign_merchant_boundary_gate as gate

HELD=json.loads((ROOT/'reviews'/'r421_offer_funnel_hard_hold.json').read_text())
ASSET='grok_20261116_ABCDEF'
YT='https://www.youtube.com/watch?v=abcdefghijk'

def campaign(post=YT,platform='youtube',name='family_pilot_2026_11'):
    d=copy.deepcopy(HELD)
    d['campaign'].update(status='PROPOSED_MATCH',asset_id=ASSET,platform=platform,
          post_url=post,asset_rights_checked=True,hook_source_checked=True,
          mobile_destination=f'https://finalvestige.com/preparedness/?utm_source={platform}&utm_medium=organic_social&utm_campaign={name}&utm_content={ASSET}',
          utm_campaign=name,utm_content=ASSET)
    return d

def paid():
    d=campaign()
    d['paid_offer'].update(status='REVIEW_CANDIDATE',sku='fvs_prep_pack_001',seller='Final Vestige Studios',
      merchant_checkout='https://payhip.com/b/Good123',refund_terms_url='https://payhip.com/refunds',
      rights_receipt_sha256='a'*64,fulfillment_receipt_sha256='b'*64,merchant_confirmation_sha256='c'*64)
    return d

def held(tc,d):
    r=gate.validate(d)
    tc.assertEqual(r['release_state'],'DRAFT_HARD_HOLD');tc.assertFalse(r['eligible'])
    tc.assertFalse(r['publication_approved']);tc.assertFalse(r['safety_qd_approved'])
    tc.assertFalse(r['paid_activation_approved']);tc.assertIsNone(r['verified_paid_orders'])
    tc.assertIsNone(r['net_revenue_per_1000_qualified_humans'])
    return r

class Core(unittest.TestCase):
    def test_baseline(self):
        r=held(self,HELD);self.assertTrue(r['structural_integrity_ok'],r['errors'])
    def test_proposed(self):
        r=held(self,campaign());self.assertTrue(r['structural_integrity_ok'],r['errors'])
    def test_paid_shape_still_hold(self):
        r=held(self,paid());self.assertTrue(r['structural_integrity_ok'],r['errors'])
        self.assertIn('R423_PAYHIP_SHAPE_IS_NOT_VERIFIED_SELLER_PRODUCT_OR_SETTLEMENT',r['holds'])
    def test_proposed_parent_accepts_unapproved_domain(self):
        d=paid();d['paid_offer']['merchant_checkout']='https://evil.test/b/Good123'
        self.assertTrue(gate.r422.validate(d)['structural_integrity_ok'])
        self.assertIn('R423_MERCHANT_ENDPOINT_NOT_APPROVED_REVIEW_SHAPE',held(self,d)['errors'])
    def test_parent_accepts_unreviewed_privacy_query(self):
        d=campaign(YT+'&email=person%40example.com')
        self.assertTrue(gate.r422.validate(d)['structural_integrity_ok'])
        self.assertIn('R423_SOCIAL_QUERY_PRIVACY_OR_CONTEXT_DRIFT',held(self,d)['errors'])
    def test_parent_accepts_personal_campaign(self):
        d=campaign(name='family_contacts_customer_123')
        self.assertTrue(gate.r422.validate(d)['structural_integrity_ok'])
        self.assertIn('R423_UNBOUNDED_OR_PERSONALIZED_CAMPAIGN_ID',held(self,d)['errors'])
    def test_determinism_and_immutability(self):
        d=paid();x=copy.deepcopy(d);self.assertEqual(gate.validate(d),gate.validate(d));self.assertEqual(x,d)
    def test_unmatched_never_asserts_purchase(self):
        r=held(self,HELD);self.assertIsNone(r['verified_paid_orders']);self.assertIn('NO_AUTHENTICATED_PURCHASABLE_FV_PREPAREDNESS_SKU',r['holds'])
    def test_malformed_no_release(self):
        for obj in (None,{},[],123,'hello'):
            r=held(self,obj);self.assertFalse(r['structural_integrity_ok'])
    def test_parent_approvals_cannot_override(self):
        d=paid();d['approvals']['publish']=True;r=held(self,d);self.assertFalse(r['structural_integrity_ok'])
    def test_cli_baseline_exit2(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r423_campaign_merchant_boundary_gate.py'),str(ROOT/'reviews'/'r421_offer_funnel_hard_hold.json')],capture_output=True,text=True)
        self.assertEqual(p.returncode,2,p.stderr);self.assertTrue(json.loads(p.stdout)['structural_integrity_ok'])
    def test_cli_duplicate_key_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'d.json';p.write_text('{"schema":1,"schema":2}')
            r=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r423_campaign_merchant_boundary_gate.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,2);self.assertFalse(json.loads(r.stdout)['structural_integrity_ok'])
    def test_cli_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'d.json';p.symlink_to(ROOT/'reviews'/'r421_offer_funnel_hard_hold.json')
            r=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r423_campaign_merchant_boundary_gate.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(r.returncode,2);self.assertFalse(json.loads(r.stdout)['structural_integrity_ok'])

class SocialAllowed(unittest.TestCase): pass
allowed=[
 ('youtube','https://www.youtube.com/watch?v=abcdefghijk'),
 ('youtube','https://youtu.be/abcdefghijk?si=BCDf012'),
 ('youtube','https://www.youtube.com/shorts/abcdefghijk'),
 ('youtube','https://www.youtube.com/watch?v=abcdefghijk&t=10'),
 ('youtube','https://www.youtube.com/watch?v=abcdefghijk&feature=share'),
 ('tiktok','https://www.tiktok.com/@finalvestige/video/7345678901234567890'),
 ('tiktok','https://www.tiktok.com/@finalvestige/video/7345678901234567890?lang=en'),
 ('instagram','https://www.instagram.com/reel/ABCDEFG1234/'),
 ('instagram','https://www.instagram.com/p/ABCDEFG1234?igsh=abc123'),
 ('facebook','https://www.facebook.com/watch/?v=1234567891234'),
 ('facebook','https://www.facebook.com/reel/1234567891234'),
]
for i,(platform,url) in enumerate(allowed):
    def test(self,p=platform,u=url):
        r=held(self,campaign(u,p));self.assertTrue(r['structural_integrity_ok'],(p,u,r['errors']))
    setattr(SocialAllowed,f'test_allowed_{i:02d}',test)

class SocialDenied(unittest.TestCase): pass
bad=[
 'https://www.youtube.com/watch?v=abcdefghijk&email=me@example.com',
 'https://www.youtube.com/watch?v=abcdefghijk&phone=5555551111',
 'https://www.youtube.com/watch?v=abcdefghijk&user_id=1234',
 'https://www.youtube.com/watch?v=abcdefghijk&session=abcd',
 'https://www.youtube.com/watch?v=abcdefghijk&token=abcd',
 'https://www.youtube.com/watch?v=abcdefghijk&auth=abcd',
 'https://www.youtube.com/watch?v=abcdefghijk&cookie=x',
 'https://www.youtube.com/watch?v=abcdefghijk&fbclid=x',
 'https://www.youtube.com/watch?v=abcdefghijk&gclid=x',
 'https://www.youtube.com/watch?v=abcdefghijk&redirect=https://example.com',
 'https://www.youtube.com/watch?v=abcdefghijk&v=ZZZZZZZZZZZ',
 'https://www.youtube.com/watch?v=abcdefghijk&feature=',
 'https://www.youtube.com/watch?v=abcdefghijk&feature=share;email=test',
 'https://www.youtube.com/watch?v=abcdefghijk&feature=secret',
 'https://www.youtube.com/watch?v=abcdefghijk&feature=abc%0Adef',
 'https://www.youtube.com/watch?v=abcdefghijk&v%00=bad',
 'https://www.youtube.com/watch?v=abcdefghijk&feature=%C3%A9',
 'https://www.youtube.com/watch?v=abcdefghijk&feature=abc%20def',
 'https://www.youtube.com/shorts/abcdefghijk?v=abcdefghijk',
 'https://www.youtube.com/shorts/abcdefghijk?feature=share&pp=xyz',
 'https://www.youtube.com/watch?v=abcdefghijk&feature=share&feature=share',
 'https://www.youtube.com/watch?v=abcdefghijk&si=client_id_2233',
 'https://www.youtube.com/watch?v=abcdefghijk&si=visitor_id_987',
 'https://www.youtube.com/watch?v=abcdefghijk&si=referrer_987',
 'https://www.youtube.com/watch?v=abcdefghijk&si=access_key_33',
 'https://www.youtube.com/watch?v=abcdefghijk&si=passWORD333',
 'https://www.youtube.com/watch?v=abcdefghijk&si=abcdefghij'+('x'*150),
]
for i,url in enumerate(bad):
    def test(self,u=url):
        r=held(self,campaign(u));self.assertFalse(r['structural_integrity_ok'],(u,r['errors']))
        self.assertIn('R423_SOCIAL_QUERY_PRIVACY_OR_CONTEXT_DRIFT',r['errors'])
    setattr(SocialDenied,f'test_block_{i:02d}',test)

class CampaignDenied(unittest.TestCase):pass
bad_names=['customer123','family_2026_11','family_pilot_2026_13','family_pilot_2026_00',
 'family_pilot_2025_11','family_pilot_2036_11','family_pilot_2026_1','family_pilot_2026_011',
 'family_pilot_2026_11_extra','FAMILY_PILOT_2026_11','family_pilot_2026_11_user23',
 'family_pilot_2026_11@abc.com','', 'family_pilot_2026_11%0A']
for i,name in enumerate(bad_names):
    def test(self,v=name):
        self.assertIn('R423_UNBOUNDED_OR_PERSONALIZED_CAMPAIGN_ID',held(self,campaign(name=v))['errors'])
    setattr(CampaignDenied,f'test_name_{i:02d}',test)

class MerchantDenied(unittest.TestCase): pass
merchant_bad=[
 ('merchant_checkout','https://evil.example.com/b/Good123'),
 ('merchant_checkout','https://payhip.com.evil.com/b/Good123'),
 ('merchant_checkout','https://payhip.com/b/'),
 ('merchant_checkout','https://payhip.com/b/X'),
 ('merchant_checkout','https://payhip.com/b/Good123?ref=stuff'),
 ('merchant_checkout','https://payhip.com/b/Good123#fragment'),
 ('merchant_checkout','https://payhip.com/b/Good123/extra'),
 ('merchant_checkout','https://payhip.com/checkout/Good123'),
 ('merchant_checkout','https://www.payhip.com/b/Good123'),
 ('refund_terms_url','https://evil.example.com/refunds'),
 ('refund_terms_url','https://www.payhip.com/refunds'),
 ('refund_terms_url','https://payhip.com/refunds?customer=abc'),
 ('refund_terms_url','https://payhip.com/%2e%2e/evil'),
 ('refund_terms_url','https://payhip.com/refunds#fragment'),
 ('refund_terms_url','https://payhip.com/old-water-guide'),
]
for i,(key,value) in enumerate(merchant_bad):
    def test(self,k=key,v=value):
        d=paid();d['paid_offer'][k]=v;r=held(self,d)
        self.assertIn('R423_MERCHANT_ENDPOINT_NOT_APPROVED_REVIEW_SHAPE',r['errors'])
    setattr(MerchantDenied,f'test_merchant_{i:02d}',test)

class DestinationDenied(unittest.TestCase):pass
bad_mobile=[
 '&email=someone%40example.com',
 '&phone=5551231212',
 '&visitor_id=abc',
 '&utm_campaign=family_pilot_2026_11',
 '&utm_content=',
 '&token=abcdef',
 '&utm_source=evil',
 '&utm_campaign=%C3%A9',
 '&utm_campaign=%0A',
 '&utm_campaign=auth_token_123',
]
for i,suf in enumerate(bad_mobile):
    def test(self,s=suf):
        d=campaign();d['campaign']['mobile_destination']+=s
        r=held(self,d);self.assertFalse(r['structural_integrity_ok'])
    setattr(DestinationDenied,f'test_mobile_{i:02d}',test)

if __name__=='__main__':unittest.main()
