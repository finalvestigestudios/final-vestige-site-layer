"""Synthetic-only regression suite for R378; not real source/clinical approval."""
import copy
import importlib.util
import pathlib
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'r378_authoritative_registry_claim_gate.py'
spec = importlib.util.spec_from_file_location('r378_gate', SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
IDS = ['cdc-botulism-prevention', 'fsis-home-cure-qa', 'nchfp-cure-smoke',
       'nchfp-jerky', 'food-fsis-jerky', 'food-fsis-jerky-qa', 'food-ksu-jerky',
       'food-fsis-shelf-stable', 'food-fsis-emergencies', 'food-osu-survival-food', 'food-nchfp-other']


def row(sid, verified=True):
    return {'id': sid, 'url': 'https://example.org/' + sid, 'title': sid,
            'supports': 'Only a synthetic source reading scope',
            'verified_on': '2026-10-29' if verified else None,
            'human_link_check': False}


def fixture():
    base = {'sources': [row(s) for s in gate.BASE_ONLY] + [row('nchfp-jerky', False)]}
    food = {'sources': [row(s) for s in IDS if s not in gate.BASE_ONLY]}
    meta = {'n': 11, 'slug': 'safe-jerky-dehydration',
            'status': {'publish': 'draft'}, 'safety_review': {'state': 'pending'},
            'source_use': {sid: 'Author-specific complete reading description ' + sid for sid in IDS}}
    body = 'Wild game freezing and heat to 160: ' + ''.join('{{cite:%s}}' % sid for sid in IDS * 6 + IDS[:5])
    crosswalk = {'article_origins': {'safe-jerky-dehydration': 'food'}}
    prior = {'source_use_ids_absent_from_r374_fragment_crosswalk': list(gate.BASE_ONLY),
             'release_state': 'DRAFT_HARD_HOLD', 'publication_approved': False}
    return [base, food, body, meta, crosswalk, prior]


def check(fx):
    return gate.evaluate(*fx)


class PositiveAndHardHold(unittest.TestCase):
    def test_synthetic_source_path_explained_without_approval(self):
        result = check(fixture())
        self.assertEqual(result['errors'], [])
        self.assertTrue(result['source_path_resolved'])
        self.assertFalse(result['approval'])
        self.assertFalse(result['human_link_checks_complete'])
        self.assertFalse(result['qualified_food_safety_review'])
        self.assertFalse(result['public_publish_allowed'])
        self.assertFalse(result['commercial_offer_allowed'])
        self.assertEqual(result['release_state'], 'DRAFT_HARD_HOLD')
    def test_exact_citation_count_in_synthetic_fixture(self):
        self.assertEqual(check(fixture())['citations']['occurrences'], 71)
    def test_distinct_citations_in_synthetic_fixture(self):
        self.assertEqual(check(fixture())['citations']['unique_ids'], 11)
    def test_base_only_reconciliation_does_not_assert_link_check(self):
        self.assertEqual(check(fixture())['citations']['base_fallback_ids'], list(gate.BASE_ONLY))
    def test_food_origin_pinned_in_synthetic_fixture(self):
        self.assertEqual(check(fixture())['citations']['resolved_origin_map']['nchfp-jerky'], 'food')
    def test_missing_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = gate.check_pins(pathlib.Path(tmp))
            self.assertEqual(len(missing), len(gate.PIN))
    def test_git_blob_known_vector(self):
        self.assertEqual(gate.git_blob(b'hello\n'), 'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_git_blob_sensitive_to_byte_change(self):
        self.assertNotEqual(gate.git_blob(b'hello\n'), gate.git_blob(b'hello'))


class RejectMutations(unittest.TestCase):
    def test_unknown_source_gate_is_no_release(self):
        fx = fixture()
        fx[0]['sources'] = []
        r = check(fx)
        self.assertFalse(r['source_path_resolved'])
        self.assertFalse(r['approval'])
    def test_invalid_register_type_fails(self):
        r = gate.evaluate({'sources': {}}, {}, '', {}, {}, {})
        self.assertFalse(r['source_path_resolved'])
    def test_does_not_modify_inputs(self):
        fx = fixture()
        before = copy.deepcopy(fx)
        check(fx)
        self.assertEqual(fx, before)


def _bad_case(name, mutator):
    def method(self):
        fx = fixture()
        mutator(fx)
        result = check(fx)
        self.assertFalse(result['source_path_resolved'], name)
        self.assertFalse(result['approval'])
        self.assertEqual(result['release_state'], 'DRAFT_HARD_HOLD')
        self.assertGreaterEqual(len(result['errors']), 1)
    method.__name__ = 'test_reject_' + name
    return method


MUTATIONS = []
for sid in gate.BASE_ONLY:
    MUTATIONS.extend([
        (sid + '_deleted', lambda fx, sid=sid: fx[0]['sources'].__setitem__(slice(None), [x for x in fx[0]['sources'] if x['id'] != sid])),
        (sid + '_http', lambda fx, sid=sid: next(x for x in fx[0]['sources'] if x['id'] == sid).__setitem__('url', 'http://example.org')),
        (sid + '_scope_blank', lambda fx, sid=sid: next(x for x in fx[0]['sources'] if x['id'] == sid).__setitem__('supports', '')),
        (sid + '_unchecked', lambda fx, sid=sid: next(x for x in fx[0]['sources'] if x['id'] == sid).__setitem__('verified_on', None)),
        (sid + '_human_flag_flip', lambda fx, sid=sid: next(x for x in fx[0]['sources'] if x['id'] == sid).__setitem__('human_link_check', True)),
        (sid + '_shadow', lambda fx, sid=sid: fx[1]['sources'].append(row(sid))),
    ])
for sid in IDS:
    MUTATIONS.append((sid + '_blank_source_use', lambda fx, sid=sid: fx[3]['source_use'].__setitem__(sid, '')))
for sid in IDS[4:]:
    MUTATIONS.extend([
        (sid + '_missing_origin', lambda fx, sid=sid: fx[1]['sources'].__setitem__(slice(None), [x for x in fx[1]['sources'] if x['id'] != sid])),
        (sid + '_bad_link_flag', lambda fx, sid=sid: next(x for x in fx[1]['sources'] if x['id'] == sid).__setitem__('human_link_check', True)),
        (sid + '_missing_scope', lambda fx, sid=sid: next(x for x in fx[1]['sources'] if x['id'] == sid).__setitem__('supports', '')),
    ])
MUTATIONS += [
    ('wrong_slug', lambda f: f[3].__setitem__('slug', 'alternate')),
    ('wrong_number', lambda f: f[3].__setitem__('n', 10)),
    ('publish_flip', lambda f: f[3]['status'].__setitem__('publish', 'published')),
    ('safety_approved_without_review', lambda f: f[3]['safety_review'].__setitem__('state', 'approved')),
    ('one_citation_deleted', lambda f: f.__setitem__(2, f[2].replace('{{cite:food-fsis-jerky}}', '', 1))),
    ('citation_injected', lambda f: f.__setitem__(2, f[2] + '{{cite:rogue-id}}')),
    ('missing_usage', lambda f: f[3]['source_use'].pop('food-fsis-jerky')),
    ('extra_usage', lambda f: f[3]['source_use'].__setitem__('unexpected', 'extra')),
    ('wrong_origin', lambda f: f[4]['article_origins'].__setitem__('safe-jerky-dehydration', 'base')),
    ('docket_ids', lambda f: f[5].__setitem__('source_use_ids_absent_from_r374_fragment_crosswalk', [])),
    ('prior_approval', lambda f: f[5].__setitem__('publication_approved', True)),
    ('prior_state', lambda f: f[5].__setitem__('release_state', 'LIVE')),
    ('nchfp_food_missing', lambda f: f[1]['sources'].__setitem__(slice(None), [x for x in f[1]['sources'] if x['id'] != 'nchfp-jerky'])),
    ('nchfp_origin_unverified', lambda f: next(x for x in f[1]['sources'] if x['id'] == 'nchfp-jerky').__setitem__('verified_on', None)),
    ('nchfp_url_mismatch', lambda f: next(x for x in f[1]['sources'] if x['id'] == 'nchfp-jerky').__setitem__('url', 'https://other.org')),
    ('nchfp_base_verified', lambda f: next(x for x in f[0]['sources'] if x['id'] == 'nchfp-jerky').__setitem__('verified_on', '2026-10-29')),
    ('wild_game_claim_disappeared', lambda f: f.__setitem__(2, f[2].replace('Wild game', 'Wildlife'))),
    ('heat_claim_disappeared', lambda f: f.__setitem__(2, f[2].replace('heat to 160', 'cool to cold'))),
    ('base_duplicate_id', lambda f: f[0]['sources'].append(copy.deepcopy(f[0]['sources'][0]))),
    ('food_duplicate_id', lambda f: f[1]['sources'].append(copy.deepcopy(f[1]['sources'][0]))),
]
for n, mutation in MUTATIONS:
    setattr(RejectMutations, 'test_reject_' + n.replace('-', '_'), _bad_case(n, mutation))

if __name__ == '__main__':
    unittest.main()
