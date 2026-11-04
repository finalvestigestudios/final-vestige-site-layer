"""R115 original author-body evidence gate tests, all synthetic and isolated."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]/'tools/r115_frozen_corpus_evidence_gate.py'
s=importlib.util.spec_from_file_location('r115e',P)
g=importlib.util.module_from_spec(s);s.loader.exec_module(g)

def example():
    slate=[{'n':n,'slug':f'article-{n}','section':'start-here','track':'modern'} for n in range(1,36)]
    body=lambda n: f'<p>Research paragraph {{'+'{cite:source-one}}</p>'
    docs={r['slug']:(body(r['n']).encode(),{'slug':r['slug'],'section':'start-here','track':'modern',
        'status':{'publish':'draft','editorial':'drafted'},'safety_review':{'state':'pending'},
        'source_use':{'source-one':'Original author reading context'}}) for r in slate}
    rows=[{'n':r['n'],'slug':r['slug'],'section':r['section'],'track':r['track'],
        'body_git_blob_oid':g.git_blob(docs[r['slug']][0]),'raw_citation_occurrences':1,
        'distinct_author_scoped_source_ids':1} for r in slate]
    ledger={'schema':g.SCHEMA,'reference_commit':'abc','release_state':'HOLD',
        'may_publish':False,'source_claim_truth_verified':False,
        'qualified_safety_review_verified':False,'independent_QD_PASS':False,
        'article_count':35,'rows_NOT_APPROVED':rows,
        'raw_citation_occurrences_total':35,
        'article_scoped_source_id_total_NOT_GLOBAL_UNIQUE':35,
        'self_reported_safety_metadata_counts':{'pending':35,'approved':0,'not-required':0}}
    return {'base_path':'/preparedness/','slate':slate},ledger,docs

class Evidence(unittest.TestCase):
    def test_normal(self):
        r=g.verify(*example());self.assertEqual(r['frozen_article_count'],35)
        self.assertEqual(r['unique_urls'],35)
        self.assertFalse(r['may_publish'])
    def test_reproducibility(self):
        self.assertEqual(g.verify(*example()),g.verify(*example()))
    def test_not_mutated(self):
        data=example();f=copy.deepcopy(data);g.verify(*data);self.assertEqual(f,data)
    def test_no_claim_accuracy(self):
        self.assertFalse(g.verify(*example())['source_claim_truth_verified'])
    def test_git_object_standard(self):
        self.assertEqual(g.git_blob(b'test'),'30d74d258442c7c65512eafab474568dd706c430')

MUTANTS=[
 ('base',lambda t,l,a:t.update(base_path='/wrong/')),
 ('slatecount',lambda t,l,a:t['slate'].pop()),
 ('slatenum',lambda t,l,a:t['slate'][2].update(n=2)),
 ('ledger_schema',lambda t,l,a:l.update(schema='fake')),
 ('ledger_ref',lambda t,l,a:l.update(reference_commit='')),
 ('ledger_state',lambda t,l,a:l.update(release_state='PASS')),
 ('publish_claim',lambda t,l,a:l.update(may_publish=True)),
 ('facts_claim',lambda t,l,a:l.update(source_claim_truth_verified=True)),
 ('safety_claim',lambda t,l,a:l.update(qualified_safety_review_verified=True)),
 ('qd_claim',lambda t,l,a:l.update(independent_QD_PASS=True)),
 ('ledger_count',lambda t,l,a:l.update(article_count=34)),
 ('ledger_short',lambda t,l,a:l['rows_NOT_APPROVED'].pop()),
 ('ledger_duplicate',lambda t,l,a:l['rows_NOT_APPROVED'][1].update(slug='article-1')),
 ('missing_doc',lambda t,l,a:a.pop('article-3')),
 ('unexpected_doc',lambda t,l,a:a.update({'extra':a['article-1']})),
 ('wrong_slug',lambda t,l,a:t['slate'][1].update(slug='article-other')),
 ('wrong_section',lambda t,l,a:t['slate'][2].update(section='food')),
 ('wrong_track',lambda t,l,a:t['slate'][2].update(track='lost-ways')),
 ('path_slash',lambda t,l,a:t['slate'][2].update(slug='../bad')),
 ('duplicate_url',lambda t,l,a:t['slate'][2].update(slug='article-2')),
 ('bad_oid',lambda t,l,a:l['rows_NOT_APPROVED'][3].update(body_git_blob_oid='0'*40)),
 ('changed_body',lambda t,l,a:a.__setitem__('article-5',(a['article-5'][0]+b' extra',a['article-5'][1]))),
 ('body_type',lambda t,l,a:a.__setitem__('article-5',('text',a['article-5'][1]))),
 ('meta_type',lambda t,l,a:a.__setitem__('article-5',(a['article-5'][0],[]))),
 ('meta_slug',lambda t,l,a:a['article-5'][1].update(slug='not-right')),
 ('meta_section',lambda t,l,a:a['article-5'][1].update(section='food')),
 ('meta_track',lambda t,l,a:a['article-5'][1].update(track='lost-ways')),
 ('meta_publish',lambda t,l,a:a['article-5'][1]['status'].update(publish='published')),
 ('meta_status',lambda t,l,a:a['article-5'][1].pop('status')),
 ('meta_scopes',lambda t,l,a:a['article-5'][1].pop('source_use')),
 ('scope_blank',lambda t,l,a:a['article-5'][1]['source_use'].update({'source-one':' '})),
 ('scope_id',lambda t,l,a:a['article-5'][1]['source_use'].update({'source-two':'another source'})),
 ('wrong_cite_count',lambda t,l,a:l['rows_NOT_APPROVED'][3].update(raw_citation_occurrences=2)),
 ('wrong_source_count',lambda t,l,a:l['rows_NOT_APPROVED'][3].update(distinct_author_scoped_source_ids=9)),
 ('global_occurrences',lambda t,l,a:l.update(raw_citation_occurrences_total=34)),
 ('global_scopes',lambda t,l,a:l.update(article_scoped_source_id_total_NOT_GLOBAL_UNIQUE=34)),
 ('state_approved',lambda t,l,a:a['article-5'][1]['safety_review'].update(state='approved')),
 ('state_missing',lambda t,l,a:a['article-5'][1].pop('safety_review')),
 ('state_invalid',lambda t,l,a:a['article-5'][1]['safety_review'].update(state='safe')),
 ('state_ledger',lambda t,l,a:l['self_reported_safety_metadata_counts'].update(pending=30)),
]
for name,mutate in MUTANTS:
    def build(m):
        def test(self):
            t,l,a=example();m(t,l,a)
            with self.assertRaises((g.EvidenceHold,KeyError,TypeError,ValueError)):
                g.verify(t,l,a)
        return test
    setattr(Evidence,'test_mutation_'+name,build(mutate))
if __name__=='__main__':unittest.main()
