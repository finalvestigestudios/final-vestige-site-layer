"""Isolated R11 synthetic tests. NOT a real-content evidence or safety check."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draft_export_custody as guard


class FakeLib:
    def __init__(self, root):
        self.root = Path(root)
        self.articles = {
            'water-math': self._meta('water-math', 'water', 'modern'),
            'salt-history': self._meta('salt-history', 'lost-ways', 'lost-ways'),
            'water-planner': self._meta('water-planner', 'field-tools', 'modern', kind='tool'),
        }
        self.taxonomy = {
            'slate': [{'slug': 'water-math'}, {'slug': 'salt-history'}],
            'sections': [{'slug': 'water'}, {'slug': 'lost-ways'}, {'slug': 'field-tools'}],
        }
        self.source_variants = {'A': [{'id': 's1', 'human_link_check': False}, {'id': 's2', 'human_link_check': False}],
                                'B': [{'id': 's3', 'human_link_check': None}, {'id': 's4', 'human_link_check': False}]}
        self.crosswalk_groups = {'https://example.org/a': {'review_status': 'pending'},
                                 'https://example.org/b': {'review_status': 'pending'}}

    @staticmethod
    def _meta(slug, section, track, kind='article'):
        return {'slug': slug, 'section': section, 'track': track, 'kind': kind,
                'status': {'publish': 'draft'}, 'h1': slug.title(), 'description': 'A draft testing record.'}


class FakeBuild:
    """Only the renderer interface needed to test R11's output trust boundary."""
    @staticmethod
    def build_article(lib, slug):
        meta = lib.articles[slug]
        return {'slug': slug, 'meta': meta, 'inner': f'<div class="pa pa-article" data-slug="{slug}"><h1>{meta["h1"]}</h1><p>Research, not medical advice.</p></div>',
                'words': 2200 if meta['kind'] == 'article' else 500, 'minutes': 8,
                'sources': ['s1', 's2'], 'canonical': f'https://finalvestige.com/preparedness/{meta["section"]}/{slug}/'}

    @staticmethod
    def build_hub(lib, section, include_drafts=True):
        assert include_drafts is True
        return {'slug': 'hub-' + section, 'inner': f'<div class="pa pa-hub">{section}</div>',
                'title': 'Hub ' + section, 'description': 'An unpublished hub',
                'count': sum(m['section'] == section for m in lib.articles.values())}

    @staticmethod
    def build_landing(lib, include_drafts=True):
        assert include_drafts is True
        return {'inner': '<div class="pa pa-landing">Draft index</div>',
                'populated_sections': 3, 'article_cards': len(lib.articles)}

    @staticmethod
    def wp_wrap(lib, inner):
        return '<!-- wp:html -->\n<style>.pa {padding:1rem}</style>\n' + inner + '\n<!-- /wp:html -->\n'

    @staticmethod
    def preview_wrap(lib, inner, title, description):
        return ('<!doctype html><html><head><meta name="robots" content="noindex,nofollow">'
                '<title>' + title + '</title><meta name="description" content="' + description + '"></head><body>' + inner + '</body></html>')

    @staticmethod
    def slate_status(lib, slug):
        return 'drafted-pending-safety-review'


