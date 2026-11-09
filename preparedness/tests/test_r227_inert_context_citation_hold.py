"""Isolated, deterministic R227 tests; synthetic drafts are never safety approvals."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools' / 'r227_inert_context_citation_hold.py'
SPEC = importlib.util.spec_from_file_location('r227', SCRIPT)
G = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(G)

WARNING = '<p>Independent safety/source and QD verification pending</p>'
BODY = '<div class="pa-body" id="pa-main"><p>Plan <sup class="pa-cite"><a href="#src-1">[1]</a></sup></p></div>'
SOURCE = '<section class="pa-sources"><ol><li id="src-1"><a href="https://ready.gov/plan">Ready.gov</a></li></ol></section>'
REVIEW = '<section class="pa-review"><h2>Review record</h2><p>Safety review pending</p></section>'
PAGE = '<main><div class="pa pa-article">' + WARNING + BODY + SOURCE + REVIEW + '</div></main>'
ORDER = ['ready-plan']


def check(page=PAGE, order=ORDER):
    return G.verify_inert_contexts(page, order)


class InertContextSafety(unittest.TestCase):
    def test_original_draft_hold(self):
        self.assertEqual(check()['state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(check()['release_authorized'])

    def test_wordpress_html_wrapper(self):
        self.assertEqual(check('<!-- wp:html -->' + PAGE + '<!-- /wp:html -->')['source_targets'], 1)

    def test_preview_html_wrapper(self):
        doc = '<!doctype html><html><head><style>.pa {color:#000}</style></head><body>' + PAGE + '</body></html>'
        self.assertEqual(check(doc)['source_targets'], 1)

    def test_open_details_still_accessible(self):
        self.assertEqual(check(PAGE.replace(SOURCE, '<details open>' + SOURCE + '</details>'))['source_targets'], 1)

    def test_open_dialog_still_accessible(self):
        self.assertEqual(check(PAGE.replace(REVIEW, '<dialog open>' + REVIEW + '</dialog>'))['source_targets'], 1)

    def test_empty_citation_free_tool(self):
        page = PAGE.replace('<sup class="pa-cite"><a href="#src-1">[1]</a></sup>', '').replace('<li id="src-1"><a href="https://ready.gov/plan">Ready.gov</a></li>', '')
        self.assertEqual(check(page, [])['source_targets'], 0)

    def test_noncritical_template_allowed(self):
        self.assertEqual(check(PAGE + '<template><p>Unrelated illustration</p></template>')['state'], 'DRAFT_HARD_HOLD')

    def test_noncritical_closed_details_allowed(self):
        self.assertEqual(check(PAGE + '<details><summary>Optional notes</summary><p>Extra</p></details>')['state'], 'DRAFT_HARD_HOLD')

    def test_warning_only_in_noscript(self):
        self.assertRaises(ValueError, check, PAGE.replace(WARNING, '<noscript>' + WARNING + '</noscript>'))

    def test_warning_only_in_closed_dialog(self):
        self.assertRaises(ValueError, check, PAGE.replace(WARNING, '<dialog>' + WARNING + '</dialog>'))

    def test_warning_only_in_closed_details(self):
        self.assertRaises(ValueError, check, PAGE.replace(WARNING, '<details>' + WARNING + '</details>'))

    def test_critical_orphan_end_tag(self):
        self.assertRaises(ValueError, check, PAGE.replace('<section class="pa-sources">', '<section class="pa-sources"></aside>'))

    def test_critical_broken_parent_close(self):
        self.assertRaises(ValueError, check, PAGE.replace('</li></ol>', '</ol>'))

    def test_unclosed_review(self):
        self.assertRaises(ValueError, check, PAGE.replace('</section></div></main>', '</div></main>'))

    def test_duplicate_bibliography(self):
        self.assertRaises(ValueError, check, PAGE.replace(SOURCE, SOURCE + SOURCE))

    def test_duplicate_source_id(self):
        self.assertRaises(ValueError, check, PAGE.replace('</ol>', '<li id="src-1">duplicate</li></ol>'))

    def test_empty_expected_order_with_source(self):
        self.assertRaises(ValueError, check, PAGE, [])

    def test_expected_order_duplicate(self):
        self.assertRaises(ValueError, check, PAGE, ['ready-plan', 'ready-plan'])

    def test_invalid_page_type(self):
        self.assertRaises(ValueError, check, 1)

    def test_invalid_order_type(self):
        self.assertRaises(ValueError, check, PAGE, 'ready-plan')


# Each mutation targets a different tag/context and semantic role. The inherited
# R226 checker tests explicit IDs, ordinals and destinations; R227 covers HTML
# fragments that browsers omit from the active reading/accessibility surface.
MUTATIONS = [
    (label + '_' + role, target, '<' + tag + suffix + '>' + target + '</' + tag + '>')
    for label, tag, suffix in [
        ('template', 'template', ''), ('noscript', 'noscript', ''),
        ('head', 'head', ''), ('script', 'script', ''), ('style', 'style', ''),
        ('iframe', 'iframe', ''), ('object', 'object', ''),
        ('canvas', 'canvas', ''), ('svg', 'svg', ''),
        ('math', 'math', ''), ('select', 'select', ''),
        ('textarea', 'textarea', ''), ('audio', 'audio', ''),
        ('video', 'video', ''), ('closed_details', 'details', ''),
        ('closed_dialog', 'dialog', ''),
    ]
    for role, target in [('source', SOURCE), ('review', REVIEW), ('body', BODY)]
]

for number, (label, target, replacement) in enumerate(MUTATIONS):
    def case(self, needle=target, substitute=replacement):
        self.assertIn(needle, PAGE)
        with self.assertRaises(ValueError):
            check(PAGE.replace(needle, substitute, 1))
    setattr(InertContextSafety, 'test_inert_%03d_%s' % (number, label), case)

if __name__ == '__main__':
    unittest.main()
