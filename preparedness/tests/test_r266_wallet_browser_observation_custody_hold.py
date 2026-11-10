"""R266 bounded-browser evidence protection; synthetic adversarial cases only.
The separate real Chromium smoke was performed on candidate bytes matching Git.
No successful test is a privacy, medical or WordPress release decision.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'tools/r266_wallet_browser_observation_custody_hold.py'
spec = importlib.util.spec_from_file_location('r266', P)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
HTML = (ROOT / gate.CANDIDATE_PATH).read_bytes()
RECEIPT = (ROOT / gate.OBSERVATION_PATH).read_bytes()

def prior():
    return {'state': gate.HOLD, 'candidate_git_blob': gate.CANDIDATE_BLOB,
            'ready_for_wordpress': False, 'safe_to_carry_certified': False,
            'real_browser_and_cutout_qa_completed': False}

def check(candidate=HTML, receipt=RECEIPT, previous=None):
    return gate.inspect(candidate, receipt, prior() if previous is None else previous)

def evidence_change(k, v):
    d = json.loads(RECEIPT)
    d[k] = v
    return (json.dumps(d, ensure_ascii=False, indent=2) + '\n').encode()

class Positive(unittest.TestCase):
    def test_strict_blob(self): self.assertEqual(gate.git_blob(HTML),gate.CANDIDATE_BLOB)
    def test_receipt_checksum(self):self.assertEqual(check()['receipt_git_blob'],gate.git_blob(RECEIPT))
    def test_observation(self):self.assertTrue(check()['bounded_chromium_print_observation_recorded'])
    def test_still_held(self):self.assertEqual(check()['state'],gate.HOLD)
    def test_overflow_witness(self):self.assertTrue(check()['mobile_horizontal_overflow_observed'])
    def test_no_pipeline_pass(self):self.assertIs(check()['full_native_pipeline_executed'],False)
    def test_no_publication(self):self.assertIs(check()['ready_for_wordpress'],False)
    def test_not_review(self):self.assertTrue(check()['single_browser_is_not_independent_accessibility_or_privacy_approval'])
    def test_all_approvals_false(self):
        for k in gate.NO_APPROVAL:self.assertIs(check()[k],False)
    def test_recognizes_original_pin(self):self.assertEqual(check()['candidate_git_blob'],gate.CANDIDATE_BLOB)

class Negative(unittest.TestCase):
    def test_candidate_drift(self):
        with self.assertRaises(ValueError):check(candidate=HTML+b'X')
    def test_candidate_not_bytes(self):
        with self.assertRaises(ValueError):check(candidate=HTML.decode())
    def test_missing_receipt(self):
        with self.assertRaises(ValueError):check(receipt=b'')
    def test_receipt_not_bytes(self):
        with self.assertRaises(ValueError):check(receipt='bad')
    def test_nonutf8(self):
        with self.assertRaises(ValueError):check(receipt=RECEIPT+b'\xff')
    def test_invalid_json(self):
        with self.assertRaises(ValueError):check(receipt=b'{'*1024)
    def test_duplicate_key(self):
        inserted=RECEIPT.replace(b'"state": "DRAFT_HARD_HOLD",',b'"state": "DRAFT_HARD_HOLD", "state":"DRAFT_HARD_HOLD",')
        with self.assertRaises(ValueError):check(receipt=inserted)
    def test_extra_key(self):
        with self.assertRaises(ValueError):check(receipt=evidence_change('revenue','100000'))
    def test_missing_key(self):
        d=json.loads(RECEIPT);del d['pdf_pages_observed']
        with self.assertRaises(ValueError):check(receipt=json.dumps(d).encode())
    def test_previous_missing(self):
        with self.assertRaises(ValueError):check(previous={})
    def test_previous_wrong_type(self):
        with self.assertRaises(ValueError):check(previous='DRAFT_HARD_HOLD')
    def test_previous_wrong_git_blob(self):
        p=prior();p['candidate_git_blob']='0'*40
        with self.assertRaises(ValueError):check(previous=p)
    def test_previous_wordpress_pass(self):
        p=prior();p['ready_for_wordpress']=True
        with self.assertRaises(ValueError):check(previous=p)
    def test_previous_browser_pass(self):
        p=prior();p['real_browser_and_cutout_qa_completed']=True
        with self.assertRaises(ValueError):check(previous=p)
    def test_previous_carry_pass(self):
        p=prior();p['safe_to_carry_certified']=True
        with self.assertRaises(ValueError):check(previous=p)

# One independently named rejecting mutation per contract field.
# These are not substituted for genuine browser/paper QA.
for key, value in gate.EXPECTED.items():
    if type(value) is bool: mutation = not value
    elif type(value) is int or type(value) is float: mutation = value+1
    elif type(value) is list: mutation = value+[0]
    elif type(value) is str: mutation = value+'-altered'
    else: raise AssertionError(key)
    def make(key=key, mutation=mutation):
        def test(self):
            changed=evidence_change(key,mutation)
            self.assertNotEqual(changed,RECEIPT)
            with self.assertRaises(ValueError,msg=key):check(receipt=changed)
        return test
    setattr(Negative,'test_change_'+key,make())

if __name__ == '__main__':unittest.main()
