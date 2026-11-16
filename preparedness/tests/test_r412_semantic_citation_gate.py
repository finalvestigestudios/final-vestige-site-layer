"""R412 synthetic 35-article paired export semantic/citation regressions; NO safety or QD claims."""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import r411_visible_evidence_gate as old
import r412_semantic_citation_gate as gate
from test_r410_full_slate_export_gate import fixture

BASE_ANCHOR = '<a data-source-id="src-0" href="https://www.ready.gov/asset-0">Original source</a>'
BASE_HEADING = '<h1>Verified only as synthetic source-citation fixture</h1>'


def mutate(change, both=False):
    d, m, e = fixture()
    html = e['guide-0'][0]
    changed = change(html)
    assert changed != html, 'test mutation must actually change input'
    e['guide-0'] = (changed, changed if both else html)
    return d, m, e


class Controls(unittest.TestCase):
    def test_baseline_35_articles_stays_held(self):
        d, m, e = fixture()
        r = gate.check(d, m, e, test_only=True)
        self.assertTrue(r['integrity_ok'], r['errors'])
        self.assertEqual(r['articles_inspected'], 35)
        self.assertEqual(r['release_state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(r['eligible'])
        self.assertFalse(r['publication_approved'])

    def test_original_r397_git_blob_pin_still_required(self):
        d, m, e = fixture()
        self.assertFalse(gate.check(d, m, e)['integrity_ok'])

    def test_matching_aria_label_can_be_accessible(self):
        d,m,e = mutate(lambda s: s.replace(BASE_ANCHOR,
                     BASE_ANCHOR.replace('>Original source', ' aria-label="Original source">Original source')), both=True)
        self.assertTrue(gate.check(d,m,e,test_only=True)['integrity_ok'])

    def test_native_link_role_and_tabindex_zero_allowed(self):
        d,m,e = mutate(lambda s: s.replace(BASE_ANCHOR,
                     BASE_ANCHOR.replace('>Original source', ' role="link" tabindex="0">Original source')), both=True)
        self.assertTrue(gate.check(d,m,e,test_only=True)['integrity_ok'])

    def test_unique_anchor_identifier_allowed(self):
        d,m,e = mutate(lambda s: s.replace(BASE_ANCHOR,
                     BASE_ANCHOR.replace('>Original source', ' id="source-1">Original source')), both=True)
        self.assertTrue(gate.check(d,m,e,test_only=True)['integrity_ok'])

    def test_allowed_print_paragraphs(self):
        d,m,e = mutate(lambda s: s.replace(BASE_ANCHOR, '<p>'+BASE_ANCHOR+'</p>'), both=True)
        self.assertTrue(gate.check(d,m,e,test_only=True)['integrity_ok'])

    def test_unchanged_synced_nested_markup(self):
        d,m,e = mutate(lambda s: s.replace('<p>This is draft', '<p><strong>This</strong> is draft'), both=True)
        self.assertTrue(gate.check(d,m,e,test_only=True)['integrity_ok'])

    def test_missing_original_artifacts_exit_two(self):
        r = subprocess.run([sys.executable, str(ROOT/'tools'/'r412_semantic_citation_gate.py'),
                            '/missing/original', '/missing/manifest', '/missing/exports'],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        data = json.loads(r.stdout)
        self.assertFalse(data['integrity_ok'])
        self.assertEqual(data['release_state'], 'DRAFT_HARD_HOLD')


# These alter only presentation STRUCTURE or accessible link meaning; the R411 baseline
# erroneously treats the 35-article paired fixture as structurally OK because word/cite
# order and heading-tag sequence remain unchanged. Both R411 and R412 still HARD HOLD.
PARITY_CASES = [
    ('heading_truncated', lambda s:s.replace(BASE_HEADING,'<h1>Verified only as synthetic source-citation</h1><span>fixture</span>')),
    ('heading_delayed', lambda s:s.replace(BASE_HEADING,'<span>Verified </span><h1>only as synthetic source-citation fixture</h1>')),
    ('heading_empty',lambda s:s.replace(BASE_HEADING,'<h1></h1><p>Verified only as synthetic source-citation fixture</p>')),
    ('anchor_text_cut', lambda s:s.replace(BASE_ANCHOR,'<span>Original </span>'+BASE_ANCHOR.replace('Original source','source'))),
    ('anchor_text_split',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('Original source','Original')+'<span> source</span>')),
    ('anchor_inside_paragraph',lambda s:s.replace(BASE_ANCHOR,'<p>'+BASE_ANCHOR+'</p>')),
    ('anchor_inside_quote',lambda s:s.replace(BASE_ANCHOR,'<blockquote>'+BASE_ANCHOR+'</blockquote>')),
    ('anchor_inside_list',lambda s:s.replace(BASE_ANCHOR,'<ul><li>'+BASE_ANCHOR+'</li></ul>')),
    ('paragraph_to_quote',lambda s:s.replace('<p>This is draft','<blockquote>This is draft').replace('</p><a data-source-id','</blockquote><a data-source-id')),
    ('anchor_inside_definition',lambda s:s.replace(BASE_ANCHOR,'<dl><dd>'+BASE_ANCHOR+'</dd></dl>')),
    ('anchor_inside_table',lambda s:s.replace(BASE_ANCHOR,'<table><tr><td>'+BASE_ANCHOR+'</td></tr></table>')),
    ('anchor_inside_caption',lambda s:s.replace(BASE_ANCHOR,'<figure><figcaption>'+BASE_ANCHOR+'</figcaption></figure>')),
    ('anchor_inside_summary',lambda s:s.replace(BASE_ANCHOR,'<details open><summary>'+BASE_ANCHOR+'</summary></details>')),
    ('anchor_inside_pre',lambda s:s.replace(BASE_ANCHOR,'<pre>'+BASE_ANCHOR+'</pre>')),
    ('empty_visible_anchor',lambda s:s.replace(BASE_ANCHOR, BASE_ANCHOR.replace('Original source','')+'<span>Original source</span>')),
    ('extra_empty_p',lambda s:s.replace('</article>','<p></p></article>')),
    ('extra_empty_quote',lambda s:s.replace('</article>','<blockquote></blockquote></article>')),
    ('extra_empty_li',lambda s:s.replace('</article>','<ul><li></li></ul></article>')),
    ('extra_summary',lambda s:s.replace('</article>','<details open><summary></summary></details></article>')),
    ('changed_heading_level_2',lambda s:s.replace(BASE_HEADING,BASE_HEADING.replace('h1','h2'))),
]
# Do NOT assert R411 accepted the changed heading level (it already rejects that case).
PARITY_CASES = [x for x in PARITY_CASES if x[0] != 'changed_heading_level_2']

# All these can be inserted identically in both exports; R411 preserves matching visible words/cites
# while allowing accessible citation spoofing or semantic identifier ambiguity.
ACCESSIBILITY_CASES = [
    ('aria_false_caption',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' aria-label="Ignore this source">Original source'))),
    ('aria_fake_safety',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' aria-label="Medically approved and safe">Original source'))),
    ('role_presentation',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' role="presentation">Original source'))),
    ('role_none',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' role="none">Original source'))),
    ('role_button',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' role="button">Original source'))),
    ('role_image',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' role="img">Original source'))),
    ('tabindex_negative',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' tabindex="-1">Original source'))),
    ('tabindex_positive',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' tabindex="2">Original source'))),
    ('tabindex_invalid',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' tabindex="abc">Original source'))),
    ('aria_labelledby',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' aria-labelledby="fake">Original source'))),
    ('aria_describedby',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' aria-describedby="fake">Original source'))),
    ('duplicate_id',lambda s:s.replace('<article>','<article id="same">').replace('<h1>','<h1 id="same">')),
    ('invalid_id_char',lambda s:s.replace('<article>','<article id="un safe">')),
    ('invalid_id_numeric',lambda s:s.replace('<article>','<article id="123">')),
    ('block_heading_role_none',lambda s:s.replace('<h1>','<h1 role="none">')),
    ('block_heading_role_presentation',lambda s:s.replace('<h1>','<h1 role="presentation">')),
    ('block_heading_role_button',lambda s:s.replace('<h1>','<h1 role="button">')),
    ('attribute_bidi_title',lambda s:s.replace('<article>','<article title="record\u202e reversed">')),
    ('attribute_zero_width_title',lambda s:s.replace('<article>','<article title="rec\u200bord">')),
    ('attribute_bidi_aria',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' aria-label="Original\u202e source">Original source'))),
    ('attribute_zero_width_aria',lambda s:s.replace(BASE_ANCHOR,BASE_ANCHOR.replace('>Original source',' aria-label="Or\u200biginal source">Original source'))),
]

