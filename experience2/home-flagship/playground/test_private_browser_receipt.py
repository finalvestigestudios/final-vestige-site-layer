#!/usr/bin/env python3
"""Offline checks on derived Playground Blueprint, in-browser panel and fail-closed results.
This is NOT WordPress acceptance: Chromium uses an explicit faux WordPress shell fixture.
"""
import base64
import hashlib
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).parent))
from make_private_browser_receipt_variant import derive, git_blob, write_bundle, SOURCE_BLOB, PLUGIN_SHA256

HERE=Path(__file__).parent
SOURCE=(HERE/'FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json').read_bytes()
PLUGIN=(HERE/'fv-ex2-private-browser-receipt.php').read_bytes()


def get_fixture_html():
    obj=json.loads(SOURCE)
    php=obj['steps'][2]['data']
    html=re.search(r"return <<<'FVPG_HTML_END'\n(.*?)\nFVPG_HTML_END;",php,re.S).group(1)
    css=re.search(r"<<<'FVPG_CSS_END'\n(.*?)\nFVPG_CSS_END",php,re.S).group(1)
    plugin=PLUGIN.decode()
    panel=re.search(r'(<aside id="fv-ex2-receipt".*?</aside>\s*<script id="fv-ex2-receipt-local-script">.*?</script>)',plugin,re.S).group(1)
    return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>{css}</style><body><div class="wp-site-blocks">{html}</div>{panel}</body></html>'


