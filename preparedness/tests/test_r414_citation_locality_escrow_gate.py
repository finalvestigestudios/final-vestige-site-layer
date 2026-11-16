"""R414 source-adjacent citation relocation tests using only synthetic 35-article material."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
sys.path.insert(0,str(ROOT/'tests'))
from test_r413_warning_heading_escrow_gate import fixture as r413_fixture
import r413_warning_heading_escrow_gate as previous
import r414_citation_locality_escrow_gate as gate

BEFORE = '<p>'+'A museum ledger records an ordinary sequence of objects and dates. '*5+'</p>'
AFTER = '<p>'+'The historical catalog contains examples of preservation and archival references. '*5+'</p>'
ANCHOR = '<a data-source-id="src-0" href="https://www.ready.gov/asset-0">Original source</a>'


def fixture():
    d,m,e,c=r413_fixture()
    text=e['guide-0'][0].replace(ANCHOR, BEFORE+ANCHOR).replace('</article>',AFTER+'</article>')
    key=('guide-0',d['original_articles'][0]['body_candidate_git_blobs'][0]); c.pop(key)
    pin=gate._r412._r409.blob(text.encode())
    d['original_articles'][0]['body_candidate_git_blobs']=[pin]
    c[('guide-0',pin)] = text.encode()
    e['guide-0'] = (text,text)
    return d,m,e,c


def review(mutator=None):
    d,m,e,c=fixture()
    if mutator:
        mutator(d,m,e,c)
    return gate.check(d,m,e,c,test_only=True)


def rewrite_both(d,m,e,c,fn):
    t=fn(e['guide-0'][0]);e['guide-0']=(t,t)


def migrate_link(d,m,e,c, filler):
    # Move unchanged source ID/href/link label into a different paragraph/position.
    # Both outputs remain identical. Earlier gates structurally accept this.
    rewrite_both(d,m,e,c,lambda s:s.replace(ANCHOR,'').replace('</article>',filler+ANCHOR+'</article>'))


class Positive(unittest.TestCase):
    def test_full_thirty_five_source_graph_passes_structurally_but_stays_held(self):
        r=review();self.assertTrue(r['integrity_ok'],r['errors']);self.assertEqual(r['candidates_compared'],35)
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD');self.assertFalse(r['eligible'])
        self.assertFalse(r['publication_approved']);self.assertFalse(r['qualified_safety_approved'])
    def test_missing_original_pin_never_passes(self):
        d,m,e,c=fixture();self.assertFalse(gate.check(d,m,e,c)['integrity_ok'])
    def test_missing_authentic_files_cli_returns_exit_two(self):
        x=subprocess.run([sys.executable,'-I',str(ROOT/'tools'/'r414_citation_locality_escrow_gate.py'),'/no/original','/no/manifest','/no/export','/no/private'],capture_output=True,text=True)
        self.assertEqual(x.returncode,2); self.assertEqual(json.loads(x.stdout)['release_state'],'DRAFT_HARD_HOLD')
    def test_exact_inline_marker_context(self):
        x=gate.positions('<p>First second third <a data-source-id="src-7" href="https://example.org">Source note</a> fourth</p>')
        self.assertEqual(x.markers,[('src-7',3)]);self.assertEqual(x.words[-1],'fourth')
    def test_markdown_cite_at_plain_text_position(self):
        p=gate.positions(b'# Intro\nOne two three {{cite:src-12}} four five',candidate=True)
        self.assertEqual(p.markers,[('src-12',4)])
    def test_markdown_two_distinct_markers(self):
        p=gate.positions('Before {{cite:src-1}} middle {{cite:src-2}} after',candidate=True)
        self.assertEqual([x[0] for x in p.markers],['src-1','src-2'])
    def test_report_no_private_excerpts_or_rendered_text(self):
        r=review();self.assertNotIn('A museum ledger records',json.dumps(r));self.assertNotIn('Never use unsafe water',json.dumps(r))
    def test_no_file_change_from_in_memory_review(self):
        d,m,e,c=fixture();copy_d,copy_m,copy_e,copy_c=copy.deepcopy((d,m,e,c));gate.check(d,m,e,c,test_only=True)
        self.assertEqual((d,m,e,c),(copy_d,copy_m,copy_e,copy_c))
    def test_lookaround_left_right_both_required(self):
        a=(('museum','ledger'),('original','source'))
        self.assertTrue(gate.match_context(a,a))
        self.assertFalse(gate.match_context(a,(('totally','different'),a[1])))
        self.assertFalse(gate.match_context(a,(a[0],('totally','different'))))
    def test_extraneous_unrelated_content_distant_from_inline_source_is_tolerated_structurally(self):
        def more(d,m,e,c):rewrite_both(d,m,e,c,lambda s:s.replace('</article>','<p>A harmless archival appendix mentions ordinary documents.</p></article>'))
        r=review(more);self.assertTrue(r['integrity_ok'],r['errors'])
    def test_html_entity_expansion_in_tokenization(self):
        p=gate.positions('<p>Archive &amp; records <a data-source-id="src-1">Reference title</a></p>')
        self.assertEqual(p.words[:3],['archive','records','reference'])
    def test_duplicate_markers_are_kept_distinct(self):
        p=gate.positions('a {{cite:x}} b {{cite:x}} c',candidate=True)
        self.assertEqual(len(p.markers),2)
    def test_quoted_markdown_image_omitted_from_original_context(self):
        p=gate.positions('Words ![graph](https://example.org/foo.png) {{cite:x}} after',candidate=True)
        self.assertEqual(p.words,['words','after'])


class Reproduction(unittest.TestCase):
    def test_prior_r413_allows_bibliography_relocation_but_r414_blocks(self):
        d,m,e,c=fixture()
        migrate_link(d,m,e,c,'')
        old=previous.check(d,m,e,c,test_only=True);new=gate.check(d,m,e,c,test_only=True)
        self.assertTrue(old['integrity_ok'],old['errors']);self.assertFalse(new['integrity_ok'])
        self.assertTrue(any('detached' in x for x in new['errors']))
    def test_same_source_url_id_and_counts_are_insufficient(self):
        d,m,e,c=fixture();migrate_link(d,m,e,c,'')
        self.assertEqual(ANCHOR in e['guide-0'][0],True)
        self.assertEqual(e['guide-0'][0],e['guide-0'][1])
        self.assertFalse(gate.check(d,m,e,c,test_only=True)['integrity_ok'])


# Every case creates fresh 35-source original fixture; the new location is changed
# without altering citation ID, URL, label, original SHA, or total citation count.
class Relocations(unittest.TestCase): pass

def make_move_test(n):
    def t(self):
        filler='<p>' + ('Additional chronological context from ordinary museum catalogs and historic ledgers. '*n) + '</p>'
        r=review(lambda d,m,e,c:migrate_link(d,m,e,c,filler))
        self.assertFalse(r['integrity_ok'],r['errors']);self.assertFalse(r['eligible'])
        self.assertTrue(any('detached' in x for x in r['errors']))
    return t

for n in range(1,32):
    setattr(Relocations,'test_displaced_citation_after_extra_'+str(n).zfill(2),make_move_test(n))


class Adversarial(unittest.TestCase):pass

ATTACKS = [
('replace_source_id',lambda d,m,e,c:rewrite_both(d,m,e,c,lambda s:s.replace('data-source-id="src-0"','data-source-id="src-1"'))),
('swap_source_url',lambda d,m,e,c:rewrite_both(d,m,e,c,lambda s:s.replace('asset-0','asset-8'))),
('remove_anchor',lambda d,m,e,c:rewrite_both(d,m,e,c,lambda s:s.replace(ANCHOR,''))),
('duplicate_anchor',lambda d,m,e,c:rewrite_both(d,m,e,c,lambda s:s.replace(ANCHOR,ANCHOR+ANCHOR))),
('change_anchor_label',lambda d,m,e,c:rewrite_both(d,m,e,c,lambda s:s.replace('Original source</a>','Modified source</a>'))),
('place_anchor_in_hidden',lambda d,m,e,c:rewrite_both(d,m,e,c,lambda s:s.replace(ANCHOR,'<p hidden>'+ANCHOR+'</p>'))),
('wrong_manifest_source',lambda d,m,e,c:m['articles'][0].__setitem__('sources',['src-2'])),
('delete_original_artifact',lambda d,m,e,c:c.pop(next(iter(c)))),
('extra_original_candidate',lambda d,m,e,c:c.__setitem__(('guide-0','f'*40),b'fake')),
('invalid_render_encoding',lambda d,m,e,c:e.__setitem__('guide-0',(b'\xff',b'\xff'))),
('no_original_source_marker',lambda d,m,e,c:_no_source_marker(d,m,e,c)),
('private_preview_diff',lambda d,m,e,c:e.__setitem__('guide-0',(e['guide-0'][0],e['guide-0'][1].replace('Original source','Changed source')))),
('invalid_citation_attribute',lambda d,m,e,c:rewrite_both(d,m,e,c,lambda s:s.replace('data-source-id="src-0"','data-source-id="../foo"'))),
('nested_hidden_source',lambda d,m,e,c:rewrite_both(d,m,e,c,lambda s:s.replace(ANCHOR,'<template>'+ANCHOR+'</template>'))),
('missing_original_graph_article',lambda d,m,e,c:d['original_articles'].pop()),
('fabricated_qd_true',lambda d,m,e,c:m.__setitem__('approved',True)),
]

def _no_source_marker(d,m,e,c):
    # Re-authenticate a modified source; output still cites a source but source
    # placement cannot be proven from the new, authentic synthetic Git blob.
    p=d['original_articles'][0]['body_candidate_git_blobs'][0]
    original=c.pop(('guide-0',p)).replace(b'data-source-id="src-0"',b'data-original-source-id="src-0"')
    sha=gate._r412._r409.blob(original)
    d['original_articles'][0]['body_candidate_git_blobs']=[sha]
    c[('guide-0',sha)]=original


def make_attack(name,fn):
    def t(self):
        r=review(fn)
        self.assertFalse(r['integrity_ok'],name+' passed structural review')
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
        self.assertFalse(r['eligible']);self.assertFalse(r['publication_approved'])
    return t

for name,fn in ATTACKS:
    setattr(Adversarial,'test_'+name,make_attack(name,fn))

if __name__=='__main__': unittest.main()
