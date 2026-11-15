"""Synthetic Article #11 scope-collision controls; no safety approval implied."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r400_jerky_source_scope_gate as gate

REGISTRY_FILE = Path(__file__).resolve().parents[1] / 'reviews' / 'r400_article11_postfreeze_scope_registry.json'


def serialize(obj):
    return (json.dumps(obj, sort_keys=True) + '\n').encode()


def fake_original():
    return {
        'release_state': gate.STATE, 'publication_approved': False,
        'qualified_safety_approved': False, 'automatic_variant_selection': False,
        'expected': {
            'original_article_count': 35, 'original_distinct_source_ids': 203,
            'source_record_occurrences': 280, 'source_evidence_disputes': 5,
            'unselected_original_forks': 9,
        },
        'original_articles': [{'slug': 'safe-jerky-dehydration'}] +
            [{'slug': f'synthetic-article-{i:02d}'} for i in range(34)],
        'source_evidence_disputes': [{
            'source_id': 'nchfp-jerky', 'decision': 'HUMAN_REVIEW_REQUIRED',
            'selected_record': None,
            'variants': [
                {'source_blob': sha, 'human_link_check': False}
                for sha in sorted(gate.ORIGINAL_SOURCE_BLOBS)
            ],
        }],
    }

class R400IntegrityCases(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(REGISTRY_FILE.read_text(encoding='utf-8'))
        self.docket = fake_original()
        self.registry["source_docket_git_blob"] = gate.git_blob(serialize(self.docket))

    def result(self, *, registry=None, docket=None, pin=None):
        raw = serialize(self.docket if docket is None else docket)
        obj = self.registry if registry is None else registry
        return gate.inspect(raw, serialize(obj), docket_pin=gate.git_blob(raw) if pin is None else pin)

    def test_clean_synthetic_structure_still_hard_holds(self):
        r = self.result()
        self.assertEqual(r['integrity'], 'PASS', r['failures'])
        self.assertEqual(r['release'], gate.STATE)
        self.assertFalse(r['eligible'])
        self.assertEqual(r['source_count'], 5)
        self.assertEqual(r['conflict_count'], 4)

    def test_original_docket_exact_sha_required(self):
        self.assertIn('original_docket_blob', self.result(pin=gate.ORIGINAL_DOCKET_BLOB)['failures'])

    def test_invalid_docket_json_fail_closed(self):
        r = gate.inspect(b'not-json', serialize(self.registry), docket_pin=gate.git_blob(b'not-json'))
        self.assertEqual(r['integrity'], 'FAIL')

    def test_invalid_registry_json_fail_closed(self):
        raw = serialize(self.docket)
        r = gate.inspect(raw, b'not-json', docket_pin=gate.git_blob(raw))
        self.assertEqual(r['integrity'], 'FAIL')

    def test_nonobject_docket_fail_closed(self):
        raw = b'[]'
        r = gate.inspect(raw, serialize(self.registry), docket_pin=gate.git_blob(raw))
        self.assertEqual(r['integrity'], 'FAIL')

    def test_nonobject_registry_fail_closed(self):
        raw = serialize(self.docket)
        r = gate.inspect(raw, b'[]', docket_pin=gate.git_blob(raw))
        self.assertEqual(r['integrity'], 'FAIL')

    def test_duplicate_source_identity_rejected(self):
        obj = copy.deepcopy(self.registry)
        obj['sources'][1]['id'] = obj['sources'][0]['id']
        self.assertEqual(self.result(registry=obj)['integrity'], 'FAIL')

    def test_duplicate_conflict_identity_rejected(self):
        obj = copy.deepcopy(self.registry)
        obj['conflicts'][1]['id'] = obj['conflicts'][0]['id']
        self.assertEqual(self.result(registry=obj)['integrity'], 'FAIL')

    def test_source_inventory_must_be_unchanged(self):
        obj = copy.deepcopy(self.docket)
        obj['expected']['source_record_occurrences'] -= 1
        self.assertIn('original_inventory_changed', self.result(docket=obj)['failures'])

    def test_article_identity_must_remain_present(self):
        obj = copy.deepcopy(self.docket)
        obj['original_articles'][0]['slug'] = 'different-article'
        self.assertIn('original_article_identity', self.result(docket=obj)['failures'])

    def test_original_source_git_blob_cannot_change(self):
        obj = copy.deepcopy(self.docket)
        obj['source_evidence_disputes'][0]['variants'][0]['source_blob'] = '0' * 40
        self.assertIn('original_candidate_blobs', self.result(docket=obj)['failures'])

    def test_original_source_link_review_stays_false(self):
        obj = copy.deepcopy(self.docket)
        obj['source_evidence_disputes'][0]['variants'][0]['human_link_check'] = True
        self.assertIn('original_human_link_status', self.result(docket=obj)['failures'])

    def test_original_source_variant_auto_selection_blocked(self):
        obj = copy.deepcopy(self.docket)
        obj['source_evidence_disputes'][0]['selected_record'] = 1
        self.assertIn('original_dispute_selected', self.result(docket=obj)['failures'])

    def test_original_source_variant_decision_not_promoted(self):
        obj = copy.deepcopy(self.docket)
        obj['source_evidence_disputes'][0]['decision'] = 'PASS'
        self.assertIn('original_dispute_selected', self.result(docket=obj)['failures'])

    def test_missing_original_source_dispute_rejected(self):
        obj = copy.deepcopy(self.docket)
        obj['source_evidence_disputes'] = []
        self.assertIn('original_source_dispute', self.result(docket=obj)['failures'])


def add_case(name, mutate, *, mutate_docket=False):
    def _case(self):
        obj = copy.deepcopy(self.docket if mutate_docket else self.registry)
        mutate(obj)
        result = self.result(**({'docket': obj} if mutate_docket else {'registry': obj}))
        self.assertEqual(result['integrity'], 'FAIL', f'{name}: {result}')
        self.assertEqual(result['release'], gate.STATE)
        self.assertFalse(result['eligible'])
    setattr(R400IntegrityCases, 'test_reject_' + name, _case)


for key, change in {
    'schema': 'not-a-real-schema', 'source_docket_git_blob': 'f' * 40,
    'article_slug': 'an-unrelated-article', 'source_id': 'wrong-source',
    'editorial_issue': 0, 'conversion_issue': 0, 'business_charter_issue': 0,
    'review_comment_ids': [6901118072], 'state': 'LIVE', 'decision': 'APPROVED',
    'selected_source_id': 'nchfp_home_jerky', 'selected_manuscript_blob': 'f' * 40,
    'current_household_instructions': 'unreviewed method text',
    'actual_paid_preparedness_sku': 'unverified-product',
}.items():
    add_case('metadata_' + key, lambda x, k=key, v=change: x.__setitem__(k, v))
for flag in gate.RELEASE_FALSE:
    add_case('release_flag_' + flag, lambda x, k=flag: x.__setitem__(k, True))
for source_id in gate.SOURCE_POLICY:
    for prop, value in {
        'url': 'https://example.invalid/',
        'evidence_level': 'DIRECTLY_VERIFIED_SAFETY_APPROVAL',
        'scope': 'ALL_FOOD_PRODUCTS_SAFE',
        'observed_on': '1900-01-01',
        'human_reviewer_checked': True,
        'usable_as_current_home_method': True,
        'selected_for_article': True,
    }.items():
        def change(x, sid=source_id, k=prop, v=value):
            next(i for i in x['sources'] if i['id'] == sid)[k] = v
        add_case(source_id + '_' + prop, change)
    def drop(x, sid=source_id):
        x['sources'] = [i for i in x['sources'] if i['id'] != sid]
    add_case(source_id + '_missing', drop)
for conflict_id in gate.CONFLICT_POLICY:
    for prop, value in {
        'source_ids': ['unrelated_source'],
        'decision': 'APPROVED',
        'approved_public_guidance': True,
    }.items():
        def change(x, cid=conflict_id, k=prop, v=value):
            next(i for i in x['conflicts'] if i['id'] == cid)[k] = v
        add_case(conflict_id + '_' + prop, change)
    def drop(x, cid=conflict_id):
        x['conflicts'] = [i for i in x['conflicts'] if i['id'] != cid]
    add_case(conflict_id + '_missing', drop)
for req in ('product_and_processing_scope', 'source_date_and_currency', 'storage_conditions',
            'processing_sequence', 'species_specific_risks', 'independent_qualified_signoff'):
    add_case('review_gap_' + req, lambda x, v=req: x['review_requirements'].remove(v))

if __name__ == '__main__':
    unittest.main()
