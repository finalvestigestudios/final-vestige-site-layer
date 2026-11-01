"""R35 synthetic evidence-bound reviewer intake tests; NO real source edits."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import citation_review_batch_gate as r34
import citation_review_handoff_gate as gate
from test_r34_citation_review_batches import fixture, SMALL


def valid():
    p, q = fixture()
    return r34.make_batch_index(p, q, expected=SMALL, batch_size=1)


def resign(doc):
    doc['fingerprint_sha256'] = gate.digest({k:v for k,v in doc.items()
                                              if k != 'fingerprint_sha256'})


class IntactHandoff(unittest.TestCase):
    def setUp(self):
        self.parent = valid()
        self.h = gate.make_handoff(self.parent, expected=SMALL)

    def test_source_one_to_one(self):
        self.assertEqual(2, len(self.h['source_scope_review_forms']))
    def test_claim_one_to_one(self):
        self.assertEqual(4, len(self.h['claim_occurrence_review_forms']))
    def test_fallback_one_to_one(self):
        self.assertEqual(1, len(self.h['base_fallback_review_forms']))
    def test_used_shared_url_not_conflated_with_global(self):
        self.assertEqual(1, len(self.h['shared_url_review_forms_for_used_sources_only']))
    def test_all_source_cards_covered(self):
        self.assertEqual({x['relationship_id_sha256'] for x in self.parent['relationship_review_cards']},
                         {x['relationship_id_sha256'] for x in self.h['source_scope_review_forms']})
    def test_all_claim_occurrences_covered(self):
        old = {x['claim_ref_sha256'] for card in self.parent['relationship_review_cards']
               for x in card['citation_review_items']}
        new = {x['claim_ref_sha256'] for x in self.h['claim_occurrence_review_forms']}
        self.assertEqual(old, new)
    def test_all_original_contexts_retained(self):
        old = {x['original_context'] for card in self.parent['relationship_review_cards']
               for x in card['citation_review_items']}
        new = {x['exact_original_context'] for x in self.h['claim_occurrence_review_forms']}
        self.assertEqual(old, new)
    def test_original_supports_retained(self):
        self.assertEqual({x['original_source_record_as_selected']['supports']
                          for x in self.parent['relationship_review_cards']},
                         {x['unabridged_original_source_record']['supports']
                          for x in self.h['source_scope_review_forms']})
    def test_original_notes_distinct_on_shared_url(self):
        rows = self.h['source_scope_review_forms']
        self.assertEqual(rows[0]['source_url'], rows[1]['source_url'])
        self.assertNotEqual(rows[0]['unabridged_original_source_record']['notes'],
                            rows[1]['unabridged_original_source_record']['notes'])
    def test_original_article_use_retained(self):
        self.assertEqual({x['full_original_article_source_use']
                          for x in self.parent['relationship_review_cards']},
                         {x['unabridged_article_specific_source_use']
                          for x in self.h['source_scope_review_forms']})
    def test_no_citation_approved(self):
        self.assertTrue(all(x['review_state'] == 'NOT_STARTED'
                            for x in self.h['claim_occurrence_review_forms']))
    def test_no_source_approved(self):
        self.assertTrue(all(x['review_state'] == 'NOT_STARTED'
                            for x in self.h['source_scope_review_forms']))
    def test_no_fallback_approved(self):
        self.assertTrue(all(x['review_state'] == 'NOT_STARTED'
                            for x in self.h['base_fallback_review_forms']))
    def test_no_shared_url_approved(self):
        self.assertTrue(all(x['review_state'] == 'NOT_STARTED'
                            for x in self.h['shared_url_review_forms_for_used_sources_only']))
    def test_human_fields_null(self):
        for r in self.h['claim_occurrence_review_forms']:
            self.assertIsNone(r['human_claim_to_source_support_assessment'])
            self.assertIsNone(r['human_exact_page_or_section_locator'])
            self.assertIsNone(r['independent_qualified_safety_review'])
    def test_source_human_fields_null(self):
        for r in self.h['source_scope_review_forms']:
            self.assertIsNone(r['human_link_access_date'])
            self.assertIsNone(r['human_source_reading_scope_assessment'])
    def test_no_false_clearances(self):
        self.assertEqual(self.h['release_state'], 'HOLD')
        for k in gate.HOLD_FLAGS:
            self.assertIs(self.h[k], False)
    def test_review_priority_is_not_safety_verdict(self):
        self.assertEqual({'REVIEW_FIRST', 'STANDARD_REVIEW'},
                         {r['triage_priority_not_verdict']
                          for r in self.h['claim_occurrence_review_forms']})
    def test_priority_total_reconciled(self):
        counts = self.h['review_task_counts']
        self.assertEqual(4, counts['review_first_claims_unreviewed'] +
                         counts['standard_claims_unreviewed'])
    def test_human_review_scope_not_url_deduped(self):
        ids = self.h['shared_url_review_forms_for_used_sources_only'][0]['independent_relationship_ids']
        self.assertEqual(len(set(ids)), 2)
    def test_fallback_keeps_original_source_origin(self):
        r = self.h['base_fallback_review_forms'][0]
        self.assertNotEqual(r['original_source_origin'], r['article_origin'])
    def test_parent_digest_bound(self):
        self.assertEqual(self.parent['fingerprint_sha256'],
                         self.h['parent_R34_fingerprint_sha256'])
    def test_output_fingerprint_bound(self):
        self.assertEqual(self.h['fingerprint_sha256'],
                         gate.digest({k:v for k,v in self.h.items()
                                      if k != 'fingerprint_sha256'}))
    def test_unique_source_form_ids(self):
        ids = [x['source_case_id_sha256'] for x in self.h['source_scope_review_forms']]
        self.assertEqual(len(ids), len(set(ids)))
    def test_unique_claim_form_ids(self):
        ids = [x['review_case_id_sha256'] for x in self.h['claim_occurrence_review_forms']]
        self.assertEqual(len(ids), len(set(ids)))
    def test_unique_fallback_form_ids(self):
        ids = [x['fallback_case_id_sha256'] for x in self.h['base_fallback_review_forms']]
        self.assertEqual(len(ids), len(set(ids)))
    def test_deterministic(self):
        self.assertEqual(self.h, gate.make_handoff(self.parent, expected=SMALL))
    def test_does_not_mutate_parent(self):
        parent = valid()
        before = copy.deepcopy(parent)
        gate.make_handoff(parent, expected=SMALL)
        self.assertEqual(parent, before)
    def test_output_edits_cannot_mutate_parent_source(self):
        parent = valid()
        h = gate.make_handoff(parent, expected=SMALL)
        before = gate.canonical(parent)
        h['source_scope_review_forms'][0]['unabridged_original_source_record']['notes'] = 'edited'
        self.assertEqual(before, gate.canonical(parent))
    def test_production_totals_cannot_be_overridden_in_default(self):
        with self.assertRaises(gate.HandoffHold):
            gate.make_handoff(self.parent)
    def test_unicode_stable(self):
        self.assertEqual(gate.canonical({'café':'🌿'}),
                         gate.canonical(json.loads(gate.canonical({'café':'🌿'}))))


# Each case is a separate adversarial test. Re-sign modified fixtures to prove
# structural checks, rather than relying solely on a stale parent digest.
CASES = {
    'issue_forged':lambda x:x.update(issue=777),
    'wrong_schema':lambda x:x.update(schema_version=99),
    'published':lambda x:x.update(release_state='PUBLISHED'),
    'authority_forged':lambda x:x.update(machine_authority='APPROVED'),
    'may_publish_true':lambda x:x.update(may_publish=True),
    'may_publish_zero':lambda x:x.update(may_publish=0),
    'qd_true':lambda x:x.update(independent_QD_approval=True),
    'medical_true':lambda x:x.update(qualified_safety_clearance=True),
    'human_reviews_true':lambda x:x.update(human_source_reviews_completed=True),
    'claims_true':lambda x:x.update(source_claim_accuracy_verified=True),
    'r25_parent_removed':lambda x:x.pop('parent_R25_fingerprint_sha256'),
    'r33_parent_invalid':lambda x:x.update(parent_R33_fingerprint_sha256='broken'),
    'counts_changed':lambda x:x['counts'].update(citations=7),
    'counts_missing':lambda x:x.pop('counts'),
    'cards_none':lambda x:x.update(relationship_review_cards=None),
    'cards_missing':lambda x:x['relationship_review_cards'].pop(),
    'cards_extra':lambda x:x['relationship_review_cards'].append(copy.deepcopy(x['relationship_review_cards'][0])),
    'cards_duplicate':lambda x:x['relationship_review_cards'].__setitem__(1,copy.deepcopy(x['relationship_review_cards'][0])),
    'source_approved':lambda x:x['relationship_review_cards'][0].update(review_state='APPROVED'),
    'source_id_changed':lambda x:x['relationship_review_cards'][0].update(source_id='wrong'),
    'source_url_changed':lambda x:x['relationship_review_cards'][0].update(source_url='https://different.example.org'),
    'source_url_http':lambda x:x['relationship_review_cards'][0].update(source_url='http://example.org'),
    'article_origin_missing':lambda x:x['relationship_review_cards'][0].pop('article_origin'),
    'source_origin_missing':lambda x:x['relationship_review_cards'][0].pop('source_origin'),
    'source_id_digest_changed':lambda x:x['relationship_review_cards'][0].update(relationship_id_sha256='f'*64),
    'source_use_changed':lambda x:x['relationship_review_cards'][0].update(full_original_article_source_use='fabricated'),
    'source_use_blank':lambda x:x['relationship_review_cards'][0].update(full_original_article_source_use=' '),
    'source_use_none':lambda x:x['relationship_review_cards'][0].update(full_original_article_source_use=None),
    'supports_changed':lambda x:x['relationship_review_cards'][0]['original_source_record_as_selected'].update(supports='false'),
    'supports_blank':lambda x:x['relationship_review_cards'][0]['original_source_record_as_selected'].update(supports=' '),
    'notes_changed':lambda x:x['relationship_review_cards'][0]['original_source_record_as_selected'].update(notes='other'),
    'fallback_flag_changed':lambda x:x['relationship_review_cards'][0].update(base_fallback_requires_human_scope_review=True),
    'fallback_flag_int':lambda x:x['relationship_review_cards'][1].update(base_fallback_requires_human_scope_review=1),
    'shared_url_flag_int':lambda x:x['relationship_review_cards'][0].update(shared_url_group_requires_human_review=1),
    'shared_url_flag_lost':lambda x:x['relationship_review_cards'][0].update(shared_url_group_requires_human_review=False),
    'claim_list_none':lambda x:x['relationship_review_cards'][0].update(citation_review_items=None),
    'claim_list_empty':lambda x:x['relationship_review_cards'][0].update(citation_review_items=[]),
    'claim_duplicate':lambda x:x['relationship_review_cards'][0]['citation_review_items'].__setitem__(1,copy.deepcopy(x['relationship_review_cards'][0]['citation_review_items'][0])),
    'claim_approved':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0].update(review_state='APPROVED'),
    'claim_context_changed':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0].update(original_context='Other [CITATION]'),
    'claim_context_no_marker':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0].update(original_context='no citation'),
    'claim_ref_wrong_source':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0]['claim_ref'].update(source_id='wrong'),
    'claim_ref_wrong_body':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0]['claim_ref'].update(original_article_html_sha256='a'*64),
    'claim_ref_wrong_record':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0]['claim_ref'].update(original_source_record_sha256='a'*64),
    'claim_ref_wrong_use':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0]['claim_ref'].update(original_source_use_sha256='a'*64),
    'claim_offset_str':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0]['claim_ref'].update(citation_codepoint_offset='8'),
    'claim_offset_bool':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0]['claim_ref'].update(citation_codepoint_offset=True),
    'claim_offset_negative':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0]['claim_ref'].update(citation_codepoint_offset=-1),
    'priority_safe_claim':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0].update(priority='SAFE'),
    'tags_as_string':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0].update(triage_tags_not_safety_findings='safe'),
    'tags_as_bool':lambda x:x['relationship_review_cards'][0]['citation_review_items'][0].update(triage_tags_not_safety_findings=[True]),
    'batch_missing':lambda x:x['review_batches'].pop(),
    'batch_duplicate':lambda x:x['review_batches'].append(copy.deepcopy(x['review_batches'][0])),
    'batch_approved':lambda x:x['review_batches'][0].update(review_state='APPROVED'),
    'batch_number_wrong':lambda x:x['review_batches'][0].update(batch_number=7),
    'batch_id_wrong':lambda x:x['review_batches'][0].update(batch_id_sha256='d'*64),
    'batch_count_wrong':lambda x:x['review_batches'][0].update(citation_occurrences=999),
    'batch_relation_changed':lambda x:x['review_batches'][0].update(relationship_ids=['b'*64]),
    'batch_size_boolean':lambda x:x.update(batch_size=True),
    'batch_size_zero':lambda x:x.update(batch_size=0),
    'batch_size_over_limit':lambda x:x.update(batch_size=51),
    'shared_tracks_none':lambda x:x.update(shared_url_coordination_only=None),
    'shared_track_lost':lambda x:x['shared_url_coordination_only'].pop(),
    'shared_track_duplicate':lambda x:x['shared_url_coordination_only'].append(copy.deepcopy(x['shared_url_coordination_only'][0])),
    'shared_track_approved':lambda x:x['shared_url_coordination_only'][0].update(review_state='APPROVED'),
    'shared_track_url_wrong':lambda x:x['shared_url_coordination_only'][0].update(url='https://other.example.org'),
    'shared_track_ids_lost':lambda x:x['shared_url_coordination_only'][0]['distinct_relationship_ids'].pop(),
    'shared_track_ids_duplicate':lambda x:x['shared_url_coordination_only'][0]['distinct_relationship_ids'].append(x['shared_url_coordination_only'][0]['distinct_relationship_ids'][0]),
}

class Adversarial(unittest.TestCase):
    pass

def make_case(name, mutate):
    def test(self):
        doc=valid()
        mutate(doc)
        resign(doc)
        with self.assertRaises((gate.HandoffHold, TypeError, ValueError),msg=name):
            gate.make_handoff(doc,expected=SMALL)
    return test

for name,mutation in CASES.items():
    setattr(Adversarial, 'test_'+name, make_case(name,mutation))


class ParameterSafety(unittest.TestCase):
    def test_wrong_fingerprint(self):
        d=valid();d['fingerprint_sha256']='0'*64
        with self.assertRaises(gate.HandoffHold):gate.make_handoff(d,expected=SMALL)
    def test_fingerprint_missing(self):
        d=valid();d.pop('fingerprint_sha256')
        with self.assertRaises(gate.HandoffHold):gate.make_handoff(d,expected=SMALL)
    def test_input_none(self):
        with self.assertRaises(gate.HandoffHold):gate.make_handoff(None,expected=SMALL)
    def test_input_list(self):
        with self.assertRaises(gate.HandoffHold):gate.make_handoff([],expected=SMALL)
    def test_expected_bool(self):
        with self.assertRaises(gate.HandoffHold):gate.make_handoff(valid(),expected=(1,0,4,2,True,1))
    def test_expected_list(self):
        with self.assertRaises(gate.HandoffHold):gate.make_handoff(valid(),expected=list(SMALL))
    def test_expected_bad_arity(self):
        with self.assertRaises(gate.HandoffHold):gate.make_handoff(valid(),expected=(1,0))
    def test_expected_negative(self):
        with self.assertRaises(gate.HandoffHold):gate.make_handoff(valid(),expected=(1,0,4,2,-1,1))
    def test_nan_not_canonical(self):
        with self.assertRaises(ValueError):gate.canonical({'bad':float('nan')})
    def test_output_mutation_not_fingerprint_equivalent(self):
        x=gate.make_handoff(valid(),expected=SMALL)
        old=x['fingerprint_sha256']
        x['claim_occurrence_review_forms'][0]['human_source_access_date']='2026-10-31'
        self.assertNotEqual(old,gate.digest({k:v for k,v in x.items() if k!='fingerprint_sha256'}))


if __name__=='__main__':
    unittest.main()
