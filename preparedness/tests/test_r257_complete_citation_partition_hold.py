"""Synthetic regression fixtures ONLY: not authentic full-corpus or medical-source verification."""
import copy
import importlib.util
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / 'tools/r257_complete_citation_partition_hold.py'
spec = importlib.util.spec_from_file_location('r257', SRC)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def fixture():
    positions = [(n, o) for n in range(1, 36)
                 for o in range(1, 63 if n == 35 else 58)]
    selected = [p for p in positions if p not in ((7, 30), (7, 48), (20, 55))][:561]
    selected.append((20, 55))
    selected = sorted(selected)
    assert len(positions) == 2000 and len(selected) == 562
    chosen = set(selected)
    ids = ['start-ready-plan'] + [f'shared-{x}' for x in range(55)]
    groups = [{'source_url': f'https://evidence.example/source-{x:02d}',
               'source_ids': [], 'workorders': [], 'workorder_count': 0,
               'state': 'PENDING_HUMAN_SOURCE_AND_CLAIM_REVIEW',
               'source_scope_approved': False, 'claim_support_approved': False}
              for x in range(32)]
    for i, sid in enumerate(ids):
        groups[i // 2 if i < 48 else i - 24]['source_ids'].append(sid)
    slot_to_id = {p: ids[i % len(ids)] for i, p in enumerate(selected)}
    slot_to_id[20, 55] = 'start-ready-plan'
    slot_to_id[7, 30] = slot_to_id[7, 48] = 'cdc-find-clean-water'
    articles, external = [], []
    for n in range(1, 36):
        rows = []
        for ordinal in range(1, 63 if n == 35 else 58):
            point = n, ordinal
            sid = slot_to_id.get(point, f'nonshared-{n % 11}')
            excerpt = f'Original passage A{n} cite {ordinal} — status STILL UNREVIEWED.'
            row = {'ordinal': ordinal, 'source_id': sid,
                   'context_excerpt': excerpt, 'context_sha256': r.digest(excerpt),
                   'author_note_sha256': r.digest('author note ' + sid),
                   'independent_claim_source_verified': False,
                   'human_risk_review_terms': ['human_review']}
            rows.append(row)
            if point in chosen:
                gr = next(g for g in groups if sid in g['source_ids'])
                gr['workorders'].append({
                    'article_n': n, 'article_slug': f'article-{n}',
                    'citation_ordinal': ordinal, 'source_id': sid,
                    'authored_context_excerpt': excerpt,
                    'context_sha256': row['context_sha256'],
                    'author_source_use_note_sha256': row['author_note_sha256'],
                    'review_terms': ['human_review'],
                    'disputed_original_citation': point == (20, 55),
                    'source_support_verified': False, 'safety_approved': False})
            elif point in ((7, 30), (7, 48)):
                external.append({'article_n': n, 'article_slug': f'article-{n}',
                    'citation_ordinal': ordinal, 'source_id': sid,
                    'authored_context_excerpt': excerpt,
                    'context_sha256': row['context_sha256'],
                    'author_source_use_note_sha256': row['author_note_sha256'],
                    'review_terms': ['human_review'],
                    'disputed_original_citation': True,
                    'source_support_verified': False, 'safety_approved': False})
        articles.append({'n': n, 'slug': f'article-{n}', 'occurrences': rows,
                         'citation_count': len(rows),
                         'body_sha256': r.digest('body' + str(n)),
                         'metadata_sha256': r.digest('meta' + str(n)),
                         'claim_context_receipt_sha256': r.digest(r.canonical(rows))})
    for group in groups:
        group['workorders'].sort(key=lambda w: (w['article_n'], w['citation_ordinal']))
        group['workorder_count'] = len(group['workorders'])
    claims = {'state': r.HOLD, 'articles': articles, 'article_count': 35,
              'citation_count': 2000, 'original_hold_occurrences': 3,
              'human_review_required': True,
              **{key: False for key in ('release_authorized', 'independent_qd_pass',
              'source_review_approved', 'medical_safety_verified',
              'claim_evidence_adjudicated')}}
    work = {'schema': r.UPSTREAM, 'state': r.HOLD,
            'article_count': 35, 'citation_count': 2000,
            'source_review_groups': 32, 'shared_source_ids': 56,
            'human_readable_workorders': 562,
            'other_citation_occurrences_still_unreviewed': 1438,
            'disputed_original_claims': 3,
            'shared_disputed_claims': 1, 'outside_shared_disputed_claims': 2,
            'outside_shared_disputed_workorders': external, 'review_queue': groups,
            **{key: False for key in r.FALSE}}
    work['receipt_sha256'] = r.digest(r.canonical(work))
    return claims, work


BASE = fixture()


def refresh_claim(claims, n):
    a = claims['articles'][n - 1]
    a['claim_context_receipt_sha256'] = r.digest(r.canonical(a['occurrences']))


def refresh_work(work):
    work['receipt_sha256'] = r.digest(r.canonical({
        k: v for k, v in work.items() if k != 'receipt_sha256'}))


class TestCompletePartition(unittest.TestCase):
    def test_all_2000_original_citations_partition_exactly_once(self):
        result = r.audit_full_partition(*BASE)
        self.assertEqual((result['citation_count'], result['shared_workorders'],
                          result['nonshared_workorders']), (2000, 562, 1438))
        self.assertEqual(len(result['unreviewed_nonshared_queue']), 1438)
        self.assertEqual(result['state'], r.HOLD)
        for flag in r.FALSE:
            self.assertIs(result[flag], False)

    def test_three_disputed_citations_preserved_across_partition(self):
        result = r.audit_full_partition(*BASE)
        self.assertEqual([(x['article_n'], x['citation_ordinal'])
                          for x in result['unreviewed_nonshared_queue'] if x['original_dispute']],
                         [(7, 30), (7, 48)])
        self.assertEqual((result['shared_disputes'], result['nonshared_disputes']), (1, 2))

    def test_no_input_mutation_and_determinism(self):
        original = copy.deepcopy(BASE)
        a, b = r.audit_full_partition(*BASE), r.audit_full_partition(*BASE)
        self.assertEqual(a, b)
        self.assertEqual(BASE, original)
        self.assertEqual(a['receipt_sha256'], r.digest(r.canonical({
            k: v for k, v in a.items() if k != 'receipt_sha256'})))

    def test_queue_evidence_not_approval(self):
        result = r.audit_full_partition(*BASE)
        for row in result['unreviewed_nonshared_queue']:
            self.assertFalse(row['source_support_verified'])
            self.assertFalse(row['safety_approved'])
            self.assertEqual(row['context_sha256'], r.digest(row['authored_context_excerpt']))

    def test_nontyped_input(self):
        for bad in (None, [], False, 'words'):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'HARD HOLD'):
                r.audit_full_partition(bad, {})


