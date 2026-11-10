"""R269 source-bound card tests: synthetic tampering must FAIL; not a QD test."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r269',ROOT/'tools/r269_cutout_review_status_hold.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
OLD=(ROOT/gate.OLD_PATH).read_bytes()
NEW=(ROOT/gate.NEW_PATH).read_bytes()

class Positive(unittest.TestCase):
    def test_source_git_blob(self):self.assertEqual(gate.git_blob(OLD),gate.OLD_BLOB)
    def test_candidate_git_blob(self):self.assertEqual(gate.git_blob(NEW),gate.NEW_BLOB)
    def test_exact_proposal(self):self.assertEqual(gate.proposed(OLD),NEW)
    def test_original_has_no_detachable_status(self):self.assertNotIn(gate.LABEL.encode(),OLD)
    def test_strict_hold(self):
        result=gate.inspect(OLD,NEW)
        self.assertEqual(result['state'],gate.HOLD)
        for key in gate.FALSE_STATES:self.assertIs(result[key],False,key)
    def test_two_separate_face_badges(self):
        p=gate.FaceObserver();p.feed(NEW.decode());p.close()
        self.assertEqual(p.badges,[(n,gate.LABEL) for n in gate.FACE_NAMES])
    def test_safe_reader_bound(self):
        called=[]
        def read(root,path):called.append(path);return (root/path).read_bytes()
        self.assertEqual(gate.audit(ROOT,read)['state'],gate.HOLD)
        self.assertEqual(called,[gate.OLD_PATH,gate.NEW_PATH])

# Each mutation targets a materially distinct protected witness.
PATCH={
 'badge_off':(b'UNAPPROVED - DO NOT USE',b'APPROVED - SAFE'),
 'status_omitted':(b'<p class="pa-prototype-status">',b'<p>'),
 'status_font':(b'font-size:8pt; line-height:1.1',b'font-size:3pt; line-height:1.1'),
 'status_hidden':(b'pa-prototype-status {',b'pa-prototype-status { display:none;'),
 'status_transparent':(b'pa-prototype-status {',b'pa-prototype-status { color:transparent;'),
 'status_border':(b'border:1px solid #111; padding:1px 2px;',b'border:none;padding:0;'),
 'status_aria':(b'<p class="pa-prototype-status">',b'<p class="pa-prototype-status" aria-hidden="true">'),
 'source_header':(b'<!-- Unapproved',b'<!-- Approved'),
 'sheet_warning':(b'UNAPPROVED REVIEW CONCEPT.',b'REVIEW CONCEPT.'),
 'footer_release':(b'Not an approved replacement',b'An approved replacement'),
 'front_identity':(b'aria-label="Front"',b'aria-label="Shared"'),
 'back_identity':(b'aria-label="Back"',b'aria-label="Shared"'),
 'face_element':(b'<section class="pa-face"',b'<div class="pa-face"'),
 'privacy_front':(b'Privacy: This card may be lost',b'Privacy: This card cannot be lost'),
 'privacy_back':(b'Privacy: A finder can read',b'Privacy: A finder cannot read'),
 'field_1':(b'Out-of-area contact:',b'Home address:'),
 'field_2':(b'Telephone:',b'Password:'),
 'field_3':(b'Backup contact:',b'Medical ID:'),
 'field_4':(b'Backup telephone:',b'Credit card:'),
 'field_5':(b'Plan reviewed:',b'Access code:'),
 'width':(b'width:7in;',b'width:11in;'),
 'height':(b'min-height:2.125in;',b'min-height:1in;'),
 'screen_reflow':(b'max-width: 739px',b'max-width: 1px'),
 'overflow':(b'minmax(0, 1fr)',b'minmax(800px, 1fr)'),
 'print_style':(b'@media print {',b'@media screen {'),
 'body_color':(b'color:#111; background:#fff',b'color:#fff; background:#fff'),
 'privacy_font':(b'font-size:8pt; margin:.06in',b'font-size:3pt; margin:.06in'),
 'phone_label':(b'Backup telephone: ',b'Password: '),
 'header_copy':(b'<h2>Emergency contact</h2>',b'<h2>Authorized emergency card</h2>'),
 'other_header':(b'<h2>Backup contact</h2>',b'<h2>Approved document</h2>'),
 'font_family':(b'font-family:sans-serif;',b'font-family:serif;'),
 'cut_line':(b'border-right:1px dashed #111;',b'border-right:0;'),
 'privacy_body':(b'Carry only non-sensitive contact details',b'Carry sensitive passwords'),
 'scripted_link':(b'</section>\n',b'<script>alert(1)</script></section>\n'),
 'event_handler':(b'<section class="pa-face"',b'<section onclick="steal()" class="pa-face"'),
 'browser_print':(b'@page { margin:.5in; }',b'@page { margin:0; }'),
 'card_grid':(b'grid-template-columns:1fr 1fr',b'grid-template-columns:1fr 2fr'),
 'card_class':(b'class="pa-foldcard"',b'class="pa-hidden-card"'),
 'card_label':(b'aria-label="Foldable two-face concept"',b'aria-label="Approved family card"'),
 'dangerous_claim':(b'Not an approved replacement',b'Fully approved replacement'),
}
class Mutations(unittest.TestCase):pass
for name,(old,new) in PATCH.items():
    def test(self,a=old,b=new,name=name):
        self.assertIn(a,NEW,name)
        candidate=NEW.replace(a,b,1)
        self.assertNotEqual(candidate,NEW)
        with self.assertRaises(ValueError):gate.inspect(OLD,candidate)
    setattr(Mutations,'test_reject_'+name,test)

class Invalid(unittest.TestCase):pass
for name,original,candidate in [
 ('empty_old',b'',NEW),('old_bom',b'\xef\xbb\xbf'+OLD,NEW),
 ('old_added',OLD+b'!',NEW),('empty_new',OLD,b''),('new_bom',OLD,b'\xef\xbb\xbf'+NEW),
 ('new_added',OLD,NEW+b'!'),('new_trimmed',OLD,NEW[:-2]),
 ('new_duplicate_badge',OLD,NEW+gate.LABEL.encode()),
 ('new_js',OLD,NEW+b'<script>steal()</script>'),
 ('missing_front',OLD,NEW.replace(b'aria-label="Front"',b'aria-label="No"')),
 ('missing_back',OLD,NEW.replace(b'aria-label="Back"',b'aria-label="No"')),
 ('missing_status_rule',OLD,NEW.replace(gate.CSS_ADD,b'')),
]:
    def test(self,old=original,new=candidate):
        with self.assertRaises(ValueError):gate.inspect(old,new)
    setattr(Invalid,'test_reject_'+name,test)

class Parser(unittest.TestCase):
    def test_concealed(self):
        with self.assertRaises(ValueError):
            gate.FaceObserver().feed('<section class="pa-face"><p class="pa-prototype-status" hidden>review</p></section>')
    def test_nested(self):
        with self.assertRaises(ValueError):
            gate.FaceObserver().feed('<section class="pa-face"><div><p class="pa-prototype-status">review</p></div></section>')
    def test_external(self):
        with self.assertRaises(ValueError):
            gate.FaceObserver().feed('<p class="pa-prototype-status">review</p>')
    def test_injected_script(self):
        with self.assertRaises(ValueError):gate.FaceObserver().feed('<script></script>')
    def test_event_handler(self):
        with self.assertRaises(ValueError):gate.FaceObserver().feed('<div onclick="x()"></div>')

if __name__=='__main__':unittest.main()
