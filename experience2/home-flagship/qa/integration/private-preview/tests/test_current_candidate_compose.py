#!/usr/bin/env python3
"""Real PHP composition regression for the exact source-controlled seven-chapter candidate.

Offline and non-production: executes guarded PHP composer without WordPress, external
media or CMS writes. Pass does NOT establish full WordPress, WCAG or image delivery.
"""
from __future__ import annotations
import base64
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
PLUGIN = ROOT / 'qa/integration/private-preview/fv-ex2-private-preview.php'
STAGING_GATE = ROOT / 'qa/release-candidate/verify_exact_staging.py'
ASSETS = ('index.html', 'flagship.css', 'chronicle.css', 'chronicle-lens.css',
          'inquiry.css', 'observer-lab.css', 'reading-trail.css',
          'flagship.js', 'observer-lab.js', 'chronicle-lens.js', 'reading-trail.js')


def php_assoc(values: dict[str, str]) -> str:
    assert all(k in ASSETS for k in values)
    assert all(value.isascii() and "'" not in value for value in values.values())
    return '[' + ','.join(f"'{k}'=>'{v}'" for k, v in values.items()) + ']'


def run_compose(assets: dict[str, bytes]) -> tuple[int, dict]:
    with tempfile.TemporaryDirectory(prefix='fv-ex2-php-custody-') as temp:
        root = Path(temp)
        shutil.copyfile(PLUGIN, root / 'fv-ex2-private-preview.php')
        hashes = {name: hashlib.sha256(value).hexdigest() for name, value in assets.items()}
        encoded = {name: base64.b64encode(value).decode('ascii') for name, value in assets.items()}
        (root / 'fv-ex2-private-payload.php').write_text(
            "<?php\nreturn ['sha256'=>" + php_assoc(hashes)
            + ",'data'=>" + php_assoc(encoded) + "];\n", encoding='ascii')
        php = r'''
define('ABSPATH', '/local-test-only/');
function add_shortcode($name,$handler) { return true; }
function add_action($name,$handler) { return true; }
require $argv[1];
$composed = fv_ex2_private_compose();
if ($composed === null) { echo json_encode(['status'=>'BLOCKED']); exit(2); }
$html = $composed['html'];
echo json_encode([
    'status'=>'COMPOSED',
    'index_sha256'=>$composed['index_sha256'],
    'has_folio'=>strpos($html,'fv-hf__folio-arrival') !== false,
    'editorial_label'=>strpos($html,'EDITORIAL TYPESETTING') !== false,
    'locked_identity'=>strpos($html,'data-fv-direction-choice') === false,
    'script_at_end'=>strrpos($html,'<script nonce=') < strrpos($html,'</body>'),
    'no_raw_css_ref'=>strpos($html,'href="./flagship.css"') === false,
    'no_raw_js_ref'=>strpos($html,'src="./flagship.js"') === false
]);
'''
        result = subprocess.run(['php', '-r', php, str(root / 'fv-ex2-private-preview.php')],
                                capture_output=True, text=True, timeout=15, check=False)
        if result.returncode not in (0, 2):
            raise AssertionError('Guarded PHP composer failed: ' + result.stderr[:600])
        return result.returncode, json.loads(result.stdout)


class CurrentCandidateComposerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('php'):
            raise AssertionError('PHP CLI required; do not claim PHP composer PASS without it')
        if not PLUGIN.is_file() or not STAGING_GATE.is_file():
            raise AssertionError('Exact checkout lacks the PHP composer or staging verifier')
        cls.assets = {name: (ROOT/name).read_bytes() for name in ASSETS}

    def test_exact_seven_chapter_php_preview_composes(self):
        code, data = run_compose(self.assets)
        self.assertEqual(code, 0, data)
        self.assertEqual(data['status'], 'COMPOSED')
        self.assertEqual(data['index_sha256'], hashlib.sha256(self.assets['index.html']).hexdigest())
        for key in ('has_folio','editorial_label','locked_identity','script_at_end',
                    'no_raw_css_ref','no_raw_js_ref'):
            self.assertTrue(data[key], (key, data))

    def test_damaged_exact_banner_rejected(self):
        assets = dict(self.assets)
        old = 'DESIGN CANDIDATE · NOT LIVE'.encode()
        self.assertIn(old, assets['index.html'])
        assets['index.html'] = assets['index.html'].replace(old, b'IMPROPERLY PUBLISHED', 1)
        code, data = run_compose(assets)
        self.assertEqual((code, data['status']), (2, 'BLOCKED'))

    def test_missing_stylesheet_reference_rejected(self):
        assets = dict(self.assets)
        old = b'<link rel="stylesheet" href="./flagship.css">'
        self.assertIn(old, assets['index.html'])
        assets['index.html'] = assets['index.html'].replace(old, b'', 1)
        code, data = run_compose(assets)
        self.assertEqual((code, data['status']), (2, 'BLOCKED'))

    def test_unexpected_remote_script_reference_rejected(self):
        assets = dict(self.assets)
        assets['index.html'] = assets['index.html'].replace(
            b'</body>', b'<script src="https://example.invalid/evil.js"></script></body>', 1)
        code, data = run_compose(assets)
        self.assertEqual((code, data['status']), (2, 'BLOCKED'))

    def test_missing_payload_asset_rejected(self):
        assets = dict(self.assets)
        del assets['reading-trail.js']
        code, data = run_compose(assets)
        self.assertEqual((code, data['status']), (2, 'BLOCKED'))

    def test_staging_gate_does_not_require_retired_direction_controls(self):
        gate = STAGING_GATE.read_text(encoding='utf-8')
        self.assertNotIn("check('direction_visible'", gate)
        self.assertIn("check('locked_visual_identity'", gate)
        self.assertIn("check('franklin_folio_primary_date'", gate)
        self.assertNotIn('data-fv-direction-choice="museum"', gate)


if __name__ == '__main__':
    unittest.main()
