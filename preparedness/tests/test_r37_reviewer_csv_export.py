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
    def test_manifest_byte_digests(self):
        import hashlib
        for name,body in self.out['csv_tables'].items():
            meta=self.out['manifest']['csv_tables'][name]
            self.assertEqual(meta['sha256_utf8'],hashlib.sha256(body.encode('utf-8')).hexdigest())
            self.assertEqual(meta['bytes_utf8'],len(body.encode('utf-8')))
    def test_manifest_columns_match_csv(self):
        for name,header in gate.TABLES.items():
            self.assertEqual(self.out['manifest']['csv_tables'][name]['columns'],list(header))
    def test_production_defaults_reject_synthetic(self):
        with self.assertRaises(gate.ExportHold):gate.build_review_csv_export(self.h,self.g,self.original)
    def test_json_serializable_manifest(self):json.dumps(self.out['manifest'],allow_nan=False,ensure_ascii=False)
    def test_excel_CRLF_dialect(self):
        for body in self.out['csv_tables'].values():self.assertIn('\r\n',body)
    def test_no_file_io(self):self.assertEqual(sorted(self.out),['csv_tables','manifest'])

class Uncited(unittest.TestCase):
    def setUp(self):
        self.h,self.g,self.t,self.original=inputs(True)
        self.out=export(self.h,self.g,self.t)
    def test_two_global_review_rows(self):self.assertEqual(len(rows(self.out,'global_shared_url_review.csv')),2)
    def test_uncited_url_appears(self):self.assertIn(UNCITED_URL,{x['source_url'] for x in rows(self.out,'global_shared_url_review.csv')})
    def test_uncited_not_claimed_cited(self):
        uncited=next(x for x in rows(self.out,'global_shared_url_review.csv') if x['source_url']==UNCITED_URL)
        self.assertEqual(uncited['used_in_any_citation'],'false')
    def test_uncited_original_reading_not_lost(self):
        uncited=next(x for x in rows(self.out,'global_shared_url_review.csv') if x['source_url']==UNCITED_URL)
        scopes=json.loads(uncited['distinct_original_variants_json'])
        self.assertEqual({x['original_full_source_record']['notes'] for x in scopes},
                         {'Unique contributor note 0','Unique contributor note 1'})
    def test_uncited_stays_unreviewed(self):
        uncited=next(x for x in rows(self.out,'global_shared_url_review.csv') if x['source_url']==UNCITED_URL)
        self.assertEqual(uncited['review_state'],'NOT_STARTED')
    def test_number_of_cited_claims_not_inflated(self):self.assertEqual(len(rows(self.out,'claim_review.csv')),4)
    def test_no_input_mutation(self):
        before=copy.deepcopy((self.h,self.g)); export(self.h,self.g,self.t)
        self.assertEqual((self.h,self.g),before)

class FormulaEscapes(unittest.TestCase):
    def test_safe_literal(self):self.assertEqual(gate._safe_cell('normal evidence'),'normal evidence')
    def test_equals(self):self.assertEqual(gate._safe_cell('=HYPERLINK("evil")'),"'=HYPERLINK(\"evil\")")
    def test_plus(self):self.assertEqual(gate._safe_cell('+1+2'),"'+1+2")
    def test_minus(self):self.assertEqual(gate._safe_cell('-1+2'),"'-1+2")
    def test_at(self):self.assertEqual(gate._safe_cell('@SUM(1,2)'),"'@SUM(1,2)")
    def test_leading_space(self):self.assertEqual(gate._safe_cell('   =X'),"'   =X")
    def test_leading_unicode_bom(self):self.assertEqual(gate._safe_cell('\ufeff=Y'),"'\ufeff=Y")
    def test_leading_zero_width(self):self.assertEqual(gate._safe_cell('\u200b=Y'),"'\u200b=Y")
    def test_newline_no_physical_csv_split(self):
        body=gate._render(('evidence','case'),[{'evidence':'source note\n=WEBSERVICE(1)','case':'abc'}])
        values=list(csv.DictReader(io.StringIO(body,newline='')))
        self.assertEqual(len(values),1)
        self.assertEqual(values[0]['evidence'],'source note\\n=WEBSERVICE(1)')
    def test_carriage_return_escaped(self):self.assertEqual(gate._safe_cell('abc\r=CMD()'),'abc\\r=CMD()')
    def test_tab_escaped(self):self.assertEqual(gate._safe_cell('\t=2'),r'\t=2')
    def test_backslash_roundtrip(self):self.assertEqual(gate._safe_cell(r'c:\data\records'),r'c:\\data\\records')
    def test_non_english_untouched(self):self.assertEqual(gate._safe_cell('mémoire — 船'), 'mémoire — 船')
    def test_csv_quotes_do_not_make_formula_active(self):
        body=gate._render(('x',),[{'x':'=1+1'}]);
        self.assertEqual(list(csv.DictReader(io.StringIO(body,newline='')))[0]['x'],"'=1+1")
    def test_json_evidence_retained(self):
        raw={'supports':'=INVOCATION','notes':'notes, newline\n and a backslash \\'}
        v=gate._safe_cell(raw)
        self.assertEqual(json.loads(v)['supports'],'=INVOCATION')
    def test_bool_type(self):self.assertEqual(gate._safe_cell(False),'false')
    def test_none_blank(self):self.assertEqual(gate._safe_cell(None),'')
    def test_no_missing_columns(self):
        with self.assertRaises(gate.ExportHold):gate._render(('x',),[{'y':'oops'}])
    def test_duplicate_header(self):
        with self.assertRaises(gate.ExportHold):gate._render(('x','x'),[{'x':'x'}])

MUTATIONS={
    'h_wrong_authority': lambda h,g:h.update(machine_authority='APPROVED'),
    'h_wrong_release': lambda h,g:h.update(release_state='PUBLISHED'),
    'h_wrong_schema': lambda h,g:h.update(schema_version=2),
    'h_wrong_issue': lambda h,g:h.update(issue=137),
    'h_wrong_fingerprint': lambda h,g:h.update(fingerprint_sha256='0'*64),
    'g_wrong_fingerprint': lambda h,g:g.update(fingerprint_sha256='0'*64),
    'g_wrong_authority': lambda h,g:g.update(machine_authority='APPROVED'),
    'g_wrong_release': lambda h,g:g.update(release_state='PUBLISHED'),
    'g_wrong_issue': lambda h,g:g.update(issue=137),
    'g_detached_parent': lambda h,g:g.update(parent_R35_fingerprint_sha256='0'*64),
    'h_claim_missing': lambda h,g:h['claim_occurrence_review_forms'].pop(),
    'h_source_missing': lambda h,g:h['source_scope_review_forms'].pop(),
    'h_fallback_missing': lambda h,g:h['base_fallback_review_forms'].pop(),
    'g_group_missing': lambda h,g:g['globally_unreviewed_shared_url_cards'].pop(),
