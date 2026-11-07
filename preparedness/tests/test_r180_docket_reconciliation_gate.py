"""R180 standalone synthetic regression suite; NOT a source/food/medical approval."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOL=Path(__file__).resolve().parents[1]/'tools/r180_docket_reconciliation_gate.py'
spec=importlib.util.spec_from_file_location('r180_gate',TOOL)
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)

TARGETS={
 'safe-jerky-dehydration':['food-fsis-jerky','food-fsis-jerky-qa','nchfp-jerky',
       'food-ksu-jerky','fsis-home-cure-qa','cdc-botulism-prevention'],
 'pemmican-and-dried-meats':['hist-food-fsis-jerky','hist-food-nchfp-jerky',
       'hist-food-marcy-prairie-traveler-text','cdc-botulism-prevention'],
 'pioneer-travel-rations':['hist-food-fsis-jerky','hist-food-nchfp-jerky',
       'hist-food-marcy-prairie-traveler-text','cdc-botulism-prevention'],
}
CLAIMS={
 'safe-jerky-dehydration':[
  ['food-fsis-jerky-qa','nchfp-jerky'],['food-fsis-jerky','nchfp-jerky'],
  ['nchfp-jerky','food-ksu-jerky'],['nchfp-jerky'],['nchfp-jerky']],
 'pemmican-and-dried-meats':[
  [],['hist-food-fsis-jerky'],['hist-food-nchfp-jerky','hist-food-fsis-jerky']],
 'pioneer-travel-rations':[
  ['hist-food-fsis-jerky','hist-food-marcy-prairie-traveler-text'],
  ['hist-food-nchfp-jerky','hist-food-fsis-jerky']],
}


def fixture():
    base_slugs=list(TARGETS)+[f'other-article-{i:02}' for i in range(32)]
    roster={'schema':'synthetic','state':gate.HOLD,'expected_articles':35,
       'expected_citations':2000,'expected_source_use':385,
       'publication_authorized':False,'independent_qd_pass':False,
       'legacy_approved_unverified':['making-water-safer','salt-beef-salt-pork-age-of-sail'],
       'not_required_still_editorial_hold':['navigation-before-gps',
           'pioneer-supply-chains-failed','root-cellars-cool-storage',
           'sanitation-before-germ-theory'], 'articles':[]}
    cross={'state':gate.HOLD,'publication_authorized':False,
       'human_source_claim_review_complete':False,'article_count':35,
       'citation_occurrences':2000,'article_source_relationships':385,'crosswalk':[]}
    urls={'hist-food-nchfp-jerky':'https://nchfp.uga.edu/how/dry/recipes/jerky/',
          'nchfp-jerky':'https://nchfp.uga.edu/how/dry/recipes/jerky'}
    for i,slug in enumerate(base_slugs):
        state='approved' if i in (5,20) else 'not-required' if i in (13,16,27,32) else 'pending'
        roster['articles'].append({'slug':slug,'meta_git_blob':f'{i+1:040x}',
            'recorded_state':state,'source_use_count':11})
        ids=list(TARGETS.get(slug,[]))
        while len(ids)<11:ids.append(f'synthetic-{i:02}-{len(ids):02}')
        for sid in ids:
            cross['crosswalk'].append({'article':slug,'source_id':sid,
              'source_url':urls.get(sid,'https://example.org/'+sid),
              'independently_reviewed_claim':False,'modern_safety_approved':False})
    roster['articles'][5]['slug']='making-water-safer'
    roster['articles'][20]['slug']='salt-beef-salt-pork-age-of-sail'
    roster['articles'][13]['slug']='navigation-before-gps'
    roster['articles'][16]['slug']='pioneer-supply-chains-failed'
    roster['articles'][27]['slug']='root-cellars-cool-storage'
    roster['articles'][32]['slug']='sanitation-before-germ-theory'
    for j,a in enumerate([5,20,13,16,27,32]):
        old=base_slugs[a];new=roster['articles'][a]['slug']
        for u in cross['crosswalk']:
            if u['article']==old:u['article']=new
    family={'schema':'fv-preparedness-r170-family-source-docket-v1',
            'state':gate.HOLD,'scope':'family-reunification-card',
            'independent_qd_pass':False,'publication_authorized':False,
            'decisions':[{'id':f'shelter-source-{i:02}',
               'original_url':f'https://example.org/family-{i}',
               'alternative_current_page':None, 'source_scope':'Pending editorial review',
               'review_state':'PENDING','human_link_check':False,
               'qualified_safety_review':False} for i in range(11)]}
    variance={'schema':'fv-preparedness-r171-source-variance-quarantine-v1',
       'state':gate.HOLD, 'source_url_group_material_roster_discrepancies':1,
       'crosswalk_shared_url_groups':32,'shared_id_conflicting_url_groups':0,
       'human_source_equivalence_review_complete':False,
       'material_discrepancy':{'source_id':'hist-food-nchfp-jerky',
          'crosswalk_group_url':'https://nchfp.uga.edu/how/dry/recipes/jerky',
          'current_literal_fragment_url':'https://nchfp.uga.edu/how/dry/recipes/jerky/'}}
    impact={'schema':'fv-preparedness-r172-jerky-source-impact-docket-v1',
       'state':gate.HOLD,'original_hist_food_source_id':'hist-food-nchfp-jerky',
       'hist_food_literal_url':'https://nchfp.uga.edu/how/dry/recipes/jerky/',
       'source_group_human_review':'PENDING',
       'review_decisions':{'url_equivalence':False,'source_claim_scope':False,
          'qualified_food_safety':False,'independent_qd':False,
          'founder_publication_authorized':False},
       'pending_source_decisions_previously_reported':75,'impacted_articles':[]}
    for slug in gate.IMPACT:
        p=next(r for r in roster['articles'] if r['slug']==slug)
        impact['impacted_articles'].append({'slug':slug,'source_id':
          'nchfp-jerky' if slug=='safe-jerky-dehydration' else 'hist-food-nchfp-jerky',
          'metadata_blob':p['meta_git_blob'],'route':'/preparedness/food/'+slug+'/'})
    claims={'schema':'fv-preparedness-r173-claim-scope-human-docket-v1',
       'state':gate.HOLD, 'previous_source_decisions_pending':75,
       'crosswalk_shared_url_groups_pending':32,'claims':[]}
    for slug,groups in CLAIMS.items():
        for i,ids in enumerate(groups):
            claims['claims'].append({'slug':slug,'claim':f'claim-{i+1}',
              'source_ids':ids,'human_source_scope_decision':'PENDING',
              'qualified_food_safety_decision':'PENDING',
              'independent_qd_decision':'PENDING',
              'reviewer':None,'reviewed_at':None,'evidence_link':None})
    return [roster,cross,family,variance,impact,claims]


class R180ReviewTests(unittest.TestCase):
    def setUp(self):self.data=fixture()
    def report(self):return gate.reconcile(*self.data)
    def test_synthetic_packet_always_hard_hold(self):
        a=self.report()
        self.assertEqual(a['state'],gate.HOLD)
        self.assertEqual((a['review_tickets_pending'],len(a['tickets'])),(21,21))
        self.assertEqual((a['family_source_decisions_pending'],a['jerky_claim_decisions_pending']),(11,10))
        self.assertTrue(a['legacy_counts_overlap_not_additive'])
        self.assertFalse(a['publication_authorized'])
        self.assertFalse(a['commercial_product_verified'])
        self.assertFalse(a['independent_qd_pass'])
    def test_deterministic_packet_across_record_order(self):
        p=self.report()['packet_sha256']
        self.data[2]['decisions'].reverse()
        self.data[5]['claims'].reverse()
        self.data[1]['crosswalk'].reverse()
        self.assertEqual(self.report()['packet_sha256'],p)
    def test_changed_legitimate_scope_changes_digest(self):
        p=self.report()['packet_sha256']
        self.data[2]['decisions'][0]['original_url']='https://example.org/replacement'
        self.assertNotEqual(self.report()['packet_sha256'],p)
    def test_untrusted_source_links_rejected(self):
        for bad in ['http://example.org','https://a:b@example.org/path',
                    'https://example.org/a#x','javascript:alert(1)',
                    'https://example.org/white space','https://example.org:1443/a',None]:
            with self.subTest(url=bad):
                x=fixture();x[2]['decisions'][0]['original_url']=bad
                with self.assertRaises(ValueError):gate.reconcile(*x)
    def test_missing_crosswalk_admission(self):
        self.data[1]['state']='VERIFIED'
        with self.assertRaises(ValueError):self.report()
    def test_crosswalk_fabricated_qd_approval(self):
        self.data[1]['crosswalk'][0]['independently_reviewed_claim']=True
        with self.assertRaises(ValueError):self.report()
    def test_crosswalk_385_custody(self):
        self.data[1]['crosswalk'].pop()
        with self.assertRaises(ValueError):self.report()
    def test_bad_roster_35_custody(self):
        self.data[0]['articles'].pop()
        with self.assertRaises(ValueError):self.report()
    def test_family_missing_decision(self):
        self.data[2]['decisions'].pop()
        with self.assertRaises(ValueError):self.report()
    def test_jerky_missing_claim(self):
        self.data[5]['claims'].pop()
        with self.assertRaises(ValueError):self.report()
    def test_duplicate_jerky_claim(self):
        self.data[5]['claims'][1]['claim']=self.data[5]['claims'][0]['claim']
        with self.assertRaises(ValueError):self.report()
    def test_undocumented_jerky_citation(self):
        self.data[5]['claims'][0]['source_ids']=['unsourced-new-identifier']
        with self.assertRaises(ValueError):self.report()
    def test_citation_order_preservation(self):
        self.data[1]['crosswalk'].append(self.data[1]['crosswalk'][0].copy())
        with self.assertRaises(ValueError):self.report()
    def test_discrepant_jerky_url_never_normalized(self):
        self.data[3]['material_discrepancy']['current_literal_fragment_url']=\
           'https://nchfp.uga.edu/how/dry/recipes/jerky'
        with self.assertRaises(ValueError):self.report()
    def test_jerky_source_pairing_immutable(self):
        self.data[4]['impacted_articles'][0]['source_id']='nchfp-jerky'
        with self.assertRaises(ValueError):self.report()
    def test_family_approval_scope_requires_review(self):
        self.data[2]['independent_qd_pass']=True
        with self.assertRaises(ValueError):self.report()
    def test_ambiguous_historical_approval_not_accepted(self):
        self.data[0]['legacy_approved_unverified']=[]
        with self.assertRaises(ValueError):self.report()
    def test_no_mixed_legacy_aggregate_counts(self):
        self.data[5]['previous_source_decisions_pending']=64
        with self.assertRaises(ValueError):self.report()
    def test_duplicate_source_ids_in_claim(self):
        self.data[5]['claims'][0]['source_ids']=['nchfp-jerky']*2
        with self.assertRaises(ValueError):self.report()
    def test_fabricated_secondary_clearance_flags_rejected(self):
        for index,key in ((5,'source_alias_equivalence_approved'),
                          (5,'human_checked_links'),(4,'commercial_offer_verified'),
                          (4,'founder_publication_authorized'),
                          (3,'human_source_equivalence_review_complete'),
                          (2,'independent_qd_pass')):
            with self.subTest(flag=key):
                fixture_data=fixture()
                fixture_data[index][key]=True
                with self.assertRaises(ValueError):gate.reconcile(*fixture_data)
    def test_missing_checkout_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            a=gate.inspect_repo(Path(directory))
            self.assertEqual(a['state'],gate.INVALID)
            self.assertTrue(a['errors'])
            self.assertFalse(a['independent_qd_pass'])
    def test_cli_incomplete_returns_exit2(self):
        with tempfile.TemporaryDirectory() as directory:
            p=subprocess.run([sys.executable,str(TOOL),'--repo',directory,'--summary'],
                      capture_output=True,text=True,timeout=15)
            self.assertEqual(p.returncode,2)
            self.assertEqual(json.loads(p.stdout)['state'],gate.INVALID)


def make_hostile_family(i,field):
    def test(self):
        self.data[2]['decisions'][i][field]=True if field=='human_link_check' else 'APPROVED'
        with self.assertRaises(ValueError):self.report()
    return test


def make_hostile_claim(i,field):
    def test(self):
        self.data[5]['claims'][i][field]='APPROVED'
        with self.assertRaises(ValueError):self.report()
    return test

for i in range(11):
    for field in ('review_state','human_link_check'):
        setattr(R180ReviewTests,f'test_family_{i:02}_{field}_unsafe',make_hostile_family(i,field))
for i in range(10):
    for field in ('human_source_scope_decision','qualified_food_safety_decision',
                  'independent_qd_decision'):
        setattr(R180ReviewTests,f'test_jerky_{i:02}_{field}_unsafe',make_hostile_claim(i,field))

if __name__=='__main__':unittest.main()
