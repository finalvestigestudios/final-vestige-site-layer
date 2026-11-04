"""Synthetic R116 tests: no real advice, customer records, or CMS mutation."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / 'tools/r116_frozen_metadata_and_roster_gate.py'
spec = importlib.util.spec_from_file_location('r116_gate', PATH)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def fixture():
    r115 = {
        'schema': g.R115_SCHEMA, 'reference_commit': 'a' * 40,
        'release_state': 'HOLD', 'may_publish': False,
        'rows_NOT_APPROVED': [],
        'self_reported_safety_metadata_counts': {'pending': 29, 'approved': 2, 'not-required': 4},
        'article_scoped_source_id_total_NOT_GLOBAL_UNIQUE': 35,
    }
    m = {'schema': g.SCHEMA, 'reference_commit': 'a' * 40,
         'release_state': 'HOLD', 'may_publish': False,
         'independent_QD_PASS': False, 'medical_safety_verified': False,
         'metadata_count': 35, 'original_article_body_count': 35,
         'metadata_rows_NOT_APPROVED': []}
    raw = {}
    for n in range(1, 36):
        slug = f'article-{n:02}'
        safety = 'pending' if n <= 29 else ('approved' if n <= 31 else 'not-required')
        data = {'slug': slug, 'section': 'start-here', 'track': 'modern',
                'status': {'publish': 'draft', 'editorial': 'drafted'},
                'safety_review': {'state': safety, 'reviewer': 'not independently checked'},
                'source_use': {f'src-{n:02}': 'Synthetic source reading limited to a test fixture.'},
                'description': 'Clearly synthetic fixture; no emergency guidance.'}
        bs = json.dumps(data, sort_keys=True).encode()
        raw[slug] = bs
        m['metadata_rows_NOT_APPROVED'].append({
            'n': n, 'slug': slug, 'metadata_git_blob_oid': g.git_blob(bs)})
        r115['rows_NOT_APPROVED'].append({'n': n, 'slug': slug,
                                         'section': 'start-here', 'track': 'modern',
                                         'distinct_author_scoped_source_ids': 1})
    return m, r115, raw, set(raw)


class ValidBaseline(unittest.TestCase):
    def test_full_35_synthetic_inventory_is_held(self):
        x = g.audit(*fixture())
        self.assertEqual(x['original_metadata_git_blobs_verified'], 35)
        self.assertEqual(x['paired_article_bodies_in_inventory'], 35)
        self.assertFalse(x['may_publish'])
        self.assertFalse(x['independent_QD_PASS'])
        self.assertFalse(x['medical_safety_verified'])
        self.assertFalse(x['merchant_offer_verified'])
        self.assertEqual(x['release_state'], 'HOLD')

    def test_sha_matches_canonical_git_blob(self):
        self.assertEqual(g.git_blob(b'test content'),
                         '08cf6101416f0ce0dda3c80e627f333854c4085c')

    def test_json_decode_rejects_duplicate_security_keys(self):
        with self.assertRaisesRegex(g.IntegrityHold, 'DUPLICATE_JSON_KEY'):
            g.strict_json(b'{"publish":"draft","publish":"published"}')


def make_changed_metadata_test(n):
    def body(self):
        m, old, raw, bodies = fixture()
        slug = f'article-{n:02}'
        obj = json.loads(raw[slug]); obj['source_use'][f'src-{n:02}'] = 'An altered interpretation.'
        raw[slug] = json.dumps(obj, sort_keys=True).encode()
        with self.assertRaisesRegex(g.IntegrityHold, 'ORIGINAL_METADATA_CHANGED_REVIEW_REQUIRED_'+slug):
            g.audit(m, old, raw, bodies)
    return body


for _n in range(1, 36):
    setattr(ValidBaseline, f'test_author_scope_changed_article_{_n:02}', make_changed_metadata_test(_n))


class MutationGates(unittest.TestCase):
    def check_failure(self, edit, msg):
        m, old, raw, bodies = fixture()
        edit(m, old, raw, bodies)
        with self.assertRaisesRegex(g.IntegrityHold, msg):
            g.audit(m, old, raw, bodies)

    def test_replaced_malicious_publish_state_held(self):
        def change(m, old, raw, bodies):
            o = json.loads(raw['article-01']); o['status']['publish'] = 'published'
            raw['article-01'] = json.dumps(o).encode()
        self.check_failure(change, 'ORIGINAL_METADATA_CHANGED')

    def test_metadata_safety_swap_preserving_aggregate_counts_still_held(self):
        def change(m, old, raw, bodies):
            a, b = json.loads(raw['article-01']), json.loads(raw['article-30'])
            a['safety_review'], b['safety_review'] = b['safety_review'], a['safety_review']
            raw['article-01'] = json.dumps(a).encode()
            raw['article-30'] = json.dumps(b).encode()
        self.check_failure(change, 'ORIGINAL_METADATA_CHANGED')

    def test_article_removed(self):
        self.check_failure(lambda m,o,r,b: r.pop('article-01'), 'EXTRA_MISSING_OR_ORPHAN')

    def test_article_added(self):
        self.check_failure(lambda m,o,r,b: r.update({'intruder': b'{}'}), 'EXTRA_MISSING_OR_ORPHAN')

    def test_extra_body(self):
        self.check_failure(lambda m,o,r,b: b.add('intruder'), 'EXTRA_MISSING_OR_ORPHAN')

    def test_missing_body(self):
        self.check_failure(lambda m,o,r,b: b.remove('article-01'), 'EXTRA_MISSING_OR_ORPHAN')

    def test_wrong_r115_reference(self):
        self.check_failure(lambda m,o,r,b: o.update({'reference_commit': 'b'*40}), 'FROZEN_REFERENCE_COMMIT_MISMATCH')

    def test_invalid_reference(self):
        self.check_failure(lambda m,o,r,b: m.update({'reference_commit': 'bad'}), 'FROZEN_REFERENCE_COMMIT_MISMATCH')

    def test_r115_approves_publish(self):
        self.check_failure(lambda m,o,r,b: o.update({'may_publish': True}), 'R115_EVIDENCE_NOT_HELD')

    def test_r116_approves_publish(self):
        self.check_failure(lambda m,o,r,b: m.update({'may_publish': True}), 'INVALID_MANIFEST_GOVERNANCE')

    def test_r116_claims_qd_pass(self):
        self.check_failure(lambda m,o,r,b: m.update({'independent_QD_PASS': True}), 'INVALID_MANIFEST_GOVERNANCE')

    def test_r116_claims_medical_safety(self):
        self.check_failure(lambda m,o,r,b: m.update({'medical_safety_verified': True}), 'INVALID_MANIFEST_GOVERNANCE')

    def test_bad_r116_schema(self):
        self.check_failure(lambda m,o,r,b: m.update({'schema': 'not-your-safety-approval'}), 'UNKNOWN_FROZEN_METADATA_MANIFEST')

    def test_bad_r115_schema(self):
        self.check_failure(lambda m,o,r,b: o.update({'schema': 'wrong'}), 'R115_EVIDENCE_NOT_HELD')

    def test_missing_frozen_row(self):
        self.check_failure(lambda m,o,r,b: m['metadata_rows_NOT_APPROVED'].pop(), 'INCOMPLETE_35_ARTICLE_CENSUS')

    def test_missing_r115_row(self):
        self.check_failure(lambda m,o,r,b: o['rows_NOT_APPROVED'].pop(), 'INCOMPLETE_35_ARTICLE_CENSUS')

    def test_doubled_slug(self):
        self.check_failure(lambda m,o,r,b: m['metadata_rows_NOT_APPROVED'][1].update({'slug':'article-01'}), 'DUPLICATE_OR_UNSAFE_SLUG')

    def test_path_traversal_slug(self):
        self.check_failure(lambda m,o,r,b: m['metadata_rows_NOT_APPROVED'][1].update({'slug':'../evil'}), 'DUPLICATE_OR_UNSAFE_SLUG')

    def test_reversed_reading_order(self):
        self.check_failure(lambda m,o,r,b: m['metadata_rows_NOT_APPROVED'].reverse(), 'FROZEN_READING_ORDER_CHANGED')

    def test_wrong_article_number(self):
        self.check_failure(lambda m,o,r,b: m['metadata_rows_NOT_APPROVED'][5].update({'n':999}), 'FROZEN_READING_ORDER_CHANGED')

    def test_wrong_metadata_oid(self):
        self.check_failure(lambda m,o,r,b: m['metadata_rows_NOT_APPROVED'][0].update({'metadata_git_blob_oid':'b'*40}), 'ORIGINAL_METADATA_CHANGED')

    def test_non_hex_metadata_oid(self):
        self.check_failure(lambda m,o,r,b: m['metadata_rows_NOT_APPROVED'][0].update({'metadata_git_blob_oid':'z'*40}), 'INVALID_FROZEN_METADATA_BLOB')

    def test_wrong_summary_total(self):
        self.check_failure(lambda m,o,r,b: o.update({'article_scoped_source_id_total_NOT_GLOBAL_UNIQUE':34}), 'AUTHOR_SOURCE_USE_TOTAL_DRIFT')

    def test_invalid_status_counts(self):
        self.check_failure(lambda m,o,r,b: o.update({'self_reported_safety_metadata_counts':{'pending':35}}), 'SAFETY_STATE_CENSUS_DRIFT')

    def test_nonbytes_metadata(self):
        self.check_failure(lambda m,o,r,b: r.update({'article-01':'notbytes'}), 'INPUT_NOT_BYTES')

    def test_census_mismatch(self):
        self.check_failure(lambda m,o,r,b: m.update({'original_article_body_count':34}), 'INCOMPLETE_35_ARTICLE_CENSUS')


class DirectoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='fvs-r116-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.prep = self.root / 'preparedness'
        folder = self.prep / 'content/articles'
        folder.mkdir(parents=True)
        (self.prep/'docs').mkdir()
        m, old, raw, bodies = fixture()
        (self.prep/'docs/R116_FROZEN_35_METADATA_BLOB_CENSUS.json').write_text(json.dumps(m))
        (self.prep/'docs/R115_FROZEN_ALL_35_AUTHOR_BODY_CENSUS.json').write_text(json.dumps(old))
        for slug, contents in raw.items():
            (folder/(slug+'.meta.json')).write_bytes(contents)
            (folder/(slug+'.body.html')).write_text('Synthetic placeholder: not advice.')
        self.folder = folder

    def test_audit_original_files(self):
        self.assertEqual(g.audit_checkout(self.root)['original_metadata_git_blobs_verified'],35)

    def test_extra_metadata_file_is_rejected(self):
        (self.folder/'unapproved.meta.json').write_text('{}')
        with self.assertRaisesRegex(g.IntegrityHold, 'EXTRA_MISSING_OR_ORPHAN'):
            g.audit_checkout(self.root)

    def test_extra_body_file_is_rejected(self):
        (self.folder/'unapproved.body.html').write_text('Unauthorized draft.')
        with self.assertRaisesRegex(g.IntegrityHold, 'EXTRA_MISSING_OR_ORPHAN'):
            g.audit_checkout(self.root)

    def test_missing_metadata_file_is_rejected(self):
        (self.folder/'article-05.meta.json').unlink()
        with self.assertRaisesRegex(g.IntegrityHold, 'EXTRA_MISSING_OR_ORPHAN'):
            g.audit_checkout(self.root)

    def test_missing_body_file_is_rejected(self):
        (self.folder/'article-05.body.html').unlink()
        with self.assertRaisesRegex(g.IntegrityHold, 'EXTRA_MISSING_OR_ORPHAN'):
            g.audit_checkout(self.root)

    def test_source_use_text_change_is_rejected(self):
        path = self.folder/'article-02.meta.json'
        path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(g.IntegrityHold, 'ORIGINAL_METADATA_CHANGED'):
            g.audit_checkout(self.root)

    def test_symlink_file_is_rejected(self):
        real = self.folder/'article-03.meta.json'
        real.unlink()
        real.symlink_to(self.folder/'article-04.meta.json')
        with self.assertRaisesRegex(g.IntegrityHold, 'UNSAFE_ARTICLE_FILE_ENTRY'):
            g.audit_checkout(self.root)


if __name__ == '__main__':
    unittest.main()
