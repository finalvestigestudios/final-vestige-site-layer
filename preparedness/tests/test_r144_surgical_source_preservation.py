"""Synthetic isolated adversarial tests; not a real 35-article approval."""
from copy import deepcopy
from pathlib import Path
import json
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).parent))
import r144_surgical_source_preservation as g

class ReviewGate(unittest.TestCase):
    def setUp(self):
        self.slug='three-day-kit'
        self.before='<h2 id="medicine">Medicines</h2>\n'+''.join(
            f'<p>Para {i}: consult your doctor or pharmacist before changing prescribed care and maintain detailed storage plans. {{{{cite:start-ready-power}}}}</p>\n'
            for i in range(35)) + '<h2 id="later">Later</h2><p>Do not stop, throw away or ration medicine. Call your doctor or pharmacist. Two FEMA documents, two wordings.</p>'
        self.meta={'slug':self.slug,'status':{'publish':'draft'},'safety_review':{'state':'pending'}}
        self.candidate=self.before.replace('Para 9: consult','Para 9: kindly consult')
    def check(self,candidate=None,metadata=None,slug=None):
        return g.review(self.before,self.candidate if candidate is None else candidate,
              self.meta if metadata is None else metadata,
              self.slug if slug is None else slug,baseline_sha=g.blob_sha(self.before.encode()))
    def reject(self,candidate=None,metadata=None,slug=None):
        with self.assertRaises(g.Hold): self.check(candidate,metadata,slug)
    def test_accept_review_only(self):
        r=self.check()
        self.assertEqual(r['paragraph_index'],9)
        self.assertFalse(r['publication_allowed'])
        self.assertFalse(r['automatic_merge'])
        self.assertEqual(r['independent_qd'],'NOT_APPROVED')
        self.assertEqual(r['unchanged_citation_occurrences'],35)
    def test_block_non_target(self): self.reject(slug='water-math')
    def test_block_wrong_baseline(self):
        with self.assertRaises(g.Hold): g.review(self.before,self.candidate,self.meta,self.slug)
    def test_block_no_change(self): self.reject(candidate=self.before)
    def test_block_two_paragraph_changes(self): self.reject(candidate=self.candidate.replace('Para 8:', 'Changed 8:'))
    def test_block_heading(self): self.reject(candidate=self.candidate.replace('id="medicine"','id="medical"'))
    def test_block_status(self): self.reject(metadata={**self.meta,'status':{'publish':'published'}})
    def test_block_safety_state(self): self.reject(metadata={**self.meta,'safety_review':{'state':'approved'}})
    def test_block_wrong_slug(self): self.reject(metadata={**self.meta,'slug':'wrong'})
    def test_block_citation_remove(self): self.reject(candidate=self.candidate.replace('{{cite:start-ready-power}}','',1))
    def test_block_citation_add(self): self.reject(candidate=self.candidate.replace('{{cite:start-ready-power}}','{{cite:start-ready-power}}{{cite:ready-are-you-ready}}',1))
    def test_block_bad_citation(self): self.reject(candidate=self.candidate.replace('{{cite:start-ready-power}}','{{cite:BAD}}',1))
    def test_block_shortened(self): self.reject(candidate=self.before.replace(self.before.split('<p>')[10].split('</p>')[0], 'oops'))
    def test_block_missing_warning(self): self.reject(candidate=self.candidate.replace('Two FEMA documents, two wordings','Two archival documents'))
    def test_block_unsafe_form(self): self.reject(candidate=self.candidate.replace('kindly consult','<form>kindly consult</form>'))
    def test_block_unsafe_script(self): self.reject(candidate=self.candidate.replace('kindly consult','<script>1</script> kindly consult'))
    def test_block_unsafe_link(self): self.reject(candidate=self.candidate.replace('kindly consult','<a href="/buy">kindly consult</a>'))
    def test_block_hidden(self): self.reject(candidate=self.candidate.replace('kindly consult','<span aria-hidden="true">kindly consult</span>'))
    def test_block_click(self): self.reject(candidate=self.candidate.replace('kindly consult','<b onclick="x()">kindly consult</b>'))
    def test_blob_sha(self): self.assertEqual(g.blob_sha(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_each_other_paragraph_rejected(self):
        for i in range(35):
            if i!=9:
                with self.subTest(i=i): self.reject(candidate=self.candidate.replace(f'Para {i}:',f'Changed {i}:'))
    def test_each_citation_removed_rejected(self):
        for i in range(35):
            pos=self.candidate.index(f'<p>Para {i}:') if i!=9 else self.candidate.index('<p>Para 9:')
            stop=self.candidate.index('</p>',pos)
            target=self.candidate[pos:stop]
            with self.subTest(i=i): self.reject(candidate=self.candidate.replace(target,target.replace('{{cite:start-ready-power}}','')))
    def test_nonparagraph_variants_rejected(self):
        for left,right in [('<h2 id="later">','<h2 id="later-changed">'),('Medicines','medicines'),('Later','Later now')]:
            with self.subTest(right=right): self.reject(candidate=self.candidate.replace(left,right))

# Independently named mutation cases are individually counted by unittest runners.
def _make_paragraph_mutation(i):
    def run(self):
        if i == 9:
            self.reject(candidate=self.candidate.replace('Para 9: kindly consult','Para 9:'))
        else:
            self.reject(candidate=self.candidate.replace(f'Para {i}:', f'Altered {i}:'))
    return run

def _make_citation_mutation(i):
    def run(self):
        pos=self.candidate.index(f'<p>Para {i}:')
        stop=self.candidate.index('</p>',pos)
        text=self.candidate[pos:stop]
        self.reject(candidate=self.candidate.replace(text,text.replace('{{cite:start-ready-power}}','')))
    return run

for i in range(35):
    if i != 9:
        setattr(ReviewGate, f'test_other_paragraph_mutation_{i:02d}', _make_paragraph_mutation(i))
    setattr(ReviewGate, f'test_source_occurrence_removed_{i:02d}', _make_citation_mutation(i))

if __name__ == '__main__': unittest.main()
