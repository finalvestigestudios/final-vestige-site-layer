"""R34 synthetic, fail-closed contributor-reading custody and review batching."""
from __future__ import annotations
import copy
import hashlib
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import citation_review_batch_gate as g

SMALL = (1, 0, 4, 2, 1, 1)
URL = 'https://example.org/shared-but-not-identical-reading'
H = lambda s: hashlib.sha256(s.encode('utf-8')).hexdigest()


def sign(obj):
    obj['fingerprint_sha256'] = g.sha({k: v for k, v in obj.items() if k != 'fingerprint_sha256'})


def fixture():
    rows, tasks = [], []
    body = H('<article>frozen</article>')
    for i, sid in enumerate(('original-primary', 'other-cluster-fallback')):
        origin = 'cluster-one' if i == 0 else 'cluster-two'
        record = {'id': sid, '_origin': origin, 'url': URL,
                  'supports': 'Full original field reading paragraph ' + str(i),
                  'notes': 'Distinct original reading scope ' + str(i),
                  'verified_on': '2026-10-29', 'publisher': 'Fixture publisher'}
        use = 'Article-specific use with detailed original context ' + str(i)
        offsets = [i*100 + 8, i*100 + 19]
        contexts = [f'Medication history {sid} [CITATION] for independent review',
                    f'Ordinary source account {sid} [CITATION] with limits']
        row = {'slug': 'test-history', 'source_id': sid, 'article_origin': 'cluster-one',
               'source_origin': origin, 'source_url': URL,
               'original_source_record_as_selected': record,
               'original_source_record_sha256': g.sha(record),
               'article_source_use_as_recorded': use,
               'frozen_source_use_sha256': H(use),
               'frozen_article_html_sha256': body,
               'base_fallback_requires_human_scope_review': bool(i),
               'shared_url_group_requires_human_review': True,
               'human_claim_reviewed_by_this_gate': False,
               'human_link_checked_by_this_gate': False,
               'citation_occurrences': 2,
               'citation_token_codepoint_offsets': offsets,
               'all_citation_contexts_for_human_claim_review': contexts}
        rows.append(row)
        for j, (offset, context) in enumerate(zip(offsets, contexts)):
            ref = {'slug': 'test-history', 'source_id': sid,
                   'citation_codepoint_offset': offset, 'original_article_html_sha256': body,
                   'original_source_record_sha256': g.sha(record),
                   'original_source_use_sha256': H(use),
                   'citation_context_sha256': H(context)}
            tasks.append({'claim_ref': ref, 'claim_ref_sha256': g.sha(ref),
                          'citation_context_for_human_review': context,
                          'source_url': URL, 'source_origin': origin,
                          'article_origin': 'cluster-one',
                          'priority': 'REVIEW_FIRST' if j == 0 else 'STANDARD_REVIEW',
                          'triage_tags_not_safety_findings': ['medical-and-dependencies'] if j == 0 else [],
                          'review_state': g.PENDING})
    totals = dict(zip(g.COUNT_KEYS, SMALL))
    p = {'schema_version': 1, 'issue': 136, 'release_state': 'HOLD',
         'machine_authority': 'STRUCTURAL_CITATION_TO_SOURCE_REVIEW_QUEUE_ONLY',
         'may_publish': False, 'independent_QD_approval': False,
         'qualified_safety_clearance': False, 'human_source_reviews_completed': False,
         'source_claim_accuracy_verified': False, 'counts': totals, 'review_queue': rows}
    sign(p)
    q = {'schema_version': 1, 'issue': 136, 'release_state': 'HOLD',
         'machine_authority': 'LOSSLESS_REVIEW_PRIORITIZATION_NOT_SAFETY_APPROVAL',
         'may_publish': False, 'independent_QD_approval': False,
         'qualified_safety_clearance': False, 'human_source_reviews_completed': False,
         'source_claim_accuracy_verified': False, 'counts': totals, 'review_tasks': tasks,
         'parent_R25_fingerprint_sha256': p['fingerprint_sha256']}
    sign(q)
    return p, q


def rebind(p, q):
    sign(p)
    q['parent_R25_fingerprint_sha256'] = p['fingerprint_sha256']
    sign(q)


