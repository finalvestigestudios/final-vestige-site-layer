"""Negative controls: unchanged bytes MUST NOT count when unavailable in the DOM."""
import unittest
from test_homepage_preservation import PreservationGateTests as Original
from verify_homepage_preservation import evaluate, inventory


class DOMCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Original.setUpClass()
        cls.good = Original.source
        cls.baseline = Original.baseline

    def verdict(self, html):
        return evaluate(html, self.baseline)

    def test_valid_exact_markup_admitted_for_inventory_only(self):
        result = self.verdict(self.good)
        self.assertEqual(result['gate'], 'PASS')
        self.assertFalse(result['release_approved'])

    def test_valid_additive_evidence_preserves_content(self):
        self.assertEqual(self.verdict(self.good + '<aside>New source disclosure</aside>')['gate'], 'PASS')

    def test_whole_page_hidden_in_comment(self):
        hidden = '<!-- ' + self.good + ' -->'
        self.assertEqual(inventory(hidden)['record_count'], 72)
        self.assertTrue(inventory(hidden)['jetpack_block_present'])
        self.assertEqual(self.verdict(hidden)['gate'], 'HOLD')

    def test_whole_page_hidden_in_template(self):
        hidden = '<template>' + self.good + '</template>'
        self.assertEqual(inventory(hidden)['record_count'], 72)
        self.assertTrue(inventory(hidden)['jetpack_block_present'])
        self.assertEqual(self.verdict(hidden)['gate'], 'HOLD')

    def test_whole_page_hidden_attribute(self):
        self.assertEqual(self.verdict('<div hidden>' + self.good + '</div>')['gate'], 'HOLD')

    def test_whole_page_inert_attribute(self):
        self.assertEqual(self.verdict('<div inert>' + self.good + '</div>')['gate'], 'HOLD')

    def test_whole_page_aria_hidden(self):
        self.assertEqual(self.verdict('<div aria-hidden="true">' + self.good + '</div>')['gate'], 'HOLD')

    def test_whole_page_inline_display_none(self):
        self.assertEqual(self.verdict('<div style="color:teal; DISPLAY : none;">' + self.good + '</div>')['gate'], 'HOLD')

    def test_whole_page_inline_visibility_hidden(self):
        self.assertEqual(self.verdict('<div style="visibility:hidden">' + self.good + '</div>')['gate'], 'HOLD')

    def test_whole_page_inline_content_visibility_hidden(self):
        self.assertEqual(self.verdict('<div style="content-visibility: hidden">' + self.good + '</div>')['gate'], 'HOLD')

    def test_jetpack_only_hidden(self):
        html = self.good.replace(Original.jetpack, '<div hidden>' + Original.jetpack + '</div>')
        self.assertEqual(self.verdict(html)['gate'], 'HOLD')

    def test_one_margin_hidden(self):
        item = Original.records.splitlines()[0]
        self.assertEqual(self.verdict(self.good.replace(item, '<div hidden>' + item + '</div>'))['gate'], 'HOLD')

    def test_duplicate_chapter_id(self):
        self.assertEqual(self.verdict(self.good + '<aside id="fv-hf-title">Duplicate</aside>')['gate'], 'HOLD')

    def test_raw_gutenberg_block_comment_is_not_rendered_jetpack(self):
        # WordPress context=edit returns Gutenberg source; it must not be
        # presented as an accepted rendered subscription UI.
        raw = self.good.replace(Original.jetpack, '<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->')
        self.assertEqual(self.verdict(raw)['gate'], 'HOLD')

    def test_jetpack_in_regular_comment_does_not_count(self):
        hidden = self.good.replace(Original.jetpack, '<!-- ' + Original.jetpack + ' -->')
        self.assertEqual(self.verdict(hidden)['gate'], 'HOLD')

    def test_all_existing_mutation_tests_still_import(self):
        self.assertEqual(len(self.baseline['required_chapter_ids']), 7)
        self.assertEqual(self.verdict(self.good)['dom_custody']['exposed_margin_count'], 72)


if __name__ == '__main__':
    unittest.main(verbosity=2)
