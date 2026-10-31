"""R27 adverse citation placement fixtures: 35+ executable, no live safety PASS."""
from __future__ import annotations
from pathlib import Path
import copy
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import citation_fallback_review_gate as gate
import citation_token_visibility_gate as placement
from test_citation_fallback_review_gate import Library, SMALL


class VisibleTokenTests(unittest.TestCase):
    def test_original_synthetic_article_passes(self):
        self.assertEqual(len(placement.verified_citations(Library().articles['plan']['_body'])), 3)
        self.assertEqual(gate.audit(Library(), expected=SMALL)['counts']['citations'], 4)

    def test_original_unicode_offsets(self):
        s='<div>🌐🏡 — water {{cite:id}}\n next <em>☃</em>{{cite:other}}</div>'
        hits=placement.verified_citations(s)
        self.assertEqual([x.start() for x in hits],[s.index('{{cite:id}}'),s.index('{{cite:other}}')])

    def test_editorial_link_syntax_not_confused(self):
        self.assertEqual(len(placement.verified_citations('<p>{{link:start|Go}}<span>✓</span>{{cite:id}}</p>')),1)

    def test_repeated_same_source_preserved(self):
        s='<p>{{cite:id}}{{cite:id}}<b>{{cite:id}}</b></p>'
        self.assertEqual(len(placement.verified_citations(s)),3)

    def test_encoded_entities_do_not_shift_offsets(self):
        s='A &amp; B &#123; at ❤ {{cite:id}} next &copy; {{cite:id}}'
        self.assertEqual([m.start() for m in placement.verified_citations(s)],
                         [i for i in (s.index('{{cite:id}}'),s.rindex('{{cite:id}}'))])

    def test_large_multiline_unicode(self):
        s='<section>\n'+'<p>Δ𐍈 ×</p>\n'*60+'<p>final {{cite:id}}.</p>\n</section>'
        self.assertEqual(placement.verified_citations(s)[0].start(),s.index('{{cite:id}}'))

    def test_no_citations_yields_empty(self):
        self.assertEqual(placement.verified_citations('<p>No source tokens.</p>'),[])

    def test_do_not_mutate_input(self):
        body=Library().articles['plan']['_body']
        placement.verified_citations(body)
        self.assertEqual(body,Library().articles['plan']['_body'])


