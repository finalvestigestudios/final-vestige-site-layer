"""Isolated synthetic tests; NOT a native full-repository source or safety audit."""
import copy
import importlib.util
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).with_name('r254_readable_claim_workorders_hold.py')
spec = importlib.util.spec_from_file_location('r254', SOURCE)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def fixture():
    ids = ['cdc-find-clean-water', 'start-ready-plan'] + [f'shared-{n:02d}' for n in range(54)]
    url_of_id = {sid: f'https://evidence.example/group-{i // 2 if i < 48 else i - 24:02d}'
                 for i, sid in enumerate(ids)}
    url_map = {f'https://evidence.example/group-{i:02d}': [] for i in range(32)}
    for sid, url in url_of_id.items():
        url_map[url].append(sid)
    global_citations = [(n, ordinal) for n in range(1, 36)
                        for ordinal in range(1, 63 if n == 35 else 58)]
    held = {(7, 30), (7, 48), (20, 55)}
    chosen = set(global_citations[:559]) | held
    # fixed disputed citations are within the initial 559 for Article7, so
    # fill until precisely 562, preserving all 3 original held positions.
    for point in global_citations:
        if len(chosen) >= 562:
            break
        chosen.add(point)
    assert len(chosen) == 562
    articles, assigned, seq = [], {url: [] for url in url_map}, 0
    for n in range(1, 36):
        rows = []
        for ordinal in range(1, 63 if n == 35 else 58):
            if (n, ordinal) in chosen:
                sid = ('cdc-find-clean-water' if n == 7 and ordinal in (30, 48)
                       else 'start-ready-plan' if n == 20 and ordinal == 55
                       else ids[2 + (seq % (len(ids) - 2))])
                seq += 1
            else:
                sid = 'other-source'
            excerpt = f'Unapproved author context from article {n}, citation {ordinal} near source {sid}.'
            row = {'ordinal': ordinal, 'source_id': sid, 'offset': ordinal * 100,
                   'context_excerpt': excerpt, 'context_sha256': r.sha(excerpt),
                   'author_note_sha256': r.sha('note:' + sid),
                   'human_risk_review_terms': ['water'] if ordinal % 3 == 0 else [],
                   'independent_claim_source_verified': False}
            rows.append(row)
            if sid in url_of_id:
                assigned[url_of_id[sid]].append({'n': n, 'article_slug': f'guide-{n}',
                    'contributor_cluster': 'start', 'ordinal': ordinal,
                    'source_id': sid, 'context_sha256': row['context_sha256'],
                    'author_note_sha256': row['author_note_sha256'],
                    'review_terms': row['human_risk_review_terms']})
        articles.append({'n': n, 'slug': f'guide-{n}', 'citation_count': len(rows),
            'body_sha256': r.sha(f'body-{n}'), 'metadata_sha256': r.sha(f'meta-{n}'),
            'claim_context_receipt_sha256': r.sha(r.packed(rows)), 'occurrences': rows})
    queue = []
    for url, group_ids in sorted(url_map.items()):
        matches = assigned[url]
        queue.append({'url': url, 'source_ids': group_ids, 'priority': 'HIGH_CONSEQUENCE_REVIEW',
                      'state': 'PENDING_HUMAN_SOURCE_SCOPE_AND_CLAIM_REVIEW',
                      'source_scope_approved': False, 'claim_support_approved': False,
                      'cited_occurrence_count': len(matches),
                      'matched_citation_evidence': matches,
                      'source_evidence_sha256': r.sha(url)})
    claims = {'state': r.HOLD, 'article_count': 35, 'citation_count': 2000,
              'original_hold_occurrences': 3, 'human_review_required': True,
              'articles': articles, **{flag: False for flag in r.FALSE_CLAIMS}}
    joined = {'schema': 'fv-preparedness-r253-source-context-priority-crosswalk-v1',
              'state': r.HOLD, 'article_count': 35, 'citation_count': 2000,
              'source_rows': 244, 'contributor_cluster_count': 7,
              'totals': {'groups': 32, 'matched_occurrences': 562,
                         'unmatched_occurrences': 1438, 'original_disputed_occurrences': 3},
              'review_queue': queue, **{flag: False for flag in r.FALSE_JOIN}}
    joined['receipt_sha256'] = r.sha(r.packed(joined))
    assert sum(len(x['matched_citation_evidence']) for x in queue) == 562
    return joined, claims


BASE = fixture()


def run(data=None):
    x, y = data if data is not None else BASE
    return r.audit_readable_workorders(x, y)


def update_join(d):
    d[0]['receipt_sha256'] = r.sha(r.packed({k: v for k, v in d[0].items()
                                             if k != 'receipt_sha256'}))


def update_claim(d, index):
    a = d[1]['articles'][index]
    a['claim_context_receipt_sha256'] = r.sha(r.packed(a['occurrences']))


