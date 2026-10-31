"""Adversarial R12 tests: original citation vs rendered source link parity."""
from __future__ import annotations

import copy
from html import escape
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rendered_citation_gate as gate


SOURCES = {
    'one': {'title': 'First & Primary', 'url': 'https://example.org/a?x=1&y=2',
            'notes': 'Section 2 only; not the full work', 'human_link_check': False},
    'two': {'title': 'Second Study', 'url': 'https://example.edu/b',
            'notes': '', 'human_link_check': False},
}
NOTES = {'one': 'Supports one specific proposition', 'two': 'Used for a different claim'}
BODY = '<p>Original A {{cite:one}}, another A {{cite:one}}.</p><p>Original B {{cite:two}}.</p>'


def claims(body):
    return [{'source_id': m.group(1), 'ordinal': n}
            for n, m in enumerate(re.finditer(r'\{\{cite:([a-z0-9-]+)\}\}', body), 1)]


class FakeLib:
    def __init__(self):
        self.articles = {'sample': {'slug': 'sample', 'status': {'publish': 'draft'},
                                    'source_use': copy.deepcopy(NOTES), '_body': BODY}}
        self.sources = copy.deepcopy(SOURCES)
        self.crosswalk_groups = {SOURCES['one']['url']: {'review_status': 'pending'}}

    def source_for(self, meta, sid):
        return self.sources[sid]


class FakeRenderer:
    def __init__(self, *, mutate=lambda s: s, sources=None, meta=None, slug='sample'):
        self.mutate = mutate
        self.sources = sources
        self.meta = meta
        self.slug = slug

    def build_article(self, lib, slug):
        meta = lib.articles[slug]
        sequence = claims(meta['_body'])
        order = list(dict.fromkeys(c['source_id'] for c in sequence))
        refs = []
        for c in sequence:
            sid = c['source_id']; n = order.index(sid) + 1
            title = escape(lib.source_for(meta, sid)['title'], quote=True)
            refs.append(f'<sup class="pa-cite"><a href="#src-{n}" aria-label="Source {n}: {title}">[{n}]</a></sup>')
        foot = []
        for n, sid in enumerate(order, 1):
            src = lib.source_for(meta, sid)
            marker = 'Human source-link check pending'
            text = f'<span class="pa-src-meta">Machine-checked 2026-10-30 · {marker}</span>'
            text += f'<span class="pa-src-use">Used for: {escape(meta["source_use"][sid])}</span>'
            if src.get('notes'):
                text += f'<span class="pa-src-use">Reading scope / limitations: {escape(src["notes"])}</span>'
            if lib.crosswalk_groups.get(src['url']):
                text += '<span class="pa-src-use">Shared-source reading scope: independent review pending</span>'
            foot.append(f'<li id="src-{n}"><a href="{escape(src["url"], quote=True)}" rel="noopener">'
                        f'{escape(src["title"])}</a>{text}</li>')
        inner = ('<div class="pa pa-article"><header>Draft: not public</header>'
                 '<div class="pa-body" id="pa-main">' + ''.join(refs) + '</div>'
                 '<section class="pa-sources"><h2>Sources</h2><ol>' + ''.join(foot) + '</ol></section>'
                 '<script type="application/ld+json">{"hello":true}</script></div>')
        return {'slug': self.slug, 'meta': self.meta if self.meta is not None else meta,
                'sources': self.sources if self.sources is not None else order, 'inner': self.mutate(inner)}


def run(mod=lambda s: s, lib=None, renderer=None):
    lib = lib or FakeLib()
    renderer = renderer or FakeRenderer(mutate=mod)
    return gate.audit_article(lib, renderer, 'sample', claim_parser=claims)


