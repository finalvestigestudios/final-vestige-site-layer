"""R14 deterministic synthetic/adversarial tests. No real link or safety checks."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

FILE = Path(__file__).with_name('outbound_link_custody.py')
spec = importlib.util.spec_from_file_location('outbound_link_custody', FILE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

ARTICLE = ('<h2 id="overview">Overview</h2>'
           '<p>Read the <a href="https://official.test/rules">source reference</a> and the '
           '<a href="https://outside.test/new">untracked guidance</a>.</p>'
           '<p><a href="#overview">Jump to the overview</a></p>')

class DummyLib:
    def __init__(self, article=ARTICLE, status='draft', n=1):
        self.articles = {}
        self.source = {'url': 'https://official.test/rules'}
        for idx in range(n):
            slug = 'guide' if n == 1 else f'guide-{idx:02d}'
            self.articles[slug] = {'slug': slug, 'status': {'publish': status},
                                   '_body': article, 'source_use': {'first': 'Specific page read'}}
    def source_for(self, meta, sid):
        if sid != 'first':
            raise KeyError(sid)
        return self.source

class DummyRenderer:
    def __init__(self, *, transform=lambda x: x, order=('first',)):
        self.transform = transform
        self.order = list(order)
    def resolve_tokens(self, lib, meta):
        return meta['_body'], self.order
    def build_article(self, lib, slug):
        meta = lib.articles[slug]
        inner = ('<div><div id="pa-main">' + self.transform(meta['_body']) +
                 '</div><section class="pa-sources"><li id="src-1">citation</li></section></div>')
        return {'meta': meta, 'slug': slug, 'sources': self.order, 'inner': inner}


class GateTests(unittest.TestCase):
    def setUp(self):
        self.lib = DummyLib()
        self.r = DummyRenderer()

    def test_good_report_remains_hold(self):
        r = gate.audit_article(self.lib, self.r, 'guide')
        self.assertEqual(r['reader_links'], 3)
        self.assertEqual(r['outbound_links'], 2)
        self.assertEqual(r['outbound_not_in_article_source_register'], 1)
        self.assertTrue(all(x['status'].startswith('PENDING_HUMAN') for x in r['outgoing']))

    def test_source_match_is_url_exact_not_host_match(self):
        self.lib.source['url'] = 'https://official.test/other'
        r = gate.audit_article(self.lib, self.r, 'guide')
        self.assertEqual(r['outbound_not_in_article_source_register'], 2)

    def test_repeatability(self):
        self.assertEqual(gate.audit_corpus(self.lib,self.r,expected_items=1),
                         gate.audit_corpus(self.lib,self.r,expected_items=1))

    def test_empty_queue_is_not_approval(self):
        self.lib.articles['guide']['_body'] = '<p>No embedded hyperlinks.</p>'
        r = gate.audit_corpus(self.lib,self.r,expected_items=1)
        self.assertEqual(r['outbound_links'], 0)
        self.assertFalse(r['may_publish'])
        self.assertFalse(r['advice_safety_verified'])
        self.assertEqual(r['human_link_checks_verified'], 0)

    def test_frozen_count_guard(self):
        with self.assertRaises(gate.LinkCustodyFailure): gate.audit_corpus(self.lib,self.r)

    def test_frozen_complete_collection(self):
        self.lib = DummyLib(n=36)
        r = gate.audit_corpus(self.lib, self.r)
        self.assertEqual(r['items'], 36)
        self.assertEqual(r['outbound_links'], 72)
        self.assertEqual(r['outbound_not_in_article_source_register'], 36)

    def test_source_body_fingerprint_changes(self):
        before = gate.audit_article(self.lib,self.r,'guide')
        self.lib.articles['guide']['_body'] += '<p>Another paragraph.</p>'
        after = gate.audit_article(self.lib,self.r,'guide')
        self.assertNotEqual(before['body_sha256'],after['body_sha256'])

    def test_tampered_target_rejected(self):
        r = DummyRenderer(transform=lambda s:s.replace('official.test','hijack.test'))
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,r,'guide')

    def test_tampered_label_rejected(self):
        r = DummyRenderer(transform=lambda s:s.replace('source reference','false description'))
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,r,'guide')

    def test_tampered_rel_rejected(self):
        self.lib.articles['guide']['_body']='<p><a href="https://outside.test" rel="noopener">Read</a></p>'
        r = DummyRenderer(transform=lambda s:s.replace('noopener','nofollow'))
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,r,'guide')

    def test_added_link_rejected(self):
        r=DummyRenderer(transform=lambda s:s+'<a href="https://new.test">new</a>')
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,r,'guide')

    def test_dropped_link_rejected(self):
        r=DummyRenderer(transform=lambda s:s.replace('<a href="https://outside.test/new">untracked guidance</a>','untracked guidance'))
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,r,'guide')

    def test_reordered_links_rejected(self):
        r=DummyRenderer(transform=lambda s:s.replace('https://official.test/rules','https://temp.test').replace('https://outside.test/new','https://official.test/rules').replace('https://temp.test','https://outside.test/new'))
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,r,'guide')

    def test_changed_rendered_slug_rejected(self):
        class Wrong(DummyRenderer):
            def build_article(self,lib,slug):
                r=super().build_article(lib,slug);r['slug']='wrong';return r
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,Wrong(),'guide')

    def test_changed_rendered_source_order_rejected(self):
        class Wrong(DummyRenderer):
            def build_article(self,lib,slug):
                r=super().build_article(lib,slug);r['sources']=[];return r
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,Wrong(),'guide')

    def test_changed_rendered_article_identity_rejected(self):
        class Wrong(DummyRenderer):
            def build_article(self,lib,slug):
                r=super().build_article(lib,slug);r['meta']=copy.deepcopy(r['meta']);return r
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,Wrong(),'guide')

    def test_status_published_rejected(self):
        self.lib.articles['guide']['status']['publish']='published'
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,self.r,'guide')

    def test_unknown_article_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.audit_article(self.lib,self.r,'missing')

    def test_unresolved_source_rejected(self):
        self.r.order=['unknown']
        with self.assertRaises(KeyError):gate.audit_article(self.lib,self.r,'guide')

    def test_duplicate_main_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<div id="pa-main"></div><div id="pa-main"></div>',main_only=True)

    def test_missing_main_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<p>None</p>',main_only=True)

    def test_duplicate_id_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<p id="a">One</p><p id="a">Two</p>')

    def test_fragment_valid(self):
        p=gate.parse_links('<h2 id="context">There</h2><p><a href="#context">Jump</a></p>')
        self.assertEqual(p.links[0]['kind'],'LOCAL_FRAGMENT')

    def test_fragment_missing_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<p><a href="#absent">Jump</a></p>')

    def test_citation_source_footnote_is_outside_body(self):
        p=gate.parse_links('<p><sup class="pa-cite"><a href="#src-1">[1]</a></sup></p>')
        self.assertEqual(p.links[0]['kind'],'LOCAL_FRAGMENT')

    def test_image_alt_is_accessible_label(self):
        p=gate.parse_links('<p><a href="https://docs.test"><img alt="download docs" src="/doc.png"></a></p>')
        self.assertEqual(p.links[0]['label'],'download docs')

    def test_aria_label_is_accessible_label(self):
        p=gate.parse_links('<p><a aria-label="review this" href="https://docs.test"><span></span></a></p>')
        self.assertEqual(p.links[0]['aria_label'],'review this')

    def test_empty_label_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<p><a href="https://docs.test"></a></p>')

    def test_nested_links_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<a href="#foo">One<a href="#bar">Two</a></a>')

    def test_duplicate_attribute_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<a href="/a" href="/b">A</a>')

    def test_malformed_nesting_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<p><a href="/a">A</p></a>')

    def test_truncated_markup_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<p><a href="/a">A')

    def test_no_hrefs_hidden_in_script_are_recorded(self):
        p=gate.parse_links('<script>var x="<a href=\\\"https://evil.test\\\">";</script><p>Text</p>')
        self.assertEqual(p.links, [])

    def test_unmatched_html_comment_not_recorded(self):
        p=gate.parse_links('<!-- <a href="https://evil.test">evil</a> --><p>Text</p>')
        self.assertEqual(p.links, [])

    def test_http_is_review_not_approval(self):
        self.assertEqual(gate.classify_destination('http://archive.test/history')[0], 'EXTERNAL_HTTP_REVIEW')

    def test_external_lookalike_host(self):
        self.assertEqual(gate.classify_destination('https://finalvestige.com.evil.test/')[0], 'EXTERNAL_HTTPS')

    def test_origin_absolute_not_safety_clearance(self):
        self.assertEqual(gate.classify_destination('https://finalvestige.com/focus/')[0], 'SITE_ABSOLUTE')

    def test_human_review_state_cannot_be_passed(self):
        r=gate.audit_corpus(self.lib,self.r,expected_items=1)
        self.assertNotIn('approved', gate.canonical_json(r).lower())

    def test_export_report_fingerprint_changes_with_content(self):
        one=gate.audit_corpus(self.lib,self.r,expected_items=1)
        self.lib.articles['guide']['_body'] += '<p>New.</p>'
        two=gate.audit_corpus(self.lib,self.r,expected_items=1)
        self.assertNotEqual(one['report_sha256'],two['report_sha256'])

    def test_oversized_html_rejected(self):
        with patch.object(gate,'MAX_HTML_BYTES',200):
            with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<p>' + 'x'*201 + '</p>')

    def test_excess_anchors_rejected(self):
        with patch.object(gate,'MAX_ANCHORS',1):
            with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links(ARTICLE)

    def test_protocol_inside_blank_target_rejected(self):
        with self.assertRaises(gate.LinkCustodyFailure):gate.parse_links('<p><a href="https://outside.test" target="_blank">Read</a></p>')

    def test_blank_target_with_noopener_accepted(self):
        p=gate.parse_links('<p><a href="https://outside.test" target="_blank" rel="noopener">Read</a></p>')
        self.assertEqual(p.links[0]['target'],'_blank')

    def test_formula_like_link_text_is_data(self):
        p=gate.parse_links('<p><a href="https://a.test">=1+1</a></p>')
        self.assertEqual(p.links[0]['label'],'=1+1')


INVALID_HREFS = [
    '', ' ', '\nhttps://valid.test', 'https://valid.test\n',
    'javascript:alert(1)', 'data:text/html,payload', 'ftp://files.test',
    'file:///etc/passwd', '//bad.test', 'mailto:person@example.test',
    'tel:5551212', '/../../admin', '/preparedness/../../admin', '/a/%2fadmin',
    '/a/?token=x', '/a/<script>', '#', '#x y', '#1bad',
    'https://user:pass@official.test/path', 'https://official.test@evil.test/path',
    'https://evil.test\\@official.test', 'https://evil.test/%00',
    'https://fóó.test/path', 'https://evil.test\u200b/path',
    'https://example.test/\t', 'https://example.test:99999',
    'https://example.test:abc', 'https://', 'https:wrong.example',
    'https://exa%6dple.test', 'HTTPS://example.test',
    'https://example.test/&#x6a;avascript:',
    'https://example.test/?x=&amp;amp;y=1',
    'http://127.0.0.1\r', '\x00',
    '/preparedness/a/?e=<svg>', '/a#bad%20id',
]

for i, href in enumerate(INVALID_HREFS):
    def make_test(value):
        def test(self):
            with self.assertRaises((gate.LinkCustodyFailure, ValueError)):
                gate.classify_destination(value)
        return test
    setattr(GateTests, f'test_invalid_href_{i:02d}', make_test(href))

VALID_HREFS = [
    ('https://example.test/a?b=1&c=2','EXTERNAL_HTTPS'),
    ('http://old-archives.test/','EXTERNAL_HTTP_REVIEW'),
    ('https://finalvestige.com/preparedness/start-here/','SITE_ABSOLUTE'),
    ('/preparedness/water/','ARCHIVE_INTERNAL'),
    ('/focus/','SITE_INTERNAL'),
    ('#footnotes','LOCAL_FRAGMENT'),
]
for i, (href, kind) in enumerate(VALID_HREFS):
    def make_test(h, expected):
        def test(self):
            self.assertEqual(gate.classify_destination(h)[0],expected)
        return test
    setattr(GateTests, f'test_valid_href_{i:02d}', make_test(href,kind))

if __name__ == '__main__':
    unittest.main(verbosity=2)
