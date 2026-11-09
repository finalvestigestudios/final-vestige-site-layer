"""R229: browser-vs-HTMLParser non-void self-closing safety regression.

Uses synthetic Preparedness content only. No source/advice/QD or release approval.
Ref: https://html.spec.whatwg.org/multipage/parsing.html#parse-error-non-void-html-element-start-tag-with-trailing-solidus
"""
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'


def module(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + '.py'))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


R226 = module('r226_export_browser_custody')
R227 = module('r227_inert_context_citation_hold')
WARNING = '<p>Independent safety/source and QD verification pending</p>'
CITE = '<sup class="pa-cite"><a href="#src-1">[1]</a></sup>'
INNER = '<h2>Plan</h2><p>Contact ' + CITE + '</p>'
BODY = '<div class="pa-body" id="pa-main">' + INNER + '</div>'
SOURCE = ('<section class="pa-sources"><ol><li id="src-1">'
          '<a href="https://ready.gov/plan">Ready.gov planning</a></li></ol></section>')
REVIEW = ('<section class="pa-review"><h2>Review record</h2>'
          '<p>Independent review pending</p></section>')
PAGE = '<main><div class="pa pa-article">' + WARNING + BODY + SOURCE + REVIEW + '</div></main>'
ORDER = ['ready-plan']


class Library:
    def source_for(self, meta, sid):
        if sid != 'ready-plan':
            raise KeyError(sid)
        return {'url': 'https://ready.gov/plan'}


def both(page):
    return (R226.verify_export(page, ORDER, {}, Library(), INNER),
            R227.verify_inert_contexts(page, ORDER))


