"""R421 synthetic receipt tests, NOT live merchant or social verification."""
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
import r421_funnel_evidence_gate as gate
BASE=json.loads((ROOT/'reviews'/'r421_offer_funnel_hard_hold.json').read_text())
H='a'*64

def base():return copy.deepcopy(BASE)
def matched(d):
    d['campaign'].update(status='PROPOSED_MATCH',asset_id='grok_20261116_AA1222',
      platform='youtube',post_url='https://www.youtube.com/watch?v=abcdef123',
      asset_rights_checked=True,hook_source_checked=True,
      mobile_destination='https://finalvestige.com/preparedness/?utm_source=youtube&utm_medium=organic_social&utm_campaign=family_pilot_2026_11&utm_content=grok_20261116_AA1222',
      utm_campaign='family_pilot_2026_11',utm_content='grok_20261116_AA1222')
    return d

def offer(d):
    d['paid_offer'].update(status='REVIEW_CANDIDATE',sku='fvs_pack_2026_a1',
       seller='Final Vestige Studios',merchant_checkout='https://example.org/pay',
       rights_receipt_sha256=H,fulfillment_receipt_sha256=H,
       refund_terms_url='https://example.org/refunds',merchant_confirmation_sha256=H)
    return d

def cohort(d, days=7):
    d['cohorts'].append({'days':days,'asset_id':d['campaign']['asset_id'],
      'qualified_human_sessions':50,'verified_paid_orders':2,'gross_cents':2000,
      'refund_cents':300,'fees_cents':200,'merchant_receipt_sha256':H})
    return d

class ReceiptTests(unittest.TestCase):
    def test_held_baseline(self):
        r=gate.validate(base());self.assertTrue(r['structural_integrity_ok'],r['errors'])
        self.assertFalse(r['eligible']);self.assertIsNone(r['verified_paid_orders'])
        self.assertIsNone(r['net_revenue_per_1000_qualified_humans'])
    def test_valid_structural_candidate_also_unverified(self):
        r=gate.validate(cohort(offer(matched(base()))))
        self.assertTrue(r['structural_integrity_ok'],r['errors'])
        self.assertFalse(r['paid_activation_approved'])
        self.assertIsNone(r['verified_paid_orders'])
    def test_both_nested_cohorts_structure_not_proof(self):
        d=cohort(cohort(offer(matched(base()))),30)
        self.assertTrue(gate.validate(d)['structural_integrity_ok'])
    def test_identifiers_not_returned(self):
        d=offer(matched(base()));r=gate.validate(d)
        self.assertNotIn(d['campaign']['asset_id'],json.dumps(r))
    def test_read_only_and_deterministic(self):
        d=cohort(offer(matched(base())));pre=copy.deepcopy(d)
        self.assertEqual(gate.validate(d),gate.validate(d));self.assertEqual(d,pre)
    def test_cli_normal_receipt_always_hold_and_exit2(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r421_funnel_evidence_gate.py'),
                          str(ROOT/'reviews'/'r421_offer_funnel_hard_hold.json')],
                         capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertTrue(json.loads(p.stdout)['structural_integrity_ok'])
    def test_cli_missing_receipt_hold(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r421_funnel_evidence_gate.py'),'/no/receipt'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertFalse(json.loads(p.stdout)['structural_integrity_ok'])
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):json.loads('{"a":1,"a":2}',object_pairs_hook=gate.unique_pairs)
    def test_cli_duplicate_json_rejected(self):
        with tempfile.TemporaryDirectory() as x:
            p=Path(x)/'d.json';p.write_text('{"a":1,"a":2}')
            a=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r421_funnel_evidence_gate.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(a.returncode,2);self.assertFalse(json.loads(a.stdout)['structural_integrity_ok'])
    def test_cli_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as x:
            p=Path(x)/'d.json';p.symlink_to(ROOT/'reviews'/'r421_offer_funnel_hard_hold.json')
            a=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r421_funnel_evidence_gate.py'),str(p)],capture_output=True,text=True)
            self.assertEqual(a.returncode,2);self.assertFalse(json.loads(a.stdout)['structural_integrity_ok'])
    def test_missing_whole_receipt_rejected(self):
        self.assertFalse(gate.validate(None)['structural_integrity_ok'])
    def test_unknown_top_level_metadata_rejected(self):
        d=base();d['paid_sale']=True;self.assertFalse(gate.validate(d)['structural_integrity_ok'])
    def test_self_asserted_receipt_never_authenticates_revenue(self):
        d=cohort(offer(matched(base())));self.assertIn('NOT_COMPUTABLE',gate.validate(d)['revenue_status'])
    def test_no_safety_approval_ever(self):
        d=base();d['approvals']['safety_qd']=True
        r=gate.validate(d);self.assertFalse(r['structural_integrity_ok']);self.assertFalse(r['safety_qd_approved'])

class MutationTests(unittest.TestCase): pass

def change(path,value,d):
    a=d
    for k in path[:-1]:a=a[k]
    a[path[-1]]=value
    return d

