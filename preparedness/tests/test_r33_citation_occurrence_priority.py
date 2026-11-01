"""R33: deterministic, fail-closed claim work order. Synthetic fixtures only."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import citation_fallback_review_gate as r25
import citation_review_index_gate as r31
import citation_occurrence_priority_gate as gate
from test_citation_fallback_review_gate import Library, SMALL


def fixture():
    p = r25.audit(Library(), expected=SMALL)
    return p, r31.build_index(p, expected=SMALL)


def resign(obj):
    obj['fingerprint_sha256'] = gate.digest({k:v for k,v in obj.items()
                                              if k!='fingerprint_sha256'})


def rebind(p, i):
    resign(p)
    i['parent_R25_fingerprint_sha256'] = p['fingerprint_sha256']
    resign(i)


class Acceptance(unittest.TestCase):
    def test_exact_four_occurrence_tasks_without_collapse(self):
        p,i=fixture();q=gate.build_priority_queue(p,i,expected=SMALL)
        self.assertEqual(len(q['review_tasks']),4)
        self.assertEqual(len({(x['claim_ref']['slug'],x['claim_ref']['citation_codepoint_offset'])
                              for x in q['review_tasks']}),4)
    def test_all_tasks_pending_even_when_no_keywords(self):
        p,i=fixture();q=gate.build_priority_queue(p,i,expected=SMALL)
        self.assertTrue(all(x['review_state'].startswith('PENDING_') for x in q['review_tasks']))
    def test_never_publish_or_approve(self):
        p,i=fixture();q=gate.build_priority_queue(p,i,expected=SMALL)
        for k in ('may_publish','independent_QD_approval','qualified_safety_clearance',
                  'human_source_reviews_completed','source_claim_accuracy_verified'):
            self.assertIs(q[k],False)
        self.assertEqual(q['release_state'],'HOLD')
    def test_binds_two_independent_parent_digests(self):
        p,i=fixture();q=gate.build_priority_queue(p,i,expected=SMALL)
        self.assertEqual(q['parent_R25_fingerprint_sha256'],p['fingerprint_sha256'])
        self.assertEqual(q['parent_R31_fingerprint_sha256'],i['fingerprint_sha256'])
    def test_own_digest_is_correct(self):
        p,i=fixture();q=gate.build_priority_queue(p,i,expected=SMALL)
        self.assertEqual(q['fingerprint_sha256'],gate.digest({k:v for k,v in q.items()
                                                              if k!='fingerprint_sha256'}))
    def test_determinism_and_no_input_mutation(self):
        p,i=fixture();before=(copy.deepcopy(p),copy.deepcopy(i))
        q=gate.build_priority_queue(p,i,expected=SMALL)
        self.assertEqual(q,gate.build_priority_queue(p,i,expected=SMALL))
        self.assertEqual((p,i),before)
    def test_context_and_original_digests_retained(self):
        p,i=fixture();q=gate.build_priority_queue(p,i,expected=SMALL)
        a=q['review_tasks'][0]
        self.assertIn('[CITATION]',a['citation_context_for_human_review'])
        self.assertRegex(a['claim_ref_sha256'],r'^[a-f0-9]{64}$')
        self.assertRegex(a['claim_ref']['original_source_record_sha256'],r'^[a-f0-9]{64}$')
    def test_priority_contains_review_first_and_original_coordinates(self):
        p,i=fixture();q=gate.build_priority_queue(p,i,expected=SMALL)
        self.assertEqual(q['counts']['citations'],4)
        self.assertEqual(sum(q['priority_counts'].values()),4)
        self.assertTrue(all(type(x['claim_ref']['citation_codepoint_offset']) is int
                            for x in q['review_tasks']))
    def test_default_production_counts_reject_reduced_fixture(self):
        p,i=fixture()
        with self.assertRaises(gate.PriorityHold):gate.build_priority_queue(p,i)
    def test_order_never_declares_standard_safe(self):
        p,i=fixture();q=gate.build_priority_queue(p,i,expected=SMALL)
        self.assertNotIn('SAFE',set(x['priority'] for x in q['review_tasks']))
        self.assertIn('not safety',q['limitations'].lower())
    def test_context_sha256_uses_utf8_not_ascii(self):
        p,i=fixture();p['review_queue'][0]['all_citation_contexts_for_human_claim_review'][0]='café [CITATION]'
        rebind(p,i)
        q=gate.build_priority_queue(p,i,expected=SMALL)
        t=next(t for t in q['review_tasks'] if t['claim_ref']['source_id']==p['review_queue'][0]['source_id']
               and t['claim_ref']['citation_codepoint_offset']==p['review_queue'][0]['citation_token_codepoint_offsets'][0])
        import hashlib
        self.assertEqual(t['claim_ref']['citation_context_sha256'],hashlib.sha256('café [CITATION]'.encode()).hexdigest())
    def test_mixed_categories_can_coexist(self):
        p,i=fixture();p['review_queue'][0]['all_citation_contexts_for_human_claim_review'][0]='insulin, drinking water, generator [CITATION]'
        rebind(p,i)
        q=gate.build_priority_queue(p,i,expected=SMALL)
        t=next(t for t in q['review_tasks'] if 'medical-and-dependencies' in t['triage_tags_not_safety_findings'])
        self.assertIn('water-and-chemicals',t['triage_tags_not_safety_findings'])
        self.assertIn('fire-and-combustion',t['triage_tags_not_safety_findings'])


TOPIC_CASES = {
    'water_boiling':'Boiling water [CITATION]',
    'bleach':'bleach concentration [CITATION]',
    'chlorine':'chlorination [CITATION]',
    'cistern':'cistern storage [CITATION]',
    'chemical':'chemical contamination [CITATION]',
    'water_advisory':'water advisory [CITATION]',
    'food_jerky':'jerky [CITATION]',
    'food_botulism':'botulism [CITATION]',
    'food_canning':'pressure canning [CITATION]',
    'food_refrigeration':'refrigeration [CITATION]',
    'food_fermentation':'fermentation [CITATION]',
    'food_freezer':'freezer [CITATION]',
    'fire_generator':'generator [CITATION]',
    'fire_charcoal':'charcoal [CITATION]',
    'fire_carbon_monoxide':'carbon monoxide [CITATION]',
    'fire_evacuate':'evacuation [CITATION]',
    'fire_smoke_alarm':'smoke alarm [CITATION]',
    'medical_insulin':'insulin [CITATION]',
    'medical_oxygen':'oxygen [CITATION]',
    'medical_medication':'medication [CITATION]',
    'medical_pharmacist':'pharmacist [CITATION]',
    'medical_dialysis':'dialysis [CITATION]',
    'medical_firstaid':'first aid [CITATION]',
    'access_wheelchair':'wheelchair [CITATION]',
    'access_formula':'infant formula [CITATION]',
    'access_caregiver':'caregiver [CITATION]',
    'access_disability':'disability [CITATION]',
    'access_baby':'baby [CITATION]',
}

class TopicTriage(unittest.TestCase):pass

def topic_case(k,v):
    def t(self):
        p,i=fixture();r=p['review_queue'][0]
        r['all_citation_contexts_for_human_claim_review'][0]=v
        rebind(p,i)
        tasks=gate.build_priority_queue(p,i,expected=SMALL)['review_tasks']
        self.assertTrue(any(x['citation_context_for_human_review']==v and
                            x['priority']=='REVIEW_FIRST' for x in tasks),k)
    return t
for k,v in TOPIC_CASES.items():setattr(TopicTriage,'test_'+k,topic_case(k,v))


MUTATIONS = {
 'packet_not_dict':lambda p,i:('bad',i),
 'index_not_dict':lambda p,i:(p,'bad'),
 'packet_schema':lambda p,i:p.update(schema_version=2),
 'index_schema':lambda p,i:i.update(schema_version=2),
 'packet_wrong_issue':lambda p,i:p.update(issue=44),
 'index_wrong_issue':lambda p,i:i.update(issue=44),
 'packet_published':lambda p,i:p.update(release_state='PUBLISHED'),
 'index_published':lambda p,i:i.update(release_state='PUBLISHED'),
 'packet_publish_flag':lambda p,i:p.update(may_publish=True),
 'index_publish_flag':lambda p,i:i.update(may_publish=True),
 'packet_zero_flag':lambda p,i:p.update(may_publish=0),
 'index_zero_flag':lambda p,i:i.update(may_publish=0),
 'packet_QD_claim':lambda p,i:p.update(independent_QD_approval=True),
 'index_QD_claim':lambda p,i:i.update(independent_QD_approval=True),
 'packet_safety_claim':lambda p,i:p.update(qualified_safety_clearance=True),
 'index_safety_claim':lambda p,i:i.update(qualified_safety_clearance=True),
 'packet_human_claim':lambda p,i:p.update(human_source_reviews_completed=True),
 'index_human_claim':lambda p,i:i.update(human_source_reviews_completed=True),
 'packet_accuracy_claim':lambda p,i:p.update(source_claim_accuracy_verified=True),
 'index_accuracy_claim':lambda p,i:i.update(source_claim_accuracy_verified=True),
 'packet_authority':lambda p,i:p.update(machine_authority='HUMAN_REVIEW'),
 'index_authority':lambda p,i:i.update(machine_authority='HUMAN_REVIEW'),
 'different_article_totals':lambda p,i:p['counts'].update(articles=10),
 'different_citation_totals':lambda p,i:p['counts'].update(citations=100),
 'index_wrong_totals':lambda p,i:i['counts'].update(relationships=10),
 'missing_queue':lambda p,i:p.pop('review_queue'),
 'extra_queue_row':lambda p,i:p['review_queue'].append(copy.deepcopy(p['review_queue'][0])),
 'missing_queue_row':lambda p,i:p['review_queue'].pop(),
 'no_cards':lambda p,i:i.pop('article_review_cards'),
 'card_loss':lambda p,i:i['article_review_cards'].pop(),
 'duplicate_card':lambda p,i:i['article_review_cards'].__setitem__(1,copy.deepcopy(i['article_review_cards'][0])),
 'false_card_review':lambda p,i:i['article_review_cards'][0].update(review_state='REVIEWED'),
 'wrong_card_body':lambda p,i:i['article_review_cards'][0].update(article_html_sha256='0'*64),
 'unknown_slug':lambda p,i:p['review_queue'][0].update(slug='unknown'),
 'no_source_id':lambda p,i:p['review_queue'][0].update(source_id=''),
 'bad_body_hash':lambda p,i:p['review_queue'][0].update(frozen_article_html_sha256='badhash'),
 'bad_scope_hash':lambda p,i:p['review_queue'][0].update(frozen_source_use_sha256='badhash'),
 'bad_record_hash':lambda p,i:p['review_queue'][0].update(original_source_record_sha256='badhash'),
 'no_offsets':lambda p,i:p['review_queue'][0].update(citation_token_codepoint_offsets=[]),
 'offset_string':lambda p,i:p['review_queue'][0]['citation_token_codepoint_offsets'].__setitem__(0,'0'),
 'negative_offset':lambda p,i:p['review_queue'][0]['citation_token_codepoint_offsets'].__setitem__(0,-1),
 'duplicate_offsets':lambda p,i:p['review_queue'][0].update(citation_token_codepoint_offsets=[1]*p['review_queue'][0]['citation_occurrences']),
 'no_contexts':lambda p,i:p['review_queue'][0].update(all_citation_contexts_for_human_claim_review=[]),
 'context_int':lambda p,i:p['review_queue'][0]['all_citation_contexts_for_human_claim_review'].__setitem__(0,42),
 'context_missing_marker':lambda p,i:p['review_queue'][0]['all_citation_contexts_for_human_claim_review'].__setitem__(0,'omitted citation'),
 'context_extra_marker':lambda p,i:p['review_queue'][0]['all_citation_contexts_for_human_claim_review'].__setitem__(0,'[CITATION] twice [CITATION]'),
 'fractional_citation_count':lambda p,i:p['review_queue'][0].update(citation_occurrences=1.5),
 'missing_citation_count':lambda p,i:p['review_queue'][0].pop('citation_occurrences'),
 'fallback_nonboolean':lambda p,i:p['review_queue'][0].update(base_fallback_requires_human_scope_review='false'),
 'shared_nonboolean':lambda p,i:p['review_queue'][0].update(shared_url_group_requires_human_review=0),
 'human_claim_yes':lambda p,i:p['review_queue'][0].update(human_claim_reviewed_by_this_gate=True),
 'human_link_yes':lambda p,i:p['review_queue'][0].update(human_link_checked_by_this_gate=True),
 'card_relationship_mismatch':lambda p,i:i['article_review_cards'][0].update(relationships=99),
 'card_citation_mismatch':lambda p,i:i['article_review_cards'][0].update(citations=99),
 'origins_mutated':lambda p,i:p['review_queue'][0].update(article_origin='other'),
}

class RejectMutations(unittest.TestCase):pass

def rejection(k,fn):
    def t(self):
        p,i=fixture()
        change=fn(p,i)
        if isinstance(change,tuple):p,i=change
        if type(p) is dict and type(i) is dict:rebind(p,i)
        with self.assertRaises(gate.PriorityHold,msg=k):
            gate.build_priority_queue(p,i,expected=SMALL)
    return t
for k,fn in MUTATIONS.items():setattr(RejectMutations,'test_'+k,rejection(k,fn))

class ChecksumControls(unittest.TestCase):
    def test_packet_edit_without_resigning(self):
        p,i=fixture();p['review_queue'][0]['source_url']='https://other.example.org'
        with self.assertRaisesRegex(gate.PriorityHold,'fingerprint mismatch'):
            gate.build_priority_queue(p,i,expected=SMALL)
    def test_index_edit_without_resigning(self):
        p,i=fixture();i['article_review_cards'][0]['review_state']='REVIEWED'
        with self.assertRaisesRegex(gate.PriorityHold,'fingerprint mismatch'):
            gate.build_priority_queue(p,i,expected=SMALL)
    def test_index_bound_to_wrong_packet(self):
        p,i=fixture();p['review_queue'][0]['source_url']='https://changed.example.org';resign(p)
        with self.assertRaisesRegex(gate.PriorityHold,'different claim packet'):
            gate.build_priority_queue(p,i,expected=SMALL)
    def test_bad_expected_counts_type(self):
        p,i=fixture()
        for wrong in ('35',[],(True,1,4,3,1,1),SMALL[:-1]):
            with self.subTest(wrong=wrong),self.assertRaises(gate.PriorityHold):
                gate.build_priority_queue(p,i,expected=wrong)

if __name__=='__main__':unittest.main()
