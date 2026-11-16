"""R417 synthetic numeric provenance regressions. No article/safety approval."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tests')]
from test_r414_citation_locality_escrow_gate import fixture as original_fixture
import r416_cited_claim_block_gate as old
import r417_quantitative_claim_provenance_gate as gate

SOURCE_PARA='<p>Historical ledger year 1814 counted 12 sealed crates arriving at the harbor.</p>'

def fixture():
    d,m,e,c=original_fixture()
    first=d['original_articles'][0]
    key=('guide-0',first['body_candidate_git_blobs'][0])
    data=c.pop(key).decode('utf-8')
    data=data.replace('</article>',SOURCE_PARA+'</article>')
    pin=gate._r409.blob(data.encode('utf-8'))
    first['body_candidate_git_blobs']=[pin]
    c[('guide-0',pin)]=data.encode('utf-8')
    e['guide-0']=(data,data)
    return d,m,e,c


def revise(fn):
    d,m,e,c=fixture()
    html=fn(e['guide-0'][0]); e['guide-0']=(html,html)
    return d,m,e,c

class Basic(unittest.TestCase):
    def test_complete_synthetic_35_slate_keeps_draft_hold(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(r['integrity_ok'],r['errors']);self.assertEqual(r['draft_checks'],70)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
        for f in ['eligible','publication_approved','qualified_safety_approved']:
            self.assertFalse(r[f])
    def test_source_pinned_count(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        x=[z for z in r['details'] if z['slug']=='guide-0']
        self.assertEqual([s['original_uncited_quantitative_blocks'] for s in x],[1,1])
    def test_prior_accepts_modified_uncited_year_but_new_gate_blocks(self):
        d,m,e,c=revise(lambda s:s.replace('year 1814','year 1815'))
        self.assertTrue(old.check(d,m,e,c,test_only=True)['integrity_ok'])
        new=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(new['integrity_ok']);self.assertIn('R417 original quantitative',str(new['errors']))
    def test_prior_accepts_modified_uncited_count_but_new_gate_blocks(self):
        d,m,e,c=revise(lambda s:s.replace('counted 12','counted 90'))
        self.assertTrue(old.check(d,m,e,c,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_original_evidence_duplicate_replay_quarantined(self):
        d,m,e,c=revise(lambda s:s.replace('</article>',SOURCE_PARA+'</article>'))
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_unrelated_non_action_archival_appendix_allowed(self):
        d,m,e,c=revise(lambda s:s.replace('</article>',
            '<p>The catalog refers to 2021 library microfilm accession.</p></article>'))
        self.assertTrue(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_new_quantity_with_household_action_caught(self):
        d,m,e,c=revise(lambda s:s.replace('</article>',
            '<p>Give children 8 tablets every 3 hours.</p></article>'))
        self.assertTrue(old.check(d,m,e,c,test_only=True)['integrity_ok'])
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok']);self.assertIn('novel uncited',str(r['errors']))
    def test_new_numeric_without_modal_caught(self):
        d,m,e,c=revise(lambda s:s.replace('</article>',
            '<p>Mix 3 gallons of water in the emergency container.</p></article>'))
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok']);self.assertIn('quantitative instruction',str(r['errors']))
    def test_candidate_blob_mismatch_blocks(self):
        d,m,e,c=fixture();k=next(iter(c));c[k]=c[k]+b'changed'
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_without_original_not_authentic(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c)
        self.assertFalse(r['integrity_ok'])
    def test_result_does_not_expose_private_content(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        s=json.dumps(r)
        self.assertNotIn('Historical ledger year',s);self.assertNotIn('Give children',s)
    def test_does_not_mutate_any_input(self):
        d,m,e,c=fixture();z=copy.deepcopy((d,m,e,c))
        gate.check(d,m,e,c,test_only=True);self.assertEqual(z,(d,m,e,c))
    def test_cli_missing_authentic_inputs_holds_with_exit_two(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r417_quantitative_claim_provenance_gate.py'),
            '/missing/a','/missing/b','/missing/c','/missing/d'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)['release_state'],'DRAFT_HARD_HOLD')
    def test_source_markers_preserve_exact_occurrences(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        self.assertEqual(r['draft_checks'],70)
    def test_blank_empty_quantified_evidence(self):
        p=gate._r416.extract('<article><p>Purely words here.</p></article>')
        self.assertEqual(gate.quantitative_original(p),[])
    def test_lexical_casefold_and_units(self):
        p=gate._r416.extract('<article><p>Give BABIES 2 Tablets.</p></article>')
        self.assertEqual(sum(gate.numeric_action_blocks(p).values()),1)
    def test_numeric_count_spelled_out(self):
        p=gate._r416.extract('<article><p>Give children eight pills today.</p></article>')
        self.assertEqual(sum(gate.numeric_action_blocks(p).values()),1)
    def test_no_source_approval_from_numerical_match(self):
        d,m,e,c=fixture();r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(any('cannot establish' in s for s in r['warnings']))
    def test_wordpress_only_mutation_blocks(self):
        d,m,e,c=fixture();e['guide-0']=(e['guide-0'][0].replace('year 1814','year 1817'),e['guide-0'][1])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_rejects_excessive_blocks(self):
        s='<article>'+('<p>archive</p>'*2001)+'</article>'
        p=gate._r416.extract(s)
        with self.assertRaises(ValueError):gate.align_original_blocks(p,p)

class NumericMutations(unittest.TestCase):pass
ALTERATIONS=[str(i) for i in range(1800,1825) if i!=1814] + [str(i) for i in range(25,50)]
for n,replacement in enumerate(ALTERATIONS):
    def test(self,rep=replacement):
        d,m,e,c=revise(lambda s:s.replace('1814 counted','%s counted'%rep))
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'],rep)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    setattr(NumericMutations,'test_original_quantitative_year_'+str(n).zfill(2),test)

class AddedQuantitativeSafetyReview(unittest.TestCase):pass
ADDED=[
'Give children 8 tablets every 3 hours.',
'Mix 2 gallons of water to treat the emergency supply.',
'Cook meat for 15 minutes.',
'Store the freezer food for 30 days.',
'Add 4 drops of bleach to water.',
'Use 1 canning pressure cycle.',
'Take 2 pills with a drink.',
'Dose medical drops every 6 hours.',
'Heat emergency shelter to 100 degrees.',
'Replace generator fuel in 5 minutes.',
'Boil the drinking water for 3 seconds.',
'Give a baby four tablets.',
]
for n,paragraph in enumerate(ADDED):
    def test(self,para=paragraph):
        d,m,e,c=revise(lambda s:s.replace('</article>','<p>'+para+'</p></article>'))
        r=gate.check(d,m,e,c,test_only=True)
        self.assertFalse(r['integrity_ok'],para)
        self.assertTrue(any('quantitative instruction' in x or 'high-consequence' in x for x in r['errors']))
    setattr(AddedQuantitativeSafetyReview,'test_added_numeric_instruction_'+str(n).zfill(2),test)

if __name__=='__main__': unittest.main()
