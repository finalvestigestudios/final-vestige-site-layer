"""R212 synthetic evidence-gate regression; no authentic drafts are modified."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('r212', HERE/'tools'/'r212_citation_exception_receipts.py')
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def j(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')


def fixture():
    pool = {'sources': [
        {'id': 'cdc-find-clean-water', 'url': gate.HELD['cdc-find-clean-water']['url'],
         'human_link_check': False},
        {'id': 'ordinary-seven', 'url': 'https://example.org/7', 'human_link_check': False}
    ]}
    frag = {'sources': [
        {'id': 'start-ready-plan', 'url': gate.HELD['start-ready-plan']['url'],
         'human_link_check': False},
        {'id': 'ordinary-twenty', 'url': 'https://example.org/20', 'human_link_check': False}
    ]}
    body7 = ('<p>{{cite:ordinary-seven}}</p>'*49 +
             '<li>Water heater or melted ice? {{cite:cdc-find-clean-water}}</li>' +
             '<li>Fuel exposure is a different risk. {{cite:cdc-find-clean-water}}</li>')
    body20 = ('<p>{{cite:ordinary-twenty}}</p>'*63 +
              '<li>Household languages {{cite:start-ready-plan}}</li>')
    meta7 = {'n': 7, 'slug': 'homemade-water-filters', 'status': {'publish': 'draft'},
             'safety_review': {'state': 'pending'}, 'source_use': {'ordinary-seven': 'Evidence stated.'}}
    meta20 = {'n': 20, 'slug': 'preparedness-real-households', 'status': {'publish': 'draft'},
              'safety_review': {'state': 'pending'}, 'source_use': {'ordinary-twenty': 'Evidence stated.'}}
    return {
        gate.A7+'.body.html': body7.encode(), gate.A7+'.meta.json': j(meta7),
        gate.A20+'.body.html': body20.encode(), gate.A20+'.meta.json': j(meta20),
        gate.REGISTER: j(pool), gate.START: j(frag),
    }


def inspect_files(files, pins=None):
    pins = pins if pins is not None else {path: gate.blob_sha(raw if type(raw) is bytes else b'INVALID') for path, raw in files.items()}
    return gate.evaluate(files, expected=pins)


class ReceiptGate(unittest.TestCase):
    def setUp(self):
        self.data = fixture()

    def check_invalid(self):
        result = inspect_files(self.data)
        self.assertEqual(result['state'], gate.INVALID, result)
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['independent_qd_pass'])
        self.assertFalse(result['medically_safe'])

    def test_expected_exact_three_held(self):
        result = inspect_files(self.data)
        self.assertEqual(result['state'], gate.HOLD, result)
        self.assertEqual(len(result['held_occurrences']), 3)
        self.assertFalse(result['human_link_check_complete'])
        self.assertFalse(result['source_claim_review_complete'])
        self.assertEqual([x['article'] for x in result['held_occurrences']], [7,7,20])
        self.assertEqual(len(set(x['receipt_sha256'] for x in result['held_occurrences'])), 3)
        self.assertTrue(all(x['claim_support_review']=='PENDING' for x in result['held_occurrences']))

    def test_report_is_deterministic(self):
        self.assertEqual(inspect_files(self.data),inspect_files(copy.deepcopy(self.data)))

    def test_bad_original_blob_pin(self):
        pins={p:gate.blob_sha(b) for p,b in self.data.items()}
        pins[gate.REGISTER]='0'*40
        self.assertEqual(inspect_files(self.data,pins)['state'],gate.INVALID)

    def test_missing_source_file(self):
        del self.data[gate.REGISTER];self.check_invalid()

    def test_extra_file(self):
        self.data['unexpected.txt']=b'x';self.check_invalid()

    def test_nonbyte_source(self):
        self.data[gate.A7+'.body.html']='text';self.check_invalid()

    def test_duplicate_json_keys_rejected(self):
        self.data[gate.A7+'.meta.json']=b'{"n":7,"n":7}';self.check_invalid()

    def test_nonfinite_json_rejected(self):
        self.data[gate.A20+'.meta.json']=b'{"n":NaN}';self.check_invalid()

    def test_broken_utf8_rejected(self):
        self.data[gate.START]=b'\xff';self.check_invalid()

    def test_publish_state_rejected(self):
        m=json.loads(self.data[gate.A7+'.meta.json']);m['status']['publish']='publish'
        self.data[gate.A7+'.meta.json']=j(m);self.check_invalid()

    def test_safety_approval_rejected(self):
        m=json.loads(self.data[gate.A20+'.meta.json']);m['safety_review']['state']='approved'
        self.data[gate.A20+'.meta.json']=j(m);self.check_invalid()

    def test_wrong_article_number_rejected(self):
        m=json.loads(self.data[gate.A20+'.meta.json']);m['n']=19
        self.data[gate.A20+'.meta.json']=j(m);self.check_invalid()

    def test_wrong_slug_rejected(self):
        m=json.loads(self.data[gate.A7+'.meta.json']);m['slug']='changed'
        self.data[gate.A7+'.meta.json']=j(m);self.check_invalid()

    def test_rewording_held_citation_requires_new_adjudication(self):
        p=gate.A7+'.body.html';self.data[p]=self.data[p].replace(b'Water heater',b'Fuel tank')
        before={p:gate.PINS[p] for p in gate.PINS}
        self.assertEqual(gate.evaluate(self.data,expected=before)['state'],gate.INVALID)

    def test_removed_cdc_citation_rejected(self):
        p=gate.A7+'.body.html';self.data[p]=self.data[p].replace(b'{{cite:cdc-find-clean-water}}',b'',1)
        self.check_invalid()

    def test_extra_cdc_citation_rejected(self):
        p=gate.A7+'.body.html';self.data[p]+=b'{{cite:cdc-find-clean-water}}'
        self.check_invalid()

    def test_malformed_marker_rejected(self):
        p=gate.A7+'.body.html';self.data[p]=self.data[p].replace(b'{{cite:ordinary-seven}}',b'{{cite:uppercase_ID}}',1)
        self.check_invalid()

    def test_added_source_explanation_still_requires_new_review(self):
        p=gate.A7+'.meta.json';m=json.loads(self.data[p]);m['source_use']['cdc-find-clean-water']='new'
        self.data[p]=j(m);self.check_invalid()

    def test_missing_other_source_explanation_rejected(self):
        p=gate.A7+'.meta.json';m=json.loads(self.data[p]);m['source_use'].clear()
        self.data[p]=j(m);self.check_invalid()

    def test_empty_other_source_explanation_rejected(self):
        p=gate.A7+'.meta.json';m=json.loads(self.data[p]);m['source_use']['ordinary-seven']=' '
        self.data[p]=j(m);self.check_invalid()

    def test_replaced_official_cdc_url_rejected(self):
        p=gate.REGISTER;x=json.loads(self.data[p]);x['sources'][0]['url']='https://example.com/incorrect'
        self.data[p]=j(x);self.check_invalid()

    def test_replaced_official_ready_url_rejected(self):
        p=gate.START;x=json.loads(self.data[p]);x['sources'][0]['url']='https://example.com/incorrect'
        self.data[p]=j(x);self.check_invalid()

    def test_duplicate_target_source_rejected(self):
        p=gate.START;x=json.loads(self.data[p]);x['sources'].append(copy.deepcopy(x['sources'][0]))
        self.data[p]=j(x);self.check_invalid()

    def test_changed_human_link_check_requires_new_review(self):
        p=gate.REGISTER;x=json.loads(self.data[p]);x['sources'][0]['human_link_check']=True
        self.data[p]=j(x);self.check_invalid()

    def test_missing_source_id_rejected(self):
        p=gate.REGISTER;x=json.loads(self.data[p]);del x['sources'][0]['id']
        self.data[p]=j(x);self.check_invalid()

    def test_noncanonical_expected_sha_rejected(self):
        pins={p:gate.blob_sha(b) for p,b in self.data.items()};pins[gate.START]='A'*40
        self.assertEqual(inspect_files(self.data,pins)['state'],gate.INVALID)

    def test_unicode_byte_span(self):
        p=gate.A7+'.body.html';self.data[p]=b'\xc3\xa9'+self.data[p]
        result=inspect_files(self.data)
        self.assertEqual(result['state'],gate.HOLD)
        first=result['held_occurrences'][0]
        raw=self.data[p]
        self.assertEqual(raw[first['byte_span'][0]:first['byte_span'][1]],b'{{cite:cdc-find-clean-water}}')

    def test_receipt_changes_with_claim_text(self):
        original=inspect_files(self.data)['held_occurrences'][0]['receipt_sha256']
        p=gate.A7+'.body.html';self.data[p]=self.data[p].replace(b'Water heater',b'Melted ice')
        modified=inspect_files(self.data)
        self.assertEqual(modified['state'],gate.HOLD)
        self.assertNotEqual(original,modified['held_occurrences'][0]['receipt_sha256'])


def make_slot_mutation(slot):
    def test(self):
        p=gate.A7+'.body.html'
        source=b'{{cite:ordinary-seven}}'
        replacement=b'{{cite:unexplained-claim}}'
        raw=self.data[p]
        loc=-1
        for _ in range(slot):
            loc=raw.find(source,loc+1)
        self.assertGreaterEqual(loc,0)
        self.data[p]=raw[:loc]+replacement+raw[loc+len(source):]
        self.check_invalid()
    return test

for slot in range(1,36):
    setattr(ReceiptGate, f'test_article_slot_{slot:02d}_no_unexplained_citation',make_slot_mutation(slot))

if __name__=='__main__':
    unittest.main()
