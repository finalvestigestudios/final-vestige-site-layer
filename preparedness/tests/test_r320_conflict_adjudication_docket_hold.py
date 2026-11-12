"""No write to authentic Preparedness inputs: R320 fixture integrity tests."""
import copy
import json
import unittest
from preparedness.tests.test_r319_three_way_custody_hold import fixture
from preparedness.tools import r320_conflict_adjudication_docket_hold as gate


def dossier_fixture():
    # Use R319 fixture's stable exact inventory; relabel only the affected slugs
    # while keeping two authored files per slug and 35 article/6 tool invariants.
    m=fixture()
    article_slugs=['family-communication-plan','home-fire-escape-plan','homemade-water-filters',
                  'making-water-safer','outage-heat-cold-generators','salt-beef-salt-pork-age-of-sail',
                  'shelter-or-evacuate']+[f'extra-article-{i:02}' for i in range(28)]
    tool_slugs=['power-outage-planner','reunification-plan']+[f'extra-tool-{i:02}' for i in range(4)]
    for r in m['records']:
        import re
        match=re.fullmatch(r'preparedness/content/(articles|tools)/(article|tool)-(\d+)\.(body\.html|meta\.json)',r['path'])
        family,_,num,ext=match.groups()
        slug=(article_slugs if family=='articles' else tool_slugs)[int(num)]
        r['path']=f'preparedness/content/{family}/{slug}.{ext}'
        r['continuation']=None;r['followup']=None;r['disposition']='INTEGRATED_ONLY'
    expected={'preparedness/content/'+p for p in gate.REVIEW_MATRIX}
    for r in m['records']:
        if r['path'] in expected:
            r['followup']={'sha':'a'*40,'size':999}
            r['disposition']='HUMAN_REVIEW_REQUIRED'
    # Count 15 conflicts, six bodies, nine metadata; assign 13 others identical.
    equal=iter(r for r in m['records'] if r['disposition']=='INTEGRATED_ONLY')
    for r in list(equal)[:13]:
        r['followup']=r['integrated'].copy();r['continuation']=r['integrated'].copy();r['disposition']='IDENTICAL'
    assert not gate.custody.validate_manifest(m)['errors'],gate.custody.validate_manifest(m)['errors']
    return m,gate.build_docket(m)

