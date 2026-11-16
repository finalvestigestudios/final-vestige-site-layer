"""R411 exact implementation, 35-article fixtures and visibility/citation bypass regressions.

All content is synthetic. This is not a native WordPress/qualified-safety test.
"""
from __future__ import annotations
from pathlib import Path
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import r411_visible_evidence_gate as gate
import r410_full_slate_export_gate as old
from test_r410_full_slate_export_gate import fixture


def pair_with(html, slug='guide-0'):
    d, m, ex = fixture()
    ex[slug] = (html, html)
    return d, m, ex


def wrap(modifier):
    d, m, ex = fixture()
    html = ex['guide-0'][0]
    ex['guide-0'] = (modifier(html), modifier(html))
    return d, m, ex


class PositiveControls(unittest.TestCase):
    def test_complete_synthetic_fixture_stays_held(self):
        d,m,e=fixture(); r=gate.check(d,m,e,test_only=True)
        self.assertTrue(r['integrity_ok'],r['errors']); self.assertEqual(r['articles_inspected'],35)
        self.assertFalse(r['eligible']); self.assertFalse(r['publication_approved'])
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    def test_original_pin_still_required(self):
        d,m,e=fixture();self.assertFalse(gate.check(d,m,e)['integrity_ok'])
    def test_normalized_html_entities_not_false_hidden(self):
        d,m,e=wrap(lambda x:x.replace('Verified only','Verified &amp; documented only'))
        self.assertTrue(gate.check(d,m,e,test_only=True)['integrity_ok'])
    def test_aria_hidden_false_is_not_hidden(self):
        d,m,e=wrap(lambda x:'<main aria-hidden="false">'+x+'</main>')
        self.assertTrue(gate.check(d,m,e,test_only=True)['integrity_ok'])
    def test_details_open_valid_if_nesting_complete(self):
        d,m,e=wrap(lambda x:'<details open><summary>Detailed sources</summary>'+x+'</details>')
        self.assertTrue(gate.check(d,m,e,test_only=True)['integrity_ok'])
    def test_void_br_is_not_unclosed(self):
        d,m,e=wrap(lambda x:x.replace('<p>','<p><br>'))
        self.assertTrue(gate.check(d,m,e,test_only=True)['integrity_ok'])
    def test_missing_data_hard_hold_cli(self):
        p=subprocess.run([sys.executable,str(ROOT/'tools'/'r411_visible_evidence_gate.py'),'/no/original','/no/manifest','/no/exports'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertFalse(json.loads(p.stdout)['integrity_ok'])

class DemonstratedBypasses(unittest.TestCase):
    def test_r410_accepts_fully_hidden_35_article_pair(self):
        d,m,e=wrap(lambda x:'<div hidden>'+x+'</div>')
        old_result=old.check(d,m,e,test_only=True)
        self.assertTrue(old_result['integrity_ok'],old_result['errors'])
        new=gate.check(d,m,e,test_only=True)
        self.assertFalse(new['integrity_ok']); self.assertFalse(new['eligible'])
    def test_r410_accepts_bidi_override_in_reading_copy(self):
        d,m,e=wrap(lambda x:x.replace('This is draft','This is \u202edraft',1))
        self.assertTrue(old.check(d,m,e,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,test_only=True)['integrity_ok'])
    def test_r410_accepts_unbalanced_html(self):
        d,m,e=wrap(lambda x:x.replace('</article>','</section>',1))
        self.assertTrue(old.check(d,m,e,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,test_only=True)['integrity_ok'])
    def test_r410_accepts_reader_hidden_template(self):
        d,m,e=wrap(lambda x:'<template>'+x+'</template>')
        self.assertTrue(old.check(d,m,e,test_only=True)['integrity_ok'])
        self.assertFalse(gate.check(d,m,e,test_only=True)['integrity_ok'])
    def test_source_ids_and_duplicate_groups_inherit_exact_check(self):
        d,m,e=fixture();m['articles'][0]['sources']=['src-0','src-1']
        self.assertFalse(gate.check(d,m,e,test_only=True)['integrity_ok'])

# Distinct mutation cases exercise conservatively invisible or ambiguous evidence.
HIDDEN=[]
for tag in ('div','section','main','aside','article','header','footer','span','p','blockquote','figure','ul','li','hgroup'):
    HIDDEN.append(('html_hidden_'+tag,lambda x,tag=tag:f'<{tag} hidden>'+x+f'</{tag}>'))
    HIDDEN.append(('html_inert_'+tag,lambda x,tag=tag:f'<{tag} inert>'+x+f'</{tag}>'))
for val in ('true','TRUE','1','yes','True'):
    HIDDEN.append(('aria_hidden_'+val,lambda x,val=val:f'<main aria-hidden="{val}">'+x+'</main>'))
for css in ('hidden','is-hidden','u-hidden','d-none','display-none','invisible','sr-only','visually-hidden','screen-reader-text','opacity-0'):
    HIDDEN.append(('css_class_'+css,lambda x,css=css:f'<main class="article {css} careful">'+x+'</main>'))
for tag in ('template','noscript','dialog'):
    HIDDEN.append(('inert_element_'+tag,lambda x,tag=tag:f'<{tag}>'+x+f'</{tag}>'))
for attr in ('popover','popover="auto"','aria-expanded="false"'):
    HIDDEN.append(('concealing_attr_'+attr.replace('"','').replace('=','_'),lambda x,attr=attr:f'<section {attr}>'+x+'</section>'))
HIDDEN.append(('closed_details',lambda x:'<details><summary>Collapsed</summary>'+x+'</details>'))
HIDDEN.append(('hidden_source_only',lambda x:x.replace('<a data-source-id', '<a hidden data-source-id')))
HIDDEN.append(('hidden_heading_only',lambda x:x.replace('<h1>', '<h1 hidden>')))
for code in (0x202a,0x202b,0x202c,0x202d,0x202e,0x2066,0x2067,0x2068,0x2069,0x200b,0x200c,0x200d,0x200e,0x200f,0xfeff,0x061c,0x1f):
    HIDDEN.append(('control_'+format(code,'04x'),lambda x,code=code:x.replace('This is draft','This is '+chr(code)+'draft',1)))
for bad in (
    ('unclosed_section',lambda x:'<section>'+x),
    ('misnested_article',lambda x:x.replace('</article>','</div></article>')),
    ('orphan_section',lambda x:'</section>'+x),
    ('misnested_heading',lambda x:x.replace('</h1>','</h2>')),
    ('void_close',lambda x:x.replace('</article>','<br></br></article>')),
    ('unexpected_extra_closing',lambda x:x+'</section>'),
    ('nested_anchor',lambda x:x.replace('<a data-source-id','<a><a data-source-id').replace('</a></article>','</a></a></article>')),
    ('case_duplicate_attr',lambda x:x.replace('<article>','<article class="ok" CLASS="ok">')),
): HIDDEN.append(bad)

class MutationAttacks(unittest.TestCase): pass

def make_test(name, transform):
    def check_rejected(self):
        d,m,e=wrap(transform)
        r=gate.check(d,m,e,test_only=True)
        self.assertFalse(r['integrity_ok'],name+' unexpectedly passed: '+str(r))
        self.assertFalse(r['eligible']);self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    check_rejected.__name__='test_'+name
    return check_rejected

for name, transform in HIDDEN:
    setattr(MutationAttacks,'test_'+name,make_test(name,transform))

if __name__=='__main__': unittest.main()
