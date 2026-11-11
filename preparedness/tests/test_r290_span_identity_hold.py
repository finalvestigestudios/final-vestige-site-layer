"""R290: synthetic exact-span citation identity and reader-context regression tests.

No production content, repository-source writes, merchant calls or QD approval.
"""
from collections import Counter
import hashlib
import importlib.util
from pathlib import Path
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'

def load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + '.py'))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

r288 = load('r288_reader_exposure_citation_hold')
r289 = load('r289_claim_context_review_hold')

def canonical(raw, name):
    text = raw.decode('utf-8')
    ids = r289.CITE.findall(text)
    if len(ids) != text.count('{{cite:'):
        raise ValueError('synthetic malformed source')
    return Counter(ids)

def scan(text):
    return r289.scan_document(text.encode(), 'synthetic', r288.scan_body, canonical)

class ExactSpanRegression(unittest.TestCase):
    def test_upstream_same_id_cancellation_reproduced(self):
        raw = b'<span hidden>{{cite:a}}</span><p>{{ci<b>te:a}}</b></p>'
        self.assertEqual(r288.scan_body(raw, 'synthetic', canonical)['inline_occurrences'], 1)
        with self.assertRaisesRegex(ValueError, 'nonreader hidden'):
            scan(raw.decode())

    def test_distinct_occurrence_positions(self):
        text = '<p>{{cite:a}} and {{cite:a}}</p>'
        edges = scan(text)['source_edges']
        self.assertEqual(len(edges), 2)
        self.assertNotEqual(edges[0]['raw_start'], edges[1]['raw_start'])
        for edge in edges:
            self.assertEqual(text[edge['raw_start']:edge['raw_end']], '{{cite:a}}')

    def test_unicode_position(self):
        text = '<p>Café 👩‍🚒 {{cite:a}}</p>'
        self.assertEqual(scan(text)['source_edges'][0]['raw_start'], text.index('{{cite:a}}'))

    def test_entity_formula_digest(self):
        edge = scan('<p>3 &times; 4 = 12 {{cite:a}}</p>')['source_edges'][0]
        self.assertIn('3 × 4 = 12', edge['review_excerpt'])
        self.assertEqual(edge['context_sha256'], hashlib.sha256('3 × 4 = 12'.encode()).hexdigest())

    def test_entity_ampersand_context(self):
        self.assertIn('Harper & Brothers', scan('<p>Harper &amp; Brothers {{cite:a}}</p>')['source_edges'][0]['review_excerpt'])

    def test_entity_equivalence(self):
        a = scan('<p>A &times; B {{cite:a}}</p>')['source_edges'][0]['context_sha256']
        b = scan('<p>A &#215; B {{cite:a}}</p>')['source_edges'][0]['context_sha256']
        self.assertEqual(a, b)

    def test_hidden_claim_cannot_fill_empty_context(self):
        edge = scan('<p><span hidden>HIDDEN BAD CLAIM</span>{{cite:a}}</p>')['source_edges'][0]
        self.assertIn('no-claim-text-in-block', edge['review_flags'])
        self.assertNotIn('HIDDEN', edge['review_excerpt'])

    def test_hidden_prose_not_in_context_digest(self):
        a = scan('<p>Visible {{cite:a}}</p>')['source_edges'][0]['context_sha256']
        b = scan('<p><span aria-hidden="true">Hidden</span>Visible {{cite:a}}</p>')['source_edges'][0]['context_sha256']
        self.assertEqual(a, b)

    def test_entity_assembled_source_rejected(self):
        with self.assertRaisesRegex(ValueError, 'assembled'):
            scan('<p>&#123;&#123;cite:a&#125;&#125;</p>')

    def test_entity_assembled_plus_real_source_rejected(self):
        with self.assertRaisesRegex(ValueError, 'assembled'):
            scan('<p>&#123;&#123;cite:a&#125;&#125; {{cite:a}}</p>')

    def test_comment_and_split_not_cancellation(self):
        with self.assertRaises(ValueError):
            scan('<!-- {{cite:a}} --><p>{{ci<b>te:a}}</b></p>')

    def test_no_approval_from_mechanical_gate(self):
        result = scan('<p>Claim {{cite:a}}</p>')
        self.assertTrue(result['source_occurrence_identity_verified'])
        self.assertFalse(result['source_scope_verified'])
        self.assertFalse(result['browser_visibility_verified'])
        status = r289.audit('/nonexistent/r290')
        self.assertFalse(status['publication_authorized'])
        self.assertFalse(status['independent_qd_pass'])

HIDDEN_TAGS = ['head', 'script', 'style', 'template', 'noscript', 'iframe',
               'svg', 'math', 'canvas', 'object', 'textarea', 'select', 'option', 'datalist']
for i, tag in enumerate(HIDDEN_TAGS):
    def negative(self, element=tag):
        with self.assertRaises(ValueError):
            scan('<' + element + '>{{cite:a}}</' + element + '>')
    setattr(ExactSpanRegression, 'test_hidden_element_%02d' % i, negative)

HIDDEN_PARENTS = ['hidden', 'inert', 'aria-hidden="true"', 'style="display:none"',
                  'style="visibility:hidden"', 'style="content-visibility:hidden"',
                  'style="opacity:0"', 'style="filter:opacity(0)"', 'style="transform:scale(0)"']
for i, attr in enumerate(HIDDEN_PARENTS):
    def negative(self, attribute=attr):
        with self.assertRaises(ValueError):
            scan('<div ' + attribute + '><p>{{cite:a}}</p></div>')
    setattr(ExactSpanRegression, 'test_hidden_parent_%02d' % i, negative)

BLOCKS = ['p', 'li', 'td', 'th', 'blockquote', 'figcaption', 'caption',
          'dt', 'dd', 'summary', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
for i, tag in enumerate(BLOCKS):
    def positive(self, block=tag):
        edge = scan('<' + block + '>Claim {{cite:a}}</' + block + '>')['source_edges'][0]
        self.assertEqual(edge['block_tag'], block)
    setattr(ExactSpanRegression, 'test_reader_block_%02d' % i, positive)

if __name__ == '__main__':
    unittest.main()
