"""R455: synthetic adversarial renderer parity; NOT genuine 35-article export QA."""
from __future__ import annotations

from html import escape
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from r455_rendered_citation_parity import CitationParityError, verify_pair, authored_order

SOURCES = {
    'ready-plan': {'url': 'https://www.ready.gov/plan', 'title': 'Make A Plan',
                   'publisher': 'FEMA / Ready.gov', 'supports': 'Four planning steps; original full reading scope.'},
    'ready-alt': {'url': 'https://www.ready.gov/plan', 'title': 'Household Guide',
                  'publisher': 'Independent contributor', 'supports': 'Second source reading scope, not merged.'},
}
BODY = '<h2>Contacts</h2><p>First decision.{{cite:ready-plan}}</p><p>Another view.{{cite:ready-alt}}{{cite:ready-plan}}</p>'


def build(body=BODY, sources=SOURCES, use=None):
    used = authored_order(body)
    id_for = {sid: i + 1 for i, sid in enumerate(used)}
    text = body
    import re
    text = re.sub(r'\{\{cite:([a-z0-9-]+)\}\}',
        lambda m: '<sup class="pa-cite"><a href="#src-{n}" aria-label="Source {n}: {title}">[{n}]</a></sup>'.format(
            n=id_for[m.group(1)], title=escape(sources[m.group(1)]['title'], quote=True)), text)
    items = []
    for sid in used:
        n = id_for[sid]
        s = sources[sid]
        scope = (use or {}).get(sid) or s['supports']
        items.append('<li id="src-{n}"><a href="{url}" rel="noopener">{title}</a>. {pub}. '
                     '<span class="pa-src-meta">Human source-link check pending</span>'
                     '<span class="pa-src-use">Used for: {scope}</span></li>'.format(
                         n=n, url=escape(s['url'], quote=True), title=escape(s['title']),
                         pub=escape(s['publisher']), scope=escape(scope)))
    block = '<section class="pa-sources"><h2>Sources</h2><ol>' + ''.join(items) + '</ol></section>'
    return '<div class="pa">' + text + block + '</div>'


def ok(body=BODY, sources=None, wp=None, preview=None, use=None):
    src = SOURCES if sources is None else sources
    try:
        valid = build(body, src, use)
    except (KeyError, TypeError):
        if wp is None:
            raise
        valid = build()
    return verify_pair(body, src, valid if wp is None else wp,
                       valid if preview is None else preview, use)


class TestR455Parity(unittest.TestCase):
    def test_baseline(self):
        result = ok()
        self.assertEqual(result['release_state'], 'DRAFT_HARD_HOLD')
        self.assertFalse(result['qd_pass'])
        self.assertFalse(result['wordpress_published'])
        self.assertFalse(result['source_claim_support_verified'])

    def test_same_url_distinct_source_id(self):
        self.assertEqual(ok()['parity']['bibliography_entries'], 2)

    def test_repeated_citation_counts(self):
        self.assertEqual(ok()['parity']['citation_occurrences'], 3)

    def test_scope_override(self):
        self.assertTrue(ok(use={'ready-plan': 'Only four tasks were read.'})['parity']['all_id_url_scope_links_preserved'])

    def test_html_entity_title(self):
        src = {k: dict(v) for k, v in SOURCES.items()}
        src['ready-plan']['title'] = 'Plan & Prepare'
        self.assertTrue(ok(sources=src)['parity']['all_id_url_scope_links_preserved'])

    def test_only_one_source(self):
        self.assertEqual(ok(body='<p>One.{{cite:ready-plan}}</p>')['parity']['bibliography_entries'], 1)

    def test_extra_unique_source(self):
        self.assertEqual(ok(body=BODY + '<p>Repeated.{{cite:ready-alt}}</p>')['parity']['citation_occurrences'], 4)

    def test_quote_ampersand_source_url(self):
        src = {k: dict(v) for k, v in SOURCES.items()}
        src['ready-plan']['url'] = 'https://www.ready.gov/plan?x=1&y=2'
        self.assertTrue(ok(sources=src)['parity']['all_id_url_scope_links_preserved'])

    def test_hidden_previews_are_checked(self):
        valid = build()
        with self.assertRaises(CitationParityError):
            ok(preview=valid.replace('href="#src-1"', 'href="#src-2"', 1))

    def test_wordpress_previews_same_semantics(self):
        valid = build()
        self.assertTrue(ok(wp=valid, preview='<html><body>' + valid + '</body></html>')['parity']['all_id_url_scope_links_preserved'])

    def test_case_sensitive_url(self):
        src = {k: dict(v) for k, v in SOURCES.items()}
        src['ready-plan']['url'] = 'https://www.ready.gov/Plan'
        self.assertTrue(ok(sources=src)['parity']['all_id_url_scope_links_preserved'])

    def test_only_no_cross_source_global_url_merge(self):
        src = {k: dict(v) for k, v in SOURCES.items()}
        src['ready-plan']['supports'] = 'Read paragraph 1.'
        src['ready-alt']['supports'] = 'Read paragraph 2.'
        self.assertTrue(ok(sources=src)['parity']['all_id_url_scope_links_preserved'])


