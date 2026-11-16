"""R405 exact-code synthetic-only citation custody tests; never scientific clearance."""
from __future__ import annotations
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
import unittest

SPEC = spec_from_file_location('r405_exact', Path(__file__).resolve().parents[1] / 'tools' / 'r405_editorial_lineage_citation_gate.py')
g = module_from_spec(SPEC)
SPEC.loader.exec_module(g)


def article(extra='', refs=None):
    urls = sorted(g.SOURCE_URLS if refs is None else refs)
    return ('<article id="main"><style>.diagram {display:grid}</style><h1>Unpublished research</h1>'
            + ''.join('<a href="' + url + '">Primary record</a>' for url in urls)
            + '<a href="#main">jump</a>' + extra + '</article>').encode('utf-8')


def fixture():
    html = article()
    out = BytesIO()
    with ZipFile(out, 'w', ZIP_DEFLATED) as z:
        z.writestr('E395_ARTICLE11_SOURCE_SCOPE_WORDPRESS_HARD_HOLD.html', html)
    archive = out.getvalue()
    versions = {v: html for v in ('E395', 'E397', 'E398')}
    hashes = {'E395_ZIP': g.sha256(archive), **{v + '_HTML': g.sha256(html) for v in versions}}
    return archive, versions, hashes


class Custody(unittest.TestCase):
    def test_synthetic_bundle_structural_pass_never_release(self):
        zip_data, pages, hashes = fixture()
        r = g.inspect_bundle(zip_data, pages, receipts=hashes)
        self.assertEqual(r['integrity'], 'PASS')
        self.assertIs(r['eligible'], False)
        self.assertIs(r['publication_approved'], False)
        self.assertIs(r['source_safety_approved'], False)
        self.assertEqual(r['release'], 'DRAFT_HARD_HOLD')
        self.assertIsNone(r['lineage']['variant_selected'])

    def test_no_original_zip_refused(self):
        _, pages, hashes = fixture()
        r = g.inspect_bundle(None, pages, receipts=hashes)
        self.assertEqual(r['integrity'], 'FAIL')
        self.assertIn('zip:missing_original_zip_or_html', r['failures'])

    def test_archive_byte_mutation_refused(self):
        zip_data, pages, hashes = fixture()
        r = g.inspect_bundle(zip_data + b'junk', pages, receipts=hashes)
        self.assertEqual(r['integrity'], 'FAIL')

    def test_same_named_article_different_bytes_refused(self):
        zip_data, pages, hashes = fixture()
        pages['E395'] += b'<!--drift-->'
        hashes['E395_HTML'] = g.sha256(pages['E395'])
        r = g.inspect_bundle(zip_data, pages, receipts=hashes)
        self.assertIn('zip:r404:article_sha256_mismatch', r['failures'])

    def test_default_receipts_reject_synthetic_bytes(self):
        zip_data, pages, _ = fixture()
        self.assertEqual(g.inspect_bundle(zip_data, pages)['integrity'], 'FAIL')

    def test_missing_derivative_refused(self):
        zip_data, pages, hashes = fixture()
        pages['E398'] = None
        self.assertEqual(g.inspect_bundle(zip_data, pages, receipts=hashes)['integrity'], 'FAIL')

    def test_additional_derivative_cannot_be_automatically_selected(self):
        zip_data, pages, hashes = fixture()
        pages['E399'] = article()
        self.assertEqual(g.inspect_bundle(zip_data, pages, receipts=hashes)['integrity'], 'FAIL')

    def test_original_four_source_scope_loss_refused(self):
        url = sorted(g.SOURCE_URLS)[0]
        raw = article(refs=g.SOURCE_URLS - {url})
        result = g.scan_html(raw, g.sha256(raw))
        self.assertIn('four_source_links_unproven', result['failures'])
        self.assertIn(url, result['source_scope_missing'])

    def test_derivative_citation_loss_reported(self):
        _, pages, hashes = fixture()
        url = sorted(g.SOURCE_URLS)[0]
        pages['E397'] = article(refs=g.SOURCE_URLS - {url})
        hashes['E397_HTML'] = g.sha256(pages['E397'])
        result = g.inspect(pages, receipts=hashes)
        self.assertIn(url, result['citation_changes']['E395_to_E397']['removed'])
        self.assertIn('derivative_removed_citation_requires_review', result['failures'])

    def test_added_citation_records_change_but_no_safety_claim(self):
        _, pages, hashes = fixture()
        pages['E398'] = article('<a href="https://www.fda.gov/food">FDA</a>')
        hashes['E398_HTML'] = g.sha256(pages['E398'])
        result = g.inspect(pages, receipts=hashes)
        self.assertIn('https://www.fda.gov/food', result['citation_changes']['E397_to_E398']['added'])
        self.assertFalse(result['scientific_safety_approved'])

    def test_unicode_invalid_utf8_refused(self):
        html = article() + b'\xff'
        self.assertIn('invalid_html_input', g.scan_html(html, g.sha256(html))['failures'])

    def test_release_even_no_input_exit_two(self):
        from unittest.mock import patch
        with patch('builtins.print'):
            self.assertEqual(g.main([]), 2)

    def test_receipt_schema_cannot_expand(self):
        _, pages, hashes = fixture()
        hashes['qualified_approval'] = 'f'*64
        self.assertIn('receipt_inventory_invalid', g.inspect(pages, receipts=hashes)['failures'])


