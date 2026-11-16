"""R412 35-item synthetic, no real manuscripts or safety/commerce approval."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import r412_baseline_citation_gate as gate
import r411_visible_evidence_gate as old
from test_r410_full_slate_export_gate import fixture


def prepared():
    d, m, exports = fixture()
    candidates = {}
    for entry in d['original_articles']:
        slug = entry['slug']
        body = exports[slug][0].encode('utf-8')
        pin = gate._r409.blob(body)
        entry['body_candidate_git_blobs'] = [pin]
        candidates[(slug,pin)] = body
    return d,m,exports,candidates


def run(edit=None, *, with_result=False):
    d,m,e,c = prepared()
    if edit: edit(d,m,e,c)
    result = gate.check(d,m,e,c,test_only=True)
    return result if with_result else result['integrity_ok']


def mutate_html(d,m,e,c,modifier,*,both=True):
    html = e['guide-0'][0]
    modified = modifier(html)
    e['guide-0'] = (modified, modified if both else html)


class PositiveSyntheticControls(unittest.TestCase):
    def test_full_original_escrow_structurally_passes_but_release_held(self):
        r = run(with_result=True)
        self.assertTrue(r['integrity_ok'],r['errors']); self.assertEqual(r['candidate_compared'],35)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
        self.assertFalse(r['eligible']); self.assertFalse(r['publication_approved'])
        self.assertTrue(all(x['review_required'] for x in r['details']))
    def test_authentic_source_pin_is_still_required(self):
        d,m,e,c=prepared(); self.assertFalse(gate.check(d,m,e,c)['integrity_ok'])
    def test_genuine_candidate_sha_enforced(self):
        d,m,e,c=prepared(); key=next(iter(c)); c[key]=c[key]+b' '
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_missing_originals_cli_never_passes(self):
        p=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r412_baseline_citation_gate.py'),'/no/original','/no/manifest','/no/exports','/no/private'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertFalse(json.loads(p.stdout)['integrity_ok'])
    def test_mixed_anchor_child_text_is_visible(self):
        self.assertTrue(run(lambda d,m,e,c:mutate_html(d,m,e,c,lambda s:s.replace('>Original source</a>','><strong>Original</strong> source</a>'))))
    def test_approved_new_window_link_rel_pair_is_structural_only(self):
        self.assertTrue(run(lambda d,m,e,c:mutate_html(d,m,e,c,lambda s:s.replace('<a data-source-id','<a target="_blank" rel="noopener noreferrer" data-source-id'))))
    def test_source_word_tokenizer_html_extract(self):
        text=b'<article><h1>Hello world</h1><p>Original evidence matters</p></article>'
        self.assertEqual(gate.source_words(text),['hello','world','original','evidence','matters'])
    def test_shingle_equal_and_unrelated(self):
        self.assertEqual(gate.shingle_score('one two three four five six'.split(),'one two three four five six'.split()),1)
        self.assertEqual(gate.shingle_score('one two three four five six'.split(),'seven eight nine ten eleven twelve'.split()),0)
    def test_pin_coverage_multiple_forks_can_remain_held(self):
        d,m,e,c=prepared(); slug='guide-0'; body=c[(slug,d['original_articles'][0]['body_candidate_git_blobs'][0])]
        alt=body.replace(b'Verified only',b'Verified also')
        pin=gate._r409.blob(alt);d['original_articles'][0]['body_candidate_git_blobs'].append(pin);c[(slug,pin)]=alt
        r=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(r['integrity_ok'],r['errors']); self.assertEqual(r['candidate_compared'],36)
        self.assertFalse(r['eligible'])
    def test_private_candidate_reader_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root); (p/'article').mkdir(); (p/'target').write_text('data'); (p/'article'/'abc.txt').symlink_to(p/'target')
            with self.assertRaises(ValueError):gate.checked_candidate_read(p/'article'/'abc.txt',root=p)
    def test_private_candidate_reader_rejects_hardlink(self):
        import os
        with tempfile.TemporaryDirectory() as root:
            p=Path(root); (p/'article').mkdir(); (p/'target').write_text('data'); os.link(p/'target',p/'article'/'abc.txt')
            with self.assertRaises(ValueError):gate.checked_candidate_read(p/'article'/'abc.txt',root=p)
    def test_private_candidate_reader_normal_file(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root); (p/'article').mkdir(); (p/'article'/'abc.txt').write_bytes(b'original')
            self.assertEqual(gate.checked_candidate_read(p/'article'/'abc.txt',root=p),b'original')
    def test_candidate_paths_not_reflected_in_public_receipt(self):
        r=run(with_result=True)
        self.assertNotIn('private_candidate_root',json.dumps(r))

# Every rejection operates on a fresh complete 35-item source graph, 203 source IDs.
ATTACKS=[]
for label in ('',' ','   ','link','source','Here','click here','READ MORE','details','more','learn more','click','...','!', '→','🔗','a'):
    ATTACKS.append((f'bad_link_text_{len(ATTACKS)}',
      lambda d,m,e,c,label=label:mutate_html(d,m,e,c,lambda s:s.replace('>Original source</a>','>'+label+'</a>'))))
for attribute in ('tabindex="-1"','tabindex="-2"','disabled','aria-disabled="true"',
                  'role="none"','role="presentation"','role="button"','download',
                  'target="_blank"','target="_blank" rel="noopener"',
                  'target="_blank" rel="noreferrer"', 'target="_blank" rel="external"'):
    ATTACKS.append((f'bad_link_attribute_{len(ATTACKS)}',
      lambda d,m,e,c,attribute=attribute:mutate_html(d,m,e,c,lambda s:s.replace('<a data-source-id','<a '+attribute+' data-source-id'))))
for length in range(1,13):
    # Both exports are identically shortened. R411 would compare equal and accept at >=50 words.
    ATTACKS.append((f'reduce_both_exports_{length}',
      lambda d,m,e,c,length=length:mutate_html(d,m,e,c,
         lambda s:s.replace('This is draft synthetic placeholder text for comparative source auditing only. '*7,
                            'This is draft synthetic placeholder text for comparative source auditing only. '*max(1,7-(length+1)//2)))))
for change in ('fake', 'unrelated', 'replacement', 'modified', 'missing', 'adulterated', 'reframed', 'filtered', 'undocumented'):
    ATTACKS.append((f'rewrite_original_phrase_{change}',
      lambda d,m,e,c,change=change:mutate_html(d,m,e,c,
        lambda s:s.replace('This is draft synthetic', change+' is a synthetic'))))
ATTACKS += [
('missing_all_private',lambda d,m,e,c:c.clear()),
('missing_one_original',lambda d,m,e,c:c.pop(next(iter(c)))),
('extra_unreviewed_original',lambda d,m,e,c:c.__setitem__(('guide-0','f'*40),b'extra')),
('missing_candidate_pins',lambda d,m,e,c:d['original_articles'][0].pop('body_candidate_git_blobs')),
('candidate_pins_empty',lambda d,m,e,c:d['original_articles'][0].__setitem__('body_candidate_git_blobs',[])),
('candidate_pins_bad',lambda d,m,e,c:d['original_articles'][0].__setitem__('body_candidate_git_blobs',['../bad'])),
('candidate_type_wrong',lambda d,m,e,c:c.__setitem__(next(iter(c)),'not-bytes')),
('candidate_empty',lambda d,m,e,c:c.__setitem__(next(iter(c)),b'')),
('candidate_oversize',lambda d,m,e,c:c.__setitem__(next(iter(c)),b'A'*1_000_001)),
('candidate_invalid_utf8',lambda d,m,e,c:c.__setitem__(next(iter(c)),b'\xff')),
('candidate_nul_character',lambda d,m,e,c:c.__setitem__(next(iter(c)),b'\x00')),
('candidate_bidi_character',lambda d,m,e,c:c.__setitem__(next(iter(c)),b'a\xe2\x80\xaeb')),
('candidate_not_a_dict',lambda d,m,e,c:c.clear()),
('candidate_original_slug_removed',lambda d,m,e,c:d['original_articles'].pop()),
('extra_candidate_blob_pin',lambda d,m,e,c:d['original_articles'][0]['body_candidate_git_blobs'].append('f'*40)),
]

class MutationAttacks(unittest.TestCase):pass

def make_test(name, fn):
    def t(self):
        r=run(fn,with_result=True)
        self.assertFalse(r['integrity_ok'],name+' unexpectedly accepted')
        self.assertFalse(r['eligible']); self.assertFalse(r['publication_approved'])
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    t.__name__='test_'+name
    return t

for name, fn in ATTACKS:
    setattr(MutationAttacks,'test_'+name,make_test(name,fn))

class PriorGateGap(unittest.TestCase):
    def test_r411_accepts_identical_shortened_exports_against_no_original(self):
        d,m,e,c=prepared()
        for slug, pair in e.items():
            shortened = pair[0].replace('This is draft synthetic placeholder text for comparative source auditing only. '*7,
                                        'This is draft synthetic placeholder text for comparative source auditing only. '*5)
            e[slug] = (shortened,shortened)
        self.assertTrue(old.check(d,m,e,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])
    def test_r411_accepts_invisible_blank_citation_anchor(self):
        d,m,e,c=prepared()
        mutate_html(d,m,e,c,lambda s:s.replace('>Original source</a>','> </a>'))
        self.assertTrue(old.check(d,m,e,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])

if __name__=='__main__':unittest.main()
