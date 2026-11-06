"""Isolated R161 checks; all file mutations happen in synthetic TemporaryDirectories."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import r161_body_custody_gate as gate


class BodyCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = tempfile.TemporaryDirectory(prefix='fv-r161-source-')
        root = Path(cls.original.name)
        articles = root / gate.ARTICLE_DIR
        articles.mkdir(parents=True)
        cls.base = {'schema': gate.SCHEMA, 'status': 'DRAFT_HARD_HOLD',
                                 'source_commit': 'a'*40, 'r151_manifest_git_blob': gate.R151_BLOB,
                                 'article_count': 35, 'total_citations': 700,
                                 'article_source_relationships': 35, 'articles': {}}
        cls.legacy = {'schema': 'fv-preparedness-r151-v1', 'decision': 'DRAFT_HARD_HOLD',
                      'metadata_blobs': {}, 'articles': []}
        states = ['pending']*29 + ['not-required']*4 + ['approved']*2
        for i in range(35):
            slug = f'article-{i:02d}'
            html = '<article><p>' + ' '.join(['substantive']*1520) + '</p>\n' + '<p>Context {{cite:sample-source}}</p>\n'*20 + '</article>'
            meta = {'slug': slug, 'section':'start-here', 'status':{'publish':'draft'},
                    'safety_review':{'state':states[i]},
                    'source_use':{'sample-source':'Author-specific review pending'}}
            b = html.encode('utf8'); m = (json.dumps(meta, sort_keys=True)+'\n').encode('utf8')
            (articles / (slug+'.body.html')).write_bytes(b)
            (articles / (slug+'.meta.json')).write_bytes(m)
            cls.base['articles'][slug] = {'git_blob':gate.git_blob(b), 'citations':20}
            cls.legacy['metadata_blobs'][slug] = gate.git_blob(m)
            if i < 7:
                cls.legacy['articles'].append({'slug':slug,'candidate':{'blob':gate.git_blob(b)}})

    @classmethod
    def tearDownClass(cls):
        cls.original.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fv-r161-case-')
        self.root = Path(self.temp.name)
        shutil.copytree(Path(self.original.name)/'preparedness', self.root/'preparedness')
        self.pins = copy.deepcopy(self.base)
        self.legacy_pins = copy.deepcopy(self.legacy)

    def tearDown(self):
        self.temp.cleanup()

    def body(self, slug='article-08'):
        return self.root / gate.ARTICLE_DIR / (slug+'.body.html')

    def meta(self, slug='article-08'):
        return self.root / gate.ARTICLE_DIR / (slug+'.meta.json')

    def check(self):
        return gate.verify(self.root, self.pins, self.legacy_pins)

    def fail_hold(self, term=None):
        with self.assertRaisesRegex(ValueError, term or '.*'):
            self.check()

    def rewrite_meta(self, change, slug='article-08'):
        path=self.meta(slug)
        data=json.loads(path.read_text())
        change(data)
        raw=(json.dumps(data, sort_keys=True)+'\n').encode('utf8')
        path.write_bytes(raw)
        self.legacy_pins['metadata_blobs'][slug]=gate.git_blob(raw)

    def test_clean_35_article_review_is_still_hard_hold(self):
        v=self.check()
        self.assertEqual((v['articles'],v['citations'],v['source_uses']),(35,700,35))
        self.assertEqual(v['state'],'DRAFT_HARD_HOLD')
        self.assertFalse(v['publication_authorized'])
        self.assertFalse(v['independent_qd_pass'])
        self.assertFalse(v['claim_verification'])

    def test_validation_does_not_write_or_modify_input(self):
        before=self.body().read_bytes()
        self.check()
        self.assertEqual(before,self.body().read_bytes())

    def test_body_text_change_fails_with_unchanged_citation_count(self):
        path=self.body()
        path.write_text(path.read_text().replace('substantive','UNREVIEWED',1))
        self.fail_hold('Git blob drift')

    def test_body_citation_swap_fails_even_with_unchanged_count(self):
        path=self.body()
        path.write_text(path.read_text().replace('{{cite:sample-source}}','{{cite:fake-source}}',1))
        self.fail_hold('Git blob drift')

    def test_reference_manifest_can_not_replace_r151_trust_anchor(self):
        self.pins['r151_manifest_git_blob']='b'*40
        self.fail_hold('trust anchor')

    def test_wrong_frozen_candidate_detected(self):
        self.legacy_pins['articles'][0]['candidate']['blob']='f'*40
        self.fail_hold('seven-branch')

    def test_35_file_census_rejects_new_unreviewed_article(self):
        (self.root/gate.ARTICLE_DIR/'extra.body.html').write_text('unreviewed')
        self.fail_hold('article pairs')

    def test_missing_body_rejected(self):
        self.body().unlink()
        self.fail_hold('article pairs')

    def test_replaced_body_symlink_rejected(self):
        path=self.body()
        original=self.body('article-09')
        path.unlink()
        path.symlink_to(original)
        self.fail_hold('symlink')

    def test_source_use_can_not_be_reassigned_even_with_repin_meta(self):
        self.rewrite_meta(lambda m: m['source_use'].update({'invented':'Unsupported source'}))
        self.fail_hold('unmapped')

    def test_source_use_forgery_detected_by_pinned_metadata(self):
        path=self.meta()
        path.write_text(path.read_text().replace('Author-specific','Invented'))
        self.fail_hold('Git blob drift')

    def test_safety_approval_forgery_rejected_even_with_synthetic_repin(self):
        self.rewrite_meta(lambda m: m['safety_review'].__setitem__('state','approved'))
        self.fail_hold('safety-state distribution')

    def test_publishing_a_single_article_rejected(self):
        self.rewrite_meta(lambda m: m['status'].__setitem__('publish','publish'))
        self.fail_hold('publication drift')

    def test_no_reduction_of_article_citations(self):
        path=self.body()
        raw=path.read_bytes().replace(b'{{cite:sample-source}}',b'',1)
        path.write_bytes(raw)
        self.pins['articles']['article-08']['git_blob']=gate.git_blob(raw)
        self.fail_hold('citation count')

    def test_no_reduction_of_reading_depth(self):
        path=self.body()
        raw=path.read_text().replace('substantive ', '', 150).encode('utf8')
        path.write_bytes(raw)
        self.pins['articles']['article-08']['git_blob']=gate.git_blob(raw)
        self.fail_hold('reading-depth')

    def test_no_malformed_citation_even_with_same_valid_count(self):
        path=self.body()
        raw=path.read_text().replace('{{cite:sample-source}}','{{cite:UPPERCASE}}',1).encode('utf8')
        path.write_bytes(raw)
        self.pins['articles']['article-08']['git_blob']=gate.git_blob(raw)
        self.fail_hold('citation count/markup')

    def test_total_citations_enforced(self):
        self.pins['total_citations']=701
        self.fail_hold('total original citations')

    def test_total_source_uses_enforced(self):
        self.pins['article_source_relationships']=36
        self.fail_hold('source-use count')

    def test_manifest_requires_35_bodies(self):
        self.pins['articles'].pop('article-09')
        self.fail_hold('35 article bodies')

    def test_unknown_recorded_safety_state_rejected(self):
        self.rewrite_meta(lambda m: m['safety_review'].__setitem__('state','passed'))
        self.fail_hold('invalid recorded safety state')

    def test_cli_never_returns_exit_zero(self):
        with contextlib.redirect_stdout(io.StringIO()) as b:
            code=gate.main(['--repo',str(self.root)])
        self.assertEqual(code,2)
        self.assertIn('INVALID_HARD_HOLD',b.getvalue())


def _build_single_article_mutation(i):
    def check(self):
        slug=f'article-{i:02d}'
        path=self.body(slug)
        # No citation count or reading depth change: R160's local contexts may
        # remain unchanged, but R161 must reject ANY original-body mutation.
        path.write_text(path.read_text().replace('substantive','altered',1))
        self.fail_hold('Git blob drift')
    check.__name__=f'test_frozen_body_{i:02d}_rejects_unreviewed_claim_edit'
    return check

for _i in range(35):
    setattr(BodyCustodyTests, f'test_frozen_body_{_i:02d}_rejects_unreviewed_claim_edit', _build_single_article_mutation(_i))

if __name__ == '__main__':
    unittest.main()
