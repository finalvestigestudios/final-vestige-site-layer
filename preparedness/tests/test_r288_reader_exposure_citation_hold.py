"""R288 pure synthetic citation-context adversarial tests (no repository writes)."""
from __future__ import annotations
from collections import Counter
import importlib.util
from pathlib import Path
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1]/'tools/r288_reader_exposure_citation_hold.py'
spec = importlib.util.spec_from_file_location('fv_r288_test',PATH)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

def parent_parser(raw, name):
    s=raw.decode('utf8')
    tokens=list(g.CITE.finditer(s))
    if s.count('{{cite:')!=len(tokens):
        raise ValueError('malformed parent marker')
    return Counter(m.group(1) for m in tokens)

def scan(s):
    return g.scan_body(s.encode('utf-8'),'synthetic',parent_parser)

class ReaderCitationContext(unittest.TestCase):
    def test_empty(self): self.assertEqual(scan('<p>hello</p>')['inline_occurrences'],0)
    def test_visible(self): self.assertEqual(scan('<p>source {{cite:proof}}</p>')['inline_occurrences'],1)
    def test_multiple(self): self.assertEqual(scan('{{cite:a}}{{cite:a}}{{cite:b}}')['inline_occurrences'],3)
    def test_nested(self): self.assertEqual(scan('<article><p><em>{{cite:a}}</em></p></article>')['inline_occurrences'],1)
    def test_src_counts(self): self.assertEqual(scan('{{cite:a}}{{cite:b}}{{cite:b}}')['distinct_source_ids'],2)
    def test_html_entities(self): self.assertEqual(scan('<p>&amp; {{cite:a}} &lt;cite&gt;</p>')['inline_occurrences'],1)
    def test_non_ascii(self): self.assertEqual(scan('<p>Café {{cite:cafe}}</p>')['inline_occurrences'],1)
    def test_details(self): self.assertEqual(scan('<details><summary>Proof {{cite:a}}</summary></details>')['inline_occurrences'],1)
    def test_void(self): self.assertEqual(scan('<p>Proof<br/>{{cite:a}}</p>')['inline_occurrences'],1)
    def test_selfclosing(self): self.assertEqual(scan('<hr/><p>{{cite:a}}</p>')['inline_occurrences'],1)
    def test_missing_root(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(g.audit(d)['state'],g.INVALID)
    def test_load_parent_missing(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'missing'):g.load_parent(d)
    def test_load_parent_bad_sha(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/g.PARENT;p.parent.mkdir(parents=True);p.write_text('def audit(x):pass')
            with self.assertRaisesRegex(ValueError,'drift'):g.load_parent(d)
    def test_no_approval_fields(self):
        r=scan('<p>{{cite:x}}</p>');self.assertIs(r['render_visibility_verified'],False)
        self.assertIs(r['human_source_scope_verified'],False)
    def test_raw_zero_text_citation(self): self.assertEqual(scan('<p>No citation at all.</p>')['inline_occurrences'],0)

INVALID_SNIPPETS = [
 '<!-- {{cite:a}} -->','<p>{{cite:a}}</p><!-- {{cite:b}} -->',
 '<div title="{{cite:a}}">text</div>','<a href="{{cite:a}}">link</a>',
 '<img alt="{{cite:a}}">','<div data-cite="{{cite:a}}"></div>',
 '<script>{{cite:a}}</script>','<style>{{cite:a}}</style>',
 '<template>{{cite:a}}</template>','<head>{{cite:a}}</head>',
 '<noscript>{{cite:a}}</noscript>','<iframe>{{cite:a}}</iframe>',
 '<svg><text>{{cite:a}}</text></svg>','<math>{{cite:a}}</math>',
 '<canvas>{{cite:a}}</canvas>','<object>{{cite:a}}</object>',
 '<div hidden>{{cite:a}}</div>','<div hidden="until-found">{{cite:a}}</div>',
 '<div inert>{{cite:a}}</div>','<div aria-hidden="true">{{cite:a}}</div>',
 '<div style="display:none">{{cite:a}}</div>',
 '<div style="visibility:hidden">{{cite:a}}</div>',
 '<div style="content-visibility:hidden">{{cite:a}}</div>',
 '<div style="background:red; display: none !important">{{cite:a}}</div>',
 '<section aria-hidden="true"><p>{{cite:a}}</p></section>',
 '<section><span style="display:none">{{cite:a}}</span></section>',
 '<p>{{cite:a}}</p><style>{{cite:b}}</style>',
 '<p>{{cite:a}}</p><script>{{cite:b}}</script>',
 '<div title="{{cite:a}}"><p>{{cite:b}}</p></div>',
 '<div aria-hidden="true"><span>{{cite:a}}</span></div>',
 '<p>{{ci<strong>te:a}}</strong></p>',
]
for i,sample in enumerate(INVALID_SNIPPETS):
    def bad(self, html=sample):
        with self.assertRaises(ValueError):scan(html)
    setattr(ReaderCitationContext,'test_context_reject_%02d'%i,bad)

class FailClosedContract(unittest.TestCase):
    def test_invalid_root(self): self.assertEqual(g.audit('/does/not/exist')['state'],g.INVALID)
    def test_not_utf8(self):
        with self.assertRaises(UnicodeError):g.scan_body(b'\xff','bad',parent_parser)
    def test_nonbytes(self):
        with self.assertRaises(ValueError):g.scan_body('x','bad',parent_parser)
    def test_not_callable(self):
        with self.assertRaises(ValueError):g.scan_body(b'hi','bad',None)
    def test_bad_marker(self):
        with self.assertRaises(ValueError):scan('{{cite:a')
    def test_duplicate_visible(self): self.assertEqual(scan('{{cite:x}}{{cite:x}}')['inline_occurrences'],2)
    def test_boolean_inert_attr(self):
        with self.assertRaises(ValueError):scan('<div inert="">{{cite:x}}</div>')
    def test_boolean_hidden_attr(self):
        with self.assertRaises(ValueError):scan('<div hidden="false">{{cite:x}}</div>')
    def test_mixed_hidden_visible(self):
        with self.assertRaises(ValueError):scan('<p>{{cite:a}}<i hidden>{{cite:b}}</i></p>')
    def test_comment_no_citation(self): self.assertEqual(scan('<!-- note --><p>{{cite:a}}</p>')['inline_occurrences'],1)

if __name__=='__main__':unittest.main(verbosity=2)
