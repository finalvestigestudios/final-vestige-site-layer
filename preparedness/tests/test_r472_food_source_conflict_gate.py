"""Synthetic-only R472 P0 food source/version conflict tests; no public/CMS writes."""
import importlib.util
from pathlib import Path
from copy import deepcopy
import unittest

SRC = Path(__file__).resolve().parents[1] / 'tools/r472_food_source_conflict_gate.py'
spec = importlib.util.spec_from_file_location('r472_food_gate', SRC)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

SITE_A = ('<li><strong>Pork and wild game:</strong> NCHFP says to treat the meat for '
          '<em>Trichinella</em> by freezing at 0°F for at least 30 days.'
          '{{cite:nchfp-jerky}}</li>')
SITE_B = ('<tr><th><em>Trichinella</em></th><td>Pork and wild game.</td>'
          '<td>Freeze 0°F for 30 days.{{cite:nchfp-jerky}}</td></tr>')
META = {'n': 11, 'slug': 'safe-jerky-dehydration',
        'status': {'publish': 'draft'},
        'safety_review': {'state':'pending','reviewer':None,'date':None},
        'source_use': {'nchfp-jerky': 'Trichinella freezing, wild game reading scope'}}

class FoodSourceHoldTests(unittest.TestCase):
    def setUp(self):
        self.body = SITE_A + '\n' + SITE_B
        self.meta = deepcopy(META)
    def test_original_two_risk_sites_remain_held(self):
        result = gate.audit(self.body, self.meta)
        self.assertEqual(result['flagged_original_claim_sites'], 2)
        self.assertFalse(result['may_publish'])
        self.assertFalse(result['qualified_qd_pass'])
        self.assertTrue(result['human_adjudication_required'])
    def test_CDC_and_NCHFP_not_silently_equated(self):
        r=gate.audit(self.body,self.meta)
        self.assertEqual(len(r['source_urls']),4)
        self.assertIn('CDC/USDA',r['source_version_question'])
    def test_cli_is_always_nonapproval_even_without_checkout(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as td:
            self.assertEqual(gate.main(['--root',td]),2)
    def test_missing_claim_site_rejected(self):
        with self.assertRaises(gate.SafetyHold):
            gate.audit(SITE_A, self.meta)
    def test_extra_claim_site_rejected(self):
        with self.assertRaises(gate.SafetyHold):
            gate.audit(self.body + SITE_A, self.meta)
    def test_citation_removed_rejected(self):
        with self.assertRaises(gate.SafetyHold):
            gate.audit(self.body.replace('{{cite:nchfp-jerky}}',''), self.meta)
    def test_source_use_is_not_safety_approval(self):
        self.assertFalse(gate.audit(self.body,self.meta)['medical_or_food_safety_verified'])
    def test_duplicate_metadata_key_rejected(self):
        with self.assertRaises(gate.SafetyHold):
            gate.strict_json(b'{"status":{},"status":{}}')
    def test_nested_duplicate_metadata_key_rejected(self):
        with self.assertRaises(gate.SafetyHold):
            gate.strict_json(b'{"status":{"publish":"draft","publish":"live"}}')
    def test_git_blob_calculation_is_reproducible(self):
        self.assertEqual(gate.git_blob(b''),'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391')
    def test_nearby_context_is_not_counted_as_unrelated_hazard(self):
        sample='<li>Freeze blueberries for 30 days at 0°F.</li>'
        self.assertEqual(gate.evidence_sites(sample),[])
    def test_pork_only_CDC_rule_not_mislabeled_as_wild_game(self):
        sample='<li>Freeze pork at 5°F for 20 days.</li>'
        self.assertEqual(gate.evidence_sites(sample),[])

# Each dynamic test is a separately reported regression, not a hidden subtest.
def mutate_meta_case(field, value):
    def test(self):
        meta=deepcopy(self.meta)
        if field in ('slug','n'):
            meta[field]=value
        elif field=='publish':
            meta['status'][field]=value
        elif field in ('state','reviewer','date'):
            meta['safety_review'][field]=value
        else:
            meta['source_use']=value
        with self.assertRaises(gate.SafetyHold):
            gate.audit(self.body,meta)
    return test

CASES=[('slug',x) for x in ('wrong','',None,0,'jerky')]
CASES += [('n',x) for x in (10,12,0,None,'11')]
CASES += [('publish',x) for x in ('published','ready','live',None,False,'QD_PASS')]
CASES += [('state',x) for x in ('passed','safe','approved','QD_PASS',None,False,'reviewed')]
CASES += [('reviewer',x) for x in ('Dr X','agent','Claude',True,'QD',1)]
CASES += [('date',x) for x in ('2026-11-18',True,1,'approved',False)]
CASES += [('source_use',x) for x in ({},{'nchfp-jerky':'safe'}, {'nchfp-jerky':'Trichinella'}, None,[],{'other':'wild game Trichinella'})]
for i,(field,value) in enumerate(CASES):
    setattr(FoodSourceHoldTests,f'test_metadata_mutation_{i:02d}_{field}',mutate_meta_case(field,value))

def mutate_body_case(edit):
    def test(self):
        with self.assertRaises(gate.SafetyHold):
            gate.audit(edit(self.body),self.meta)
    return test

EDITS=[lambda b: b.replace('30 days','30 years'),
       lambda b: b.replace('0°F','0 C'),
       lambda b: b.replace('Freeze','Cool'),
       lambda b: b.replace('freezing','refrigerating'),
       lambda b: b.replace('{{cite:nchfp-jerky}}','{{cite:unsupported}}'),
       lambda b: b.replace('Trichinella','other hazards').replace('wild game','domestic pork'),
       lambda b: b.replace('Trichinella','other hazards').replace('Pork and wild game','pork'),
       lambda b: b.replace('</tr>','</td>')]
for i,edit in enumerate(EDITS):
    setattr(FoodSourceHoldTests,f'test_body_mutation_{i:02d}',mutate_body_case(edit))

if __name__=='__main__': unittest.main()
