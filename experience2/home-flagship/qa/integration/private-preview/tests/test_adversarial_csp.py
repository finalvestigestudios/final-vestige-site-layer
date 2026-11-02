"""Adversarial composer and Chromium CSP smoke for the protected EX2 preview.

This suite uses a SMALL SYNTHETIC FIXTURE, not a canonical homepage checkout or a
WordPress staging installation. It exercises actual shipping PHP composer bytes.
Browser CSP is enforced through a meta policy under Playwright set_content;
frame-ancestors, HTTP header, cookies and WordPress integration remain untested.
"""
from __future__ import annotations
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from build_private_preview import php_payload

CSS = ('flagship.css', 'chronicle.css', 'chronicle-lens.css', 'inquiry.css',
       'observer-lab.css', 'reading-trail.css')
JS = ('flagship.js', 'observer-lab.js', 'chronicle-lens.js', 'reading-trail.js')


def fixture() -> dict[str, bytes]:
    head = ''.join(f'<link rel="stylesheet" href="./{name}">' for name in CSS)
    head += ''.join(f'<script src="./{name}" defer></script>' for name in JS)
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            + head + '</head><body><div data-fv-home-flagship>'
            + '<h1>DESIGN STUDY · NOT LIVE</h1>'
            + '<p>DO NOT DEPLOY AS THE WORDPRESS HOME PAGE</p>'
            + '</div></body></html>')
    assets = {'index.html': html.encode('utf-8')}
    assets.update({name: b'.fv-test{color:#987c53}' for name in CSS})
    assets.update({name: b'window.__fvAuthorScripts=(window.__fvAuthorScripts||0)+1;' for name in JS})
    return assets


class ComposerAdversarial(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='fv-ex2-adversarial-')
        self.p = Path(self.tmp.name)
        shutil.copy2(BASE / 'fv-ex2-private-preview.php', self.p / 'fv-ex2-private-preview.php')
        self.assets = fixture()
        self.launcher = self.p / 'launch.php'
        self.launcher.write_text('''<?php
        define('ABSPATH','/synthetic/');
        function add_shortcode($name,$callback){} function add_action($name,$callback){}
        function plugin_dir_path($file){return dirname($file).DIRECTORY_SEPARATOR;}
        require __DIR__.'/fv-ex2-private-preview.php';
        $p = fv_ex2_private_compose();
        if ($p === null) { echo json_encode(['valid'=>false]); exit; }
        echo json_encode(['valid'=>true,'nonce'=>$p['nonce'],'html'=>$p['html']]);
        ''', encoding='utf-8')

    def tearDown(self): self.tmp.cleanup()

    def compose(self, assets=None):
        a = assets or self.assets
        (self.p / 'fv-ex2-private-payload.php').write_bytes(php_payload(a))
        result = subprocess.run(['php', str(self.launcher)], text=True, capture_output=True, timeout=8)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_signed_canonical_shape_assembles_with_four_tail_scripts(self):
        result = self.compose()
        self.assertTrue(result['valid'])
        html = result['html']
        self.assertEqual(html.count('data-fv-private-asset='), 10)
        self.assertEqual(html.count('<style nonce='), 6)
        self.assertEqual(html.count('<script nonce='), 4)
        self.assertEqual(html.count('<script src='), 0)
        self.assertTrue(html.index('<script nonce=') > html.index('</div>'))

    def test_css_breakout_rejected_even_if_sha_manifest_recomputed(self):
        a = self.assets.copy()
        a['observer-lab.css'] += b'</style><script>window.rogue=1</script>'
        self.assertFalse(self.compose(a)['valid'])

    def test_script_breakout_rejected_even_if_sha_manifest_recomputed(self):
        a = self.assets.copy()
        a['reading-trail.js'] += b'/* </script> */'
        self.assertFalse(self.compose(a)['valid'])

    def test_unknown_source_asset_rejected_even_if_signed(self):
        a = self.assets.copy()
        a['an-extra-js.js'] = b'console.log(1)'
        self.assertFalse(self.compose(a)['valid'])

    def test_duplicate_executable_html_reference_rejected(self):
        a = self.assets.copy()
        a['index.html'] = a['index.html'].replace(
            b'</head>', b'<script src="https://unapproved.invalid/test.js"></script></head>')
        self.assertFalse(self.compose(a)['valid'])

    def test_duplicate_css_reference_rejected(self):
        a = self.assets.copy()
        a['index.html'] = a['index.html'].replace(b'</head>',
            b'<link rel="stylesheet" href="./flagship.css"></head>')
        self.assertFalse(self.compose(a)['valid'])

    def test_truncated_source_payload_rejected(self):
        a = self.assets.copy()
        a.pop('chronicle.css')
        self.assertFalse(self.compose(a)['valid'])

    def test_exact_script_order_preserved(self):
        a = self.assets.copy()
        for i, name in enumerate(JS):
            a[name] = f'window.__fvOrder=(window.__fvOrder||[]);window.__fvOrder.push({i});'.encode()
        result = self.compose(a)
        self.assertTrue(result['valid'])
        html = result['html']
        offsets = [html.index(f'data-fv-private-asset="{name}"') for name in JS]
        self.assertEqual(offsets, sorted(offsets))

    def test_real_chromium_blocks_rogue_inline_script_with_meta_csp(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.fail('Playwright is required for CSP evidence; do not silently skip')
        result = self.compose()
        self.assertTrue(result['valid'])
        nonce = result['nonce']
        # Meta CSP simulates enforcement of script/style directives only; it cannot
        # enforce the HTTP-only frame-ancestors directive or WordPress credentials.
        policy = (f"default-src 'none'; script-src 'nonce-{nonce}'; "
                  "style-src 'unsafe-inline'; img-src https://finalvestige.com "
                  "https://i0.wp.com data:; connect-src 'none'")
        meta = '<meta http-equiv="Content-Security-Policy" content="' + policy + '">'
        html = result['html'].replace('</head>', meta + '</head>')
        html = html.replace('</head>', '</head><script>window.__rogueScriptRan=1;</script>')
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path='/usr/bin/chromium',
                                         args=['--no-sandbox', '--disable-dev-shm-usage'])
            for width in (390, 1440):
                context = browser.new_context(viewport={'width': width, 'height': 850}, reduced_motion='reduce')
                page = context.new_page()
                console_errors = []
                page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)
                page.set_content(html, wait_until='domcontentloaded')
                self.assertEqual(page.evaluate('window.__fvAuthorScripts'), 4)
                self.assertIsNone(page.evaluate('window.__rogueScriptRan'))
                self.assertTrue(any('Content Security Policy' in e for e in console_errors))
                self.assertEqual(page.locator('h1').count(), 1)
                context.close()
            browser.close()

if __name__ == '__main__': unittest.main()
