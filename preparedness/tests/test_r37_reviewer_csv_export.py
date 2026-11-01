"""R37 synthetic tests: truly private CSV review desk; never human approval."""
from __future__ import annotations
import copy
import csv
import io
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import reviewer_csv_export_gate as gate
import global_shared_source_review_gate as r36
import citation_review_batch_gate as r34
from test_r34_citation_review_batches import fixture as original_fixture
from test_r36_global_source_review import (synthetic, synthetic_with_uncited,
                                           validate, validate_uncited, SMALL,
                                           SMALL_UNCITED, URL, UNCITED_URL)

def inputs(with_uncited=False):
    p,q=original_fixture()
    original=r34.make_batch_index(p,q,expected=SMALL)
    if with_uncited:
        lib,h=synthetic_with_uncited()
        return h,validate_uncited(lib,h),SMALL_UNCITED,original
    lib,h=synthetic()
    return h,validate(lib,h),SMALL,original

def export(h,g,tot=SMALL,reading=None):
    if reading is None:
        p,q=original_fixture()
        reading=r34.make_batch_index(p,q,expected=SMALL)
    return gate.build_review_csv_export(h,g,reading,expected=tot)

def refresh(doc):
    doc['fingerprint_sha256']=gate.sha({k:v for k,v in doc.items() if k!='fingerprint_sha256'})

def rows(bundle,name):
    parsed=list(csv.DictReader(io.StringIO(bundle['csv_tables'][name],newline='')))
    return parsed

