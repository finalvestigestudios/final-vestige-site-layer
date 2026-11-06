"""R174 synthetic/adversarial provenance tests; passing tests NEVER equal safety/QD."""
from __future__ import annotations
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import copy
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r174_rendered_citation_gate as g


def fixture():
    meta = {'slug': 'sample-article', 'status': {'publish': 'draft'},
            'source_use': {'a': 'First verified reading scope pending.',
                           'b': 'Second independently read source pending.'}}
    sources = {'a': {'title': 'Source A', 'url': 'https://agency.example/a',
                     'human_link_check': False, '_shared_pending': True},
               'b': {'title': 'Source B', 'url': 'https://museum.example/b',
                     'human_link_check': False, '_shared_pending': False}}
    order = ['a', 'b']
    marks = ['a', 'b'] * 10
    body = '<p>' + ' '.join('{{cite:' + sid + '}}' for sid in marks) + '</p>'
    links = ''.join('<sup class="pa-cite"><a href="#src-{n}" aria-label="Source {n}: {title}">[{n}]</a></sup>'.format(
        n=order.index(sid) + 1, title=sources[sid]['title']) for sid in marks)
    srcs = []
    for n, sid in enumerate(order, 1):
        s = sources[sid]
        scope = '<span>Shared-source reading scope: independent review pending</span>' if s['_shared_pending'] else ''
        srcs.append('<li id="src-{n}"><a href="{url}" rel="noopener">{title}</a>. '
                    '<span>Human source-link check pending</span><span>Used for: {note}</span>{scope}</li>'.format(
            n=n,url=s['url'],title=s['title'],note=meta['source_use'][sid],scope=scope))
    inner = '<div class="pa-body" id="pa-main">' + links + '</div>' + \
            '<section class="pa-sources">' + ''.join(srcs) + '</section>Draft: not public'
    return meta, body, inner, order, sources


class TestR174(unittest.TestCase):
    def valid(self, *args, strict=True):
        return g.audit_one(*args, strict=strict)

    def bad(self, *args, strict=True):
        with self.assertRaises(ValueError):
            self.valid(*args, strict=strict)

    def test_synthetic_hold_does_not_certify(self):
        args = fixture()
        report = self.valid(*args)
        self.assertEqual(report['citations'], 20)
        self.assertEqual(report['source_uses'], 2)
        self.assertNotIn('approval', report)

    def test_deterministic_receipt(self):
        args=fixture()
        self.assertEqual(self.valid(*args), self.valid(*copy.deepcopy(args)))

    def test_missing_source_explanation(self):
        args=list(fixture());args[0]['source_use'].pop('a');self.bad(*args)

    def test_extra_unreferenced_source_explanation(self):
        args=list(fixture());args[0]['source_use']['c']='Unreferenced interpretation.';self.bad(*args)

    def test_published_metadata(self):
        args=list(fixture());args[0]['status']['publish']='published';self.bad(*args)

    def test_invalid_slug(self):
        args=list(fixture());args[0]['slug']='../../invalid';self.bad(*args)

    def test_wrong_citation_order(self):
        args=list(fixture());args[3]=['b','a'];self.bad(*args)

    def test_missing_cited_source(self):
        args=list(fixture());args[4].pop('b');self.bad(*args)

    def test_malformed_reference_sup(self):
        args=list(fixture());args[2]=args[2].replace('<sup class="pa-cite">','<sup>',1);self.bad(*args)

    def test_missing_one_in_text_citation(self):
        args=list(fixture());args[2]=args[2].replace('</sup>','</broken>',1);self.bad(*args)

    def test_extra_body_marker(self):
        args=list(fixture());args[1]+='{{cite:b}}';self.bad(*args)

    def test_dropped_body_marker(self):
        args=list(fixture());args[1]=args[1].replace('{{cite:a}}','',1);self.bad(*args)

    def test_wrong_aria_label_number(self):
        args=list(fixture());args[2]=args[2].replace('aria-label="Source 1:', 'aria-label="Source 7:',1);self.bad(*args)

    def test_wrong_reference_href(self):
        args=list(fixture());args[2]=args[2].replace('href="#src-1"','href="#src-77"',1);self.bad(*args)

    def test_wrong_sup_display_number(self):
        args=list(fixture());args[2]=args[2].replace('>[1]</a>','>[77]</a>',1);self.bad(*args)

    def test_wrong_sup_title(self):
        args=list(fixture());args[2]=args[2].replace('Source 1: Source A','Source 1: Source B',1);self.bad(*args)

    def test_duplicate_source_list_item(self):
        args=list(fixture());args[2]=args[2].replace('<li id="src-2">','<li id="src-1">');self.bad(*args)

    def test_missing_source_item(self):
        args=list(fixture());args[2]=args[2].replace('<li id="src-2">','<li>');self.bad(*args)

    def test_wrong_source_title(self):
        args=list(fixture());args[2]=args[2].replace('>Source B</a>.','>Bad Title</a>.');self.bad(*args)

    def test_missing_article_use_description(self):
        args=list(fixture());args[2]=args[2].replace('Used for: First verified reading scope pending.','Used for: unknown');self.bad(*args)

    def test_false_human_link_complete(self):
        args=list(fixture());args[2]=args[2].replace('Human source-link check pending','Human source-link check complete',1);self.bad(*args)

    def test_source_object_falsely_verified(self):
        args=list(fixture());args[4]['b']['human_link_check']=True;self.bad(*args)

    def test_missing_shared_scope_warning(self):
        args=list(fixture());args[2]=args[2].replace('Shared-source reading scope: independent review pending','citation approved');self.bad(*args)

    def test_missing_draft_label(self):
        args=list(fixture());args[2]=args[2].replace('Draft: not public','Published');self.bad(*args)

    def test_missing_source_section(self):
        args=list(fixture());args[2]=args[2].replace('class="pa-sources"','class="other"');self.bad(*args)

    def test_missing_body_section(self):
        args=list(fixture());args[2]=args[2].replace('class="pa-body"','class="other"');self.bad(*args)

    def test_unresolved_citation(self):
        args=list(fixture());args[2]+='{{cite:a}}';self.bad(*args)

    def test_unresolved_article_link(self):
        args=list(fixture());args[2]+='{{link:b|click}}';self.bad(*args)

    def test_empty_original_fails(self):
        args=list(fixture());args[1]='';self.bad(*args)

    def test_minimum_citations_strict(self):
        args=list(fixture());args[1]='{{cite:a}}{{cite:b}}';self.bad(*args)

    def test_missing_checkout_hard_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            with redirect_stdout(StringIO()) as out:
                ret=g.main(['--repo',td,'--check-export'])
            self.assertEqual(ret,2)
            payload=json.loads(out.getvalue())
            self.assertEqual(payload['state'],'INVALID_HARD_HOLD')
            self.assertIs(payload['publication_authorized'],False)


