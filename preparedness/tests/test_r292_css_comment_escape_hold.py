"""R292: fail-closed source-level citation integrity for CSS comments and escapes.

This is NOT a CSS/browser renderer, medical assertion, or publication approval.
All synthetic fixtures are in memory; nothing writes to source directories.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import hashlib
import importlib.util
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'

def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name+'.py'))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

r288 = load('r288_reader_exposure_citation_hold')
r289 = load('r289_claim_context_review_hold')

def canonical(raw, name):
    return Counter(m.group(1) for m in r289.CITE.finditer(raw.decode('utf-8')))

def inspect(markup):
    return r289.scan_document(markup.encode('utf-8'), 'synthetic-r292',
                              r288.scan_body, canonical)

def one(markup):
    edges = inspect(markup)['source_edges']
    assert len(edges) == 1
    return edges[0]

HARD = (
    ('display', 'none'), ('visibility', 'hidden'),
    ('visibility', 'collapse'), ('content-visibility', 'hidden'))

class CssSafety(unittest.TestCase):
    def test_prepatch_failure_was_reproducible(self):
        self.assertIn('display-none',r289.style_flags('display:/**/none')[0])
        self.assertNotRegex('display:/**/none',r288.HIDE_STYLE)

    def test_no_release_for_invalid_root(self):
        result = r289.audit('/definitely/not/a/preparedness/checkout')
        self.assertEqual(result['state'],r289.INVALID)
        for key in ('publication_authorized','independent_qd_pass',
                    'medical_safety_verified','privacy_approved'):
            self.assertIs(result[key],False)

    def test_escaped_property(self):
        self.assertIn('display-none', r289.style_flags(r'di\73play:/**/none')[0])

    def test_escaped_value(self):
        self.assertIn('display-none', r289.style_flags(r'display:n\6f ne')[0])

    def test_css_untrusted_dynamic_value_review(self):
        entry = one('<p style="display:var(--display)">Claim {{cite:a}}</p>')
        self.assertIn('dynamic-css-visibility-unverified',entry['review_flags'])
        self.assertFalse(inspect('<p>Claim {{cite:a}}</p>')['browser_visibility_verified'])

    def test_external_style_unverified_not_approved(self):
        for html in ('<p class="maybe">Text {{cite:a}}</p>',
                     '<div id="maybe"><p>Text {{cite:a}}</p></div>'):
            self.assertIn('external-css-visibility-unverified',one(html)['review_flags'])

    def test_source_identity_remains_exact(self):
        html = '<p style="color:navy">Claim {{cite:a}}</p>'
        entry = one(html)
        self.assertEqual(html[entry['raw_start']:entry['raw_end']], '{{cite:a}}')
        self.assertEqual(entry['context_sha256'], hashlib.sha256(b'Claim').hexdigest())

    def test_synthetic_hold_preserves_body_fields(self):
        res = inspect('<p>Claim {{cite:a}}</p>')
        self.assertEqual(res['count'],1)
        self.assertTrue(res['source_occurrence_identity_verified'])
        self.assertFalse(res['source_scope_verified'])
        self.assertFalse(res['browser_visibility_verified'])

# A real citation in a CSS-hidden element must not be counted as reader-facing.
# Each name and mutation is unique, and all fixtures stay in memory.
VARIANTS = (
    '{prop}:/**/{value}',
    '{prop}:/*comment*/ {value}',
    '{prop}: {value} /*comment*/ !important',
    '{prop}: {value} ; color: blue',
    'font-size:12px; {prop}:/* multi\nline */{value}',
    '{prop}: {start}/*comment*/{end}',
    '{prop}:/*one*//*two*/{value}',
    '{prop}: {upper} !IMPORTANT',
)
for index, (property_name, value) in enumerate(HARD):
    for variant_index, fmt in enumerate(VARIANTS):
        candidate = fmt.format(prop=property_name, value=value,
                               start=value[:2], end=value[2:], upper=value.upper())
        def concealed_citation(self, css=candidate):
            html = '<p><span style="'+css+'">{{cite:a}}</span></p>'
            with self.assertRaises((ValueError,)):
                inspect(html)
        setattr(CssSafety, f'test_hidden_citation_{index}_{variant_index}', concealed_citation)

        def sibling_exclusion(self, css=candidate):
            html = '<p><span style="'+css+'">UNSUPPORTED SAFETY CLAIM</span>Visible claim {{cite:a}}</p>'
            e = one(html)
            self.assertNotIn('UNSUPPORTED', e['review_excerpt'])
            self.assertIn('excluded-nonreader-sibling-context',e['review_flags'])
            self.assertEqual(e['context_sha256'],hashlib.sha256(b'Visible claim').hexdigest())
        setattr(CssSafety, f'test_hidden_sibling_{index}_{variant_index}', sibling_exclusion)

ESCAPED = (
    r'di\73play: none',
    r'display: n\6f ne',
    r'display: \6e one',
    r'v\69sibility: hidden',
    r'visibility: h\69 dden',
    r'content-visibility: \68 idden',
    r'display:\00006E one',
    r'display: no/**/ne',
    r'display:n\6f/**/ne',
    r'visibility: h\69/**/dden',
)
for index, css in enumerate(ESCAPED):
    def escaped_cite(self, style=css):
        html='<div style="'+style+'"><p>Example {{cite:a}}</p></div>'
        with self.assertRaisesRegex(ValueError,'concealed|hidden|nonreader'):
            inspect(html)
    setattr(CssSafety, f'test_escaped_citation_{index}', escaped_cite)

    def escaped_claim(self, style=css):
        html='<p><span style="'+style+'">FALSE SUPPORT</span>Documented claim {{cite:a}}</p>'
        e=one(html)
        self.assertNotIn('FALSE SUPPORT',e['review_excerpt'])
        self.assertIn('excluded-nonreader-sibling-context',e['review_flags'])
    setattr(CssSafety, f'test_escaped_sibling_{index}', escaped_claim)

VISIBLE_STYLES=(
    'display:contents','display:block','display:inline',
    'visibility:visible','content-visibility:visible',
    'opacity:1','color:transparent','--display:none',
    'background-image:url("display:none")','display:grid',
)
for index, css in enumerate(VISIBLE_STYLES):
    def visible(self, style=css):
        result=one('<p style="'+style+'">Claim {{cite:a}}</p>')
        self.assertNotIn('display-none',result['review_flags'])
        self.assertEqual(result['source_id'],'a')
        self.assertFalse(inspect('<p style="'+style+'">Claim {{cite:a}}</p>')['browser_visibility_verified'])
    setattr(CssSafety,f'test_nonhard_style_{index}',visible)

if __name__=='__main__': unittest.main(verbosity=2)
