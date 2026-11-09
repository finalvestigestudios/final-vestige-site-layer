"""R234 read-only synthetic auxiliary surface tests; no corpus/WordPress writes."""
from __future__ import annotations

from html import escape
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r234_auxiliary_draft_exposure_hold as gate


def card(route, title, section='start-here', track='modern'):
    return (f'<li class="pa-card" data-section="{section}" data-track="{track}" '
            f'data-verify="pending"><h3><a href="{route}">{escape(title)}</a></h3>'
            '<p class="pa-card-meta"><span>5 min read</span><span>Draft</span></p></li>')


def pages(cards):
    text = '<main><a href="/editorial-standards/">Standards</a><ul>' + cards + '</ul></main>'
    return {'wp': '<!-- wp:html -->\n' + text + '\n<!-- /wp:html -->',
            'preview': '<!doctype html><html><head><meta name="robots" content="noindex,nofollow"></head><body>' + text + '</body></html>'}


ROUTES = {'/preparedness/start-here/one/': {'title': 'Make a plan', 'section': 'start-here', 'track': 'modern'},
          '/preparedness/water/two/': {'title': 'Water & safety', 'section': 'water', 'track': 'modern'},
          '/preparedness/lost-ways/three/': {'title': 'Historical food', 'section': 'lost-ways', 'track': 'lost-ways'}}


def valid_cards():
    return ''.join(card(route, r['title'], r['section'], r['track']) for route, r in ROUTES.items())


class AuxiliaryMarkupTests(unittest.TestCase):
    def check(self, cards=None, *, preview=False, pre='', post='', edit=None):
        contents = pages(valid_cards() if cards is None else cards)['preview' if preview else 'wp']
        if edit:
            contents = edit(contents)
        return gate.verify_page(pre + contents + post, ROUTES, preview=preview)

    def test_wp_positive_is_hold_only(self):
        r = self.check()
        self.assertEqual(r['draft_cards'], 3)
        self.assertEqual(r['state'], gate.HOLD)
        self.assertIs(r['release_authorized'], False)
        self.assertIs(r['commercial_approval'], False)
        self.assertIs(r['independent_qd_pass'], False)

    def test_preview_positive_is_noindex_and_hold(self):
        self.assertEqual(self.check(preview=True)['draft_cards'], 3)

    def test_html_entity_title_preserves_real_text(self):
        self.assertIn('Water &amp; safety', valid_cards())
        self.check()

    def test_preview_missing_noindex_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'noindex'):
            self.check(preview=True, edit=lambda s: s.replace('noindex,nofollow', 'index,follow'))

    def test_invalid_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'invalid page'):
            gate.verify_page('', {}, preview=False)

    def test_extra_duplicate_article_card_rejected(self):
        with self.assertRaisesRegex(ValueError, 'missing/duplicate'):
            self.check(cards=valid_cards() + card('/preparedness/start-here/one/', 'Make a plan'))

    def test_missing_article_card_rejected(self):
        with self.assertRaisesRegex(ValueError, 'missing/duplicate'):
            self.check(cards=valid_cards().replace(card('/preparedness/water/two/', 'Water & safety', 'water'), ''))

    def test_heading_link_text_drift_rejected(self):
        with self.assertRaisesRegex(ValueError, 'title/track drift'):
            self.check(edit=lambda s: s.replace('Make a plan</a>', 'Get rich quick</a>'))

    def test_outbound_link_outside_card_rejected(self):
        with self.assertRaisesRegex(ValueError, 'outbound'):
            self.check(post='<a href="https://payhip.com/b/unknown">Buy now</a>')

    def test_submit_form_rejected(self):
        with self.assertRaisesRegex(ValueError, 'submitting'):
            self.check(post='<form action="https://example.org" method="post"></form>')

    def test_inline_search_form_does_not_trigger(self):
        self.check(post='<form onsubmit="return false"><input type="search"></form>')

    def test_external_script_rejected(self):
        with self.assertRaisesRegex(ValueError, 'script'):
            self.check(post='<script src="https://example.com/analytics.js"></script>')

    def test_nested_unapproved_iframe_rejected(self):
        with self.assertRaisesRegex(ValueError, 'iframe'):
            self.check(post='<iframe src="https://example.org"></iframe>')

    def test_hidden_parent_card_rejected(self):
        with self.assertRaisesRegex(ValueError, 'concealed'):
            self.check(pre='<div style="display:none">', post='</div>')

    def test_hidden_title_link_rejected(self):
        with self.assertRaisesRegex(ValueError, 'card anchor'):
            self.check(edit=lambda s:s.replace('<h3><a href=', '<h3><a hidden href=', 1))

    def test_hidden_draft_badge_rejected(self):
        with self.assertRaisesRegex(ValueError, 'concealed draft'):
            self.check(edit=lambda s:s.replace('<span>Draft</span>', '<span hidden>Draft</span>', 1))

    def test_absent_draft_badge_rejected(self):
        with self.assertRaisesRegex(ValueError, 'draft badge'):
            self.check(edit=lambda s:s.replace('<span>Draft</span>', '<span>Live!</span>', 1))

    def test_duplicate_html_attribute_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate HTML attribute'):
            self.check(edit=lambda s:s.replace('data-verify="pending"', 'data-verify="pending" data-verify="approved"', 1))

    def test_data_track_swap_rejected(self):
        with self.assertRaisesRegex(ValueError, 'title/track drift'):
            self.check(edit=lambda s:s.replace('data-track="modern"', 'data-track="lost-ways"', 1))

    def test_duplicate_card_link_inside_heading_rejected(self):
        with self.assertRaisesRegex(ValueError, 'card title link count'):
            self.check(edit=lambda s:s.replace('</h3>', '<a href="/preparedness/water/two/">extra</a></h3>', 1))


