#!/usr/bin/env python3
"""Actual PHP 8.x process tests of BOTH derived WordPress MU-plugin entrypoints.

WordPress core is NOT installed in this test. The actual unchanged shortcode
markup is executed after real PHP guard evaluation, with stubbed WP callbacks.
"""
from __future__ import annotations
import hashlib
import io
import os
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile
from make_loopback_guard_variant import derive, digest, GUARD, CANONICAL

ORIGINAL=Path(os.environ.get('FV_EX2_CANONICAL_ZIP', str(Path(__file__).with_name('fv-ex2-local-cli-preflight-guarded.zip'))))
PHP = r'''<?php
$host=$argv[3];$mode=$argv[4];
define('ABSPATH','/FV_EX2_LOCAL_TEST/');
if ($mode==='production') define('WP_ENVIRONMENT_TYPE','production');
elseif ($mode==='development') define('WP_ENVIRONMENT_TYPE','development');
function home_url($path='/') {return $GLOBALS['host'];}
function wp_parse_url($url,$component=-1){return parse_url($url,$component);}
function get_option($name,$default='') {return $GLOBALS['marker']?'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1':'';}
function is_page($slug) {return $GLOBALS['page']==='review' && $slug==='fv-ex2-review';}
function add_action($hook,$fn) {$GLOBALS['actions'][$hook][]=$fn;}
function add_shortcode($name,$fn) {$GLOBALS['shortcodes'][$name]=$fn;}
function wp_register_style($name,$src,$dep,$ver) {}
function wp_enqueue_style($name) {}
function wp_add_inline_style($name,$value) {$GLOBALS['css'].=$value;}
function wp_register_script($name,$src,$deps,$ver,$footer) {}
function wp_enqueue_script($name) {}
function wp_add_inline_script($name,$value) {$GLOBALS['js'].=$value;}
$GLOBALS['host']=$host;$GLOBALS['marker']=$argv[5]==='on';
$GLOBALS['page']=$argv[6];$GLOBALS['actions']=[];$GLOBALS['shortcodes']=[];
$GLOBALS['css']='';$GLOBALS['js']='';
require $argv[1]; require $argv[2];
foreach($GLOBALS['actions']['wp_enqueue_scripts']??[] as $fn) $fn();
$markup=isset($GLOBALS['shortcodes']['fv_ex2_playground']) ? ($GLOBALS['shortcodes']['fv_ex2_playground'])() : '';
echo json_encode(['actions'=>array_map('count',$GLOBALS['actions']),
  'shortcodes'=>array_keys($GLOBALS['shortcodes']),
  'html_length'=>strlen($markup),
  'html_hash'=>hash('sha256',$markup),
  'margins'=>substr_count($markup,'class="fv-margin-strip__item"'),
  'focus'=>substr_count($markup,'https://finalvestige.com/focus/'),
  'img_tags'=>substr_count($markup,'data-fv-archive-img'),
  'css_length'=>strlen($GLOBALS['css']),'js_length'=>strlen($GLOBALS['js']),
  'css_hash'=>hash('sha256',$GLOBALS['css']),'js_hash'=>hash('sha256',$GLOBALS['js'])],JSON_UNESCAPED_SLASHES);
'''

class IsolationGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_blob=ORIGINAL.read_bytes()
        cls.variant,cls.receipt=derive(cls.source_blob)
        cls.data={}
        with zipfile.ZipFile(io.BytesIO(cls.source_blob)) as z:
            cls.original_data={path:z.read(path) for path in CANONICAL}
        with zipfile.ZipFile(io.BytesIO(cls.variant)) as z:
            for path in CANONICAL: cls.data[path]=z.read(path)
            cls.custody=json.loads(z.read('SOURCE_CUSTODY.json'))

    def run_php(self,host='http://127.0.0.1:8888/',mode='local',marker='on',page='review',guarded=True):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            for i,blob in enumerate((self.data if guarded else self.original_data).values()): (d/f'p{i}.php').write_bytes(blob)
            (d/'runner.php').write_text(PHP)
            r=subprocess.run(['php',str(d/'runner.php'),str(d/'p0.php'),str(d/'p1.php'),host,mode,marker,page],capture_output=True,text=True,timeout=12)
            self.assertEqual(r.returncode,0,r.stderr)
            return json.loads(r.stdout)

    def assert_refused(self,**kwargs):
        d=self.run_php(**kwargs)
        self.assertEqual(d['shortcodes'],[],d)
        self.assertFalse(d['actions'],d)
        self.assertEqual(d['html_length'],0,d)

    def test_01_local_loopback_marker_and_page_permit_actual_php(self):
        d=self.run_php()
        self.assertEqual(d['shortcodes'],['fv_ex2_playground'])
        self.assertEqual(d['actions'],{'wp_enqueue_scripts':1,'wp_footer':1})
        self.assertEqual((d['margins'],d['focus'],d['img_tags']),(72,5,2))
        self.assertGreater(d['html_length'],45000)
        self.assertGreater(d['css_length'],50000)
        self.assertGreater(d['js_length'],10000)
        self.assertEqual(d['html_hash'],'baf26bcaddbf1b86b90f0065e1d68fbd856be03027ecd9d14ebc0ada60a21b1d')
        self.assertEqual(d['css_hash'],'152bfd327325997bee65191028501467292c70bc8573a39b439a5e6d49bc8afb')
        self.assertEqual(d['js_hash'],'67230d93773a46fb2942368d5e13fb127788bf4504bb8ff106c317fd4af5b6ee')

    def test_02_site_mapped_to_actual_prod_refused_even_marker_copied(self):
        self.assert_refused(host='https://finalvestige.com/',mode='local',marker='on')

    def test_02b_before_guard_admitted_unsafe_mapped_host_with_marker(self):
        before=self.run_php(host='https://finalvestige.com/',guarded=False)
        after=self.run_php(host='https://finalvestige.com/',guarded=True)
        self.assertEqual(before['shortcodes'],['fv_ex2_playground'])
        self.assertEqual(after['shortcodes'],[])

    def test_03_explicit_prod_wp_environment_refused_on_loopback(self):
        self.assert_refused(mode='production')

    def test_04_evil_localhost_suffix_refused(self):
        for host in ['https://localhost.evil.example/','https://localhost.attacker.tld/','https://totallynotlocalhost/']:
            with self.subTest(host=host):self.assert_refused(host=host)

    def test_05_valid_loopback_forms(self):
        for host in ['http://localhost:8899/','http://127.0.0.1:9000/', 'http://alice.localhost:7777/','http://LOCALHOST.:9001/','http://[::1]:9999/']:
            with self.subTest(host=host):self.assertEqual(self.run_php(host=host)['focus'],5)

    def test_06_absent_activation_marker_refused(self):
        self.assert_refused(marker='off')

    def test_07_wrong_page_omits_assets_and_shortcode_markup(self):
        d=self.run_php(page='other')
        self.assertEqual((d['html_length'],d['css_length'],d['js_length']),(0,0,0))

    def test_08_explicit_development_accepted_only_on_loopback(self):
        self.assertEqual(self.run_php(mode='development')['margins'],72)
        self.assert_refused(host='https://finalvestige.com/',mode='development')

    def test_09_package_deterministic(self):
        clone,report=derive(self.source_blob)
        self.assertEqual(clone,self.variant)
        self.assertEqual(report,self.receipt)

    def test_10_canonical_source_hash_drift_rejected(self):
        with self.assertRaisesRegex(ValueError,'source ZIP SHA-256 mismatch'):
            derive(self.source_blob+b'X')

    def test_11_retains_original_blueprint_and_protected_content(self):
        with zipfile.ZipFile(io.BytesIO(self.source_blob)) as before,zipfile.ZipFile(io.BytesIO(self.variant)) as after:
            self.assertEqual(before.read('blueprint.json'),after.read('blueprint.json'))
            self.assertEqual(before.read('REVIEW.txt'),after.read('REVIEW.txt'))
            for k in CANONICAL:
                a=before.read(k);b=after.read(k)
                self.assertEqual(b,a.replace(b"if (!defined('ABSPATH')) { exit; }\n",b"if (!defined('ABSPATH')) { exit; }\n"+GUARD,1))

    def test_12_source_custody_reconciles_both_plugins(self):
        for path in CANONICAL:
            self.assertEqual(self.custody['files_sha256'][path],digest(self.data[path]))
        self.assertEqual(self.custody['guarded_local_variant']['canonical_bundle_sha256'],digest(self.source_blob))

if __name__=='__main__':unittest.main()
