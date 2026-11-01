#!/usr/bin/env python3
"""R53 private staging pre-head asset admission; not a real WordPress acceptance."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'integration/fv-ex2-apollo-suite.php'
PROBE = ROOT / 'tests/php_preload_r53_probe.php'

class NestedBlockAssetPreload(unittest.TestCase):
    def test_php_parses_and_page_allowlist_is_strict(self):
        for path in (PLUGIN, PROBE):
            p = subprocess.run(['php','-l',str(path)],capture_output=True,text=True,check=True)
            self.assertIn('No syntax errors',p.stdout)
        p = subprocess.run(['php',str(PROBE)],capture_output=True,text=True,check=True)
        outcomes = json.loads(p.stdout)
        self.assertEqual(len(outcomes),8)
        self.assertTrue(all(outcomes.values()),outcomes)

    def test_head_preload_is_opt_in_not_global(self):
        content = PLUGIN.read_text(encoding='utf-8')
        self.assertIn("'FV_EX2_APOLLO_SUITE_PRELOAD_PAGE_IDS'", content)
        self.assertIn("has_shortcode($post->post_content, 'fv_ex2_apollo_suite')", content)
        self.assertIn('if (!is_singular()) { return; }', content)
        self.assertIn('fv_ex2_apollo_suite_page_opted_in($post)',content)
        self.assertIn("add_action('wp_enqueue_scripts', 'fv_ex2_apollo_suite_pre_enqueue', 22)", content)
        self.assertIn('fv_ex2_apollo_verified_desk()',content)
        self.assertNotIn('wp_insert_post(',content)
        self.assertNotIn('update_option(',content)

    def test_atlas_assets_enqueue_in_pre_head_path(self):
        content = PLUGIN.read_text(encoding='utf-8')
        start = content.index('function fv_ex2_apollo_suite_enqueue(): bool {')
        end = content.index('function fv_ex2_apollo_suite_page_opted_in(',start)
        body = content[start:end]
        self.assertIn("wp_enqueue_style('fv-ex2-apollo-suite'",body)
        self.assertIn("wp_enqueue_style('fv-ex2-research-desk'",body)
        self.assertIn("wp_enqueue_script('fv-ex2-research-desk'",body)
        self.assertIn("function_exists('fv_ex2_atlas_enqueue_assets')",body)
        self.assertIn('fv_ex2_atlas_enqueue_assets();',body)
        self.assertLess(body.index("wp_enqueue_style('fv-ex2-apollo-suite'"),body.index('fv_ex2_atlas_enqueue_assets();'))

if __name__ == '__main__': unittest.main()
