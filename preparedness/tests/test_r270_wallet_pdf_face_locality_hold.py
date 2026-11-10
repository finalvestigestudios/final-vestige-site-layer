"""Negative-safety regression for R270 PDF print-locality receipt; never QD PASS."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r270',ROOT/'tools/r270_wallet_pdf_face_locality_hold.py')
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
SOURCE=(ROOT/gate.HTML_PATH).read_bytes()
RECEIPT=(ROOT/gate.RECEIPT_PATH).read_bytes()
SCRIPT=(ROOT/gate.SCRIPT_PATH).read_bytes()
OBS=gate.load_receipt(RECEIPT)

class Positive(unittest.TestCase):
    def test_blob_source(self):self.assertEqual(gate.git_blob(SOURCE),gate.HTML_BLOB)
    def test_blob_receipt(self):self.assertEqual(gate.git_blob(RECEIPT),gate.RECEIPT_BLOB)
    def test_blob_script(self):self.assertEqual(gate.git_blob(SCRIPT),gate.SCRIPT_BLOB)
    def test_safe_audit(self):self.assertEqual(gate.audit(ROOT,lambda root,path:(root/path).read_bytes())['state'],gate.HOLD)
    def test_direct_inspect(self):self.assertEqual(gate.inspect(SOURCE,RECEIPT,SCRIPT)['state'],gate.HOLD)
    def test_pdf_receipt_not_certification(self):
        result=gate.validate(OBS)
        self.assertTrue(result['printed_notice_8pt_risk_requires_human_review'])
        for f in gate.FALSE_FLAGS:self.assertIs(result[f],False)
    def test_both_faces_have_distinct_source_fields(self):
        self.assertEqual(OBS['javascript_modes']['false']['front']['verified_field_labels'],gate.FRONT_FIELDS)
        self.assertEqual(OBS['javascript_modes']['false']['back']['verified_field_labels'],gate.BACK_FIELDS)
    def test_modes_equal(self):self.assertEqual(OBS['javascript_modes']['false'],OBS['javascript_modes']['true'])

# Mutation tests exercise field-level constraints before the authenticated Git-blob check.
MUTATORS={
 'schema':lambda x:x.update(schema='v2'),
 'state':lambda x:x.update(state='QD_PASS'),
 'source_sha':lambda x:x.update(source_git_blob='0'*40),
 'page_a4':lambda x:x.update(pdf_page_size_pt=[595,842]),
 'page_letter_wrong':lambda x:x.update(pdf_page_size_pt=[612,793]),
 'scope_drift':lambda x:x.update(proof_scope='fully certified safe printed card'),
 'chromium_drift':lambda x:x.update(chromium_version='1.0'),
 'risk_false':lambda x:x.update(printed_warning_below_internal_9pt_review_floor=False),
 'paper_claim':lambda x:x.update(physical_paper_cut_fold_not_tested=False),
 'mode_missing':lambda x:x.update(javascript_modes={'false':x['javascript_modes']['false']}),
 'extra_mode':lambda x:x['javascript_modes'].update(other=x['javascript_modes']['true']),
 'js_diff':lambda x:x['javascript_modes']['true']['front'].update(status_count=2),
 'js_on_page':lambda x:x['javascript_modes']['true'].update(page_count=2),
 'js_off_badges':lambda x:x['javascript_modes']['false'].update(pdf_text_label_count=1),
 'front_status':lambda x:x['javascript_modes']['false']['front'].update(status_count=0),
 'back_status':lambda x:x['javascript_modes']['false']['back'].update(status_count=0),
 'front_privacy':lambda x:x['javascript_modes']['false']['front'].update(privacy_count=0),
 'back_privacy':lambda x:x['javascript_modes']['false']['back'].update(privacy_count=2),
 'front_bounds':lambda x:x['javascript_modes']['false']['front'].update(text_inside_expected_cutout_bounds=False),
 'back_bounds':lambda x:x['javascript_modes']['false']['back'].update(text_inside_expected_cutout_bounds=False),
 'front_field_missing':lambda x:x['javascript_modes']['false']['front'].update(verified_field_labels=['Telephone:']),
 'back_field_missing':lambda x:x['javascript_modes']['false']['back'].update(verified_field_labels=['Backup contact:']),
 'front_field_unsafe':lambda x:x['javascript_modes']['false']['front'].update(verified_field_labels=['Child password:']),
 'back_field_unsafe':lambda x:x['javascript_modes']['false']['back'].update(verified_field_labels=['Medical history:']),
 'front_font_tiny':lambda x:x['javascript_modes']['false']['front'].update(min_warning_font_pt=3),
 'back_font_tiny':lambda x:x['javascript_modes']['false']['back'].update(min_warning_font_pt=3),
 'front_font_large':lambda x:x['javascript_modes']['false']['front'].update(max_warning_font_pt=11),
 'back_font_large':lambda x:x['javascript_modes']['false']['back'].update(max_warning_font_pt=11),
 'front_font_reverse':lambda x:x['javascript_modes']['false']['front'].update(min_warning_font_pt=8.2,max_warning_font_pt=7.8),
 'back_font_reverse':lambda x:x['javascript_modes']['false']['back'].update(min_warning_font_pt=8.2,max_warning_font_pt=7.8),
 'front_missing':lambda x:x['javascript_modes']['false'].pop('front'),
 'back_missing':lambda x:x['javascript_modes']['false'].pop('back'),
 'unexpected_field':lambda x:x['javascript_modes']['false']['back'].update(accessibility_approved=True),
 'extra_pdf_key':lambda x:x['javascript_modes']['false'].update(payment_received=True),
 'missing_count':lambda x:x['javascript_modes']['false']['front'].pop('status_count'),
 'wrong_type':lambda x:x['javascript_modes']['false']['front'].update(min_warning_font_pt='8'),
}
for flag in gate.FALSE_FLAGS:
    MUTATORS['approval_'+flag]=lambda x,flag=flag:x.update({flag:True})

class Mutations(unittest.TestCase):pass
for name,edit in MUTATORS.items():
    def run(self,edit=edit):
        x=copy.deepcopy(OBS)
        edit(x)
        with self.assertRaises(ValueError):gate.validate(x)
    setattr(Mutations,'test_reject_'+name,run)

class BadInputs(unittest.TestCase):pass
BAD={
 'empty':b'', 'array':b'[]', 'null':b'null',
 'broken':b'{"schema":', 'invalid_utf8':b'\xff',
 'duplicate_top':b'{"foo":false,"foo":true}',
 'duplicate_nested':b'{"foo":{"ok":false,"ok":true}}',
 'nan':b'{"a":NaN}', 'infinite':b'{"a":Infinity}',
 'huge':b' '*100001,
}
for name,data in BAD.items():
    def test(self,data=data):
        with self.assertRaises(ValueError):gate.load_receipt(data)
    setattr(BadInputs,'test_reject_'+name,test)

class IdentityTamper(unittest.TestCase):
    def test_source_appended(self):
        with self.assertRaises(ValueError):gate.inspect(SOURCE+b'!',RECEIPT,SCRIPT)
    def test_source_bom(self):
        with self.assertRaises(ValueError):gate.inspect(b'\xef\xbb\xbf'+SOURCE,RECEIPT,SCRIPT)
    def test_script_appended(self):
        with self.assertRaises(ValueError):gate.inspect(SOURCE,RECEIPT,SCRIPT+b'#')
    def test_receipt_appended(self):
        with self.assertRaises(ValueError):gate.inspect(SOURCE,RECEIPT+b' ',SCRIPT)
    def test_receipt_semantic_edit(self):
        changed=RECEIPT.replace(b'DRAFT_HARD_HOLD',b'RELEASE_PASS',1)
        with self.assertRaises(ValueError):gate.inspect(SOURCE,changed,SCRIPT)
    def test_reject_string_identity(self):
        with self.assertRaises(ValueError):gate.git_blob('not bytes')

if __name__=='__main__':unittest.main()
