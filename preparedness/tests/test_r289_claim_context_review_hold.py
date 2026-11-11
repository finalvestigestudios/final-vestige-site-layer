"""R289 isolated reader-context/CSS-risk regression suite. Pure synthetic; no source writes."""
from collections import Counter
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]/'tools'

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT/filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

r289=load('r289_test_exact','r289_claim_context_review_hold.py')
r288=load('r288_test_exact','r288_reader_exposure_citation_hold.py')

def canonical(raw, name):
    text=raw.decode('utf8')
    results=list(r289.CITE.finditer(text))
    if text.count('{{cite:') != len(results):
        raise ValueError('malformed literal source marker')
    return Counter(m.group(1) for m in results)

def scan(text):
    return r289.scan_document(text.encode('utf-8'),'synthetic',r288.scan_body,canonical)

class BasicReviewLedger(unittest.TestCase):
    def test_empty(self): self.assertEqual(scan('<p>No citations.</p>')['count'],0)
    def test_one(self): self.assertEqual(scan('<p>Source {{cite:one}}</p>')['count'],1)
    def test_two(self): self.assertEqual(scan('<p>A {{cite:a}} B {{cite:b}}</p>')['count'],2)
    def test_source_ids(self): self.assertEqual([x['source_id'] for x in scan('{{cite:z}}{{cite:a}}')['source_edges']],['z','a'])
    def test_full_hold(self): self.assertIs(scan('{{cite:a}}')['source_scope_verified'],False)
    def test_browser_unverified(self): self.assertIs(scan('{{cite:a}}')['browser_visibility_verified'],False)
    def test_context_digest(self): self.assertEqual(len(scan('<p>Some claim {{cite:a}}</p>')['source_edges'][0]['context_sha256']),64)
    def test_source_anchor(self): self.assertIn('[SOURCE]',scan('<p>Fact {{cite:a}}</p>')['source_edges'][0]['review_excerpt'])
    def test_non_ascii(self): self.assertIn('Café',scan('<p>Café {{cite:cafe}}</p>')['source_edges'][0]['review_excerpt'])
    def test_nested_citation(self): self.assertEqual(scan('<p>Claim <em>{{cite:a}}</em></p>')['source_edges'][0]['block_tag'],'p')
    def test_list_citation(self): self.assertEqual(scan('<ul><li>Claim {{cite:a}}</li></ul>')['source_edges'][0]['block_tag'],'li')
    def test_table_citation(self): self.assertEqual(scan('<table><tr><td>A {{cite:a}}</td></tr></table>')['source_edges'][0]['block_tag'],'td')
    def test_title_citation(self): self.assertEqual(scan('<h2>A {{cite:a}}</h2>')['source_edges'][0]['block_tag'],'h2')
    def test_implicit_flag(self): self.assertIn('no-semantic-block',scan('Fact {{cite:a}}')['source_edges'][0]['review_flags'])
    def test_empty_block_flag(self): self.assertIn('no-claim-text-in-block',scan('<p>{{cite:a}}</p>')['source_edges'][0]['review_flags'])
    def test_reading_text(self): self.assertNotIn('{{cite',scan('<p>Fact {{cite:a}}</p>')['source_edges'][0]['context_sha256'])
    def test_repeat(self): self.assertEqual(scan('<p>Fact {{cite:a}}{{cite:a}}</p>')['count'],2)
    def test_comments_no_source(self): self.assertEqual(scan('<!-- note --><p>{{cite:a}}</p>')['count'],1)
    def test_entities(self): self.assertEqual(scan('<p>&amp; source {{cite:a}}</p>')['count'],1)
    def test_void(self): self.assertEqual(scan('<p>Fact<br/>{{cite:a}}</p>')['count'],1)
    def test_siblings_independent_blocks(self):
        edges=scan('<p>One {{cite:a}}</p><p>Two {{cite:b}}</p>')['source_edges']
        self.assertNotEqual(edges[0]['context_sha256'],edges[1]['context_sha256'])
    def test_same_claim_context_for_siblings(self):
        edges=scan('<p>One {{cite:a}} Two {{cite:b}}</p>')['source_edges']
        self.assertEqual(edges[0]['context_sha256'],edges[1]['context_sha256'])
    def test_line_column(self):
        e=scan('<p>Start\nSecond {{cite:a}}</p>')['source_edges'][0]
        self.assertEqual(e['line'],2);self.assertGreaterEqual(e['column'],7)
    def test_does_not_store_complete_shortened_excerpt(self):
        self.assertLessEqual(len(scan('<p>'+'x'*500+'{{cite:a}}'+'</p>')['source_edges'][0]['review_excerpt']),240)
    def test_collapsed_details_flag(self):
        e=scan('<details><p>Hidden until opened {{cite:a}}</p></details>')['source_edges'][0]
        self.assertIn('closed-details-disclosure',e['review_flags'])
    def test_open_details_no_flag(self):
        e=scan('<details open><p>Claim {{cite:a}}</p></details>')['source_edges'][0]
        self.assertNotIn('closed-details-disclosure',e['review_flags'])
    def test_summary_default_visible(self):
        e=scan('<details><summary>Label {{cite:a}}</summary></details>')['source_edges'][0]
        self.assertNotIn('closed-details-disclosure',e['review_flags'])
    def test_opacity_parent(self):
        with self.assertRaisesRegex(ValueError,'CSS-concealed'):scan('<div style="opacity:0"><p>{{cite:a}}</p></div>')
    def test_css_font_zero_flag(self):
        e=scan('<p style="font-size:0">Fact {{cite:a}}</p>')['source_edges'][0]
        self.assertIn('font-size-zero',e['review_flags'])
    def test_css_transparent_flag(self):
        e=scan('<p style="color:transparent">Fact {{cite:a}}</p>')['source_edges'][0]
        self.assertIn('transparent-text',e['review_flags'])
    def test_css_clipped_flag(self):
        e=scan('<p style="clip-path:inset(50%)">Fact {{cite:a}}</p>')['source_edges'][0]
        self.assertIn('css-clipping',e['review_flags'])
    def test_hold_invalid_root(self): self.assertEqual(r289.audit('/never/existing/path')['state'],r289.INVALID)
    def test_load_missing(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'missing'):r289.load_parent(d)
    def test_load_tampered(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/r289.PARENT;p.parent.mkdir(parents=True);p.write_text('def audit(x):return {}')
            with self.assertRaisesRegex(ValueError,'drift'):r289.load_parent(d)
    def test_no_false_release_in_error(self):
        o=r289.audit('/nonexistent');self.assertIs(o['publication_authorized'],False)
        self.assertIs(o['independent_qd_pass'],False)
        self.assertIs(o['medical_safety_verified'],False)
    def test_error_bad_parser(self):
        with self.assertRaises(ValueError):r289.scan_document(b'abc','bad',None,canonical)
    def test_error_nonbytes(self):
        with self.assertRaises(ValueError):r289.scan_document('abc','bad',r288.scan_body,canonical)
    def test_error_unmatched_end_tag(self):
        with self.assertRaisesRegex(ValueError,'tag structure'):scan('<p>Claim {{cite:a}}</p></section>')
    def test_error_non_utf8(self):
        with self.assertRaises(UnicodeError):r289.scan_document(b'\xff','bad',r288.scan_body,canonical)
    def test_error_bad_marker(self):
        with self.assertRaises(ValueError):scan('<p>{{cite:a</p>')

HARD_CSS = [
    'opacity:0', 'opacity: 0', 'opacity:0.0', 'opacity:.0', 'opacity:0%',
    'opacity: 0 !important', 'color:red;opacity:0', 'OPACITY:0',
    'opacity:/* note */0', 'filter:opacity(0)', 'filter: opacity(0%)',
    '-webkit-filter:opacity(0)', 'filter:blur(2px) opacity(0)',
    'transform:scale(0)', 'transform: scale(0.0)', 'color:blue;transform:scale(0)'
]
for n,css in enumerate(HARD_CSS):
    def negative(self, s=css):
        with self.assertRaisesRegex(ValueError,'CSS-concealed'):
            scan('<section style="'+s+'"><p>Fact {{cite:x}}</p></section>')
    setattr(BasicReviewLedger,'test_css_hard_%02d'%n,negative)

NON_NARRATIVE = ['textarea','select','option','datalist']
for n,tag in enumerate(NON_NARRATIVE):
    def negative(self, t=tag):
        with self.assertRaisesRegex(ValueError,'non-narrative'):
            scan('<'+t+'>{{cite:x}}</'+t+'>')
    setattr(BasicReviewLedger,'test_form_%02d'%n,negative)

WARN_CSS = [
    ('font-size:0','font-size-zero'),('font-size:0px','font-size-zero'),
    ('font-size:0em','font-size-zero'),('font-size:0rem','font-size-zero'),
    ('line-height:0','line-height-zero'),('color:transparent','transparent-text'),
    ('clip:rect(0,0,0,0)','css-clipping'),('overflow:hidden','overflow-hidden')
]
for n,(style,flag) in enumerate(WARN_CSS):
    def warning(self, css=style, expected=flag):
        e=scan('<p style="'+css+'">Claim {{cite:x}}</p>')['source_edges'][0]
        self.assertIn(expected,e['review_flags'])
    setattr(BasicReviewLedger,'test_css_review_%02d'%n,warning)

if __name__ == '__main__':unittest.main(verbosity=2)
