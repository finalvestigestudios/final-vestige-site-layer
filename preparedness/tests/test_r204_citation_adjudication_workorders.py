"""Synthetic-only R204 citation workorder security regressions; no QD approvals."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools/r204_citation_adjudication_workorders.py'
spec=importlib.util.spec_from_file_location('r204',PATH)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture():
    heads={'start':'1'*40,'food':'2'*40}
    sources={'global':{'sources':[{'id':'cdc-find-clean-water','url':'https://www.cdc.gov/water-emergency/about/how-to-find-clean-water-in-an-emergency.html','publisher':'CDC','human_link_check':False}]},
             'start':{'sources':[{'id':'start-ready-plan','url':'https://www.ready.gov/plan','publisher':'FEMA','human_link_check':False},{'id':'good-source','human_link_check':False}]},
             'food':{'sources':[{'id':'good-source','human_link_check':False}]}}
    rows=[];bodies={};metas={}
    for n in range(1,36):
        slug='homemade-water-filters' if n==7 else 'preparedness-real-households' if n==20 else f'synthetic-article-{n}'
        body='<p>Neutral research context {{cite:good-source}}</p>'
        if n==7: body+='<p>Use alternate clean sources {{cite:cdc-find-clean-water}}</p><p>Avoid fuel/chemical contamination {{cite:cdc-find-clean-water}}</p>'
        if n==20: body+='<p>Ask about household languages {{cite:start-ready-plan}}</p>'
        raw=body.encode()
        rows.append({'n':n,'slug':slug,'source_cluster':'start','branch_sha':heads['start'],
                     'body_oid':gate.oid(raw),'body_bytes':len(raw)})
        bodies[slug]=raw
        metas[slug]={'slug':slug,'source_use':{'good-source':'synthetic only'}}
    man={'issue':136,'conversion_issue':820,'state':gate.HOLD,'publication_authorized':False,
         'independent_qd_pass':False,'branch_heads':heads,'articles':rows}
    structural={'state':gate.HOLD,'publication_authorized':False,'independent_qd_pass':False,'errors':[]}
    return man,bodies,metas,sources,structural

class WorkorderTests(unittest.TestCase):
    def setUp(self):
        self.m,self.b,self.me,self.s,self.pre=fixture()
    def evaluate(self,**kw):
        return gate.check(self.m,self.b,self.me,self.s,self.pre,**kw)
    def invalid(self,needle):
        report=self.evaluate()
        self.assertEqual(report['state'],gate.INVALID,report)
        self.assertIn(needle,str(report['errors']))
        self.assertEqual(report['workorders'],[])
        self.assertFalse(report['publication_authorized'])
    def replace(self,n,data):
        row=self.m['articles'][n-1]
        self.b[row['slug']]=data
        row['body_oid']=gate.oid(data)
        row['body_bytes']=len(data)
    def test_complete_review_packet_remains_hold(self):
        r=self.evaluate();self.assertEqual(r['state'],gate.HOLD,r)
        self.assertEqual(r['summary']['missing_source_use_occurrences'],3)
        self.assertEqual(r['summary']['missing_source_use_pairs'],2)
        self.assertEqual(r['summary']['original_articles'],35)
        self.assertFalse(r['publication_authorized'])
        self.assertFalse(r['human_source_approved'])
        self.assertIsNone(r['net_revenue'])
        self.assertEqual([x['article_number'] for x in r['workorders']],[7,7,20])
    def test_claim_context_and_source_origin_are_preserved(self):
        r=self.evaluate()
        self.assertTrue(all(x['decision']=='UNREVIEWED_HARD_HOLD' for x in r['workorders']))
        self.assertTrue(all('claim_context' in x and x['claim_context'] for x in r['workorders']))
        self.assertEqual(r['workorders'][0]['eligible_source_origins'],['global'])
        self.assertEqual(r['workorders'][2]['eligible_source_origins'],['start'])
    def test_missing_source_registration_rejected(self):
        self.s['global']['sources']=[];self.invalid('no eligible origin')
    def test_unapproved_source_cannot_auto_upgrade(self):
        self.s['global']['sources'][0]['human_link_check']=True
        self.invalid('historically unreviewed source unexpectedly changed')
    def test_source_id_collision_rejected(self):
        self.s['start']['sources'].append({'id':'good-source'})
        self.invalid('duplicate/invalid source id')
    def test_unexpected_new_missing_source_use_detected(self):
        self.me['synthetic-article-1']['source_use']={}
        self.invalid('unexpected missing-source-use census')
    def test_all_holes_must_remain_explicitly_unadjudicated(self):
        self.me['homemade-water-filters']['source_use']['cdc-find-clean-water']='unreviewed fake explanation'
        self.invalid('unexpected missing-source-use census')
    def test_release_approval_forbidden(self):
        self.m['publication_authorized']=True;self.invalid('manifest/governance')
    def test_qd_approval_forbidden(self):
        self.pre['independent_qd_pass']=True;self.invalid('R202 prerequisite')
    def test_unknown_body_rejected(self):
        self.b['unknown']=b'synthetic';self.invalid('closed-world')
    def test_missing_body_rejected(self):
        del self.b['synthetic-article-1'];self.invalid('closed-world')
    def test_writes_nothing_on_checkout_failure(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'report.json'
            self.assertEqual(gate.main(['--repo',td,'--report',str(path)]),3)
            self.assertIn('INVALID_HARD_HOLD',path.read_text())


def add_mutation(n):
    def test(self):
        self.b[self.m['articles'][n-1]['slug']]+=b'x'
        self.invalid('unfrozen article body')
    return test
for number in range(1,36):
    setattr(WorkorderTests,f'test_frozen_body_{number:02d}',add_mutation(number))


def add_scope_mutation(n):
    def test(self):
        row=self.m['articles'][n-1]
        row['branch_sha']='a'*40
        self.invalid('source cluster/branch drift')
    return test
for number in range(1,36):
    setattr(WorkorderTests,f'test_branch_scope_{number:02d}',add_scope_mutation(number))

if __name__=='__main__':
    unittest.main()
