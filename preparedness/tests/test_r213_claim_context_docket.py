"""R213 structural tests: every test uses synthetic source bytes, NOT article approvals."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[1]

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, HERE/'tools'/path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

r212 = load('r212_citation_exception_receipts.py','r212_fixture_gate')
r213 = load('r213_claim_context_docket.py','r213_docket')

def j(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False).encode()


def fixture():
    # Two synthetic articles matching the shape/count of three unresolved original
    # citations. The 35 slots below are NOT 35 authentic article regressions.
    reg = {'sources': [{'id':'cdc-find-clean-water',
                        'url':r212.HELD['cdc-find-clean-water']['url'],
                        'human_link_check':False},
                       {'id':'ordinary-seven','url':'https://example.org/7'}]}
    start = {'sources': [{'id':'start-ready-plan',
                          'url':r212.HELD['start-ready-plan']['url'],
                          'human_link_check':False},
                         {'id':'ordinary-twenty','url':'https://example.org/20'}]}
    b7 = ('<h2>Water sources</h2>\n' + '<p>Background reference {{cite:ordinary-seven}}</p>\n'*49 +
          '<p>Drinking-water heater versus heating system, and melted ice. '
          '{{cite:cdc-find-clean-water}}</p>\n' +
          '<p>Fuel and chemical pollution cannot be treated like microbes. '
          '{{cite:cdc-find-clean-water}}</p>\n')
    b20 = ('<p>Other source {{cite:ordinary-twenty}}</p>\n'*63 +
           '<p>Family contact plans should include language needs. '
           '{{cite:start-ready-plan}}</p>\n')
    m7={'n':7,'slug':'homemade-water-filters','status':{'publish':'draft'},
        'safety_review':{'state':'pending'},
        'source_use':{'ordinary-seven':'Synthetic evidence explanation.'}}
    m20={'n':20,'slug':'preparedness-real-households','status':{'publish':'draft'},
         'safety_review':{'state':'pending'},
         'source_use':{'ordinary-twenty':'Synthetic evidence explanation.'}}
    return {r212.A7+'.body.html':b7.encode(), r212.A7+'.meta.json':j(m7),
            r212.A20+'.body.html':b20.encode(),r212.A20+'.meta.json':j(m20),
            r212.REGISTER:j(reg),r212.START:j(start)}


def pins(raw):
    return {path:r212.blob_sha(data) for path,data in raw.items()}


def check(raw, expected=None):
    return r213.evaluate(raw, synthetic_pins=pins(raw) if expected is None else expected)


class DocketRegression(unittest.TestCase):
    def setUp(self):
        self.data=fixture()
        self.original_pins=pins(self.data)

    def assert_hold(self,report):
        self.assertEqual(report['state'],r213.HOLD,report)
        self.assertEqual(len(report['claims']),3)
        self.assertFalse(report['publication_authorized'])
        self.assertFalse(report['independent_qd_pass'])
        self.assertFalse(report['medically_safe'])
        self.assertFalse(report['review_complete'])

    def assert_invalid(self,report):
        self.assertEqual(report['state'],r213.INVALID,report)
        self.assertFalse(report['publication_authorized'])
        self.assertFalse(report['independent_qd_pass'])
        self.assertFalse(report['medically_safe'])
        self.assertFalse(report['review_complete'])
        self.assertEqual(report['claims'],[])

    def test_01_valid_synthetic_snapshot_still_hard_hold(self):
        self.assert_hold(check(self.data))

    def test_02_replay_same_raw_same_docket(self):
        self.assertEqual(check(self.data), check(copy.deepcopy(self.data)))

    def test_03_distinct_immutable_receipts(self):
        records=check(self.data)['claims']
        self.assertEqual(len(set(x['receipt_sha256'] for x in records)),3)
        self.assertEqual([x['article'] for x in records],[7,7,20])

    def test_04_claims_preserve_exact_byte_spans(self):
        report=check(self.data)
        for claim in report['claims']:
            b=self.data[(r212.A7 if claim['article']==7 else r212.A20)+'.body.html']
            expected=('{{cite:'+claim['source_id']+'}}').encode()
            self.assertEqual(b[claim['source_start_byte']:claim['source_end_byte']],expected)

    def test_05_excerpt_sha_correct(self):
        for rec in check(self.data)['claims']:
            self.assertEqual(hashlib.sha256(rec['context_excerpt'].encode()).hexdigest(),
                             rec['context_excerpt_sha256'])

    def test_06_readable_and_no_html_tags_in_claim_preview(self):
        for claim in check(self.data)['claims']:
            self.assertIn(' ',claim['context_excerpt'])
            self.assertNotIn('<p>',claim['context_excerpt'])
            self.assertGreater(len(claim['context_excerpt']),24)

    def test_07_human_link_unverified_even_with_context(self):
        for claim in check(self.data)['claims']:
            self.assertIs(claim['source_link_verified_by_human'],False)
            self.assertEqual(claim['editorial_decision'],'PENDING')

    def test_08_original_pins_then_single_claim_rewording_fails(self):
        self.assert_hold(check(self.data,self.original_pins))
        self.data[r212.A7+'.body.html']=self.data[r212.A7+'.body.html'].replace(b'melted ice',b'pond water')
        result=check(self.data,self.original_pins)
        self.assert_invalid(result)
        self.assertIn('source blob drift',result['errors'][0])

    def test_09_repin_synthetic_reword_changes_receipt_without_approval(self):
        original=check(self.data)['claims'][0]['receipt_sha256']
        p=r212.A7+'.body.html'
        self.data[p]=self.data[p].replace(b'melted ice',b'pond water')
        revised=check(self.data)
        self.assert_hold(revised)
        self.assertNotEqual(original,revised['claims'][0]['receipt_sha256'])

    def test_10_source_entry_link_check_true_does_not_clear_hold(self):
        p=r212.REGISTER
        data=json.loads(self.data[p]);data['sources'][0]['human_link_check']=True
        self.data[p]=j(data)
        self.assert_invalid(check(self.data))

    def test_11_renamed_article_identity_fails(self):
        p=r212.A20+'.meta.json';x=json.loads(self.data[p]);x['slug']='different';self.data[p]=j(x)
        self.assert_invalid(check(self.data))

    def test_12_changed_water_source_url_fails(self):
        p=r212.REGISTER;x=json.loads(self.data[p]);x['sources'][0]['url']='https://untrusted.test'
        self.data[p]=j(x);self.assert_invalid(check(self.data))

    def test_13_removed_held_citation_fails(self):
        p=r212.A7+'.body.html';self.data[p]=self.data[p].replace(b'{{cite:cdc-find-clean-water}}',b'',1)
        self.assert_invalid(check(self.data))

    def test_14_extra_held_citation_fails(self):
        p=r212.A20+'.body.html';self.data[p]+=b'{{cite:start-ready-plan}}'
        self.assert_invalid(check(self.data))

    def test_15_added_citation_explanation_requires_new_review(self):
        p=r212.A20+'.meta.json';x=json.loads(self.data[p]);x['source_use']['start-ready-plan']='Approved'
        self.data[p]=j(x);self.assert_invalid(check(self.data))

    def test_16_frozen_default_never_matches_synthetic(self):
        self.assert_invalid(r213.evaluate(self.data))

    def test_17_wrong_data_type_fails_closed(self):
        self.assert_invalid(r213.evaluate(None))

    def test_18_citation_unicoded_byte_span_and_receipt(self):
        p=r212.A7+'.body.html';self.data[p]='é'.encode()+self.data[p]
        self.assert_hold(check(self.data))

    def test_19_duplicate_key_in_source_metadata_fails(self):
        p=r212.A7+'.meta.json';self.data[p]=b'{"n":7,"n":7}'
        self.assert_invalid(check(self.data))

    def test_20_promoting_draft_publishing_fails(self):
        p=r212.A7+'.meta.json';x=json.loads(self.data[p]);x['status']['publish']='publish'
        self.data[p]=j(x);self.assert_invalid(check(self.data))


def make_slot_test(slot, kind):
    def test(self):
        # Each mutation uses the ORIGINAL matched six-file pin set, and the
        # baseline is demonstrably accepted as HOLD. Therefore rejection is
        # attributable to this specific change, not preexisting pin failure.
        before=check(self.data,self.original_pins)
        self.assert_hold(before)
        p=r212.A7+'.body.html'
        marker=b'{{cite:ordinary-seven}}'
        raw=self.data[p]
        loc=-1
        for _ in range(slot):
            loc=raw.find(marker,loc+1)
        self.assertGreaterEqual(loc,0)
        if kind=='citation':
            new=b'{{cite:unexplained-claim}}'
            self.data[p]=raw[:loc]+new+raw[loc+len(marker):]
        elif kind=='adjacent_text':
            # Alter evidence text without changing token count or position.
            pos=raw.rfind(b'Background',0,loc)
            self.assertGreaterEqual(pos,0)
            self.data[p]=raw[:pos]+b'Forgery___'+raw[pos+len(b'Background'):]
        else:
            raise AssertionError(kind)
        after=check(self.data,self.original_pins)
        self.assert_invalid(after)
        self.assertIn('source blob drift',after['errors'][0])
        self.assertEqual(self.data[r212.A20+'.body.html'],fixture()[r212.A20+'.body.html'])
    return test

for slot in range(1,36):
    for kind in ('citation','adjacent_text'):
        setattr(DocketRegression, f'test_r213_{kind}_{slot:02d}_pinned_replay', make_slot_test(slot,kind))

if __name__=='__main__':
    unittest.main()