BAD_HTML = {
    'script': '<script>alert(1)</script>', 'iframe': '<iframe src="https://example.org"></iframe>',
    'object': '<object data="x"></object>', 'embed': '<embed src="x">',
    'form': '<form action="/contact"></form>', 'input': '<input name="child">',
    'textarea': '<textarea></textarea>', 'button': '<button>Pay</button>',
    'select': '<select></select>', 'video': '<video></video>', 'audio': '<audio></audio>',
    'canvas': '<canvas></canvas>', 'applet': '<applet></applet>',
    'base': '<base href="https://example.org">', 'svg': '<svg></svg>',
    'math': '<math><mi>u</mi></math>', 'link': '<link rel="stylesheet" href="https://example.org">',
    'onclick': '<p onclick="evil()">text</p>', 'onload': '<p onload="evil()">text</p>',
    'onerror': '<img onerror="evil()">', 'srcdoc': '<div srcdoc="a"></div>',
    'contenteditable': '<p contenteditable="true">hi</p>',
    'javascript': '<a href="javascript:evil()">source</a>',
    'data_uri': '<a href="data:text/html,a">source</a>',
    'http': '<a href="http://example.org">source</a>',
    'ftp': '<a href="ftp://example.org">source</a>',
    'protocol_relative': '<a href="//example.org">source</a>',
    'remote_image': '<img src="https://example.org/track.png">',
    'local_image': '<img src="picture.jpg">',
    'srcset': '<img srcset="https://example.org/track.png">',
    'ping': '<a href="#main" ping="https://example.org">hello</a>',
    'background': '<body background="https://example.org/track.png"></body>',
    'style_import': '<style>@import "https://example.org/p.css";</style>',
    'css_url': '<style>div{background:url(https://example.org/p)}</style>',
    'style_url': '<p style="background:url(/internal.png)">p</p>',
    'duplicate_id': '<p id="main">again</p>',
    'empty_id': '<p id="">empty</p>',
    'duplicate_attr': '<a href="https://example.org" href="https://evil.org">dup</a>',
    'missing_fragment': '<a href="#missing">broken anchor</a>',
    'mailto': '<a href="mailto:x@example.org">address</a>',
    'blank_href': '<a href="">blank</a>',
    'userinfo': '<a href="https://foo:bar@example.org">auth</a>',
    'backslash': '<a href="https://example.org\\evil">ambiguous</a>',
    'meta_refresh': '<meta http-equiv="refresh" content="0;url=https://example.org">',
    'unclosed_style': '<style>p{display:grid}',
}


def make_case(fragment):
    def verify(self):
        raw = article(fragment)
        result = g.scan_html(raw, g.sha256(raw))
        self.assertEqual(result['integrity'], 'FAIL', fragment)
        self.assertTrue(result['failures'])
    return verify


for name, html in BAD_HTML.items():
    setattr(Custody, 'test_reject_' + name, make_case(html))


if __name__ == '__main__':
    unittest.main()
