"""Isolated synthetic/adversarial source-custody tests. Never writes the shared tree."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'r124_source_crosswalk_integrity.py'
SPEC = importlib.util.spec_from_file_location('r124_gate', TOOL)
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)


def prepare(tmp):
    root = Path(tmp)
    folder = root / 'preparedness' / 'sources'
    folder.mkdir(parents=True)
    registers = {origin: [] for origin in G.FILES}
    for idx in range(32):
        origin1 = 'base' if idx < 16 else 'health'
        origin2 = 'food' if idx < 16 else 'shelter'
        for origin in (origin1, origin2):
            registers[origin].append({'id': f'source-{origin}-{idx:02d}',
                 'url': f'https://example.org/source/{idx:02d}',
                 'supports': 'Distinct interpretation ' + origin, 'verified_on': '2026-11-04'})
    for idx, origin in enumerate(('base', 'start', 'hist-field')):
        registers[origin].append({'id': f'unique-{origin}',
                                 'url': f'https://unique.example.org/{idx}',
                                 'supports': 'Unique source'})
    source_files = []
    by_url = {}
    for origin, suffix in G.FILES.items():
        path = folder / suffix
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps({'sources': registers[origin]}, indent=2).encode()
        path.write_bytes(raw)
        source_files.append({'origin': origin, 'path': 'preparedness/sources/' + suffix,
                             'git_blob_sha': G.blob_sha(raw), 'count': len(registers[origin])})
        for i, source in enumerate(registers[origin]):
            by_url.setdefault(G.key_url(source['url']), []).append(
                {'origin': origin, 'source_file': 'preparedness/sources/' + suffix,
                 'row_index': i, 'source': copy.deepcopy(source)})
    groups = []
    for url, rows in sorted(by_url.items()):
        if len(rows) < 2:
            continue
        groups.append({'url': url, 'canonical_url': url,
                       'review_status': G.PENDING, 'reviewer': None, 'reviewed_on': None,
                       'variants': rows,
                       'identities': [{'origin': v['origin'], 'id': v['source']['id'],
                                      'row_index': v['row_index']} for v in rows]})
    crosswalk = {'status': 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
                 'historical_crosswalk_census_20261030':
                    {'duplicate_url_groups': 30, 'raw_source_rows': 224},
                 'source_files': source_files, 'groups': groups,
                 'raw_source_rows': 67, 'unique_source_urls': 35,
                 'duplicate_url_groups': 32, 'duplicate_id_groups': 0,
                 'candidate_reconciliation_20261104': {
                    'status': G.HOLD, 'candidate_commit': G.CANDIDATE,
                    'issue': 136, 'business_issue': 820, 'business_charter': 818,
                    'candidate_source_rows': 67, 'candidate_distinct_urls': 35,
                    'candidate_shared_url_groups': 32,
                    **{f: False for f in ('independent_QD_PASS','safety_approved',
                      'medical_safety_verified','may_publish','may_merge',
                      'merchant_offer_verified')}}}
    (folder / 'crosswalk.json').write_text(json.dumps(crosswalk, indent=2), encoding='utf-8')
    return root, crosswalk


class SyntheticReview(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root, self.x = prepare(self.workspace.name)

    def save(self):
        (self.root/'preparedness/sources/crosswalk.json').write_text(
            json.dumps(self.x, indent=2), encoding='utf-8')

    def add_alias(self):
        """Add a third origin with a distinct literal URL and author reading scope.

        This extends the *same* canonical group, but does not change any of the
        32 exact-URL groups, source records, or human-review decisions.
        """
        source = copy.deepcopy(self.x['groups'][0]['variants'][0]['source'])
        source['id'] = 'hist-food-separate-reading'
        source['url'] += '/'
        source['supports'] = 'Distinct author reading scope, not a merged claim.'
        path = self.root/'preparedness/sources/fragments/hist-food.json'
        fragment = json.loads(path.read_text(encoding='utf-8'))
        i = len(fragment['sources'])
        fragment['sources'].append(source)
        raw = json.dumps(fragment, indent=2).encode()
        path.write_bytes(raw)
        source_file = next(f for f in self.x['source_files'] if f['origin'] == 'hist-food')
        source_file['git_blob_sha'] = G.blob_sha(raw)
        source_file['count'] += 1
        self.x['raw_source_rows'] += 1
        self.x['unique_source_urls'] += 1
        self.x['candidate_reconciliation_20261104']['candidate_source_rows'] += 1
        self.x['candidate_reconciliation_20261104']['candidate_distinct_urls'] += 1
        variant = {'origin':'hist-food',
                   'source_file':'preparedness/sources/fragments/hist-food.json',
                   'row_index':i, 'source':source}
        self.x['groups'][0]['variants'].append(variant)
        self.x['groups'][0]['identities'].append(
            {'origin':'hist-food','id':source['id'],'row_index':i})
        return variant

    def assert_hold(self, code):
        self.save()
        with self.assertRaisesRegex(G.IntegrityHold, code):
            G.audit(self.root)

    def test_valid_synthetic_is_only_hold(self):
        result = G.audit(self.root)
        self.assertEqual(result['release_state'], 'HOLD')
        self.assertEqual(result['unreviewed_groups'], 32)
        self.assertFalse(result['QD_PASS'])
        self.assertFalse(result['may_publish'])
        self.assertFalse(result['medical_safety_verified'])

    def test_deterministic(self):
        self.assertEqual(G.audit(self.root), G.audit(self.root))

    def test_missing_group(self):
        self.x['groups'].pop()
        self.assert_hold('MISSING_OR_EXTRA_SHARED_URL_GROUP')

    def test_extra_group(self):
        self.x['groups'].append(copy.deepcopy(self.x['groups'][0]))
        self.assert_hold('DUPLICATE_SHARED_URL_GROUP')

    def test_duplicate_url_group(self):
        self.x['groups'][1]['url'] = self.x['groups'][0]['url']
        self.assert_hold('DUPLICATE_SHARED_URL_GROUP')

    def test_approved_group_rejected(self):
        self.x['groups'][0]['review_status'] = 'approved'
        self.assert_hold('PREMATURE_SOURCE_APPROVAL')

    def test_forged_reviewer_rejected(self):
        self.x['groups'][0]['reviewer'] = 'not-a-real-review'
        self.assert_hold('PREMATURE_SOURCE_APPROVAL')

    def test_canonical_url_tamper(self):
        self.x['groups'][0]['canonical_url'] = 'https://other.example.org/'
        self.assert_hold('CANONICAL_URL_DRIFT')

    def test_candidate_commit_drift(self):
        self.x['candidate_reconciliation_20261104']['candidate_commit'] = 'f'*40
        self.assert_hold('CANDIDATE_COMMIT_DRIFT')

    def test_wrong_business_issue(self):
        self.x['candidate_reconciliation_20261104']['business_issue'] = 819
        self.assert_hold('ISSUE_SCOPE_DRIFT')

    def test_unapproved_merchant_flag(self):
        self.x['candidate_reconciliation_20261104']['merchant_offer_verified'] = True
        self.assert_hold('UNAUTHORIZED_APPROVAL')

    def test_unapproved_qd_flag(self):
        self.x['candidate_reconciliation_20261104']['independent_QD_PASS'] = True
        self.assert_hold('UNAUTHORIZED_APPROVAL')

    def test_historical_record_tamper(self):
        self.x['historical_crosswalk_census_20261030']['raw_source_rows'] = 0
        self.assert_hold('HISTORICAL_EVIDENCE_LOST')

    def test_duplicate_variant_identity(self):
        self.x['groups'][0]['variants'][1] = copy.deepcopy(self.x['groups'][0]['variants'][0])
        self.assert_hold('SOURCE_VARIANT_ROSTER_DRIFT')

    def test_removed_variant(self):
        self.x['groups'][0]['variants'].pop()
        self.assert_hold('SOURCE_VARIANT_ROSTER_DRIFT')

    def test_retarget_variant_url(self):
        self.x['groups'][0]['variants'][0]['source']['url'] = 'https://other.org/'
        self.assert_hold('SOURCE_VARIANT_CONTENT_DRIFT')

    def test_stale_source_scope(self):
        self.x['groups'][0]['variants'][0]['source']['supports'] = 'Omitted author reading scope'
        self.assert_hold('SOURCE_VARIANT_CONTENT_DRIFT')

    def test_identity_roster_missing(self):
        self.x['groups'][0]['identities'].pop()
        self.assert_hold('SOURCE_IDENTITY_ROSTER_DRIFT')

    def test_changed_fragment_blob(self):
        p = self.root/'preparedness/sources/fragments/food.json'
        p.write_text(p.read_text()+'\n')
        self.assert_hold('SOURCE_FILE_BLOB_OR_ROW_DRIFT')

    def test_https_required(self):
        for url in ('javascript:alert(1)', 'http://example.org/a', 'ftp://example.org/a'):
            with self.subTest(url=url), self.assertRaises(G.IntegrityHold):
                G.key_url(url)

    def test_path_case_preserved(self):
        self.assertNotEqual(G.key_url('https://example.org/A'),
                            G.key_url('https://example.org/a'))

    def test_query_order_preserved(self):
        self.assertNotEqual(G.key_url('https://example.org/?a=1&b=2'),
                            G.key_url('https://example.org/?b=2&a=1'))

    def test_fragment_preserved(self):
        self.assertNotEqual(G.key_url('https://example.org/a#one'),
                            G.key_url('https://example.org/a#two'))

    def test_duplicate_json_field(self):
        p = self.root/'preparedness/sources/crosswalk.json'
        p.write_text('{"status":"a","status":"b"}')
        with self.assertRaisesRegex(G.IntegrityHold, 'DUPLICATE_JSON_KEY'):
            G.audit(self.root)

    def test_no_shared_filesystem_mutation(self):
        p = self.root/'preparedness/sources/crosswalk.json'
        before = p.read_bytes()
        G.audit(self.root)
        self.assertEqual(before, p.read_bytes())

    def test_canonical_alias_adds_author_without_erasing_scope(self):
        added = self.add_alias()
        self.save()
        result = G.audit(self.root)
        self.assertEqual(result['shared_url_groups'], 32)
        self.assertEqual(result['canonical_shared_groups'], 32)
        self.assertEqual(result['canonical_alias_groups'], 1)
        self.assertEqual(result['unreviewed_groups'], 32)
        self.assertEqual(result['release_state'], 'HOLD')
        self.assertFalse(result['may_publish'])
        self.assertEqual(added['source']['supports'],
                         'Distinct author reading scope, not a merged claim.')

    def test_canonical_alias_missing_variant_fails(self):
        self.add_alias()
        self.x['groups'][0]['variants'].pop()
        self.assert_hold('SOURCE_VARIANT_ROSTER_DRIFT')

    def test_canonical_alias_missing_identity_fails(self):
        self.add_alias()
        self.x['groups'][0]['identities'].pop()
        self.assert_hold('SOURCE_IDENTITY_ROSTER_DRIFT')

    def test_canonical_alias_wrong_author_fails(self):
        alias = self.add_alias()
        alias['origin'] = 'food'
        self.assert_hold('SOURCE_VARIANT_ROSTER_DRIFT')

    def test_canonical_alias_changed_reading_scope_fails(self):
        alias = self.add_alias()
        alias['source']['supports'] = 'Fabricated substitute.'
        self.assert_hold('SOURCE_VARIANT_CONTENT_DRIFT')

    def test_canonical_alias_changed_row_index_fails(self):
        alias = self.add_alias()
        alias['row_index'] = 99
        self.assert_hold('SOURCE_VARIANT_ROSTER_DRIFT')

    def test_canonical_alias_unauthorized_approval_fails(self):
        self.add_alias()
        self.x['groups'][0]['review_status'] = 'resolved'
        self.assert_hold('PREMATURE_SOURCE_APPROVAL')

    def test_canonical_alias_group_retarget_fails(self):
        self.add_alias()
        self.x['groups'][0]['url'] = 'https://unrelated.example.org/wrong'
        self.assert_hold('CANONICAL_URL_DRIFT')

    def test_alias_key_keeps_query_distinct(self):
        self.assertNotEqual(G.alias_key_url('https://example.org/a/?x=1'),
                            G.alias_key_url('https://example.org/a?x=2'))

    def test_alias_key_keeps_path_case_distinct(self):
        self.assertNotEqual(G.alias_key_url('https://example.org/A/'),
                            G.alias_key_url('https://example.org/a'))

    def test_alias_key_collapses_terminal_slash_only(self):
        self.assertEqual(G.alias_key_url('https://example.org/a/'),
                         G.alias_key_url('https://example.org/a'))
        self.assertNotEqual(G.key_url('https://example.org/a/'),
                            G.key_url('https://example.org/a'))

    def test_alias_key_preserves_fragments(self):
        self.assertNotEqual(G.alias_key_url('https://example.org/a/#first'),
                            G.alias_key_url('https://example.org/a/#second'))


def per_group_test(index):
    def check(self):
        self.x['groups'][index]['variants'][-1]['source']['supports'] += ' injected'
        self.assert_hold('SOURCE_VARIANT_CONTENT_DRIFT')
    return check

for i in range(32):
    setattr(SyntheticReview, 'test_scope_preservation_group_%02d' % i, per_group_test(i))


class ActualCheckout(unittest.TestCase):
    def test_actual_candidate_if_full_repo_present(self):
        root = Path(__file__).resolve().parents[2]
        if not (root/'preparedness/sources/register.json').exists():
            self.skipTest('full trusted checkout not mounted locally')
        result = G.audit(root)
        self.assertEqual(result['shared_url_groups'], 32)
        self.assertFalse(result['QD_PASS'])


if __name__ == '__main__':
    unittest.main()
