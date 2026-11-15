"""R401 rejects ambiguous source-review evidence. Synthetic tests, not safety approval."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r400_jerky_source_scope_gate as gate
from test_r400_jerky_source_scope_gate import fake_original, serialize, REGISTRY_FILE


class R401EvidenceFirewallTests(unittest.TestCase):
    def setUp(self):
        self.docket = fake_original()
        self.registry = json.loads(REGISTRY_FILE.read_text(encoding='utf-8'))
        self.registry['source_docket_git_blob'] = gate.git_blob(serialize(self.docket))

    def review(self, *, docket=None, registry=None, docket_raw=None, registry_raw=None):
        original = serialize(self.docket if docket is None else docket) if docket_raw is None else docket_raw
        register = serialize(self.registry if registry is None else registry) if registry_raw is None else registry_raw
        return gate.inspect(original, register, docket_pin=gate.git_blob(original)
                            if isinstance(original, bytes) else gate.ORIGINAL_DOCKET_BLOB)

    def test_control_synthetic_integrity_pass_still_not_eligible(self):
        r = self.review()
        self.assertEqual('PASS', r['integrity'], r)
        self.assertEqual(gate.STATE, r['release'])
        self.assertFalse(r['eligible'])

    def test_cli_missing_authentic_docket_remains_exit_2(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            registry = Path(temp) / 'scope.json'
            registry.write_bytes(serialize(self.registry))
            missing = Path(temp) / 'not-real-docket.json'
            self.assertEqual(2, gate.main(['--original-docket', str(missing),
                                          '--scope-registry', str(registry)]))

    def test_unexpected_top_level_instruction_fails(self):
        obj = copy.deepcopy(self.registry)
        obj['shelf_life_directions'] = 'UNREVIEWED'
        self.assertEqual('FAIL', self.review(registry=obj)['integrity'])

    def test_original_untrusted_nested_type_stays_structured(self):
        obj = copy.deepcopy(self.docket)
        obj['expected'] = 'not-a-dict'
        self.assertEqual('FAIL', self.review(docket=obj)['integrity'])

    def test_duplicate_registry_key_even_if_same_value(self):
        raw = serialize(self.registry)
        raw = raw[:-2] + b', "state": "DRAFT_HARD_HOLD"}\n'
        self.assertEqual('FAIL', self.review(registry_raw=raw)['integrity'])

    def test_duplicate_docket_key_even_if_same_value(self):
        raw = serialize(self.docket)
        raw = raw[:-2] + b', "release_state": "DRAFT_HARD_HOLD"}\n'
        self.assertEqual('FAIL', self.review(docket_raw=raw)['integrity'])

    def test_non_finite_registry_literal(self):
        raw = serialize(self.registry)
        raw = raw[:-2] + b', "note": NaN}\n'
        self.assertEqual('FAIL', self.review(registry_raw=raw)['integrity'])

    def test_review_requirements_duplicates_not_elided(self):
        obj = copy.deepcopy(self.registry)
        obj['review_requirements'].append(obj['review_requirements'][0])
        self.assertEqual('FAIL', self.review(registry=obj)['integrity'])

    def test_bytes_bound_and_nonbytes(self):
        self.assertEqual('FAIL', self.review(registry_raw=b' ' * 2_000_001)['integrity'])
        self.assertEqual('FAIL', self.review(registry_raw='not bytes')['integrity'])


def _add_case(name, mutator, *, root='registry'):
    def _case(self):
        obj = copy.deepcopy(self.registry if root == 'registry' else self.docket)
        mutator(obj)
        result = self.review(**{root: obj})
        self.assertEqual('FAIL', result['integrity'], name)
        self.assertFalse(result['eligible'])
        self.assertEqual(gate.STATE, result['release'])
        self.assertTrue(result['failures'])
    setattr(R401EvidenceFirewallTests, 'test_fails_' + name, _case)


# Additive keys can otherwise smuggle unsupported public instructions or false QD flags.
for extra in (
    'unapproved_instruction', 'storage_shelf_life_days', 'safe_for_children',
    'automatic_review_pass', 'emergency_current_guidance', 'checkout_link',
    'affiliate_merchant_sold', 'paid_product_id', 'human_approved_at',
    'word_press_publish_now', 'source_claim_verified', 'citation_override',
):
    _add_case('root_extra_' + extra, lambda o, k=extra: o.__setitem__(k, 'unreviewed'))

for collection in ('sources', 'conflicts'):
    for extra in (
        'approved_instructions', 'source_context', 'cached_content',
        'editorial_override', 'qualified_signoff', 'last_reviewed',
        'checkout_url', 'authoritative_new_claim',
    ):
        _add_case(collection + '_extra_' + extra,
                  lambda o, c=collection, k=extra: o[c][0].__setitem__(k, 'unreviewed'))
    for missing in ('id', 'url') if collection == 'sources' else ('id', 'source_ids'):
        _add_case(collection + '_missing_' + missing,
                  lambda o, c=collection, k=missing: o[c][0].pop(k))

for field, bad in {
    'expected': None, 'original_articles': 1, 'source_evidence_disputes': 'not-a-list',
}.items():
    _add_case('docket_bad_' + field, lambda o, k=field, v=bad: o.__setitem__(k, v), root='docket')
for field, bad in {
    'source_evidence_disputes': [None],
    'original_articles': [None],
}.items():
    _add_case('docket_invalid_element_' + field, lambda o,k=field,v=bad:o.__setitem__(k,v), root='docket')

for source_shape in (None, 7, {}, 'bad', [None], [4]):
    key = 'source_shape_' + type(source_shape).__name__ + '_' + str(len(str(source_shape)))
    _add_case(key, lambda o,v=source_shape: o.__setitem__('sources', v))
for conflict_shape in (None, 7, {}, 'bad', [None], [4]):
    key = 'conflict_shape_' + type(conflict_shape).__name__ + '_' + str(len(str(conflict_shape)))
    _add_case(key, lambda o,v=conflict_shape: o.__setitem__('conflicts', v))

for bad in (None, 7, {}, 'bad', [None], [4]):
    key = 'requirements_shape_' + type(bad).__name__ + '_' + str(len(str(bad)))
    _add_case(key, lambda o,v=bad: o.__setitem__('review_requirements', v))

for field in ('sources', 'conflicts'):
    _add_case('nested_unhashable_' + field,
              lambda o,k=field:o[k][0].__setitem__('id', {'bad':'id'}))

_add_case('docket_bad_variants', lambda o:o['source_evidence_disputes'][0].__setitem__('variants', [None]),root='docket')
_add_case('docket_variant_not_list', lambda o:o['source_evidence_disputes'][0].__setitem__('variants', 'bad'),root='docket')
_add_case('docket_dispute_element_not_object',lambda o:o['source_evidence_disputes'].append(None),root='docket')


if __name__ == '__main__':
    unittest.main()
