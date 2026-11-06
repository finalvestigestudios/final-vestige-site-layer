"""Synthetic/adversarial checks only. These do not review actual article safety."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'tools/r178_safety_state_admission_gate.py'
spec = importlib.util.spec_from_file_location('r178_safety_gate', SOURCE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

SLUGS = [f'article-{i:02d}' for i in range(1, 36)]
LEGACY = ['article-11', 'article-25']
NOT_REQUIRED = ['article-13', 'article-18', 'article-23', 'article-26']


def write_json(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def fixture(directory):
    root = Path(directory)
    article_path = root / gate.ARTICLES
    article_path.mkdir(parents=True)
    records = []
    originals = {}
    for index, slug in enumerate(SLUGS, start=1):
        state = ('approved' if slug in LEGACY else 'not-required'
                 if slug in NOT_REQUIRED else 'pending')
        source_use = {f'proof-{j}': 'This is a synthetic source used solely by test fixture.'
                      for j in range(11)}
        note = ('This was not an independent safety review; QD not performed; '
                'scope was not confirmed.' if state == 'approved'
                else 'A human editorial review is still required.'
                if state == 'not-required' else 'Awaiting review.')
        meta = {'slug': slug, 'n': index, 'section': 'testing',
                'status': {'publish': 'draft'},
                'safety_review': {'state': state, 'scope': note},
                'source_use': source_use}
        meta_file = article_path / (slug + '.meta.json')
        write_json(meta_file, meta)
        citations = 58 if index <= 5 else 57
        body = ' '.join('{{cite:proof-%s}}' % (i % 11)
                        for i in range(citations)) + ' ' + 'evidence ' * 1550
        body_file = article_path / (slug + '.body.html')
        body_file.write_text(body, encoding='utf-8')
        records.append({'slug': slug, 'meta_git_blob': gate.git_blob(meta_file.read_bytes()),
                        'article_number': index, 'recorded_state': state,
                        'source_use_count': 11})
        originals[slug] = {'citations': citations,
                           'git_blob': gate.git_blob(body_file.read_bytes())}
    assert sum(x['citations'] for x in originals.values()) == 2000
    custody = {'article_count': 35, 'article_source_relationships': 385,
               'articles': originals}
    custody_file = root / gate.CUSTODY_PATH
    write_json(custody_file, custody)
    baseline = {'schema': gate.SCHEMA, 'state': gate.HOLD,
                'r161_body_custody_blob': gate.CUSTODY_GIT_BLOB,
                'expected_articles': 35, 'expected_citations': 2000,
                'expected_source_use': 385,
                'recorded_state_counts': {'pending': 29, 'not-required': 4,
                                          'approved': 2},
                'historical_labels_are_not_approvals': True,
                'publication_authorized': False, 'independent_qd_pass': False,
                'qualified_safety_review_complete': False,
                'legacy_approved_unverified': LEGACY,
                'not_required_still_editorial_hold': NOT_REQUIRED,
                'articles': records}
    # For unit-test fixtures only: the six test exceptions are named differently.
    baseline['legacy_approved_unverified'] = ['making-water-safer',
                                           'salt-beef-salt-pork-age-of-sail']
    baseline['not_required_still_editorial_hold'] = [
        'navigation-before-gps', 'pioneer-supply-chains-failed',
        'root-cellars-cool-storage', 'sanitation-before-germ-theory']
    # The production validator pins these *actual* exception names. Fixtures must
    # use those six names too; substitute the list of fixture slugs consistently.
    rename = dict(zip(LEGACY + NOT_REQUIRED,
                      baseline['legacy_approved_unverified'] +
                      baseline['not_required_still_editorial_hold']))
    # Regenerate file pairs and custody with authentic exception slugs and
    # maintain a canonical sorted article roster after rename.
    for old, new in rename.items():
        (article_path / (old+'.meta.json')).rename(article_path / (new+'.meta.json'))
        (article_path / (old+'.body.html')).rename(article_path / (new+'.body.html'))
        item = next(x for x in records if x['slug'] == old)
        mpath = article_path / (new+'.meta.json')
        m = json.loads(mpath.read_text()); m['slug'] = new; write_json(mpath, m)
        item['slug'] = new
        item['meta_git_blob'] = gate.git_blob(mpath.read_bytes())
        custody['articles'][new] = custody['articles'].pop(old)
    # Avoid collisions with existing fixture slugs if exception names differ.
    records.sort(key=lambda row: row['slug'])
    write_json(custody_file, custody)
    pins_file = root / gate.PIN_PATH
    write_json(pins_file, baseline)
    digest = hashlib.sha256(pins_file.read_bytes()).hexdigest()
    blob = gate.git_blob(custody_file.read_bytes())
    return root, digest, blob, records


class SafetyStateAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='fv-prep-r178-test-')
        self.repo, self.sha, self.custody, self.records = fixture(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self):
        return gate.inspect(self.repo, pins_sha256=self.sha,
                            custody_git_blob=self.custody)

    def assert_invalid(self):
        report = self.check()
        self.assertEqual(report['state'], gate.INVALID, report)
        self.assertFalse(report['publication_authorized'])
        self.assertFalse(report['independent_qd_pass'])
        self.assertTrue(report['errors'])

    def test_intact_synthetic_corpus_remains_hold(self):
        report = self.check()
        self.assertEqual(report['state'], gate.HOLD, report)
        self.assertEqual((report['article_count'], report['citations'],
                          report['source_use']), (35, 2000, 385))
        self.assertEqual(report['human_review_admission'], 'NONE')
        self.assertEqual(len(report['legacy_approved_unverified']), 2)
        self.assertEqual(len(report['not_required_editorial_hold']), 4)
        self.assertFalse(report['food_safety_approved'])
        self.assertFalse(report['commercial_product_verified'])

    def test_missing_meta(self):
        (self.repo/gate.ARTICLES/(self.records[0]['slug']+'.meta.json')).unlink()
        self.assert_invalid()

    def test_duplicate_json_key(self):
        path=self.repo/gate.ARTICLES/(self.records[0]['slug']+'.meta.json')
        path.write_bytes(path.read_bytes().replace(b'"slug":', b'"slug":"bad", "slug":',1))
        self.assert_invalid()

    def test_release_flag_in_roster(self):
        path = self.repo/gate.PIN_PATH
        path.write_text(path.read_text().replace('"publication_authorized": false',
                                                   '"publication_authorized": true'))
        self.assert_invalid()

    def test_main_manifest_changed(self):
        path = self.repo/gate.PIN_PATH
        path.write_bytes(path.read_bytes()+b'\n')
        self.assert_invalid()

    def test_missing_body(self):
        (self.repo/gate.ARTICLES/(self.records[0]['slug']+'.body.html')).unlink()
        self.assert_invalid()

    def test_body_custody_changed(self):
        path = self.repo/gate.CUSTODY_PATH
        path.write_bytes(path.read_bytes()+b' ')
        self.assert_invalid()

    def test_created_unpinned_article(self):
        (self.repo/gate.ARTICLES/'new-article.meta.json').write_text('{}')
        self.assert_invalid()

    def test_symlink_article_file(self):
        path=self.repo/gate.ARTICLES/(self.records[0]['slug']+'.body.html')
        path.unlink();path.symlink_to(self.repo/gate.CUSTODY_PATH)
        self.assert_invalid()

    def test_wrong_pins_sha(self):
        report=gate.inspect(self.repo, pins_sha256='0'*64,
                            custody_git_blob=self.custody)
        self.assertEqual(report['state'], gate.INVALID)

    def test_wrong_custody_blob(self):
        report=gate.inspect(self.repo, pins_sha256=self.sha,
                            custody_git_blob='0'*40)
        self.assertEqual(report['state'], gate.INVALID)


def make_mutation(slug, suffix, mutate):
    def test(self):
        path = self.repo/gate.ARTICLES/(slug+suffix)
        mutate(path)
        self.assert_invalid()
    return test


# Every member of the 35-article roster must be checked, not only the two
# historical 'approved' anomalies. 70 distinct mutation tests are generated.
for key in SLUGS:
    # The six exceptional fixture labels were renamed; resolve by ordinal.
    index=SLUGS.index(key)
    actual = {11:'making-water-safer', 25:'salt-beef-salt-pork-age-of-sail',
              13:'navigation-before-gps', 18:'pioneer-supply-chains-failed',
              23:'root-cellars-cool-storage', 26:'sanitation-before-germ-theory'}.get(index+1,key)
    def tamper_meta(path):
        text=path.read_text();path.write_text(text.replace('"draft"','"publish"',1))
    def tamper_body(path):
        path.write_bytes(path.read_bytes()+b' SILENT ADVICE CHANGE')
    setattr(SafetyStateAdmissionTests, 'test_meta_'+key.replace('-','_'),
            make_mutation(actual,'.meta.json',tamper_meta))
    setattr(SafetyStateAdmissionTests, 'test_body_'+key.replace('-','_'),
            make_mutation(actual,'.body.html',tamper_body))

if __name__ == '__main__':
    unittest.main()
