"""R150 offline adversarial source-custody tests (all synthetic, no live claims)."""
import copy
import importlib.util
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('r150',Path(__file__).with_name('r150_origin_migration_gate.py'))
g=importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

TOOLS={'family-reunification-card':'shelter','home-fire-escape-worksheet':'shelter',
       'kit-builder':'start','power-outage-planner':'shelter',
       'reunification-plan':'start','water-planner':'base'}

def fixture():
    regs={k:{'sources':[]} for k in g.ORIGIN_FILES}
    d={'schema':g.R149_SCHEMA,'status':'CANDIDATE_ONLY_HUMAN_SOURCE_REVIEW_REQUIRED',
       'publication_allowed':False,'source_scope_human_review':'PENDING',
       'independent_qd':'NOT_APPROVED','candidate_tool_origins':TOOLS.copy(),
       'tool_summaries':[],'source_use_rows':[]}
    for idx,(tool,origin) in enumerate(TOOLS.items()):
        unresolved=[]
        for i in range(10):
            sid=f'src-{idx}-{i}'
            rec={'id':sid,'url':f'https://example.org/{idx}/{i}',
                 'publisher':'Example','supports':f'Author-reviewed fragment {i}',
                 'notes':'fragment'}
            prior=None
            if i<3 or origin=='base':
                prior={**rec,'notes':'base'} if origin!='base' and i==0 else dict(rec)
                regs['base']['sources'].append(prior)
            if origin!='base':
                regs[origin]['sources'].append(rec)
            selected=rec
            if prior is None:unresolved.append(sid)
            d['source_use_rows'].append({'tool':tool,'source_id':sid,'citation_occurrences':2,
                 'current_origin':'base','candidate_origin':origin,
                 'effective_source_origin':origin if origin!='base' else 'base',
                 'currently_resolvable':prior is not None,'literal_url':selected['url'],
                 'source_supports':selected['supports'],'publisher':selected['publisher'],
                 'author_specific_use':'Source supports this sentence',
                 'human_link_check_recorded':False,'reviewer':None,
                 'review_decision':'PENDING','human_source_scope_adjudicated':False,
                 'medical_safety_approved':False})
        d['tool_summaries'].append({'tool':tool,'current_origin':'base','candidate_origin':origin,
             'unique_cited_sources':10,'citation_occurrences':20,
             'currently_unresolved_source_ids':unresolved})
    d['source_use_row_count']=len(d['source_use_rows'])
    return d,regs

