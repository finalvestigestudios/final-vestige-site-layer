"""R418 semantic, default-off, source custody and fail-open acceptance on actual PHP fixture."""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import unittest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
EX2 = ROOT.parent
SOURCE = ROOT / 'staging-chronology-bridge.php'
CSS = ROOT / 'assets/chronology-bridge.css'
ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
NASA_TEXT = [
    'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
    'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/',
    'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/',
]

def render(mode='staging'):
    result = subprocess.run(['php', str(ROOT/'qa/render_fixture.php')],
                            capture_output=True, text=True, check=True,
                            env=dict(os.environ, FV_TEST_MODE=mode))
    return BeautifulSoup(result.stdout, 'html.parser')

def blob(path):
    content = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()

class R418Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = render()
        cls.main = cls.page.select_one('[data-fv-r418-chronology]')

    def test_php_lint(self):
        for path in (SOURCE, ROOT/'qa/render_fixture.php'):
            lint = subprocess.run(['php', '-l', str(path)], capture_output=True, text=True, check=True)
            self.assertIn('No syntax errors', lint.stdout)

    def test_exact_reviewed_source_pins(self):
        expected = {
            EX2/'apollo-r411/staging-source-drawer.php':'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1',
            EX2/'apollo-r415/staging-journey.php':'18d20114af2a854bc06f1b265026860f6ccee30c',
            CSS:'08cd991db94f368b173e04013842d4dcde7e3e4b',
        }
        for path,sha in expected.items():
            self.assertEqual(blob(path), sha, str(path))

    def test_six_source_context_distinct_from_three_historical_stages(self):
        self.assertIsNotNone(self.main)
        stages = self.main.select('ol.fv-r418__rail > li')
        self.assertEqual(len(stages), 3)
        self.assertEqual(len(self.main.select('h3')), 3)
        for expected in ('27 January 1967','December 1967','February 1968','14 March 1968'):
            self.assertIn(expected, self.main.get_text(' ', strip=True))
        self.assertEqual(len(self.main.select('details > summary')), 3)
        self.assertEqual(len(self.main.select('.fv-r418__limit')), 3)

    def test_each_source_is_textual_record_for_correct_period(self):
        stages = self.main.select('.fv-r418__stage')
        for i,stage in enumerate(stages):
            self.assertEqual([a.get('href') for a in stage.select('a')], [NASA_TEXT[i]])
            self.assertIn('Evidence boundary:', stage.get_text(' ', strip=True))
        self.assertIn('102 deliberate ignitions', stages[1].get_text(' ', strip=True))
        self.assertIn('2017 museum tribute', stages[1].get_text(' ', strip=True))
        self.assertIn('could not conclusively identify', stages[0].get_text(' ', strip=True))
        self.assertIn('does not retrospectively', stages[2].get_text(' ', strip=True))

    def test_no_false_atlas_cross_links(self):
        self.assertFalse(self.main.select('a[href^="#fv-r414-gallery-"]'))
        self.assertFalse(self.main.select('a[href^="https://www.nasa.gov/image-detail/"]'))
        self.assertNotIn('Related evidence 06', str(self.main))
        self.assertIn('no archival photographs', self.main.get_text(' ', strip=True).lower())

    def test_no_script_media_geo_tracking_purchases_or_forms(self):
        for selector in ('script','iframe','img','picture','video','svg','canvas','map','form','input','audio'):
            self.assertEqual(self.main.select(selector), [], selector)
        self.assertEqual(len(self.main.select('a[href="'+ARTICLE+'"]')), 1)
        self.assertFalse([a for a in self.main.select('a[href]') if a['href'] not in NASA_TEXT + [ARTICLE, 'https://www.nasa.gov/nasa-brand-center/images-and-media/']])

    def test_all_time_boundaries_visible_with_no_js(self):
        for stage in self.main.select('.fv-r418__stage'):
            self.assertTrue(stage.select_one('.fv-r418__limit'))
            self.assertTrue(stage.select_one('a[href^="https://www.nasa.gov/"]'))

    def test_wordpress_gate_disallows_unapproved_context(self):
        for mode in ('production','wrong-page','disabled','archive'):
            page = render(mode)
            self.assertIsNone(page.select_one('[data-fv-r418-chronology]'))
            self.assertEqual(len(page.select('a[href="'+ARTICLE+'"]')), 1)

    def test_double_render_ids_unique_and_one_cta_each(self):
        page = render('double')
        self.assertEqual(len(page.select('[data-fv-r418-chronology]')), 2)
        ids = [e['id'] for e in page.select('[id]')]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(page.select('a[href="'+ARTICLE+'"]')), 2)

    def test_css_dependency_mutation_rejected(self):
        prior = CSS.read_bytes()
        try:
            CSS.write_bytes(prior + b'\n/* unsafe mutation */\n')
            page = render()
            self.assertIsNone(page.select_one('[data-fv-r418-chronology]'))
            self.assertEqual(len(page.select('a[href="'+ARTICLE+'"]')), 1)
        finally:
            CSS.write_bytes(prior)
        self.assertEqual(blob(CSS), '08cd991db94f368b173e04013842d4dcde7e3e4b')

    def test_staging_id_not_initialized_by_default(self):
        self.assertIn("defined('FV_R418_ENABLED')", SOURCE.read_text())
        self.assertIn("wp_get_environment_type() === 'staging'", SOURCE.read_text())

if __name__ == '__main__':
    unittest.main(verbosity=2)
