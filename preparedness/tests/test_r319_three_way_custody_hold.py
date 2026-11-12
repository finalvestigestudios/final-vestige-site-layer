"""R319 invariant regression suite — deliberate synthetic fixtures, no source edits."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from preparedness.tools import r319_three_way_custody_hold as gate

SLUGS_A = [f'article-{i:02d}' for i in range(35)]
SLUGS_T = [f'tool-{i:02d}' for i in range(6)]


def fixture():
    records = []
    for family, slugs in (('articles', SLUGS_A), ('tools', SLUGS_T)):
        for slug in slugs:
            for ext in ('body.html', 'meta.json'):
                path = f'preparedness/content/{family}/{slug}.{ext}'
                data = path.encode()
                entry = {'sha': gate.blob(data), 'size': len(data)}
                records.append({'path': path, 'integrated': entry, 'continuation': None,
                                'followup': None, 'disposition': 'INTEGRATED_ONLY'})
    # First 15 become authentic conflicts (6 bodies + 9 metadata), next 13 exact.
    bodies = [r for r in records if r['path'].endswith('.body.html')]
    metas = [r for r in records if r['path'].endswith('.meta.json')]
    changed = bodies[:6] + metas[:9]
    equal = [r for r in records if r not in changed][:13]
    for r in changed:
        r['followup'] = {'sha': gate.blob(b'changed:' + r['path'].encode()), 'size': 999}
        r['continuation'] = r['integrated'].copy()
        r['disposition'] = 'HUMAN_REVIEW_REQUIRED'
    for r in equal:
        r['followup'] = r['integrated'].copy()
        r['continuation'] = r['integrated'].copy()
        r['disposition'] = 'IDENTICAL'
    return {'schema': gate.SCHEMA, 'baseline': copy.deepcopy(gate.BASELINE),
            'branches': copy.deepcopy(gate.BRANCHES), 'expected': copy.deepcopy(gate.EXPECTED),
            'release': {'publication_authorized': False, 'qualified_safety_approved': False,
                        'independent_qd_pass': False, 'paid_conversion_verified': False},
            'records': records}


def write_fixture(root, manifest):
    for r in manifest['records']:
        p = root / r['path']; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r['path'].encode())


class Invariants(unittest.TestCase):
    def setUp(self):
        self.data = fixture()
    def errors(self):
        return gate.validate_manifest(self.data)['errors']
    def test_draft_hard_hold_only(self):
        r = gate.validate_manifest(self.data)
        self.assertEqual(r['state'], 'DRAFT_HARD_HOLD')
        self.assertEqual(r['review_required_count'], 15)
        self.assertFalse(r['publishing_authorized'])
    def test_missing_manifest(self):
        self.assertEqual(gate.validate_manifest(None)['state'], 'INVALID_HARD_HOLD')
    def test_schema_drift(self):
        self.data['schema'] = 'wrong'; self.assertIn('SCHEMA_MISMATCH', self.errors())
    def test_baseline_drift(self):
        self.data['baseline']['sha'] = 'a'*40; self.assertIn('BASELINE_SHA_OR_REF_DRIFT', self.errors())
    def test_contributor_drift(self):
        self.data['branches']['followup']['sha'] = 'b'*40; self.assertIn('CONTRIBUTOR_SHA_OR_REF_DRIFT', self.errors())
    def test_expected_drift(self):
        self.data['expected']['total_records'] = 40; self.assertIn('EXPECTED_SOURCE_COUNTS_DRIFT', self.errors())
    def test_fake_release_approval(self):
        self.data['release']['independent_qd_pass'] = True; self.assertIn('INVALID_RELEASE_HOLD', self.errors())
    def test_fake_sale(self):
        self.data['release']['paid_conversion_verified'] = True; self.assertIn('INVALID_RELEASE_HOLD', self.errors())
    def test_duplicate_file(self):
        self.data['records'].append(copy.deepcopy(self.data['records'][0])); self.assertTrue(any('DUPLICATE_SOURCE_PATH' in e for e in self.errors()))
    def test_path_escape(self):
        self.data['records'][0]['path'] = 'preparedness/content/articles/../../secrets'; self.assertTrue(any('INVALID_SOURCE_PATH' in e for e in self.errors()))
    def test_bad_git_sha(self):
        self.data['records'][0]['integrated']['sha'] = 'xyz'; self.assertTrue(any('INVALID_INTEGRATED_BLOB' in e for e in self.errors()))
    def test_boolean_size_invalid(self):
        self.data['records'][0]['integrated']['size'] = True; self.assertTrue(any('INVALID_INTEGRATED_BLOB' in e for e in self.errors()))
    def test_bad_contributor_sha(self):
        self.data['records'][0]['followup'] = {'sha': 'g'*40, 'size': 5}; self.assertTrue(any('INVALID_CONTRIBUTOR_BLOB' in e for e in self.errors()))
    def test_false_identical(self):
        self.data['records'][0]['disposition'] = 'IDENTICAL'; self.assertTrue(any('MISCLASSIFIED_CONFLICT' in e for e in self.errors()))
    def test_suppress_review(self):
        r = next(x for x in self.data['records'] if x['disposition'] == 'HUMAN_REVIEW_REQUIRED')
        r['disposition'] = 'IDENTICAL'; self.assertTrue(any('MISCLASSIFIED_CONFLICT' in e for e in self.errors()))
    def test_delete_body(self):
        self.data['records'] = [r for r in self.data['records'] if not r['path'].endswith('article-00.body.html')]
        self.assertTrue(any('MISSING_BODY_OR_METADATA_PAIR' in e for e in self.errors()))
    def test_unexpected_shape(self):
        self.data['records'][0]['approved'] = True; self.assertTrue(any('INVALID_RECORD_SHAPE' in e for e in self.errors()))
    def test_bad_record_container(self):
        self.data['records'] = None; self.assertIn('MISSING_SOURCE_RECORDS', self.errors())
    def test_source_no_links(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); write_fixture(root, self.data)
            p = root / self.data['records'][0]['path']; p.unlink()
            p.symlink_to(root / self.data['records'][1]['path'])
            self.assertTrue(any('MISSING_OR_LINKED_INTEGRATED_SOURCE' in e for e in gate.validate_manifest(self.data, root)['errors']))
    def test_extra_authored_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); write_fixture(root, self.data)
            (root/'preparedness/content/articles/rogue.body.html').write_text('x')
            self.assertTrue(any('UNREVIEWED_ADDED_OR_REMOVED_SOURCE' in e for e in gate.validate_manifest(self.data, root)['errors']))
    def test_complete_synthetic_tree_still_hold(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); write_fixture(root, self.data)
            r = gate.validate_manifest(self.data, root)
            self.assertEqual(r['errors'], [])
            self.assertEqual(r['state'], 'DRAFT_HARD_HOLD')
            self.assertFalse(r['source_safety_qd_approved'])


def _make_mutation_test(index):
    def test(self):
        data = fixture()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); write_fixture(root, data)
            rec = data['records'][index]
            (root / rec['path']).write_bytes(b'tampered')
            result = gate.validate_manifest(data, root)
            self.assertEqual(result['state'], 'INVALID_HARD_HOLD')
            self.assertIn('SOURCE_CONTENT_CHANGED_REQUIRES_NEW_REVIEW:' + rec['path'], result['errors'])
    return test

for i in range(82):
    setattr(Invariants, f'test_byte_mutation_{i:02d}', _make_mutation_test(i))

if __name__ == '__main__': unittest.main()