class PositiveControls(unittest.TestCase):
    def test_60_rows(self):
        d,r=fixture();res=g.analyze(d,r,strict_baseline=False)
        self.assertEqual(len(res['rows']),60)
        self.assertEqual(res['totals']['citations'],120)
        self.assertFalse(res['publish_allowed'])
    def test_three_impact_types(self):
        d,r=fixture();types={v['impact'] for v in g.analyze(d,r,strict_baseline=False)['rows']}
        self.assertEqual(types,{'missing','scope_change','unchanged'})
    def test_deterministic(self):
        d,r=fixture(); self.assertEqual(g.analyze(d,r,strict_baseline=False),g.analyze(d,r,strict_baseline=False))
    def test_fingerprint(self):
        self.assertEqual(g.fingerprint({'a':1,'b':2}),g.fingerprint({'b':2,'a':1}))
    def test_custody_gitblob(self):
        self.assertEqual(g.git_blob(b''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
    def test_strict_needs_authentic(self):
        d,r=fixture();self.assertRaises(g.Hold,g.analyze,d,r)

class MutationCases(unittest.TestCase):
    def test_each_author_source_support_detects_tampering(self):
        for i in range(60):
            with self.subTest(i=i):
                d,r=fixture();d['source_use_rows'][i]['source_supports']='changed without source approval'
                self.assertRaises(g.Hold,g.analyze,d,r,strict_baseline=False)
    def test_each_author_identity_detects_tampering(self):
        for i in range(60):
            with self.subTest(i=i):
                d,r=fixture();d['source_use_rows'][i]['literal_url']='https://fake.example/change'
                self.assertRaises(g.Hold,g.analyze,d,r,strict_baseline=False)
    def test_each_author_reviewers_cannot_approve(self):
        for i in range(60):
            with self.subTest(i=i):
                d,r=fixture();d['source_use_rows'][i]['reviewer']='self-appointed'
                self.assertRaises(g.Hold,g.analyze,d,r,strict_baseline=False)
    def test_each_source_count_cannot_disappear(self):
        for i in range(60):
            with self.subTest(i=i):
                d,r=fixture();d['source_use_rows'][i]['citation_occurrences']=0
                self.assertRaises(g.Hold,g.analyze,d,r,strict_baseline=False)

class AttackCases(unittest.TestCase):
    def check_fail(self,mutator):
        d,r=fixture();mutator(d,r)
        self.assertRaises(g.Hold,g.analyze,d,r,strict_baseline=False)
    def test_missing_docket_row(self):self.check_fail(lambda d,r:d['source_use_rows'].pop())
    def test_missing_docket_metadata(self):self.check_fail(lambda d,r:d.pop('schema'))
    def test_approval_state(self):self.check_fail(lambda d,r:d.update(publication_allowed=True))
    def test_status_forgery(self):self.check_fail(lambda d,r:d.update(status='VERIFIED'))
    def test_reviewer_status_forgery(self):self.check_fail(lambda d,r:d.update(source_scope_human_review='APPROVED'))
    def test_qd_forgery(self):self.check_fail(lambda d,r:d.update(independent_qd='PASS'))
    def test_unknown_origin(self):self.check_fail(lambda d,r:d['candidate_tool_origins'].update({'kit-builder':'imaginary'}))
    def test_unknown_tool(self):self.check_fail(lambda d,r:d['candidate_tool_origins'].pop('kit-builder'))
    def test_summary_count_forgery(self):self.check_fail(lambda d,r:d['tool_summaries'][0].update(unique_cited_sources=11))
    def test_author_usage_missing(self):self.check_fail(lambda d,r:d['source_use_rows'][0].update(author_specific_use=''))
    def test_duplicate_author_row(self):self.check_fail(lambda d,r:d['source_use_rows'][1].update(source_id=d['source_use_rows'][0]['source_id']))
    def test_source_missing(self):self.check_fail(lambda d,r:r['shelter']['sources'].pop())
    def test_invalid_source_url(self):self.check_fail(lambda d,r:r['start']['sources'][0].update(url='http://example.org/no'))
    def test_duplicate_register_id(self):self.check_fail(lambda d,r:r['start']['sources'].append(copy.deepcopy(r['start']['sources'][0])))
    def test_source_record_tampering(self):self.check_fail(lambda d,r:r['start']['sources'][0].update(supports='spoofed'))
    def test_resolvable_forgery(self):self.check_fail(lambda d,r:d['source_use_rows'][3].update(currently_resolvable=True))
    def test_old_url_drift(self):self.check_fail(lambda d,r:r['shelter']['sources'][0].update(url='https://wrong.example'))
    def test_same_id_url_scope_change(self):self.check_fail(lambda d,r:r['base']['sources'][0].update(url='https://bad.example'))
    def test_publisher_tampering(self):self.check_fail(lambda d,r:d['source_use_rows'][0].update(publisher='other'))
    def test_missing_all_tools(self):self.check_fail(lambda d,r:d.update(tool_summaries=[]))
    def test_review_decision_forgery(self):self.check_fail(lambda d,r:d['source_use_rows'][0].update(review_decision='PASS'))
    def test_medical_approval_forgery(self):self.check_fail(lambda d,r:d['source_use_rows'][0].update(medical_safety_approved=True))
    def test_unsupported_origin(self):self.check_fail(lambda d,r:r.update(extra={'sources':[]}))
    def test_citation_boolean_forgery(self):self.check_fail(lambda d,r:d['source_use_rows'][0].update(citation_occurrences=True))
    def test_citation_inventory_forgery(self):self.check_fail(lambda d,r:d['tool_summaries'][0].update(citation_occurrences=19))
    def test_human_link_status_forgery(self):self.check_fail(lambda d,r:d['source_use_rows'][0].update(human_link_check_recorded=True))
    def test_source_scope_forgery(self):self.check_fail(lambda d,r:d['source_use_rows'][0].update(human_source_scope_adjudicated=True))
    def test_origin_annotation_drift(self):self.check_fail(lambda d,r:d['source_use_rows'][0].update(effective_source_origin='base'))

# Each subTest executes an independent synthetic mutation. There are 240 per-row
# adversarial subcases and 28 named negative tests across 38 unittest methods.
if __name__=='__main__':unittest.main()
