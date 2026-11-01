"""R36 adversarial synthetic crosswalk review, no live content or source approvals."""
from __future__ import annotations
import copy
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import citation_review_batch_gate as r34
import citation_review_handoff_gate as r35
import global_shared_source_review_gate as gate
from test_r34_citation_review_batches import fixture, SMALL, URL

FILES={'cluster-one':'preparedness/sources/fragments/cluster-one.json',
       'cluster-two':'preparedness/sources/fragments/cluster-two.json'}
INV=(2,1,1,0)

def synthetic():
    a,b=fixture()
    h=r35.make_handoff(r34.make_batch_index(a,b,expected=SMALL),expected=SMALL)
    originals=[copy.deepcopy(x['unabridged_original_source_record']) for x in h['source_scope_review_forms']]
    entries=[]
    for original in originals:
        origin=original['_origin']
        entries.append({'origin':origin,'source_file':FILES[origin],'row_index':0,
                        'source':{k:copy.deepcopy(v) for k,v in original.items() if k!='_origin'}})
    group={'url':URL,'canonical_url':URL,
           'review_status':gate.PENDING,'reviewer':None,'reviewed_on':None,
           'variants':copy.deepcopy(entries),
           'identities':[{'origin':e['origin'],'id':e['source']['id'],
                          'row_index':e['row_index']} for e in entries]}
    cw={'schema_version':1,'status':'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
        'raw_source_rows':2,'unique_source_urls':1,'duplicate_url_groups':1,
        'duplicate_id_groups':0,'groups':[group]}
    variants={o['id']:[copy.deepcopy(o)] for o in originals}
    return SimpleNamespace(crosswalk=cw,crosswalk_groups={URL:copy.deepcopy(group)},
                           source_variants=variants),h

def validate(lib,h):
    return gate.build_global_source_review(lib,h,expected=SMALL,inventory=INV,source_files=FILES)

class Success(unittest.TestCase):
    def setUp(self):
        self.lib,self.h=synthetic()
        self.out=validate(self.lib,self.h)
    def test_one_global_group(self):
        self.assertEqual(len(self.out['globally_unreviewed_shared_url_cards']),1)
    def test_two_original_variants_not_collapsed(self):
        self.assertEqual(len(self.out['globally_unreviewed_shared_url_cards'][0]['distinct_original_variants']),2)
    def test_reading_depth_preserved(self):
        self.assertEqual({x['original_full_source_record']['supports'] for x in self.out['globally_unreviewed_shared_url_cards'][0]['distinct_original_variants']},
                         {x['supports'] for v in self.lib.source_variants.values() for x in v})
    def test_notes_preserved(self):
        self.assertEqual({x['original_full_source_record']['notes'] for x in self.out['globally_unreviewed_shared_url_cards'][0]['distinct_original_variants']},
                         {x['notes'] for v in self.lib.source_variants.values() for x in v})
    def test_every_claim_case_bound(self):
        self.assertEqual(len(self.out['globally_unreviewed_shared_url_cards'][0]['cited_claim_review_case_ids']),4)
    def test_every_relationship_bound(self):
        self.assertEqual(len(self.out['globally_unreviewed_shared_url_cards'][0]['cited_relationship_ids']),2)
    def test_false_human_review_not_asserted(self):
        self.assertEqual(self.out['global_shared_url_groups_reviewed_by_human'],0)
    def test_release_hold(self):
        self.assertEqual(self.out['release_state'],'HOLD')
    def test_false_approvals_blocked_in_output(self):
        self.assertTrue(all(self.out[f] is False for f in gate.HOLD_FLAGS))
    def test_variant_review_blank(self):
        self.assertTrue(all(v['human_source_access_date'] is None for v in self.out['globally_unreviewed_shared_url_cards'][0]['distinct_original_variants']))
    def test_global_review_blank(self):
        self.assertIsNone(self.out['globally_unreviewed_shared_url_cards'][0]['human_independent_safety_assessment'])
    def test_deterministic(self):
        self.assertEqual(self.out,validate(self.lib,self.h))
    def test_fingerprint(self):
        self.assertEqual(self.out['fingerprint_sha256'],gate.sha({k:v for k,v in self.out.items() if k!='fingerprint_sha256'}))
    def test_parent_binds(self):
        self.assertEqual(self.out['parent_R35_fingerprint_sha256'],self.h['fingerprint_sha256'])
    def test_full_global_crosswalk_bound(self):
        self.assertEqual(self.out['original_global_crosswalk_sha256'],gate.sha(self.lib.crosswalk))
    def test_no_input_mutation(self):
        old=copy.deepcopy((self.lib,self.h));validate(self.lib,self.h)
        self.assertEqual(old,(self.lib,self.h))
    def test_unabridged_original_crosswalk(self):
        self.assertEqual(self.out['globally_unreviewed_shared_url_cards'][0]['unabridged_original_crosswalk_group'],self.lib.crosswalk['groups'][0])
    def test_all_counts(self):
        self.assertEqual(self.out['counts'],dict(zip(('source_rows','unique_urls','global_shared_url_groups','repeated_source_id_groups'),INV)))
    def test_reading_scope_marked_not_started(self):
        self.assertEqual({'NOT_STARTED'}, {v['review_state'] for v in self.out['globally_unreviewed_shared_url_cards'][0]['distinct_original_variants']})
    def test_urls_are_not_normalized(self):
        self.assertEqual(self.out['globally_unreviewed_shared_url_cards'][0]['source_url'],URL)
    def test_machines_do_not_visit(self):
        self.assertNotIn('human_source_access_date',self.out)
    def test_no_external_writes(self):
        self.assertEqual(len(self.lib.crosswalk['groups']),1)
    def test_full_original_metadata(self):
        self.assertIn('publisher',self.out['globally_unreviewed_shared_url_cards'][0]['distinct_original_variants'][0]['original_full_source_record'])
    def test_unique_global_group_id(self):
        self.assertEqual(len(self.out['globally_unreviewed_shared_url_cards'][0]['global_group_case_id_sha256']),64)
    def test_unreviewed_counts_consistent(self):
        self.assertEqual(self.out['shared_url_groups_with_cited_sources']+self.out['shared_url_groups_without_cited_sources'],1)
    def test_used_sources_flag(self):
        self.assertTrue(self.out['globally_unreviewed_shared_url_cards'][0]['used_in_any_citation'])
    def test_plain_json_serializable(self):
        json.dumps(self.out,ensure_ascii=False,allow_nan=False)
    def test_default_freeze_rejects_small_synthetic(self):
        with self.assertRaises(gate.GlobalSourceHold): gate.build_global_source_review(self.lib,self.h)

