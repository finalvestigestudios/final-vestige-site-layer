"""R291 synthetic regression: a citation's claim context must exclude non-reader siblings.

Read-only unit tests. Never represent HTML-parser output as actual browser visibility,
source-scope verification, medical/publication approval, or a CMS release gate.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import importlib.util
from pathlib import Path
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'


def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


r288 = load('r288_reader_exposure_citation_hold')
r289 = load('r289_claim_context_review_hold')


def canonical(raw, name):
    text = raw.decode('utf-8')
    literal = list(r289.CITE.finditer(text))
    if text.count('{{cite:') != len(literal):
        raise ValueError('malformed synthetic citation')
    return Counter(m.group(1) for m in literal)


def scan(text):
    return r289.scan_document(text.encode('utf-8'), 'synthetic', r288.scan_body, canonical)


def edge(text):
    result = scan(text)
    assert len(result['source_edges']) == 1
    return result['source_edges'][0]


BASE_TEXT = 'Visible supporting claim'
BASE = '<p>' + BASE_TEXT + ' {{cite:a}}</p>'
EMPTY = '<p>{{cite:a}}</p>'
BASE_EDGE = None  # Avoid building a false shared test assertion at import time.


class ContextIsolation(unittest.TestCase):
    def test_empty_block_flag(self):
        self.assertIn('no-claim-text-in-block', edge(EMPTY)['review_flags'])

    def test_visible_prose_baseline_digest(self):
        self.assertEqual(edge(BASE)['context_sha256'], hashlib.sha256(BASE_TEXT.encode()).hexdigest())

    def test_existing_visible_citation_preserves_span(self):
        doc = '<p><span style="opacity:0">Not available</span>' + BASE_TEXT + ' {{cite:a}}</p>'
        e = edge(doc)
        self.assertEqual(doc[e['raw_start']:e['raw_end']], '{{cite:a}}')
        self.assertIn('source_occurrence_identity_verified', scan(doc))

    def test_hidden_only_claim_not_accepted(self):
        e = edge('<p><span style="opacity:0">Fake evidence</span>{{cite:a}}</p>')
        self.assertIn('no-claim-text-in-block', e['review_flags'])
        self.assertNotIn('Fake evidence', e['review_excerpt'])
        self.assertEqual(e['context_sha256'], hashlib.sha256(b'').hexdigest())
        self.assertIn('excluded-nonreader-sibling-context', e['review_flags'])

    def test_control_only_claim_not_accepted(self):
        e = edge('<p><textarea>Fake evidence</textarea>{{cite:a}}</p>')
        self.assertIn('no-claim-text-in-block', e['review_flags'])
        self.assertNotIn('Fake evidence', e['review_excerpt'])
        self.assertIn('excluded-nonreader-sibling-context', e['review_flags'])

    def test_css_prose_not_in_excerpt_before(self):
        e = edge('<p><b style="filter:opacity(0)">DO NOT USE</b>Claim {{cite:a}}</p>')
        self.assertNotIn('DO NOT USE', e['review_excerpt'])
        self.assertIn('excluded-nonreader-sibling-context', e['review_flags'])

    def test_css_prose_not_in_excerpt_after(self):
        e = edge('<p>Claim {{cite:a}}<i style="transform:scale(0)">DO NOT USE</i></p>')
        self.assertNotIn('DO NOT USE', e['review_excerpt'])

    def test_control_prose_not_in_excerpt(self):
        e = edge('<p><select><option>DO NOT USE</option></select>Claim {{cite:a}}</p>')
        self.assertNotIn('DO NOT USE', e['review_excerpt'])

    def test_entity_decoding_still_supported(self):
        e = edge('<p>Visible &times; 4 {{cite:a}}</p>')
        self.assertIn('Visible × 4', e['review_excerpt'])
        self.assertNotIn('excluded-nonreader-sibling-context', e['review_flags'])

    def test_hidden_entity_ignored(self):
        e = edge('<p><span style="opacity:0">Fake &times; source</span>{{cite:a}}</p>')
        self.assertEqual(e['context_sha256'], hashlib.sha256(b'').hexdigest())

    def test_control_entity_ignored(self):
        e = edge('<p><textarea>Fake &amp; source</textarea>{{cite:a}}</p>')
        self.assertEqual(e['context_sha256'], hashlib.sha256(b'').hexdigest())

    def test_source_inside_css_still_rejected(self):
        with self.assertRaisesRegex(ValueError, 'CSS-concealed'):
            scan('<p><span style="opacity:0">{{cite:a}}</span></p>')

    def test_source_inside_control_still_rejected(self):
        with self.assertRaisesRegex(ValueError, 'non-narrative'):
            scan('<p><textarea>{{cite:a}}</textarea></p>')

    def test_hidden_literal_source_still_rejected(self):
        with self.assertRaisesRegex(ValueError, 'nonreader'):
            scan('<p><span aria-hidden="true">{{cite:a}}</span></p>')

    def test_markup_assembled_source_still_rejected(self):
        with self.assertRaisesRegex(ValueError, 'assembled|markup-split'):
            scan('<p>{{ci<em>te:a}}</em></p>')

    def test_no_false_release(self):
        self.assertFalse(scan(BASE)['source_scope_verified'])
        self.assertFalse(scan(BASE)['browser_visibility_verified'])
        self.assertEqual(r289.audit('/invalid/nonexistent')['state'], 'INVALID_HARD_HOLD')


# Exact existing CSS hard-hide variants, now applied to uncited siblings rather than citations.
HARD_CSS = [
    'opacity:0', 'opacity: 0', 'opacity:0.0', 'opacity:.0', 'opacity:0%',
    'opacity: 0 !important', 'color:red;opacity:0', 'OPACITY:0',
    'opacity:/* note */0', 'filter:opacity(0)', 'filter: opacity(0%)',
    '-webkit-filter:opacity(0)', 'filter:blur(2px) opacity(0)',
    'transform:scale(0)', 'transform: scale(0.0)',
    'color:blue;transform:scale(0)',
]
for i, css in enumerate(HARD_CSS):
    def css_before(self, style=css):
        document = '<p><span style="' + style + '">HIDDEN</span>' + BASE_TEXT + ' {{cite:a}}</p>'
        self.assertEqual(edge(document)['context_sha256'], edge(BASE)['context_sha256'])
        self.assertNotIn('HIDDEN', edge(document)['review_excerpt'])
    setattr(ContextIsolation, f'test_css_hidden_sibling_before_{i:02d}', css_before)

    def css_only(self, style=css):
        document = '<p><span style="' + style + '">FABRICATED CONTEXT</span>{{cite:a}}</p>'
        self.assertIn('no-claim-text-in-block', edge(document)['review_flags'])
    setattr(ContextIsolation, f'test_css_only_sibling_{i:02d}', css_only)


CONTROLS = ('textarea', 'select', 'option', 'datalist')
for i, tag in enumerate(CONTROLS):
    def control_before(self, element=tag):
        document = '<p><' + element + '>HIDDEN CONTEXT</' + element + '>' + BASE_TEXT + ' {{cite:a}}</p>'
        self.assertEqual(edge(document)['context_sha256'], edge(BASE)['context_sha256'])
    setattr(ContextIsolation, f'test_form_sibling_{i:02d}', control_before)

    def control_only(self, element=tag):
        document = '<p><' + element + '>HIDDEN CONTEXT</' + element + '>{{cite:a}}</p>'
        self.assertIn('no-claim-text-in-block', edge(document)['review_flags'])
    setattr(ContextIsolation, f'test_form_only_{i:02d}', control_only)


HIDDEN_ATTRS = ('hidden', 'inert', 'aria-hidden="true"',
                'style="display:none"', 'style="visibility:hidden"',
                'style="content-visibility:hidden"')
for i, attr in enumerate(HIDDEN_ATTRS):
    def hidden_before(self, a=attr):
        document = '<p><span ' + a + '>HIDDEN CONTEXT</span>' + BASE_TEXT + ' {{cite:a}}</p>'
        self.assertEqual(edge(document)['context_sha256'], edge(BASE)['context_sha256'])
    setattr(ContextIsolation, f'test_attribute_hidden_sibling_{i:02d}', hidden_before)


ENTITIES = ('&amp;', '&times;', '&#215;', '&#xD7;', '&lt;', '&gt;')
for i, ref in enumerate(ENTITIES):
    def hard_entity(self, entity=ref):
        document = '<p><span style="opacity:0">FAKE ' + entity + ' PROOF</span>{{cite:a}}</p>'
        self.assertIn('no-claim-text-in-block', edge(document)['review_flags'])
    setattr(ContextIsolation, f'test_hard_entity_{i:02d}', hard_entity)

    def control_entity(self, entity=ref):
        document = '<p><textarea>FAKE ' + entity + ' PROOF</textarea>{{cite:a}}</p>'
        self.assertIn('no-claim-text-in-block', edge(document)['review_flags'])
    setattr(ContextIsolation, f'test_control_entity_{i:02d}', control_entity)


if __name__ == '__main__':
    unittest.main(verbosity=2)