class TestWorkorders(unittest.TestCase):
    def test_complete_35_2000_562_1438(self):
        out = run()
        self.assertEqual((out['source_review_groups'], out['shared_source_ids'],
                          out['article_count'], out['citation_count'],
                          out['human_readable_workorders'],
                          out['other_citation_occurrences_still_unreviewed']),
                         (32, 56, 35, 2000, 562, 1438))
        self.assertEqual(out['state'], r.HOLD)
        self.assertFalse(out['publication_authorized'])

    def test_disputed_claims_with_exact_order(self):
        out = run()
        got = [(w['article_n'], w['citation_ordinal'], w['source_id'])
               for g in out['review_queue'] for w in g['workorders']
               if w['disputed_original_citation']]
        self.assertEqual(sorted(got), sorted(r.HELD))
        self.assertEqual(len(got), 3)

    def test_reader_contexts_preserved_and_non_approved(self):
        out = run()
        for group in out['review_queue']:
            for work in group['workorders']:
                self.assertEqual(work['context_sha256'], r.sha(work['authored_context_excerpt']))
                self.assertFalse(work['source_support_verified'])
                self.assertFalse(work['safety_approved'])

    def test_deterministic_no_mutation(self):
        before = copy.deepcopy(BASE)
        self.assertEqual(run(), run())
        self.assertEqual(BASE, before)

    def test_unmatched_review_groups_preserved(self):
        out = run()
        self.assertEqual(len(out['review_queue']), 32)
        self.assertTrue(all(g['state'].startswith('PENDING_') for g in out['review_queue']))

    def test_wrong_structure(self):
        for bad in (None, [], 'unknown'):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'R254 HARD HOLD'):
                r.audit_readable_workorders(bad, {})


def mutant(name, change, fix_join=True, fix_claim_index=None):
    def test(self):
        d = copy.deepcopy(BASE)
        change(d)
        if fix_claim_index is not None:
            update_claim(d, fix_claim_index)
        if fix_join:
            update_join(d)
        with self.assertRaisesRegex(ValueError, 'R254 HARD HOLD'):
            run(d)
    setattr(TestWorkorders, 'test_mutation_' + name, test)


for flag in r.FALSE_CLAIMS:
    for kind, val in [('true', True), ('none', None), ('string', 'false')]:
        mutant('claims_flag_' + flag + '_' + kind,
               lambda d, f=flag, v=val: d[1].__setitem__(f, v))
for flag in r.FALSE_JOIN:
    for kind, val in [('true', True), ('none', None)]:
        mutant('join_flag_' + flag + '_' + kind,
               lambda d, f=flag, v=val: d[0].__setitem__(f, v))
for field, val in [('state', 'PASS'), ('article_count', 34), ('citation_count', 1999),
                   ('original_hold_occurrences', 2), ('human_review_required', False)]:
    mutant('claims_' + field, lambda d, f=field, v=val: d[1].__setitem__(f, v))
for field, val in [('state', 'PASS'), ('article_count', 34), ('citation_count', 1999),
                   ('source_rows', 243), ('contributor_cluster_count', 6)]:
    mutant('join_' + field, lambda d, f=field, v=val: d[0].__setitem__(f, v))
for field, val in [('groups', 31), ('matched_occurrences', 561),
                   ('unmatched_occurrences', 1439), ('original_disputed_occurrences', 2)]:
    mutant('totals_' + field, lambda d, f=field, v=val: d[0]['totals'].__setitem__(f, v))
for field, val in [('state', 'approved'), ('source_scope_approved', True),
                   ('claim_support_approved', True), ('cited_occurrence_count', 0),
                   ('source_ids', ['different']), ('url', 'https://evidence.example/group-01')]:
    mutant('group_' + field, lambda d, f=field, v=val: d[0]['review_queue'][0].__setitem__(f, v))
for field, val in [('article_slug', 'other-slug'), ('source_id', 'wrong-id'),
                   ('context_sha256', '0' * 64), ('author_note_sha256', '1' * 64),
                   ('ordinal', 300), ('review_terms', ['not-from-claim'])]:
    mutant('match_' + field, lambda d, f=field, v=val: d[0]['review_queue'][0]['matched_citation_evidence'][0].__setitem__(f, v))
for field, val in [('n', 6), ('slug', 18), ('citation_count', 56),
                   ('body_sha256', 'x'), ('metadata_sha256', 'x')]:
    mutant('article_' + field, lambda d, f=field, v=val: d[1]['articles'][7].__setitem__(f, v))
for field, val in [('ordinal', 0), ('source_id', 'bad-claim'),
                   ('context_excerpt', 'changed author excerpt'),
                   ('context_sha256', '0' * 64), ('author_note_sha256', 'notsha'),
                   ('independent_claim_source_verified', True)]:
    mutant('claim_' + field, lambda d, f=field, v=val: d[1]['articles'][4]['occurrences'][1].__setitem__(f, v),
           fix_claim_index=4)
mutant('drop_group', lambda d: d[0]['review_queue'].pop())
mutant('drop_article', lambda d: d[1]['articles'].pop())
mutant('duplicate_claim_link', lambda d: d[0]['review_queue'][0]['matched_citation_evidence'].append(
    copy.deepcopy(d[0]['review_queue'][0]['matched_citation_evidence'][0])))
mutant('drop_claim_link', lambda d: d[0]['review_queue'][0]['matched_citation_evidence'].pop())
mutant('drop_held_citation', lambda d: d[1]['articles'][6]['occurrences'][29].__setitem__('source_id', 'other-source'),
       fix_claim_index=6)
mutant('move_held_citation', lambda d: d[1]['articles'][6]['occurrences'][29].__setitem__('ordinal', 29),
       fix_claim_index=6)
mutant('nonsense_join_receipt', lambda d: d[0].__setitem__('receipt_sha256', '0'*64), fix_join=False)
mutant('reorder_workorders', lambda d: d[0]['review_queue'][0]['matched_citation_evidence'].reverse())

if __name__ == '__main__':
    unittest.main()
