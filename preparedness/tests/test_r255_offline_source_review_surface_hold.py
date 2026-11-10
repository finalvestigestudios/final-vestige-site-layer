"""Isolated synthetic tests only. Not a live source claim/safety or WordPress audit."""
import copy
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'tools/r255_offline_source_review_surface_hold.py'
spec = importlib.util.spec_from_file_location('r255', SOURCE)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def fixture():
    urls = [f'https://evidence.example/scope-{n:02d}' for n in range(32)]
    ids = ['start-ready-plan'] + [f'other-{n}' for n in range(55)]
    groups = [{'source_url': url, 'source_ids': [], 'priority': 'REVIEW_REQUIRED',
               'source_evidence_sha256': r.digest(url), 'workorders': [],
               'state': r.PENDING, 'source_scope_approved': False,
               'claim_support_approved': False} for url in urls]
    for idx, sid in enumerate(ids):
        groups[idx // 2 if idx < 48 else idx - 24]['source_ids'].append(sid)
    # exactly 2,000 logical slots: 57 citations each for 34 articles; 62 for #35
    slots = [(a, b) for a in range(1, 36)
             for b in range(1, 63 if a == 35 else 58)]
    dispute = {(7, 30): 'cdc-find-clean-water',
               (7, 48): 'cdc-find-clean-water', (20, 55): 'start-ready-plan'}
    chosen = set(slots[:559]) | set(dispute)
    for point in slots:
        if len(chosen) >= 564:
            break
        chosen.add(point)
    # Preserve two Article #7 CDC disputed citations OUTSIDE shared groups.
    external = []
    for i, point in enumerate(sorted(chosen)):
        a, b = point
        sid = dispute.get(point, ids[1 + i % 55])
        excerpt = f'Authored context A{a} cite{b} — <img src=x onerror=alert(1)> & "unsafe".'
        row = {'article_n': a, 'article_slug': f'article-{a}',
            'citation_ordinal': b, 'source_id': sid,
            'authored_context_excerpt': excerpt, 'context_sha256': r.digest(excerpt),
            'author_source_use_note_sha256': r.digest('note' + sid),
            'review_terms': [], 'disputed_original_citation': point in dispute,
            'source_support_verified': False, 'safety_approved': False}
        if sid == 'cdc-find-clean-water':
            external.append(row)
        else:
            group = next(g for g in groups if sid in g['source_ids'])
            group['workorders'].append(row)
    for group in groups:
        group['workorders'].sort(key=lambda w: (w['article_n'], w['citation_ordinal']))
        group['workorder_count'] = len(group['workorders'])
    receipt = {'schema': r.UPSTREAM, 'state': r.HOLD,
               'source_review_groups': 32, 'shared_source_ids': 56,
               'article_count': 35, 'citation_count': 2000,
               'human_readable_workorders': 562,
               'other_citation_occurrences_still_unreviewed': 1438,
               'disputed_original_claims': 3, 'shared_disputed_claims': 1,
               'outside_shared_disputed_claims': 2,
               'outside_shared_disputed_workorders': external,
               'review_queue': groups,
               **{k: False for k in r.FALSE}}
    receipt['receipt_sha256'] = r.digest(r.canonical(receipt))
    assert sum(g['workorder_count'] for g in groups) == 562
    return receipt


BASE = fixture()


def refreshed(data):
    data['receipt_sha256'] = r.digest(r.canonical({
        k: v for k, v in data.items() if k != 'receipt_sha256'}))
    return data


class TestR255(unittest.TestCase):
    def test_complete_inert_review(self):
        record = r.audit_offline_review(BASE)
        self.assertEqual((record['source_review_groups'], record['review_workorders'],
                          record['unmatched_citations_unreviewed'],
                          record['original_disputes_visible']), (32, 562, 1438, 3))
        self.assertEqual(record['state'], r.HOLD)
        self.assertFalse(record['independent_qd_pass'])
        self.assertFalse(record['publication_authorized'])

    def test_full_562_contexts_stay_escaped(self):
        page = r.render_offline_review(BASE)
        self.assertEqual(page.count('<article>'), 564)
        self.assertEqual(page.count('<section>'), 33)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', page)
        self.assertNotIn('<img ', page)
        self.assertNotIn('<a ', page)
        self.assertNotIn('<script', page)
        self.assertNotIn('<form', page)
        self.assertIn('default-src &#39;none&#39;', page)

    def test_determinism_and_zero_upstream_mutation(self):
        before = copy.deepcopy(BASE)
        self.assertEqual(r.audit_offline_review(BASE), r.audit_offline_review(BASE))
        self.assertEqual(BASE, before)

    def test_triage_does_not_grant_source_clearance(self):
        annotations, _ = r.source_url_annotations('http://example.org/p?tag=a#ref')
        self.assertEqual(annotations, ('non_https_review', 'query_scope_review',
                                       'fragment_scope_review'))

    def test_url_alias_detection_is_a_review_signal_only(self):
        data = copy.deepcopy(BASE)
        data['review_queue'][0]['source_url'] = 'https://EVIDENCE.example/scope-01/'
        refreshed(data)
        result = r.audit_offline_review(data)
        self.assertEqual(result['potential_url_alias_pairs_to_review'], 1)
        self.assertFalse(result['publication_authorized'])

    def test_wrong_shapes(self):
        for bad in (None, '', [], False):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'HARD HOLD'):
                r.audit_offline_review(bad)


