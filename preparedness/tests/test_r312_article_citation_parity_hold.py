"""R312 source parity tests: all fixtures in temporary trees; no real source writes."""
from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('r312_tested', HERE / 'tools/r312_article_citation_parity_hold.py')
r312 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r312)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='fv-r312-citations-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.dir = self.root / 'preparedness/content/articles'
        self.dir.mkdir(parents=True)
        self.ledger = {'articles': []}
        for n in range(1, 36):
            slug = f'article-{n}'
            body = f'<section><p>Claim {n} {{' + '{cite:source-a}}' + '<a>more</a> {{link:family-reunification-card|card}}</p></section>'
            meta = {'slug':slug,'status':{'editorial':'drafted','publish':'draft'},
                    'safety_review':{'state':'pending'},'source_use':{'source-a':'Official guidance with caveats'}}
            bp = self.dir / f'{slug}.body.html'
            mp = self.dir / f'{slug}.meta.json'
            bp.write_text(body,encoding='utf-8')
            mp.write_text(json.dumps(meta),encoding='utf-8')
            self.ledger['articles'].append({'slug':slug,'route':f'/preparedness/start-here/{slug}/',
                                            'integrated_body_blob':r312.r310.oid(bp.read_bytes()),
                                            'integrated_meta_blob':r312.r310.oid(mp.read_bytes())})

    def check(self, code: str):
        result = r312.audit_articles(self.root,self.ledger)
        self.assertTrue(any(s.startswith(code) for s in result['errors']), result['errors'])
        self.assertEqual(result['state'],'INVALID_HARD_HOLD')
        self.assertFalse(result['publication_authorized'])

    def mutate_meta(self, n: int, action):
        path=self.dir/f'article-{n}.meta.json'
        data=json.loads(path.read_text());action(data)
        path.write_text(json.dumps(data),encoding='utf-8')
        self.ledger['articles'][n-1]['integrated_meta_blob']=r312.r310.oid(path.read_bytes())

    def mutate_body(self,n:int,action):
        path=self.dir/f'article-{n}.body.html'
        path.write_text(action(path.read_text()),encoding='utf-8')
        self.ledger['articles'][n-1]['integrated_body_blob']=r312.r310.oid(path.read_bytes())


