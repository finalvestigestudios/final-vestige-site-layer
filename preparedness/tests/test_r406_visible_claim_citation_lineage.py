"""R406 synthetic-only read-only manuscript/depth/source contextual tests."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest import mock
from io import StringIO
import contextlib

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'r406_visible_claim_citation_lineage.py'
spec = importlib.util.spec_from_file_location('r406_local', TOOL)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

SOURCES = frozenset({
    'https://nchfp.uga.edu/how/dry/recipes/jerky/',
    'https://ask.fsis.usda.gov/article/Is-jerky-safe-when-stored-at-room-temperature',
    'https://extension.umn.edu/food/preparing/cooking-at-home/food-preservation/drying',
    'https://extension.umn.edu/natural-resources/weather-and-climate/prepare-for-risks/cooking-without-a-kitchen',
})


def doc(text='Evidence-led text about distinct food storage contexts.', links=None, suffix='', start='<article>'):
    links = sorted(SOURCES if links is None else links)
    return (start + '<h1>Unpublished source audit</h1><p>' + text + '</p><ul>' +
            ''.join('<li><a href="' + u + '">Verify the original source</a></li>' for u in links) +
            '</ul>' + suffix + '</article>').encode('utf-8')


class VisibleLineage(unittest.TestCase):
    def test_synthetic_unmodified_depth_pass_is_not_publication(self):
        raw = doc()
        r = g.inspect({'E395': raw, 'E397': raw, 'E398': raw, 'E399': raw}, SOURCES, e399_receipt=g.digest(raw.decode()))
        self.assertEqual(r['integrity'], 'PASS')
        self.assertFalse(r['eligible'])
        self.assertFalse(r['publication_approved'])
        self.assertFalse(r['medical_or_food_safety_approved'])
        self.assertFalse(r['source_authenticity_proven'])
        self.assertEqual(r['release'], 'DRAFT_HARD_HOLD')
        self.assertIsNone(r['selected_variant'])

    def test_removed_non_citation_paragraph_fails_lineage(self):
        original = doc(suffix='<p>Critical long detail requiring human adjudication</p>')
        r = g.inspect({'E395': original, 'E397': doc(), 'E398': doc(), 'E399': doc()}, SOURCES, e399_receipt=g.digest(doc().decode()))
        self.assertIn('editorial_depth_or_citation_context_changes_need_human_review', r['failures'])
        self.assertEqual(r['deltas']['E395_to_E397']['removed_blocks'], 1)
        self.assertLess(r['deltas']['E395_to_E397']['word_delta'], 0)

    def test_reordered_paragraphs_fails(self):
        base = doc(suffix='<p>A unique statement</p><p>B unique statement</p>')
        other = doc(suffix='<p>B unique statement</p><p>A unique statement</p>')
        result = g.inspect({'E395': base, 'E397': other, 'E398': other, 'E399': other}, SOURCES, e399_receipt=g.digest(other.decode()))
        self.assertTrue(result['deltas']['E395_to_E397']['reordered_or_changed'])
        self.assertEqual(result['deltas']['E395_to_E397']['removed_blocks'], 0)

    def test_edited_wording_fails_even_with_all_source_urls(self):
        a, b = doc(text='Storage differs by product.'), doc(text='Every kind of food is safe forever.')
        self.assertEqual(g.inspect({'E395': a, 'E397': b, 'E398': b, 'E399': b}, SOURCES, e399_receipt=g.digest(b.decode()))['integrity'], 'FAIL')

    def test_addition_is_not_auto_approved(self):
        a, b = doc(), doc(suffix='<p>New advice not reviewed by a qualified expert.</p>')
        r = g.inspect({'E395': a, 'E397': b, 'E398': b, 'E399': b}, SOURCES, e399_receipt=g.digest(b.decode()))
        self.assertEqual(r['deltas']['E395_to_E397']['added_blocks'], 1)
        self.assertFalse(r['publication_approved'])
        self.assertEqual(r['integrity'], 'FAIL')

    def test_source_in_hidden_region_does_not_count_as_supported(self):
        source = sorted(SOURCES)[0]
        text = doc(links=SOURCES - {source}, suffix=f'<div hidden><p><a href="{source}">Source</a></p></div>')
        r = g.capture(text, SOURCES)
        self.assertIn(source, r['source_urls_seen'])
        self.assertIn(source, r['source_scope_missing'])

    def test_source_outside_claim_does_not_count(self):
        source = sorted(SOURCES)[0]
        text = doc(links=SOURCES - {source}, suffix=f'<div><a href="{source}">Source</a></div>')
        r = g.capture(text, SOURCES)
        self.assertIn(source, r['source_scope_missing'])
        self.assertIn('source_link_outside_claim_context', r['failures'])

    def test_source_citation_inside_heading_does_not_count(self):
        source = sorted(SOURCES)[0]
        text = doc(links=SOURCES - {source}, suffix=f'<h2><a href="{source}">Source</a></h2>')
        self.assertIn(source, g.capture(text, SOURCES)['source_scope_missing'])

    def test_source_in_visible_claim_paragraph_counts(self):
        source = sorted(SOURCES)[0]
        r = g.capture(doc(links=SOURCES - {source}, suffix=f'<p><a href="{source}">Source</a></p>'), SOURCES)
        self.assertNotIn(source, r['source_scope_missing'])

    def test_source_in_visible_list_counts(self):
        source = sorted(SOURCES)[0]
        r = g.capture(doc(links=SOURCES - {source}, suffix=f'<ul><li><a href="{source}">Source</a></li></ul>'), SOURCES)
        self.assertNotIn(source, r['source_scope_missing'])

    def test_source_in_visible_table_cell_counts(self):
        source = sorted(SOURCES)[0]
        r = g.capture(doc(links=SOURCES - {source}, suffix=f'<table><tr><td><a href="{source}">Source</a></td></tr></table>'), SOURCES)
        self.assertNotIn(source, r['source_scope_missing'])

    def test_missing_required_source_removed_from_scope(self):
        source = sorted(SOURCES)[0]
        r = g.capture(doc(links=SOURCES - {source}), SOURCES)
        self.assertEqual(r['source_scope_missing'], [source])
        self.assertIn('required_sources_not_visibly_claim_bound', r['failures'])

    def test_duplicate_identical_blocks_preserved_by_count(self):
        a = doc(suffix='<p>Repeat me</p><p>Repeat me</p>')
        b = doc(suffix='<p>Repeat me</p>')
        r = g.inspect({'E395': a, 'E397': b, 'E398': b, 'E399': b}, SOURCES, e399_receipt=g.digest(b.decode()))
        self.assertEqual(r['deltas']['E395_to_E397']['removed_blocks'], 1)

    def test_source_removal_detected_even_if_reading_words_remain(self):
        source = sorted(SOURCES)[0]
        a = doc()
        b = doc(links=SOURCES - {source}, suffix='<p>Verify the original source</p>')
        r = g.inspect({'E395': a, 'E397': b, 'E398': b, 'E399': b}, SOURCES, e399_receipt=g.digest(b.decode()))
        self.assertIn(source, r['deltas']['E395_to_E397']['removed_bound_sources'])
        self.assertIn('claim_bound_source_removed', r['failures'])

    def test_invalid_inventory_refused(self):
        result = g.inspect({'E395': doc()}, SOURCES)
        self.assertEqual(result['integrity'], 'FAIL')
        self.assertFalse(result['publication_approved'])

    def test_e399_is_mandatory_and_not_silent_latest(self):
        raw = doc()
        r = g.inspect({'E395': raw, 'E397': raw, 'E398': raw}, SOURCES)
        self.assertEqual(r['integrity'], 'FAIL')
        self.assertIn('variant_inventory_mismatch', r['failures'])

    def test_e399_reported_authentic_receipt_is_not_synthetic(self):
        raw = doc()
        r = g.inspect({k: raw for k in g.EDITION_KEYS}, SOURCES)
        self.assertIn('e399_original_receipt_mismatch', r['failures'])

    def test_e399_to_e398_difference_preserved(self):
        raw = doc()
        variant = doc(suffix='<p>E399 new claim needs human approval</p>')
        r = g.inspect({'E395': raw, 'E397': raw, 'E398': raw, 'E399': variant},
                      SOURCES, e399_receipt=g.digest(variant.decode()))
        self.assertEqual(r['deltas']['E398_to_E399']['added_blocks'], 1)
        self.assertEqual(r['integrity'], 'FAIL')

    def test_missing_source_inventory_type_refused(self):
        self.assertEqual(g.capture(doc(), None)['failures'], ['invalid_source_inventory'])

    def test_utf8_error_refused(self):
        self.assertIn('unparseable_html', g.capture(doc() + b'\xff', SOURCES)['failures'])

    def test_missing_input_refused(self):
        self.assertIn('missing_or_oversized_html', g.capture(None, SOURCES)['failures'])

    def test_empty_input_refused(self):
        self.assertIn('missing_or_oversized_html', g.capture(b'', SOURCES)['failures'])

    def test_over_limit_refused_without_parse(self):
        self.assertIn('missing_or_oversized_html', g.capture(b'x' * (g.MAX_HTML_BYTES + 1), SOURCES)['failures'])

    def test_unclosed_paragraph_refused(self):
        self.assertIn('unclosed_html_markup', g.capture(b'<article><p>Unclosed', frozenset())['failures'])

    def test_stray_close_refused(self):
        self.assertIn('stray_closing_tag', g.capture(b'<p>Closed</p></article>', frozenset())['failures'])

    def test_markup_misnest_refused(self):
        self.assertIn('misnested_html', g.capture(b'<article><p><em>Words</p></em></article>', frozenset())['failures'])

    def test_empty_visible_manuscript_refused(self):
        self.assertIn('empty_visible_manuscript', g.capture(b'<article><style>p{color:red}</style></article>', frozenset())['failures'])

    def test_no_claim_blocks_refused(self):
        self.assertIn('missing_reading_blocks', g.capture(b'<article>Loose narrative only</article>', frozenset())['failures'])

    def test_digest_normalizes_whitespace_only(self):
        self.assertEqual(g.normalized('hello   world\n test'), 'hello world test')
        self.assertNotEqual(g.digest('not the same'), g.digest('same'))

    def test_no_originals_exit_two(self):
        with contextlib.redirect_stdout(StringIO()) as out:
            self.assertEqual(g.main([]), 2)
        import json
        self.assertEqual(json.loads(out.getvalue())['integrity'], 'FAIL')

    def test_nested_source_anchor_is_flagged(self):
        url = sorted(SOURCES)[0]
        raw = doc(suffix=f'<p><a href="{url}">Outer<a href="{url}">Inner</a></a></p>')
        self.assertIn('nested_anchor', g.capture(raw, SOURCES)['failures'])

    def test_anchor_without_text_does_not_count(self):
        source = sorted(SOURCES)[0]
        r = g.capture(doc(links=SOURCES - {source}, suffix=f'<p><a href="{source}"></a></p>'), SOURCES)
        self.assertIn(source, r['source_scope_missing'])
        self.assertIn('unlabeled_source_link', r['failures'])

    def test_html_structure_change_flagged_even_same_text(self):
        a = doc(suffix='<p>Source note</p>')
        b = doc(suffix='<li>Source note</li>')
        r = g.inspect({'E395': a, 'E397': b, 'E398': b, 'E399': b}, SOURCES, e399_receipt=g.digest(b.decode()))
        self.assertEqual(r['integrity'], 'FAIL')

    def test_unwrapped_reading_depth_loss_also_requires_review(self):
        original = doc(suffix='<div>Unwrapped but visible reader explanation.</div>')
        amended = doc()
        r = g.inspect({'E395': original, 'E397': amended, 'E398': amended, 'E399': amended},
                      SOURCES, e399_receipt=g.digest(amended.decode()))
        self.assertTrue(r['deltas']['E395_to_E397']['reading_text_changed'])
        self.assertEqual(r['deltas']['E395_to_E397']['removed_blocks'], 0)
        self.assertIn('editorial_depth_or_citation_context_changes_need_human_review', r['failures'])

    def test_semantically_neutral_inline_markup_does_not_false_fail(self):
        original = doc()
        amended = original.decode().replace('<li><a', '<li><span><a').replace('</a></li>', '</a></span></li>').encode()
        r = g.inspect({'E395': original, 'E397': amended, 'E398': amended, 'E399': amended}, SOURCES, e399_receipt=g.digest(amended.decode()))
        self.assertEqual(r['integrity'], 'PASS')

    def test_semantically_neutral_list_wrapper_does_not_false_fail(self):
        original = doc()
        amended = original.replace(b'<ul>', b'<div>').replace(b'</ul>', b'</div>')
        r = g.inspect({'E395': original, 'E397': amended, 'E398': amended, 'E399': amended}, SOURCES, e399_receipt=g.digest(amended.decode()))
        self.assertEqual(r['integrity'], 'PASS')

    def test_url_fragment_normalizes(self):
        url = sorted(SOURCES)[0]
        self.assertEqual(g._link(url + '#more'), url)


HIDDEN_WRAPPERS = {
    'hidden_attr': '<div hidden>{}</div>',
    'inert': '<div inert>{}</div>',
    'aria_hidden': '<div aria-hidden="true">{}</div>',
    'display_none': '<div style="display:none">{}</div>',
    'display_none_important': '<div style="color:blue; display: none !important;">{}</div>',
    'visibility_hidden': '<div style="visibility:hidden;">{}</div>',
    'head': '<head>{}</head>',
    'style': '<style>{}</style>',
    'script': '<script>{}</script>',
    'noscript': '<noscript>{}</noscript>',
    'template': '<template>{}</template>',
    'nav': '<nav>{}</nav>',
    'footer': '<footer>{}</footer>',
}


def make_hidden_case(wrapper):
    def test(self):
        source = sorted(SOURCES)[0]
        markup = wrapper.format('<p><a href="' + source + '">Source</a></p>')
        raw = doc(links=SOURCES - {source}, suffix=markup)
        r = g.capture(raw, SOURCES)
        self.assertIn(source, r['source_scope_missing'])
        self.assertNotIn(source, r['claim_bound_source_urls'])
        self.assertIn('required_sources_not_visibly_claim_bound', r['failures'])
    return test


for label, wrapper in HIDDEN_WRAPPERS.items():
    setattr(VisibleLineage, 'test_hidden_source_' + label, make_hidden_case(wrapper))


BODY_MUTATIONS = {
    'remove_h1': (lambda d: d.replace('<h1>Unpublished source audit</h1>', '')),
    'rename_h1': (lambda d: d.replace('Unpublished source audit', 'Unverified claims')),
    'remove_claim': (lambda d: d.replace('Evidence-led text', '')),
    'change_storage_word': (lambda d: d.replace('food storage contexts', 'all households')),
    'swap_claim_sentence': (lambda d: d.replace('distinct food storage contexts', 'one universal storage rule')),
    'add_unreviewed_statement': (lambda d: d.replace('</article>', '<p>Unreviewed new finding</p></article>')),
    'replace_h1_h2': (lambda d: d.replace('<h1>', '<h2>').replace('</h1>', '</h2>')),
    'change_source_label': (lambda d: d.replace('Verify the original source', 'Might support claim')),
    'alter_paragraph_tag': (lambda d: d.replace('<p>', '<li>').replace('</p>', '</li>')),
    'add_plain_text': (lambda d: d.replace('distinct', 'distinct and nuanced')),
}


def make_mutation_case(change):
    def test(self):
        original = doc().decode()
        variant = change(original).encode()
        r = g.inspect({'E395': original.encode(), 'E397': variant, 'E398': variant, 'E399': variant}, SOURCES, e399_receipt=g.digest(variant.decode()))
        if variant == original.encode():
            self.skipTest('no actual change produced')
        self.assertEqual(r['integrity'], 'FAIL')
        self.assertFalse(r['publication_approved'])
        self.assertTrue(r['deltas']['E395_to_E397']['reordered_or_changed'])
    return test


for label, change in BODY_MUTATIONS.items():
    setattr(VisibleLineage, 'test_derivative_' + label, make_mutation_case(change))

if __name__ == '__main__':
    unittest.main()