class TestR455FailClosed(unittest.TestCase):
    def bad(self, wp=None, preview=None, body=BODY, sources=None, use=None):
        with self.assertRaises(CitationParityError):
            ok(wp=wp, preview=preview, body=body, sources=sources, use=use)

    def test_no_citation(self): self.bad(body='<p>None.</p>', wp=build())
    def test_invalid_placeholder(self): self.bad(body=BODY + '{{ cite:ready-plan }}', wp=build())
    def test_missing_source_id(self): self.bad(body=BODY.replace('ready-plan', 'not-present'), wp=build())
    def test_unused_override(self): self.bad(use={'unused': 'scope'})
    def test_no_scope(self):
        s = {k: dict(v) for k, v in SOURCES.items()}; s['ready-plan']['supports'] = ''
        self.bad(sources=s, wp=build())
    def test_http_url_rejected(self):
        s = {k: dict(v) for k, v in SOURCES.items()}; s['ready-plan']['url'] = 'http://www.ready.gov/plan'
        self.bad(sources=s, wp=build())
    def test_bad_source_record(self):
        s = dict(SOURCES); s['ready-plan'] = {}
        self.bad(sources=s, wp=build())
    def test_null_source_record(self):
        s = dict(SOURCES); s['ready-plan'] = None
        self.bad(sources=s, wp=build())
    def test_empty_body(self): self.bad(body='', wp=build())
    def test_missing_source_section(self): self.bad(wp=build().replace('pa-sources', 'plain'))
    def test_missing_source_entry(self): self.bad(wp=build().replace('id="src-2"', 'id="not-source"'))
    def test_missing_sup(self): self.bad(wp=build().replace('class="pa-cite"', 'class="plain"', 1))
    def test_missing_anchor(self): self.bad(wp=build().replace('href="#src-1"', 'href=""', 1))
    def test_moved_citation_source(self): self.bad(wp=build().replace('href="#src-1"', 'href="#src-2"', 1))
    def test_citation_number_wrong(self): self.bad(wp=build().replace('>[1]</a>', '>[2]</a>', 1))
    def test_citation_aria_wrong(self): self.bad(wp=build().replace('Source 1:', 'Source 9:', 1))
    def test_citation_missing_aria(self): self.bad(wp=build().replace('aria-label="Source 1: Make A Plan"', '', 1))
    def test_source_url_reassignment(self): self.bad(wp=build().replace('href="https://www.ready.gov/plan"', 'href="https://fake.invalid/plan"', 1))
    def test_source_url_changed_slash(self): self.bad(wp=build().replace('href="https://www.ready.gov/plan"', 'href="https://www.ready.gov/plan/"', 1))
    def test_source_url_changed_case(self): self.bad(wp=build().replace('href="https://www.ready.gov/plan"', 'href="https://www.ready.gov/PLAN"', 1))
    def test_duplicate_source_id_entry(self): self.bad(wp=build().replace('id="src-2"', 'id="src-1"', 1))
    def test_bibliography_title_changed(self): self.bad(wp=build().replace('>Household Guide</a>', '>Different title</a>', 1))
    def test_publisher_deleted(self): self.bad(wp=build().replace('Independent contributor', 'Other party', 1))
    def test_used_for_scope_shortened(self): self.bad(wp=build().replace('Second source reading scope, not merged.', 'Second source reading scope.'))
    def test_scope_removed(self): self.bad(wp=build().replace('Used for: ', 'Notes: '))
    def test_status_not_reader_visible(self): self.bad(wp=build().replace('Human source-link check pending', 'Machine complete'))
    def test_source_rel_noopener_missing(self): self.bad(wp=build().replace('rel="noopener"', 'rel="external"', 1))
    def test_hidden_sup(self): self.bad(wp=build().replace('<sup class="pa-cite">', '<sup class="pa-cite" hidden>', 1))
    def test_inert_sup(self): self.bad(wp=build().replace('<sup class="pa-cite">', '<sup class="pa-cite" inert>', 1))
    def test_aria_hidden_sup(self): self.bad(wp=build().replace('<sup class="pa-cite">', '<sup class="pa-cite" aria-hidden="true">', 1))
    def test_style_hide_sup(self): self.bad(wp=build().replace('<sup class="pa-cite">', '<sup class="pa-cite" style="display: none">', 1))
    def test_style_opacity_sup(self): self.bad(wp=build().replace('<sup class="pa-cite">', '<sup class="pa-cite" style="opacity: 0">', 1))
    def test_style_hide_ref(self): self.bad(wp=build().replace('href="#src-1"', 'href="#src-1" style="visibility:hidden"', 1))
    def test_hidden_source(self): self.bad(wp=build().replace('<li id="src-1">', '<li id="src-1" hidden>', 1))
    def test_aria_hidden_source(self): self.bad(wp=build().replace('<li id="src-1">', '<li id="src-1" aria-hidden="true">', 1))
    def test_hidden_parent(self): self.bad(wp=build().replace('<div class="pa">', '<div class="pa" hidden>', 1))
    def test_duplicate_sources_section(self): self.bad(wp=build() + build())
    def test_duplicate_attribute(self): self.bad(wp=build().replace('class="pa-cite"', 'class="pa-cite" class="other"', 1))
    def test_invalid_type_body(self):
        with self.assertRaises(CitationParityError): verify_pair(None, SOURCES, build(), build())
    def test_oversized_body(self): self.bad(body=BODY+' ' * 5_000_001, wp=build())
    def test_preview_missing_scope(self): self.bad(preview=build().replace('Second source reading scope, not merged.', ''))
    def test_preview_misnumbered(self): self.bad(preview=build().replace('href="#src-1"', 'href="#src-3"', 1))
    def test_scope_override_lost(self): self.bad(wp=build(), use={'ready-plan': 'A narrower scope not in the rendered body.'})


