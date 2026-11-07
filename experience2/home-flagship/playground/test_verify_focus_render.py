"""Adversarial, in-memory browser checks; NOT a Jetpack or live-site test."""
import asyncio
from pathlib import Path
import tempfile
import unittest
from verify_focus_render import run, APPROVED

HERE = Path(__file__).parent

class FocusRenderContractTests(unittest.TestCase):
    def inspect_fixture(self, name):
        return asyncio.run(run(str(HERE / (name + '_fixture.html')), False, None))

    def test_valid_form_fixture_is_usable_all_ten_modes(self):
        report = self.inspect_fixture('positive')
        self.assertEqual((report['passed'],report['tests']), (10,10))
        self.assertEqual({r['width'] for r in report['records']},{320,360,390,768,1440})
        self.assertEqual({r['mode'] for r in report['records']},{'js','nojs'})

    def test_editor_only_fallback_is_not_a_form(self):
        report = self.inspect_fixture('negative')
        self.assertEqual((report['passed'],report['tests']), (0,10))
        self.assertTrue(all(not r['usable_native_form'] for r in report['records']))

    def test_modal_occlusion_is_rejected(self):
        report = self.inspect_fixture('overlay')
        self.assertEqual((report['passed'],report['tests']), (0,10))
        self.assertTrue(all(not r['email_hit'] for r in report['records']))

    def test_spoofed_download_message_is_rejected(self):
        report = self.inspect_fixture('spoof')
        self.assertEqual((report['passed'],report['tests']), (0,10))
        self.assertTrue(all(r['gift_visible'] for r in report['records']))

    def test_live_target_is_exact_only(self):
        with self.assertRaises(ValueError):
            asyncio.run(run('https://finalvestige.com/wp-admin/', True, None))
        self.assertEqual(APPROVED,'https://finalvestige.com/focus/')

    def test_non_html_offline_file_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'bad.txt'; f.write_text('<html>no</html>')
            with self.assertRaises(ValueError):
                asyncio.run(run(str(f),False,None))

if __name__=='__main__':
    unittest.main()
