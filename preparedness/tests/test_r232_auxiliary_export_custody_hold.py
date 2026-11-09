"""R232 offline, non-publishing synthetic tests (no real corpus edits)."""
from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r232_auxiliary_export_custody_hold as gate


class FakeLibrary:
    def __init__(self):
        self.articles = {f'article-{i}': {'slug': f'article-{i}'} for i in range(1, 36)}
        self.articles.update({f'tool-{i}': {'slug': f'tool-{i}'} for i in range(1, 7)})
        self.taxonomy = {'sections': [{'slug': 'family-communication'}, {'slug': 'food'},
                                      {'slug': 'not-populated'}]}


class FakeBuilder:
    @staticmethod
    def build_hub(lib, section, include_drafts=True):
        if not include_drafts:
            raise ValueError('draft content must not be filtered from offline custody')
        if section == 'not-populated':
            return None
        count = 21 if section == 'food' else 20
        return {'slug': 'hub-' + section, 'count': count, 'inner': '<section>' + section + '</section>',
                'title': section + ' | The Preparedness Archive', 'description': 'Synthetic hub'}

    @staticmethod
    def build_landing(lib, include_drafts=True):
        if not include_drafts:
            raise ValueError('draft content must not be filtered from offline custody')
        return {'slug': 'landing', 'inner': '<main>Archive, draft only</main>',
                'populated_sections': ['family-communication', 'food'], 'article_cards': 41}

    @staticmethod
    def wp_wrap(lib, inner):
        return '<!-- wp:html -->\n' + inner + '\n<!-- /wp:html -->\n'

    @staticmethod
    def preview_wrap(lib, inner, title, description):
        return '<!doctype html><title>' + title + '</title><p>' + description + '</p>' + inner


def safe_read(root, path):
    p = root
    for part in Path(path).parts:
        if p.is_symlink():
            raise ValueError('linked path')
        p = p / part
    if p.is_symlink() or not p.is_file():
        raise ValueError('linked/missing file')
    return p.read_bytes()


class SyntheticAuxiliaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='fv-r232-synthetic-')
        self.root = Path(self.tmp.name)
        self.lib = FakeLibrary()
        self.builder = FakeBuilder
        self.report = {'articles': [{'slug': s} for s in self.lib.articles],
                       'hubs': [{'section': 'family-communication', 'guides': 20},
                                {'section': 'food', 'guides': 21}],
                       'landing': {'populated_sections': ['family-communication', 'food'],
                                   'article_cards': 41}}
        for mode in ('wp', 'preview'):
            p = self.root / 'build' / mode
            p.mkdir(parents=True)
            for slug in self.lib.articles:
                (p / f'{slug}.html').write_text('AUTHENTIC ARTICLE PLACEHOLDER', encoding='utf-8')
            for sid in ('family-communication', 'food'):
                hub = self.builder.build_hub(self.lib, sid)
                page = (self.builder.wp_wrap(self.lib, hub['inner']) if mode == 'wp'
                        else self.builder.preview_wrap(self.lib, hub['inner'], hub['title'], hub['description']))
                (p / (hub['slug'] + '.html')).write_bytes(page.encode('utf-8'))
            land = self.builder.build_landing(self.lib)
            page = (self.builder.wp_wrap(self.lib, land['inner']) if mode == 'wp'
                    else self.builder.preview_wrap(self.lib, land['inner'],
                         gate.LANDING_TITLE, gate.LANDING_DESCRIPTION))
            (p / 'landing.html').write_bytes(page.encode('utf-8'))

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, report=None):
        return gate.audit_auxiliary_exports(self.root, report if report is not None else self.report,
                                            self.lib, self.builder, safe_read)

    def test_exact_positive_draft_only(self):
        result = self.check()
        self.assertEqual(result['state'], 'DRAFT_HARD_HOLD')
        self.assertIs(result['release_authorized'], False)
        self.assertIs(result['independent_qd_pass'], False)
        self.assertIs(result['commercial_approval'], False)
        self.assertIs(result['source_or_medical_safety_approved'], False)
        self.assertEqual(result['article_tool_names'], 41)
        self.assertEqual(result['hubs'], 2)
        self.assertEqual(result['auxiliary_files_verified'], 6)
        self.assertEqual(result['total_expected_html_files'], 88)

    def test_missing_hub_report(self):
        r = copy.deepcopy(self.report)
        r.pop('hubs')
        with self.assertRaisesRegex(ValueError, 'R232 hub-report'):
            self.check(r)

    def test_changed_hub_report_count(self):
        r = copy.deepcopy(self.report)
        r['hubs'][0]['guides'] = 999
        with self.assertRaisesRegex(ValueError, 'R232 hub-report'):
            self.check(r)

    def test_changed_hub_report_order(self):
        r = copy.deepcopy(self.report)
        r['hubs'].reverse()
        with self.assertRaisesRegex(ValueError, 'R232 hub-report'):
            self.check(r)

    def test_changed_landing_report_count(self):
        r = copy.deepcopy(self.report)
        r['landing']['article_cards'] += 1
        with self.assertRaisesRegex(ValueError, 'R232 landing-report'):
            self.check(r)

    def test_changed_landing_report_sections(self):
        r = copy.deepcopy(self.report)
        r['landing']['populated_sections'].reverse()
        with self.assertRaisesRegex(ValueError, 'R232 landing-report'):
            self.check(r)

    def test_missing_articles_report(self):
        r = copy.deepcopy(self.report)
        del r['articles']
        with self.assertRaisesRegex(ValueError, 'R232 missing build report'):
            self.check(r)

    def test_incorrect_article_count(self):
        self.lib.articles.pop('article-35')
        with self.assertRaisesRegex(ValueError, 'R232 exact 35'):
            self.check()

    def test_duplicate_section(self):
        self.lib.taxonomy['sections'].append({'slug': 'food'})
        with self.assertRaisesRegex(ValueError, 'R232 duplicate/unsafe section'):
            self.check()

    def test_unsafe_section(self):
        self.lib.taxonomy['sections'][0]['slug'] = '../escape'
        with self.assertRaisesRegex(ValueError, 'R232 duplicate/unsafe section'):
            self.check()

    def test_bad_article_slug(self):
        self.lib.articles['../../escape'] = self.lib.articles.pop('article-1')
        with self.assertRaisesRegex(ValueError, 'R232 invalid article/tool slug'):
            self.check()

    def test_hub_missing_producer_count(self):
        class Broken(FakeBuilder):
            @staticmethod
            def build_hub(lib, section, include_drafts=True):
                h = FakeBuilder.build_hub(lib, section, include_drafts)
                if h: h.pop('count')
                return h
        self.builder = Broken
        with self.assertRaisesRegex(ValueError, 'R232 malformed hub'):
            self.check()

    def test_landing_changed_producer_identity(self):
        class Broken(FakeBuilder):
            @staticmethod
            def build_landing(lib, include_drafts=True):
                l = FakeBuilder.build_landing(lib, include_drafts)
                l['slug'] = 'somewhere-else'
                return l
        self.builder = Broken
        with self.assertRaisesRegex(ValueError, 'R232 malformed landing'):
            self.check()

    def test_symlink_wp_directory(self):
        d = self.root / 'build' / 'wp'
        link = self.root / 'build' / 'wp-link'
        d.rename(link)
        d.symlink_to(link, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'R232 missing/symlinked output'):
            self.check()

    def test_symlink_preview_file(self):
        p = self.root / 'build' / 'preview' / 'landing.html'
        p.unlink()
        p.symlink_to(self.root / 'build' / 'wp' / 'landing.html')
        with self.assertRaisesRegex(ValueError, 'R232 unsafe generated export'):
            self.check()

    def test_unexpected_subdirectory(self):
        (self.root / 'build' / 'wp' / 'hidden').mkdir()
        with self.assertRaisesRegex(ValueError, 'R232 unsafe generated export'):
            self.check()

    def test_no_duplicate_posted_merchant(self):
        p = self.root / 'build' / 'wp' / 'landing.html'
        p.write_text(p.read_text() + '<a href="https://example.invalid/buy">Buy</a>')
        with self.assertRaisesRegex(ValueError, 'R232 auxiliary export-byte drift'):
            self.check()


