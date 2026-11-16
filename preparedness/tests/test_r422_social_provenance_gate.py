"""R422 deterministic adversarial URL custody and commercial HOLD tests (synthetic only)."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import r422_social_provenance_gate as guard

HELD=json.loads((ROOT/'reviews'/'r421_offer_funnel_hard_hold.json').read_text())
ASSET='grok_20261116_AA1222'

def candidate(platform='youtube',post='https://www.youtube.com/watch?v=abcdef123'):
    d=copy.deepcopy(HELD)
    d['campaign'].update(status='PROPOSED_MATCH',asset_id=ASSET,platform=platform,
       post_url=post,asset_rights_checked=True,hook_source_checked=True,
       mobile_destination=f'https://finalvestige.com/preparedness/?utm_source={platform}&utm_medium=organic_social&utm_campaign=family_pilot_2026_11&utm_content={ASSET}',
       utm_campaign='family_pilot_2026_11',utm_content=ASSET)
    return d

def assert_held(tc, receipt):
    r=guard.validate(receipt)
    tc.assertFalse(r['eligible']);tc.assertFalse(r['publication_approved'])
    tc.assertFalse(r['safety_qd_approved']);tc.assertFalse(r['paid_activation_approved'])
    tc.assertIsNone(r['verified_paid_orders']);tc.assertIsNone(r['net_revenue_per_1000_qualified_humans'])
    tc.assertIn('NOT_COMPUTABLE',r['revenue_status'])
    return r

class Baseline(unittest.TestCase):
    def test_held_receipt_valid_structure(self):
        r=assert_held(self,HELD); self.assertTrue(r['structural_integrity_ok'],r['errors']);self.assertIn('R422_NO_VERIFIED_MATCHED_POST',r['holds'])
    def test_unrelated_offer_remains_unverified(self):
        r=assert_held(self,HELD);self.assertEqual(r['verified_paid_orders'],None)
    def test_original_receipt_unchanged(self):
        d=copy.deepcopy(HELD);guard.validate(d);self.assertEqual(d,HELD)
    def test_deterministic_receipt(self):
        d=candidate();self.assertEqual(guard.validate(d),guard.validate(d))
    def test_format_not_publication(self):
        r=assert_held(self,candidate());self.assertIn('R422_POST_URL_IS_NOT_INDEPENDENT_PUBLICATION_OR_RIGHTS_PROOF',r['holds'])
    def test_both_gates_used(self):
        d=candidate();d['approvals']['safety_qd']=True;self.assertFalse(guard.validate(d)['structural_integrity_ok'])
    def test_malformed_campaign_no_exception(self):
        for bad in (None,[],0,True,'string'):
            d=copy.deepcopy(HELD);d['campaign']=bad;self.assertFalse(guard.validate(d)['structural_integrity_ok'])
    def test_malformed_whole_receipt_no_exception(self):
        for bad in (None,[],False,1,'wrong'):
            self.assertFalse(guard.validate(bad)['structural_integrity_ok'])
    def test_malformed_cohort_no_exception(self):
        d=candidate();d['cohorts']=[{'days':7}];self.assertFalse(guard.validate(d)['structural_integrity_ok'])
    def test_cli_held_exit2(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r422_social_provenance_gate.py'),str(ROOT/'reviews'/'r421_offer_funnel_hard_hold.json')],capture_output=True,text=True)
        self.assertEqual(p.returncode,2,p.stderr);r=json.loads(p.stdout);self.assertTrue(r['structural_integrity_ok'])
    def test_cli_missing_exit2(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r422_social_provenance_gate.py'),'/tmp/r422-nonexistent-9876.json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2,p.stderr);self.assertFalse(json.loads(p.stdout)['structural_integrity_ok'])
    def test_cli_symlink_exit2(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'receipt.json';p.symlink_to(ROOT/'reviews'/'r421_offer_funnel_hard_hold.json')
            result=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r422_social_provenance_gate.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(result.returncode,2);self.assertFalse(json.loads(result.stdout)['structural_integrity_ok'])
    def test_cli_duplicate_keys_exit2(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'receipt.json';p.write_text('{"schema":1,"schema":1}')
            result=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r422_social_provenance_gate.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(result.returncode,2);self.assertFalse(json.loads(result.stdout)['structural_integrity_ok'])
    def test_merchant_candidate_still_held(self):
        d=candidate();d['paid_offer'].update(status='REVIEW_CANDIDATE',sku='fvs_tool_2026_11',seller='Final Vestige Studios',merchant_checkout='https://payhip.com/b/random',rights_receipt_sha256='a'*64,fulfillment_receipt_sha256='a'*64,refund_terms_url='https://payhip.com/refund',merchant_confirmation_sha256='a'*64)
        r=assert_held(self,d);self.assertIn('R422_SELF_ATTESTED_SELLER_HASHES_NOT_EXTERNAL_ORDER_PROOF',r['holds'])

class ValidUrls(unittest.TestCase): pass
positives={
 'youtube':[
  'https://www.youtube.com/watch?v=abcdef123','https://youtube.com/shorts/ABCDEFGHI12',
  'https://youtu.be/ABCdefGH12','https://m.youtube.com/watch?v=abcdEF1234&t=30',
  'https://www.youtube.com/live/ABCDabcd1234'],
 'tiktok':['https://www.tiktok.com/@some.creator/video/7345678901234567890',
           'https://m.tiktok.com/@some.creator/video/7345678901234567890'],
 'instagram':['https://www.instagram.com/reel/C5f2CB19xyz/','https://instagram.com/p/CDEFGabcdef',
              'https://www.instagram.com/reel/C5f2CB19xyz'],
 'facebook':['https://www.facebook.com/reel/1234567891234','https://facebook.com/watch/?v=1234567891234',
             'https://www.facebook.com/my.page/videos/1234567891234']
}
for platform,urls in positives.items():
    for i,url in enumerate(urls):
        def run(self,p=platform,u=url):
            d=candidate(p,u);r=assert_held(self,d)
            self.assertTrue(r['structural_integrity_ok'],(p,u,r['errors']))
        setattr(ValidUrls,'test_'+platform+'_'+str(i).zfill(2),run)

class InvalidUrls(unittest.TestCase): pass
negatives={
 'youtube':[
 'https://example.com/watch?v=abcdef123','https://youtube.com.evil.test/watch?v=abcdef123',
 'https://youtube.com/redirect?url=https://finalvestige.com/preparedness/',
 'https://www.youtube.com/watch?v=abc', 'https://youtu.be/ab',
 'https://www.youtube.com/watch?v=validVIDEO11&v=anotherVid123',
 'https://www.youtube.com/@account', 'https://www.youtube.com/playlist?list=PLAYLISTID',
 'https://www.youtube.com/watch?v=abcdef123&redirect=https://wrong.test',
 'https://youtu.be/abcdEF123/other','https://www.youtube.com/shorts/abcdEF123/other',
 'https://www.youtube.com/%73horts/abcdEF123','https://www.youtube.com/shorts/../abcdEF123',
 'https://www.youtube.com//shorts/abcdEF123', 'https://youtube.com/watch',
 'https://evil.test@youtube.com/watch?v=abcdef123',
 'https://www.youtube.com/watch?v=abcdef123#comments',
 'https://www.youtube.com/watch?v=abcdef123&next=https://evil.test',
 'http://www.youtube.com/watch?v=abcdef123',
 'https://www.youtube.com/watch?v=abcdef123&destination=https://bad.test',
 ],
 'tiktok':[
  'https://vm.tiktok.com/ZM1234567/', 'https://tiktok.com.evil.test/@user/video/7345678901234567890',
  'https://www.tiktok.com/@creator', 'https://www.tiktok.com/@creator/video/abc',
  'https://www.tiktok.com/@creator/video/123456789',
  'https://www.tiktok.com/@creator/video/7345678901234567890/extra',
  'https://www.tiktok.com/t/ZT123abc'],
 'instagram':[
  'https://www.instagram.com/stories/user/123456789','https://www.instagram.com/reel/',
  'https://www.instagram.com/reel/a',
  'https://www.instagram.com.evil.test/reel/CDEFGabcd12',
  'https://www.instagram.com/direct/inbox',
  'https://www.instagram.com/reel/CDEFGabcd12/redirect'],
 'facebook':[
  'https://facebook.com/profile.php?id=123456789',
  'https://m.facebook.com/watch/?v=abcdef123',
  'https://facebook.com/reel/',
  'https://www.facebook.com/my.page/videos/abc',
  'https://www.facebook.com.evil.test/reel/1234567890123',
  'https://www.facebook.com/watch/?v=123456789&v=123456789',
  'https://www.facebook.com/redirect?to=https://example.com',
 ],
}
for platform,urls in negatives.items():
    for i,url in enumerate(urls):
        def run(self,p=platform,u=url):
            d=candidate(p,u);r=assert_held(self,d)
            self.assertFalse(r['structural_integrity_ok'],(p,u,r['errors']))
            self.assertIn('R422_SOCIAL_POST_PLATFORM_OR_PERMALINK_INVALID',r['errors'])
        setattr(InvalidUrls,'test_'+platform+'_'+str(i).zfill(2),run)

class CrossPlatform(unittest.TestCase): pass
for platform in positives:
    for other in positives:
        if other == platform: continue
        def run(self,p=platform,o=other):
            r=guard.validate(candidate(p,positives[o][0]));self.assertFalse(r['structural_integrity_ok']);self.assertIn('R422_SOCIAL_POST_PLATFORM_OR_PERMALINK_INVALID',r['errors'])
        setattr(CrossPlatform,'test_'+platform+'_not_'+other,run)

if __name__=='__main__': unittest.main()
