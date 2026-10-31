"""Preflight for Jetpack custom excerpts; never a real delivery test."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ExcerptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.excerpts = json.loads((ROOT / 'delivery' / 'wordpress_excerpt_copy.json').read_text(encoding='utf-8'))
        cls.manifest = json.loads((ROOT / 'manifest.json').read_text(encoding='utf-8'))

    def test_count_and_same_order_as_campaign(self):
        a = self.excerpts['entries']
        self.assertEqual([x['number'] for x in a], [1, 2, 3, 4, 5, 6])
        self.assertEqual([x['subject'] for x in a], [m['subject'] for m in self.manifest['issues']])

    def test_excerpts_have_real_content_and_fit_preview(self):
        for e in self.excerpts['entries']:
            self.assertTrue(45 <= len(e['excerpt'].split()) <= 100, str(e['number']))
            self.assertNotIn('[[', e['excerpt'])
            self.assertNotIn('http', e['excerpt'].lower())

    def test_commercial_relationship_expressed_in_both_excerpt_emails(self):
        for e in self.excerpts['entries']:
            if e['number'] in (3, 5):
                self.assertIn('commission', e['excerpt'].lower())
                self.assertIn('affiliate', e['excerpt'].lower())
            else:
                self.assertNotIn('may earn a commission', e['excerpt'].lower())
                self.assertNotIn('affiliate', e['excerpt'].lower())

    def test_hold_only(self):
        self.assertEqual(self.excerpts['status'], 'DRAFT_FOR_WORDPRESS_EDITOR_REVIEW_ONLY')
        self.assertIn('NOT direct affiliate', self.excerpts['delivery_mode'])


if __name__ == '__main__':
    unittest.main()
