"""Run locally on exact parent PR215 + stacked bridge; fail-closed PHP custody.

Use: python -m unittest discover -s experience2/apollo-wp-bridge/sealed/qa -p 'test_sealed.py' -v
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile
import sys

HERE = Path(__file__).resolve().parent
SEALED = HERE.parent
BRIDGE = SEALED.parent
ROOT = 'fv-ex2-apollo-private-review'
sys.path.insert(0, str(SEALED))
from build_sealed import build, FILES, PIN


def php(plugin: Path, mode: str, action: str, file: str = ''):
    return subprocess.run(['php', str(HERE / 'mock_wordpress.php'), str(plugin), mode, action, file],
                          capture_output=True, timeout=30)


def unpack(where: Path):
    dest = where / 'review.zip'
    m = build(dest)
    with zipfile.ZipFile(dest) as z:
        names = z.namelist()
        plugin = where / 'plugin.php'
        plugin.write_bytes(z.read(ROOT + '/fv-ex2-apollo-sealed.php'))
    return dest, m, names, plugin


class SealedApollo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.work = Path(cls.tmp.name)
        cls.zip, cls.m, cls.members, cls.plugin = unpack(cls.work)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_01_source_pin_custody_and_no_public_files(self):
        self.assertTrue(self.m['source_match_all_12_blob_pins'])
        self.assertEqual(self.m['source_pr215_head'], PIN)
        self.assertEqual(len(self.m['outputs_sha256']), 7)
        self.assertEqual(len(self.members), 3)
        self.assertTrue(all(not any(name.endswith('/' + file) for file in FILES) for name in self.members))
        self.assertEqual(len(self.m['generated_public_static_assets']), 0)

    def test_02_deterministic_zip_and_php_lint(self):
        again = self.work / 'again.zip'
        self.assertEqual(build(again), self.m)
        self.assertEqual(again.read_bytes(), self.zip.read_bytes())
        for name in ('fv-ex2-apollo-sealed-template.php',):
            p = subprocess.run(['php', '-l', str(SEALED / name)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout)
        p = subprocess.run(['php', '-l', str(self.plugin)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout)

    def test_03_all_denials_shortcode_and_ajax(self):
        for mode in ('production', 'off', 'guest', 'reader'):
            with self.subTest(mode=mode):
                short = php(self.plugin, mode, 'shortcode')
                self.assertEqual(short.returncode, 0, short.stderr)
                self.assertEqual(short.stdout, b'')
                for action in ('page', 'download'):
                    denied = php(self.plugin, mode, action, 'evidence-export.csv')
                    self.assertEqual(denied.stdout, b'')
                    self.assertIn(b'STATUS:403', denied.stderr)

    def test_04_nonce_rejection(self):
        for action in ('page', 'download'):
            p = php(self.plugin, 'badnonce', action, 'response-export.json')
            self.assertEqual(p.returncode, 62)
            self.assertIn(b'BAD_NONCE', p.stderr)
            self.assertEqual(p.stdout, b'')

    def test_05_authorized_shortcode_and_routes(self):
        x = php(self.plugin, 'staging', 'shortcode')
        self.assertEqual(x.returncode, 0, x.stderr)
        text = x.stdout.decode()
        self.assertIn('sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox allow-downloads"', text)
        self.assertNotIn('allow-same-origin', text)
        self.assertIn('PRIVATE STAGING STUDY', text)
        self.assertIn('Open the private full-page evidence review', text)
        self.assertIn('rel="noopener noreferrer"', text)
        self.assertNotIn('allow-same-origin', text)
        self.assertNotIn('allow-top-navigation', text)
        self.assertIn('fv_ex2_apollo_sealed_page', text)
        self.assertIn('fixed-cli-test-nonce', text)
        r = php(self.plugin, 'staging', 'registrations')
        self.assertEqual(r.returncode, 0)
        registered = json.loads(r.stdout)
        self.assertEqual(registered['shortcodes'], ['fv_ex2_apollo_sealed_preview'])
        self.assertEqual(set(registered['actions']), {'wp_ajax_fv_ex2_apollo_sealed_page',
                                                     'wp_ajax_fv_ex2_apollo_sealed_download'})
        self.assertNotIn('nopriv', str(registered))

    def test_06_authorized_page_exact_sources(self):
        x = php(self.plugin, 'staging', 'page')
        self.assertEqual(x.returncode, 0, x.stderr)
        s = x.stdout.decode()
        self.assertIn('id="atlas"', s)
        self.assertIn('id="documentary-trails"', s)
        self.assertIn('Apollo 1: Research Desk and primary-source casefile', s)
        self.assertEqual(s.count('<h1 '), 1)
        self.assertEqual(s.count('<main '), 1)
        self.assertEqual(s.count('</main>'), 1)
        self.assertIn('id="fv-ex2-apollo-document"', s)
        self.assertIn('href="#fv-ex2-apollo-document">Skip to Apollo evidence</a>', s)
        self.assertIn('.fv-ex2-apollo__skip:focus-visible{transform:none', s)
        self.assertEqual(s.count('fv_ex2_apollo_sealed_download'), 4)
        self.assertNotIn('{{FV_EX2_ASSET_BASE}}', s)
        self.assertIn('nonce="', s)
        self.assertNotIn('<link rel="stylesheet" href=', s)
        self.assertIn('data-ex2-atlas-item', s)
        self.assertGreater(len(s), 110_000)
        (self.work / 'exact-page.html').write_text(s, encoding='utf-8')

    def test_07_exact_downloads_allowlist(self):
        generated = BRIDGE / 'generated'
        for file in FILES[3:]:
            with self.subTest(file=file):
                response = php(self.plugin, 'staging', 'download', file)
                self.assertEqual(response.returncode, 0, response.stderr)
                self.assertEqual(response.stdout, (generated / file).read_bytes())
        blocked = php(self.plugin, 'staging', 'download', '../fragment.html')
        self.assertEqual(blocked.stdout, b'')
        self.assertIn(b'STATUS:404', blocked.stderr)

    def test_08_tamper_integrity_failure(self):
        # Mutation affects only one packed byte, not any digest or source file.
        source = self.plugin.read_text(encoding='utf-8')
        marker = '"apollo.js":"'
        self.assertIn(marker, source)
        start = source.index(marker) + len(marker)
        bad = source[:start] + ('A' if source[start] != 'A' else 'B') + source[start+1:]
        tamper = self.work / 'tampered.php'
        tamper.write_text(bad, encoding='utf-8')
        test = php(tamper, 'staging', 'page')
        self.assertEqual(test.stdout, b'')
        self.assertIn(b'STATUS:503', test.stderr)

    def test_10_axe_release_gate_fails_closed_without_verified_bundle(self):
        # The developer smoke run may proceed without axe, but no release gate may
        # silently report green when the audited engine was never executed.
        import os
        env = dict(os.environ)
        env.pop('FV_VERIFIED_AXE_BUNDLE', None)
        env.pop('FV_VERIFIED_AXE_SHA256', None)
        proc = subprocess.run(
            [sys.executable, str(HERE / 'browser_exact.py'), '--require-axe'],
            cwd=BRIDGE.parent.parent, env=env, text=True, capture_output=True, timeout=35,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('RELEASE HOLD: supply FV_VERIFIED_AXE_BUNDLE', proc.stderr)

    def test_09_no_prod_writes_and_csp_contract(self):
        source = (SEALED / 'fv-ex2-apollo-sealed-template.php').read_text(encoding='utf-8')
        for bad in ('wp_insert_post(', 'wp_update_post(', 'wp_delete_post(', 'update_option(',
                    'add_option(', 'wp_ajax_nopriv_fv_ex2_apollo_sealed_'):
            self.assertNotIn(bad, source)
        self.assertIn("script-src 'nonce-{$csp_nonce}'", source)
        self.assertIn('frame-ancestors', source)
        self.assertIn("img-src 'none'", source)
        self.assertIn("Content-Disposition: attachment", source)
        self.assertIn("'FV_EX2_APOLLO_STAGING_ALLOW'", source)

if __name__ == '__main__':
    unittest.main()
