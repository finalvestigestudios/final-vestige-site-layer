#!/usr/bin/env python3
"""Real-PHP regression for WordPress' documented wp_insert_post unslashing.

Tests the actual imported Assembler template PHP function and the real public-safe
Gutenberg markup. PHP functions are local stubs; this is NOT a native WP render.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
PHP = HERE / 'apply_local_parity.php'
MANIFEST = HERE / 'assembler-public-safe.json'


def get_function_source() -> str:
    php = PHP.read_text(encoding='utf-8')
    match = re.search(r'(?s)(function fv_local_parity_insert_verified\(\$record, \$old\)\s*\{.*?\n\})\n\$ids\s*=\s*\[\];', php)
    if match is None:
        raise AssertionError('Actual PHP persistence function must exist unchanged in source')
    return match.group(1)


def actual_markup() -> dict[str, str]:
    data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    return data['template_content']


def php_case(name: str, *, remove_slashing: bool = False, tamper: bool = False) -> subprocess.CompletedProcess[str]:
    func = get_function_source()
    if remove_slashing:
        previous = "'post_content'=>wp_slash($record['content'])"
        if previous not in func:
            raise AssertionError('Cannot apply red-control mutation: slashing guard missing')
        func = func.replace(previous, "'post_content'=>$record['content']", 1)
    markup = actual_markup()[name]
    data = base64.b64encode(markup.encode('utf-8')).decode('ascii')
    # Mock WordPress' documented wp_unslash behavior. No CMS/network/plugins.
    # addslashes / stripslashes are exact PHP primitives, not string mockups.
    source = '''<?php
    error_reporting(E_ALL);
    function wp_slash($value) { return addslashes($value); }
    function is_wp_error($value) { return false; }
    function wp_insert_post($args, $wp_error = false) {
      $source = stripslashes($args['post_content']);
      if (defined('TEST_TAMPER') && TEST_TAMPER) $source .= 'UNREVIEWED_EDIT';
      $GLOBALS['stored'] = (object)[
        'post_content' => $source,
        'post_type' => $args['post_type'],
        'post_status' => $args['post_status'],
        'post_name' => $args['post_name'] ];
      return 777;
    }
    function wp_set_object_terms($id, $term, $taxonomy) { return [1]; }
    function taxonomy_exists($taxonomy) { return true; }
    function update_post_meta($id, $name, $value) { return true; }
    function get_post($id) { return $GLOBALS['stored']; }
    function get_post_meta($id, $name, $single) { return '1'; }
    function wp_get_object_terms($id, $taxonomy, $args) {
      return $taxonomy === 'wp_theme' ? ['assembler'] : ['header'];
    }
    '''
    source += '\n' + func + '\n'
    source += "define('TEST_TAMPER', " + ('true' if tamper else 'false') + ");\n"
    source += "$exact = base64_decode('" + data + "', true);\n"
    source += "$record = ['type'=>'wp_template_part','slug'=>'header','content'=>$exact,'area'=>'header'];\n"
    source += "$id = fv_local_parity_insert_verified($record, null);\n"
    source += "if ($id !== 777 || $GLOBALS['stored']->post_content !== $exact) throw new RuntimeException('Unexpected stored bytes');\n"
    source += "echo 'PHP_READBACK_BYTE_IDENTICAL sha256=' . hash('sha256', $GLOBALS['stored']->post_content);\n"
    with tempfile.TemporaryDirectory(prefix='fv-php-persistence-') as work:
        source_path = Path(work) / 'probe.php'
        source_path.write_text(source, encoding='utf-8')
        syntax = subprocess.run(['php', '-l', str(source_path)], text=True, capture_output=True, timeout=10)
        if syntax.returncode != 0:
            raise AssertionError(syntax.stderr or syntax.stdout)
        return subprocess.run(['php', str(source_path)], text=True, capture_output=True, timeout=10)


class WordPressTemplatePersistence(unittest.TestCase):
    def test_real_public_template_contains_unslash_sensitive_backslashes(self):
        markup = actual_markup()
        self.assertGreaterEqual(markup['header'].count('\\'), 1)
        self.assertGreaterEqual(markup['overlay'].count('\\'), 1)

    def test_throwaway_wordpress_admin_context_is_behind_local_host_gate(self):
        source = PHP.read_text(encoding='utf-8')
        guard = source.index("wp_get_environment_type() !== 'local'")
        admin = source.index('wp_set_current_user(1);')
        insert = source.index('function fv_local_parity_insert_verified')
        self.assertLess(guard, admin)
        self.assertLess(admin, insert)
        self.assertIn("is_multisite()", source[guard:admin])
        self.assertIn("current_user_can('unfiltered_html')", source[admin:insert])
        self.assertIn("get_current_user_id() !== 1", source[admin:insert])

    def test_source_explicitly_slashes_before_wp_insert_post(self):
        self.assertIn("'post_content'=>wp_slash($record['content'])", get_function_source())
        self.assertIn("$saved->post_content !== $record['content']", get_function_source())

    def test_saved_wordpress_header_bytes_are_identical(self):
        result = php_case('header')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PHP_READBACK_BYTE_IDENTICAL sha256=', result.stdout)

    def test_saved_wordpress_overlay_bytes_are_identical(self):
        result = php_case('overlay')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PHP_READBACK_BYTE_IDENTICAL sha256=', result.stdout)

    def test_old_raw_input_is_rejected_after_wp_unslash(self):
        result = php_case('header', remove_slashing=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('local template readback differs', result.stderr)

    def test_sanitizer_or_hook_mutation_is_rejected(self):
        result = php_case('header', tamper=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('local template readback differs', result.stderr)



class CliStartupDiagnostics(unittest.TestCase):
    @staticmethod
    def _script():
        import importlib.util
        path = HERE.parent / 'ci_ex2_wp_playground.py'
        spec = importlib.util.spec_from_file_location('fv_isolated_cli_diagnostics', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_private_log_failure_excerpt_redacts_paths_urls_and_passwords(self):
        module = self._script()
        with tempfile.TemporaryDirectory(prefix='fv-cli-log-test-') as temp:
            path = Path(temp) / 'private.log'
            path.write_text(
                "An Error: failed to read /home/runner/confidential/example.php\n"
                "Error: cannot download https://example.org/a?private=1\n"
                "Error: password=do-not-disclose\n", encoding='utf-8')
            summary = module.safe_cli_failure_excerpt(path)
        self.assertIn('failed to read [LOCAL_PATH]', summary)
        self.assertIn('[URL]', summary)
        self.assertNotIn('/home/runner/', summary)
        self.assertNotIn('example.org', summary)
        self.assertNotIn('do-not-disclose', summary)
        self.assertNotIn('password', summary)

    def test_private_log_classifies_exact_template_corruption_without_leaking_source(self):
        module = self._script()
        with tempfile.TemporaryDirectory(prefix='fv-cli-log-test-') as temp:
            path = Path(temp) / 'private.log'
            path.write_text('PHP Error: REFUSED: local template readback differs: header\n', encoding='utf-8')
            self.assertEqual(module.diagnose_private_cli_log(path), 'WP_SAVED_TEMPLATE_BYTES_CHANGED')
            self.assertIn('readback differs', module.safe_cli_failure_excerpt(path))


    def test_local_debug_blueprint_is_separate_and_loopback_only(self):
        module = self._script()
        with tempfile.TemporaryDirectory(prefix='fv-blueprint-probe-') as td:
            stage = Path(td) / 'stage'
            secret = Path(td) / 'secrets'
            stage.mkdir()
            secret.mkdir()
            blueprint = stage / 'playground-blueprint.json'
            original = {'steps': [{'step': 'defineWpConfigConsts', 'consts': {
                'WP_ENVIRONMENT_TYPE': 'local', 'FV_EX2_ALLOW_PREVIEW': True,
                'WP_DEBUG_DISPLAY': False}},
                {'step':'activateTheme', 'themeFolderName':'assembler'}]}
            blueprint.write_text(json.dumps(original))
            argv = ['npx','@wp-playground/cli@3.1.61','server',
                    '--blueprint='+str(blueprint),'--port=9400',
                    '--mount='+str(stage/'assembler')+':/wordpress/wp-content/themes/assembler',
                    '--mount='+str(stage/'plugin')+':/wordpress/wp-content/plugins/fv-ex2-private-preview',
                    '--mount='+str(stage/'parity')+':/wordpress/wp-content/uploads/fv-ex2-parity']
            result = module.build_local_debug_blueprint_argv(stage, argv, secret)
            self.assertEqual(result.count('--port=9401'), 1)
            self.assertEqual(result.count('--port=9400'), 0)
            self.assertEqual(len([x for x in result if x.startswith('--mount=')]), 3)
            diagnostic = json.loads((secret/'local-debug-blueprint.json').read_text())
            self.assertEqual(diagnostic['steps'][0]['consts']['WP_ENVIRONMENT_TYPE'], 'local')
            self.assertTrue(diagnostic['steps'][0]['consts']['WP_DISABLE_FATAL_ERROR_HANDLER'])
            self.assertTrue(diagnostic['steps'][0]['consts']['WP_DEBUG_DISPLAY'])
            self.assertFalse(json.loads(blueprint.read_text())['steps'][0]['consts']['WP_DEBUG_DISPLAY'])
            original['steps'][0]['consts']['WP_ENVIRONMENT_TYPE'] = 'production'
            blueprint.write_text(json.dumps(original))
            with self.assertRaisesRegex(ValueError, 'outside isolated local'):
                module.build_local_debug_blueprint_argv(stage, argv, secret)

    def test_missing_private_log_fails_to_specific_nonsecret_marker(self):
        module = self._script()
        self.assertEqual(module.safe_cli_failure_excerpt(HERE / 'nonexistent-private-stdout.log'), 'NO_PRIVATE_LOG')


if __name__ == '__main__':
    unittest.main()