class RenderedCitationsTests(unittest.TestCase):
    def test_baseline(self):
        self.assertEqual(run(), {'slug': 'sample', 'citations': 3, 'source_pairs': 2})

    def test_receipt_hold_only(self):
        lib = FakeLib()
        result = gate.audit_corpus(lib, FakeRenderer(), claim_parser=claims,
                                   expected_items=1, expected_occurrences=3, expected_pairs=2)
        self.assertEqual(result['release_state'], 'HOLD')
        self.assertIs(result['may_publish'], False)
        self.assertIs(result['human_source_claim_verification'], False)
        self.assertIs(result['medical_food_water_fire_safety_verified'], False)

    def test_repeated_occurrences_preserved(self):
        self.assertEqual(run()['citations'], 3)
        self.assertEqual(run()['source_pairs'], 2)

    def test_html_entities_decoded_for_title_and_url(self):
        self.assertEqual(run()['source_pairs'], 2)

    def test_content_changed(self):
        lib = FakeLib(); lib.articles['sample']['_body'] = 'no citations'
        with self.assertRaises(gate.RenderCitationFailure): run(lib=lib)

    def test_non_draft_rejected(self):
        lib = FakeLib(); lib.articles['sample']['status']['publish'] = 'published'
        with self.assertRaises(gate.RenderCitationFailure): run(lib=lib)

    def test_missing_article_slug_rejected(self):
        lib = FakeLib(); lib.articles['sample']['slug'] = 'other'
        with self.assertRaises(gate.RenderCitationFailure): run(lib=lib)

    def test_extra_source_use_rejected(self):
        lib = FakeLib(); lib.articles['sample']['source_use']['three'] = 'phantom'
        with self.assertRaises(gate.RenderCitationFailure): run(lib=lib)

    def test_missing_source_use_rejected(self):
        lib = FakeLib(); del lib.articles['sample']['source_use']['two']
        with self.assertRaises(gate.RenderCitationFailure): run(lib=lib)

    def test_unsupported_source_claim(self):
        lib = FakeLib(); lib.articles['sample']['_body'] += '{{cite:unknown}}'
        with self.assertRaises((KeyError, gate.RenderCitationFailure)): run(lib=lib)

    def test_wrong_build_slug(self):
        with self.assertRaises(gate.RenderCitationFailure): run(renderer=FakeRenderer(slug='other'))

    def test_wrong_build_source_order(self):
        with self.assertRaises(gate.RenderCitationFailure): run(renderer=FakeRenderer(sources=['two', 'one']))

    def test_wrong_build_meta_identity(self):
        with self.assertRaises(gate.RenderCitationFailure): run(renderer=FakeRenderer(meta={}))

    def test_baseline_count_regression(self):
        with self.assertRaises(gate.RenderCitationFailure):
            gate.audit_corpus(FakeLib(), FakeRenderer(), claim_parser=claims,
                              expected_items=1, expected_occurrences=4, expected_pairs=2)

    def test_baseline_pairs_regression(self):
        with self.assertRaises(gate.RenderCitationFailure):
            gate.audit_corpus(FakeLib(), FakeRenderer(), claim_parser=claims,
                              expected_items=1, expected_occurrences=3, expected_pairs=3)

    def test_baseline_items_regression(self):
        with self.assertRaises(gate.RenderCitationFailure):
            gate.audit_corpus(FakeLib(), FakeRenderer(), claim_parser=claims,
                              expected_items=36)

    def test_bad_report_source_checks(self):
        lib = FakeLib(); lib.sources['one']['human_link_check'] = True
        with self.assertRaises(gate.RenderCitationFailure): run(lib=lib)

    def test_explicit_shared_group_withheld(self):
        lib = FakeLib(); lib.crosswalk_groups[SOURCES['one']['url']]['review_status'] = 'pending'
        self.assertEqual(run(lib=lib)['citations'], 3)

    def test_approved_safety_not_release(self):
        lib = FakeLib(); lib.articles['sample']['safety_review'] = {'state': 'approved'}
        result = gate.audit_corpus(lib, FakeRenderer(), claim_parser=claims,
                                   expected_items=1, expected_occurrences=3, expected_pairs=2)
        self.assertIs(result['may_publish'], False)

    def test_source_details_changed_with_renderer_same(self):
        lib = FakeLib(); lib.sources['one']['notes'] = 'Newly restricted chapter'
        self.assertEqual(run(lib=lib)['source_pairs'], 2)

    def test_unchecked_source_note_none(self):
        lib = FakeLib(); lib.articles['sample']['source_use']['two'] = None
        with self.assertRaises((TypeError, gate.RenderCitationFailure)):
            run(lib=lib)

    def test_invalid_parser_result(self):
        with self.assertRaises(gate.RenderCitationFailure):
            gate.audit_article(FakeLib(), FakeRenderer(), 'sample', claim_parser=lambda x: [{}])

    def test_rendered_claim_occurrences_not_number_of_source_pairs(self):
        lib = FakeLib(); lib.articles['sample']['_body'] = '<p>{{cite:one}}{{cite:one}}{{cite:one}}{{cite:two}}</p>'
        self.assertEqual(run(lib=lib)['citations'], 4)
        self.assertEqual(run(lib=lib)['source_pairs'], 2)