# Deliberately distinct, discoverable adversarial test methods (36+ required).
# Each mutation is checked independently against the exact implementation.
MUTATIONS = {
    'src_anchor_1': ('id="src-1"', 'id="src-99"'),
    'src_anchor_2': ('id="src-2"', 'id="src-99"'),
    'ref_anchor_1': ('href="#src-1"', 'href="#src-10"'),
    'ref_anchor_2': ('href="#src-2"', 'href="#src-10"'),
    'source_http': ('href="https://www.ready.gov/plan"', 'href="http://www.ready.gov/plan"'),
    'source_fragment': ('href="https://www.ready.gov/plan"', 'href="https://www.ready.gov/plan#x"'),
    'source_query': ('href="https://www.ready.gov/plan"', 'href="https://www.ready.gov/plan?ref=1"'),
    'missing_title': ('>Make A Plan</a>', '></a>'),
    'hidden_cite_ancestor': ('<div class="pa">', '<div class="pa" style="display:none">'),
    'inert_cite_ancestor': ('<div class="pa">', '<div class="pa" inert>'),
    'aria_hide_cite_ancestor': ('<div class="pa">', '<div class="pa" aria-hidden="true">'),
    'source_link_inert': ('href="https://www.ready.gov/plan"', 'href="https://www.ready.gov/plan" inert'),
    'source_link_hidden': ('href="https://www.ready.gov/plan"', 'href="https://www.ready.gov/plan" hidden'),
    'citation_link_hidden': ('href="#src-1"', 'href="#src-1" aria-hidden="true"'),
    'source_title_changed': ('>Make A Plan</a>', '>Make a plan (paraphrase)</a>'),
    'source_publisher_changed': ('FEMA / Ready.gov', 'Unknown Publisher'),
    'source_scope_changed': ('Four planning steps; original full reading scope.', 'Four planning steps'),
    'source_scope_removed': ('Four planning steps; original full reading scope.', ''),
    'source_verification_removed': ('Human source-link check pending', ''),
    'source_verification_fabricated': ('Human source-link check pending', 'Checked by AI'),
}


def make_mutation(name, old, new):
    def test(self):
        rendered = build()
        assert old in rendered, name
        with self.assertRaises(CitationParityError):
            ok(wp=rendered.replace(old, new, 1))
    test.__name__ = 'test_mutation_' + name
    return test

for name, (old, new) in MUTATIONS.items():
    setattr(TestR455FailClosed, 'test_mutation_' + name, make_mutation(name, old, new))


if __name__ == '__main__':
    unittest.main()
