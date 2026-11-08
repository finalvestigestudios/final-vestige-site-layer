"""Standalone negative regression tests against a synthetic Article/Tool draft."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'tools' / 'r226_export_browser_custody.py'
SPEC = importlib.util.spec_from_file_location('r226', PATH)
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)

BODY = '<h2 id="intro">Start</h2><p>Do this <sup class="pa-cite"><a href="#src-1">[1]</a></sup></p>'
SOURCE = ('<section class="pa-sources"><h2 id="sources-h">Sources and verification</h2>'
          '<ol><li id="src-1"><a href="https://ready.gov/plan">Ready.gov</a>'
          '<span>Reading scope: household plan</span></li></ol></section>')
REVIEW = ('<section class="pa-review"><h2 id="review-h">Review record</h2>'
          '<p>Safety/source and independent review still pending.</p></section>')
WARNING = '<p>Independent safety/source and QD verification pending</p>'
PAGE = '<main><div class="pa pa-article">' + WARNING + '<div class="pa-body" id="pa-main">' + BODY + '</div>' + SOURCE + REVIEW + '</div></main>'

class Library:
    def source_for(self, meta, sid):
        return {'url': 'https://ready.gov/plan'}


def check(page=PAGE, body=BODY):
    return G.verify_export(page, ['ready-plan'], {}, Library(), body)


class BrowserSemantics(unittest.TestCase):
    def test_baseline_hold(self):
        self.assertEqual(check()['state'], 'DRAFT_HARD_HOLD')

    def test_empty_bibliography_allowed_when_no_citations(self):
        self.assertEqual(G.verify_export(PAGE.replace('<sup class="pa-cite"><a href="#src-1">[1]</a></sup>', '').replace('<li id="src-1"><a href="https://ready.gov/plan">Ready.gov</a><span>Reading scope: household plan</span></li>', ''), [], {}, Library(), '' )['source_targets'], 0)

    def test_missing_disclosure(self):
        self.assertRaises(ValueError, check, PAGE.replace(WARNING, ''))

    def test_hidden_review(self):
        self.assertRaises(ValueError, check, PAGE.replace('class="pa-review"', 'class="pa-review" hidden'))

    def test_missing_source_link(self):
        self.assertRaises(ValueError, check, PAGE.replace('https://ready.gov/plan', 'https://wrong.gov'))

    def test_duplicate_id(self):
        self.assertRaises(ValueError, check, PAGE.replace('<main>', '<main><div id="src-1"></div>'))

    def test_extra_source(self):
        self.assertRaises(ValueError, check, PAGE.replace('</ol>', '<li id="src-2"><a href="https://ready.gov/plan">extra</a></li></ol>'))

    def test_missing_source(self):
        self.assertRaises(ValueError, check, PAGE.replace('src-1"><a href="https://ready.gov/plan"', 'src-9"><a href="https://ready.gov/plan"'))

    def test_missing_cite(self):
        self.assertRaises(ValueError, check, PAGE.replace('href="#src-1"', 'href="#src-2"'))

    def test_bad_body(self):
        self.assertRaises(ValueError, check, PAGE.replace('id="pa-main"', 'id="not-body"'))

    def test_false_external_link(self):
        self.assertRaises(ValueError, check, PAGE.replace('href="https://ready.gov/plan"', 'href="javascript:alert(1)"'))

    def test_href_dup(self):
        self.assertRaises(ValueError, check, PAGE.replace('href="https://ready.gov/plan"', 'href="javascript:alert(1)" href="https://ready.gov/plan"'))

    def test_href_base(self):
        self.assertRaises(ValueError, check, PAGE.replace('<main>', '<main><base href="https://attacker.example">'))

    def test_meta_refresh(self):
        self.assertRaises(ValueError, check, PAGE.replace('<main>', '<main><meta http-equiv="refresh" content="0;url=https://attacker.example">'))

    def test_aria_hidden_warning(self):
        self.assertRaises(ValueError, check, PAGE.replace(WARNING, '<div aria-hidden="true">'+WARNING+'</div>'))

    def test_hidden_body_ancestor(self):
        self.assertRaises(ValueError, check, PAGE.replace('<main>', '<main hidden>'))

    def test_hidden_citation(self):
        self.assertRaises(ValueError, check, PAGE.replace('class="pa-cite"', 'class="pa-cite" style="display:none"'))

    def test_hidden_source_subtree(self):
        self.assertRaises(ValueError, check, PAGE.replace('class="pa-sources"', 'class="pa-sources" style="visibility:hidden"'))

    def test_hidden_entry(self):
        self.assertRaises(ValueError, check, PAGE.replace('<li id="src-1">', '<li id="src-1" aria-hidden="true">'))

    def test_style_override(self):
        self.assertRaises(ValueError, check, PAGE.replace('</ol>', '</ol><style>.pa-sources{display:none}</style>'))

    def test_two_source_links(self):
        self.assertRaises(ValueError, check, PAGE.replace('Ready.gov</a>', 'Ready.gov</a><a href="https://second.gov">Two</a>'))

    def test_duplicate_citation(self):
        self.assertRaises(ValueError, check, PAGE.replace('</p></div>', '<a class="pa-cite" href="#src-1">[1]</a></p></div>'))

    def test_unclosed_bibliography(self):
        self.assertRaises(ValueError, check, PAGE.replace('</section>'+REVIEW, REVIEW))

    def test_unexpected_closer(self):
        self.assertRaises(ValueError, check, PAGE.replace('<main>', '</aside><main>'))

    def test_wordpress_block_wrapper(self):
        wp = '<!-- wp:html -->\n<style>.pa{color:#fff}</style>\n' + PAGE + '\n<!-- /wp:html -->'
        self.assertEqual(check(wp)['state'], 'DRAFT_HARD_HOLD')

    def test_preview_document_wrapper(self):
        doc = '<!doctype html><html lang="en"><head><meta charset="utf-8"><style>.pa{}</style></head><body>' + PAGE + '</body></html>'
        self.assertEqual(check(doc)['source_targets'], 1)

    def test_fake_warning_only_in_script(self):
        fake = PAGE.replace(WARNING, '<script>var text="'+G.WARNING+'";</script>')
        self.assertRaises(ValueError, check, fake)

    def test_fake_warning_only_in_style(self):
        fake = PAGE.replace(WARNING, '<style>/* '+G.WARNING+' */</style>')
        self.assertRaises(ValueError, check, fake)

    def test_duplicate_review_section(self):
        self.assertRaises(ValueError, check, PAGE.replace(REVIEW, REVIEW+REVIEW))

    def test_duplicate_empty_source_section(self):
        self.assertRaises(ValueError, check, PAGE.replace(REVIEW, '<section class="pa-sources"></section>'+REVIEW))

    def test_two_citations_same_source(self):
        two = PAGE.replace(BODY, BODY + BODY.replace('id="intro"', 'id="other"'))
        expected = BODY + BODY.replace('id="intro"', 'id="other"')
        self.assertEqual(check(two, expected)['citation_mentions'], 2)

    def test_missing_citation_in_mutated_export(self):
        self.assertRaises(ValueError, check, PAGE.replace('class="pa-cite"','class="foo"'))

# Diverse independent DOM-level mutation regressions, not a single repeated assertion.
for _idx, (_token, _replacement) in enumerate([
    ('class="pa-body" id="pa-main"','class="pa-body" id="pa-main" hidden'),
    ('class="pa-body" id="pa-main"','class="pa-body" id="pa-main" inert'),
    ('class="pa-body" id="pa-main"','class="pa-body" id="pa-main" aria-hidden="true"'),
    ('class="pa-body" id="pa-main"','class="pa-body" id="pa-main" style="opacity:0"'),
    ('class="pa-body" id="pa-main"','class="pa-body" id="pa-main" style="font-size:0px"'),
    ('class="pa-body" id="pa-main"','class="pa-body" id="pa-main" style="content-visibility:hidden"'),
    ('class="pa-sources"','class="pa-sources" inert'),
    ('class="pa-sources"','class="pa-sources" aria-hidden="true"'),
    ('class="pa-sources"','class="pa-sources" style="opacity:0"'),
    ('class="pa-sources"','class="pa-sources" style="display: none"'),
    ('class="pa-review"','class="pa-review" inert'),
    ('class="pa-review"','class="pa-review" style="font-size:0"'),
    ('class="pa-review"','class="pa-review" aria-hidden="true"'),
    ('href="#src-1"','href=" #src-1"'),
    ('href="#src-1"','href="#src-0"'),
    ('href="#src-1"','href="#src-99"'),
    ('href="#src-1"','href="data:text/html,bad"'),
    ('href="#src-1"','href="javascript:alert(1)"'),
    ('href="https://ready.gov/plan"','href="https://ready.gov/plan/"'),
    ('href="https://ready.gov/plan"','href="http://ready.gov/plan"'),
    ('href="https://ready.gov/plan"','href="https://evil.gov/plan"'),
    ('href="https://ready.gov/plan"','href="data:text/plain,wrong"'),
    ('id="src-1"','id="src-0"'),
    ('id="src-1"','id="src-02"'),
    ('id="src-1"','id="src-999"'),
    ('id="src-1"','id="src-1" id="src-1"'),
    ('id="src-1"','id="src-1" aria-hidden="true"'),
    ('id="src-1"','id="src-1" style="display:none"'),
    ('id="src-1"','id="src-1" style="visibility:collapse"'),
    ('id="sources-h"','id="src-1"'),
    ('id="pa-main"','id="src-1"'),
    ('id="review-h"','id="src-1"'),
    ('class="pa-cite"','class="pa-cite" hidden'),
    ('class="pa-cite"','class="pa-cite" inert'),
    ('class="pa-cite"','class="pa-cite" aria-hidden="true"'),
    ('class="pa-cite"','class="pa-cite" style="opacity:0"'),
    ('class="pa-cite"','class="pa-cite" style="visibility:hidden"'),
    ('class="pa-cite"','class="pa-cite" style="display:none"'),
    ('class="pa-cite"','class="pa-cite" class="pa-cite"'),
    ('<main>','<main><base href="/wrong/">'),
    ('<main>','<main><meta http-equiv="refresh" content="0;url=/wrong/">'),
    (WARNING,'<div hidden>'+WARNING+'</div>'),
    (WARNING,'<span style="display:none">'+WARNING+'</span>'),
    (WARNING,'<span style="opacity:0">'+WARNING+'</span>'),
    ('<section class="pa-sources">','<section class="pa-sources" aria-hidden="true">'),
    ('<section class="pa-sources">','<section class="pa-sources" style="font-size:0px">'),
    ('<section class="pa-review">','<section class="pa-review" style="opacity:0">'),
    ('<section class="pa-review">','<section class="pa-review" style="display:none">'),
]):
    def mutate_case(self, token=_token, value=_replacement):
        self.assertIn(token, PAGE)
        self.assertRaises(ValueError, check, PAGE.replace(token, value, 1))
    setattr(BrowserSemantics, f'test_mutation_{_idx:03d}', mutate_case)

if __name__ == '__main__':
    unittest.main()
