"""R267: actual local screen/print measurements are external to these tamper tests.
60+ isolated regressions; no synthetic PASS means medical, privacy, QD or WP approval.
"""
from __future__ import annotations
import copy,importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('r267',ROOT/'tools/r267_wallet_responsive_preview_hold.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
OLD=(ROOT/gate.ORIGINAL_PATH).read_bytes()
NEW=(ROOT/gate.PREVIEW_PATH).read_bytes()
REC=(ROOT/gate.RECEIPT_PATH).read_bytes()
R266={'state':gate.HOLD,'candidate_git_blob':gate.ORIGINAL_BLOB,
      'mobile_horizontal_overflow_observed':True,'full_native_pipeline_executed':False,
      'ready_for_wordpress':False}

def check(old=OLD,new=NEW,receipt=REC,prev=R266):
    return gate.inspect(old,new,receipt,prev)

def mutated_receipt(field,value):
    obj=json.loads(REC);obj[field]=value
    return (json.dumps(obj,indent=2)+'\n').encode()

class TestPositive(unittest.TestCase):
    def test_original_pin(self):self.assertEqual(gate.git_blob(OLD),gate.ORIGINAL_BLOB)
    def test_preview_pin(self):self.assertEqual(gate.git_blob(NEW),gate.PREVIEW_BLOB)
    def test_receipt_pin(self):self.assertEqual(gate.git_blob(REC),gate.RECEIPT_BLOB)
    def test_still_held(self):self.assertEqual(check()['state'],gate.HOLD)
    def test_legacy_overflow_preserved(self):self.assertTrue(check()['original_r266_overflow_negative_finding_preserved'])
    def test_exact_css_delta(self):self.assertEqual(NEW,OLD.replace(b'@media print {',gate.SCREEN_RULE+b'@media print {',1))
    def test_no_content_loss(self):self.assertEqual(NEW.replace(gate.SCREEN_RULE,b'',1),OLD)
    def test_screen_css_one(self):self.assertEqual(NEW.count(gate.SCREEN_RULE),1)
    def test_original_print_css_preserved(self):self.assertIn(b'@media print {',NEW)
    def test_no_approval(self):self.assertTrue(all(check()[k] is False for k in gate.NO_APPROVAL))
    def test_not_accessibility(self):self.assertIs(check()['accessibility_approved'],False)
    def test_not_qd(self):self.assertIs(check()['independent_qd_pass'],False)
    def test_pdf_still_8_point(self):self.assertTrue(check()['print_warning_font_is_only_8pt'])
    def test_browser_widths(self):self.assertEqual(json.loads(REC)['screen_viewports_css_px'],[320,360,390,768,1440])
    def test_original_r266_not_overwritten(self):self.assertEqual(json.loads(REC)['original_document_scroll_width_css_px'],[680,680,680,768,1440])
    def test_print_geometry(self):self.assertEqual(json.loads(REC)['print_unfolded_card_width_css_px'],672)

class TestTamper(unittest.TestCase):
    def test_missing_screen_rule(self):
        with self.assertRaises(ValueError):check(new=OLD)
    def test_duplicate_screen_rule(self):
        with self.assertRaises(ValueError):check(new=NEW.replace(gate.SCREEN_RULE,gate.SCREEN_RULE*2))
    def test_removed_print(self):
        with self.assertRaises(ValueError):check(new=NEW.replace(b'@media print {',b'@media screen {'))
    def test_script_injected(self):
        with self.assertRaises(ValueError):check(new=NEW+b'<script>alert(1)</script>')
    def test_privacy_notice_removed(self):
        with self.assertRaises(ValueError):check(new=NEW.replace(b'Privacy: A finder can read this card.',b'') )
    def test_changed_original(self):
        with self.assertRaises(ValueError):check(old=OLD+b' ')
    def test_wrong_types(self):
        for f in [lambda:check(old=OLD.decode()),lambda:check(new=NEW.decode()),lambda:check(receipt='hi'),lambda:check(prev=None)]:
            with self.subTest(f=f),self.assertRaises(ValueError):f()
    def test_duplicate_json_key(self):
        dup=REC.replace(b'"state": "DRAFT_HARD_HOLD",',b'"state": "DRAFT_HARD_HOLD", "state": "DRAFT_HARD_HOLD",')
        with self.assertRaises(ValueError):check(receipt=dup)
    def test_bad_json(self):
        with self.assertRaises(ValueError):check(receipt=b'{')
    def test_nonfinite(self):
        with self.assertRaises(ValueError):check(receipt=REC.replace(b'"date_utc": "2026-11-10"',b'"date_utc": NaN'))
    def test_extra_field(self):
        with self.assertRaises(ValueError):check(receipt=REC[:-2]+b',"approval":true}\n')

# Each mutation is a distinct independent error-rejection test, not a subTest.
for field,valid in gate.EXPECTED.items():
    if isinstance(valid,bool):bad=not valid
    elif isinstance(valid,str):bad=valid+'-altered'
    elif isinstance(valid,int):bad=valid+1
    elif isinstance(valid,list):bad=valid[:-1] if len(valid)>1 else valid+[999]
    else:continue
    def build(k,v):
        def run(self):
            with self.assertRaises(ValueError):check(receipt=mutated_receipt(k,v))
        return run
    setattr(TestTamper,'test_receipt_'+field,build(field,bad))

for field,bad in [('state','PASS'),('candidate_git_blob','0'*40),
 ('mobile_horizontal_overflow_observed',False),('full_native_pipeline_executed',True),
 ('ready_for_wordpress',True)]:
    def build(k,v):
        def run(self):
            altered=copy.deepcopy(R266);altered[k]=v
            with self.assertRaises(ValueError):check(prev=altered)
        return run
    setattr(TestTamper,'test_prior_'+field,build(field,bad))

if __name__=='__main__':unittest.main()
