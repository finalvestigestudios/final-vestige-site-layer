"""R184 synthetic-only quarantine regressions; no actual repository safety QD."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import r184_report_admission_gate as gate


def make_fixture(root: Path) -> list[str]:
    base = root / 'preparedness'
    articles = base / 'content' / 'articles'
    out = base / 'build' / 'wp'
    articles.mkdir(parents=True)
    out.mkdir(parents=True)
    slugs = [f'article-{i:02d}' for i in range(35)]
    slate = [{'slug': slug} for slug in slugs]
    (base / 'taxonomy.json').write_text(json.dumps({'base_path':'/preparedness/', 'slate':slate}))
    report_articles = []
    landing_cards = []
    for i,slug in enumerate(slugs):
        state = 'approved' if i < 2 else 'not-required' if i < 6 else 'pending'
        n = 57 + (i < 5)  # 35 * 57 + 5 = 2000
        body = '<p>' + ('{{cite:original-source}} ' * n) + '</p>'
        (articles / f'{slug}.body.html').write_text(body)
        (articles / f'{slug}.meta.json').write_text(json.dumps({'slug':slug, 'section':'start-here',
            'status':{'publish':'draft'}, 'safety_review':{'state':state}}))
        historical = ('Historical label recorded as approved by historian. This label has not been independently verified.'
                      if state == 'approved' else
                      'Historically marked not required for topic-specific safety review. Editorial source review and independent QD are still required before publication.'
                      if state == 'not-required' else 'Pending. Independent QD required.')
        html = ('<!-- wp:html -->\n<div data-slug="' + slug + '">Draft: not public\n'
                'Independent safety/source and QD verification pending\n'
                '<section class="pa-sources">Sources</section>'
                '<section class="pa-review">' + historical + '</section>'
                + '<sup class="pa-cite">[1]</sup>' * n + '</div>\n<!-- /wp:html -->\n')
        (out / f'{slug}.html').write_text(html)
        report_articles.append({'slug':slug, 'words':2200,
             'canonical': gate.BASE + 'start-here/' + slug + '/'})
        landing_cards.append('<li class="pa-card" data-section="start-here" data-verify="pending"></li>')
    (out / 'landing.html').write_text('<!-- wp:html -->' + ''.join(landing_cards) + '<!-- /wp:html -->')
    report = {'articles':report_articles, 'slate_status':{gate.PENDING:35},
        'landing':{'article_cards':35},
        'release_evidence':{'state':'HOLD', 'article_published':0, 'article_drafts':35,
          'independent_qa_verified':False, 'wordpress_publication_performed':False}}
    (base / 'build' / 'build-report.json').write_text(json.dumps(report))
    return slugs


class ReportAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.slugs = make_fixture(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def assert_hold(self, expected=None):
        errors, summary = gate.check(self.root)
        self.assertEqual(summary['state'], 'INVALID_HARD_HOLD')
        self.assertTrue(errors, summary)
        if expected: self.assertTrue(any(expected in e for e in errors), errors)

    def mutate_json(self, rel, fn, expected=None):
        path = self.root / rel
        old = path.read_text()
        try:
            doc = json.loads(old)
            fn(doc)
            path.write_text(json.dumps(doc))
            self.assert_hold(expected)
        finally:
            path.write_text(old)

    def mutate_html(self, rel, old, new, expected=None):
        path = self.root / rel
        original = path.read_text()
        self.assertIn(old, original)
        try:
            path.write_text(original.replace(old, new, 1))
            self.assert_hold(expected)
        finally:
            path.write_text(original)

    def test_001_valid_synthetic_still_hard_hold(self):
        errors, summary = gate.check(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(summary['state'], 'DRAFT_HARD_HOLD')
        self.assertEqual(summary['articles_checked'], 35)
        self.assertEqual(summary['citation_occurrences_checked'], 2000)
        self.assertFalse(summary['independent_qa_verified'])

    def test_002_cli_exit_two_even_when_structurally_clean(self):
        self.assertEqual(gate.main(['--repo', str(self.root)]), 2)

    def test_003_report_historical_approved_bucket_rejected(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['slate_status'].update({'safety-approved-draft':2}), 'approval')

    def test_004_report_false_qa_rejected(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['release_evidence'].update(independent_qa_verified=True), 'QD')

    def test_005_report_false_publication_rejected(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['release_evidence'].update(wordpress_publication_performed=True), 'publication')

    def test_006_report_false_release_rejected(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['release_evidence'].update(state='PASS'), 'HOLD')

    def test_007_report_paid_article_rejected(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['release_evidence'].update(article_published=1), 'published')

    def test_008_report_draft_count_rejected(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['release_evidence'].update(article_drafts=34), 'draft count')

    def test_009_duplicate_report_slug_rejected(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['articles'].append(x['articles'][0].copy()), 'duplicate report')

    def test_010_canonical_redirect_rejected(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['articles'][0].update(canonical='https://example.org/merchant'), 'canonical')

    def test_011_depth_loss_rejected(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['articles'][0].update(words=100), 'depth')

    def test_012_mismatched_landing_card_count_rejected(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['landing'].update(article_cards=34), 'card count')

    def test_013_false_landing_reviewed_rejected(self):
        self.mutate_html('preparedness/build/wp/landing.html',
            'data-verify="pending"','data-verify="reviewed"', 'reviewed')

    def test_014_missing_landing_rejected(self):
        path = self.root / 'preparedness/build/wp/landing.html'
        renamed = path.with_suffix('.bak')
        path.rename(renamed)
        try: self.assert_hold('landing')
        finally: renamed.rename(path)

    def test_015_source_section_missing_rejected(self):
        self.mutate_html('preparedness/build/wp/article-00.html',
            'class="pa-sources"','class="absent"', 'review/source')

    def test_016_review_section_missing_rejected(self):
        self.mutate_html('preparedness/build/wp/article-00.html',
            'class="pa-review"','class="unreviewed"', 'review/source')

    def test_017_incomplete_repo_rejected(self):
        errors, summary = gate.check(self.root / 'missing')
        self.assertTrue(errors)
        self.assertEqual(summary['state'], 'INVALID_HARD_HOLD')

    def test_018_future_slate_status_cannot_be_fake_reviewed(self):
        self.mutate_json('preparedness/build/build-report.json',
            lambda x: x['slate_status'].update({'reviewed':35}), 'slate states')


def make_slug_warning_test(slug):
    def test(self):
        self.mutate_html('preparedness/build/wp/' + slug + '.html',
            'Independent safety/source and QD verification pending',
            'Safety source approved', 'disclaimer')
    return test


def make_slug_citation_test(slug):
    def test(self):
        self.mutate_html('preparedness/build/wp/' + slug + '.html',
            '<sup class="pa-cite">[1]</sup>', '<span>citation lost</span>', 'citation')
    return test


for i in range(35):
    slug = f'article-{i:02d}'
    setattr(ReportAdmissionTests, f'test_1{i:02d}_warning_mutation', make_slug_warning_test(slug))
    setattr(ReportAdmissionTests, f'test_2{i:02d}_citation_mutation', make_slug_citation_test(slug))

if __name__ == '__main__':
    unittest.main()