class Acceptance(unittest.TestCase):
    def test_all_citations_retained(self):
        p, q = fixture(); x = g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual(sum(len(c['citation_review_items']) for c in x['relationship_review_cards']), 4)
    def test_all_relationships_retained(self):
        p,q=fixture(); x=g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual(len(x['relationship_review_cards']),2)
    def test_repeated_url_does_not_dedupe_reading_notes(self):
        p,q=fixture(); x=g.make_batch_index(p,q,expected=SMALL)
        c=x['relationship_review_cards']
        self.assertEqual(c[0]['source_url'],c[1]['source_url'])
        self.assertNotEqual(c[0]['original_source_record_as_selected']['notes'],c[1]['original_source_record_as_selected']['notes'])
    def test_full_reading_depth_preserved(self):
        p,q=fixture(); x=g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual({c['original_source_record_as_selected']['supports'] for c in x['relationship_review_cards']},
                         {r['original_source_record_as_selected']['supports'] for r in p['review_queue']})
    def test_article_specific_source_use_preserved(self):
        p,q=fixture(); x=g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual({c['full_original_article_source_use'] for c in x['relationship_review_cards']},
                         {r['article_source_use_as_recorded'] for r in p['review_queue']})
    def test_all_pending_no_approval(self):
        p,q=fixture(); x=g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual(x['release_state'],'HOLD')
        for flag in ('may_publish','independent_QD_approval','qualified_safety_clearance',
                     'human_source_reviews_completed','source_claim_accuracy_verified'):
            self.assertIs(x[flag],False)
        self.assertTrue(all(c['review_state']=='UNREVIEWED' for c in x['relationship_review_cards']))
        self.assertTrue(all(t['review_state']==g.PENDING for c in x['relationship_review_cards'] for t in c['citation_review_items']))
    def test_deterministic(self):
        p,q=fixture(); self.assertEqual(g.make_batch_index(p,q,expected=SMALL),g.make_batch_index(p,q,expected=SMALL))
    def test_inputs_not_mutated(self):
        p,q=fixture(); before=copy.deepcopy((p,q));g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual((p,q),before)
    def test_full_custody_chain(self):
        p,q=fixture(); x=g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual(x['parent_R25_fingerprint_sha256'],p['fingerprint_sha256'])
        self.assertEqual(x['parent_R33_fingerprint_sha256'],q['fingerprint_sha256'])
        self.assertEqual(x['fingerprint_sha256'],g.sha({k:v for k,v in x.items() if k!='fingerprint_sha256'}))
    def test_batch_size_one(self):
        p,q=fixture(); x=g.make_batch_index(p,q,expected=SMALL,batch_size=1)
        self.assertEqual(len(x['review_batches']),2)
    def test_batch_size_two(self):
        p,q=fixture(); x=g.make_batch_index(p,q,expected=SMALL,batch_size=2)
        self.assertEqual(len(x['review_batches']),1)
    def test_source_url_coordination_without_merging(self):
        p,q=fixture(); x=g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual(len(x['shared_url_coordination_only']),1)
        self.assertEqual(len(x['shared_url_coordination_only'][0]['distinct_relationship_ids']),2)
    def test_source_url_tracks_remain_unreviewed(self):
        p,q=fixture();x=g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual(x['shared_url_coordination_only'][0]['review_state'],'UNREVIEWED')
    def test_fallback_flag_preserved(self):
        p,q=fixture();x=g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual(sum(c['base_fallback_requires_human_scope_review'] for c in x['relationship_review_cards']),1)
    def test_offsets_preserved(self):
        p,q=fixture();x=g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual(sorted(t['claim_ref']['citation_codepoint_offset'] for c in x['relationship_review_cards'] for t in c['citation_review_items']), [8,19,108,119])
    def test_batch_coverage(self):
        p,q=fixture();x=g.make_batch_index(p,q,expected=SMALL,batch_size=1)
        ids=[v for b in x['review_batches'] for v in b['relationship_ids']]
        self.assertEqual(set(ids),{c['relationship_id_sha256'] for c in x['relationship_review_cards']})
    def test_default_production_totals_reject_small_fixture(self):
        p,q=fixture()
        with self.assertRaises(g.BatchHold): g.make_batch_index(p,q)
    def test_unicode_notes_preserved(self):
        p,q=fixture();r=p['review_queue'][0];r['original_source_record_as_selected']['notes']='Café — mémoire ∑';r['original_source_record_sha256']=g.sha(r['original_source_record_as_selected']);
        for t in q['review_tasks'][:2]:
            t['claim_ref']['original_source_record_sha256']=r['original_source_record_sha256'];t['claim_ref_sha256']=g.sha(t['claim_ref'])
        rebind(p,q);x=g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual(x['relationship_review_cards'][0]['original_source_record_as_selected']['notes'],'Café — mémoire ∑')
    def test_no_external_writes(self):
        p,q=fixture();g.make_batch_index(p,q,expected=SMALL)
        self.assertEqual(2,len(p['review_queue']))


