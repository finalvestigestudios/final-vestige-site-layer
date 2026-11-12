"""R309 standalone tests: real R305 Git blob, HTML raw-fragment-first fallback.

Synthetic in-memory markup only. No source, CMS, network, or build writes.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'r305_html5_link_target_review_hold.py'
spec = importlib.util.spec_from_file_location('fv_r309_raw_fragment_parser', MODULE)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def check(fragment, ids, *, mode='source'):
    html = ''.join(f'<div id="{identifier}"></div>' for identifier in ids)
    html += f'<a href="#{fragment}">Details</a>'
    return parser.scan(html, mode)


class FragmentPriority(unittest.TestCase):
    def test_missing_unencoded_target_rejected(self):
        problems, diagnostic = check('missing', ['existing'])
        self.assertIn('MISSING_SAME_DOCUMENT_TARGET:missing', problems)
        self.assertEqual(diagnostic['resolved_fragment_ids'], [])

    def test_html_entity_decoded_before_fragment_processing(self):
        problems, diagnostic = check('room&amp;board', ['room&board'])
        self.assertEqual(problems, [])
        self.assertEqual(diagnostic['resolved_fragment_ids'], ['room&board'])

    def test_fragment_resolution_is_source_and_export_consistent(self):
        for mode in ('source','export'):
            with self.subTest(mode=mode):
                problems, diag = check('room%2Dplan',['room%2Dplan','room-plan'],mode=mode)
                self.assertEqual(problems, [])
                self.assertEqual(diag['resolved_fragment_ids'], ['room%2Dplan'])

    def test_multiple_anchor_order_is_preserved(self):
        html = '<h2 id="raw%2Dfirst">Raw</h2><h2 id="raw-first">Decoded</h2>'
        html += '<a href="#raw%2Dfirst">A</a><a href="#raw-first">B</a>'
        problems, diag = parser.scan(html,'source')
        self.assertEqual(problems, [])
        self.assertEqual(diag['resolved_fragment_ids'], ['raw%2Dfirst','raw-first'])

    def test_duplicate_ids_remain_rejected(self):
        problems, _ = parser.scan('<div id="x"></div><p id="x"></p><a href="#x">x</a>','source')
        self.assertIn('DUPLICATE_HTML_ID:x',problems)

    def test_javascript_remains_rejected(self):
        problems, _ = parser.scan('<a href="javascript:alert(1)">Bad</a>','source')
        self.assertTrue(any('UNAPPROVED_URL_SCHEME' in problem for problem in problems))

    def test_no_unsafe_approval_property(self):
        problems, diagnostic = check('a%2Db',['a%2Db','a-b'])
        self.assertEqual(problems,[])
        self.assertNotIn('publication_authorized',diagnostic)


# Distinct percent encodings, including accented, non-Latin and literal percent IDs.
CASES = (
    ('water%2Dsafety','water-safety'),
    ('family%2Dcontact','family-contact'),
    ('evacuation%2Droute','evacuation-route'),
    ('emergency%2Fcard','emergency/card'),
    ('caf%C3%A9','café'),
    ('%E6%B0%B4','水'),
    ('phone%2Btext','phone+text'),
    ('A%2EB','A.B'),
    ('zero%30','zero0'),
    ('foo%25bar','foo%bar'),
    ('%C2%A9','©'),
    ('plan%5F2026','plan_2026'),
    ('section%3Aplan','section:plan'),
    ('home%2Ekit','home.kit'),
    ('head%7Eone','head~one'),
)

for index,(raw,decoded) in enumerate(CASES):
    def literal(self,raw=raw):
        problems,diag=check(raw,[raw])
        self.assertEqual(problems,[])
        self.assertEqual(diag['resolved_fragment_ids'],[raw])
    def decoded_only(self,raw=raw,decoded=decoded):
        problems,diag=check(raw,[decoded])
        self.assertEqual(problems,[])
        self.assertEqual(diag['resolved_fragment_ids'],[decoded])
    def dual(self,raw=raw,decoded=decoded):
        problems,diag=check(raw,[decoded,raw])
        self.assertEqual(problems,[])
        self.assertEqual(diag['resolved_fragment_ids'],[raw])
    def missing(self,raw=raw,decoded=decoded):
        problems,diag=check(raw,['absent-target'])
        self.assertIn('MISSING_SAME_DOCUMENT_TARGET:'+decoded,problems)
        self.assertEqual(diag['resolved_fragment_ids'],[])
    setattr(FragmentPriority,f'test_literal_{index:02d}',literal)
    setattr(FragmentPriority,f'test_decoded_fallback_{index:02d}',decoded_only)
    setattr(FragmentPriority,f'test_literal_priority_{index:02d}',dual)
    setattr(FragmentPriority,f'test_missing_{index:02d}',missing)

BAD = ('bad%','bad%2','bad%xy','bad%zz','%FF','%C3%28','%E0%A4%A',
       '%00','%0A','%0D','%1F','%7F','control%0Aline','%ED%A0%80','%C0%AF')
for index,bad in enumerate(BAD):
    def denied(self,bad=bad):
        problems,diag=check(bad,[bad])
        self.assertTrue(any(p.startswith(('INVALID_PERCENT_ENCODED_FRAGMENT',
                                          'INVALID_UTF8_FRAGMENT','UNSAFE_DECODED_FRAGMENT'))
                            for p in problems),(bad,problems))
        self.assertEqual(diag['resolved_fragment_ids'],[])
    setattr(FragmentPriority,f'test_invalid_encoding_{index:02d}',denied)

if __name__ == '__main__':
    unittest.main()
