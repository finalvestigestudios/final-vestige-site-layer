#!/usr/bin/env python3
"""R189 fail-open/cache invariant source tests; do not treat as installed WP tests."""
import hashlib, subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r189 import build, PIN, DEST, JS
class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt=build(reuse=True)
        cls.dist=ROOT/'dist'
        cls.php=(cls.dist/'fv-ex2-apollo-r189.php').read_text()
        cls.html=(cls.dist/'templates/atlas-fragment.html').read_text()
    def test_byte_pinned_source_custody(self):
        for kind,path in [('html','templates/atlas-fragment.html'),('css','assets/atlas-scoped.css')]:
            self.assertEqual(hashlib.sha256((self.dist/path).read_bytes()).hexdigest(),PIN[kind])
    def test_no_server_side_visitor_input(self):
        self.assertNotIn('$_GET',self.php)
        self.assertNotIn('campaign_handoff(',self.php)
        self.assertIn('return $html;',self.php)
    def test_reading_cta_unchanged_in_shared_html(self):
        self.assertEqual(self.html.count('<a class="cta" href="'+DEST+'">'),1)
    def test_optional_js_immutable_and_pinned(self):
        js=(self.dist/'assets/campaign-handoff.js').read_bytes()
        self.assertEqual(js.decode(),JS)
        self.assertIn(hashlib.sha256(js).hexdigest(),self.php)
    def test_no_analytics_storage_or_commerce(self):
        js=JS.lower()
        for bad in ('localstorage','sessionstorage','document.cookie','sendbeacon','fetch(', 'gtag(', 'fbq(', 'pixel(', 'checkout', 'awin1.com'):
            self.assertNotIn(bad,js)
    def test_no_cms_mutations(self):
        for banned in ('wp_insert_post(', 'update_option(', 'wp_remote_post(', 'wp_update_post('):
            self.assertNotIn(banned,self.php)
    def test_no_new_remote_images(self):
        self.assertNotIn('<img ',self.html.lower())
    def test_exact_cta_static_failopen(self):
        self.assertIn('function fv_ex2_r189_fallback()',self.php)
        self.assertIn('Read the original investigation',self.php)
    def test_real_php_render_is_cache_invariant(self):
        shim=str(ROOT/'qa/wordpress_mock_render.php')
        php=str(self.dist/'fv-ex2-apollo-r189.php')
        one='utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo_lf_001'
        two='utm_source=tiktok&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo_sf_002'
        def output(query):
            p=subprocess.run(['php',shim,php,query],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            return p.stdout
        a,b=output(one),output(two)
        self.assertEqual(a,b)
        self.assertIn('No conclusively identified ignition source',a)
        self.assertIn('S67-21294',a)
        self.assertNotIn('utm_source',a)
    def test_prior_server_cache_hazard_is_reproducible(self):
        shim=str(ROOT/'qa/wordpress_mock_render.php')
        old=str(ROOT.parent/'apollo-r188/dist/fv-ex2-apollo-r188.php')
        one='utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo_lf_001'
        two='utm_source=tiktok&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo_sf_002'
        a=subprocess.run(['php',shim,old,one],capture_output=True,text=True,check=True).stdout
        b=subprocess.run(['php',shim,old,two],capture_output=True,text=True,check=True).stdout
        self.assertNotEqual(a,b, 'R188 unexpectedly cache invariant; investigate fixture')
        self.assertIn('utm_source=youtube',a)
        self.assertIn('utm_source=tiktok',b)
    def test_php_syntax(self):
        r=subprocess.run(['php','-l',str(self.dist/'fv-ex2-apollo-r189.php')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
    def test_js_syntax(self):
        r=subprocess.run(['node','--check',str(self.dist/'assets/campaign-handoff.js')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
if __name__=='__main__': unittest.main(verbosity=2)