class Adversarial(unittest.TestCase):
    pass


def make_case(name, change, both):
    def test_case(self):
        d,m,e = mutate(change,both=both)
        earlier = old.check(d,m,e,test_only=True)
        self.assertTrue(earlier['integrity_ok'],
                        f'prior gate already detects {name}: '+str(earlier['errors']))
        newer = gate.check(d,m,e,test_only=True)
        self.assertFalse(newer['integrity_ok'],f'{name} unexpectedly accepted')
        self.assertEqual(newer['release_state'],'DRAFT_HARD_HOLD')
        self.assertFalse(newer['eligible'])
        self.assertFalse(newer['publication_approved'])
    test_case.__name__ = 'test_'+name
    return test_case

for name, fn in PARITY_CASES:
    setattr(Adversarial,'test_structure_'+name,make_case(name,fn,False))
for name, fn in ACCESSIBILITY_CASES:
    setattr(Adversarial,'test_accessibility_'+name,make_case(name,fn,True))


class Robustness(unittest.TestCase):
    def test_malformed_exports_fail_not_crash(self):
        d,m,e = fixture()
        e['guide-0'] = (None, e['guide-0'][1])
        r=gate.check(d,m,e,test_only=True)
        self.assertFalse(r['integrity_ok'])

    def test_missing_export_key_fails(self):
        d,m,e = fixture();e.pop('guide-0')
        self.assertFalse(gate.check(d,m,e,test_only=True)['integrity_ok'])

    def test_invalid_nonstring_slug_fails(self):
        d,m,e = fixture();e[2] = e.pop('guide-0')
        self.assertFalse(gate.check(d,m,e,test_only=True)['integrity_ok'])

    def test_invalid_utf8_fails(self):
        d,m,e = fixture();e['guide-0']=(b'\xff',e['guide-0'][1])
        self.assertFalse(gate.check(d,m,e,test_only=True)['integrity_ok'])

    def test_plain_text_markup_does_not_imply_source_review(self):
        d,m,e=fixture();r=gate.check(d,m,e,test_only=True)
        self.assertTrue(r['integrity_ok'])
        self.assertTrue(any('not original-manuscript' in x for x in r['warnings']))


if __name__=='__main__':
    unittest.main()
