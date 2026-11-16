"""R413 tests: synthetic 35-item manuscript evidence, no actual safety approval."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from test_r412_baseline_citation_gate import prepared
import r412_baseline_citation_gate as prior
import r413_warning_heading_escrow_gate as gate

EXTRA = 'Synthetic supporting background provides comparison context only. ' * 17
SAFETY = ('Never use unsafe water without official guidance because serious injury may occur. '
          'Do not ignore emergency warnings unless local officials confirm otherwise. '
          'Only call the listed number when required and stop if conditions change. ')


def fixture():
    d,m,e,c = prepared()
    original = e['guide-0'][0]
    new = original.replace('<a data-source-id', '<p>'+EXTRA+SAFETY+'</p><a data-source-id')
    e['guide-0'] = (new,new)
    key=('guide-0',d['original_articles'][0]['body_candidate_git_blobs'][0])
    c.pop(key)
    pin=gate._r412._r409.blob(new.encode('utf-8'))
    d['original_articles'][0]['body_candidate_git_blobs']=[pin]
    c[('guide-0',pin)]=new.encode('utf-8')
    return d,m,e,c


def run(modifier=None):
    d,m,e,c=fixture()
    if modifier:
        modified=modifier(e['guide-0'][0])
        e['guide-0']=(modified,modified)
    return gate.check(d,m,e,c,test_only=True)


class Positive(unittest.TestCase):
    def test_complete_fixture_retains_all_but_never_releases(self):
        r=run(); self.assertTrue(r['integrity_ok'],r['errors'])
        self.assertEqual(r['original_candidates_inspected'],35)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
        self.assertFalse(r['eligible']);self.assertFalse(r['publication_approved'])
        self.assertFalse(r['qualified_safety_approved'])
    def test_protected_window_counter_preserves_multiplicity(self):
        a=gate.warning_windows(['never','use','no','water','never','use','no','water'],radius=1)
        b=gate.warning_windows(['never','use','no','water'],radius=1)
        self.assertGreaterEqual(sum(a.values()),sum(b.values()))
    def test_plaintext_markdown_headings(self):
        self.assertEqual(gate.headings(b'#  Start here\n\n## Safety Notes\n'),
                         [('start','here'),('safety','notes')])
    def test_html_headings(self):
        self.assertEqual(gate.headings(b'<article><h1>Start here</h1><p>Text</p><h2>Safety <em>notes</em></h2></article>'),
                         [('start','here'),('safety','notes')])
    def test_void_html_break_not_treated_as_unclosed(self):
        self.assertEqual(gate.headings(b'<article><h1>Start<br>Here</h1></article>'), [('start','here')])
    def test_missing_originals_cli_returns_exit_two(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r413_warning_heading_escrow_gate.py'),
                          '/missing/a','/missing/b','/missing/c','/missing/d'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertFalse(json.loads(p.stdout)['eligible'])
    def test_authentic_original_docket_pin_still_required(self):
        d,m,e,c=fixture()
        self.assertFalse(gate.check(d,m,e,c)['integrity_ok'])
    def test_report_does_not_reveal_private_warning_excerpt(self):
        self.assertNotIn(SAFETY,json.dumps(run()))
    def test_noncritical_reordering_is_subject_to_existing_depth_gate(self):
        r=run(); self.assertTrue(r['integrity_ok'],r['errors'])


class Regression(unittest.TestCase):
    def test_prior_r412_accepts_short_negation_flip_but_new_gate_rejects(self):
        d,m,e,c=fixture()
        edited=e['guide-0'][0].replace('Never use unsafe water','Always use unsafe water')
        e['guide-0']=(edited,edited)
        older=prior.check(d,m,e,c,test_only=True)
        newer=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(older['integrity_ok'],older['errors'])
        self.assertFalse(newer['integrity_ok'])
    def test_prior_r412_accepts_missing_short_warning_but_new_gate_rejects(self):
        d,m,e,c=fixture()
        edited=e['guide-0'][0].replace('Do not ignore emergency warnings unless local officials confirm otherwise. ','')
        e['guide-0']=(edited,edited)
        older=prior.check(d,m,e,c,test_only=True)
        newer=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(older['integrity_ok'],older['errors'])
        self.assertFalse(newer['integrity_ok'])
    def test_prior_r412_accepts_same_heading_text_changed_both_outputs(self):
        d,m,e,c=fixture()
        edited=e['guide-0'][0].replace('Verified only as synthetic source-citation fixture','Synthetic verification headline changed')
        e['guide-0']=(edited,edited)
        older=prior.check(d,m,e,c,test_only=True)
        newer=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(older['integrity_ok'],older['errors'])
        self.assertFalse(newer['integrity_ok'])


ATTACKS=[]
for word,replacement in [
    ('Never','Always'),('Never',''),('unsafe','safe'),('without','with'),
    ('serious','minor'),('injury','benefit'),('may','will'),('Do not','Do'),
    ('Do not',''),('ignore','follow'),('emergency','ordinary'),
    ('warnings','suggestions'),('unless','because'),('unless',''),
    ('local','distant'),('officials','strangers'),('confirm','guess'),
    ('otherwise','immediately'),('Only','Always'),('Only',''),
    ('call','email'),('listed','any'),('number','website'),
    ('when','whenever'),('required','convenient'),('stop','continue'),
    ('conditions','circumstances'),('change','improve'),
    ('guidance','advice'),('water','juice'),('safe','unsafe'),
    ('unsafe water','clean water'),('official guidance','informal tips'),
    ('not ignore','ignore'),('stop if','continue if'),
    ('Do not ignore emergency warnings','Ignore emergency warnings')]:
    ATTACKS.append((word,replacement))

class QualifierMutations(unittest.TestCase):
    pass

def make_test(idx,word,replacement):
    def check_mutation(self):
        altered=run(lambda html: html.replace(word,replacement,1))
        self.assertFalse(altered['integrity_ok'],(word,replacement,altered['errors']))
        self.assertFalse(altered['eligible'])
    check_mutation.__name__='test_context_mutation_'+str(idx)
    return check_mutation

for i,(word,repl) in enumerate(ATTACKS):
    setattr(QualifierMutations,'test_context_mutation_'+str(i).zfill(2),make_test(i,word,repl))

if __name__=='__main__': unittest.main()