MUTATIONS = {
    'packet_not_dict':lambda p,q:('bad',q),
    'queue_not_dict':lambda p,q:(p,'bad'),
    'packet_wrong_issue':lambda p,q:p.update(issue=135),
    'queue_wrong_issue':lambda p,q:q.update(issue=135),
    'packet_schema_two':lambda p,q:p.update(schema_version=2),
    'queue_schema_two':lambda p,q:q.update(schema_version=2),
    'packet_published':lambda p,q:p.update(release_state='PUBLISHED'),
    'queue_published':lambda p,q:q.update(release_state='PUBLISHED'),
    'packet_publish_true':lambda p,q:p.update(may_publish=True),
    'queue_publish_true':lambda p,q:q.update(may_publish=True),
    'packet_publish_zero':lambda p,q:p.update(may_publish=0),
    'queue_publish_zero':lambda p,q:q.update(may_publish=0),
    'packet_qd_pass':lambda p,q:p.update(independent_QD_approval=True),
    'queue_qd_pass':lambda p,q:q.update(independent_QD_approval=True),
    'packet_medical_pass':lambda p,q:p.update(qualified_safety_clearance=True),
    'queue_medical_pass':lambda p,q:q.update(qualified_safety_clearance=True),
    'packet_human_complete':lambda p,q:p.update(human_source_reviews_completed=True),
    'queue_human_complete':lambda p,q:q.update(human_source_reviews_completed=True),
    'packet_accuracy_pass':lambda p,q:p.update(source_claim_accuracy_verified=True),
    'queue_accuracy_pass':lambda p,q:q.update(source_claim_accuracy_verified=True),
    'packet_authority_forgery':lambda p,q:p.update(machine_authority='PUBLISH'),
    'queue_authority_forgery':lambda p,q:q.update(machine_authority='PUBLISH'),
    'packet_corrupt_fingerprint':lambda p,q:p.update(fingerprint_sha256='a'*64),
    'queue_corrupt_fingerprint':lambda p,q:q.update(fingerprint_sha256='a'*64),
    'packet_fingerprint_missing':lambda p,q:p.pop('fingerprint_sha256'),
    'queue_fingerprint_missing':lambda p,q:q.pop('fingerprint_sha256'),
    'packet_totals_wrong':lambda p,q:p['counts'].update(citations=999),
    'queue_totals_wrong':lambda p,q:q['counts'].update(relationships=999),
    'missing_relationship':lambda p,q:p['review_queue'].pop(),
    'extra_relationship':lambda p,q:p['review_queue'].append(copy.deepcopy(p['review_queue'][0])),
    'duplicate_relationship':lambda p,q:p['review_queue'].__setitem__(1,copy.deepcopy(p['review_queue'][0])),
    'missing_claim':lambda p,q:q['review_tasks'].pop(),
    'extra_claim':lambda p,q:q['review_tasks'].append(copy.deepcopy(q['review_tasks'][0])),
    'duplicate_claim':lambda p,q:q['review_tasks'].__setitem__(1,copy.deepcopy(q['review_tasks'][0])),
    'source_use_tampered':lambda p,q:p['review_queue'][0].update(article_source_use_as_recorded='new unsupported source use'),
    'original_supports_tampered':lambda p,q:p['review_queue'][0]['original_source_record_as_selected'].update(supports='Made up'),
    'source_notes_tampered':lambda p,q:p['review_queue'][0]['original_source_record_as_selected'].update(notes='Made up'),
    'source_id_tampered':lambda p,q:p['review_queue'][0]['original_source_record_as_selected'].update(id='wrong'),
    'source_url_tampered':lambda p,q:p['review_queue'][0]['original_source_record_as_selected'].update(url='https://fake.example'),
    'source_origin_tampered':lambda p,q:p['review_queue'][0]['original_source_record_as_selected'].update(_origin='wrong'),
    'source_record_missing':lambda p,q:p['review_queue'][0].pop('original_source_record_as_selected'),
    'source_use_missing':lambda p,q:p['review_queue'][0].pop('article_source_use_as_recorded'),
    'blank_source_use':lambda p,q:p['review_queue'][0].update(article_source_use_as_recorded='  '),
    'blank_original_supports':lambda p,q:p['review_queue'][0]['original_source_record_as_selected'].update(supports='  '),
    'wrong_body_hash':lambda p,q:p['review_queue'][0].update(frozen_article_html_sha256='invalid'),
    'missing_url':lambda p,q:p['review_queue'][0].pop('source_url'),
    'fallback_count_drift':lambda p,q:p['review_queue'][1].update(base_fallback_requires_human_scope_review=False),
    'fallback_as_int':lambda p,q:p['review_queue'][1].update(base_fallback_requires_human_scope_review=1),
    'shared_url_flag_as_int':lambda p,q:p['review_queue'][0].update(shared_url_group_requires_human_review=1),
    'source_claim_review_forged':lambda p,q:p['review_queue'][0].update(human_claim_reviewed_by_this_gate=True),
    'source_link_review_forged':lambda p,q:p['review_queue'][0].update(human_link_checked_by_this_gate=True),
    'offsets_lost':lambda p,q:p['review_queue'][0].update(citation_token_codepoint_offsets=[]),
    'offset_duplicate':lambda p,q:p['review_queue'][0].update(citation_token_codepoint_offsets=[8,8]),
    'offset_negative':lambda p,q:p['review_queue'][0].update(citation_token_codepoint_offsets=[-1,19]),
    'offset_string':lambda p,q:p['review_queue'][0].update(citation_token_codepoint_offsets=['8',19]),
    'context_removed':lambda p,q:p['review_queue'][0]['all_citation_contexts_for_human_claim_review'].pop(),
    'context_forged':lambda p,q:p['review_queue'][0]['all_citation_contexts_for_human_claim_review'].__setitem__(0,'Different [CITATION] wording'),
    'claim_ref_hash_forged':lambda p,q:q['review_tasks'][0]['claim_ref'].update(original_source_record_sha256='b'*64),
    'claim_context_forged':lambda p,q:q['review_tasks'][0].update(citation_context_for_human_review='Other [CITATION] context'),
    'claim_source_url_forged':lambda p,q:q['review_tasks'][0].update(source_url='https://fake.example'),
    'claim_article_origin_forged':lambda p,q:q['review_tasks'][0].update(article_origin='other'),
    'claim_source_origin_forged':lambda p,q:q['review_tasks'][0].update(source_origin='other'),
    'claim_review_approved':lambda p,q:q['review_tasks'][0].update(review_state='APPROVED'),
    'claim_priority_approved':lambda p,q:q['review_tasks'][0].update(priority='SAFE'),
    'claim_offset_forged':lambda p,q:q['review_tasks'][0]['claim_ref'].update(citation_codepoint_offset=999),
    'claim_slug_forged':lambda p,q:q['review_tasks'][0]['claim_ref'].update(slug='other'),
    'claim_source_id_forged':lambda p,q:q['review_tasks'][0]['claim_ref'].update(source_id='other'),
    'claim_tag_invalid':lambda p,q:q['review_tasks'][0].update(triage_tags_not_safety_findings='approved'),
    'review_queue_none':lambda p,q:p.update(review_queue=None),
    'review_tasks_none':lambda p,q:q.update(review_tasks=None),
}