MUTATIONS = {
 'wrong_schema':lambda l,h:l.crosswalk.update(schema_version=2),
 'crosswalk_approved':lambda l,h:l.crosswalk.update(status='APPROVED'),
 'bad_source_rows':lambda l,h:l.crosswalk.update(raw_source_rows=3),
 'bad_distinct_urls':lambda l,h:l.crosswalk.update(unique_source_urls=3),
 'bad_repeat_url_count':lambda l,h:l.crosswalk.update(duplicate_url_groups=0),
 'bad_repeat_id_count':lambda l,h:l.crosswalk.update(duplicate_id_groups=1),
 'missing_group':lambda l,h:l.crosswalk.update(groups=[]),
 'missing_lookup_group':lambda l,h:l.crosswalk_groups.clear(),
 'fake_group_review':lambda l,h:l.crosswalk['groups'][0].update(review_status='APPROVED'),
 'fake_reviewer_name':lambda l,h:l.crosswalk['groups'][0].update(reviewer='somebody'),
 'fake_review_date':lambda l,h:l.crosswalk['groups'][0].update(reviewed_on='2026-10-31'),
 'wrong_canonical':lambda l,h:l.crosswalk['groups'][0].update(canonical_url='https://elsewhere.example'),
 'group_url_change':lambda l,h:l.crosswalk['groups'][0].update(url='https://elsewhere.example'),
 'remove_group_source_variant':lambda l,h:l.crosswalk['groups'][0]['variants'].pop(),
 'remove_group_identity':lambda l,h:l.crosswalk['groups'][0]['identities'].pop(),
 'change_group_supports':lambda l,h:l.crosswalk['groups'][0]['variants'][0]['source'].update(supports='shorter'),
 'change_group_notes':lambda l,h:l.crosswalk['groups'][0]['variants'][0]['source'].update(notes='fake notes'),
 'change_group_publisher':lambda l,h:l.crosswalk['groups'][0]['variants'][0]['source'].update(publisher='wrong'),
 'change_group_source_id':lambda l,h:l.crosswalk['groups'][0]['variants'][0]['source'].update(id='new-id'),
 'change_group_url':lambda l,h:l.crosswalk['groups'][0]['variants'][0]['source'].update(url='https://bad.example'),
 'change_group_origin':lambda l,h:l.crosswalk['groups'][0]['variants'][0].update(origin='mystery'),
 'change_group_path':lambda l,h:l.crosswalk['groups'][0]['variants'][0].update(source_file='bad/path'),
 'change_group_index':lambda l,h:l.crosswalk['groups'][0]['variants'][0].update(row_index=-3),
 'duplicate_variant':lambda l,h:l.crosswalk['groups'][0]['variants'].append(copy.deepcopy(l.crosswalk['groups'][0]['variants'][0])),
 'identity_index_substitution':lambda l,h:l.crosswalk['groups'][0]['identities'][0].update(row_index=99),
 'identity_id_substitution':lambda l,h:l.crosswalk['groups'][0]['identities'][0].update(id='fake'),
 'alter_library_source_note':lambda l,h:next(iter(l.source_variants.values()))[0].update(notes='tampered'),
 'alter_library_source_id':lambda l,h:next(iter(l.source_variants.values()))[0].update(id='wrong'),
 'alter_library_source_url':lambda l,h:next(iter(l.source_variants.values()))[0].update(url='http://not-secure.example'),
 'drop_library_source':lambda l,h:l.source_variants.pop(next(iter(l.source_variants))),
 'same_origin_duplicate':lambda l,h:next(iter(l.source_variants.values())).append(copy.deepcopy(next(iter(l.source_variants.values()))[0])),
 'R35_wrong_issue':lambda l,h:h.update(issue=137),
 'R35_wrong_authority':lambda l,h:h.update(machine_authority='APPROVED'),
 'R35_wrong_release':lambda l,h:h.update(release_state='PUBLIC'),
 'R35_publish_true':lambda l,h:h.update(may_publish=True),
 'R35_QD_pass':lambda l,h:h.update(independent_QD_approval=True),
 'R35_safety_pass':lambda l,h:h.update(qualified_safety_clearance=True),
 'R35_human_complete':lambda l,h:h.update(human_source_reviews_completed=True),
 'R35_source_accuracy_claim':lambda l,h:h.update(source_claim_accuracy_verified=True),
 'R35_wrong_fingerprint':lambda l,h:h.update(fingerprint_sha256='0'*64),
 'R35_source_missing':lambda l,h:h['source_scope_review_forms'].pop(),
 'R35_claim_missing':lambda l,h:h['claim_occurrence_review_forms'].pop(),
 'R35_fallback_missing':lambda l,h:h['base_fallback_review_forms'].pop(),
 'R35_source_approved':lambda l,h:h['source_scope_review_forms'][0].update(review_state='APPROVED'),
 'R35_claim_approved':lambda l,h:h['claim_occurrence_review_forms'][0].update(review_state='APPROVED'),
 'R35_fallback_approved':lambda l,h:h['base_fallback_review_forms'][0].update(review_state='APPROVED'),
 'R35_cited_url_changed':lambda l,h:h['source_scope_review_forms'][0].update(source_url='https://tamper.example'),
 'R35_cited_record_changed':lambda l,h:h['source_scope_review_forms'][0]['unabridged_original_source_record'].update(notes='fake'),
 'R35_claim_orphan':lambda l,h:h['claim_occurrence_review_forms'][0].update(relationship_id_sha256='0'*64),
 'R35_claim_url_changed':lambda l,h:h['claim_occurrence_review_forms'][0].update(source_url='https://fake.example'),
 'R35_fallback_orphan':lambda l,h:h['base_fallback_review_forms'][0].update(relationship_id_sha256='f'*64),
 'R35_shared_missing':lambda l,h:h['shared_url_review_forms_for_used_sources_only'].clear(),
 'R35_shared_approval':lambda l,h:h['shared_url_review_forms_for_used_sources_only'][0].update(human_separate_reading_scopes_reconciled=True),
 'R35_shared_changed':lambda l,h:h['shared_url_review_forms_for_used_sources_only'][0].update(independent_relationship_ids=[]),
 'R35_global_count_approved':lambda l,h:h['review_task_counts'].update(global_shared_url_groups_unreviewed=0),
 'R35_claim_duplicate':lambda l,h:h['claim_occurrence_review_forms'][1].update(review_case_id_sha256=h['claim_occurrence_review_forms'][0]['review_case_id_sha256']),
 'R35_fallback_tamper':lambda l,h:h['base_fallback_review_forms'][0].update(review_state='COMPLETE'),
 'missing_R35_scope_record_sha':lambda l,h:h['source_scope_review_forms'][0].update(source_record_sha256='0'*64),
 'bad_R35_scope_origin':lambda l,h:h['source_scope_review_forms'][0].update(source_origin='wrong'),
 'bad_R35_scope_sid':lambda l,h:h['source_scope_review_forms'][0].update(source_id='wrong'),
}

def fail_case(name,mutate):
    def test(self):
        l,h=synthetic();mutate(l,h)
        with self.assertRaises(gate.GlobalSourceHold,msg=name): validate(l,h)
    test.__name__='test_reject_'+name
    return test

class Mutations(unittest.TestCase):pass
for _name,_mutation in MUTATIONS.items():
    setattr(Mutations,'test_reject_'+_name,fail_case(_name,_mutation))

if __name__=='__main__':unittest.main()
