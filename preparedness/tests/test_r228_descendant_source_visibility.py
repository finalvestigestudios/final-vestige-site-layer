"""R228 synthetic regression matrix for invisible source-link descendants.

These tests do not establish independent source review or publication safety.
"""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'r227_inert_context_citation_hold.py'
SPEC = importlib.util.spec_from_file_location('r227', SCRIPT)
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)

WARNING = '<p>Independent safety/source and QD verification pending</p>'
CITE = '<sup class="pa-cite"><a href="#src-1">[1]</a></sup>'
BODY = '<div class="pa-body" id="pa-main"><p>Plan ' + CITE + '</p></div>'
LINK = '<a href="https://ready.gov/plan">Ready.gov</a>'
SOURCE = '<section class="pa-sources"><ol><li id="src-1">' + LINK + '</li></ol></section>'
REVIEW_TEXT = '<p>Safety review pending</p>'
REVIEW = '<section class="pa-review"><h2>Review record</h2>' + REVIEW_TEXT + '</section>'
PAGE = '<main>' + WARNING + BODY + SOURCE + REVIEW + '</main>'


def verify(page=PAGE):
    return G.verify_inert_contexts(page, ['ready-plan'])


class DescendantSafety(unittest.TestCase):
    def test_ordinary_document_hold(self):
        result = verify()
        self.assertEqual(result['state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(result['release_authorized'])

    def test_unrelated_template_in_article_body_allowed(self):
        updated = PAGE.replace('</p></div>', '<template><span>Decorative</span></template></p></div>')
        self.assertEqual(verify(updated)['state'], G.HOLD)

    def test_source_fragment_inside_body_template_rejected(self):
        broken = PAGE.replace(CITE, '<template><a href="#src-1">[1]</a></template>' + CITE)
        with self.assertRaisesRegex(ValueError, 'source-fragment hyperlink'):
            verify(broken)

    def test_already_hidden_outer_source_rejected(self):
        with self.assertRaises(ValueError):
            verify(PAGE.replace(SOURCE, '<template>' + SOURCE + '</template>'))

    def test_html_preview_wrapper_passes(self):
        self.assertEqual(verify('<!doctype html><html><body>' + PAGE + '</body></html>')['source_targets'], 1)

    def test_wordpress_wrapper_passes(self):
        self.assertEqual(verify('<!-- wp:html -->' + PAGE + '<!-- /wp:html -->')['source_targets'], 1)

    def test_open_details_source_link_allowed(self):
        self.assertEqual(verify(PAGE.replace(LINK, '<details open>' + LINK + '</details>'))['source_targets'], 1)

    def test_open_dialog_citation_allowed(self):
        self.assertEqual(verify(PAGE.replace(CITE, '<dialog open>' + CITE + '</dialog>'))['source_targets'], 1)

    def test_nested_hidden_source_link_rejected(self):
        broken = PAGE.replace(LINK, '<template><noscript>' + LINK + '</noscript></template>')
        with self.assertRaisesRegex(ValueError, 'inert/conditional descendant'):
            verify(broken)

    def test_no_citation_allowed_if_no_sources(self):
        clean = PAGE.replace(CITE, '').replace('<li id="src-1">' + LINK + '</li>', '')
        self.assertEqual(G.verify_inert_contexts(clean, [])['source_targets'], 0)


TAGS = ['template', 'noscript', 'head', 'script', 'style', 'iframe', 'object',
        'canvas', 'svg', 'math', 'select', 'textarea', 'audio', 'video',
        'details', 'dialog']
ROLES = [('source_href', LINK), ('citation_href', '<a href="#src-1">[1]</a>'),
         ('review_content', REVIEW_TEXT)]
for tag in TAGS:
    for role, target in ROLES:
        def case(self, tag=tag, target=target):
            self.assertIn(target, PAGE)
            broken = PAGE.replace(target, f'<{tag}>' + target + f'</{tag}>', 1)
            with self.assertRaisesRegex(ValueError, 'inert/conditional descendant'):
                verify(broken)
        setattr(DescendantSafety, 'test_inert_descendant_' + tag + '_' + role, case)


if __name__ == '__main__':
    unittest.main()
