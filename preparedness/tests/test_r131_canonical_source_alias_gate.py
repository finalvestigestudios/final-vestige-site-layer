"""Synthetic/adversarial tests for R131. Does not grant human source review."""
import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'tools' / 'r131_canonical_source_alias_gate.py'
spec = importlib.util.spec_from_file_location('r131_canonical_source_alias_gate', SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture(complete=False):
    docs = {o: {'sources': []} for o in gate.FILE_PINS}
    def row(id, url, supports='scope'):
        return {'id': id, 'url': url, 'supports': supports, 'notes': 'unique notes'}
    docs['base']['sources'] = [row('root-jerky', 'https://nchfp.uga.edu/how/dry/recipes/jerky')]
    docs['food']['sources'] = [row('food-jerky', 'https://nchfp.uga.edu/how/dry/recipes/jerky')]
    docs['hist-food']['sources'] = [row('historic-jerky', 'https://nchfp.uga.edu/how/dry/recipes/jerky/', 'another interpretation')]
    refs = [{'origin': 'base','id': 'root-jerky','row_index': 0},
            {'origin': 'food','id': 'food-jerky','row_index': 0}]
    if complete:
        refs.append({'origin': 'hist-food', 'id': 'historic-jerky', 'row_index': 0})
    crosswalk = {'groups':[{'url': 'https://nchfp.uga.edu/how/dry/recipes/jerky',
                            'review_status':'pending-human-source-and-reading-scope-review',
                            'reviewer': None, 'reviewed_on': None, 'identities':refs}]}
    return docs, crosswalk


class AuditTests(unittest.TestCase):
    def test_actual_alias_gap_is_not_an_approval(self):
        d, c = fixture()
        a = gate.audit(d, c)
        self.assertEqual(a['status'], 'HOLD_CANONICAL_CROSSWALK_GAP')
        self.assertEqual(a['incomplete_groups'][0]['missing'], [['hist-food','historic-jerky',0]])
        self.assertFalse(a['may_merge'])
        self.assertFalse(a['may_publish'])

    def test_complete_crosswalk_still_holds(self):
        d, c = fixture(True)
        a = gate.audit(d, c)
        self.assertEqual(a['status'], 'HOLD_HUMAN_SOURCE_SCOPE_REVIEW')
        self.assertTrue(a['structural_crosswalk_complete'])
        self.assertFalse(a['independent_QD_PASS'])
        self.assertFalse(a['human_safety_approved'])
        self.assertFalse(a['commercial_offer_approved'])

    def test_exact_and_canonical_censuses_differ(self):
        d, c = fixture()
        a = gate.audit(d, c)
        self.assertEqual((a['source_rows'],a['exact_urls'],a['canonical_urls']), (3,2,1))
        self.assertEqual(len(a['canonical_alias_groups']),1)

    def test_forged_approval_rejected(self):
        d, c = fixture(True)
        c['groups'][0]['review_status']='approved'
        with self.assertRaisesRegex(gate.GateError, 'PREMATURE_APPROVAL'):
            gate.audit(d,c)

    def test_reviewer_added_without_review_rejected(self):
        d, c = fixture(True)
        c['groups'][0]['reviewer']='auto'
        with self.assertRaisesRegex(gate.GateError,'REVIEWER_STATE_CHANGED'):
            gate.audit(d,c)

    def test_duplicate_key_rejected(self):
        with self.assertRaisesRegex(gate.GateError,'DUPLICATE_JSON_KEY'):
            gate.parse_json('{"a":1,"a":2}')

    def test_different_query_is_distinct_source(self):
        d, c = fixture(True)
        d['hist-food']['sources'][0]['url'] += '?x=1'
        a = gate.audit(d,c)
        self.assertEqual(a['status'], 'HOLD_CANONICAL_CROSSWALK_GAP')
        self.assertTrue(a['incomplete_groups'])

    def test_duplicate_row_identity_rejected(self):
        d, c = fixture(True)
        c['groups'][0]['identities'].append(c['groups'][0]['identities'][0])
        with self.assertRaisesRegex(gate.GateError,'DUPLICATE_CROSSWALK_IDENTITY'):
            gate.audit(d,c)

    def test_duplicate_fragment_id_rejected(self):
        d,c=fixture(True)
        d['food']['sources'].append(d['food']['sources'][0])
        with self.assertRaisesRegex(gate.GateError,'DUPLICATE_ID_WITHIN_FRAGMENT'):
            gate.audit(d,c)

    def test_missing_source_origin_rejected(self):
        d,c=fixture(True)
        d.pop('start')
        with self.assertRaisesRegex(gate.GateError,'INCOMPLETE_SOURCE_ROSTER'):
            gate.audit(d,c)

    def test_unknown_identity_rejected(self):
        d,c=fixture(True)
        c['groups'][0]['identities'][2]['id']='forged'
        a=gate.audit(d,c)
        self.assertEqual(a['status'],'HOLD_CANONICAL_CROSSWALK_GAP')
        self.assertEqual(a['incomplete_groups'][0]['unexpected'],[['hist-food','forged',0]])

    def test_malformed_group_rejected(self):
        d,c=fixture(True)
        c['groups'][0]['identities'][0]['row_index']=True
        with self.assertRaisesRegex(gate.GateError,'INVALID_ROW_INDEX'):
            gate.audit(d,c)

    def test_blob_sha_standard_git_object(self):
        self.assertEqual(gate.blob_sha(b'test content\n'),'d670460b4b4aece5915caf5c68d12f560a9fe3e4')


GOOD = [
('https://example.org/', 'https://example.org/'),
('HTTPS://Example.ORG/path/', 'https://example.org/path'),
('https://example.org/path', 'https://example.org/path'),
('https://example.org:443/path/', 'https://example.org/path'),
('https://EXAMPLE.org/path?st=list', 'https://example.org/path?st=list'),
('https://example.org/path?st=list', 'https://example.org/path?st=list'),
('https://example.org/path?st=other','https://example.org/path?st=other'),
('https://example.org/a/B/','https://example.org/a/B'),
('https://example.org/a/b/','https://example.org/a/b'),
('https://example.org/a%20b/','https://example.org/a%20b'),
('https://example.org/a%2Eb','https://example.org/a%2Eb'),
('https://nchfp.uga.edu/how/dry/recipes/jerky/','https://nchfp.uga.edu/how/dry/recipes/jerky'),
('https://nchfp.uga.edu/how/dry/recipes/jerky','https://nchfp.uga.edu/how/dry/recipes/jerky'),
('https://www.loc.gov/resource/foo/?st=list','https://www.loc.gov/resource/foo?st=list'),
('https://archive.org/download/a/a_djvu.txt','https://archive.org/download/a/a_djvu.txt'),
('https://archive.org/a//b','https://archive.org/a//b'),
('https://example.org/abc///','https://example.org/abc'),
('https://example.org/ABC///','https://example.org/ABC'),
]
BAD = [
'', ' ', 'http://example.org/path', 'file:///etc/passwd', 'javascript:alert(1)',
'https://user:secret@example.org/a','https://user@example.org/a',
'https://example.org:444/path','https://example.org:99999/a',
'https://example.org/path#unsafe','https://example.org/has space',
'https://example.org/has\\slash','https://example.org/a%2Fb',
'https://example.org/a%5cb','https://example.org/a%00b',
'https://example.org//path', 'https://.example.org/a',
'https://example..org/a', 'not a url', None, 9,
'https://example.org/white\tspace','https://example.org/white\nspace',
]


def make_good(index, raw, expect):
    def go(self):
        self.assertEqual(gate.canonical(raw), expect)
    go.__name__ = f'test_good_url_{index:02d}'
    return go


def make_bad(index, raw):
    def go(self):
        with self.assertRaises(gate.GateError):
            gate.canonical(raw)
    go.__name__ = f'test_bad_url_{index:02d}'
    return go

for n, (raw, expected) in enumerate(GOOD,1):
    setattr(AuditTests, f'test_good_url_{n:02d}', make_good(n,raw,expected))
for n, raw in enumerate(BAD,1):
    setattr(AuditTests, f'test_bad_url_{n:02d}', make_bad(n,raw))

if __name__ == '__main__':
    unittest.main()
