"""Fail-closed unit tests for the integration checker and staging package.

The generated local test page is a synthetic fixture, NOT the exact GitHub
homepage. It is used to exercise error detection and packaging behavior.
"""
from __future__ import annotations
import importlib.util,sys,tempfile,shutil,re,zipfile,json,hashlib,subprocess,os
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/"qa/integration"
SOURCE_ROOT=Path(os.environ.get("FV_EX2_SOURCE_ROOT",str(ROOT))).resolve()
sys.path.insert(0,str(QA))
from check_contract import scan,ASSETS
from build_staging_zip import build,PREFIX

class GateTests(unittest.TestCase):

    def work(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        root=Path(t.name)/"src";root.mkdir()
        for n in ASSETS:shutil.copyfile(SOURCE_ROOT/n,root/n)
        return root

    def test_checkout_passes_21_contract_checks(self):
        check,obs,errors=scan(SOURCE_ROOT)
        self.assertEqual(len(check),21)
        self.assertEqual(len(errors),0)

    def test_missing_asset_fails_closed(self):
        root=self.work();(root/"observer-lab.js").unlink()
        _,_,errors=scan(root)
        self.assertTrue(any('exact_asset_set_present' in e for e in errors))
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):build(root,QA,Path(d)/'wrong.zip','fixture-only')

    def test_duplicate_anchor_caught(self):
        root=self.work();h=root/"index.html";h.write_text(h.read_text().replace('id="fv-hf-evidence"','id="fv-hf-chronicle"'))
        _,_,errors=scan(root)
        self.assertTrue(any('unique_dom_ids' in e for e in errors))

    def test_unapproved_direct_affiliate_link_caught(self):
        root=self.work();h=root/"index.html";h.write_text(h.read_text().replace('</body>','<a href="https://hop.clickbank.net/unsafe">BUY</a></body>'))
        _,_,errors=scan(root)
        self.assertTrue(any('no_web_form_or_affiliate_checkout' in e for e in errors))

    def test_js_only_hidden_source_caught(self):
        root=self.work();h=root/"index.html";h.write_text(h.read_text().replace('id="fv-hf-inquiry"','id="missing-inquiry"'))
        _,_,errors=scan(root)
        self.assertTrue(any('seven_chapters_resolve' in e for e in errors))

    def test_remote_script_or_style_caught(self):
        root=self.work();h=root/"index.html";h.write_text(h.read_text().replace('src="./flagship.js"','src="https://external.invalid/flagship.js"'))
        _,_,errors=scan(root)
        self.assertTrue(any('only_expected_local_scripts' in e for e in errors))

    def test_wordpress_zip_contains_exact_asset_bytes_and_manifest(self):
        root=self.work()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'staging.zip';m=build(root,QA,path,'fixture-not-a-git-commit')
            with zipfile.ZipFile(path) as z:
                names=z.namelist()
                self.assertEqual(len(names),len(ASSETS)+3)
                self.assertIn(f'{PREFIX}/assets/index.html.txt',names)
                self.assertNotIn(f'{PREFIX}/assets/index.html',names)
                self.assertIn(f'{PREFIX}/fv-ex2-preview.php',names)
                self.assertEqual(z.read(f'{PREFIX}/assets/observer-lab.js'),(root/'observer-lab.js').read_bytes())
                self.assertEqual(m['source_sha256']['index.html'],hashlib.sha256((root/'index.html').read_bytes()).hexdigest())
                self.assertIn('DO_NOT_ACTIVATE_ON_PRODUCTION',m['status'])

    def test_php_compiles(self):
        x=subprocess.run(['php','-l',str(QA/'fv-ex2-preview.php')],capture_output=True,text=True)
        self.assertEqual(x.returncode,0,x.stderr)

    def test_wordpress_plugin_never_registers_public_ajax_or_mutates_cms(self):
        s=(QA/'fv-ex2-preview.php').read_text()
        self.assertNotRegex(s,r'add_action\s*\(\s*[\'\"]wp_ajax_nopriv_')
        for phrase in ['wp_update_post(', 'update_option(', 'wp_insert_post(', 'wp_insert_user(', 'wp_redirect(', 'wp_set_object_terms(']:
            self.assertNotIn(phrase,s)
        self.assertIn("'staging', 'development', 'local'",s)
        self.assertIn("FV_EX2_ALLOW_PREVIEW",s)

    def test_runtime_wordpress_capability_gate(self):
        php=str(QA/'fv-ex2-preview.php')
        # Harness invokes only the safe shortcode; never invokes the Ajax echo+exit route.
        stub='''<?php
        define('ABSPATH','/');define('FV_EX2_ALLOW_PREVIEW',true);
        $ENVIRONMENT='production';$LOGGED=true;$EDITOR=true;
        function add_shortcode($n,$f){$GLOBALS['shortcode']=$f;}
        function add_action($n,$f){$GLOBALS['actions'][$n]=$f;}
        function wp_get_environment_type(){return $GLOBALS['ENVIRONMENT'];}
        function is_user_logged_in(){return $GLOBALS['LOGGED'];}
        function current_user_can($x){return $GLOBALS['EDITOR'];}
        function add_query_arg($q,$u){return $u.'?action='.$q['action'];}
        function wp_create_nonce($n){return 'stub-only';}
        function admin_url($p){return 'https://private-staging.invalid/wp-admin/'.$p;}
        function esc_url($u){return htmlspecialchars($u,ENT_QUOTES);}
        require '__FILE__';
        if ($GLOBALS['shortcode'] !== 'fv_ex2_preview_shortcode') exit(31);
        if (fv_ex2_preview_shortcode([]) !== '') exit(32);
        $ENVIRONMENT='staging';$LOGGED=false;
        if (fv_ex2_preview_shortcode([]) !== '') exit(33);
        $LOGGED=true;$EDITOR=false;
        if (fv_ex2_preview_shortcode([]) !== '') exit(34);
        $EDITOR=true;$out=fv_ex2_preview_shortcode([]);
        if (strpos($out,'<iframe')===false || strpos($out,'sandbox="allow-scripts allow-popups"')===false)exit(35);
        if (isset($GLOBALS['actions']['wp_ajax_nopriv_fv_ex2_render_preview']))exit(36);
        echo 'gates pass';
        '''.replace('__FILE__',php.replace("'","\\'"))
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'stub.php';f.write_text(stub)
            x=subprocess.run(['php',str(f)],capture_output=True,text=True)
            self.assertEqual(x.returncode,0,x.stderr+"\n"+x.stdout)
            self.assertIn('gates pass',x.stdout)

if __name__=='__main__':unittest.main()
