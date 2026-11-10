"""Fail-closed native Focus CTA admission for private Playground.
Mock PHP runtime regression only. NOT real WordPress/Jetpack acceptance.
"""
from __future__ import annotations
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'tools/experience-2/build_page6_playground_bundle.py'
spec = importlib.util.spec_from_file_location('fv_page6_bundle', TOOL)
bp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bp)


def source():
    margins = ''.join('<span class="fv-margin-strip__item">SYNTHETIC</span>' for _ in range(72))
    chapters = '<div data-fv-home-flagship>seven synthetic chapters</div>'
    native = '<section class="fv-focus-cta"><a class="fv-focus-cta__button" href="/focus/">Fieldbook</a></section>'
    return (f'<!-- wp:html -->{margins}<!-- /wp:html -->'
            f'<!-- wp:html -->{chapters}<!-- /wp:html -->'
            f'<!-- wp:html -->{native}<!-- /wp:html -->'
            '<!-- wp:group --><div><!-- wp:jetpack/subscriptions /--></div><!-- /wp:group -->'
            '<!-- wp:html -->other<!-- /wp:html -->')


def execute(raw):
    sha = hashlib.sha256(raw.encode()).hexdigest()
    generated = bp.guarded_php(sha, True, 5, 4)
    generated = generated.replace("require_once '/wordpress/wp-load.php';", '')
    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / 'page.html'
        file.write_text(raw)
        generated = generated.replace('/tmp/fv-ex2-page6-review.blocks.html', str(file))
        mock = """<?php
        define('FV_EX2_LOCAL_ONLY', true);
        function wp_get_environment_type(){ return 'local'; }
        function parse_blocks($s) {
            $b=[];
            for($i=0;$i<4;$i++) $b[]=['blockName'=>'core/html','innerBlocks'=>[]];
            $b[]=['blockName'=>'core/group','innerBlocks'=>[['blockName'=>'jetpack/subscriptions','innerBlocks'=>[]]]];
            return $b;
        }
        function get_page_by_path($s){return false;}
        function wp_slash($s){return $s;}
        function wp_insert_post($v,$e){$GLOBALS['saved']=$v['post_content'];return 44;}
        function is_wp_error($x){return false;}
        function get_post($id){return (object)['post_content'=>$GLOBALS['saved']];}
        function update_post_meta($id,$k,$v){return true;}
        function wp_delete_post($id,$force){return null;}
        ?>"""
        runner = Path(tmp) / 'runner.php'
        runner.write_text(mock + '\n' + generated)
        lint = subprocess.run(['php', '-l', str(runner)], capture_output=True, text=True)
        if lint.returncode:
            raise AssertionError(lint.stderr)
        result = subprocess.run(['php', str(runner)], capture_output=True, text=True)
        return result.returncode, result.stderr


class NativeFocusCustody(unittest.TestCase):
    def assert_rejected(self, content):
        status, error = execute(content)
        self.assertNotEqual(status, 0)
        self.assertIn('native Jetpack/Focus custody failed', error)

    def test_original_relative_link_accepted(self):
        status, error = execute(source())
        self.assertEqual(status, 0, error)

    def test_original_canonical_absolute_link_accepted(self):
        status, error = execute(source().replace('href="/focus/"', 'href="https://finalvestige.com/focus/"'))
        self.assertEqual(status, 0, error)

    def test_rejects_unsafe_original_plus_safe_decoy_in_next_section(self):
        altered = source().replace('href="/focus/"', 'href="https://example.invalid/"')
        altered = altered.replace('</section>', '</section><section><a class="fv-focus-cta__button" href="/focus/">Decoy</a></section>', 1)
        self.assert_rejected(altered)

    def test_rejects_fake_cta_inside_replaceable_flagship(self):
        altered = source().replace('<section class="fv-focus-cta">', '<section class="removed-native-focus">')
        altered = altered.replace('<div data-fv-home-flagship>',
             '<div data-fv-home-flagship><section class="fv-focus-cta"><a class="fv-focus-cta__button" href="/focus/">Decoy</a></section>', 1)
        self.assert_rejected(altered)

    def test_rejects_duplicate_native_sections(self):
        altered = source().replace('</section>',
          '</section><section class="fv-focus-cta"><a class="fv-focus-cta__button" href="/focus/">Duplicate</a></section>', 1)
        self.assert_rejected(altered)

    def test_rejects_action_in_unrelated_section(self):
        altered = source().replace('class="fv-focus-cta__button" href="/focus/"',
                                    'class="irrelevant-button" href="/focus/"', 1)
        altered = altered.replace('</section>',
          '</section><section><a class="fv-focus-cta__button" href="/focus/">Wrong section</a></section>', 1)
        self.assert_rejected(altered)

    def test_redirects_fragments_and_queries_rejected(self):
        for href in ('/focus/?next=evil', '/focus/#fake', '//example.org/focus/',
                     'http://finalvestige.com/focus/'):
            with self.subTest(href=href):
                self.assert_rejected(source().replace('href="/focus/"', f'href="{href}"'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