BAD = [
    ('missing_final_braces','<p>{{cite:a</p>'),
    ('single_closing_brace','<p>{{cite:a}</p>'),
    ('incomplete_open','<p>{{cite</p>'),
    ('empty_id','<p>{{cite:}}</p>'),
    ('space_before_colon','<p>{{cite :a}}</p>'),
    ('space_after_colon','<p>{{cite: a}}</p>'),
    ('space_in_id','<p>{{cite:a b}}</p>'),
    ('slash_id','<p>{{cite:../../x}}</p>'),
    ('script_url_id','<p>{{cite:https://example.org}}</p>'),
    ('quote_id','<p>{{cite:"a"}}</p>'),
    ('pipe_id','<p>{{cite:a|read}}</p>'),
    ('control_id','<p>{{cite:a\nb}}</p>'),
    ('uppercase_token','<p>{{CITE:a}}</p>'),
    ('mixedcase_token','<p>{{Cite:a}}</p>'),
    ('start_space','<p>{{ cite:a}}</p>'),
    ('start_newline','<p>{{\ncite:a}}</p>'),
    ('wrapped_syntax','<p>{{cite(a)}}</p>'),
    ('just_prefix','<p>{{cite:.</p>'),
    ('unclosed_in_comment','<!-- {{cite:a -->'),
    ('attribute_title','<p title="{{cite:a}}">Hi</p>'),
    ('attribute_alt','<img alt="{{cite:a}}">'),
    ('attribute_href','<a href="{{cite:a}}">Hi</a>'),
    ('attribute_data','<p data-proof="{{cite:a}}">Hi</p>'),
    ('attribute_onclick','<button onclick="{{cite:a}}">Hi</button>'),
    ('attribute_aria','<a aria-label="{{cite:a}}">Hi</a>'),
    ('attribute_newline','<div title="hello\n{{cite:a}}">ok</div>'),
    ('comment','<!-- {{cite:a}} -->'),
    ('comment_multiline','<!--\n{{cite:a}}\n-->'),
    ('doctype','<!DOCTYPE html {{cite:a}}><p>Hi</p>'),
    ('style','<style>.a{content:"{{cite:a}}"}</style>'),
    ('script','<script>const a="{{cite:a}}";</script>'),
    ('template','<template><p>{{cite:a}}</p></template>'),
    ('textarea','<textarea>{{cite:a}}</textarea>'),
    ('noscript','<noscript>{{cite:a}}</noscript>'),
    ('svg','<svg><text>{{cite:a}}</text></svg>'),
    ('math','<math><mn>{{cite:a}}</mn></math>'),
    ('iframe','<iframe>{{cite:a}}</iframe>'),
    ('object','<object>{{cite:a}}</object>'),
    ('pre','<pre>{{cite:a}}</pre>'),
    ('code','<code>{{cite:a}}</code>'),
    ('nested_inert','<script><p>{{cite:a}}</p></script>'),
    ('nontext_input','<input value="{{cite:a}}">'),
    ('nontext_meta','<meta content="{{cite:a}}">'),
    ('hidden_comment_adjacent','<p>{{cite:a}}</p><!-- {{cite:a}} -->'),
    ('valid_plus_malformed','<p>{{cite:a}} {{cite: a}}</p>'),
    ('valid_plus_hidden','<p>{{cite:a}} <span title="{{cite:a}}">ok</span></p>'),
    ('valid_plus_inert','<p>{{cite:a}}</p><style>{{cite:a}}</style>'),
]

class MalformedOrHidden(unittest.TestCase):
    pass


def make_bad(name, content):
    def test(self):
        with self.assertRaises(placement.CitationPlacementHold):
            placement.verified_citations(content)
    return test

for i,(name,content) in enumerate(BAD):
    setattr(MalformedOrHidden, 'test_%02d_%s' % (i,name),make_bad(name,content))


class EndToEndBoundary(unittest.TestCase):
    def test_invalid_extra_token_even_while_counts_unchanged(self):
        lib=Library()
        lib.articles['plan']['_body'] += '<p>{{cite: a}}</p>'
        with self.assertRaisesRegex(ValueError,'malformed'):
            gate.audit(lib, expected=SMALL)

    def test_hidden_extra_token_even_while_counts_unchanged(self):
        lib=Library()
        lib.articles['plan']['_body'] += '<!-- {{cite:a}} -->'
        with self.assertRaisesRegex(ValueError,'in HTML'):
            gate.audit(lib, expected=(1,1,5,3,1,1))

    def test_article_attribute_citation_detected(self):
        lib=Library()
        lib.articles['plan']['_body']=lib.articles['plan']['_body'].replace('{{cite:a}}','<b title="{{cite:a}}">Note</b>',1)
        with self.assertRaises(ValueError):
            gate.audit(lib, expected=SMALL)

    def test_plain_repeated_occurrences_no_collapse(self):
        lib=Library()
        lib.articles['plan']['_body']+='\n<p>More context for same source.{{cite:a}}</p>'
        p=gate.audit(lib, expected=(1,1,5,3,1,1))
        self.assertEqual(sum(row['citation_occurrences'] for row in p['review_queue']),5)

    def test_visible_cite_in_nested_format(self):
        lib=Library()
        lib.articles['plan']['_body']='<div><p><strong>Claim</strong>{{cite:a}}</p><p>{{cite:shared}}</p><p>{{cite:a}}</p></div>'
        self.assertEqual(gate.audit(lib, expected=SMALL)['counts']['citations'],4)


if __name__=='__main__':
    unittest.main()