def _missing_expected_export(mode, slug):
    def check(self):
        (self.root / 'build' / mode / (slug + '.html')).unlink()
        with self.assertRaisesRegex(ValueError, 'R232 output inventory drift'):
            self.check()
    return check


def _mutation(mode, slug, change):
    def check(self):
        p = self.root / 'build' / mode / (slug + '.html')
        p.write_text(p.read_text() + change)
        with self.assertRaisesRegex(ValueError, 'R232 auxiliary export-byte drift'):
            self.check()
    return check


def _unexpected(mode, extra):
    def check(self):
        (self.root / 'build' / mode / extra).write_text('stale or injected')
        with self.assertRaisesRegex(ValueError, 'R232 output inventory drift'):
            self.check()
    return check


for _mode in ('wp', 'preview'):
    for _slug in [f'article-{i}' for i in range(1, 36)] + [f'tool-{i}' for i in range(1, 7)] + [
            'landing', 'hub-food', 'hub-family-communication']:
        setattr(SyntheticAuxiliaryTests, f'test_{_mode}_{_slug.replace("-", "_")}_missing_hold',
                _missing_expected_export(_mode, _slug))
    for _slug in ('landing', 'hub-food', 'hub-family-communication'):
        for _kind, _payload in [
                ('tracking', '<script src="https://example.invalid/track.js"></script>'),
                ('merchant', '<a href="https://example.invalid/checkout">Pay</a>'),
                ('hidden', '<style>.pa-sources{display:none}</style>'),
                ('robots', '<meta name="robots" content="index,follow">')]:
            setattr(SyntheticAuxiliaryTests,
                    f'test_{_mode}_{_slug.replace("-", "_")}_{_kind}_hold',
                    _mutation(_mode, _slug, _payload))
    for _name in ('stale.html', 'extra-offer.html', 'index.php', '.htaccess',
                  'not-approved-redirect.html'):
        setattr(SyntheticAuxiliaryTests, f'test_{_mode}_{_name.replace(".", "_").replace("-", "_")}_extra_hold',
                _unexpected(_mode, _name))

if __name__ == '__main__':
    unittest.main()
