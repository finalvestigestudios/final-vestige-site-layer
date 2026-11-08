"""Isolated synthetic mutation tests for the R209 review-dependency HOLD gate.

All fixtures remain in memory or temporary files, never in Preparedness originals.
The tests do not certify authored content, clinical safety or publication readiness.
"""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

TOOL=Path(__file__).resolve().parents[1]/'tools'/'r209_review_dependency_gate.py'
spec=importlib.util.spec_from_file_location('r209_review_dependency_gate',TOOL)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fixture():
    names=['household-emergency-plan','three-day-kit','homemade-water-filters',
           'preparedness-real-households'] + [f'synthetic-{n:02d}' for n in range(5,36)]
    assert len(names)==35
    clusters=list(mod.FROZEN_HEADS)
    rows=[]
    for i,slug in enumerate(names,1):
        cluster=clusters[(i-1)%7]
        oid=f'{i:040x}'
        if slug=='household-emergency-plan':oid='8ca5c261dba56eeaf79c445332381a74867233de'
        if slug=='three-day-kit':oid='ef5463ca668166766ca3d868908bc0bcb6040a23'
        rows.append({'n':i,'slug':slug,'section':'start-here' if i<=4 else 'food',
            'route':f'/preparedness/{"start-here" if i<=4 else "food"}/{slug}/',
            'source_cluster':cluster,'branch_sha':mod.FROZEN_HEADS[cluster],
            'body_oid':oid,'meta_oid':f'{i+100:040x}','body_bytes':2000+i,
            'meta_bytes':800+i})
    manifest=dict(schema='fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1',
        issue=136,conversion_issue=820,state=mod.HOLD,branch_heads=copy.deepcopy(mod.FROZEN_HEADS),
        artifact_count=35,export_target_count_with_six_tools=41,
        publication_authorized=False,independent_qd_pass=False,
        human_source_approved=False,medical_safety_verified=False,merchant_offer_verified=False,
        verified_paid_orders=None,realized_net_revenue=None,articles=rows)
    observations={p:{'state':'open','draft':True,'base_sha':v['base_sha'],
        'head_sha':v['head_sha'],'files':{k:list(sha) for k,sha in v['files'].items()}}
        for p,v in mod.REVIEW_PRS.items()}
    candidates={r['slug']:r['body_oid'] for r in rows}
    return manifest,observations,candidates