def add_url_mutations():
    # 40 intentional URL distortions: the published source link must be the
    # literal article-scoped source URI, not a redirect, lookalike or shortcut.
    tampering = [
        'http://agency.example/a','https://agency.example/a/','https://agency.example/A',
        'https://agency.example/a?ref=affiliate','https://agency.example/a#fragment',
        'https://agency.example:444/a','https://agency.example/b',
        'https://agency.example/a?x=1','https://agency.example/a?x=2',
        'https://agency.example/a&x=1','https://agency.example/a%2F',
        'https://agеncy.example/a','https://fake-agency.example/a',
        'https://agency-example.com/a','https://agency.example.evil/a',
        'https://user@agency.example/a','https://agency.example/a/',
        'https://agency.example/a//','https://agency.example/./a',
        'https://agency.example/%61','https://agency.example/a?utm_source=x',
        '//agency.example/a','/a','https://agency.example',
        'https://agency.example/a?verified=true','https://agency.example/a?unsafe',
        'https://agency.example/a?route=wrong','https://museum.example/a',
        'https://agency.example/a?source=nchfp','https://agency.example/a#src',
        'https://agency.example/a?redirect=1','https://agency.example/a?x=3',
        'https://agency.example/a?x=4','https://agency.example/a?x=5',
        'https://agency.example/a?x=6','https://agency.example/a?x=7',
        'https://agency.example/a?x=8','https://agency.example/a?x=9',
        'https://agency.example/a?x=10','https://agency.example/a?x=11',
    ]
    for index, url in enumerate(tampering):
        def test(self, url=url):
            args=list(fixture())
            args[2]=args[2].replace('href="https://agency.example/a"',
                                    'href="' + url + '"', 1)
            self.bad(*args)
        setattr(TestR174,'test_url_tamper_%02d'%index,test)
add_url_mutations()

if __name__ == '__main__':
    unittest.main()
