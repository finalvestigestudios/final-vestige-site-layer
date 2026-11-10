"""R271 fail-closed full wrapped warning/cutout custody, NOT release QA."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r271',ROOT/'tools/r271_full_warning_print_hold.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
PARENT=(ROOT/gate.PARENT_PATH).read_bytes()
PREVIEW=(ROOT/gate.PREVIEW_PATH).read_bytes()
RECEIPT=(ROOT/gate.RECEIPT_PATH).read_bytes()
SCRIPT=(ROOT/gate.SCRIPT_PATH).read_bytes()
OBS=gate.parse_json(RECEIPT)

class Positive(unittest.TestCase):
    def test_sha_parent(self):self.assertEqual(gate.git_blob(PARENT),gate.PARENT_BLOB)
    def test_sha_candidate(self):self.assertEqual(gate.git_blob(PREVIEW),gate.PREVIEW_BLOB)
    def test_sha_receipt(self):self.assertEqual(gate.git_blob(RECEIPT),gate.RECEIPT_BLOB)
    def test_sha_script(self):self.assertEqual(gate.git_blob(SCRIPT),gate.SCRIPT_BLOB)
    def test_delta_strict(self):self.assertTrue(gate.source_only_delta(PARENT,PREVIEW))
    def test_audit(self):self.assertEqual(gate.audit(ROOT,lambda r,p:(r/p).read_bytes())['state'],gate.STATE)
    def test_inspect(self):self.assertFalse(gate.inspect(PARENT,PREVIEW,RECEIPT,SCRIPT)['independent_qd_pass'])
    def test_all_full_text_source(self):
        for mode in OBS['js_modes']:
            for face,exp in gate.FACES.items():
                self.assertEqual(OBS['js_modes'][mode]['faces'][face]['full_privacy_text'],exp['privacy'])
    def test_all_false(self):
        self.assertEqual(set(OBS['release_flags']),set(gate.FALSE_FLAGS))
        self.assertTrue(all(v is False for v in OBS['release_flags'].values()))
    def test_no_false_legibility(self):
        self.assertIs(OBS['reader_legibility_not_assessed'],True)
        self.assertIs(OBS['physical_cut_fold_not_tested'],True)
    def test_receipt_parity(self):self.assertEqual(OBS['js_modes']['false'],OBS['js_modes']['true'])
    def test_no_script_path_bypass(self):self.assertTrue(gate.SCRIPT_PATH.startswith('tools/'))

MUT={
'schema':lambda o:o.update(schema='malicious'),
'state':lambda o:o.update(state='QD_PASS'),
'parent_blob':lambda o:o.update(parent_git_blob='f'*40),
'candidate_blob':lambda o:o.update(candidate_git_blob='f'*40),
'scope':lambda o:o.update(proof_scope='approved physical printing'),
'chromium':lambda o:o.update(chromium_version='1.0'),
'a4':lambda o:o.update(page_size_pt=[595,842]),
'cut_fold':lambda o:o.update(physical_cut_fold_not_tested=False),
'legibility':lambda o:o.update(reader_legibility_not_assessed=False),
'unknown_top':lambda o:o.update(extra='approved'),
'missing_top':lambda o:o.pop('schema'),
'missing_false_mode':lambda o:o['js_modes'].pop('false'),
'unknown_mode':lambda o:o['js_modes'].update(other=o['js_modes']['false']),
'js_bad_page':lambda o:o['js_modes']['true'].update(page_count=2),
'js_missing_faces':lambda o:o['js_modes']['false'].pop('faces'),
'js_other_face':lambda o:o['js_modes']['false']['faces'].update(other={}),
'front_status':lambda o:o['js_modes']['false']['faces']['front'].update(status='APPROVED'),
'back_status':lambda o:o['js_modes']['false']['faces']['back'].update(status='APPROVED'),
'front_heading':lambda o:o['js_modes']['false']['faces']['front'].update(heading='Emergency meds'),
'back_heading':lambda o:o['js_modes']['false']['faces']['back'].update(heading='Passwords'),
'front_truncated':lambda o:o['js_modes']['false']['faces']['front'].update(full_privacy_text='Privacy: This card may be lost'),
'back_truncated':lambda o:o['js_modes']['false']['faces']['back'].update(full_privacy_text='Privacy: A finder can read'),
'front_continuation_removed':lambda o:o['js_modes']['false']['faces']['front']['privacy_boxes_pt'].pop(),
'back_continuation_removed':lambda o:o['js_modes']['false']['faces']['back']['privacy_fonts_pt'].pop(),
'front_wrong_lines':lambda o:o['js_modes']['false']['faces']['front'].update(privacy_lines=1),
'back_wrong_lines':lambda o:o['js_modes']['false']['faces']['back'].update(privacy_lines=1),
'front_out_x':lambda o:o['js_modes']['false']['faces']['front']['privacy_boxes_pt'][1].__setitem__(0,300),
'back_out_x':lambda o:o['js_modes']['false']['faces']['back']['privacy_boxes_pt'][1].__setitem__(2,600),
'front_out_y':lambda o:o['js_modes']['false']['faces']['front']['privacy_boxes_pt'][1].__setitem__(3,221),
'back_out_y':lambda o:o['js_modes']['false']['faces']['back']['privacy_boxes_pt'][1].__setitem__(1,69),
'front_font_small':lambda o:o['js_modes']['false']['faces']['front']['privacy_fonts_pt'].__setitem__(1,7.99),
'back_font_small':lambda o:o['js_modes']['false']['faces']['back']['privacy_fonts_pt'].__setitem__(0,7.99),
'front_status_font':lambda o:o['js_modes']['false']['faces']['front'].update(status_font_pt=8.0),
'back_status_font':lambda o:o['js_modes']['false']['faces']['back'].update(status_font_pt=8.0),
'front_status_out':lambda o:o['js_modes']['false']['faces']['front'].update(status_box_pt=[0,0,20,30]),
'back_status_out':lambda o:o['js_modes']['false']['faces']['back'].update(status_box_pt=[0,0,20,30]),
'front_field_missing':lambda o:o['js_modes']['false']['faces']['front']['field_labels'].pop(),
'back_field_missing':lambda o:o['js_modes']['false']['faces']['back']['field_labels'].pop(),
'front_field_box_out':lambda o:o['js_modes']['false']['faces']['front']['field_boxes_pt'][0].__setitem__(2,650),
'back_field_box_out':lambda o:o['js_modes']['false']['faces']['back']['field_boxes_pt'][0].__setitem__(2,650),
'front_overlap':lambda o:o['js_modes']['false']['faces']['front']['field_boxes_pt'][0].__setitem__(1,120),
'back_overlap':lambda o:o['js_modes']['false']['faces']['back']['field_boxes_pt'][0].__setitem__(1,115),
'front_spoof_bounds':lambda o:o['js_modes']['false']['faces']['front'].update(cutout_bounding_box_pt=[0,0,612,792]),
'back_spoof_bounds':lambda o:o['js_modes']['false']['faces']['back'].update(cutout_bounding_box_pt=[0,0,612,792]),
'extra_face_field':lambda o:o['js_modes']['false']['faces']['front'].update(risk_approved=True),
'missing_face_field':lambda o:o['js_modes']['false']['faces']['front'].pop('privacy_lines'),
'float_string':lambda o:o['js_modes']['false']['faces']['front'].update(status_font_pt='9'),
'bool_font':lambda o:o['js_modes']['false']['faces']['front'].update(status_font_pt=True),
'bool_page':lambda o:o['js_modes']['false'].update(page_count=True),
'flags_missing':lambda o:o['release_flags'].pop('physical_print_approved'),
'flags_extra':lambda o:o['release_flags'].update(irrelevant=False),
}
for flag in gate.FALSE_FLAGS:
    MUT['approval_'+flag]=lambda o,flag=flag:o['release_flags'].__setitem__(flag,True)

class Mutations(unittest.TestCase):pass
for name,edit in MUT.items():
    def fail(self,edit=edit):
        x=copy.deepcopy(OBS);edit(x)
        with self.assertRaises(ValueError):gate.validate(x)
    setattr(Mutations,'test_reject_'+name,fail)

BAD={
'blank':b'', 'array':b'[]', 'null':b'null', 'number':b'42',
'broken':b'{"schema":', 'bad_utf8':b'\xff',
'duplicate_root':b'{"a":false,"a":true}',
'duplicate_nested':b'{"x":{"q":true,"q":false}}',
'nonfinite_nan':b'{"a":NaN}','nonfinite_inf':b'{"a":Infinity}',
'oversize':b' '*100000,
}
class Malformed(unittest.TestCase):pass
for name,data in BAD.items():
    def fail(self,data=data):
        with self.assertRaises(ValueError):gate.parse_json(data)
    setattr(Malformed,'test_reject_'+name,fail)

class AuthenticatedTamper(unittest.TestCase):
    def test_parent(self):
        with self.assertRaises(ValueError):gate.source_only_delta(PARENT+b'!',PREVIEW)
    def test_candidate(self):
        with self.assertRaises(ValueError):gate.source_only_delta(PARENT,PREVIEW+b'!')
    def test_fake_copy_update(self):
        with self.assertRaises(ValueError):gate.source_only_delta(PARENT,PREVIEW.replace(b'Privacy:',b'SAFE:',1))
    def test_script(self):
        with self.assertRaises(ValueError):gate.inspect(PARENT,PREVIEW,RECEIPT,SCRIPT+b'!')
    def test_receipt(self):
        with self.assertRaises(ValueError):gate.inspect(PARENT,PREVIEW,RECEIPT+b' ',SCRIPT)
    def test_git_blob_text(self):
        with self.assertRaises(ValueError):gate.git_blob('string')

# Reconstruct exact PDF span text from bounded witness to exercise continuation-loss checks.
FRONT_LINES=[
'Privacy: This card may be lost or photographed. Do',
'not write child names, school details, home',
'addresses, passwords, medical information or access',
'codes.']
BACK_LINES=[
'Privacy: A finder can read this card. Carry only non-',
'sensitive contact details and review before sharing.']

def synth_spans(face):
    row=OBS['js_modes']['false']['faces'][face];s=gate.FACES[face]
    texts=FRONT_LINES if face=='front' else BACK_LINES
    spans=[{'text':s['status'],'font':row['status_font_pt'],'box':row['status_box_pt']},
           {'text':s['heading'],'font':11.,'box':[s['bounds'][0]+12.,89.,s['bounds'][0]+120.,103.]}]
    spans += [{'text':txt,'font':font,'box':box} for txt,font,box in zip(texts,row['privacy_fonts_pt'],row['privacy_boxes_pt'])]
    spans += [{'text':label+' ____','font':9.,'box':box} for label,box in zip(s['fields'],row['field_boxes_pt'])]
    return copy.deepcopy(spans)

class FullTextExtraction(unittest.TestCase):
    def test_front(self):self.assertEqual(gate.face_from_pdf_spans(synth_spans('front'),'front')['full_privacy_text'],gate.FACES['front']['privacy'])
    def test_back(self):self.assertEqual(gate.face_from_pdf_spans(synth_spans('back'),'back')['full_privacy_text'],gate.FACES['back']['privacy'])
    def test_front_dropped_middle(self):
        spans=synth_spans('front');spans.pop(3)
        with self.assertRaises(ValueError):gate.face_from_pdf_spans(spans,'front')
    def test_back_dropped_continuation(self):
        spans=synth_spans('back');spans.pop(3)
        with self.assertRaises(ValueError):gate.face_from_pdf_spans(spans,'back')
    def test_back_hyphen_spacing(self):
        self.assertEqual(gate.normalized('non- sensitive'),'non-sensitive')
    def test_front_changed_copy(self):
        spans=synth_spans('front');spans[3]['text']='COMPLETELY FALSE'
        with self.assertRaises(ValueError):gate.face_from_pdf_spans(spans,'front')
    def test_back_duplicate_status(self):
        spans=synth_spans('back');spans.append(copy.deepcopy(spans[0]))
        with self.assertRaises(ValueError):gate.face_from_pdf_spans(spans,'back')
    def test_status_outside(self):
        spans=synth_spans('front');spans[0]['box']=[0,0,20,30]
        with self.assertRaises(ValueError):gate.face_from_pdf_spans(spans,'front')
    def test_small_privacy(self):
        spans=synth_spans('front');spans[2]['font']=7.99
        with self.assertRaises(ValueError):gate.face_from_pdf_spans(spans,'front')
    def test_continuation_overflow(self):
        spans=synth_spans('back');spans[3]['box'][2]=550
        with self.assertRaises(ValueError):gate.face_from_pdf_spans(spans,'back')

if __name__=='__main__':unittest.main()