class NonVoidTrailingSolidus(unittest.TestCase):
    def assert_hard_hold(self, page):
        for gate in ('R226', 'R227'):
            with self.subTest(gate=gate):
                with self.assertRaisesRegex(ValueError, 'non-void HTML trailing solidus'):
                    if gate == 'R226':
                        R226.verify_export(page, ORDER, {}, Library(), INNER)
                    else:
                        R227.verify_inert_contexts(page, ORDER)

    def test_baseline_retains_nonpublication_state(self):
        a, b = both(PAGE)
        self.assertEqual(a['state'], 'DRAFT_HARD_HOLD')
        self.assertEqual(b['state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(b['release_authorized'])

    def test_preview_wrapper_allowed(self):
        a, b = both('<!doctype html><html lang="en"><body>' + PAGE + '</body></html>')
        self.assertEqual(a['source_targets'], 1)
        self.assertEqual(b['source_targets'], 1)

    def test_wordpress_wrapper_allowed(self):
        a, b = both('<!-- wp:html -->' + PAGE + '<!-- /wp:html -->')
        self.assertEqual(a['source_targets'], 1)
        self.assertEqual(b['source_targets'], 1)

    def test_valid_empty_html_template_before_sources_allowed(self):
        a, b = both(PAGE.replace(SOURCE, '<template></template>' + SOURCE))
        self.assertEqual(a['source_targets'], 1)
        self.assertEqual(b['source_targets'], 1)

    def test_svg_selfclosing_foreign_element_allowed(self):
        page = PAGE.replace(BODY, BODY.replace('Contact ', '<svg xmlns="http://www.w3.org/2000/svg"/>Contact '))
        self.assertEqual(both(page)[1]['state'], 'DRAFT_HARD_HOLD')

    def test_mathml_selfclosing_foreign_element_allowed(self):
        page = PAGE.replace(BODY, BODY.replace('Contact ', '<math xmlns="http://www.w3.org/1998/Math/MathML"/>Contact '))
        self.assertEqual(both(page)[1]['state'], 'DRAFT_HARD_HOLD')

    def test_svg_nested_foreign_selfclosing_element_allowed(self):
        page = PAGE.replace(BODY, BODY.replace('Contact ', '<svg><path d="M0 0"/></svg>Contact '))
        self.assertEqual(both(page)[0]['source_targets'], 1)

    def test_mathml_nested_foreign_selfclosing_element_allowed(self):
        page = PAGE.replace(BODY, BODY.replace('Contact ', '<math><mi/></math>Contact '))
        self.assertEqual(both(page)[0]['source_targets'], 1)

    def test_void_br_selfclosing_allowed(self):
        page = PAGE.replace('Contact ', '<br/>Contact ')
        self.assertEqual(both(page)[0]['source_targets'], 1)

    def test_void_img_selfclosing_allowed(self):
        page = PAGE.replace('Contact ', '<img src="/icon.png" alt=""/>Contact ')
        self.assertEqual(both(page)[1]['source_targets'], 1)

    def test_void_wbr_spaced_selfclosing_allowed(self):
        page = PAGE.replace('Contact ', '<wbr />Contact ')
        self.assertEqual(both(page)[0]['source_targets'], 1)

    def test_regression_parser_emits_single_empty_event(self):
        class EventProbe(HTMLParser):
            def __init__(self):
                super().__init__()
                self.events = []
            def handle_startendtag(self, tag, attrs):
                self.events.append(('startend', tag))
        probe = EventProbe()
        probe.feed('<template/>')
        self.assertEqual(probe.events, [('startend', 'template')])

    def test_template_slash_before_source_is_not_invisible_success(self):
        self.assert_hard_hold(PAGE.replace(SOURCE, '<template/>' + SOURCE))

    def test_script_slash_before_source_is_not_invisible_success(self):
        self.assert_hard_hold(PAGE.replace(SOURCE, '<script/>' + SOURCE))

    def test_style_slash_before_review_is_not_invisible_success(self):
        self.assert_hard_hold(PAGE.replace(REVIEW, '<style/>' + REVIEW))

    def test_template_spaced_slash_before_source_rejected(self):
        self.assert_hard_hold(PAGE.replace(SOURCE, '<template />' + SOURCE))

    def test_nonvoid_slash_rejected_even_with_following_close(self):
        self.assert_hard_hold(PAGE.replace(SOURCE, '<template/></template>' + SOURCE))

    def test_nonvoid_slash_rejected_with_data_attribute(self):
        self.assert_hard_hold(PAGE.replace(SOURCE, '<template data-test="source" />' + SOURCE))


# Diverse semantic locations, two spellings. Each generated test exercises
# BOTH independently bound R226 and R227 guards, not a mocked adapter.
NONVOID = ('template', 'script', 'style', 'noscript', 'textarea', 'select',
           'iframe', 'object', 'canvas', 'audio', 'video', 'dialog', 'details',
           'div', 'section', 'span', 'p', 'article')
POSITIONS = (('before_body', BODY), ('before_source', SOURCE),
             ('before_review', REVIEW))
for index, tag in enumerate(NONVOID):
    for place, target in POSITIONS:
        for spaced in (False, True):
            def reject_case(self, tag=tag, target=target, spaced=spaced):
                bad = '<' + tag + (' />' if spaced else '/>')
                mutated = PAGE.replace(target, bad + target, 1)
                self.assertNotEqual(mutated, PAGE)
                self.assert_hard_hold(mutated)
            title = 'test_nonvoid_%02d_%s_%s' % (
                index, place, 'spaced' if spaced else 'tight')
            setattr(NonVoidTrailingSolidus, title, reject_case)


# HTML integration points under SVG/MathML re-enter HTML parsing, so the
# mere presence of a foreign ancestor is not permission for <template/> etc.
INTEGRATION = (
    ('svg_foreignobject', '<svg><foreignObject>', '</foreignObject></svg>'),
    ('svg_desc', '<svg><desc>', '</desc></svg>'),
    ('svg_title', '<svg><title>', '</title></svg>'),
    ('math_annotation', '<math><annotation-xml encoding="text/html">', '</annotation-xml></math>'),
)
for label, start, end in INTEGRATION:
    for tag in ('template', 'script', 'style', 'p', 'div', 'textarea', 'plaintext'):
        def integration_reject(self, start=start, end=end, tag=tag):
            broken = PAGE.replace(SOURCE, start + '<' + tag + '/>' + end + SOURCE)
            self.assert_hard_hold(broken)
        setattr(NonVoidTrailingSolidus, 'test_html_integration_' + label + '_' + tag, integration_reject)
    for foreign_tag in ('path', 'mi'):
        def foreign_reject(self, start=start, end=end, tag=foreign_tag):
            broken = PAGE.replace(SOURCE, start + '<' + tag + '/>' + end + SOURCE)
            self.assert_hard_hold(broken)
        setattr(NonVoidTrailingSolidus, 'test_foreign_name_in_html_' + label + '_' + foreign_tag, foreign_reject)


if __name__ == '__main__':
    unittest.main()
