"""Synthetic negative-control tests for R175. These do NOT certify real articles."""
from __future__ import annotations
import copy
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r175_link_custody_gate as gate

ROUTES = {
    'sample-guide': '/preparedness/start-here/sample-guide/',
    'next-guide': '/preparedness/start-here/next-guide/',
    'other-guide': '/preparedness/food/other-guide/',
}
RELATED = {'sample-guide': {'title': 'Sample Guide'},
           'next-guide': {'title': 'Next Guide'},
           'other-guide': {'title': 'Other Guide'}}


def fixture():
    meta = {'slug': 'sample-guide', 'status': {'publish': 'draft'},
            'related': ['next-guide', 'other-guide']}
    original = ('<p>Go {{link:next-guide|Next}} or '
                '<a href="https://official.example/page">Official</a>.</p>'
                '<h2 id="note">Note</h2><p><a href="#note">Jump</a>'
                + '{{cite:a}}' * 20 + '</p>')
    citations = ('<sup class="pa-cite"><a href="#src-1" '
                 'aria-label="Source 1: Agency">[1]</a></sup>') * 20
    body = ('<div class="pa-body" id="pa-main"><p>Go '
            '<a href="/preparedness/start-here/next-guide/">Next</a> or '
            '<a href="https://official.example/page">Official</a>.</p>'
            '<h2 id="note">Note</h2><p><a href="#note">Jump</a>'
            + citations + '</p></div>')
    related = ('<aside class="pa-related" aria-labelledby="rel-h">'
               '<h2 id="rel-h">Keep reading</h2><ul>'
               '<li><a href="/preparedness/start-here/next-guide/">Next Guide</a></li>'
               '<li><a href="/preparedness/food/other-guide/">Other Guide</a></li>'
               '</ul></aside>')
    rendered = ('<div class="pa pa-article"><a href="#pa-main">Skip</a>'
                + body + '<section class="pa-sources" aria-labelledby="sources-h">'
                '<h2 id="sources-h">Sources</h2><ol><li id="src-1">Agency</li></ol></section>'
                + related + '</div>')
    return [meta, original, rendered, copy.deepcopy(ROUTES),copy.deepcopy(RELATED)]


class TestR175(unittest.TestCase):
    def check(self, args=None, *, good=True, require_citations=True):
        args = args or fixture()
        if good:
            return gate.audit_one(*args, require_citations=require_citations)
        with self.assertRaises(ValueError):
            gate.audit_one(*args, require_citations=require_citations)

    def test_original_fixture(self):
        receipt = self.check()
        self.assertEqual(receipt['token_links'],1)
        self.assertEqual(receipt['literal_body_links'],2)
        self.assertEqual(receipt['related_links'],2)
        self.assertEqual(receipt['route'],ROUTES['sample-guide'])
        self.assertNotIn('approved', receipt)

    def test_stable_determinism(self):
        args=fixture()
        self.assertEqual(self.check(args),self.check(copy.deepcopy(args)))

    def test_unknown_original_target(self):
        args=fixture();args[1]=args[1].replace('next-guide|Next','unbuilt-guide|Next');self.check(args,good=False)

    def test_missing_original(self):
        args=fixture();args[1]='';self.check(args,good=False)

    def test_missing_render(self):
        args=fixture();args[2]='';self.check(args,good=False)

    def test_published_flag(self):
        args=fixture();args[0]['status']['publish']='published';self.check(args,good=False)

    def test_invalid_slug(self):
        args=fixture();args[0]['slug']='../../../escape';self.check(args,good=False)

    def test_unknown_slug(self):
        args=fixture();args[0]['slug']='not-in-census';self.check(args,good=False)

    def test_duplicate_route(self):
        args=fixture();args[3]['other-guide']=args[3]['next-guide'];self.check(args,good=False)

    def test_non_archive_route(self):
        args=fixture();args[3]['sample-guide']='/other/';self.check(args,good=False)

    def test_protocol_relative_route(self):
        args=fixture();args[3]['other-guide']='//bad/';self.check(args,good=False)

    def test_query_route(self):
        args=fixture();args[3]['other-guide']='/preparedness/food/x/?target=y';self.check(args,good=False)

    def test_no_trailing_slash(self):
        args=fixture();args[3]['other-guide']='/preparedness/food/x';self.check(args,good=False)

    def test_unbuilt_related(self):
        args=fixture();args[0]['related'].append('unknown');self.check(args,good=False)

    def test_duplicate_related(self):
        args=fixture();args[0]['related'].append('next-guide');self.check(args,good=False)

    def test_related_title_drift(self):
        args=fixture();args[2]=args[2].replace('>Other Guide</a>','>Bogus Guide</a>');self.check(args,good=False)

    def test_related_link_missing(self):
        args=fixture();args[2]=args[2].replace('<li><a href="/preparedness/food/other-guide/">Other Guide</a></li>','');self.check(args,good=False)

    def test_related_extra(self):
        args=fixture();args[2]=args[2].replace('</ul></aside>', '<li><a href="/preparedness/food/other-guide/">Other Guide</a></li></ul></aside>');self.check(args,good=False)

    def test_orphan_fragment(self):
        args=fixture();args[2]=args[2].replace('href="#note"','href="#lost"');self.check(args,good=False)

    def test_duplicate_id(self):
        args=fixture();args[2]=args[2].replace('<h2 id="note">','<h2 id="pa-main">');self.check(args,good=False)

    def test_missing_body_scope(self):
        args=fixture();args[2]=args[2].replace('class="pa-body"','class="not-body"');self.check(args,good=False)

    def test_unclosed_body(self):
        args=fixture();args[2]=args[2].replace('</p></div><section','</p><section');self.check(args,good=False)

    def test_uncited_original_rejected(self):
        args=fixture();args[1]=args[1].replace('{{cite:a}}','');self.check(args,good=False)

    def test_uncited_optout_for_isolated_unit(self):
        args=fixture();args[1]=args[1].replace('{{cite:a}}','');self.check(args,good=True,require_citations=False)

    def test_label_html_is_rejected(self):
        args=fixture();args[1]=args[1].replace('next-guide|Next','next-guide|<b>Next</b>');self.check(args,good=False)

    def test_empty_token_label_is_rejected(self):
        args=fixture();args[1]=args[1].replace('next-guide|Next','next-guide| ');self.check(args,good=False)

    def test_unresolved_token(self):
        args=fixture();args[1]+='{{link:badslug|X}}';self.check(args,good=False)

    def test_fails_closed_without_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            with redirect_stdout(StringIO()) as out:
                ret=gate.main(['--repo',tmp,'--check-export'])
            self.assertEqual(ret,2)
            response=json.loads(out.getvalue())
            self.assertEqual(response['state'],'INVALID_HARD_HOLD')
            self.assertIs(response['publication_authorized'],False)