class Adversarial(unittest.TestCase):
    pass


def adversarial_case(name, mutate):
    def test(self):
        p,q=fixture()
        changes=mutate(p,q)
        if type(changes) is tuple:
            p,q=changes
        # Resign to verify substantive custody, not just invalid parent digest;
        # explicit corrupted/missing-fingerprint tests retain their corruption.
        if type(p) is dict and type(q) is dict:
            if name not in ('packet_corrupt_fingerprint','queue_corrupt_fingerprint',
                            'packet_fingerprint_missing','queue_fingerprint_missing'):
                rebind(p,q)
        with self.assertRaises((g.BatchHold, ValueError, TypeError),msg=name):
            g.make_batch_index(p,q,expected=SMALL)
    return test

for name,mutation in MUTATIONS.items():
    setattr(Adversarial,'test_'+name,adversarial_case(name,mutation))


class ParameterGuards(unittest.TestCase):
    def test_zero_size(self):
        p,q=fixture()
        with self.assertRaises(g.BatchHold):g.make_batch_index(p,q,expected=SMALL,batch_size=0)
    def test_negative_size(self):
        p,q=fixture()
        with self.assertRaises(g.BatchHold):g.make_batch_index(p,q,expected=SMALL,batch_size=-1)
    def test_large_size(self):
        p,q=fixture()
        with self.assertRaises(g.BatchHold):g.make_batch_index(p,q,expected=SMALL,batch_size=51)
    def test_bool_size(self):
        p,q=fixture()
        with self.assertRaises(g.BatchHold):g.make_batch_index(p,q,expected=SMALL,batch_size=True)
    def test_bad_expected(self):
        p,q=fixture()
        with self.assertRaises(g.BatchHold):g.make_batch_index(p,q,expected=(1,))
    def test_bool_expected(self):
        p,q=fixture()
        with self.assertRaises(g.BatchHold):g.make_batch_index(p,q,expected=(1,0,4,2,True,1))


if __name__ == '__main__':unittest.main()
