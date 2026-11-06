"""Synthetic, no shared repository writes. QA intent verification is not medical advice."""
from __future__ import annotations
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'r162_qa_rebase_gate.py'
spec = importlib.util.spec_from_file_location('r162_qa_rebase_gate', MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def base():
    h = ('<p>The simulated-outage evening. switch off nonessential lights; '
         'leave on the refrigerator and freezer, smoke and carbon monoxide alarms, '
         'sump pump, and medical or safety-critical equipment. '
         'Do not switch off the main breaker as a drill.</p>')
    k = ("Medicines that need refrigeration: ask your prescriber or pharmacist. "
         "Two FEMA documents, two wordings. We do not know which document FEMA intends to govern. "
         "Do not stop, throw away or ration a medicine. Follow the drug's label, "
         "ask about replacement. {{cite:start-fema-power-sheet}} {{cite:start-ready-power}}")
    s = {'sources': [{'id': 'start-redcross-older-adults', 'kind': 'nonprofit',
           'publisher': 'American Red Cross', 'human_link_check': False,
           'url': 'https://www.redcross.org/get-help/how-to-prepare-for-emergencies/older-adults.html'}]}
    t = {'slate': [{'slug': n, 'gate': True} for n in
         ('household-emergency-plan','three-day-kit','go-bags','preparedness-real-households')] +
         [{'slug': f'placeholder-{n:02d}', 'gate': False} for n in range(31)]}
    tests = '''def test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source(self):
    with tempfile.TemporaryDirectory() as td:
        sandbox = Path(td)
        shutil.copytree(ROOT, sandbox / 'preparedness')
        with self.assertRaisesRegex(ValueError, 'duplicate source id'): pass

def test_register_fragments_cannot_duplicate_ids(self):
    with tempfile.TemporaryDirectory() as td:
        sandbox = Path(td)
        shutil.copytree(ROOT, sandbox / 'preparedness')
        with self.assertRaisesRegex(ValueError, 'duplicate source id'): pass

def test_unverified_source_cannot_be_cited(self):
    fixture_id = 'test-fixture-unverified-source'
    src = {"verified_on": None}
    self.assertIn('unverified source', [])
'''
    return {'household': h, 'kit': k, 'sources': json.dumps(s), 'taxonomy': json.dumps(t), 'tests': tests}


class QaRebaseTests(unittest.TestCase):
    def setUp(self): self.data = base()
    def assert_bad(self, pattern):
        with self.assertRaisesRegex(ValueError, pattern): gate.verify_payload(self.data)
    def test_good_is_hold_not_approval(self):
        x=gate.verify_payload(self.data)
        self.assertEqual(x['state'],'DRAFT_HARD_HOLD')
        self.assertFalse(x['live_publication_authorized'])
        self.assertFalse(x['qualified_medical_review'])
        self.assertFalse(x['source_claim_adjudication'])
        self.assertFalse(x['independent_qd_pass'])
        self.assertFalse(x['purchasable_preparedness_sku_verified'])
    def test_no_shared_tree_writes(self):
        before=copy.deepcopy(self.data);gate.verify_payload(self.data);self.assertEqual(self.data,before)
    def test_schema_input_fails_extra(self): self.data['extra']='x';self.assert_bad('inputs')
    def test_schema_input_fails_missing(self): self.data.pop('tests');self.assert_bad('inputs')
    def test_missing_main_breaker_warning(self):
        self.data['household']=self.data['household'].replace('Do not switch off the main breaker as a drill.','')
        self.assert_bad('no-main-breaker')
    def test_old_breaker_practice_rejected(self):
        self.data['household']+='Switch off the main power'
        self.assert_bad('unsafe older')
    def test_missing_medicine_warning(self):
        self.data['kit']=self.data['kit'].replace('Do not stop, throw away or ration a medicine.','')
        self.assert_bad('refrigerated-medicine source/qualifier')
    def test_missing_uncertainty(self):
        self.data['kit']=self.data['kit'].replace('We do not know which document FEMA intends to govern.','')
        self.assert_bad('medical-source uncertainty')
    def test_source_malformed(self): self.data['sources']='{';self.assertRaises(json.JSONDecodeError,gate.verify_payload,self.data)
    def test_duplicate_redcross(self):
        s=json.loads(self.data['sources']);s['sources']+=s['sources'];self.data['sources']=json.dumps(s);self.assert_bad('Red Cross original')
    def test_missing_source(self): self.data['sources']='{"sources":[]}';self.assert_bad('Red Cross original')
    def test_nonprofit_label(self):
        s=json.loads(self.data['sources']);s['sources'][0]['kind']='regulator';self.data['sources']=json.dumps(s);self.assert_bad('incorrectly classified')
    def test_no_fake_review(self):
        s=json.loads(self.data['sources']);s['sources'][0]['human_link_check']=True;self.data['sources']=json.dumps(s);self.assert_bad('falsely upgraded')
    def test_taxonomy_short(self):
        t=json.loads(self.data['taxonomy']);t['slate'].pop();self.data['taxonomy']=json.dumps(t);self.assert_bad('35-title')
    def test_taxonomy_dup(self):
        t=json.loads(self.data['taxonomy']);t['slate'][5]['slug']=t['slate'][4]['slug'];self.data['taxonomy']=json.dumps(t);self.assert_bad('35-title')
    def test_missing_fixture_test(self):
        self.data['tests']=self.data['tests'].replace('def test_register_fragments_cannot_duplicate_ids','def test_other_name')
        self.assert_bad('missing/duplicated')
    def test_unsafe_original_fixture_dir(self):
        self.data['tests']=self.data['tests'].replace('sandbox = Path(td)', 'sandbox = Path(td)\n        frag = ROOT / "sources" / "fragments"',1)
        self.assert_bad('shared fixture')
    def test_missing_fake_source(self):
        self.data['tests']=self.data['tests'].replace('test-fixture-unverified-source','real-source')
        self.assert_bad('synthetic source test')

# 36+ independently identified mutations, plus the above control checks.
SAFETY_PHRASES = [('household', t) for t in ('The simulated-outage evening.',
    'Do not switch off the main breaker as a drill.', 'refrigerator and freezer',
    'smoke and carbon monoxide alarms','medical or safety-critical equipment','sump pump',
    'switch off nonessential lights')] + [('kit',t) for t in (
    'Medicines that need refrigeration: ask your prescriber or pharmacist',
    'Do not stop, throw away or ration a medicine', 'Two FEMA documents, two wordings',
    'start-fema-power-sheet','start-ready-power',"drug's label", 'replacement',
    'We do not know which document FEMA intends to govern')]
for i,(kind,phrase) in enumerate(SAFETY_PHRASES):
    def make(k=kind,word=phrase):
        def test(self):
            self.data[k]=self.data[k].replace(word,'',1)
            self.assert_bad('missing|absent|removed')
        return test
    setattr(QaRebaseTests, f'test_custody_phrase_{i:02d}', make())

for i,slug in enumerate(('household-emergency-plan','three-day-kit','go-bags','preparedness-real-households')):
    def make(n=slug):
        def test(self):
            t=json.loads(self.data['taxonomy']);next(a for a in t['slate'] if a['slug']==n)['gate']=False
            self.data['taxonomy']=json.dumps(t);self.assert_bad('weakened')
        return test
    setattr(QaRebaseTests, f'test_gate_{i:02d}', make())

for i,(kind,value) in enumerate((('kind','regulator'),('kind','professional-body'),
    ('publisher','FEMA'),('publisher','Red Cross'),('human_link_check',True),
    ('human_link_check','true'),('url','http://example.com'),('url','https://example.com'),
    ('id','fake-redcross-id'),('id','start-redcross-older-adult'))):
    def make(k=kind,v=value):
        def test(self):
            s=json.loads(self.data['sources']);s['sources'][0][k]=v
            self.data['sources']=json.dumps(s);self.assert_bad('Red Cross|official URL')
        return test
    setattr(QaRebaseTests,f'test_redcross_record_{i:02d}',make())

for i,(name,needle) in enumerate((('test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source','TemporaryDirectory'),
    ('test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source','copytree('),
    ('test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source','sandbox'),
    ('test_register_fragments_cannot_duplicate_ids','TemporaryDirectory'),
    ('test_register_fragments_cannot_duplicate_ids','copytree('),
    ('test_register_fragments_cannot_duplicate_ids','sandbox'),
    ('test_unverified_source_cannot_be_cited','"verified_on": None'),
    ('test_unverified_source_cannot_be_cited','unverified source'))):
    def make(n=name,word=needle):
        def test(self):
            self.data['tests']=self.data['tests'].replace(word,'',1)
            self.assert_bad('guard|synthetic')
        return test
    setattr(QaRebaseTests,f'test_fixture_requirement_{i:02d}',make())

if __name__ == '__main__': unittest.main()