class ArticleIntegrityTests(Fixture):
    def test_35_input_baseline_kept_on_hold(self):
        out=r312.audit_articles(self.root,self.ledger)
        self.assertEqual(out['state'],'DRAFT_HARD_HOLD',out['errors'])
        self.assertEqual((out['article_count'],out['verified_article_input_blobs'],out['citation_occurrences']),(35,70,35))
        self.assertEqual(out['distinct_cited_source_ids'],['source-a'])
        self.assertEqual(len(out['article_source_context_crosswalk']),35)
        self.assertTrue(all(len(row['context_witnesses'])==1 for row in out['article_source_context_crosswalk']))
        self.assertFalse(out['independent_qd_pass'])
        self.assertFalse(out['medical_safety_verified'])
        self.assertFalse(out['actual_41_wordpress_drafts_verified'])
        self.assertFalse(out['merchant_paid_orders_verified'])

    def test_changed_body_detected_by_exact_pin(self):
        p=self.dir/'article-1.body.html';p.write_text(p.read_text()+' changed')
        self.check('ARTICLE_INTEGRATED_BLOB_DRIFT:')

    def test_changed_meta_detected_by_exact_pin(self):
        p=self.dir/'article-2.meta.json';p.write_text(p.read_text()+' ')
        self.check('ARTICLE_INTEGRATED_BLOB_DRIFT:')

    def test_invalid_slug(self):
        self.ledger['articles'][0]['slug']='../../secret'
        self.check('MISSING_DUPLICATE_OR_MALFORMED_ARTICLE_SLUG')

    def test_duplicate_slug(self):
        self.ledger['articles'][0]['slug']='article-2'
        self.check('MISSING_DUPLICATE_OR_MALFORMED_ARTICLE_SLUG')

    def test_duplicate_route(self):
        self.ledger['articles'][0]['route']=self.ledger['articles'][1]['route']
        self.check('DUPLICATE_OR_MALFORMED_CANONICAL_ROUTE')

    def test_route_escape(self):
        self.ledger['articles'][0]['route']='/outside/archive/'
        self.check('DUPLICATE_OR_MALFORMED_CANONICAL_ROUTE')

    def test_short_slate(self):
        self.ledger['articles'].pop()
        self.check('EXACTLY_35_ARTICLES_REQUIRED')

    def test_untracked_article_file(self):
        (self.dir/'extra.meta.json').write_text('{}')
        self.check('ARTICLE_INPUT_SET_DRIFT')

    def test_missing_article_body(self):
        (self.dir/'article-2.body.html').unlink()
        self.check('ARTICLE_INPUT_MISSING_OR_SYMLINK:')

    def test_missing_article_meta(self):
        (self.dir/'article-2.meta.json').unlink()
        self.check('ARTICLE_INPUT_MISSING_OR_SYMLINK:')

    def test_symlink_article_body(self):
        p=self.dir/'article-3.body.html';saved=p.read_bytes();p.unlink();outside=self.root/'outside';outside.write_bytes(saved);p.symlink_to(outside)
        self.check('ARTICLE_INPUT_MISSING_OR_SYMLINK:')

    def test_invalid_json(self):
        p=self.dir/'article-4.meta.json';p.write_text('{');self.ledger['articles'][3]['integrated_meta_blob']=r312.r310.oid(p.read_bytes())
        self.check('ARTICLE_BAD_ENCODING_OR_METADATA:')

    def test_non_object_metadata(self):
        self.mutate_meta(2,lambda x:None)
        p=self.dir/'article-2.meta.json';p.write_text('[]');self.ledger['articles'][1]['integrated_meta_blob']=r312.r310.oid(p.read_bytes())
        self.check('META_NOT_OBJECT:')

    def test_false_publish_pass(self):
        self.mutate_meta(1,lambda v:v['status'].update(publish='publish'))
        self.check('ARTICLE_NOT_DRAFT:')

    def test_false_safety_pass(self):
        self.mutate_meta(1,lambda v:v['safety_review'].update(state='approved'))
        self.check('UNAUTHORIZED_SAFETY_APPROVAL:')

    def test_absent_source_use(self):
        self.mutate_meta(1,lambda v:v.pop('source_use'))
        self.check('SOURCE_USE_NOT_OBJECT:')

    def test_source_use_not_a_dict(self):
        self.mutate_meta(1,lambda v:v.update(source_use=[]))
        self.check('SOURCE_USE_NOT_OBJECT:')

    def test_orphan_body_citation(self):
        self.mutate_body(1,lambda s:s+'{{cite:source-b}}')
        self.check('CITATION_NOT_DECLARED:')

    def test_orphan_meta_citation(self):
        self.mutate_meta(1,lambda v:v['source_use'].update({'source-b':'review'}))
        self.check('SOURCE_USE_WITHOUT_CITATION:')

    def test_malformed_citation_missing_closure(self):
        self.mutate_body(1,lambda s:s.replace('{{cite:source-a}}','{{cite:source-a}'))
        self.check('MALFORMED_CITATION_TOKEN:')

    def test_malformed_citation_bad_identifier(self):
        self.mutate_body(1,lambda s:s.replace('cite:source-a','cite:source_A'))
        self.check('MALFORMED_CITATION_ID:')

    def test_bad_source_use_value(self):
        self.mutate_meta(1,lambda v:v['source_use'].update({'source-a':' '}))
        self.check('SOURCE_USE_INVALID_ENTRY:')

    def test_incorrect_metadata_slug(self):
        self.mutate_meta(1,lambda v:v.update(slug='article-wrong'))
        self.check('METADATA_SLUG_DRIFT:')

    def test_unknown_authored_link(self):
        self.mutate_body(1,lambda s:s+'{{link:nonexistent-tool|here}}')
        self.check('UNRESOLVED_AUTHORED_LINK:')

    def test_malformed_link(self):
        self.mutate_body(1,lambda s:s+'{{link:broken')
        self.check('MALFORMED_INTERNAL_LINK_TOKEN:')

    def test_impossible_link_identifier(self):
        self.mutate_body(1,lambda s:s+'{{link:/path|test}}')
        self.check('MALFORMED_INTERNAL_LINK_TARGET:')

    def test_context_hash_changes_with_claim(self):
        before=r312.audit_articles(self.root,self.ledger)['article_source_context_crosswalk'][0]['context_witnesses'][0]['prior_text_sha256']
        self.mutate_body(1,lambda s:s.replace('Claim 1','New claim'))
        after=r312.audit_articles(self.root,self.ledger)['article_source_context_crosswalk'][0]['context_witnesses'][0]['prior_text_sha256']
        self.assertNotEqual(before,after)

    def test_article_source_crosswalk_has_no_claim_approval(self):
        row=r312.audit_articles(self.root,self.ledger)['article_source_context_crosswalk'][0]
        self.assertNotIn('verified_safe',row)
        self.assertEqual(row['safety_state'],'pending')

    def test_registered_and_machine_verified_source_is_not_safety_pass(self):
        rows = [{'cited_ids':['source-a']}]
        result = r312.source_coverage(rows, {'sources.json':{'sources':[
            {'id':'source-a','verified_on':'2026-11-01','human_link_check':False}]}})
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['no_human_link_witness'],['source-a'])
        self.assertFalse(result['human_safety_review_passed'])

    def test_unregistered_article_source_fails_closed(self):
        result = r312.source_coverage([{'cited_ids':['missing']}], {'sources.json':{'sources':[]}})
        self.assertIn('ARTICLE_CITED_SOURCE_NOT_REGISTERED:missing',result['errors'])

    def test_placeholder_article_source_fails_closed(self):
        result = r312.source_coverage([{'cited_ids':['source-a']}], {'sources.json':{'sources':[
            {'id':'source-a','verified_on':None}]}})
        self.assertIn('ARTICLE_CITED_SOURCE_NOT_FETCH_VERIFIED:source-a',result['errors'])

    def test_competing_fetched_article_sources_fail_closed(self):
        result = r312.source_coverage([{'cited_ids':['source-a']}], {'one':{'sources':[
            {'id':'source-a','verified_on':'2026-11-01'}]},'two':{'sources':[
            {'id':'source-a','verified_on':'2026-11-02'}]}})
        self.assertIn('ARTICLE_MULTIPLE_FETCHED_SOURCE_RECORDS:source-a',result['errors'])

    def test_unreadable_source_fragment_rejected(self):
        result = r312.source_coverage([{'cited_ids':[]}], {'broken':None})
        self.assertIn('SOURCE_FRAGMENT_UNREADABLE:broken',result['errors'])

    def test_incomplete_checkout_fails_closed(self):
        script=HERE/'tools/r312_article_citation_parity_hold.py'
        p=subprocess.run([sys.executable,'-I',str(script),'--root',str(self.root)],capture_output=True,text=True)
        self.assertEqual(p.returncode,1,p.stdout+p.stderr)
        self.assertEqual(json.loads(p.stdout)['state'],'INVALID_HARD_HOLD')


# Different missing/mutated authentic-input cases are separately named tests.
for i in range(1, 15):
    def drift(self, n=i):
        p=self.dir/f'article-{n}.body.html'
        p.write_bytes(p.read_bytes()+b'\n')
        self.check('ARTICLE_INTEGRATED_BLOB_DRIFT:')
    setattr(ArticleIntegrityTests,f'test_individual_body_blob_drift_{i:02d}',drift)

for i in range(15, 29):
    def missing(self, n=i):
        (self.dir/f'article-{n}.meta.json').unlink()
        self.check('ARTICLE_INPUT_MISSING_OR_SYMLINK:')
    setattr(ArticleIntegrityTests,f'test_individual_metadata_missing_{i:02d}',missing)

if __name__ == '__main__':unittest.main()
