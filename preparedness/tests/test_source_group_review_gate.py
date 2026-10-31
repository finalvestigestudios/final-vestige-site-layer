"""Synthetic/provenance tests only; no source claim/safety approvals."""
import copy
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

SRC = Path(__file__).resolve().parents[1] / 'tools/source_group_review_gate.py'
spec = importlib.util.spec_from_file_location('source_group_review_gate', SRC)
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)


def fixture():
    # 224 entries, 186 URLs, 30 duplicated URLs (22 pairs and 8 triples),
    # with 15 duplicated IDs. All 8 source inventories are represented.
    records = []
    for i in range(156):
        records.append((f'https://example.org/single/{i:03d}', f'id-single-{i}'))
    for i in range(30):
        for j in range(2 if i < 22 else 3):
            sid = f'id-shared-{i}' if i < 15 else f'id-{i}-{j}'
            records.append((f'https://example.org/shared/{i:02d}', sid))
    assert len(records) == 224
    sources = {origin: [] for origin in gate.SOURCE_FILES}
    for i, (url, sid) in enumerate(records):
        origin = list(gate.SOURCE_FILES)[i % 8]
        sources[origin].append({'id': sid, 'url': url, 'title': f'Title {i}',
                                'supports': f'Reading scope {i}', 'notes': f'Note {i}',
                                'human_link_check': False})
    crosswalk = {'schema_version': 1,
                 'status': 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
                 'raw_source_rows': 224, 'unique_source_urls': 186,
                 'duplicate_url_groups': 30, 'duplicate_id_groups': 15,
                 'source_files': [], 'groups': [],
                 'source_head_commits': {n: '1'*40 for n in gate.SOURCE_FILES}}
    crosswalk['source_head_commits']['food'] = gate.FIXTURE_FOOD
    source_bytes = {}
    indexed = defaultdict(list)
    for origin, items in sources.items():
        path = gate.SOURCE_FILES[origin]
        raw = gate.canonical({'sources': items})
        source_bytes[path] = raw
        crosswalk['source_files'].append({'origin': origin, 'path': path,
                                          'git_blob_sha': gate.git_blob(raw), 'count': len(items)})
        for idx, item in enumerate(items):
            indexed[item['url']].append({'origin': origin, 'source_file': path,
                                         'row_index': idx, 'source': item})
    for url, variants in indexed.items():
        if len(variants) > 1:
            crosswalk['groups'].append({'url': url, 'canonical_url': url,
                'review_status': 'pending-human-source-and-reading-scope-review',
                'reviewer': None, 'reviewed_on': None,
                'variants': copy.deepcopy(variants),
                'identities': [{'origin': v['origin'], 'id': v['source']['id'],
                                'row_index': v['row_index']} for v in variants]})
    slugs = [f'article-{i:02d}' for i in range(35)]
    crosswalk['article_origins'] = {s: 'base' for s in slugs}
    crosswalk['article_origins']['water-planner'] = 'start'
    taxonomy = {'base_path': '/preparedness/', 'slate': [{'slug': s} for s in slugs],
                'tools': [{'slug': 'water-planner', 'gate': True}]}
    return crosswalk, taxonomy, source_bytes


class Happy(unittest.TestCase):
    def setUp(self):
        self.c, self.t, self.files = fixture()

    def test_review_queue_exact_counts(self):
        result = gate.audit(self.c, self.t, self.files)
        self.assertEqual((result['source_rows'], result['distinct_urls'],
                          result['shared_url_review_groups'], result['duplicate_id_groups']),
                         (224, 186, 30, 15))
        self.assertEqual(len(result['review_queue']), 30)
        self.assertEqual(result['article_slugs'], 35)
        self.assertEqual(result['release_state'], 'HOLD')
        self.assertIs(result['may_publish'], False)
        self.assertIs(result['medical_safety_approved'], False)
        self.assertIs(result['independent_qd_pass'], False)
        self.assertTrue(result['known_food_provenance_exception'])

    def test_queue_deterministic_independent_of_file_order(self):
        expected = gate.audit(self.c, self.t, self.files)
        self.c['source_files'].reverse()
        self.c['groups'].reverse()
        self.assertEqual(gate.audit(self.c, self.t, self.files), expected)

    def test_correct_food_author_provenance_accepted_without_approval(self):
        self.c['source_head_commits']['food'] = gate.AUTHOR_FOOD
        result = gate.audit(self.c, self.t, self.files)
        self.assertFalse(result['known_food_provenance_exception'])
        self.assertFalse(result['may_publish'])

    def test_digest_of_queue_receipt(self):
        receipt = gate.audit(self.c, self.t, self.files)
        digest = receipt.pop('sha256')
        self.assertEqual(hashlib.sha256(gate.canonical(receipt)).hexdigest(), digest)


class Mutations(unittest.TestCase):
    def setUp(self):
        self.c, self.t, self.files = fixture()

    def hold(self):
        with self.assertRaises((gate.SourceGateHold, KeyError, TypeError)):
            gate.audit(self.c, self.t, self.files)


