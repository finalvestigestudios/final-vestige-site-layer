"""Synthetic regression only; no medical/safety or human-source approval."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'tools/r203_full_slate_citation_body_gate.py'
spec=importlib.util.spec_from_file_location('r203',SOURCE)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture():
    rows=[];bodies={};metas={};sources={c:{'sources':[{'id':'local-evidence'}]}
                                        for c in ('start','shelter','food','health','hist-field','hist-food','hist-home')}
    sources['global']={'sources':[{'id':'global-evidence'}]}
    heads={c:str(i+1)*40 for i,c in enumerate(sources) if c!='global'}
    order=list(heads)
    for n in range(1,36):
        cluster=order[(n-1)%7];slug=f'synthetic-article-{n}'
        body=(f'<h2>Evidence</h2><p>One {{'+'{cite:local-evidence}}'+
              ' and another {{cite:global-evidence}} alongside '+
              f'{{{{link:{slug}|Read more}}}}</p>').encode('utf-8')
        row={'n':n,'slug':slug,'track':'modern','section':'start-here',
             'route':f'/preparedness/start-here/{slug}/',
             'source_cluster':cluster,'branch_sha':heads[cluster],
             'body_oid':gate.blob_oid(body),'body_bytes':len(body)}
        rows.append(row);bodies[slug]=body
        metas[slug]={'slug':slug,'source_use':{'local-evidence':'Synthetic provenance',
             'global-evidence':'Synthetic provenance'}}
    man={'issue':136,'conversion_issue':820,'state':gate.HOLD,
         'publication_authorized':False,'independent_qd_pass':False,
         'branch_heads':heads,'articles':rows}
    structural={'state':gate.HOLD,'errors':[],
         'independent_qd_pass':False,'publication_authorized':False}
    return man,bodies,metas,sources,structural

class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.man,self.bodies,self.meta,self.sources,self.structural=fixture()
    def run_gate(self):
        return gate.check(self.man,self.bodies,self.meta,self.sources,self.structural)
    def assert_blocked(self,text):
        x=self.run_gate()
        self.assertEqual(x['state'],gate.INVALID,x)
        self.assertIn(text,' '.join(x['errors']))
        self.assertEqual(x['citation_ledger'],[])
        self.assertEqual(x['internal_link_ledger'],[])
    def rebaseline(self,n,new):
        row=self.man['articles'][n-1];self.bodies[row['slug']]=new
        row['body_oid']=gate.blob_oid(new);row['body_bytes']=len(new)
    def test_valid_complete_synthetic_slate_is_still_hard_hold(self):
        x=self.run_gate()
        self.assertEqual(x['state'],gate.HOLD,x)
        self.assertEqual(x['summary']['articles'],35)
        self.assertEqual(x['summary']['citation_occurrences'],70)
        self.assertEqual(x['summary']['internal_link_occurrences'],35)
        self.assertFalse(x['summary']['independent_claim_support_verified'])
        self.assertFalse(x['summary']['release_ready'])
        self.assertFalse(x['publication_authorized'])
    def test_source_origin_ambiguity_kept_not_merged(self):
        self.sources['global']['sources'].append({'id':'local-evidence'})
        x=self.run_gate();self.assertEqual(x['state'],gate.HOLD)
        self.assertEqual(len(x['ambiguous_source_origins']),35)
        self.assertTrue(all(v['decision']=='HUMAN_REVIEW_REQUIRED'
                            for v in x['ambiguous_source_origins']))
    def test_frozen_body_object_substitution_detected(self):
        self.bodies['synthetic-article-1']+=b'a'
        self.assert_blocked('body Git blob drift')
    def test_unknown_source_citation_even_with_matching_body_oid(self):
        self.rebaseline(1,b'<p>{{cite:undeclared-source}}</p>')
        self.assert_blocked('absent from source_use')
    def test_source_only_in_other_cluster_not_allowed(self):
        self.sources['food']['sources'].append({'id':'foreign'})
        self.meta['synthetic-article-1']['source_use']['foreign']='Unreviewed'
        self.rebaseline(1,b'<p>{{cite:foreign}}</p>')
        self.assert_blocked('absent from eligible origins')
    def test_typo_internal_link_rejected(self):
        self.rebaseline(1,b'<p>{{cite:local-evidence}}{{link:missing|Other}}</p>')
        self.assert_blocked('internal link target')
    def test_missing_link_label_rejected(self):
        self.rebaseline(1,b'<p>{{cite:local-evidence}}{{link:synthetic-article-2|}}</p>')
        self.assert_blocked('unexpected/malformed template')
    def test_unfinished_citation_rejected(self):
        self.rebaseline(1,b'<p>{{cite:local-evidence}</p>')
        self.assert_blocked('no template tokens')
    def test_nested_tokens_rejected(self):
        self.rebaseline(1,b'<p>{{cite:{{cite:local-evidence}}}}</p>')
        self.assert_blocked('unparsed or nested')
    def test_unapproved_template_opcode_rejected(self):
        self.rebaseline(1,b'<p>{{product:paid}}</p>')
        self.assert_blocked('unexpected/malformed')
    def test_utf8_invalid_rejected(self):
        self.rebaseline(1,b'<p>{{cite:local-evidence}}</p>\xff')
        self.assert_blocked('UTF-8')
    def test_orphan_body_rejected(self):
        self.bodies['orphan']=b'orphan';self.assert_blocked('closed-world')
    def test_missing_body_rejected(self):
        del self.bodies['synthetic-article-1'];self.assert_blocked('closed-world')
    def test_manifest_publication_assertion_rejected(self):
        self.man['publication_authorized']=True;self.assert_blocked('governance')
    def test_r202_gate_must_run_first(self):
        self.structural['state']=gate.INVALID;self.assert_blocked('R202 structural')
    def test_r202_fake_qd_rejected(self):
        self.structural['independent_qd_pass']=True;self.assert_blocked('R202 structural')
    def test_no_inferred_paid_sales(self):
        x=self.run_gate();self.assertIsNone(x['verified_paid_orders'])
        self.assertIsNone(x['realized_net_revenue'])
    def test_no_citation_rejected(self):
        self.rebaseline(1,b'<p>{{link:synthetic-article-2|Other}}</p>')
        self.assert_blocked('no evidence citations')
    def test_duplicate_source_id_within_registry_rejected(self):
        self.sources['start']['sources'].append({'id':'local-evidence'})
        self.assert_blocked('duplicate/malformed source')
    def test_link_label_spaces_rejected(self):
        self.rebaseline(1,b'<p>{{cite:local-evidence}}{{link:synthetic-article-2| Padded }}</p>')
        self.assert_blocked('empty or padded link label')
    def test_missing_repo_exit3(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(gate.main(['--repo',td,'--report',td+'/x.json']),3)
            self.assertIn('INVALID_HARD_HOLD',Path(td,'x.json').read_text())


def mutation(n,kind):
    def test(self):
        slug=f'synthetic-article-{n}'
        if kind=='citation':
            self.rebaseline(n,b'<p>{{cite:undeclared-source}}</p>')
            self.assert_blocked('absent from source_use')
        elif kind=='link':
            self.rebaseline(n,b'<p>{{cite:local-evidence}} {{link:not-a-real-article|Broken}}</p>')
            self.assert_blocked('internal link target')
        elif kind=='oid':
            self.bodies[slug]+=b' corrupted'
            self.assert_blocked('body Git blob drift')
    return test

for n in range(1,36):
    for kind in ('citation','link','oid'):
        setattr(IntegrityTests,f'test_mutation_{n:02d}_{kind}',mutation(n,kind))

if __name__=='__main__':unittest.main()
