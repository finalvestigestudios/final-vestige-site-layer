"""Synthetic R198 source-origin adversarial tests; NOT end-to-end or safety approval."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / 'tools/r198_source_scope_gate.py'
spec = importlib.util.spec_from_file_location('r198_source_scope_gate', PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def fixture():
    docs=[]
    for group,slug in gate.ARTICLES:
        for version in gate.TOTALS:
            uses=[{'source_id':'base-auth','source_origins':['base'],
                   'ambiguous':False,'human_review':'PENDING'},
                  {'source_id':'cluster-auth','source_origins':[group],
                   'ambiguous':False,'human_review':'PENDING'}]
            docs.append({'cluster':group,'slug':slug,'version':version,
                'meta_blob':'a'*40,'human_review':'PENDING',
                'source_use_count':2,'origins':uses})
    return {'schema':'fv-preparedness-r197-origin-collision-custody-v1',
            'issue':136,'state':gate.HOLD,'publication_authorized':False,
            'independent_qd_pass':False,'human_source_approved':False,
            'medical_safety_verified':False,'merchant_offer_verified':False,
            'verified_paid_orders':None,'realized_net_revenue':None,
            'versioned_source_rows':{'frozen':115,'observed':119},
            'same_id_conflicts':[{'version':'frozen'}]*6+[{'version':'observed'}]*7,
            'article_origin_workorders':docs}

class ScopeTests(unittest.TestCase):
    def setUp(self): self.data=fixture()
    def check(self): return gate.verify(self.data,strict_census=False)
    def assert_denied(self):
        result=self.check()
        self.assertEqual(result['state'],gate.INVALID,result)
        self.assertTrue(result['errors'])
        self.assertEqual(result['origin_scope_workorders'],[])
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['independent_qd_pass'])
    def test_synthetic_success_is_still_hard_hold(self):
        result=self.check()
        self.assertEqual(result['state'],gate.HOLD)
        self.assertEqual(len(result['origin_scope_workorders']),28)
        self.assertEqual(result['summary']['frozen']['source_uses'],14)
        self.assertIsNone(result['verified_paid_orders'])
        self.assertFalse(result['publication_authorized'])
    def test_repeated_runs_identical(self):
        self.assertEqual(json.dumps(self.check(),sort_keys=True),json.dumps(self.check(),sort_keys=True))
    def test_strict_actual_census_blocks_synthetic_counts(self):
        self.assertEqual(gate.verify(self.data)['state'],gate.INVALID)
    def test_cross_origin_with_valid_base_is_pending_not_approved(self):
        use=self.data['article_origin_workorders'][0]['origins'][0]
        use['source_origins']=['base','hist-food'];use['ambiguous']=True
        result=self.check()
        self.assertEqual(result['state'],gate.HOLD)
        row=result['origin_scope_workorders'][0]
        self.assertEqual(row['eligible_origins'],['base'])
        self.assertEqual(row['foreign_alternatives'],['hist-food'])
        self.assertFalse(row['automatic_origin_selection'])
        self.assertEqual(row['human_review'],'PENDING')
    def test_foreign_only_rejected(self):
        self.data['article_origin_workorders'][0]['origins'][0].update(source_origins=['hist-home'])
        self.assert_denied()
    def test_git_oid_formula(self):
        self.assertEqual(gate.git_oid(b'test content\n'),'d670460b4b4aece5915caf5c68d12f560a9fe3e4')
    def test_missing_r197_pin_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'preparedness/tools/r197_source_origin_collision_gate.py'
            path.parent.mkdir(parents=True)
            path.write_text('SCHEMA="anything"\n')
            with self.assertRaises(gate.ScopeError): gate.load_pinned_r197(d)
    def test_blank_doc_rejected(self):
        self.data['article_origin_workorders'][0]={}
        self.assert_denied()

# Vary every independently pinned article and version: none may claim approval,
# silently accept another cluster's register, or erase source identity.
def bad_variant(index, change):
    def test(self):
        doc=self.data['article_origin_workorders'][index]
        row=doc['origins'][0]
        if change=='foreign_only':
            row['source_origins']=[next(x for x in sorted(gate.ORIGINS) if x not in ('base',doc['cluster']))]
        elif change=='no_origin': row['source_origins']=[]
        elif change=='duplicate_origin': row['source_origins']=['base','base'];row['ambiguous']=True
        elif change=='bad_approval': row['human_review']='PASS'
        elif change=='fake_ambiguous': row['ambiguous']=True
        elif change=='bad_meta': doc['meta_blob']='not-a-git-oid'
        elif change=='bad_article_review': doc['human_review']='APPROVED'
        elif change=='duplicate_source_id': doc['origins'][1]['source_id']=row['source_id']
        elif change=='wrong_article': doc['slug']='different-page'
        elif change=='unsorted_origins': row['source_origins']=['hist-food','base'];row['ambiguous']=True
        else:raise AssertionError(change)
        self.assert_denied()
    return test

for index in range(14):
    for change in ('foreign_only','no_origin','duplicate_origin','bad_approval','fake_ambiguous',
                   'bad_meta','bad_article_review','duplicate_source_id','wrong_article','unsorted_origins'):
        setattr(ScopeTests,f'test_mutant_{index:02d}_{change}',bad_variant(index,change))

def bad_header(which):
    def test(self):
        if which=='bad_schema':self.data['schema']='wrong'
        elif which=='approved':self.data['state']='APPROVED'
        elif which=='no_docs':self.data.pop('article_origin_workorders')
        elif which=='missing_version':self.data['article_origin_workorders'].pop()
        elif which=='duplicate_version':self.data['article_origin_workorders'][0]=copy.deepcopy(self.data['article_origin_workorders'][1])
        elif which=='fake_sales':self.data['verified_paid_orders']=3
        elif which=='fake_revenue':self.data['realized_net_revenue']=30
        elif which=='fake_merchant':self.data['merchant_offer_verified']=True
        elif which=='fake_qd':self.data['independent_qd_pass']=True
        elif which=='fake_medical':self.data['medical_safety_verified']=True
        elif which=='fake_source':self.data['human_source_approved']=True
        elif which=='fake_publish':self.data['publication_authorized']=True
        elif which=='missing_flag':self.data.pop('medical_safety_verified')
        elif which=='not_136':self.data['issue']=820
        else:raise AssertionError(which)
        self.assert_denied()
    return test
for name in ('bad_schema','approved','no_docs','missing_version','duplicate_version',
             'fake_sales','fake_revenue','fake_merchant','fake_qd','fake_medical','fake_source',
             'fake_publish','missing_flag','not_136'):
    setattr(ScopeTests,'test_header_'+name,bad_header(name))

if __name__=='__main__':unittest.main()
