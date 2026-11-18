#!/usr/bin/env python3
"""Contract/adversarial tests against PHP execution; no WordPress or merchant writes."""
import hashlib
import json
import subprocess
import unittest
import contextlib
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/'apollo-r444'
VALID='utm_source=youtube&utm_medium=organic_social&utm_campaign=apollo_pilot_2026_11&utm_content=AbCdE_12345'
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def php(code):
    result=subprocess.run(['php','-r',"require '"+str(ROOT/'bridge.php')+"'; "+code],capture_output=True,text=True)
    return result

def render(query):
    result=php('echo fv_r445_render('+json.dumps(query)+');')
    assert result.returncode==0, result.stderr
    return BeautifulSoup(result.stdout,'html.parser')

def cta(query):
    soup=render(query)
    root=soup.select_one('[data-r444-root]')
    assert root is not None
    links=root.select('.fv-r444__next a')
    assert len(links)==1
    return links[0]['href']

class BridgeTests(unittest.TestCase):
    def test_parent_pinned(self):
        import re
        x=re.search("FV_R445_R444_FILE_SHA256 = '([a-f0-9]+)'",(ROOT/'bridge.php').read_text()).group(1)
        self.assertEqual(x,hashlib.sha256((PARENT/'review_panel.php').read_bytes()).hexdigest())
    def test_php_syntax(self):
        for file in (ROOT/'bridge.php',ROOT/'qa/fixture.php'):
            self.assertEqual(subprocess.run(['php','-l',str(file)],capture_output=True).returncode,0)
    def test_valid_youtube(self):
        u=cta(VALID)
        self.assertEqual(u,DEST+'?'+VALID)
    def test_valid_tiktok(self):
        u=cta(VALID.replace('youtube','tiktok'))
        self.assertTrue(u.startswith(DEST+'?utm_source=tiktok&'))
    def test_zero_query_no_tag(self):self.assertEqual(cta(''),DEST)
    def test_irrelevant_query_no_tag(self):self.assertEqual(cta('q=abc&fbclid=secret'),DEST)
    def test_partial_no_tag(self):self.assertEqual(cta('utm_source=youtube&utm_medium=organic_social'),DEST)
    def test_duplicate_no_tag(self):self.assertEqual(cta(VALID+'&utm_content=OtherAsset'),DEST)
    def test_encoded_duplicate_no_tag(self):self.assertEqual(cta(VALID+'&utm%5Fsource=tiktok'),DEST)
    def test_invalid_source_no_tag(self):self.assertEqual(cta(VALID.replace('youtube','example.com')),DEST)
    def test_unknown_medium_no_tag(self):self.assertEqual(cta(VALID.replace('organic_social','cpc')),DEST)
    def test_other_cluster_no_tag(self):self.assertEqual(cta(VALID.replace('apollo_pilot','mind_pilot')),DEST)
    def test_impossible_month_no_tag(self):self.assertEqual(cta(VALID.replace('2026_11','2026_19')),DEST)
    def test_short_asset_no_tag(self):self.assertEqual(cta(VALID.replace('AbCdE_12345','abc')),DEST)
    def test_user_identifier_no_tag(self):self.assertEqual(cta(VALID.replace('AbCdE_12345','my@email.com')),DEST)
    def test_xss_rejected(self):
        s=render(VALID.replace('AbCdE_12345','%22%3E%3Cscript%3Ealert(1)%3C/script%3E'))
        self.assertEqual(s.select_one('.fv-r444__next a')['href'],DEST)
        self.assertEqual(len(s.select('script')),0)
    def test_query_does_not_leak(self):self.assertNotIn('secret',str(render(VALID+'&email=secret')))
    def test_no_geo_links_or_checkout(self):
        s=render(VALID)
        self.assertEqual(len(s.select('[data-lat],[data-lng],[data-long],[data-geo]')),0)
        self.assertFalse(any('checkout' in a.get('href','') for a in s.select('a')))
    def test_one_cta_nasa_proof(self):
        s=render(VALID)
        self.assertEqual(len(s.select('.fv-r444__next a')),1)
        self.assertEqual(len(s.select('a[href^="https://www.nasa.gov/"]')),5)
        self.assertEqual(len(s.select('[data-r444-record]')),5)
        self.assertEqual(len(s.select('details')),5)
    def test_asset_unchanged(self):
        s=render(VALID)
        self.assertIn('Historical interpretation: review pending',s.get_text(' '))
        self.assertIn('Commercial image rights: not cleared',s.get_text(' '))
    def test_reordering_deterministic(self):
        other='utm_content=AbCdE_12345&utm_medium=organic_social&utm_campaign=apollo_pilot_2026_11&utm_source=youtube'
        self.assertEqual(cta(VALID),cta(other))
    def test_huge_query_rejected(self):self.assertEqual(cta(VALID+'&junk='+'x'*800),DEST)
    def test_asset_length_boundary(self):self.assertIn('utm_content=',cta(VALID.replace('AbCdE_12345','A'+'a'*79)))
    def test_asset_too_long_rejected(self):self.assertEqual(cta(VALID.replace('AbCdE_12345','A'+'a'*80)),DEST)
    def test_plus_in_asset_rejected(self):self.assertEqual(cta(VALID.replace('AbCdE_12345','AA+BB+CC')),DEST)
    def test_fallback_unattributed(self):
        p=php('echo fv_r445_fallback();')
        self.assertEqual(p.returncode,0)
        self.assertIn(DEST,p.stdout)
        self.assertNotIn('utm_',p.stdout)
    def test_cli_no_shortcode_registration(self):
        r=php("echo function_exists('fv_r445_render') ? 'OK' : 'FAIL';")
        self.assertEqual(r.stdout,'OK')
    def test_prod_gate_denies_registration(self):
        code=f'''define('ABSPATH','/');function add_shortcode($n,$f){{echo 'REGISTERED';}}
                  function wp_get_environment_type(){{return 'production';}}
                  define('FV_APOLLO_R445_ENABLE_STAGING',true);
                  require {json.dumps(str(ROOT/'bridge.php'))}; echo 'SAFE';'''
        r=subprocess.run(['php','-r',code],capture_output=True,text=True)
        self.assertEqual(r.stdout,'SAFE')

    def test_parent_mutation_fails_open(self):
        target=PARENT/'review_panel.php';original=target.read_bytes()
        try:
            target.write_bytes(original+b'\n/*tampered*/')
            r=php('echo fv_r445_render('+json.dumps(VALID)+');')
            self.assertIn('Evidence preview unavailable',r.stdout)
            self.assertNotIn('utm_content=',r.stdout)
        finally: target.write_bytes(original)
    def test_css_mutation_fails_open(self):
        target=PARENT/'assets/review-panel.css';original=target.read_bytes()
        try:
            target.write_bytes(original+b'\n/*tampered*/')
            r=php('echo fv_r445_render('+json.dumps(VALID)+');')
            self.assertIn('Evidence preview unavailable',r.stdout)
            self.assertNotIn('utm_content=',r.stdout)
        finally: target.write_bytes(original)
    def test_js_mutation_fails_open(self):
        target=PARENT/'assets/review-panel.js';original=target.read_bytes()
        try:
            target.write_bytes(original+b'\n/*tampered*/')
            r=php('echo fv_r445_render('+json.dumps(VALID)+');')
            self.assertIn('Evidence preview unavailable',r.stdout)
            self.assertNotIn('utm_content=',r.stdout)
        finally: target.write_bytes(original)
    def test_staging_optin_registers_once(self):
        code=f'''define('ABSPATH','/');function add_shortcode($n,$f){{echo $n;}}
                  function wp_get_environment_type(){{return 'staging';}}
                  function add_action($n,$f,$p=10){{echo '|HOOK:'.$n;}}
                  define('FV_APOLLO_R445_ENABLE_STAGING',true);
                  require {json.dumps(str(ROOT/'bridge.php'))};'''
        r=subprocess.run(['php','-r',code],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(r.stdout,'|HOOK:wp_enqueue_scriptsfv_apollo_campaign_bridge')
    def test_staging_without_optin_denies_registration(self):
        code=f'''define('ABSPATH','/');function add_shortcode($n,$f){{echo 'REGISTERED';}}
                  function wp_get_environment_type(){{return 'staging';}}
                  require {json.dumps(str(ROOT/'bridge.php'))}; echo 'SAFE';'''
        r=subprocess.run(['php','-r',code],capture_output=True,text=True)
        self.assertEqual(r.stdout,'SAFE')

if __name__=='__main__':unittest.main()