def make_case(name, mutate):
    def test(self):
        mutate(self.c, self.t, self.files)
        self.hold()
    test.__name__ = 'test_'+name
    setattr(Mutations, test.__name__, test)


CASES = {
 'wrong_schema': lambda c,t,f: c.update(schema_version=2),
 'missing_schema': lambda c,t,f: c.pop('schema_version'),
 'false_review_state': lambda c,t,f: c.update(status='HUMAN_APPROVED'),
 'different_status': lambda c,t,f: c.update(status='IN_PROGRESS'),
 'wrong_base_path': lambda c,t,f: t.update(base_path='/other/'),
 'slate_34': lambda c,t,f: t['slate'].pop(),
 'slate_36': lambda c,t,f: t['slate'].append({'slug':'extra'}),
 'duplicate_slug': lambda c,t,f: t['slate'][1].update(slug='article-00'),
 'slash_slug': lambda c,t,f: t['slate'][0].update(slug='x/other'),
 'empty_slug': lambda c,t,f: t['slate'][0].update(slug=''),
 'missing_origin': lambda c,t,f: c['article_origins'].pop('article-00'),
 'extra_origin': lambda c,t,f: c['article_origins'].update({'wrong':'base'}),
 'bad_origin': lambda c,t,f: c['article_origins'].update({'article-00':'unknown'}),
 'missing_tool': lambda c,t,f: t.update(tools=[]),
 'unsafe_tool_gate': lambda c,t,f: t['tools'][0].update(gate=False),
 'missing_source_file': lambda c,t,f: f.pop(next(iter(f))),
 'extra_source_file': lambda c,t,f: f.update({'unexpected.json':b'{}'}),
 'source_count_7': lambda c,t,f: c['source_files'].pop(),
 'duplicate_source_file': lambda c,t,f: c['source_files'][1].update(origin='base'),
 'wrong_source_path': lambda c,t,f: c['source_files'][0].update(path='sources/other.json'),
 'unknown_origin': lambda c,t,f: c['source_files'][0].update(origin='new'),
 'source_blob_drift': lambda c,t,f: f.update({next(iter(f)):b'{"sources":[]}'}),
 'wrong_git_sha': lambda c,t,f: c['source_files'][0].update(git_blob_sha='f'*40),
 'wrong_source_count': lambda c,t,f: c['source_files'][0].update(count=1),
 'bad_food_sha': lambda c,t,f: c['source_head_commits'].update(food='0'*40),
 'missing_food_head': lambda c,t,f: c['source_head_commits'].pop('food'),
 'missing_head': lambda c,t,f: c['source_head_commits'].pop('start'),
 'raw_count_claim': lambda c,t,f: c.update(raw_source_rows=223),
 'url_count_claim': lambda c,t,f: c.update(unique_source_urls=185),
 'group_count_claim': lambda c,t,f: c.update(duplicate_url_groups=29),
 'id_count_claim': lambda c,t,f: c.update(duplicate_id_groups=14),
 'drop_group': lambda c,t,f: c['groups'].pop(),
 'duplicate_group': lambda c,t,f: c['groups'][1].update(url=c['groups'][0]['url']),
 'change_group_url': lambda c,t,f: c['groups'][0].update(url='https://example.org/unknown'),
 'change_canonical_url': lambda c,t,f: c['groups'][0].update(canonical_url='https://wrong.test/'),
 'fake_human_review': lambda c,t,f: c['groups'][0].update(review_status='reviewed'),
 'fake_human_reviewer': lambda c,t,f: c['groups'][0].update(reviewer='Dr. Nobody'),
 'fake_human_date': lambda c,t,f: c['groups'][0].update(reviewed_on='2026-10-31'),
 'missing_variant': lambda c,t,f: c['groups'][0]['variants'].pop(),
 'alter_source_note': lambda c,t,f: c['groups'][0]['variants'][0]['source'].update(notes='edited'),
 'alter_reading_scope': lambda c,t,f: c['groups'][0]['variants'][0]['source'].update(supports='all pages verified'),
 'alter_source_url': lambda c,t,f: c['groups'][0]['variants'][0]['source'].update(url='https://other.test/'),
 'alter_variant_id': lambda c,t,f: c['groups'][0]['variants'][0]['source'].update(id='someone-else'),
 'alter_variant_path': lambda c,t,f: c['groups'][0]['variants'][0].update(source_file='other.json'),
 'alter_variant_index': lambda c,t,f: c['groups'][0]['variants'][0].update(row_index=999),
 'alter_group_identity': lambda c,t,f: c['groups'][0]['identities'][0].update(id='wrong'),
 'remove_identity': lambda c,t,f: c['groups'][0]['identities'].pop(),
 'extra_identity': lambda c,t,f: c['groups'][0]['identities'].append(copy.deepcopy(c['groups'][0]['identities'][0])),
}
for key, mutation in CASES.items():
    make_case(key, mutation)


if __name__ == '__main__':
    unittest.main()