def mutate(name, patch, recalc=True):
    def case(self):
        data = copy.deepcopy(BASE)
        patch(data)
        if recalc:
            refreshed(data)
        with self.assertRaisesRegex(ValueError, 'R255 DRAFT HARD HOLD'):
            r.audit_offline_review(data)
    setattr(TestR255, 'test_reject_' + name, case)


for field, value in [('state', 'PASS'), ('schema', 'wrong'), ('source_review_groups', 31),
                     ('shared_source_ids', 55), ('article_count', 34),
                     ('citation_count', 1999), ('human_readable_workorders', 561),
                     ('other_citation_occurrences_still_unreviewed', 1439),
                     ('disputed_original_claims', 2)]:
    mutate('receipt_' + field, lambda x, k=field, v=value: x.__setitem__(k, v))
for flag in r.FALSE:
    for label, value in [('true', True), ('string_false', 'false'), ('none', None)]:
        mutate('approval_' + flag + '_' + label,
               lambda x, k=flag, v=value: x.__setitem__(k, v))
for field, value in [('source_scope_approved', True), ('claim_support_approved', True),
                     ('state', 'APPROVED'), ('source_evidence_sha256', 'invalid'),
                     ('workorder_count', 0), ('source_ids', ['wrong-id']),
                     ('priority', 7), ('source_url', 'file:///etc/hosts')]:
    mutate('group_' + field, lambda x, k=field, v=value: x['review_queue'][0].__setitem__(k, v))
for field, value in [('article_n', 36), ('article_slug', '../bad'),
                     ('citation_ordinal', 0), ('source_id', 'alien'),
                     ('context_sha256', '0'*64),
                     ('author_source_use_note_sha256', 'x'),
                     ('review_terms', ['a','a']),
                     ('disputed_original_citation', False),
                     ('source_support_verified', True), ('safety_approved', True)]:
    mutate('workorder_' + field, lambda x, k=field, v=value:
           x['review_queue'][0]['workorders'][0].__setitem__(k, v))
for label, value in [('space', 'https://bad.example/a b'),
                     ('control', 'https://bad.example/a\n'),
                     ('credentials', 'https://user:password@bad.example/'),
                     ('backslash', 'https://bad.example\\evil'),
                     ('broken_port', 'https://bad.example:invalid'),
                     ('javascript', 'javascript:alert(1)'),
                     ('no_host', 'https:///a'),
                     ('overflow', 'https://a.example/' + 'x' * 2100)]:
    mutate('url_' + label, lambda x, v=value:
           x['review_queue'][0].__setitem__('source_url', v))
mutate('drop_group', lambda x: x['review_queue'].pop())
mutate('duplicate_url', lambda x: x['review_queue'][0].__setitem__(
    'source_url', x['review_queue'][1]['source_url']))
mutate('duplicate_source_id', lambda x: x['review_queue'][0]['source_ids'].append(
    x['review_queue'][0]['source_ids'][0]))
mutate('source_id_across_groups', lambda x: x['review_queue'][1]['source_ids'].append(
    x['review_queue'][0]['source_ids'][0]))
mutate('drop_workorder', lambda x: x['review_queue'][0]['workorders'].pop())
mutate('duplicate_citation', lambda x: x['review_queue'][0]['workorders'].append(
    copy.deepcopy(x['review_queue'][0]['workorders'][0])))
mutate('reordered_group', lambda x: x['review_queue'].reverse())
mutate('reordered_claims', lambda x: x['review_queue'][0]['workorders'].reverse())
mutate('modified_excerpt', lambda x: x['review_queue'][0]['workorders'][0].__setitem__(
    'authored_context_excerpt', 'modified and unsupported source context'))
mutate('missing_original_hold', lambda x: x['outside_shared_disputed_workorders'][0].__setitem__(
    'disputed_original_citation', False))
mutate('altered_receipt_checksum', lambda x: x.__setitem__('receipt_sha256', '0' * 64), recalc=False)

mutate('drop_external_hold', lambda x: x['outside_shared_disputed_workorders'].pop())
mutate('duplicate_external_hold', lambda x: x['outside_shared_disputed_workorders'].append(
    copy.deepcopy(x['outside_shared_disputed_workorders'][0])))
mutate('launder_outside_source', lambda x: x['outside_shared_disputed_workorders'][0].__setitem__(
    'source_id', 'start-ready-plan'))
mutate('launder_outside_excerpt', lambda x: x['outside_shared_disputed_workorders'][0].__setitem__(
    'authored_context_excerpt', 'different content'))
mutate('outside_medical_approval', lambda x: x['outside_shared_disputed_workorders'][0].__setitem__(
    'safety_approved', True))
mutate('reorder_outside_held', lambda x: x['outside_shared_disputed_workorders'].reverse())
mutate('forge_external_count', lambda x: x.__setitem__('outside_shared_disputed_claims', 1))
mutate('forge_internal_count', lambda x: x.__setitem__('shared_disputed_claims', 3))


if __name__ == '__main__':
    unittest.main()