def mutant(name, change, fix_claim=(), fix_receipt=True):
    def case(self):
        c, w = copy.deepcopy(BASE)
        change(c, w)
        for n in fix_claim:
            refresh_claim(c, n)
        if fix_receipt:
            refresh_work(w)
        with self.assertRaisesRegex(ValueError, 'R257 DRAFT HARD HOLD'):
            r.audit_full_partition(c, w)
    setattr(TestCompletePartition, 'test_mutation_' + name, case)


for fld, val in [('schema','OTHER'), ('state','PASS'), ('article_count',34),
                 ('citation_count',1999), ('source_review_groups',31),
                 ('shared_source_ids',55), ('human_readable_workorders',561),
                 ('other_citation_occurrences_still_unreviewed',1439),
                 ('disputed_original_claims',2), ('shared_disputed_claims',2),
                 ('outside_shared_disputed_claims',1)]:
    mutant('R254_'+fld, lambda c,w,f=fld,v=val: w.__setitem__(f,v))
for fld,val in [('state','APPROVED'), ('article_count',34), ('citation_count',1999),
                ('original_hold_occurrences',2), ('human_review_required',False)]:
    mutant('R237_'+fld, lambda c,w,f=fld,v=val: c.__setitem__(f,v))
for fld in r.FALSE:
    mutant('R254_unsafe_'+fld, lambda c,w,f=fld: w.__setitem__(f,True))
for fld in ('release_authorized', 'independent_qd_pass',
            'source_review_approved', 'medical_safety_verified',
            'claim_evidence_adjudicated'):
    mutant('R237_unsafe_'+fld, lambda c,w,f=fld: c.__setitem__(f,True))
for fld,val in [('n',4),('slug','article-2'),('citation_count',56),
                ('body_sha256','abc'),('metadata_sha256','abc')]:
    mutant('article_'+fld,lambda c,w,f=fld,v=val: c['articles'][0].__setitem__(f,v))
for fld,val in [('ordinal',2),('source_id','another-source'),
                ('context_excerpt','different authored content'),
                ('context_sha256','0'*64),('author_note_sha256','bad'),
                ('independent_claim_source_verified',True),
                ('human_risk_review_terms',['not-original'])]:
    mutant('original_'+fld,lambda c,w,f=fld,v=val: c['articles'][6]['occurrences'][29].__setitem__(f,v), fix_claim=(7,))
for fld,val in [('state','APPROVED'),('source_scope_approved',True),
                ('claim_support_approved',True), ('workorder_count',0)]:
    mutant('group_'+fld,lambda c,w,f=fld,v=val: w['review_queue'][0].__setitem__(f,v))
for fld,val in [('article_slug','other'),('source_id','other'),
                ('authored_context_excerpt','different excerpt'),
                ('context_sha256','0'*64),('author_source_use_note_sha256','x'),
                ('source_support_verified',True),('safety_approved',True),
                ('disputed_original_citation',True)]:
    mutant('shared_'+fld,lambda c,w,f=fld,v=val: w['review_queue'][0]['workorders'][0].__setitem__(f,v))
for fld,val in [('article_slug','other'), ('source_id','other'),
                ('authored_context_excerpt','different'),('context_sha256','0'*64),
                ('author_source_use_note_sha256','bad'),
                ('disputed_original_citation',False),
                ('source_support_verified',True),('safety_approved',True)]:
    mutant('external_'+fld,lambda c,w,f=fld,v=val: w['outside_shared_disputed_workorders'][0].__setitem__(f,v))
mutant('remove_original_article', lambda c,w: c['articles'].pop())
mutant('remove_original_citation',lambda c,w: c['articles'][0]['occurrences'].pop(), fix_claim=(1,))
mutant('drop_shared_row',lambda c,w: w['review_queue'][0]['workorders'].pop())
mutant('duplicate_shared_row',lambda c,w: w['review_queue'][0]['workorders'].append(
    copy.deepcopy(w['review_queue'][0]['workorders'][0])))
mutant('drop_external_hold',lambda c,w: w['outside_shared_disputed_workorders'].pop())
mutant('duplicate_external_hold',lambda c,w: w['outside_shared_disputed_workorders'].append(
    copy.deepcopy(w['outside_shared_disputed_workorders'][0])))
mutant('bad_receipt',lambda c,w: w.__setitem__('receipt_sha256','0'*64),fix_receipt=False)

if __name__ == '__main__':
    unittest.main()
