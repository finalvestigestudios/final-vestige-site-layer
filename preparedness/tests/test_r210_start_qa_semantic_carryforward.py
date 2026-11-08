"""R210 in-memory synthetic mutation tests. No production source writes or safety approvals."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

P=Path(__file__).resolve().parents[1]/'tools'/'r210_start_qa_semantic_carryforward.py'
spec=importlib.util.spec_from_file_location('qa_r210',P)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

def fixtures():
    slate=[{'n':n,'slug':(r.FOUR[n-1] if n<5 else f'item-{n}'),
            'gate':True,'status':'drafted-pending-safety-review'} for n in range(1,36)]
    return {
        r.PLAN: ("<li>Simulated-outage evening: leave the refrigerator, smoke and carbon monoxide alarms, "
                 "and medical or safety-critical equipment powered. Do not switch off the main breaker.</li>").encode(),
        r.KIT: ("FEMA's December 2023 fact sheet: refrigerated medications and a doctor or pharmacist. "
                "Call your doctor or pharmacist; arrange an interim-use and replacement plan. "
                "{{cite:start-fema-power-sheet}}{{cite:start-ready-power}}").encode(),
        r.SOURCES: json.dumps({'sources':[{'id':'start-redcross-older-adults','kind':'nonprofit',
                                        'notes':'A humanitarian nonprofit, not a regulator.'}]}).encode(),
        r.TAXONOMY:json.dumps({'slate':slate}).encode(),
        r.TEST:("def test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source(self): pass\n"
                "def test_register_fragments_cannot_duplicate_ids(self): pass\nfrag.write_text(entry)\n").encode(),
    }

def inspect(d):
    hashes={p:r.git_blob_sha(b) if isinstance(b,bytes) else '0'*40 for p,b in d.items()}
    return r.analyze(d,expected_oids=hashes)

class TestR210(unittest.TestCase):
    def setUp(self):self.data=fixtures()
    def assert_invalid(self, data=None):
        a=inspect(self.data if data is None else data)
        self.assertEqual(a['state'],r.INVALID,a)
        self.assertFalse(a['publication_authorized'])
        self.assertFalse(a['independent_qd_pass'])
        self.assertFalse(a['medically_safe'])
        return a
    def test_baseline_stays_hard_hold(self):
        a=inspect(self.data)
        self.assertEqual(a['state'],r.HOLD)
        self.assertEqual(len(a['authenticated_files']),5)
        self.assertEqual(len(a['review_dispositions']),5)
        self.assertEqual([x['pr'] for x in a['pending_qa']],[157,169,973])
        self.assertIsNone(a['verified_paid_orders'])
    def test_untrusted_fixture_does_not_match_real_sha(self):
        self.assert_invalid_untrusted(self.data)
    def assert_invalid_untrusted(self,data):
        a=r.analyze(data)
        self.assertEqual(a['state'],r.INVALID)
        self.assertIn('Git blob mismatch',a['errors'][0])
    def test_missing_file(self):
        del self.data[r.PLAN];self.assert_invalid()
    def test_extra_file(self):
        self.data['unapproved-source.html']=b'bad';self.assert_invalid()
    def test_string_not_bytes(self):
        self.data[r.PLAN]='text';self.assert_invalid()
    def test_old_unsafe_lights_out(self):
        self.data[r.PLAN]+=b'Switch off the main power for an evening';self.assert_invalid()
    def test_breaker_prohibition_removed(self):
        self.data[r.PLAN]=self.data[r.PLAN].replace(b'Do not switch off the main breaker',b'Please turn off the main breaker')
        self.assert_invalid()
    def test_no_simulated_drill(self):
        self.data[r.PLAN]=self.data[r.PLAN].replace(b'Simulated-outage evening',b'Drill');self.assert_invalid()
    def test_no_alarm_protection(self):
        self.data[r.PLAN]=self.data[r.PLAN].replace(b'smoke and carbon monoxide alarms',b'alarms');self.assert_invalid()
    def test_no_medical_equipment(self):
        self.data[r.PLAN]=self.data[r.PLAN].replace(b'medical or safety-critical equipment',b'things');self.assert_invalid()
    def test_no_refrigerator(self):
        self.data[r.PLAN]=self.data[r.PLAN].replace(b'refrigerator',b'fridge');self.assert_invalid()
    def test_old_absolute_medicine_instruction(self):
        self.data[r.KIT]+=b'should discard refrigerated medication unless the label says otherwise';self.assert_invalid()
    def test_no_fema_source(self):
        self.data[r.KIT]=self.data[r.KIT].replace(b'start-fema-power-sheet',b'unknown-source');self.assert_invalid()
    def test_no_ready_source(self):
        self.data[r.KIT]=self.data[r.KIT].replace(b'start-ready-power',b'unknown-source');self.assert_invalid()
    def test_no_product_replacement_plan(self):
        self.data[r.KIT]=self.data[r.KIT].replace(b'interim-use and replacement plan',b'plan');self.assert_invalid()
    def test_regulator_misclassification(self):
        d=json.loads(self.data[r.SOURCES]);d['sources'][0]['kind']='regulator';self.data[r.SOURCES]=json.dumps(d).encode();self.assert_invalid()
    def test_missing_redcross_record(self):
        self.data[r.SOURCES]=b'{"sources":[]}';self.assert_invalid()
    def test_repeated_redcross_record(self):
        d=json.loads(self.data[r.SOURCES]);d['sources'].append(copy.deepcopy(d['sources'][0]));self.data[r.SOURCES]=json.dumps(d).encode();self.assert_invalid()
    def test_duplicate_json_key_in_taxonomy(self):
        self.data[r.TAXONOMY]=b'{"slate":[],"slate":[]}';self.assert_invalid()
    def test_nan_in_source_json(self):
        self.data[r.SOURCES]=b'{"sources":NaN}';self.assert_invalid()
    def test_shrunken_article_slate(self):
        d=json.loads(self.data[r.TAXONOMY]);d['slate'].pop();self.data[r.TAXONOMY]=json.dumps(d).encode();self.assert_invalid()
    def test_no_publish_gate_test(self):
        self.data[r.TEST]=b'no source tests';self.assert_invalid()
    def test_unexpected_qa_test_edit_not_auto_accepted(self):
        self.data[r.TEST]+=b'def test_start_articles_require_human_safety_review(self): pass';self.assert_invalid()
    def test_schema_never_reports_safe(self):
        a=inspect(self.data);self.assertNotIn('PASS',a['state']);self.assertFalse(a['source_safety_verified'])
    def test_missing_checkout_cli_returns_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            status=r.main(['--checkout',str(Path(td)/'missing')]);self.assertEqual(status,3)
    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);p=base/r.PLAN;p.parent.mkdir(parents=True)
            target=base/'target.txt';target.write_text('x');p.symlink_to(target)
            with self.assertRaisesRegex(r.Violation,'symlink'):
                r.read_checkout(base)
    def test_mutate_each_sha_without_fixture_override(self):
        for name in r.PINNED:
            with self.subTest(path=name):
                d=copy.deepcopy(self.data);d[name]+=b'!'
                self.assert_invalid_untrusted(d)
    def test_mutate_each_of_35_taxonomy_rows(self):
        for n in range(1,36):
            with self.subTest(row=n):
                d=copy.deepcopy(self.data);obj=json.loads(d[r.TAXONOMY]);obj['slate'][n-1]['n']=999
                d[r.TAXONOMY]=json.dumps(obj).encode();self.assert_invalid(d)
    def test_mutate_each_of_four_gated_start_articles(self):
        for slug in r.FOUR:
            for bad in (False,'safety-approved-draft','published'):
                with self.subTest(slug=slug,bad=bad):
                    d=copy.deepcopy(self.data);obj=json.loads(d[r.TAXONOMY]);x=next(x for x in obj['slate'] if x['slug']==slug)
                    if bad is False:x['gate']=False
                    else:x['status']=bad
                    d[r.TAXONOMY]=json.dumps(obj).encode();self.assert_invalid(d)
    def test_invalid_json_encoding(self):
        self.data[r.SOURCES]=b'\xff';self.assert_invalid()
    def test_wrong_expected_sha_length(self):
        sha={k:r.git_blob_sha(v) for k,v in self.data.items()};sha[r.PLAN]='123';self.assertEqual(r.analyze(self.data,expected_oids=sha)['state'],r.INVALID)

# Separate named tests guarantee at least 36 distinct unittest cases, not just
# one test containing a for-loop. All 35 article positions are adversarially tested.
def _index_test(n):
    def test(self):
        obj=json.loads(self.data[r.TAXONOMY]);obj['slate'][n-1]['n']=-n
        self.data[r.TAXONOMY]=json.dumps(obj).encode()
        self.assert_invalid()
    return test
for _n in range(1,36):
    setattr(TestR210, f'test_article_position_{_n:02d}_tamper', _index_test(_n))

if __name__=='__main__':unittest.main()