class BuildTests(unittest.TestCase):
    def test_exact_inputs_and_6_steps(self):
        raw=derive(SOURCE,PLUGIN)
        bp=json.loads(raw); orig=json.loads(SOURCE)
        self.assertEqual(git_blob(SOURCE),SOURCE_BLOB)
        self.assertEqual(len(bp['steps']),6)
        self.assertEqual([bp['steps'][i+(i>=3)] for i in range(5)],orig['steps'])
        self.assertTrue(bp['steps'][3]['path'].endswith('fv-ex2-private-browser-receipt.php'))
        self.assertEqual(raw,derive(SOURCE,PLUGIN))
    def test_bad_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'not pinned'):
            derive(SOURCE + b' ',PLUGIN)
    def test_bad_plugin_rejected(self):
        with self.assertRaisesRegex(ValueError,'plugin not pinned'):
            derive(SOURCE,PLUGIN+b'// bad edit')
    def test_manifest_launcher_and_no_live_upload(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'bundle.zip'; receipt=write_bundle(HERE/'FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json',HERE/'fv-ex2-private-browser-receipt.php',path)
            with ZipFile(path) as z:
                self.assertEqual(len(z.namelist()),3)
                self.assertEqual(json.loads(z.read('source_manifest.json'))['derived_blueprint_blob'],git_blob(z.read('blueprint_with_local_receipt.json')))
                html=z.read('launch_review.html').decode()
                fragment=re.search(r'https://playground\.wordpress\.net/#([A-Za-z0-9+/=]+)',html).group(1)
                self.assertEqual(base64.b64decode(fragment),z.read('blueprint_with_local_receipt.json'))
                self.assertNotIn('<script',html)
                self.assertFalse(receipt['native_wordpress_tested'])
    def test_php_lint(self):
        p=subprocess.run(['php','-l',str(HERE/'fv-ex2-private-browser-receipt.php')],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
    def test_no_tracking_or_remote_upload(self):
        code=PLUGIN.decode()
        for needle in ['fetch(', 'sendBeacon','XMLHttpRequest','wp_remote_post','localStorage','sessionStorage','wp_insert_post','wp_mail','admin_post_']:
            self.assertNotIn(needle,code)
        self.assertIn("is_page('fv-ex2-review')",code)
        self.assertIn('fv_ex2_playground_review_only',code)


class ChromiumReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.pw=sync_playwright().start()
        cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        cls.fixture=get_fixture_html()
        cls.outdir=Path('/tmp/fv-ex2-receipt-offline-evidence');cls.outdir.mkdir(exist_ok=True)
        cls.results=[]
    @classmethod
    def tearDownClass(cls):
        (cls.outdir/'offline_chromium_results.json').write_text(json.dumps(cls.results,indent=2)+'\n')
        cls.browser.close();cls.pw.stop()

    def scan(self,width=390,mutate=None,js=True,reduced=False,shot=None):
        source=self.fixture if mutate is None else mutate(self.fixture)
        ctx=self.browser.new_context(viewport={'width':width,'height':667 if width<=390 else 900},java_script_enabled=js,reduced_motion='reduce' if reduced else 'no-preference',accept_downloads=True)
        page=ctx.new_page()
        page.route('**/*', lambda route: route.abort() if route.request.url.startswith('https://') else route.continue_())
        page.set_content(source,wait_until='domcontentloaded')
        status=page.locator('#fv-ex2-receipt-status').inner_text()
        self.assertIn('Not run',status)
        if not js:
            self.assertEqual(page.locator('.fv-margin-strip__item').count(),72)
            self.assertTrue(page.locator('#fv-hf-mind-title').is_visible())
            ctx.close();return None
        self.assertTrue(page.locator('#fv-ex2-download').is_disabled())
        page.locator('#fv-ex2-run').click()
        data=json.loads(page.locator('#fv-ex2-receipt-output').inner_text())
        self.assertTrue(page.locator('#fv-ex2-download').is_enabled())
        with page.expect_download() as d: page.locator('#fv-ex2-download').click()
        download=d.value
        self.assertEqual(download.suggested_filename,'fv-ex2-isolated-browser-receipt.json')
        file=Path(self.outdir/f'receipt_{width}_{"tamper" if mutate else "intact"}.json')
        download.save_as(file)
        self.assertEqual(json.loads(file.read_text())['margins_count'],data['margins_count'])
        self.assertFalse(data['release_authorized'])
        self.assertIn('actual_response_bytes',data['not_qualified'])
        self.assertIn('axe_WCAG_2_2_AA',data['not_qualified'])
        if shot:
            page.locator('#fv-ex2-receipt').screenshot(path=str(self.outdir/shot))
        self.results.append({'width':width,'mutated':bool(mutate),'status':data['assessment'],'blockers':data['blockers'],'wp_shell_observed':data['wp_shell_observed']})
        ctx.close();return data

    def test_full_fixture_4_widths(self):
        for width in (320,390,768,1440):
            with self.subTest(width=width):
                d=self.scan(width,shot=f'qa_panel_{width}.png')
                self.assertEqual(d['margins_count'],72)
                self.assertEqual(d['focus_destinations'],5)
                self.assertEqual(len(d['chapters']),7)
                self.assertTrue(d['wp_shell_observed'])
                self.assertEqual(len(d['image_observations']),2)
                self.assertIn('ARCHIVAL_IMAGE_NOT_DECODED_MAY_BE_LAZY',d['blockers'])
                self.assertEqual(d['assessment'],'LOCAL_VIEWPORT_BLOCKED')
    def test_missing_wordpress_shell(self):
        d=self.scan(390,lambda x:x.replace('class="wp-site-blocks"','class="not-wordpress"',1))
        self.assertIn('NOT_WORDPRESS_SHELL',d['blockers'])
    def test_missing_margin(self):
        d=self.scan(390,lambda x:x.replace('class="fv-margin-strip__item"','class="removed-margin"',1))
        self.assertIn('MARGINS_NOT_72',d['blockers'])
    def test_bad_focus(self):
        d=self.scan(390,lambda x:x.replace('href="https://finalvestige.com/focus/"','href="https://example.invalid/focus/"',1))
        self.assertIn('FOCUS_LINKS_NOT_5',d['blockers'])
    def test_reduced_motion(self):
        d=self.scan(390,reduced=True)
        self.assertTrue(d['prefers_reduced_motion'])
    def test_no_js_content(self):
        self.assertIsNone(self.scan(390,js=False))


if __name__=='__main__':unittest.main(verbosity=2)
