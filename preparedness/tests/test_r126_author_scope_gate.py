"""R126 isolated synthetic tests; never writes the repo working tree."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

TARGET = Path(__file__).with_name('r126_author_scope_gate.py')
SPEC = importlib.util.spec_from_file_location('r126_author_scope_gate', TARGET)
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def fixture():
    urls = [f'https://example.org/source/{i:02d}' for i in range(32)]
    groups = []
    for i, url in enumerate(urls):
        groups.append({'url': url, 'review_status': G.PENDING,
                       'reviewer': None, 'reviewed_on': None,
                       'variants': [{'origin': 'base', 'source': {'id': f'id-{i:02d}', 'url': url}},
                                    {'origin': 'food', 'source': {'id': f'food-{i:02d}', 'url': url}}]})
    names = [f'article-{i:02d}' for i in range(35)]
    crosswalk = {'status': 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
                 'groups': groups, '_observed_blob_sha': 'b' * 40,
                 'article_origins': {n: 'base' for n in names}}
    taxonomy = {'slate': [{'slug': n} for n in names], '_observed_blob_sha': 'c' * 40}
    parts = []
    for index, (lo, hi) in enumerate(((0, 12), (12, 24), (24, 35))):
        rows = []
        for j in range(lo, hi):
            key = j % 32
            rows.append({'slug': names[j], 'origin': 'base',
                         'metadata_blob_sha': 'a' * 40, 'publish': 'draft',
                         'safety_state': 'pending', 'total_declared_source_uses': 1,
                         'shared_source_bindings': [{
                             'source_id': f'id-{key:02d}', 'source_record_origin': 'base',
                             'shared_url': urls[key], 'source_use_scope': 'Declared author reading scope'}]})
        parts.append({'schema': 'fv-r126-author-source-binding-part-v1',
                      'partition': G.PARTS[index], 'state': 'DRAFT_UNREVIEWED_HOLD',
                      'candidate_git_commit': G.RC, 'crosswalk_git_commit': G.PARENT,
                      'crosswalk_git_blob': 'b'*40, 'taxonomy_git_blob': 'c'*40,
                      'crosswalk_group_count': 32, 'articles': rows})
    return crosswalk, taxonomy, parts


class Synthetic(unittest.TestCase):
    def setUp(self):
        self.c, self.t, self.p = fixture()

    def rejects(self, code):
        with self.assertRaisesRegex(G.Hold, code):
            G.audit(self.c, self.t, self.p)

    def test_valid_stays_hold(self):
        result = G.audit(self.c, self.t, self.p)
        self.assertEqual(result['article_count'], 35)
        self.assertEqual(result['author_scope_bindings'], 35)
        self.assertEqual(result['unreviewed_shared_url_groups'], 32)
        self.assertFalse(result['may_publish'])
        self.assertFalse(result['medical_safety_verified'])

    def test_deterministic(self):
        self.assertEqual(G.audit(self.c, self.t, self.p), G.audit(self.c, self.t, self.p))

    def test_missing_article(self):
        self.p[1]['articles'].pop()
        self.rejects('PART_SIZE')

    def test_duplicate_slug(self):
        self.p[0]['articles'][1]['slug'] = self.p[0]['articles'][0]['slug']
        self.rejects('ARTICLE_ROSTER_ORDER')

    def test_wrong_order(self):
        self.p.reverse()
        self.rejects('PART_ORDER')

    def test_wrong_candidate_ref(self):
        self.p[0]['candidate_git_commit'] = 'x'*40
        self.rejects('PIN_DRIFT')

    def test_crosswalk_sha(self):
        self.p[0]['crosswalk_git_blob'] = 'x'*40
        self.rejects('CROSSWALK_BLOB_DRIFT')

    def test_taxonomy_sha(self):
        self.p[0]['taxonomy_git_blob'] = 'x'*40
        self.rejects('TAXONOMY_BLOB_DRIFT')

    def test_rogue_publish(self):
        self.p[0]['articles'][0]['publish'] = 'published'
        self.rejects('UNAUTHORIZED_PUBLICATION')

    def test_rogue_safety_state(self):
        self.p[0]['articles'][0]['safety_state'] = 'verified'
        self.rejects('INVALID_SAFETY_STATE')

    def test_wrong_article_origin(self):
        self.p[0]['articles'][0]['origin'] = 'health'
        self.rejects('AUTHOR_ORIGIN')

    def test_invalid_group(self):
        self.p[0]['articles'][0]['shared_source_bindings'][0]['shared_url'] = 'https://other.org'
        self.rejects('UNKNOWN_SHARED_GROUP')

    def test_source_id_swap(self):
        self.p[0]['articles'][0]['shared_source_bindings'][0]['source_id'] = 'other'
        self.rejects('FOREIGN_AUTHOR_SCOPE')

    def test_foreign_origin_claim(self):
        self.p[0]['articles'][0]['shared_source_bindings'][0]['source_record_origin'] = 'food'
        self.rejects('SOURCE_SCOPE_SUBSTITUTION')

    def test_duplicate_binding(self):
        row = self.p[0]['articles'][0]['shared_source_bindings']
        row.append(copy.deepcopy(row[0]))
        self.rejects('DUPLICATE_BINDING')

    def test_missing_groups(self):
        self.c['groups'].pop()
        self.rejects('CROSSWALK_COUNT')

    def test_approved_group(self):
        self.c['groups'][0]['review_status'] = 'resolved'
        self.rejects('PREMATURE_SOURCE_REVIEW')

    def test_forged_reviewer(self):
        self.c['groups'][0]['reviewer'] = 'somebody'
        self.rejects('PREMATURE_SOURCE_REVIEW')

    def test_missing_schema(self):
        self.p[0]['schema'] = 'other'
        self.rejects('SCHEMA')

    def test_duplicate_json_keys(self):
        with self.assertRaisesRegex(G.Hold, 'DUPLICATE_JSON_KEY'):
            json.loads('{"a":1,"a":2}', object_pairs_hook=G.unique_keys)

    def test_actual_candidate_metadata_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for part in self.p:
                for row in part['articles']:
                    path = root/'preparedness/content/articles'/(row['slug']+'.meta.json')
                    path.parent.mkdir(parents=True, exist_ok=True)
                    raw = json.dumps({'status': {'publish': 'draft'},
                                      'safety_review': {'state': 'pending'},
                                      'source_use': {record['source_id']: record['source_use_scope']
                                                     for record in row['shared_source_bindings']}}).encode()
                    path.write_bytes(raw)
                    row['metadata_blob_sha'] = G.git_blob(raw)
                    row['total_declared_source_uses'] = len(row['shared_source_bindings'])
            self.assertEqual(G.audit(self.c, self.t, self.p, candidate_root=root)['article_count'], 35)
            first = root/'preparedness/content/articles/article-00.meta.json'
            first.write_bytes(first.read_bytes()+b' ')
            with self.assertRaisesRegex(G.Hold, 'CANDIDATE_METADATA_CHANGED'):
                G.audit(self.c, self.t, self.p, candidate_root=root)


def blank_scope_for_article(index):
    def run(self):
        which = 0 if index < 12 else 1 if index < 24 else 2
        at = index if which == 0 else index-12 if which == 1 else index-24
        self.p[which]['articles'][at]['shared_source_bindings'][0]['source_use_scope'] = ''
        self.rejects('BLANK_SOURCE_SCOPE')
    return run


def group_status_mutant(index):
    def run(self):
        self.c['groups'][index]['review_status'] = 'independent_QD_PASS'
        self.rejects('PREMATURE_SOURCE_REVIEW')
    return run


for n in range(35):
    setattr(Synthetic, 'test_article_%02d_rejects_blank_claim_scope' % n, blank_scope_for_article(n))
for n in range(32):
    setattr(Synthetic, 'test_group_%02d_rejects_unreviewed_upgrade' % n, group_status_mutant(n))


if __name__ == '__main__':
    unittest.main()
