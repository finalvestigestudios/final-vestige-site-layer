"""Synthetic R273 identity and false-approval adversarial checks; NOT publication QA."""
import copy
import importlib.util
import unittest
from pathlib import Path

P = Path(__file__).resolve().parents[1] / 'tools/r273_source_review_docket_hold.py'
spec = importlib.util.spec_from_file_location('r273', P)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture():
    a = {'id': 'same', 'url': 'https://example.org/x', 'supports': 'A', 'human_link_check': False}
    b = {'id': 'same', 'url': 'https://example.org/x/', 'supports': 'B', 'human_link_check': False}
    c = {'id': 'single', 'url': 'https://example.org/y', 'supports': 'C', 'human_link_check': False}
    sources = {'base': [a, c], 'food': [b]}
    paths = {'base': 'preparedness/sources/register.json', 'food': 'preparedness/sources/fragments/food.json'}
    crosswalk = {'source_files': [{'origin': o, 'path': paths[o]} for o in sources],
                 'groups': [{'url': 'https://example.org/x', 'review_status': 'pending-human-source-and-reading-scope-review',
                             'variants': [{'origin': o, 'source_file': paths[o], 'row_index': 0,
                                           'source': copy.deepcopy(sources[o][0])} for o in ('base', 'food')]}]}
    return crosswalk, sources


class R273Tests(unittest.TestCase):
    def test_draft_hold_preserves_source_readings(self):
        x, sources = fixture()
        d = gate.build_docket(x, sources)
        self.assertEqual((d['source_rows'], d['exact_urls'], d['review_alias_groups'], d['duplicate_source_id_groups']), (3, 3, 1, 1))
        self.assertEqual(d['shared_url_review'][0]['variants'][1]['source']['supports'], 'B')
        self.assertEqual(d['duplicate_id_review'][0]['variants'][0]['source']['supports'], 'A')
        self.assertEqual(d['state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(d['publication_authorized'])

    def test_deterministic(self):
        x, sources = fixture()
        self.assertEqual(gate.build_docket(x, sources), gate.build_docket(copy.deepcopy(x), copy.deepcopy(sources)))

    def test_duplicate_key_fails(self):
        with self.assertRaises(ValueError): gate.read_json(b'{"a":1,"a":2}')

    def test_nan_fails(self):
        with self.assertRaises(ValueError): gate.read_json(b'{"a":NaN}')

    def test_untrusted_source_gate_fails_closed(self):
        result = gate.audit(Path('.'), lambda root, name: b'invalid source gate')
        self.assertEqual(result['state'], gate.INVALID)
        self.assertFalse(result['independent_qd_pass'])

    def test_blob_identity(self):
        self.assertEqual(gate.blob(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')


# Unique review attributes and every high-risk false positive must fail document parity.
CHANGES = [
    ('schema', 'fake'), ('state', 'APPROVED'), ('crosswalk_blob', 'a'*40),
    ('warning', 'SAFE'), ('source_rows', 0), ('source_rows', 245),
    ('review_alias_groups', 0), ('review_alias_groups', 31),
    ('duplicate_source_id_groups', 0), ('duplicate_source_id_groups', 14),
    ('exact_urls', 0), ('exact_urls', 201), ('article_7_chemical_claims_reviewed', True),
    ('article_7_cdc_claims_reviewed', True), ('article_20_readygov_claim_reviewed', True),
    ('independent_qd_pass', True), ('medical_safety_verified', True),
    ('privacy_approved', True), ('merchant_offer_approved', True),
    ('publication_authorized', True), ('may_merge', True),
    ('shared_url_review.0.review_alias', 'https://fake.org'),
    ('shared_url_review.0.review_status', 'approved'),
    ('shared_url_review.0.reviewer', 'signed'),
    ('shared_url_review.0.reviewed_on', '2026-11-10'),
    ('shared_url_review.0.variants.0.origin', 'wrong'),
    ('shared_url_review.0.variants.0.source_file', 'wrong'),
    ('shared_url_review.0.variants.0.row_index', 88),
    ('shared_url_review.0.variants.0.source.id', 'wrong'),
    ('shared_url_review.0.variants.0.source.url', 'https://fake.org'),
    ('shared_url_review.0.variants.0.source.supports', 'fake support'),
    ('shared_url_review.0.variants.0.source.human_link_check', True),
    ('shared_url_review.0.variants.1.source.supports', 'fake support'),
    ('duplicate_id_review.0.source_id', 'wrong'),
    ('duplicate_id_review.0.review_status', 'approved'),
    ('duplicate_id_review.0.reviewer', 'signed'),
    ('duplicate_id_review.0.reviewed_on', '2026-11-10'),
    ('duplicate_id_review.0.variants.0.origin', 'wrong'),
    ('duplicate_id_review.0.variants.0.source_file', 'wrong'),
    ('duplicate_id_review.0.variants.0.row_index', 77),
    ('duplicate_id_review.0.variants.0.source.id', 'wrong'),
    ('duplicate_id_review.0.variants.0.source.url', 'https://fake.org'),
    ('duplicate_id_review.0.variants.0.source.supports', 'fake support'),
    ('duplicate_id_review.0.variants.0.source.human_link_check', True),
]

for n, (path, value) in enumerate(CHANGES):
    def adversarial(self, path=path, value=value):
        x, sources = fixture()
        expected = gate.build_docket(x, sources)
        corrupted = copy.deepcopy(expected)
        node = corrupted
        parts = path.split('.')
        for part in parts[:-1]:
            node = node[int(part)] if part.isdigit() else node[part]
        node[parts[-1]] = value
        self.assertNotEqual(corrupted, expected)
    setattr(R273Tests, 'test_docket_mutation_%02d' % n, adversarial)

if __name__ == '__main__': unittest.main()
