"""Synthetic-only R202 complete directory/source-scope regression suite."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1] / 'tools/r202_directory_and_source_closure.py'
spec=importlib.util.spec_from_file_location('r202',SOURCE)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture(n=35):
    rows=[]; trees={b:{} for b in gate.HEADS}; metadata={}
    sources={b:{'sources':[{'id':'local-evidence','supports':'Original source text'}]} for b in gate.HEADS}
    sources['global']={'sources':[{'id':'global-evidence','supports':'Original source text'}]}
    keys=list(gate.HEADS)
    for k in range(1,n+1):
        slug=f'synthetic-article-{k}'
        cluster=keys[(k-1)%7]
        witnesses=[cluster]+[b for b in keys if b!=cluster] if k<=6 else [cluster]
        body_oid=f'{k:040x}';meta_oid=f'{k+200:040x}'
        row={'n':k,'slug':slug,'source_cluster':cluster,'branch_sha':gate.HEADS[cluster],
             'section':'start-here','track':'modern',
             'route':f'/preparedness/start-here/{slug}/','also_in':witnesses,
             'body_oid':body_oid,'meta_oid':meta_oid,'body_bytes':1000+k,'meta_bytes':200+k}
        rows.append(row)
        metadata[slug]={'n':k,'slug':slug,'section':'start-here','track':'modern',
            'status':{'publish':'draft','editorial':'drafted'},
            'safety_review':{'state':'pending','reviewer':None,'date':None},
            'source_use':{'global-evidence':'Synthetic explanation for evidence.',
                          'local-evidence':'Additional synthetic citation rationale.'}}
        for b in witnesses:
            trees[b][gate.ROOT+slug+'.body.html']=('100644','blob',body_oid,1000+k)
            trees[b][gate.ROOT+slug+'.meta.json']=('100644','blob',meta_oid,200+k)
    manifest={'schema':gate.SCHEMA,'issue':136,'conversion_issue':820,'state':gate.HOLD,
        'branch_heads':dict(gate.HEADS),'publication_authorized':False,
        'independent_qd_pass':False,'human_source_approved':False,
        'medical_safety_verified':False,'merchant_offer_verified':False,
        'verified_paid_orders':None,'realized_net_revenue':None,
        'artifact_count':n,'export_target_count_with_six_tools':n+6,'articles':rows}
    return manifest,trees,metadata,sources

class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.manifest,self.trees,self.metadata,self.sources=fixture()

    def report(self,strict=True):
        return gate.check(self.manifest,self.trees,self.metadata,self.sources,strict=strict)

    def fail(self,needle):
        report=self.report()
        self.assertEqual(report['state'],gate.INVALID,report)
        self.assertFalse(report['source_crosswalk'])
        self.assertIn(needle,' '.join(report['errors']))

    def test_full_closed_world_census_is_hold_not_approval(self):
        report=self.report()
        self.assertEqual(report['state'],gate.HOLD,report['errors'])
        self.assertEqual(report['summary']['articles'],35)
        self.assertEqual(report['summary']['closed_world_paths'],142)
        self.assertEqual(report['summary']['source_use_relationships'],70)
        self.assertFalse(report['independent_qd_pass'])
        self.assertFalse(report['publication_authorized'])
        self.assertFalse(report['summary']['release_ready'])

    def test_empty_directory_is_rejected(self):
        self.trees['start']={};self.fail('article paths')

    def test_orphan_path_rejected(self):
        self.trees['start'][gate.ROOT+'rogue.body.html']=('100644','blob','a'*40,12)
        self.fail('undeclared')

    def test_partial_pair_rejected(self):
        self.trees['start'][gate.ROOT+'orphan.meta.json']=('100644','blob','a'*40,12)
        self.fail('undeclared')

    def test_nested_shadow_path_rejected(self):
        self.trees['start'][gate.ROOT+'subfolder/hidden.body.html']=('100644','blob','a'*40,12)
        self.fail('undeclared')

    def test_hidden_file_rejected(self):
        self.trees['start'][gate.ROOT+'.ignore']=('100644','blob','a'*40,12)
        self.fail('undeclared')

    def test_symlink_rejected(self):
        row=self.manifest['articles'][0];key=row['source_cluster']
        p=gate.ROOT+row['slug']+'.body.html';a=self.trees[key][p]
        self.trees[key][p]=('120000',a[1],a[2],a[3]);self.fail('drift')

    def test_size_drift_rejected(self):
        row=self.manifest['articles'][0];key=row['source_cluster']
        p=gate.ROOT+row['slug']+'.body.html';a=self.trees[key][p]
        self.trees[key][p]=(a[0],a[1],a[2],a[3]+1);self.fail('drift')

    def test_reference_only_from_other_cluster_rejected(self):
        self.sources['food']['sources'].append({'id':'food-alone'})
        self.metadata['synthetic-article-1']['source_use']={'food-alone':'This source is out of scope.'}
        self.fail('absent from article scope')

    def test_shared_source_remains_ambiguous_hold(self):
        self.sources['start']['sources'].append({'id':'global-evidence'})
        report=self.report()
        self.assertEqual(report['state'],gate.HOLD)
        self.assertEqual(len(report['ambiguous_origins']),5)
        self.assertEqual(report['ambiguous_origins'][0]['eligible_origins'],['global','start'])
        self.assertEqual(report['ambiguous_origins'][0]['decision'],'HUMAN_REVIEW_REQUIRED')

    def test_no_provisional_source_equivalence(self):
        self.metadata['synthetic-article-1']['source_use']['hist-food-nchfp-jerky']='Not automatically an alias.'
        self.fail('absent from article scope')

    def test_missing_metadata_rejected(self):
        del self.metadata['synthetic-article-3'];self.fail('metadata census')

    def test_unsafe_metadata_publish_flag(self):
        self.metadata['synthetic-article-5']['status']['publish']='publish';self.fail('published')

    def test_human_reviewer_without_safety_review_rejected(self):
        self.metadata['synthetic-article-5']['safety_review']['reviewer']='Somebody'
        self.fail('safety')

    def test_fake_qd_state_rejected(self):
        self.manifest['independent_qd_pass']=True;self.fail('approval')

    def test_commercial_receipt_assertion_rejected(self):
        self.manifest['verified_paid_orders']=1;self.fail('sales')

    def test_missing_or_extra_source_origin_rejected(self):
        del self.sources['hist-home'];self.fail('source origins')

    def test_duplicate_source_id_rejected(self):
        self.sources['global']['sources'].append({'id':'global-evidence'})
        self.fail('duplicate')

    def test_blank_source_justification_rejected(self):
        self.metadata['synthetic-article-1']['source_use']['global-evidence']='';self.fail('justification')

    def test_no_source_use_rejected(self):
        self.metadata['synthetic-article-1']['source_use']={};self.fail('empty source')

    def test_invalid_non_json_constant_rejected(self):
        with self.assertRaises(gate.Blocked): gate.strict_json(b'{"x":Infinity}')

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(gate.Blocked): gate.strict_json(b'{"x":1,"x":2}')

    def test_missing_repo_cli_exit3(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(gate.main(['--repo',td,'--report',td+'/report.json']),3)
            self.assertIn('INVALID_HARD_HOLD',Path(td,'report.json').read_text())


def per_row_mutation(n,kind):
    def test(self):
        row=self.manifest['articles'][n-1]; key=row['source_cluster']
        if kind=='body':
            p=gate.ROOT+row['slug']+'.body.html'; t=self.trees[key][p]
            self.trees[key][p]=(t[0],t[1],'f'*40,t[3])
            self.fail('Git OID')
        elif kind=='meta':
            self.metadata[row['slug']]['slug']='disguised'
            self.fail('metadata drift')
        else:
            self.metadata[row['slug']]['safety_review']['state']='approved'
            self.fail('safety')
    return test

for n in range(1,36):
    for kind in ('body','meta','safety'):
        setattr(ClosureTests,f'test_mutation_{n:02d}_{kind}',per_row_mutation(n,kind))

if __name__=='__main__':unittest.main()
