"""R357 synthetic adversarial QA custody tests, never a release approval."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r357_qa_boundary_hold as g

ARTICLE='<h2 id="plan">Plan</h2><p>'+('Read practical information. '*60)+'{{cite:ready-plan}}</p><a href="/preparedness/">Guide</a>'
TAX={'base_path':'/preparedness/','slate':[{'slug':'family-communication-plan','status':'draft'}]}
SRC={'sources':[{'id':'source-one','title':'Official guide','publisher':'Agency','url':'https://example.gov/guide',
                 'kind':'regulator','verified_on':'2026-10-29','human_link_check':False,'supports':'Plan guidance',
                 'published':None,'updated':None,'reviewed':None}]}
P157=g.SPECS[157]['paths'];P169=g.SPECS[169]['paths'];P2205=g.SPECS[2205]['paths']
def snapshots(pr):
    if pr==157:
        before={P157[0]:ARTICLE,P157[1]:ARTICLE.replace('plan','medicine'),
                P157[2]:json.dumps(SRC),P157[3]:json.dumps(TAX),P157[4]:'test_old=True'}
        after=dict(before)
        after[P157[0]]=before[P157[0]].replace('Read practical','Read revised practical')
        after[P157[1]]=before[P157[1]].replace('Read practical','Read revised practical')
        b=copy.deepcopy(SRC);b['sources'][0]['kind']='nonprofit'
        after[P157[2]]=json.dumps(b)
        after[P157[3]]=json.dumps(TAX,indent=2)
        after[P157[4]]='test_new=True'
    elif pr==169:
        before={P169[0]:'original test fixture'}
        after={P169[0]:'with TemporaryDirectory() as td: copytree(ROOT, td)'}
    else:
        before={P2205[0]:'old fixture',P2205[1]:'old audit'}
        after={P2205[0]:'with TemporaryDirectory() as td: copytree(ROOT, td)',P2205[1]:'updated audit'}
    return before,after

def run(pr=157,before=None,after=None,**kw):
    a,b=snapshots(pr)
    return g.review_snapshot(pr,a if before is None else before,b if after is None else after,**kw)

class QATest(unittest.TestCase):
    def test_schema(self):self.assertEqual(run()['schema'],g.SCHEMA)
    def test_source_class_change_review(self):self.assertIn('SOURCE_CLASSIFICATION_REQUIRES_HUMAN_REVIEW:source-one',run()['errors'])
    def test_qa157_hold(self):self.assertEqual(run()['status'],'INVALID_HARD_HOLD')
    def test_qa169_draft_hold(self):self.assertEqual(run(169)['status'],'QA_REVIEW_REQUIRED_HARD_HOLD')
    def test_qa2205_draft_hold(self):self.assertEqual(run(2205)['status'],'QA_REVIEW_REQUIRED_HARD_HOLD')
    def test_all_pin_sha_lengths(self):
        for s in g.SPECS.values():self.assertEqual((len(s['base']),len(s['head'])),(40,40))
    def test_actual_qa_file_count(self):self.assertEqual([len(g.SPECS[n]['paths']) for n in (157,169,2205)],[5,1,2])
    def test_no_safety_claim(self):
        for n in (157,169,2205):
            for k in g.HOLD:self.assertIs(run(n)[k],False)
    def test_absent_checkout(self):
        with tempfile.TemporaryDirectory() as td:self.assertEqual(g.native_review(td,157)['status'],'INVALID_HARD_HOLD')
    def test_fake_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/'.git').mkdir()
            self.assertEqual(g.native_review(td,169)['status'],'INVALID_HARD_HOLD')
    def test_undefined_pr(self):self.assertEqual(g.review_snapshot(444,{}, {})['status'],'INVALID_HARD_HOLD')
    def test_invalid_dict(self):self.assertEqual(g.review_snapshot(157,[], {})['status'],'INVALID_HARD_HOLD')
    def test_missing_file(self):
        a,b=snapshots(157);del b[P157[0]]
        self.assertIn('INCOMPLETE_QA_SNAPSHOT',run(before=a,after=b)['errors'])
    def test_extra_file(self):
        a,b=snapshots(157);b['preparedness/private.html']='changed'
        self.assertIn('QA_CHANGE_SCOPE_DRIFT',run(before=a,after=b)['errors'])
    def test_base_pin_change(self):self.assertIn('QA_BASE_SHA_DRIFT',run(base='a'*40)['errors'])
    def test_head_pin_change(self):self.assertIn('QA_HEAD_SHA_DRIFT',run(head='b'*40)['errors'])
    def test_base_pin_correct(self):self.assertNotIn('QA_BASE_SHA_DRIFT',run(base=g.SPECS[157]['base'])['errors'])
    def test_head_pin_correct(self):self.assertNotIn('QA_HEAD_SHA_DRIFT',run(head=g.SPECS[157]['head'])['errors'])
    def test_no_body_in_docket(self):self.assertNotIn('Read practical',json.dumps(run()['docket']))
    def test_article_word_count(self):self.assertGreater(g.word_count(ARTICLE),100)
    def test_article_source_cites(self):self.assertEqual(g.CITE.findall(ARTICLE),['ready-plan'])
    def test_article_clean_change(self):self.assertEqual(g.compare_article('p',ARTICLE,ARTICLE.replace('Read practical','Read revised practical'))[0],[])
    def test_article_truncation(self):self.assertIn('READING_DEPTH_LOSS:p',g.compare_article('p',ARTICLE,'<h2 id="plan">Short</h2>')[0])
    def test_article_drop_citation(self):self.assertIn('CITATION_OCCURRENCE_LOST:p',g.compare_article('p',ARTICLE,ARTICLE.replace('{{cite:ready-plan}}',''))[0])
    def test_article_move_citation(self):self.assertIn('CITATION_OCCURRENCE_LOST:p',g.compare_article('p',ARTICLE,ARTICLE.replace('ready-plan','unregistered'))[0])
    def test_article_heading_drift(self):self.assertIn('HEADING_ANCHOR_DRIFT:p',g.compare_article('p',ARTICLE,ARTICLE.replace('id="plan"','id="renamed"'))[0])
    def test_article_link_change(self):self.assertIn('LINK_DESTINATION_CHANGE:p',g.compare_article('p',ARTICLE,ARTICLE.replace('/preparedness/','/checkout/'))[0])
    def test_article_script_change(self):self.assertIn('SCRIPT_DEPENDENCY_CHANGE:p',g.compare_article('p',ARTICLE,ARTICLE+'{{inline-js:tracker.js}}')[0])
    def test_article_preserve_citation_repetition(self):
        original=ARTICLE+'{{cite:ready-plan}}'
        self.assertIn('CITATION_OCCURRENCE_LOST:p',g.compare_article('p',original,ARTICLE)[0])
    def test_sources_duplicate_ids(self):
        d=copy.deepcopy(SRC);d['sources'].append(copy.deepcopy(d['sources'][0]))
        with self.assertRaises(ValueError):g.source_rows(json.dumps(d))
    def test_sources_invalid_shape(self):
        with self.assertRaises(ValueError):g.source_rows('{}')
    def test_source_relabel_flag(self):
        a,b=snapshots(157);self.assertEqual(run(before=a,after=b)['status'],'INVALID_HARD_HOLD')
    def test_taxonomy_semantic_preserved(self):self.assertEqual(g.compare_taxonomy(json.dumps(TAX),json.dumps(TAX,indent=2))[0],[])
    def test_taxonomy_semantic_changed(self):
        x=copy.deepcopy(TAX);x['base_path']='/wrong/'
        self.assertIn('TAXONOMY_SEMANTICS_CHANGED',g.compare_taxonomy(json.dumps(TAX),json.dumps(x))[0])
    def test_fixture_missing_temp(self):
        a,b=snapshots(169);b[P169[0]]='copytree(ROOT,td)'
        self.assertIn('SYNTHETIC_FIXTURE_ISOLATION_NOT_EVIDENCED',run(169,a,b)['errors'])
    def test_fixture_missing_copy(self):
        a,b=snapshots(169);b[P169[0]]='with TemporaryDirectory() as td: pass'
        self.assertIn('SYNTHETIC_FIXTURE_ISOLATION_NOT_EVIDENCED',run(169,a,b)['errors'])
    def test_fixture_never_approved(self):self.assertFalse(run(169)['may_merge'])
    def test_r318_never_approved(self):self.assertFalse(run(2205)['may_publish'])
    def test_unknown_path_not_writable(self):
        a,b=snapshots(169)
        p='../WordPress/private.txt';a[p]='x';b[p]='y'
        self.assertIn('UNSAFE_FILE_PATH',run(169,a,b)['errors'])
    def test_no_false_qd(self):self.assertFalse(run()['qualified_qd_pass'])
    def test_no_sales(self):self.assertFalse(run()['verified_paid_orders'])

# Additional realistic adversarial source mutations: official-source evidence may NOT drift.
for field,new in [('url','https://fake.example/'),('title','Other'),('publisher','Unknown'),
                  ('verified_on','2026-11-13'),('human_link_check',True),('supports','false'),
                  ('published','2026'),('updated','2026'),('reviewed','2026')]:
    def make(f,replacement):
        def test(self):
            a,b=snapshots(157);d=copy.deepcopy(SRC);d['sources'][0][f]=replacement
            b[P157[2]]=json.dumps(d)
            self.assertIn('SOURCE_EVIDENCE_MUTATED:source-one',run(157,a,b)['errors'])
        return test
    setattr(QATest,'test_provenance_'+field,make(field,new))

# Additional source-integrity and body mutations, all must remain hard hold.
for name,old,new,expected in [
  ('drop_anchor','id="plan"','id="gone"','HEADING_ANCHOR_DRIFT'),
  ('link_scheme','/preparedness/','javascript:alert(1)','LINK_DESTINATION_CHANGE'),
  ('no_citation','{{cite:ready-plan}}','<span>source</span>','CITATION_OCCURRENCE_LOST'),
  ('script_add','</p>','{{inline-js:track.js}}</p>','SCRIPT_DEPENDENCY_CHANGE'),
  ('deep_truncation','Read practical information. ','','READING_DEPTH_LOSS'),
  ('cite_reassign','{{cite:ready-plan}}','{{cite:other-source}}','CITATION_OCCURRENCE_LOST'),
]:
    def make(k1,k2,want):
        def test(self):
            a,b=snapshots(157);b[P157[0]]=a[P157[0]].replace(k1,k2)
            self.assertTrue(any(want in e for e in run(157,a,b)['errors']))
        return test
    setattr(QATest,'test_article_mutation_'+name,make(old,new,expected))

if __name__=='__main__':unittest.main(verbosity=2)