class TestR209Custody(unittest.TestCase):
    def setUp(self):
        self.m,self.o,self.c=fixture()
    def assert_invalid(self, m=None,o=None,c=None):
        out=mod.audit(m if m is not None else self.m,o if o is not None else self.o,
                      c if c is not None else self.c)
        self.assertEqual(out['state'],mod.INVALID,out)
        self.assertFalse(out['publication_authorized'])
        self.assertFalse(out['independent_qd_pass'])
        self.assertFalse(out['medically_safe'])
    def test_baseline_all35_frozen_remains_hold(self):
        r=mod.audit(self.m,self.o,self.c)
        self.assertEqual(r['state'],mod.HOLD)
        self.assertEqual(len(r['articles']),35)
        self.assertEqual(r['summary']['export_targets_requiring_native_validation'],41)
        self.assertEqual(r['summary']['unexplained_citation_occurrences'],3)
        self.assertEqual(r['summary']['historical_shared_source_conflicts'],7)
        self.assertEqual({x['pr'] for x in r['qa_requirements']},{157,169,973})
        self.assertTrue(all(x['status']=='FROZEN_ORIGINAL_UNREVIEWED' for x in r['articles']))
    def test_missing_all_candidates_is_hold_not_pass(self):
        r=mod.audit(self.m,self.o)
        self.assertEqual(r['state'],mod.HOLD)
        self.assertTrue(all(x['candidate_oid'] is None for x in r['articles']))
    def test_stale_qa_head_cannot_replace_later_article_revision(self):
        self.c['household-emergency-plan']=mod.REVIEW_PRS['157']['files']['preparedness/content/articles/household-emergency-plan.body.html'][1]
        self.assert_invalid()
    def test_six_stale_qa_file_bases_require_three_way_review(self):
        out=mod.audit(self.m,self.o,self.c)
        self.assertEqual(out['state'],mod.HOLD)
        self.assertEqual(out['summary']['stale_qa_base_file_witnesses'],6)
        self.assertTrue(all(not x['auto_merge_authorized'] for x in out['qa_base_drift']))
        self.assertEqual({x['pr'] for x in out['qa_base_drift']},{157,169})
    def test_foreign_body_must_fail_even_if_40char(self):
        self.c['household-emergency-plan']='f'*40
        self.assert_invalid()
    def test_source_exceptions_are_specific_and_unresolved(self):
        r=mod.audit(self.m,self.o,self.c)
        self.assertEqual([(x['article'],x['source_id'],x['affected_citation_occurrences'])
           for x in r['source_exceptions'] if 'article' in x],list(mod.REVIEW_CASES))
    def test_extra_missing_candidate(self):
        del self.c['three-day-kit']
        self.assert_invalid()
    def test_extra_foreign_candidate(self):
        self.c['unknown']='0'*40
        self.assert_invalid()
    def test_invalid_missing_source_blob(self):
        self.m['articles'][0]['meta_oid']='wrong'
        self.assert_invalid()
    def test_cli_synthetic_hold_exit2(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name,value in [('manifest',self.m),('observations',self.o),('candidates',self.c)]:
                (root/(name+'.json')).write_text(json.dumps(value),'utf-8')
            result_file=root/'result.json'
            rc=mod.main(['--manifest',str(root/'manifest.json'),'--observations',str(root/'observations.json'),
                         '--candidates',str(root/'candidates.json'),'--report',str(result_file)])
            self.assertEqual(rc,2)
            self.assertEqual(json.loads(result_file.read_text())['state'],mod.HOLD)
    def test_cli_missing_file_fail_closed_exit3(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);out=root/'out.json'
            rc=mod.main(['--manifest',str(root/'missing.json'),'--observations',str(root/'also-missing.json'),
                         '--report',str(out)])
            self.assertEqual(rc,3)
            self.assertEqual(json.loads(out.read_text())['state'],mod.INVALID)
    def test_strict_json_reject_duplicate_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'dup.json';p.write_text('{"a":1,"a":2}','utf-8')
            with self.assertRaises(mod.Violation):mod.safe_json(p)
    def test_strict_json_reject_nonfinite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'nan.json';p.write_text('{"x":NaN}','utf-8')
            with self.assertRaises(mod.Violation):mod.safe_json(p)
    def test_all_35_original_object_drift_mutations(self):
        for i in range(35):
            m=copy.deepcopy(self.m)
            m['articles'][i]['body_oid']='z'*40
            with self.subTest(article=i):self.assert_invalid(m=m)
    def test_all_35_silent_candidate_substitution_mutations(self):
        for i in range(35):
            c=copy.deepcopy(self.c)
            c[self.m['articles'][i]['slug']]='f'*40
            with self.subTest(article=i):self.assert_invalid(c=c)
    def test_all_35_route_collision_mutations(self):
        for i in range(1,35):
            m=copy.deepcopy(self.m)
            m['articles'][i]['route']=m['articles'][0]['route']
            with self.subTest(article=i):self.assert_invalid(m=m)
    def test_all_7_branch_shas_rejected_when_changed(self):
        for k in mod.FROZEN_HEADS:
            m=copy.deepcopy(self.m);m['branch_heads'][k]='0'*40
            with self.subTest(branch=k):self.assert_invalid(m=m)
    def test_independent_qa_snapshots_must_remain_draft(self):
        for pr in mod.REVIEW_PRS:
            o=copy.deepcopy(self.o);o[pr]['draft']=False
            with self.subTest(pr=pr):self.assert_invalid(o=o)
    def test_independent_qa_heads_must_remain_pinned(self):
        for pr in mod.REVIEW_PRS:
            o=copy.deepcopy(self.o);o[pr]['head_sha']='0'*40
            with self.subTest(pr=pr):self.assert_invalid(o=o)
    def test_independent_qa_file_paths_or_objects_must_remain_pinned(self):
        for pr,base in mod.REVIEW_PRS.items():
            for path in base['files']:
                o=copy.deepcopy(self.o);o[pr]['files'][path][1]='f'*40
                with self.subTest(pr=pr,path=path):self.assert_invalid(o=o)
    def test_approvals_must_be_false(self):
        for key in ('publication_authorized','independent_qd_pass','human_source_approved',
                    'medical_safety_verified','merchant_offer_verified'):
            m=copy.deepcopy(self.m);m[key]=True
            with self.subTest(key=key):self.assert_invalid(m=m)
    def test_unverified_sales_cannot_be_supplied(self):
        for key in ('verified_paid_orders','realized_net_revenue'):
            m=copy.deepcopy(self.m);m[key]=1
            with self.subTest(key=key):self.assert_invalid(m=m)
    def test_frozen_export_target_count(self):
        self.m['export_target_count_with_six_tools']=40
        self.assert_invalid()
    def test_original_missing_or_duplicate_slug(self):
        self.m['articles'][-1]['slug']=self.m['articles'][0]['slug']
        self.assert_invalid()
    def test_missing_review_pr_record(self):
        del self.o['973']
        self.assert_invalid()
    def test_fake_extra_review_pr_record(self):
        self.o['999']=copy.deepcopy(self.o['157'])
        self.assert_invalid()

# Individually enumerated tests for every article identity, candidate substitution
# and canonical route attack; no shared working tree or mutation of real sources.
def add_mutation_method(index, category):
    def test_case(self):
        if category == 'source':
            self.m['articles'][index]['body_oid']='not-a-git-object'
        elif category == 'candidate':
            self.c[self.m['articles'][index]['slug']]='f'*40
        elif category == 'route':
            self.m['articles'][index]['route']='/preparedness/water/forged-duplicate/'
        self.assert_invalid()
    setattr(TestR209Custody, f'test_mutation_{category}_{index+1:02d}', test_case)

for _category in ('source','candidate','route'):
    for _index in range(35):
        add_mutation_method(_index,_category)

if __name__=='__main__':
    unittest.main()