class FakeLibrary:
    def __init__(self):
        self.articles = {}
        self.taxonomy = {'sections': [{'slug':'start-here'}, {'slug':'water'}, {'slug':'lost-ways'}, {'slug':'empty'}]}
        for i in range(41):
            section = ['start-here', 'water', 'lost-ways'][i % 3]
            self.articles[f'draft-{i:02d}'] = {'section':section,'track':'modern' if i % 3 != 2 else 'lost-ways',
                                              'title':f'Article {i:02d}', 'status': {'publish':'draft'}}

    def url_path(self, slug):
        return f'/preparedness/{self.articles[slug]["section"]}/{slug}/'


class FakeTokenizer:
    def verify_tokenizer_states(self, text):
        return {'state': 'DRAFT_HARD_HOLD', 'release_authorized': False}


def safe_read(root, rel):
    return (root / rel).read_bytes()


class FullAuxiliaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fv-r234-')
        self.root = Path(self.temp.name)
        self.lib = FakeLibrary()
        self.tokenizer = FakeTokenizer()
        for mode in ('wp','preview'):
            out = self.root / 'build' / mode
            out.mkdir(parents=True)
            all_items = list(self.lib.articles)
            self.render(out, mode, 'landing', all_items)
            for section in ('start-here', 'water', 'lost-ways'):
                self.render(out, mode, 'hub-' + section, [s for s in all_items if self.lib.articles[s]['section']==section])

    def render(self, out, mode, name, slugs):
        markup = ''.join(card(self.lib.url_path(s),self.lib.articles[s]['title'],self.lib.articles[s]['section'],self.lib.articles[s]['track']) for s in slugs)
        (out / f'{name}.html').write_text(pages(markup)[mode], encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def check(self):
        return gate.verify_auxiliary_drafts(self.root,self.lib,self.tokenizer,safe_read)

    def test_all_41_routes_across_eight_surfaces(self):
        r=self.check()
        self.assertEqual(r['auxiliary_files_verified'],8)
        self.assertEqual(r['distinct_frozen_routes'],41)
        self.assertEqual(r['card_instances_verified'],164)
        self.assertEqual(r['state'], gate.HOLD)
        self.assertIs(r['source_or_medical_safety_approved'], False)

    def test_missing_hub_file_fails(self):
        (self.root/'build/wp/hub-water.html').unlink()
        with self.assertRaises(FileNotFoundError): self.check()

    def test_unapproved_published_status_fails(self):
        self.lib.articles['draft-00']['status']['publish']='published'
        with self.assertRaisesRegex(ValueError, 'unapproved publication'): self.check()

    def test_duplicate_frozen_route_fails(self):
        old=self.lib.url_path
        self.lib.url_path=lambda slug: '/preparedness/collision/'
        with self.assertRaisesRegex(ValueError, 'duplicate frozen route'): self.check()
        self.lib.url_path=old

    def test_non_corpus_article_count_fails(self):
        self.lib.articles.pop('draft-01')
        with self.assertRaisesRegex(ValueError, '35 articles'): self.check()

    def test_unknown_section_fails(self):
        self.lib.articles['draft-00']['section']='missing'
        with self.assertRaisesRegex(ValueError, 'unknown section'): self.check()

    def test_tokenizer_failure_fails(self):
        self.tokenizer.verify_tokenizer_states=lambda _: {'state':'INVALID_HARD_HOLD','release_authorized':False}
        with self.assertRaisesRegex(ValueError, 'tokenizer safety'): self.check()

    def test_removed_landing_cards_fail(self):
        p=self.root/'build/preview/landing.html'
        p.write_text(p.read_text().replace('data-verify="pending"','data-verify="approved"',1))
        with self.assertRaisesRegex(ValueError, 'false independent verification'): self.check()

    def test_outbound_affiliate_on_landing_fails(self):
        p=self.root/'build/preview/landing.html'
        p.write_text(p.read_text()+'<a href="https://www.awin1.com/cread.php">affiliate</a>')
        with self.assertRaisesRegex(ValueError, 'outbound'): self.check()


def mutated_badge(index):
    def run(self):
        p=self.root/'build/wp/landing.html'
        old=f'/preparedness/{self.lib.articles[f"draft-{index:02d}"]["section"]}/draft-{index:02d}/'
        text=p.read_text().replace(old, f'/preparedness/bad-route-{index}/',1)
        p.write_text(text)
        with self.assertRaisesRegex(ValueError, 'duplicate/foreign draft route'): self.check()
    return run


for n in range(41):
    setattr(FullAuxiliaryTests, f'test_canonical_draft_card_mutation_{n:02d}_fails', mutated_badge(n))

if __name__=='__main__':
    unittest.main()