def generate_link_mutation_tests():
    attacks = [
        'http://finalvestige.com/preparedness/start-here/next-guide/',
        'https://finalvestige.com/preparedness/start-here/next-guide/',
        '//finalvestige.com/preparedness/start-here/next-guide/',
        '/preparedness/start-here/next-guide',
        '/preparedness/start-here/NEXT-guide/',
        '/preparedness/start-here/next-guide/?paid=1',
        '/preparedness/start-here/next-guide/#info',
        '/preparedness/start-here/next-guide//',
        '/preparedness/start-here/next-guide/./',
        '/preparedness/start-here/next%2Dguide/',
        '/preparedness/start-here/next%2fguide/',
        '/preparedness/start-here/next-guide/../',
        '/preparedness/start-here/next-guide/?utm_source=fake',
        '/preparedness/start-here/next-guide/?affiliate=1',
        '/preparedness/start-here/next-guide/?checkout=1',
        '/preparedness/start-here/other-guide/',
        '/preparedness/food/other-guide/',
        '/preparedness/',
        '/focus/',
        '/products/',
        '/download/',
        '/preparedness/start-here/next-guide/?source=ad',
        'javascript:alert(1)',
        'data:text/html,unsafe',
        'https://evil.example/checkout',
        'https://finalvestige.com.evil.example/',
        'http://127.0.0.1/next-guide',
        'https://xn--finalvestige-z9a.com/next-guide',
        'mailto:ads@merchant.example',
        'tel:+10000000000',
        '#src-1',
        '#note',
        '#pa-main',
        '/preparedness/start-here/next-guide/?ref=partner',
        '/preparedness/start-here/next-guide/#src-1',
        '/preparedness/start-here/next-guide/?foo=%2F',
        '/preparedness/start-here/next-guide/%2e%2e/',
        '/preparedness/start-here/next-guide/?verified=true',
        '/preparedness/start-here/next-guide/?safe=true',
        '/preparedness/start-here/next-guide/?published=1',
        '/preparedness/start-here/next-guide/?coupon=now',
        '/preparedness/start-here/next-guide/?discount=60',
        '/preparedness/start-here/next-guide/?clickid=123',
        '/preparedness/start-here/next-guide/?utm_content=unverified',
        '/preparedness/start-here/next-guide/?product=imagined',
        '/preparedness/start-here/next-guide/?source=paid',
        '/preparedness/start-here/next-guide/?campaign=unapproved',
        '/preparedness/start-here/next-guide/?affiliate=hidden',
        '/preparedness/start-here/next-guide/?source=unknown',
        '/preparedness/start-here/next-guide/?ref=promo',
    ]
    assert len(set(attacks)) == len(attacks)
    for i, target in enumerate(attacks,1):
        def test(self, target=target):
            args=fixture();args[2]=args[2].replace(
                '<a href="/preparedness/start-here/next-guide/">Next</a>',
                '<a href="'+target+'">Next</a>',1)
            self.check(args,good=False)
        setattr(TestR175,f'test_injected_route_mutation_{i:02d}',test)


generate_link_mutation_tests()

if __name__=='__main__':
    unittest.main()