bad_baseline=[
(('schema',),2),(('scope',),'WRONG'),(('release_state',),'LIVE'),
(('approvals','publish'),True),(('approvals','site_write'),True),
(('approvals','social_post'),True),(('approvals','paid_activation'),True),
(('approvals','safety_qd'),True),(('free_guide','path'),'/focus/'),
(('free_guide','path'),'/preparedness/water-resilience-field-manual/'),
(('free_guide','status'),'DRAFT'),(('free_guide','source_class'),'UNSOURCED'),
(('free_guide','article_15_release'),True),
(('optional_tool','id'),102),(('optional_tool','id'),105),
(('optional_tool','status'),'LIVE'),(('optional_tool','emergency_review'),True),
(('optional_tool','child_privacy_review'),True),
(('optional_tool','accessibility_review'),True),
(('campaign','topic'),'water_funnel'),(('campaign','status'),'MATCHED'),
(('campaign','asset_id'),'fake_grok_1234567'),(('campaign','platform'),'youtube'),
(('campaign','asset_rights_checked'),True),
(('campaign','hook_source_checked'),True),
(('paid_offer','status'),'VERIFIED'),(('paid_offer','sku'),'oldwater-555'),
(('paid_offer','seller'),'Vested Wisdom'),(('paid_offer','merchant_checkout'),'https://example.org'),
]
for i,(path,value) in enumerate(bad_baseline):
    def case(self,p=path,v=value):
        d=change(p,v,base());r=gate.validate(d)
        self.assertFalse(r['structural_integrity_ok'],str(p));self.assertFalse(r['eligible'])
    setattr(MutationTests,'test_baseline_mutation_'+str(i).zfill(2),case)

class CampaignMutations(unittest.TestCase): pass
bad_match=[
(('campaign','asset_id'),'a'),(('campaign','platform'),'unknown'),
(('campaign','post_url'),'http://youtube.com/watch?v=abc'),
(('campaign','post_url'),'https://youtube.com@evil.test/watch'),
(('campaign','asset_rights_checked'),False),
(('campaign','hook_source_checked'),False),
(('campaign','mobile_destination'),'https://evil.example/preparedness/'),
(('campaign','mobile_destination'),'https://finalvestige.com/preparedness/water-resilience-field-manual/'),
(('campaign','mobile_destination'),'http://finalvestige.com/preparedness/'),
(('campaign','mobile_destination'),'https://finalvestige.com/preparedness/?utm_source=youtube&utm_campaign=family_pilot_2026_11'),
(('campaign','mobile_destination'),'https://finalvestige.com/preparedness/?utm_source=youtube&utm_medium=organic_social&utm_campaign=family_pilot_2026_11&utm_content=wrong'),
(('campaign','mobile_destination'),'https://finalvestige.com/preparedness/?utm_source=youtube&utm_source=tiktok&utm_medium=organic_social&utm_campaign=family_pilot_2026_11&utm_content=grok_20261116_AA1222'),
(('campaign','utm_content'),'other_123456789'),
(('campaign','utm_campaign'),'other_2026_11'),
]
for i,(path,value) in enumerate(bad_match):
    def case(self,p=path,v=value):
        r=gate.validate(change(p,v,matched(base())))
        self.assertFalse(r['structural_integrity_ok'],str(p))
    setattr(CampaignMutations,'test_bad_match_'+str(i).zfill(2),case)

class OfferMutations(unittest.TestCase): pass
bad_offer=[(('paid_offer','seller'),'Vested Wisdom'),(('paid_offer','sku'),'x'),
(('paid_offer','merchant_checkout'),'http://example.org/pay'),
(('paid_offer','refund_terms_url'),'javascript:alert(1)'),
(('paid_offer','rights_receipt_sha256'),'bad'),
(('paid_offer','fulfillment_receipt_sha256'),None),
(('paid_offer','merchant_confirmation_sha256'),'0'*60)]
for i,(path,value) in enumerate(bad_offer):
    def case(self,p=path,v=value):
        r=gate.validate(change(p,v,offer(matched(base()))))
        self.assertFalse(r['structural_integrity_ok'],str(p))
    setattr(OfferMutations,'test_bad_offer_'+str(i).zfill(2),case)

class CohortMutations(unittest.TestCase): pass
bad_cohort=[('days',14),('asset_id','unmatched_123'),('qualified_human_sessions',-1),
('verified_paid_orders',51),('gross_cents',-1),('refund_cents',2100),
('fees_cents',2100),('merchant_receipt_sha256',''),('verified_paid_orders',2.0),
('qualified_human_sessions',True)]
for i,(key,value) in enumerate(bad_cohort):
    def case(self,k=key,v=value):
        d=cohort(offer(matched(base())));d['cohorts'][0][k]=v
        r=gate.validate(d);self.assertFalse(r['structural_integrity_ok'],str(k))
    setattr(CohortMutations,'test_bad_cohort_'+str(i).zfill(2),case)

if __name__=='__main__': unittest.main()