class Baseline(unittest.TestCase):
    def setUp(self):
        self.h,self.g,self.t,self.original=inputs()
        self.out=export(self.h,self.g,self.t)
    def test_parent_R35_exact(self):self.assertEqual(self.out['manifest']['parent_R35_fingerprint_sha256'],self.h['fingerprint_sha256'])
    def test_parent_R36_exact(self):self.assertEqual(self.out['manifest']['parent_R36_fingerprint_sha256'],self.g['fingerprint_sha256'])
    def test_parent_R34_exact(self):self.assertEqual(self.out['manifest']['parent_R34_original_reading_sha256'],self.original['fingerprint_sha256'])
    def test_original_R34_source_mutation_rejected(self):
        modified=copy.deepcopy(self.original)
        modified['relationship_review_cards'][0]['original_source_record_as_selected']['notes']='FAKE'
        refresh(modified)
        with self.assertRaises(gate.ExportHold):export(self.h,self.g,self.t,modified)
    def test_original_R34_claim_context_mutation_rejected(self):
        modified=copy.deepcopy(self.original)
        modified['relationship_review_cards'][0]['citation_review_items'][0]['original_context']='altered [CITATION]'
        refresh(modified)
        with self.assertRaises(gate.ExportHold):export(self.h,self.g,self.t,modified)
    def test_original_R34_case_reordered_rejected_if_swapped(self):
        modified=copy.deepcopy(self.original)
        modified['relationship_review_cards'][0]['citation_review_items'][0],modified['relationship_review_cards'][1]['citation_review_items'][0]=modified['relationship_review_cards'][1]['citation_review_items'][0],modified['relationship_review_cards'][0]['citation_review_items'][0]
        refresh(modified)
        with self.assertRaises(gate.ExportHold):export(self.h,self.g,self.t,modified)
    def test_original_R34_false_review_rejected(self):
        modified=copy.deepcopy(self.original)
        modified['relationship_review_cards'][0]['review_state']='APPROVED'
        refresh(modified)
        with self.assertRaises(gate.ExportHold):export(self.h,self.g,self.t,modified)
    def test_original_R34_claim_removed_rejected(self):
        modified=copy.deepcopy(self.original)
        modified['relationship_review_cards'][0]['citation_review_items'].pop()
        refresh(modified)
        with self.assertRaises(gate.ExportHold):export(self.h,self.g,self.t,modified)
    def test_original_R34_wrong_authority_rejected(self):
        modified=copy.deepcopy(self.original)
        modified['machine_authority']='PUBLISH'
        refresh(modified)
        with self.assertRaises(gate.ExportHold):export(self.h,self.g,self.t,modified)

    def test_held(self):self.assertEqual(self.out['manifest']['release_state'],'HOLD')
    def test_authority_not_approval(self):self.assertIn('NOT_APPROVAL',self.out['manifest']['machine_authority'])
    def test_no_false_approval(self):self.assertTrue(all(self.out['manifest'][f] is False for f in gate.HOLD_FLAGS))
    def test_manifest_fingerprint(self):self.assertEqual(self.out['manifest']['fingerprint_sha256'],gate.sha({k:v for k,v in self.out['manifest'].items() if k!='fingerprint_sha256'}))
    def test_four_csv_files(self):self.assertEqual(set(self.out['csv_tables']),set(gate.TABLES))
    def test_four_claim_rows(self):self.assertEqual(len(rows(self.out,'claim_review.csv')),4)
    def test_two_scope_rows(self):self.assertEqual(len(rows(self.out,'source_scope_review.csv')),2)
    def test_one_fallback_row(self):self.assertEqual(len(rows(self.out,'fallback_scope_review.csv')),1)
    def test_one_global_url_row(self):self.assertEqual(len(rows(self.out,'global_shared_url_review.csv')),1)
    def test_different_scope_notes_same_url(self):
        source=rows(self.out,'source_scope_review.csv')
        self.assertEqual(len({r['source_url'] for r in source}),1)
        self.assertEqual(len({json.loads(r['full_original_source_record_json'])['notes'] for r in source}),2)
    def test_original_source_supports_unabridged(self):
        source=rows(self.out,'source_scope_review.csv')
        self.assertEqual({json.loads(r['full_original_source_record_json'])['supports'] for r in source},
                         {f['unabridged_original_source_record']['supports'] for f in self.h['source_scope_review_forms']})
    def test_full_article_specific_scope(self):
        self.assertEqual({r['full_original_article_source_use'] for r in rows(self.out,'source_scope_review.csv')},
                         {s['unabridged_article_specific_source_use'] for s in self.h['source_scope_review_forms']})
    def test_original_claim_context(self):
        self.assertEqual({r['exact_original_context'] for r in rows(self.out,'claim_review.csv')},
                         {c['exact_original_context'] for c in self.h['claim_occurrence_review_forms']})
    def test_claim_offsets(self):
        self.assertEqual({int(r['original_codepoint_offset']) for r in rows(self.out,'claim_review.csv')},
                         {8,19,108,119})
    def test_prioritize_not_approve(self):
        self.assertEqual({r['triage_priority_not_verdict'] for r in rows(self.out,'claim_review.csv')},
                         {'REVIEW_FIRST','STANDARD_REVIEW'})
    def test_export_claim_review_states(self):
        self.assertEqual({r['review_state'] for r in rows(self.out,'claim_review.csv')},{'NOT_STARTED'})
    def test_export_fallback_review_states(self):
        self.assertEqual({r['review_state'] for r in rows(self.out,'fallback_scope_review.csv')},{'NOT_STARTED'})
    def test_export_source_review_states(self):
        self.assertEqual({r['review_state'] for r in rows(self.out,'source_scope_review.csv')},{'NOT_STARTED'})
    def test_export_global_review_states(self):
        self.assertEqual({r['review_state'] for r in rows(self.out,'global_shared_url_review.csv')},{'NOT_STARTED'})
    def test_no_human_response_claims(self):
        for name,tab in self.out['csv_tables'].items():
            for row in rows(self.out,name):
                self.assertTrue(all(value=='' for key,value in row.items() if key.startswith('human_')), name)
    def test_fallback_origin_not_deduped(self):
        self.assertEqual(rows(self.out,'fallback_scope_review.csv')[0]['original_source_origin'],'cluster-two')
    def test_distinct_claim_case_ids(self):
        refs=[r['claim_case_sha256'] for r in rows(self.out,'claim_review.csv')]
        self.assertEqual(len(refs),len(set(refs)))
    def test_deterministic_bytes(self):
        self.assertEqual(self.out,export(self.h,self.g,self.t))
    def test_parent_packets_unchanged(self):
        before=copy.deepcopy((self.h,self.g));export(self.h,self.g,self.t)
        self.assertEqual(before,(self.h,self.g))
