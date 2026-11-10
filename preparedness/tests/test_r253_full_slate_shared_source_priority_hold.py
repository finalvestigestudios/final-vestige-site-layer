"""Synthetic, isolated R253 source-to-claim join regression tests; NOT native 35-article QA."""
import copy
import hashlib
import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'tools/r253_full_slate_shared_source_priority_hold.py'
SPEC = importlib.util.spec_from_file_location('r253', SCRIPT)
r = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def fixture():
    queue = []
    for i in range(32):
        source_id = 'cdc-find-clean-water' if i == 0 else 'start-ready-plan' if i == 1 else f'source-{i:02d}'
        queue.append({'url': f'https://source.example/{i:02d}', 'status': r.PENDING,
                      'human_scope_review_required': True, 'all_human_link_checked': False,
                      'source_ids': [source_id], 'row_count': 2,
                      'scope_variants': 2, 'verification_date_variants': 2,
                      'origins': ['base', r.SEQUENCE[i % 7] if hasattr(r, 'SEQUENCE') else sorted(r.SEVEN)[i % 7]],
                      'evidence_sha256': sha(f'group {i}')})
    sources = {'state': r.HOLD, 'raw_source_rows': 244, 'shared_url_groups': 32,
               'pending_human_groups': 32, 'review_queue': queue,
               **{f: False for f in r.FALSE_FLAGS_R235}}
    roster = []
    articles = []
    for n in range(1, 36):
        slug = f'guide-{n}'
        roster.append({'n': n, 'slug': slug, 'source_cluster': sorted(r.SEVEN)[(n-1) % 7]})
        count = 62 if n == 35 else 57
        entries = []
        for ordinal in range(1, count+1):
            i = (ordinal + n) % 32
            sid = queue[i]['source_ids'][0] if ordinal % 2 else 'unique-source'
            if n == 7 and ordinal in (1, 2):
                sid = 'cdc-find-clean-water'
            if n == 20 and ordinal == 1:
                sid = 'start-ready-plan'
            if sid == 'cdc-find-clean-water' and (n != 7 or ordinal not in (1,2)):
                sid = 'unique-source'
            if sid == 'start-ready-plan' and (n != 20 or ordinal != 1):
                sid = 'unique-source'
            text = f'Source claim context for article {n}, citation {ordinal}, source {sid}'
            entries.append({'ordinal': ordinal, 'source_id': sid,
                'offset': ordinal*80, 'context_excerpt': text,
                'context_sha256': sha(text), 'author_note_sha256': sha(f'note {n}:{sid}'),
                'human_risk_review_terms': ['water'] if ordinal % 3 == 0 else [],
                'independent_claim_source_verified': False})
        articles.append({'n': n, 'slug': slug, 'citation_count': count,
            'body_sha256': sha(f'body-{n}'), 'metadata_sha256': sha(f'meta-{n}'),
            'claim_context_receipt_sha256': sha(f'claims-{n}'), 'occurrences': entries})
    claims = {'state': r.HOLD, 'article_count': 35, 'citation_count': 2000,
              'original_hold_occurrences': 3, 'human_review_required': True,
              'articles': articles, **{f: False for f in r.FALSE_FLAGS_R237}}
    return sources, claims, roster


BASE = fixture()


def run(inp=None):
    src, claims, roster = inp if inp is not None else BASE
    return r.audit_join(src, claims, roster)


class TestJoin(unittest.TestCase):
    def test_all_35_articles_seven_contributors_and_2000_claims(self):
        a = run()
        self.assertEqual((a['article_count'], a['citation_count'], a['contributor_cluster_count']), (35, 2000, 7))
        self.assertEqual(a['totals']['groups'], 32)
        self.assertEqual(a['totals']['original_disputed_occurrences'], 3)
        self.assertEqual(a['totals']['matched_occurrences'] + a['totals']['unmatched_occurrences'], 2000)
        self.assertFalse(a['publication_authorized'])
        self.assertFalse(a['independent_qd_pass'])
        self.assertEqual(a['state'], r.HOLD)

    def test_determinism_and_no_input_mutation(self):
        before = copy.deepcopy(BASE)
        self.assertEqual(run(), run())
        self.assertEqual(BASE, before)

    def test_citation_evidence_not_marked_reviewed(self):
        a = run()
        self.assertTrue(any(q['matched_citation_evidence'] for q in a['review_queue']))
        self.assertTrue(all(q['source_scope_approved'] is False and q['claim_support_approved'] is False for q in a['review_queue']))
        self.assertEqual([q['url'] for q in a['review_queue']], sorted(q['url'] for q in a['review_queue']))
        self.assertTrue(any(q['priority'] == 'HIGH_CONSEQUENCE_REVIEW' for q in a['review_queue']))

    def test_unmapped_remains_held(self):
        inp = copy.deepcopy(BASE)
        inp[0]['review_queue'][31]['source_ids'] = ['unseen-id']
        output = run(inp)
        self.assertEqual(output['review_queue'][-1]['priority'], 'UNMAPPED_VARIANT_REVIEW')
        self.assertTrue(output['review_queue'][-1]['state'].startswith('PENDING_'))

    def test_bad_structures(self):
        for idx in range(3):
            inp = list(BASE)
            inp[idx] = None
            with self.subTest(idx=idx), self.assertRaisesRegex(ValueError, 'R253 HARD HOLD'):
                run(inp)

    def test_original_hold_count_drift(self):
        inp = copy.deepcopy(BASE)
        inp[1]['articles'][6]['occurrences'][0]['source_id'] = 'unique-source'
        with self.assertRaisesRegex(ValueError, 'historically unreviewed'):
            run(inp)

    def test_distinct_citation_context_sha_enforced(self):
        inp = copy.deepcopy(BASE)
        inp[1]['articles'][4]['occurrences'][5]['context_excerpt'] = 'tampered context'
        with self.assertRaisesRegex(ValueError, 'checksum'):
            run(inp)

    def test_cited_group_mapping_without_reassigning_source_ids(self):
        a = run()
        cited = [(x['n'], x['ordinal'], x['source_id']) for q in a['review_queue'] for x in q['matched_citation_evidence']]
        self.assertEqual(len(cited), len(set(cited)))
        self.assertIn((7, 1, 'cdc-find-clean-water'), cited)
        self.assertIn((20, 1, 'start-ready-plan'), cited)


