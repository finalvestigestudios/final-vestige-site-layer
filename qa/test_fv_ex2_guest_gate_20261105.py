"""Native Playwright gate smoke and four deliberate negative controls.

Only an isolated representative fixture is used. These tests DO NOT qualify
Final Vestige production, WordPress, Jetpack, archival images, or WCAG.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
from fv_ex2_guest_browser_admission_20261105 import inspect, run

HERE = Path(__file__).parent
subprocess.run([sys.executable, str(HERE / 'fv_ex2_guest_fixture_20261105.py')], check=True, capture_output=True)
BASE = (HERE / 'fixture.html').read_text(encoding='utf-8')

class GateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def inspect_text(self, text):
        page = self.browser.new_page(viewport={'width':390,'height':844})
        try:
            page.set_content(text)
            return inspect(page)
        finally:
            page.close()

    def test_source_fixture_structure(self):
        result = self.inspect_text(BASE)
        self.assertTrue(result['root'])
        self.assertEqual(result['margins'],72)
        self.assertTrue(all(d['exists'] for d in result['chapters']))

    def test_missing_chapter_is_rejected(self):
        result = self.inspect_text(BASE.replace('id="fv-hf-mind-title"', 'id="removed"'))
        self.assertFalse(all(d['exists'] for d in result['chapters']))

    def test_missing_margin_is_rejected(self):
        result = self.inspect_text(BASE.replace('class="fv-margin-strip__item"', 'class="gone"',1))
        self.assertEqual(result['margins'],71)

    def test_missing_contextual_offer_is_rejected(self):
        result = self.inspect_text(BASE.replace('https://finalvestige.com/focus/', 'https://finalvestige.com/blog/'))
        self.assertEqual(len(result['focusLinks']),0)

    def test_production_opt_in_is_required(self):
        with tempfile.TemporaryDirectory() as dest:
            with self.assertRaisesRegex(ValueError,'explicit --live-readonly'):
                run('https://finalvestige.com', dest)

    def test_missing_axe_fails_closed(self):
        with tempfile.TemporaryDirectory() as dest:
            command = [sys.executable, str(HERE / 'fv_ex2_guest_browser_admission_20261105.py'), '--target',
                       HERE.joinpath('fixture.html').as_uri(), '--output', dest]
            outcome = subprocess.run(command, capture_output=True, text=True, timeout=90)
            self.assertEqual(outcome.returncode, 2, outcome.stdout + outcome.stderr)
            report = json.loads(Path(dest, 'results.json').read_text())
            self.assertEqual(report['axe']['status'],'BLOCKED_AXE_MISSING')
            self.assertFalse(report['release_ready'])
            self.assertEqual(len(report['widths']), 6)
            self.assertEqual(len(report['no_js']), 2)
            self.assertEqual(len(report['interactions']), 4)
            self.assertTrue(all(report['checks'].values()))
            self.assertEqual(json.loads(Path(dest,'results.json').read_text())['release_ready'],False)

if __name__ == '__main__':
    unittest.main(verbosity=2)