class DocketIntegrity(unittest.TestCase):
    def setUp(self):self.m,self.d=dossier_fixture()
    def report(self):return gate.validate_docket(self.m,self.d)
    def test_draft_no_approval(self):
        r=self.report();self.assertEqual(r['errors'],[]);self.assertEqual(r['state'],'DRAFT_HARD_HOLD');self.assertFalse(r['publishing_authorized'])
    def test_deterministic(self):self.assertEqual(self.d,gate.build_docket(copy.deepcopy(self.m)))
    def test_exact_15(self):self.assertEqual(len(self.d['records']),15)
    def test_severity_all_high(self):self.assertTrue(all(row['severity'].startswith('P0_') for row in self.d['records']))
    def test_json_round_trip(self):self.assertEqual(self.report()['errors'],gate.validate_docket(json.loads(json.dumps(self.m)),json.loads(json.dumps(self.d)))['errors'])
    def test_missing(self):self.assertIn('INVALID_DOCKET',gate.validate_docket(self.m,None)['errors'])
    def test_source_invalid(self):self.m['baseline']['sha']='0'*40;self.assertIn('R319_SOURCE_MANIFEST_INVALID',self.report()['errors'])
    def test_schema(self):self.d['schema']='v0';self.assertIn('DOCKET_SCHEMA_DRIFT',self.report()['errors'])
    def test_baseline(self):self.d['baseline']['sha']='c'*40;self.assertIn('BASELINE_REF_DRIFT',self.report()['errors'])
    def test_branches(self):self.d['branches']['followup']['sha']='c'*40;self.assertIn('CONTRIBUTOR_REFS_DRIFT',self.report()['errors'])
    def test_path(self):self.d['r319_manifest_path']='./other';self.assertIn('SOURCE_PATH_DRIFT',self.report()['errors'])
    def test_count(self):self.d['review_required_count']=True;self.assertIn('REVIEW_COUNT_DRIFT',self.report()['errors'])
    def test_false_release(self):self.d['release']['publication_authorized']=True;self.assertIn('FALSE_RELEASE_OR_SOURCE_CHANGE',self.report()['errors'])
    def test_false_revenue(self):self.d['release']['paid_conversion_verified']=True;self.assertIn('FALSE_RELEASE_OR_SOURCE_CHANGE',self.report()['errors'])
    def test_false_qd(self):self.d['release']['independent_qd_pass']=True;self.assertIn('FALSE_RELEASE_OR_SOURCE_CHANGE',self.report()['errors'])
    def test_false_source_write(self):self.d['release']['canonical_sources_modified']=True;self.assertIn('FALSE_RELEASE_OR_SOURCE_CHANGE',self.report()['errors'])
    def test_unauthorized_extra_key(self):self.d['auto_approved']=True;self.assertIn('DOCKET_SHAPE_DRIFT',self.report()['errors'])
    def test_deleted_entry(self):self.d['records'].pop();self.assertIn('REVIEW_ROW_COUNT_DRIFT',self.report()['errors'])
    def test_bad_list(self):self.d['records']=None;self.assertIn('MISSING_DOCKET_RECORDS',self.report()['errors'])
    def test_duplicate_row(self):self.d['records'][1]=copy.deepcopy(self.d['records'][0]);self.assertTrue(any('DUPLICATE_REVIEW_PATH' in e for e in self.report()['errors']))
    def test_path_escape(self):self.d['records'][0]['path']='../../etc';self.assertTrue(any('INVALID_REVIEW_PATH' in e for e in self.report()['errors']))
    def test_false_auto_selection(self):self.d['records'][0]['automatic_selection']=True;self.assertTrue(any('FALSE_REVIEW_ATTESTATION' in e for e in self.report()['errors']))
    def test_false_complete(self):self.d['records'][0]['status']='RESOLVED';self.assertTrue(any('FALSE_REVIEW_RESOLUTION' in e for e in self.report()['errors']))
    def test_bad_shape(self):self.d['records'][0]['approved_by']='founder';self.assertTrue(any('REVIEW_ROW_SHAPE_DRIFT' in e for e in self.report()['errors']))
    def test_downgrade(self):self.d['records'][0]['severity']='P3_LOW';self.assertTrue(any('RISK_DOWNGRADED' in e for e in self.report()['errors']))
    def test_edit_task(self):self.d['records'][0]['review_task']='all good';self.assertTrue(any('REVIEW_TASK_TAMPERED' in e for e in self.report()['errors']))
    def test_manifest_remove_conflict(self):
        r=next(r for r in self.m['records'] if r['disposition']=='HUMAN_REVIEW_REQUIRED')
        r['followup']=None;r['disposition']='INTEGRATED_ONLY'
        self.assertIn('R319_SOURCE_MANIFEST_INVALID',self.report()['errors'])


    def test_corrupt_integrated_ref_never_crashes(self):
        rec=next(r for r in self.m['records'] if r['disposition']=='HUMAN_REVIEW_REQUIRED')
        rec['integrated']=None
        self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
        self.assertIn('R319_SOURCE_MANIFEST_INVALID',self.report()['errors'])
    def test_corrupt_followup_ref_never_crashes(self):
        rec=next(r for r in self.m['records'] if r['disposition']=='HUMAN_REVIEW_REQUIRED')
        rec['followup']=[]
        self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_missing_path_in_source_never_crashes(self):
        self.m['records'][0].pop('path')
        self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_untrusted_metadata_cannot_claim_approval(self):
        self.d['records'][0]['claim_by_claim_verified']='yes'
        self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_untrusted_truthy_automatic_merge_rejected(self):
        self.d['release']['automatic_merge_permitted']=1
        self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_missing_review_action_rejected(self):
        self.d['records'][0]['review_task']=None
        self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_duplicate_source_record_holds(self):
        self.m['records'].append(copy.deepcopy(self.m['records'][0]))
        self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')
    def test_deleted_source_pair_holds(self):
        self.m['records'].pop()
        self.assertEqual(self.report()['state'],'INVALID_HARD_HOLD')

def source_ref_mutation(index, field):
    def test(self):
        self.d['records'][index]['source_refs'][field]={'sha':'e'*40,'size':700}
        self.assertTrue(any('SOURCE_REF_DRIFT' in e for e in self.report()['errors']))
    return test

for i in range(15):
    for key in ('integrated','followup'):
        setattr(DocketIntegrity,f'test_conflict_{i:02}_{key}_blob_mutation',source_ref_mutation(i,key))

def review_flag_mutation(index, field):
    def test(self):
        self.d['records'][index][field]=True
        self.assertTrue(any('FALSE_REVIEW_ATTESTATION' in e for e in self.report()['errors']))
    return test
for i in range(15):
    for field in ('claim_by_claim_verified','independent_reviewer_approved'):
        setattr(DocketIntegrity,f'test_conflict_{i:02}_{field}_false',review_flag_mutation(i,field))

if __name__=='__main__':unittest.main()
