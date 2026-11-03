#!/usr/bin/env python3
"""Synthetic PHP fault-injection regression checks for Playground cleanup.

No WordPress installation, production source, live URL, or credentials.
This does NOT establish real WordPress persistence or Gutenberg editor behavior.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE / "playground_core_save_readback.php"

MOCK_WP = r'''<?php
function wp_json_encode($value) { return json_encode($value); }
function home_url() { return getenv('FV_TEST_HOST') ?: 'http://localhost/'; }
function wp_parse_url($value, $component) { return parse_url($value, $component); }
function parse_blocks($text) { return array(array('blockName'=>'core/html'),array('blockName'=>'core/html')); }
function wp_slash($value) { return $value; }
function get_users($args) { return array((object)array('ID'=>1)); }
function wp_set_current_user($id) { }
function current_user_can($cap) { return getenv('FV_TEST_CASE') !== 'deny_unfiltered_html'; }
function wp_insert_post($args, $return_error) {
    if (getenv('FV_TEST_CASE') === 'insert_error') return false;
    file_put_contents(__DIR__ . '/was_saved', $args['post_content']);
    return 123;
}
function is_wp_error($value) { return false; }
function clean_post_cache($id) {}
function get_post_field($name, $id, $context) {
    if (getenv('FV_TEST_CASE') === 'readback_exception') throw new RuntimeException('synthetic');
    if (getenv('FV_TEST_CASE') === 'readback_null') return null;
    if (getenv('FV_TEST_CASE') === 'readback_drift') return file_get_contents(__DIR__ . '/was_saved') . '!';
    return file_get_contents(__DIR__ . '/was_saved');
}
function get_post_status($id) { return 'draft'; }
function wp_delete_post($id, $force) {
    file_put_contents(__DIR__ . '/delete_attempted', 'yes');
    if (getenv('FV_TEST_CASE') === 'delete_error') throw new RuntimeException('synthetic delete');
    if (getenv('FV_TEST_CASE') === 'delete_false') return false;
    unlink(__DIR__ . '/was_saved');
    return array('ID'=>$id);
}
function get_post($id) { return file_exists(__DIR__ . '/was_saved') ? array('ID'=>$id) : null; }
function get_bloginfo($field) { return '6.8'; }
'''

def synthetic_fixture():
    spans = ''.join(
        f'<span class="fv-margin-strip__item" style="--i:{i}">Synthetic {i}</span>'
        for i in range(72)
    )
    return ("<!-- wp:html --><style>/* FV-EX2 PAGE6 REVIEW-ONLY */</style>"
            + spans + '<!-- /wp:html -->\n<!-- wp:html -->'
            + '<div class="fv-hf__chapter-nav">Focus Fieldbook</div>'
            + '<!-- /wp:html --><!-- wp:jetpack/subscriptions /-->')


class ProbeCleanup(unittest.TestCase):
    def run_case(self, test_case='success', *, host='http://localhost', marker=True):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'wp-content').mkdir()
            shutil.copy2(PROBE, root / 'fv_ex2_qa_once.php')
            (root / 'wp-load.php').write_text(MOCK_WP, encoding='utf-8')
            (root / 'wp-content/fv-ex2-synthetic-candidate.html').write_text(
                synthetic_fixture(), encoding='utf-8'
            )
            if marker:
                (root / 'wp-content/fv-ex2-synthetic-only.marker').write_text(
                    'SYNTHETIC_TEST_FIXTURE_ONLY\n', encoding='utf-8'
                )
            env = dict(os.environ, FV_TEST_CASE=test_case, FV_TEST_HOST=host)
            run = subprocess.run(
                ['php', str(root / 'fv_ex2_qa_once.php')], cwd=root,
                capture_output=True, text=True, timeout=8, env=env
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(run.stdout)
            return result, (root / 'delete_attempted').exists(), (root / 'was_saved').exists()

    def test_success_requires_cleanup_before_pass(self):
        r, attempted, remains = self.run_case()
        self.assertEqual(r['result'], 'PASS')
        self.assertEqual(r['release'], 'HOLD')
        self.assertEqual(r['cleanup'], {'attempted': True, 'deleted': True, 'verified_absent': True})
        self.assertTrue(attempted)
        self.assertFalse(remains)

    def test_readback_exception_always_removes_draft(self):
        r, attempted, remains = self.run_case('readback_exception')
        self.assertEqual(r['result'], 'FAIL')
        self.assertTrue(attempted)
        self.assertFalse(remains)
        self.assertTrue(r['cleanup']['verified_absent'])

    def test_readback_null_always_removes_draft(self):
        r, attempted, remains = self.run_case('readback_null')
        self.assertEqual(r['result'], 'FAIL')
        self.assertTrue(attempted)
        self.assertFalse(remains)

    def test_changed_readback_fails_without_residual_draft(self):
        r, attempted, remains = self.run_case('readback_drift')
        self.assertEqual(r['result'], 'FAIL')
        self.assertTrue(attempted)
        self.assertFalse(remains)

    def test_failed_deletion_never_produces_pass(self):
        r, attempted, remains = self.run_case('delete_false')
        self.assertEqual(r['result'], 'FAIL')
        self.assertEqual(r['reason'], 'Disposable draft cleanup could not be verified')
        self.assertTrue(attempted)
        self.assertTrue(remains)

    def test_deletion_exception_never_produces_pass(self):
        r, attempted, remains = self.run_case('delete_error')
        self.assertEqual(r['result'], 'FAIL')
        self.assertTrue(attempted)
        self.assertTrue(remains)

    def test_failed_insert_never_produces_pass(self):
        r, attempted, remains = self.run_case('insert_error')
        self.assertEqual(r['result'], 'FAIL')
        self.assertFalse(r['cleanup']['attempted'])
        self.assertFalse(attempted)
        self.assertFalse(remains)

    def test_production_hostname_refused_before_write(self):
        r, attempted, remains = self.run_case(host='https://finalvestige.com/')
        self.assertEqual(r['result'], 'FAIL')
        self.assertFalse(attempted)
        self.assertFalse(remains)

    def test_denied_unfiltered_html_never_writes(self):
        r, attempted, remains = self.run_case('deny_unfiltered_html')
        self.assertEqual(r['result'], 'FAIL')
        self.assertFalse(attempted)
        self.assertFalse(remains)

    def test_synthetic_marker_required_before_write(self):
        r, attempted, remains = self.run_case(marker=False)
        self.assertEqual(r['result'], 'FAIL')
        self.assertFalse(attempted)
        self.assertFalse(remains)

if __name__ == '__main__':
    unittest.main()
