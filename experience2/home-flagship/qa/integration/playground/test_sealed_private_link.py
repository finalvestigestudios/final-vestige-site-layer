"""Real PHP smoke test for the sealed-preview shortcode's authorized top-level route.

Exercises the exact WordPress plugin PHP template under minimal WordPress-compatible
function stubs, not an actual WordPress / Playground runtime. Safe: no HTTP/CMS writes.
"""
import os
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

PLUGIN = (Path(__file__).resolve().parent / "../sealed/fv-ex2-sealed-preview.php").resolve()
STUB = r'''<?php
define('ABSPATH', '/local-test/');
if (getenv('FV_FLAG') === '1') { define('FV_EX2_ALLOW_PREVIEW', true); }
function wp_get_environment_type(){ return getenv('FV_ENV') ?: 'production'; }
function is_user_logged_in(){ return getenv('FV_LOGIN') === '1'; }
function current_user_can($role){ return $role === 'edit_pages' && getenv('FV_EDIT') === '1'; }
function add_shortcode($shortcode, $callback){}
function add_action($action, $callback){}
function admin_url($path){ return 'https://local.test/wp-admin/' . $path; }
function wp_create_nonce($action){ return $action === 'fv_ex2_sealed_render' ? 'LOCAL_TEST_NONCE' : ''; }
function add_query_arg($a, $url){ return $url . '?' . http_build_query($a); }
function esc_url($url){ return htmlspecialchars($url, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
require $argv[1];
echo fv_ex2_sealed_shortcode();
'''

class TagCollector(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

@unittest.skipUnless(shutil.which('php'), 'PHP binary needed; cannot certify without it')
class SealedPreviewTests(unittest.TestCase):
    def run_php(self, **override):
        env = os.environ.copy()
        env.update({'FV_FLAG':'1','FV_ENV':'local','FV_LOGIN':'1','FV_EDIT':'1'})
        env.update(override)
        with tempfile.TemporaryDirectory() as d:
            stub = Path(d)/'stub.php'
            stub.write_text(STUB, encoding='utf8')
            return subprocess.run(['php',str(stub),str(PLUGIN)], capture_output=True,
                                  text=True,env=env,check=True).stdout

    def test_php_syntax(self):
        p=subprocess.run(['php','-l',str(PLUGIN)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)

    def test_editor_gets_real_top_level_link_and_sealed_frame(self):
        html=self.run_php()
        t=TagCollector();t.feed(html)
        a=[x for tag,x in t.tags if tag=='a']
        iframe=[x for tag,x in t.tags if tag=='iframe']
        self.assertEqual(len(a),1)
        self.assertEqual(len(iframe),1)
        self.assertEqual(a[0]['target'],'_blank')
        self.assertEqual(a[0]['rel'],'noopener noreferrer')
        self.assertEqual(a[0]['referrerpolicy'],'no-referrer')
        self.assertEqual(a[0]['href'],iframe[0]['src'])
        self.assertIn('action=fv_ex2_sealed_render',a[0]['href'])
        self.assertIn('LOCAL_TEST_NONCE',a[0]['href'])
        self.assertEqual(iframe[0]['sandbox'],'allow-scripts allow-popups')
        self.assertNotIn('allow-same-origin',iframe[0]['sandbox'])

    def test_fail_closed_without_login(self):
        self.assertEqual(self.run_php(FV_LOGIN='0'),'')
    def test_fail_closed_without_editor(self):
        self.assertEqual(self.run_php(FV_EDIT='0'),'')
    def test_fail_closed_in_production(self):
        self.assertEqual(self.run_php(FV_ENV='production'),'')
    def test_fail_closed_without_feature_flag(self):
        self.assertEqual(self.run_php(FV_FLAG='0'),'')

    def test_no_public_renderer(self):
        src=PLUGIN.read_text(encoding='utf8')
        self.assertIn("add_action('wp_ajax_fv_ex2_sealed_render'",src)
        self.assertNotIn("add_action('wp_ajax_nopriv_",src)
        self.assertNotIn('allow-same-origin',src.split('sandbox="')[1].split('"')[0])

if __name__=='__main__': unittest.main()
