"""Standalone adversarial cases for review-only packet; fixture custody is NEVER a QD PASS."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import re
import sys
import types
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
# Local synthetic tests can run without a whole repository. In the exact Git checkout
# the genuine parent r133_snapshot_gate module is imported, not this fallback stub.
try:
    import r133_snapshot_gate
except ModuleNotFoundError:
    stub = types.ModuleType('r133_snapshot_gate')
    stub.CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
    class IntegrityHold(ValueError):
        pass
    stub.IntegrityHold = IntegrityHold
    stub.audit = lambda *args: (_ for _ in ()).throw(IntegrityHold('NEEDS_REAL_CUSTODY'))
    import json
    stub.load_json = lambda b: json.loads(b.decode('utf-8'))
    sys.modules['r133_snapshot_gate'] = stub

from r134_reviewer_packet import segments, resolve_author_source, review_article, plain, citation_ids, IntegrityHold, packet

SLUGS = [
    'emergency-hygiene-sanitation', 'family-communication-plan', 'fire-making-across-time',
    'food-safety-power-outage', 'go-bags', 'history-of-food-preservation',
    'home-fire-escape-plan', 'homemade-water-filters', 'household-emergency-plan',
    'lewis-and-clark-salt-works', 'making-water-safer', 'medication-and-devices',
    'navigation-before-gps', 'outage-heat-cold-generators', 'pantry-rotation',
    'pemmican-and-dried-meats', 'pickling-fermentation-old-recipes',
    'pioneer-supply-chains-failed', 'pioneer-travel-rations',
    'preparedness-real-households', 'pressure-canning-low-acid',
    'rain-barrels-and-cisterns', 'root-cellars-cool-storage',
    'safe-jerky-dehydration', 'salt-beef-salt-pork-age-of-sail',
    'sanitation-before-germ-theory', 'shelter-or-evacuate',
    'ships-biscuit-and-hardtack', 'smokehouses-salting-curing',
    'three-day-kit', 'two-week-water-storage', 'warnings-radios-offline-maps',
    'water-advisories-explained', 'water-math', 'water-purification-through-history'
]


def data():
    src = lambda id, url, supports: {'id': id, 'url': url, 'supports': supports,
                                    'publisher': 'Agency', 'verified_on': '2026-11-03',
                                    'human_link_check': False}
    return {'base': {'a': src('a', 'https://agency.gov/a', 'base-support'),
                     'b': src('b', 'https://agency.gov/b', 'base-support-b')},
            'food': {'a': src('a', 'https://agency.gov/a/', 'author-scope'),
                     'c': src('c', 'https://agency.gov/c', 'author-c')},
            'health': {}}


def metadata(ids=('a',), state='pending'):
    return {'source_use': {id: f'Author actually read portion of {id}' for id in ids},
            'safety_review': {'state': state}, 'status': {'publish': 'draft'}}


class TestArticleRoster(unittest.TestCase):
    """35 independent synthetic article paths are preserved with their precise author scopes."""


def make_test(slug):
    def test(self):
        body = '<section><p>Water boiling guidance {{cite:a}}</p><p>History only.</p></section>'
        doc = review_article(slug, body, metadata(), 'food', data(), {('food','a','https://agency.gov/a/'): 32})
        self.assertEqual(doc['slug'], slug)
        self.assertEqual(doc['citation_occurrences'], 1)
        self.assertEqual(doc['publication_state'], 'draft')
        self.assertEqual(doc['blocks_for_human_review'][0]['bindings'][0]['source_origin'], 'food')
        self.assertTrue(doc['blocks_for_human_review'][0]['bindings'][0]['author_shadows_different_base_source'])
    return test

for _s in SLUGS:
    setattr(TestArticleRoster, 'test_exact_synthetic_article_' + _s.replace('-', '_'), make_test(_s))


class TestAdversarialCases(unittest.TestCase):
    def test_roster_count(self): self.assertEqual(len(SLUGS), 35)
    def test_unique_roster(self): self.assertEqual(len(set(SLUGS)), 35)
    def test_simple_segments(self): self.assertEqual(segments('<p>First</p><p>Second</p>'), ['First', 'Second'])
    def test_nested_markup(self): self.assertEqual(segments('<p>Fo<strong>od</strong> {{cite:a}}</p>'), ['Fo od {{cite:a}}'])
    def test_html_comments_ignored(self): self.assertEqual(segments('<!-- {{cite:b}} --><p>{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_script_ignored(self): self.assertEqual(segments('<script>{{cite:b}}</script><p>{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_style_ignored(self): self.assertEqual(segments('<style>{{cite:b}}</style><p>{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_template_ignored(self): self.assertEqual(segments('<template>{{cite:b}}</template><p>{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_noscript_ignored(self): self.assertEqual(segments('<noscript>{{cite:b}}</noscript><p>{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_hidden_ignored(self): self.assertEqual(segments('<p hidden>{{cite:b}}</p><p>{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_inert_ignored(self): self.assertEqual(segments('<div inert>{{cite:b}}</div><p>{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_aria_hidden_ignored(self): self.assertEqual(segments('<div aria-hidden="true">{{cite:b}}</div><p>{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_inline_display_none_ignored(self): self.assertEqual(segments('<span style="display : none">{{cite:b}}</span><p>{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_inline_visibility_hidden_ignored(self): self.assertEqual(segments('<span style="visibility: hidden">{{cite:b}}</span><p>{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_attribute_citation_ignored(self): self.assertEqual(segments('<p title="{{cite:b}}">{{cite:a}}</p>'), ['{{cite:a}}'])
    def test_citation_occurrences_preserved(self): self.assertEqual(citation_ids('{{cite:a}} {{cite:a}}'), ['a','a'])
    def test_plain_removes_link_token(self): self.assertEqual(plain('Hello {{link:target|Label}} world.'),'Hello world.')
    def test_author_precedence(self): self.assertEqual(resolve_author_source('food','a',data())[0], 'food')
    def test_base_fallback(self): self.assertEqual(resolve_author_source('health','a',data())[0], 'base')
    def test_same_id_shadow_does_not_merge(self): self.assertTrue(resolve_author_source('food','a',data())[2])
    def test_unknown_source_fail_closed(self):
        with self.assertRaises(IntegrityHold): resolve_author_source('health','missing',data())
    def test_nonexistent_source_from_body_fails(self):
        with self.assertRaises(IntegrityHold): review_article('a','<p>{{cite:missing}}</p>',metadata(('missing',)),'food',data(),{})
    def test_orphan_author_scope_rejected(self):
        with self.assertRaises(IntegrityHold): review_article('a','<p>{{cite:a}}</p>',metadata(('a','b')),'base',data(),{})
    def test_missing_scope_rejected(self):
        with self.assertRaises(IntegrityHold): review_article('a','<p>{{cite:a}}{{cite:b}}</p>',metadata(),'base',data(),{})
    def test_citation_hidden_fails(self):
        with self.assertRaises(IntegrityHold): review_article('a','<p>{{cite:a}}</p><div hidden>{{cite:a}}</div>',metadata(),'base',data(),{})
    def test_citation_attribute_fails(self):
        with self.assertRaises(IntegrityHold): review_article('a','<p data-ref="{{cite:a}}">No visible source</p>',metadata(),'base',data(),{})
    def test_no_keyword_no_cite_omitted(self):
        self.assertEqual(review_article('a','<p>Plain history.</p>',metadata(()),'base',data(),{})['blocks_for_human_review'],[])
    def test_risk_no_inline_cite_flag(self):
        r=review_article('a','<p>Always check medication instructions.</p>',metadata(()),'base',data(),{})
        self.assertEqual(r['keyword_flagged_without_inline_citation'],1)
    def test_risk_with_inline_cite_no_flag(self):
        r=review_article('a','<p>Use a generator only as directed {{cite:a}}</p>',metadata(),'base',data(),{})
        self.assertEqual(r['keyword_flagged_without_inline_citation'],0)
    def test_keyword_not_safety_approval(self):
        r=review_article('a','<p>Generator {{cite:a}}</p>',metadata(),'base',data(),{})
        self.assertEqual(r['safety_review_state_historical_only'],'pending')
    def test_same_source_multiple_citation_occurrences(self):
        r=review_article('a','<p>Food {{cite:a}} and temperatures {{cite:a}}</p>',metadata(),'base',data(),{})
        self.assertEqual(r['citation_occurrences'],2)
    def test_binding_scope_value_retained(self):
        r=review_article('a','<p>Boil {{cite:a}}</p>',metadata(),'base',data(),{})
        self.assertEqual(r['blocks_for_human_review'][0]['bindings'][0]['author_reading_scope'],metadata()['source_use']['a'])
    def test_binding_url_retained(self):
        r=review_article('a','<p>Boil {{cite:a}}</p>',metadata(),'base',data(),{})
        self.assertEqual(r['blocks_for_human_review'][0]['bindings'][0]['source_url'],'https://agency.gov/a')
    def test_binding_human_not_checked(self):
        r=review_article('a','<p>Boil {{cite:a}}</p>',metadata(),'base',data(),{})
        self.assertFalse(r['blocks_for_human_review'][0]['bindings'][0]['human_link_check'])
    def test_binding_crosswalk(self):
        r=review_article('a','<p>Boil {{cite:a}}</p>',metadata(),'base',data(),{('base','a','https://agency.gov/a'): 9})
        self.assertEqual(r['blocks_for_human_review'][0]['bindings'][0]['shared_source_group'],9)
    def test_long_excerpt_clamped(self):
        r=review_article('a','<p>Generator '+'x'*500+' {{cite:a}}</p>',metadata(),'base',data(),{})
        self.assertLessEqual(len(r['blocks_for_human_review'][0]['excerpt']),220)
    def test_no_output_without_custody(self):
        with self.assertRaises((IntegrityHold, FileNotFoundError)):
            packet(Path('/tmp/r134-no-trusted-candidate'), {'may_publish':False})

if __name__ == '__main__': unittest.main()
