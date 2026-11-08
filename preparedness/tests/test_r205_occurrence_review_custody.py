"""R205 synthetic closed-world original-citation custody and intake regressions."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools/r205_occurrence_review_custody.py'
spec=importlib.util.spec_from_file_location('r205',PATH)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture():
    heads={'start':'1'*40}
    sources={'global':{'sources':[{'id':'cdc-find-clean-water','url':'https://www.cdc.gov/water-emergency/','publisher':'CDC','human_link_check':False}]},
             'start':{'sources':[{'id':'start-ready-plan','url':'https://www.ready.gov/plan','publisher':'FEMA','human_link_check':False},
                                  {'id':'good-source','url':'https://example.org/','publisher':'Synthetic','human_link_check':False}]}}
    rows=[];bodies={};metas={};workorders=[]
    for n in range(1,36):
        slug='homemade-water-filters' if n==7 else 'preparedness-real-households' if n==20 else f'synthetic-article-{n}'
        body='<p>Baseline {{cite:good-source}}</p>'
        if n==7: body+='<p>Alternative source {{cite:cdc-find-clean-water}}</p><p>Fuel risk {{cite:cdc-find-clean-water}}</p>'
        if n==20: body+='<p>Use familiar language {{cite:start-ready-plan}}</p>'
        raw=body.encode('utf8')
        row={'n':n,'slug':slug,'source_cluster':'start','branch_sha':heads['start'],
             'body_oid':gate.oid(raw),'body_bytes':len(raw)}
        rows.append(row);bodies[slug]=raw
        metas[slug]={'slug':slug,'source_use':{'good-source':'synthetic evidence only'}}
        for ident in ('cdc-find-clean-water','start-ready-plan'):
            for match in gate.CITE.finditer(raw):
                if match.group(1).decode()!=ident: continue
                origin='global' if ident=='cdc-find-clean-water' else 'start'
                record=sources[origin]['sources'][0]
                workorders.append({'article':slug,'article_number':n,'article_git_oid':row['body_oid'],
                    'source_id':ident,'citation_byte_offset':match.start(),
                    'eligible_source_origins':[origin],
                    'source_records':[{'origin':origin,'url':record['url'],
                                       'publisher':record['publisher'],'human_link_check':False}],
                    'required_reviews':['claim_to_source_fit','human_link_check',
                                        'hazard_specific_safety_review','independent_QD'],
                    'decision':'UNREVIEWED_HARD_HOLD'})
    man={'issue':136,'conversion_issue':820,'state':gate.HOLD,
         'publication_authorized':False,'independent_qd_pass':False,
         'branch_heads':heads,'articles':rows}
    struct={'state':gate.HOLD,'publication_authorized':False,'independent_qd_pass':False,'errors':[]}
    r204={'schema':'fv-preparedness-r204-original-citation-adjudication-v1',
          'state':gate.HOLD,'errors':[],'publication_authorized':False,
          'independent_qd_pass':False,'human_source_approved':False,
          'medical_safety_verified':False,'paid_offer_verified':False,
          'verified_orders':None,'net_revenue':None,
          'workorders':workorders,
          'summary':{'original_articles':35,'citation_occurrences':38,
                     'missing_source_use_occurrences':3,'missing_source_use_pairs':2}}
    return man,bodies,metas,sources,struct,r204


class OccurrenceTests(unittest.TestCase):
    def setUp(self):
        self.m,self.b,self.me,self.s,self.pre,self.r=fixture()
    def run_gate(self,notes=(),authentic=False):
        return gate.build_packet(self.m,self.b,self.me,self.s,self.pre,self.r,notes,authentic=authentic)
    def invalid(self,reason):
        result=self.run_gate()
        self.assertEqual(result['state'],gate.INVALID,result)
        self.assertIn(reason,str(result['errors']))
        self.assertEqual(result['receipts'],[])
        self.assertEqual(result['quarantined_notes'],[])
        self.assertFalse(result['publication_authorized'])
    def test_all_occurrences_sealed_without_approval(self):
        result=self.run_gate()
        self.assertEqual(result['state'],gate.HOLD,result)
        self.assertEqual(result['summary']['original_citations'],38)
        self.assertEqual(len(result['receipts']),3)
        self.assertEqual([r['article_number'] for r in result['receipts']],[7,7,20])
        self.assertEqual(len({r['receipt_id'] for r in result['receipts']}),3)
        self.assertTrue(all(r['human_review_state']=='UNVERIFIED_HARD_HOLD' for r in result['receipts']))
        self.assertFalse(result['human_source_approved'])
        self.assertIsNone(result['realized_net_revenue'])
    def test_reproducible_receipts(self):
        self.assertEqual(self.run_gate(),self.run_gate())
    def test_utf8_byte_offset_claim_anchor(self):
        raw=self.b['homemade-water-filters']
        raw=b'<p>caf\xc3\xa9</p>'+raw
        self.b['homemade-water-filters']=raw
        row=self.m['articles'][6]
        row['body_oid']=gate.oid(raw);row['body_bytes']=len(raw)
        for entry in self.r['workorders'][:2]:
            entry['article_git_oid']=row['body_oid'];entry['citation_byte_offset']+=len(b'<p>caf\xc3\xa9</p>')
        result=self.run_gate()
        self.assertEqual(result['state'],gate.HOLD,result)
    def test_note_quarantined_without_publishing(self):
        original=self.run_gate()['receipts'][0]
        note={'receipt_id':original['receipt_id'],'reviewer_alias':'independent reviewer',
              'review_note':'Source claim requires additional context and a safety review.',
              'source_url_checked':'https://www.cdc.gov/water-emergency/',
              'decision':'NEEDS_SECOND_REVIEW'}
        out=self.run_gate([note]);self.assertEqual(out['state'],gate.HOLD,out)
        self.assertEqual(out['summary']['quarantined_notes'],1)
        self.assertEqual(out['quarantined_notes'][0]['status'],'UNVERIFIED_DRAFT_NOTE_NOT_SOURCE_APPROVAL')
        self.assertFalse(out['independent_qd_pass'])
    def test_changed_case_notes_fail(self):
        note={'receipt_id':'a'*64,'reviewer_alias':'reviewer',
              'review_note':'Need to inspect source context before a decision.',
              'source_url_checked':'','decision':'NO_DECISION'}
        out=self.run_gate([note]);self.assertEqual(out['state'],gate.INVALID)
    def test_unmatched_source_url_is_quarantined_as_invalid(self):
        key=self.run_gate()['receipts'][0]['receipt_id']
        note={'receipt_id':key,'reviewer_alias':'reviewer',
              'review_note':'A different site does not establish this source.',
              'source_url_checked':'https://not-official.example.org/',
              'decision':'NO_DECISION'}
        self.assertEqual(self.run_gate([note])['state'],gate.INVALID)
    def test_unsafe_note_fields_rejected(self):
        key=self.run_gate()['receipts'][0]['receipt_id']
        note={'receipt_id':key,'reviewer_alias':'reviewer','review_note':'Safety review has not been completed.',
              'source_url_checked':'','decision':'NO_DECISION','publication_authorized':True}
        self.assertEqual(self.run_gate([note])['state'],gate.INVALID)
    def test_unverified_corpus_enforced_in_authentic_mode(self):
        self.assertEqual(self.run_gate(authentic=True)['state'],gate.INVALID)
    def test_cli_missing_checkout_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'out.json'
            self.assertEqual(gate.main(['--repo',td,'--report',str(f)]),3)
            self.assertIn(gate.INVALID,f.read_text())
    def test_global_source_collision_rejected(self):
        self.s['global']['sources'].append(self.s['global']['sources'][0])
        self.invalid('duplicate source identifiers')
    def test_new_undeclared_gap_rejected(self):
        self.me['synthetic-article-2']['source_use']={}
        self.invalid('new/missing original citation exceptions')
    def test_approval_rejected(self):
        self.r['paid_offer_verified']=True
        self.invalid('R204 review gate invalid')
    def test_bad_source_origin_rejected(self):
        self.r['workorders'][0]['source_records'][0]['url']='https://wrong.example/'
        self.invalid('source record drift')
    def test_missing_workorder_rejected(self):
        self.r['workorders'].pop()
        self.invalid('workorder loss')


def make_body_change(n):
    def test(self):
        slug=self.m['articles'][n-1]['slug']
        self.b[slug]+=b' corrupted'
        self.invalid('original body identity drift')
    return test


def make_branch_change(n):
    def test(self):
        self.m['articles'][n-1]['branch_sha']='f'*40
        self.invalid('owner branch drift')
    return test

for n in range(1,36):
    setattr(OccurrenceTests,f'test_body_oid_mutation_{n:02d}',make_body_change(n))
    setattr(OccurrenceTests,f'test_owner_ref_mutation_{n:02d}',make_branch_change(n))

if __name__=='__main__':
    unittest.main()
