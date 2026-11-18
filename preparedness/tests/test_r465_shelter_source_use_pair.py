"""R465: synthetic pair-custody regressions, no live source/medical claims."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

loc = Path(__file__).resolve().parents[1] / 'tools/r465_shelter_source_use_pair.py'
spec = importlib.util.spec_from_file_location('r465', loc)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

SCOPE = {'shelter-a': 'Read the original agency subsection about contacts.',
         'shelter-b': 'Read the full second warning and the caveats.',
         'shelter-c': 'New independent source, specifically scoped.'}

def fixture():
    meta_pins = {'schema': 1, 'state': r.HOLD, 'qd_pass': False,
                 'publication_authorized': False,
                 'source_commit_sha': {v: chr(97+i) * 40 for i,v in enumerate(r.VARIANTS)},
                 'articles': {}}
    body_pins = {'schema': 1, 'state': r.HOLD, 'qd_pass': False,
                 'origin_commit_sha': dict(meta_pins['source_commit_sha']), 'articles': {}}
    evidence = {}
    for n, slug in enumerate(r.SLUGS):
        meta_pins['articles'][slug] = {}
        body_pins['articles'][slug] = {}
        for variant in r.VARIANTS:
            ids = list(SCOPE) if variant != 'original' else list(SCOPE)[:2]
            html = ('<h2>Emergency source context</h2>' +
                    ''.join('<p>Qualified reviewer required {{cite:' + k + '}}</p>' for k in ids)).encode()
            meta = {'slug': slug, 'n': n + 11, 'status': {'publish': 'draft', 'editorial': 'drafted'},
                    'safety_review': {'state': 'pending', 'reviewer': None, 'date': None},
                    'source_use': {k: SCOPE[k] for k in ids}}
            mb = json.dumps(meta, sort_keys=True).encode()
            evidence[(slug, variant)] = (html, mb)
            meta_pins['articles'][slug][variant] = r.git_blob(mb)
            body_pins['articles'][slug][variant] = r.git_blob(html)
    return meta_pins, body_pins, evidence

def repin(mp, bp, ev, slug, v, new_body=None, new_meta=None):
    old_body, old_meta = ev[(slug, v)]
    if new_body is not None: old_body = new_body
    if new_meta is not None: old_meta = new_meta
    ev[(slug, v)] = (old_body, old_meta)
    mp['articles'][slug][v] = r.git_blob(old_meta)
    bp['articles'][slug][v] = r.git_blob(old_body)

def edited_meta(mp, bp, ev, slug, v, update):
    body, raw = ev[(slug, v)]
    meta = json.loads(raw)
    update(meta)
    repin(mp, bp, ev, slug, v, new_meta=json.dumps(meta).encode())

class Basic(unittest.TestCase):
    def test_valid_pairs_are_not_approval(self):
        mp,bp,ev=fixture(); result=r.audit(mp,bp,ev)
        self.assertEqual(result['pair_count'],16)
        self.assertEqual(result['comparison_count'],12)
        self.assertEqual(result['state'],'SHELTER_SOURCE_USE_CUSTODY_INTACT_REVIEW_REQUIRED')
        self.assertFalse(result['qualified_qd_pass'])
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['paid_offer_verified'])
        self.assertFalse(result['version_winner_selected'])
    def test_preserves_original_plus_candidate_scope(self):
        mp,bp,ev=fixture(); out=r.audit(mp,bp,ev)
        originals=[x for x in out['deltas'] if x['witness']=='original']
        self.assertEqual(len(originals),4)
        self.assertTrue(all(x['source_ids_added']==['shelter-c'] for x in originals))
        self.assertTrue(all(not x['source_ids_removed'] for x in originals))
    def test_duplicate_keys_even_if_value_same(self):
        with self.assertRaises(r.PairHold): r.decode_metadata(b'{"slug":"a","slug":"a"}')
    def test_git_blob_reference(self):
        self.assertEqual(r.git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_native_cli_missing_real_witnesses_stays_hold(self):
        self.assertEqual(r.main(['--root',str(Path(__file__).resolve().parent),
                                 '--witness-root',str(Path(__file__).resolve().parent)]),2)

class Mutations(unittest.TestCase):
    pass

# Regenerated matching Git pins MUST NOT launder malformed author metadata.
operations = [
    lambda m: m.update(slug='other-article'),
    lambda m: m.update(n=0),
    lambda m: m.update(n=True),
    lambda m: m.update(n='15'),
    lambda m: m.update(status={'publish':'publish'}),
    lambda m: m.update(status={'publish':'pending'}),
    lambda m: m.update(status=None),
    lambda m: m.update(safety_review={'state':'approved','reviewer':'fake','date':'2026-11-18'}),
    lambda m: m.update(safety_review={'state':'pending','reviewer':'fake','date':None}),
    lambda m: m.update(safety_review={'state':'pending','reviewer':None,'date':'2026-11-18'}),
    lambda m: m.update(safety_review={'state':'not-required','reviewer':None,'date':None}),
    lambda m: m.update(safety_review=None),
    lambda m: m.update(source_use={}),
    lambda m: m.update(source_use=None),
    lambda m: m.update(source_use={'shelter-a':''}),
    lambda m: m.update(source_use={'shelter-a':None}),
    lambda m: m.update(source_use={'unsafe id':'text'}),
    lambda m: m.update(source_use={'shelter-b':'new note'}),
    lambda m: m['source_use'].pop('shelter-a'),
    lambda m: m['source_use'].update({'shelter-d':'a fabricated citation'}),
]
for index, modifier in enumerate(operations):
    for position in range(4):
        def make(fn, idx):
            def test(self):
                mp,bp,ev=fixture()
                slug=r.SLUGS[idx]
                edited_meta(mp,bp,ev,slug,'candidate',fn)
                with self.assertRaises((r.PairHold,TypeError,KeyError)):
                    r.audit(mp,bp,ev)
            return test
        setattr(Mutations,f'test_repin_meta_reject_{index:02d}_{position}',make(modifier,position))

class EvidenceAttacks(unittest.TestCase):
    pass

def mutation(number, mp, bp, ev):
    slug=r.SLUGS[number%4]; v=r.VARIANTS[(number//4)%4]
    typ=number//16
    if typ==0:ev.pop((slug,v))
    elif typ==1:ev[(slug,v)]=(ev[(slug,v)][0]+b'<p>Changed</p>',ev[(slug,v)][1])
    elif typ==2:ev[(slug,v)]=(ev[(slug,v)][0],ev[(slug,v)][1]+b' ')
    elif typ==3:mp['articles'][slug][v]='0'*40
    elif typ==4:bp['articles'][slug][v]='0'*40
    elif typ==5:mp['articles'][slug].pop(v)
    elif typ==6:bp['articles'][slug].pop(v)
    elif typ==7:bp['articles'].pop(slug)
    elif typ==8:mp['articles'].pop(slug)
    elif typ==9:mp['source_commit_sha'][v]='f'*40
    elif typ==10:ev[(slug,v)]=(b'<p>{{cite:INVALID}}</p>',ev[(slug,v)][1]);bp['articles'][slug][v]=r.git_blob(ev[(slug,v)][0])
    elif typ==11:ev[(slug,v)]=(b'<p>{{cite:shelter-a}}</p>',ev[(slug,v)][1]);bp['articles'][slug][v]=r.git_blob(ev[(slug,v)][0])
    elif typ==12:ev[(slug,v)]=(ev[(slug,v)][0].replace(b'{{cite:shelter-a}}',b'{{cite:unknown}}'),ev[(slug,v)][1]);bp['articles'][slug][v]=r.git_blob(ev[(slug,v)][0])
    elif typ==13:mp['articles'][slug]['rogue']='0'*40
    elif typ==14:bp['articles'][slug]['rogue']='0'*40
    elif typ==15:ev[('rogue','candidate')]=(b'fake',b'fake')

for index in range(256):
    def make(idx):
        def test(self):
            mp,bp,ev=fixture()
            mutation(idx,mp,bp,ev)
            with self.assertRaises((r.PairHold,KeyError,TypeError,ValueError)):
                r.audit(mp,bp,ev)
        return test
    setattr(EvidenceAttacks,f'test_mutation_{index:03d}',make(index))

if __name__=='__main__':unittest.main()
