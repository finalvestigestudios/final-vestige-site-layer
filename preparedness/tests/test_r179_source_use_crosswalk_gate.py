"""Synthetic cases only: never turn source inventory tests into safety approval."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1]/'tools/r179_source_use_crosswalk_gate.py'
spec = importlib.util.spec_from_file_location('r179_crosswalk', TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fixture():
    slugs = [f'article-{i:02d}' for i in range(35)]
    uses = {f'source-{i:02d}': 'Synthetic interpretation, not a human source review.' for i in range(11)}
    pins = {'articles': []}
    custody = {'article_count': 35, 'article_source_relationships': 385,
               'articles': {}}
    meta = {}
    bodies = {}
    for i, slug in enumerate(slugs):
        state = 'approved' if i in (5, 20) else 'not-required' if i in (13, 16, 27, 32) else 'pending'
        pins['articles'].append({'slug':slug,'article_number':i+1,'recorded_state':state,
                                 'source_use_count':11})
        metadata = {'n':i+1,'slug':slug,'section':'test',
                    'status':{'publish':'draft'},'safety_review':{'state':state},
                    'source_use':dict(uses)}
        meta[slug] = metadata
        count = 58 if i < 5 else 57
        bodies[slug] = '<p>' + ''.join('{{cite:source-%02d}}' % (j % 11) for j in range(count)) + '</p>'
        custody['articles'][slug] = {'citations':count, 'git_blob':'0'*40}
    inventories = {f'fragments/{key}.json':{'sources': []} for key in ('food','health','hist-field','hist-food','hist-home','shelter','start')}
    inventories['register.json'] = {'sources': [
        {'id':f'source-{i:02d}', 'url':f'https://example.org/evidence/{i}',
         'verified_on':'2026-10-01', 'human_link_check':False}
        for i in range(11)]}
    return pins,custody,meta,bodies,inventories


class CrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.pins,self.custody,self.meta,self.bodies,self.inv=fixture()

    def run_crosswalk(self):
        return mod.build_crosswalk(self.pins,self.custody,self.meta,self.bodies,self.inv)

    def test_full_synthetic_slate_is_still_hold(self):
        r = self.run_crosswalk()
        self.assertEqual(r['state'],mod.HOLD)
        self.assertEqual((r['article_count'],r['citation_occurrences'],r['article_source_relationships']),
                         (35,2000,385))
        self.assertEqual(len(r['crosswalk']),385)
        self.assertFalse(r['independent_qd_pass'])
        self.assertFalse(r['commercial_product_verified'])
        self.assertFalse(r['publication_authorized'])
        self.assertTrue(all(row['independently_reviewed_claim'] is False for row in r['crosswalk']))

    def test_digest_stable_on_reordered_dictionary_inputs(self):
        first = self.run_crosswalk()['crosswalk_sha256']
        self.meta=dict(reversed(list(self.meta.items())))
        self.inv=dict(reversed(list(self.inv.items())))
        self.assertEqual(self.run_crosswalk()['crosswalk_sha256'],first)

    def test_source_scope_changes_digest(self):
        first=self.run_crosswalk()['crosswalk_sha256']
        self.meta['article-01']['source_use']['source-02']='Different human review scope.'
        self.assertNotEqual(self.run_crosswalk()['crosswalk_sha256'],first)

    def test_duplicate_source_identical_url_is_not_resolved_automatically(self):
        self.inv['fragments/start.json']['sources'].append(
            {'id':'source-01','url':'https://example.org/evidence/1','verified_on':None})
        r=self.run_crosswalk()
        self.assertEqual(r['duplicate_source_id_groups'],['source-01'])
        self.assertEqual(next(x for x in r['crosswalk'] if x['source_id']=='source-01')['inventory_record_count'],2)

    def test_conflicting_source_id_url_rejected(self):
        self.inv['fragments/food.json']['sources'].append(
            {'id':'source-01','url':'https://attacker.example.org/changed'})
        with self.assertRaisesRegex(ValueError,'conflicting original source URLs'):
            self.run_crosswalk()

    def test_shared_literal_urls_are_review_groups(self):
        self.inv['fragments/health.json']['sources'].append(
            {'id':'a-new-source','url':'https://example.org/evidence/1'})
        r=self.run_crosswalk()
        self.assertIn(['a-new-source','source-01'],r['shared_literal_url_groups'])
        self.assertFalse(r['publication_authorized'])

    def test_trailing_slash_is_not_silently_normalized(self):
        self.inv['fragments/health.json']['sources'].append(
            {'id':'a-new-source','url':'https://example.org/evidence/1/'})
        r=self.run_crosswalk()
        self.assertEqual(len(r['trailing_slash_review_groups']),1)
        self.assertEqual(r['crosswalk'][0]['source_url'],'https://example.org/evidence/0')

    def test_source_url_query_is_legitimate_literal_identity(self):
        self.inv['register.json']['sources'][0]['url']='https://www.loc.gov/book/?st=list'
        self.assertEqual(self.run_crosswalk()['article_count'],35)

    def test_http_or_credentialed_source_rejected(self):
        for bad in ('http://example.org/unsafe','https://a:b@example.org/a',
                    'https://example.org/a#fragment','https://example.org:444/a',
                    'javascript:alert(1)','https://example.org/a b'):
            with self.subTest(url=bad):
                copy_inv=copy.deepcopy(self.inv)
                copy_inv['register.json']['sources'][0]['url']=bad
                with self.assertRaises(ValueError):
                    mod.build_crosswalk(self.pins,self.custody,self.meta,self.bodies,copy_inv)

    def test_unfetched_not_promoted_to_claim_approval(self):
        self.inv['register.json']['sources'][1]['verified_on']=None
        r=self.run_crosswalk()
        self.assertEqual(len([x for x in r['unfetched_source_uses'] if x['source_id']=='source-01']),35)
        self.assertFalse(r['human_source_claim_review_complete'])

    def test_uncited_relationship_is_explicit(self):
        # Drop all source-10 token occurrences by replacing with source-09.
        for slug,body in self.bodies.items():
            self.bodies[slug]=body.replace('cite:source-10','cite:source-09')
        r=self.run_crosswalk()
        self.assertEqual(len(r['uncited_author_source_uses']),35)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
            json.loads('{"url":"a","url":"b"}',object_pairs_hook=mod.unique_dict)

    def test_read_only_invalid_on_incomplete_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            out=mod.inspect_repo(Path(folder))
            self.assertEqual(out['state'],mod.INVALID)
            self.assertFalse(out['publication_authorized'])
            self.assertTrue(out['errors'])

    def test_cli_missing_checkout_exits_2_not_0(self):
        with tempfile.TemporaryDirectory() as folder:
            proc=subprocess.run([sys.executable,str(TOOL),'--repo',folder,'--summary'],
                                capture_output=True,text=True,timeout=15)
            self.assertEqual(proc.returncode,2)
            self.assertEqual(json.loads(proc.stdout)['state'],mod.INVALID)

    def test_missing_article(self):
        self.meta.pop('article-00')
        with self.assertRaisesRegex(ValueError,'35-article source corpus identities'):
            self.run_crosswalk()

    def test_extra_article(self):
        self.bodies['intruder']='<p>...</p>'
        with self.assertRaisesRegex(ValueError,'35-article source corpus identities'):
            self.run_crosswalk()

    def test_missing_inventory_source(self):
        self.inv['register.json']['sources'].pop()
        with self.assertRaisesRegex(ValueError,'source identifier not present'):
            self.run_crosswalk()

    def test_duplicate_roster_entry(self):
        self.pins['articles'][-1] = copy.deepcopy(self.pins['articles'][0])
        with self.assertRaises(ValueError):
            self.run_crosswalk()

    def test_total_custody_mismatch(self):
        self.custody['article_source_relationships']=384
        with self.assertRaises(ValueError):
            self.run_crosswalk()

    def test_empty_scope_rejected(self):
        self.meta['article-10']['source_use']['source-03']='   '
        with self.assertRaisesRegex(ValueError,'malformed or empty'):
            self.run_crosswalk()

    def test_published_status_rejected(self):
        self.meta['article-20']['status']['publish']='published'
        with self.assertRaisesRegex(ValueError,'invalid article identity or publication state'):
            self.run_crosswalk()

    def test_historical_safety_state_changed_rejected(self):
        self.meta['article-20']['safety_review']['state']='approved-by-bot'
        with self.assertRaisesRegex(ValueError,'modified historical safety state'):
            self.run_crosswalk()

    def test_not_filled_source_inventory_rejected(self):
        self.inv['register.json']['sources']=[]
        with self.assertRaises(ValueError):
            self.run_crosswalk()

    def test_extra_citation_rejected(self):
        self.bodies['article-00']+='{{cite:source-02}}'
        with self.assertRaisesRegex(ValueError,'citation occurrences changed'):
            self.run_crosswalk()

    def test_undeclared_citation_rejected(self):
        self.bodies['article-00']=self.bodies['article-00'].replace('cite:source-00','cite:source-99',1)
        with self.assertRaisesRegex(ValueError,'citation not declared'):
            self.run_crosswalk()


def mutation_test(slug, kind):
    def test(self):
        if kind=='source-id':
            self.meta[slug]['source_use']['fake-reference']='Incorrect source assertion'
            del self.meta[slug]['source_use']['source-09']
            with self.assertRaisesRegex(ValueError,'citation not declared by author'):
                self.run_crosswalk()
        elif kind=='citation-loss':
            self.bodies[slug]=self.bodies[slug].replace('{{cite:source-01}}','',1)
            with self.assertRaisesRegex(ValueError,'citation occurrences changed'):
                self.run_crosswalk()
        elif kind=='publish':
            self.meta[slug]['status']['publish']='published'
            with self.assertRaisesRegex(ValueError,'invalid article identity'):
                self.run_crosswalk()
        elif kind=='safety-label':
            self.meta[slug]['safety_review']['state']='approved'
            if self.meta[slug]['safety_review']['state']==next(r for r in self.pins['articles'] if r['slug']==slug)['recorded_state']:
                self.meta[slug]['safety_review']['state']='not-required'
            with self.assertRaisesRegex(ValueError,'modified historical safety state'):
                self.run_crosswalk()
    return test

# 140 different per-article hostile edits, plus hand-written global test cases.
for i in range(35):
    for kind in ('source-id','citation-loss','publish','safety-label'):
        name=f'test_mutation_{i:02d}_{kind.replace("-","_")}'
        setattr(CrosswalkTests,name,mutation_test(f'article-{i:02d}',kind))


if __name__=='__main__':
    unittest.main()