class TestDraftExportCustody(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='preparedness-r11-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'preparedness'
        self.root.mkdir()
        self.lib = FakeLib(self.root)
        self.out = self.root / 'build'
        (self.out / 'wp').mkdir(parents=True)
        (self.out / 'preview').mkdir(parents=True)
        self.refresh()

    def settings(self):
        return {'expected_articles': 2, 'expected_tools': 1, 'expected_source_rows': 4,
                'expected_shared_groups': 2, 'expected_human_links': 0}

    def audit(self, **extra):
        return guard.audit_export(self.lib, self.out, FakeBuild, **(self.settings() | extra))

    def refresh(self):
        built = [FakeBuild.build_article(self.lib, slug) for slug in self.lib.articles]
        hubs = []
        for sec in [s['slug'] for s in self.lib.taxonomy['sections']]:
            hub = FakeBuild.build_hub(self.lib, sec, include_drafts=True)
            hubs.append({'section': sec, 'guides': hub['count']})
        landing = FakeBuild.build_landing(self.lib, include_drafts=True)
        output = [(item['slug'], item['inner'], f'{item["meta"]["h1"]} | The Preparedness Archive',
                   item['meta']['description']) for item in built]
        output += [(x['slug'], x['inner'], x['title'], x['description'])
                   for x in (FakeBuild.build_hub(self.lib, s['slug'], include_drafts=True) for s in self.lib.taxonomy['sections'])]
        output += [('landing', landing['inner'], 'The Preparedness Archive | Final Vestige',
                    'Evidence-based household preparedness and a historical record of how earlier generations managed without modern infrastructure.')]
        for slug, inner, title, description in output:
            (self.out / 'wp' / (slug + '.html')).write_text(FakeBuild.wp_wrap(self.lib, inner), encoding='utf-8')
            (self.out / 'preview' / (slug + '.html')).write_text(FakeBuild.preview_wrap(self.lib, inner, title, description), encoding='utf-8')
        report = guard._expected_report(self.lib, FakeBuild, built, hubs, landing)
        (self.out / 'build-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        return report

    def change_report(self, operation):
        path = self.out / 'build-report.json'
        content = json.loads(path.read_text(encoding='utf-8'))
        operation(content)
        path.write_text(json.dumps(content), encoding='utf-8')

    def test_valid_full_draft_bundle_and_digest_reproducible(self):
        a, b = self.audit(), self.audit()
        self.assertEqual(a, b)
        self.assertEqual(a['release_state'], 'HOLD')
        self.assertFalse(a['may_publish'])
        self.assertEqual(a['article_drafts'], 2)
        self.assertEqual(a['word_press_draft_artifacts'], 7)
        self.assertEqual(a['preview_artifacts'], 7)
        self.assertEqual(len(a['artifacts']), 7)
        self.assertTrue(a['does_not_write_to_wordpress'])

    def test_accept_current_matching_canonical_receipt(self):
        result = self.audit(canonical_receipt={'release_state': 'HOLD', 'may_publish': False,
                           'independent_human_source_checks_verified': 0, 'qualified_safety_approvals': 0,
                           'editorial': {'draft_items': 3}, 'sources': {'physical_source_records': 4}})
        self.assertEqual(result['release_state'], 'HOLD')

    def test_rewrite_matching_content_is_idempotent(self):
        first = self.audit()
        self.refresh()
        self.assertEqual(self.audit(), first)

    def test_run_is_read_only_and_no_receipt_created(self):
        before = {str(p.relative_to(self.out)): (p.stat().st_size, p.read_bytes()) for p in self.out.rglob('*') if p.is_file()}
        self.audit()
        after = {str(p.relative_to(self.out)): (p.stat().st_size, p.read_bytes()) for p in self.out.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_reject_wrong_build_root(self):
        with self.assertRaises(guard.CustodyFailure):
            guard.audit_export(self.lib, self.out / 'wp', FakeBuild, **self.settings())

    def test_reject_missing_report(self):
        (self.out / 'build-report.json').unlink()
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_missing_wp_folder(self):
        for p in (self.out / 'wp').iterdir(): p.unlink()
        (self.out / 'wp').rmdir()
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_missing_preview_folder(self):
        for p in (self.out / 'preview').iterdir(): p.unlink()
        (self.out / 'preview').rmdir()
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_symlinked_build_folder(self):
        outside = self.root / 'other'
        self.out.rename(outside)
        self.out.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_symlinked_wp_folder(self):
        other = self.out / 'other'
        (self.out / 'wp').rename(other)
        (self.out / 'wp').symlink_to(other, target_is_directory=True)
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_symlinked_preview_folder(self):
        other = self.out / 'other'
        (self.out / 'preview').rename(other)
        (self.out / 'preview').symlink_to(other, target_is_directory=True)
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_symlinked_html_file(self):
        file = self.out / 'wp' / 'water-math.html'
        target = self.out / 'alternate.html'
        target.write_bytes(file.read_bytes())
        file.unlink()
        file.symlink_to(target)
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_hardlinked_html_file(self):
        file = self.out / 'wp' / 'water-math.html'
        target = self.out / 'alternate.html'
        import os
        os.link(file, target)
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_symlinked_report(self):
        file = self.out / 'build-report.json'
        target = self.out / 'backup-report.json'
        target.write_bytes(file.read_bytes())
        file.unlink()
        file.symlink_to(target)
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_non_utf8_report(self):
        (self.out / 'build-report.json').write_bytes(b'\xff\xfe\xfa')
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_array_report(self):
        (self.out / 'build-report.json').write_text('[1,2,3]')
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_truncated_report(self):
        (self.out / 'build-report.json').write_text('{"release_evidence":')
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_oversized_report(self):
        (self.out / 'build-report.json').write_bytes(b'x' * (guard.MAX_REPORT_BYTES + 1))
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_oversized_wp_artifact(self):
        (self.out / 'wp' / 'water-math.html').write_bytes(b'x' * (guard.MAX_HTML_BYTES + 1))
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_empty_preview(self):
        (self.out / 'preview' / 'water-math.html').write_bytes(b'')
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_parent_symlink_root(self):
        original = self.root
        real = original.parent / 'actual'
        original.rename(real)
        original.symlink_to(real, target_is_directory=True)
        with self.assertRaises(guard.CustodyFailure):
            self.audit()

    def test_reject_html_content_mutation(self):
        p = self.out / 'wp' / 'water-math.html'
        p.write_text(p.read_text().replace('Research, not medical advice', 'No safety review needed'))
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_hidden_preview_mutation(self):
        p = self.out / 'preview' / 'water-math.html'
        p.write_text(p.read_text().replace('noindex,nofollow', 'index,follow'))
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_html_truncation(self):
        p = self.out / 'wp' / 'salt-history.html'
        p.write_bytes(p.read_bytes()[:-80])
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_html_duplicate(self):
        p = self.out / 'preview' / 'water-math.html'
        p.write_bytes(p.read_bytes() + p.read_bytes())
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_cross_swapped_html(self):
        a = self.out / 'wp' / 'water-math.html'
        b = self.out / 'wp' / 'salt-history.html'
        tmp = a.read_bytes()
        a.write_bytes(b.read_bytes())
        b.write_bytes(tmp)
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_changed_h1_on_source_same_old_build(self):
        self.lib.articles['water-math']['h1'] = 'Dangerously rewritten'
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_changed_description_on_source_same_old_build(self):
        self.lib.articles['water-math']['description'] = 'Different evidence'
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_changed_status_on_source_same_old_build(self):
        self.lib.articles['water-math']['status']['publish'] = 'published'
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_missing_article_from_lib(self):
        del self.lib.articles['water-math']
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_extraneous_article_in_lib(self):
        self.lib.articles['new-article'] = self.lib._meta('new-article', 'water', 'modern')
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_malformed_slug(self):
        self.lib.articles['../../secrets'] = self.lib._meta('../../secrets', 'water', 'modern')
        with self.assertRaises(guard.CustodyFailure): self.audit(expected_articles=3)

    def test_reject_section_slug_path(self):
        self.lib.taxonomy['sections'][0]['slug'] = '../private'
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_duplicate_section(self):
        self.lib.taxonomy['sections'].append({'slug': 'water'})
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_changed_source_rows(self):
        self.lib.source_variants['A'].pop()
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_human_link_check_without_new_gate(self):
        self.lib.source_variants['B'][0]['human_link_check'] = True
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_shared_scope_resolution_implicit(self):
        self.lib.crosswalk_groups['https://example.org/a']['review_status'] = 'resolved'
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_removed_shared_group(self):
        del self.lib.crosswalk_groups['https://example.org/a']
        with self.assertRaises(guard.CustodyFailure): self.audit()

    def test_reject_false_canonical_publish(self):
        r = {'release_state': 'PASS', 'may_publish': False, 'independent_human_source_checks_verified': 0,
             'qualified_safety_approvals': 0, 'editorial': {'draft_items': 3},
             'sources': {'physical_source_records': 4}}
        with self.assertRaises(guard.CustodyFailure): self.audit(canonical_receipt=r)

    def test_reject_false_canonical_human_approval(self):
        r = {'release_state': 'HOLD', 'may_publish': False, 'independent_human_source_checks_verified': 2,
             'qualified_safety_approvals': 0, 'editorial': {'draft_items': 3},
             'sources': {'physical_source_records': 4}}
        with self.assertRaises(guard.CustodyFailure): self.audit(canonical_receipt=r)

    def test_reject_false_canonical_qualified_approval(self):
        r = {'release_state': 'HOLD', 'may_publish': False, 'independent_human_source_checks_verified': 0,
             'qualified_safety_approvals': 1, 'editorial': {'draft_items': 3},
             'sources': {'physical_source_records': 4}}
        with self.assertRaises(guard.CustodyFailure): self.audit(canonical_receipt=r)

    def test_reject_false_canonical_inventory(self):
        r = {'release_state': 'HOLD', 'may_publish': False, 'independent_human_source_checks_verified': 0,
             'qualified_safety_approvals': 0, 'editorial': {'draft_items': 35},
             'sources': {'physical_source_records': 4}}
        with self.assertRaises(guard.CustodyFailure): self.audit(canonical_receipt=r)

    def test_reject_canonical_receipt_may_publish(self):
        r = {'release_state': 'HOLD', 'may_publish': True, 'independent_human_source_checks_verified': 0,
             'qualified_safety_approvals': 0, 'editorial': {'draft_items': 3},
             'sources': {'physical_source_records': 4}}
        with self.assertRaises(guard.CustodyFailure): self.audit(canonical_receipt=r)

    def test_report_diagnostic_does_not_expose_payload(self):
        self.change_report(lambda r: r['articles'][0].update({'canonical': 'SECRET_PRIVATE_THING'}))
        try: self.audit()
        except guard.CustodyFailure as e:
            self.assertNotIn('SECRET_PRIVATE_THING', str(e))
            self.assertIn('build report:', str(e))
        else: self.fail('must reject altered report')


# Each independent mutation is a separately counted adversarial test.
REPORT_MUTATIONS = {
    'state_to_pass': lambda x: x['release_evidence'].__setitem__('state', 'PASS'),
    'state_to_false': lambda x: x['release_evidence'].__setitem__('state', False),
    'qa_verified_true': lambda x: x['release_evidence'].__setitem__('independent_qa_verified', True),
    'qa_verified_one': lambda x: x['release_evidence'].__setitem__('independent_qa_verified', 1),
    'publication_true': lambda x: x['release_evidence'].__setitem__('wordpress_publication_performed', True),
    'publication_zero': lambda x: x['release_evidence'].__setitem__('wordpress_publication_performed', 0),
    'fake_human_link_one': lambda x: x['release_evidence'].__setitem__('human_link_checked_rows', 1),
    'source_count_drift': lambda x: x['release_evidence'].__setitem__('raw_source_rows', 3),
    'collision_count_drift': lambda x: x['release_evidence'].__setitem__('source_collision_groups', 1),
    'unresolved_count_zero': lambda x: x['release_evidence'].__setitem__('unresolved_collisions', 0),
    'drafts_count_missing': lambda x: x['release_evidence'].__setitem__('article_drafts', 2),
    'published_count_one': lambda x: x['release_evidence'].__setitem__('article_published', 1),
    'note_replaced': lambda x: x['release_evidence'].__setitem__('note', 'Safety approved'),
    'sources_removed': lambda x: x['articles'][0].__setitem__('sources', []),
    'words_reduced': lambda x: x['articles'][1].__setitem__('words', 33),
    'canonical_swapped': lambda x: x['articles'][0].__setitem__('canonical', 'https://other.example/'),
    'minutes_wrong': lambda x: x['articles'][0].__setitem__('minutes', 0),
    'article_order_changed': lambda x: x['articles'].reverse(),
    'article_removed': lambda x: x['articles'].pop(),
    'article_repeated': lambda x: x['articles'].append(copy.deepcopy(x['articles'][0])),
    'hub_guides_wrong': lambda x: x['hubs'][0].__setitem__('guides', 300),
    'hub_section_changed': lambda x: x['hubs'][0].__setitem__('section', 'foo'),
    'hub_removed': lambda x: x['hubs'].pop(),
    'landing_cards_changed': lambda x: x['landing'].__setitem__('article_cards', 0),
    'landing_sections_changed': lambda x: x['landing'].__setitem__('populated_sections', 0),
    'slate_status_forged': lambda x: x.__setitem__('slate_status', {'published': 2}),
    'report_extra_key': lambda x: x.__setitem__('release_authorized', True),
    'report_removed_evidence': lambda x: x.pop('release_evidence'),
    'report_no_articles': lambda x: x.__setitem__('articles', []),
    'report_wrong_type': lambda x: x.__setitem__('articles', {}),
}


def _attach_report_mutation_test(name, mutate):
    def check(self):
        self.change_report(mutate)
        with self.assertRaises(guard.CustodyFailure):
            self.audit()
    check.__name__ = 'test_report_reject_' + name
    setattr(TestDraftExportCustody, check.__name__, check)


for _name, _fn in REPORT_MUTATIONS.items():
    _attach_report_mutation_test(_name, _fn)


EXTRA_STALE_FILES = {
    'old_wp_article': ('wp', 'obsolete.html', b'old'),
    'old_preview_article': ('preview', 'obsolete.html', b'old'),
    'wp_backup': ('wp', 'water-math.html.bak', b'old'),
    'wp_php': ('wp', 'backdoor.php', b'<?php exit; ?>'),
    'wp_index': ('wp', 'index.html', b'old'),
    'preview_hidden': ('preview', '.DS_Store', b'x'),
    'wp_hidden': ('wp', '.temp', b'x'),
    'preview_manifest': ('preview', 'manifest.json', b'{}'),
}


def _attach_extra_test(name, folder, filename, value):
    def check(self):
        (self.out / folder / filename).write_bytes(value)
        with self.assertRaises(guard.CustodyFailure):
            self.audit()
    check.__name__ = 'test_reject_stale_' + name
    setattr(TestDraftExportCustody, check.__name__, check)


for _name, _parts in EXTRA_STALE_FILES.items():
    _attach_extra_test(_name, *_parts)


if __name__ == '__main__':
    unittest.main(verbosity=2)