# Each distinct mutation is a separate unittest test (not a single subtest).
MUTATIONS = {
    'citation_removed': lambda s: s.replace('<sup class="pa-cite"><a href="#src-1" aria-label="Source 1: First &amp; Primary">[1]</a></sup>', '', 1),
    'citation_added': lambda s: s.replace('</div><section class="pa-sources">', '<sup class="pa-cite"><a href="#src-1" aria-label="Source 1: First &amp; Primary">[1]</a></sup></div><section class="pa-sources">', 1),
    'wrong_cite_target': lambda s: s.replace('href="#src-1"', 'href="#src-2"', 1),
    'wrong_cite_label': lambda s: s.replace('aria-label="Source 1:', 'aria-label="Source 7:', 1),
    'wrong_cite_text': lambda s: s.replace('>[1]</a>', '>[2]</a>', 1),
    'missing_aria': lambda s: s.replace('aria-label="Source 1: First &amp; Primary"', '', 1),
    'broken_cite_wrapper': lambda s: s.replace('<sup class="pa-cite">', '<span class="pa-cite">', 1).replace('</sup>', '</span>', 1),
    'citation_hijack_body': lambda s: s.replace('class="pa-body" id="pa-main"', 'class="pa-body" id="other"', 1),
    'unexpected_second_body': lambda s: s.replace('<div class="pa-body"', '<div id="pa-main"></div><div class="pa-body"', 1),
    'source_missing': lambda s: s.replace('<li id="src-2">', '<li id="lost">', 1),
    'source_duplicated': lambda s: s.replace('<li id="src-2">', '<li id="src-1">', 1),
    'source_wrong_order': lambda s: s.replace('li id="src-2"', 'li id="src-3"', 1),
    'source_url_wrong': lambda s: s.replace('href="https://example.edu/b"', 'href="https://example.edu/c"', 1),
    'source_title_wrong': lambda s: s.replace('>Second Study</a>', '>Not second study</a>', 1),
    'source_rel_removed': lambda s: s.replace('href="https://example.edu/b" rel="noopener"', 'href="https://example.edu/b"', 1),
    'source_rel_nofollow_only': lambda s: s.replace('href="https://example.edu/b" rel="noopener"', 'href="https://example.edu/b" rel="nofollow"', 1),
    'source_note_erased': lambda s: s.replace('Used for: Supports one specific proposition', 'Used for:', 1),
    'source_note_changed': lambda s: s.replace('Used for: Used for a different claim', 'Used for: unrelated', 1),
    'source_notes_erased': lambda s: s.replace('Reading scope / limitations: Section 2 only; not the full work', 'Scope erased', 1),
    'human_check_forged': lambda s: s.replace('Human source-link check pending', 'Human source-link check complete', 1),
    'human_check_missing': lambda s: s.replace('Human source-link check pending', '', 1),
    'shared_review_hidden': lambda s: s.replace('Shared-source reading scope: independent review pending', '', 1),
    'shared_review_forged': lambda s: s.replace('Shared-source reading scope: independent review pending', 'Shared-source reading scope: approved', 1),
    'raw_citation_token': lambda s: s.replace('</div><section class="pa-sources">', '{{cite:one}}</div><section class="pa-sources">', 1),
    'html_unclosed': lambda s: s[:-6],
    'source_footnote_extra': lambda s: s.replace('</ol></section>', '<li id="src-4"><a href="https://example.com" rel="noopener">fake</a></li></ol></section>', 1),
    'cite_extra_anchor': lambda s: s.replace('>[1]</a></sup>', '>[1]</a><a href="#src-1">other</a></sup>', 1),
    'foot_extra_anchor': lambda s: s.replace('>Second Study</a>', '>Second Study</a><a href="https://example.edu/other">other</a>', 1),
    'sources_section_missing': lambda s: s.replace('class="pa-sources"', 'class="elsewhere"', 1),
    'extra_source_section': lambda s: s.replace('</ol></section>', '</ol></section><section class="pa-sources"></section>', 1),
    'source_outside_section': lambda s: s.replace('<section class="pa-sources">', '</div><section class="pa-sources">', 1),
    'cite_outside_body': lambda s: s.replace('<div class="pa-body" id="pa-main">', '<div class="pa-body" id="pa-main"></div>', 1),
    'noncanonical_anchor': lambda s: s.replace('href="#src-2"', 'href="#src-02"', 1),
    'casefold_source_url': lambda s: s.replace('https://example.org/a?x=1&amp;y=2', 'https://EXAMPLE.org/a?x=1&amp;y=2', 1),
    'malformed_source_order': lambda s: s.replace('id="src-2"', 'id="src-01"', 1),
    'source_href_javascript': lambda s: s.replace('href="https://example.edu/b"', 'href="javascript:alert(1)"', 1),
    'source_href_http': lambda s: s.replace('href="https://example.edu/b"', 'href="http://example.edu/b"', 1),
    'source_href_redirect': lambda s: s.replace('href="https://example.edu/b"', 'href="https://example.org/go?to=https://example.edu/b"', 1),
    'source_malformed_html': lambda s: s.replace('</li></ol></section>', '</p></ol></section>', 1),
    'nested_sources': lambda s: s.replace('<section class="pa-sources">', '<section class="pa-sources"><section class="pa-sources"></section>', 1),
    'nested_body': lambda s: s.replace('<div class="pa-body" id="pa-main">', '<div class="pa-body" id="pa-main"><div id="pa-main"></div>', 1),
    'source_id_doubled_suffix': lambda s: s.replace('id="src-2"', 'id="src-2 src-2"', 1),
    'citation_class_removed': lambda s: s.replace('class="pa-cite"', 'class="not-a-cite"', 1),
    'citation_wrong_source_title': lambda s: s.replace('Source 2: Second Study', 'Source 2: First &amp; Primary', 1),
    'source_title_case_changed': lambda s: s.replace('>First &amp; Primary</a>', '>first &amp; primary</a>', 1),
    'source_link_missing': lambda s: s.replace('<a href="https://example.edu/b" rel="noopener">Second Study</a>', 'Second Study', 1),
    'source_injection_extra_verification': lambda s: s.replace('Human source-link check pending', 'Human source-link check pending Human source-link check complete', 1),
}


def _make_mutation_test(name, mutation):
    def test(self):
        with self.assertRaises(gate.RenderCitationFailure, msg=name):
            run(mod=mutation)
    test.__name__ = 'test_mutation_' + name
    return test


for mutation_name, mutation_fn in MUTATIONS.items():
    setattr(RenderedCitationsTests, 'test_mutation_' + mutation_name,
            _make_mutation_test(mutation_name, mutation_fn))


if __name__ == '__main__':
    unittest.main(verbosity=2)