def mutant(name, make):
    def check(self):
        inp = copy.deepcopy(BASE)
        make(inp)
        with self.assertRaisesRegex((ValueError), 'R253 HARD HOLD'):
            run(inp)
    setattr(TestJoin, 'test_mutant_' + name, check)


for field in r.FALSE_FLAGS_R235:
    for kind, value in [('true', True), ('none', None), ('string', 'false')]:
        mutant('source_flag_'+field+'_'+kind, lambda d, field=field, value=value: d[0].__setitem__(field, value))
for field in r.FALSE_FLAGS_R237:
    for kind, value in [('true', True), ('none', None), ('string', 'false')]:
        mutant('claim_flag_'+field+'_'+kind, lambda d, field=field, value=value: d[1].__setitem__(field, value))
for field, bad in [('state', 'PUBLISHED'), ('raw_source_rows', 243),
                   ('shared_url_groups', 31), ('pending_human_groups', 31)]:
    mutant('sources_'+field, lambda d, field=field, bad=bad: d[0].__setitem__(field, bad))
for field, bad in [('state', 'PASS'), ('article_count', 34), ('citation_count', 1999),
                   ('original_hold_occurrences', 2), ('human_review_required', False)]:
    mutant('claims_'+field, lambda d, field=field, bad=bad: d[1].__setitem__(field, bad))
for field, bad in [('status', 'resolved'), ('human_scope_review_required', False),
                   ('all_human_link_checked', True), ('evidence_sha256', '0'),
                   ('source_ids', ['bad id']), ('row_count', 0),
                   ('scope_variants', 0), ('verification_date_variants', 0),
                   ('origins', ['unknown'])]:
    mutant('group_'+field, lambda d, field=field, bad=bad: d[0]['review_queue'][3].__setitem__(field, bad))
for field, bad in [('n', 50), ('slug', 'other-guide'), ('citation_count', 2),
                   ('body_sha256', 'not-sha'), ('metadata_sha256', ''),
                   ('claim_context_receipt_sha256', 'hash')]:
    mutant('article_'+field, lambda d, field=field, bad=bad: d[1]['articles'][10].__setitem__(field, bad))
for field, bad in [('ordinal', 199), ('source_id', 'BAD'), ('offset', -1),
                   ('context_excerpt', 'x'), ('context_sha256', 'no'),
                   ('author_note_sha256', 'no'), ('human_risk_review_terms', 'water'),
                   ('independent_claim_source_verified', True)]:
    mutant('occurrence_'+field, lambda d, field=field, bad=bad: d[1]['articles'][8]['occurrences'][3].__setitem__(field, bad))
mutant('duplicate_source_group', lambda d: d[0]['review_queue'][5].__setitem__('url', d[0]['review_queue'][6]['url']))
mutant('same_source_id_two_groups', lambda d: d[0]['review_queue'][5].__setitem__('source_ids', d[0]['review_queue'][6]['source_ids']))
mutant('missing_group', lambda d: d[0]['review_queue'].pop())
mutant('missing_article', lambda d: d[1]['articles'].pop())
mutant('missing_cluster', lambda d: d[2][0].__setitem__('source_cluster', 'unknown'))
mutant('duplicate_slug', lambda d: d[2][1].__setitem__('slug', d[2][0]['slug']))
mutant('missing_citation', lambda d: d[1]['articles'][0]['occurrences'].pop())

if __name__ == '__main__':
    unittest.main()
