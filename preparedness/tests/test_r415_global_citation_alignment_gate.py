"""R415 synthetic global citation-binding tests; no genuine article/safety claim."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tests'))
from test_r414_citation_locality_escrow_gate import fixture, ANCHOR, BEFORE, AFTER
import r414_citation_locality_escrow_gate as prior
import r415_global_citation_alignment_gate as gate


def check(mutate=None):
    d,m,e,c=fixture()
    if mutate:
        mutate(d,m,e,c)
    return gate.check(d,m,e,c,test_only=True)


def fake_new_location(d,m,e,c, padding=0):
    """R414 false positive: unchanged 18-word source context replayed at a new spot."""
    html=e['guide-0'][0]
    gap='<p>'+'Independent ordinary background on archive catalog objects. '*padding+'</p>'
    rewritten=html.replace(ANCHOR,'').replace('</article>',gap+BEFORE+ANCHOR+AFTER+'</article>')
    e['guide-0']=(rewritten,rewritten)


class Positive(unittest.TestCase):
    def test_complete_35_item_structural_fixture_passes_without_release(self):
        r=check();self.assertTrue(r['integrity_ok'],r['errors'])
        self.assertEqual(r['draft_pairs_inspected'],70)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
        self.assertFalse(r['eligible']);self.assertFalse(r['publication_approved'])
        self.assertFalse(r['qualified_safety_approved'])
    def test_added_unrelated_appendix_keeps_source_in_place(self):
        def append(d,m,e,c):
            html=e['guide-0'][0].replace('</article>','<p>An appended independent source note with new archives.</p></article>')
            e['guide-0']=(html,html)
        r=check(append);self.assertTrue(r['integrity_ok'],r['errors'])
    def test_unchanged_source_context_unique(self):
        x=gate._r414.positions(BEFORE+ANCHOR+AFTER)
        at=x.markers[0][1]
        left=tuple(x.words[at-9:at]);right=tuple(x.words[at+2:at+11])
        self.assertEqual(gate.context_count(x.words,left,right,2),1)
    def test_context_replay_duplicate_witnesses(self):
        x=gate._r414.positions(BEFORE+ANCHOR+AFTER+BEFORE+ANCHOR+AFTER)
        at=x.markers[0][1]
        self.assertEqual(gate.context_count(x.words,tuple(x.words[at-9:at]),tuple(x.words[at+2:at+11]),2),2)
    def test_missing_escrow_strictly_held(self):
        d,m,e,c=fixture();self.assertFalse(gate.check(d,m,e,c)['integrity_ok'])
    def test_missing_cli_never_releases(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r415_global_citation_alignment_gate.py'),
            '/missing/original','/missing/manifest','/missing/exports','/missing/private'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)['release_state'],'DRAFT_HARD_HOLD')
    def test_global_alignment_simple_insertion(self):
        a=('a','b','c','d','e');b=('a','b','inserted','c','d','e')
        matches=gate.global_alignment(a,b)
        self.assertEqual(matches[2],3);self.assertEqual(matches[4],5)
    def test_global_alignment_hard_cap(self):
        with self.assertRaises(ValueError):gate.global_alignment(['x']*(gate.MAX_TOKENS+1),['x'])
    def test_report_excludes_private_article_text(self):
        result=json.dumps(check())
        self.assertNotIn('A museum ledger records',result)
        self.assertNotIn('The historical catalog contains',result)
    def test_no_mutation_of_evidence_objects(self):
        d,m,e,c=fixture();before=copy.deepcopy((d,m,e,c))
        gate.check(d,m,e,c,test_only=True)
        self.assertEqual((d,m,e,c),before)
    def test_candidate_sha_mismatch_blocks(self):
        def spoof(d,m,e,c):
            k=next(iter(c));c[k]+=b'fake'
        self.assertFalse(check(spoof)['integrity_ok'])
    def test_parity_disagreement_blocks(self):
        def spoof(d,m,e,c):
            wp,pv=e['guide-0'];e['guide-0']=(wp,pv.replace(ANCHOR,''))
        self.assertFalse(check(spoof)['integrity_ok'])


class DemonstratedGap(unittest.TestCase):
    def test_prior_r414_accepts_replayed_context_but_r415_rejects(self):
        d,m,e,c=fixture();fake_new_location(d,m,e,c)
        older=prior.check(d,m,e,c,test_only=True)
        newer=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(older['integrity_ok'],older['errors'])
        self.assertFalse(newer['integrity_ok'])
        self.assertTrue(any('globally detached' in err for err in newer['errors']))
        self.assertEqual(newer['release_state'],'DRAFT_HARD_HOLD')


class ReplayMutations(unittest.TestCase):pass


def make_replay_case(n):
    def run(self):
        r=check(lambda d,m,e,c:fake_new_location(d,m,e,c,padding=n))
        self.assertFalse(r['integrity_ok'],(n,r['errors']))
        self.assertFalse(r['eligible']);self.assertFalse(r['publication_approved'])
        self.assertTrue(any('R415 citation globally detached' in err for err in r['errors']))
    return run

for n in range(0,41):
    setattr(ReplayMutations,'test_duplicated_context_after_appendix_'+str(n).zfill(2),make_replay_case(n))


class OtherAdversarial(unittest.TestCase):pass

def mutation_case(name, f):
    def run(self):
        r=check(f)
        self.assertFalse(r['integrity_ok'],name+' unexpectedly accepted')
        self.assertFalse(r['eligible']);self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    return run

OTHER=[
    ('missing_original',lambda d,m,e,c:c.clear()),
    ('tampered_manifest',lambda d,m,e,c:m.__setitem__('approved',True)),
    ('missing_article',lambda d,m,e,c:d['original_articles'].pop()),
    ('fake_source_url',lambda d,m,e,c:e.__setitem__('guide-0',(e['guide-0'][0].replace('asset-0','other-0'),)*2)),
    ('missing_original_source_marker',lambda d,m,e,c:e.__setitem__('guide-0',(e['guide-0'][0].replace(ANCHOR,''),)*2)),
    ('missing_preview_pair',lambda d,m,e,c:e.__setitem__('guide-0',[])),
    ('changed_citation_label',lambda d,m,e,c:e.__setitem__('guide-0',(e['guide-0'][0].replace('Original source','Replaced source'),)*2)),
    ('unsafe_html',lambda d,m,e,c:e.__setitem__('guide-0',(e['guide-0'][0].replace('</article>','<script>alert(1)</script></article>'),)*2)),
    ('hidden_original_paragraph',lambda d,m,e,c:e.__setitem__('guide-0',(e['guide-0'][0].replace(BEFORE,'<p hidden>'+BEFORE+'</p>'),)*2)),
    ('read_depth_loss',lambda d,m,e,c:e.__setitem__('guide-0',(e['guide-0'][0].replace(BEFORE,''),)*2)),
]
for name,fn in OTHER:
    setattr(OtherAdversarial,'test_'+name,mutation_case(name,fn))

if __name__=='__main__':unittest.main()
