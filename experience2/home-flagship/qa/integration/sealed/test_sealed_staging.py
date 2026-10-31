import hashlib, json, subprocess, sys, tempfile, unittest, zipfile
from pathlib import Path
from build_sealed_staging_zip import build, FILES, ZIPROOT

ROOT=Path(__file__).resolve().parents[3]
HEAD='c1c00acfa79664163214e1f424a8868e64aa2ee3'

class SealedPreview(unittest.TestCase):
    def test_php_template_syntax(self):
        p=subprocess.run(['php','-l',str(Path(__file__).parent/'fv-ex2-sealed-preview.php')],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)

    def test_deterministic_private_package(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=Path(d)/'a.zip',Path(d)/'b.zip'
            ma=build(ROOT,a,HEAD);mb=build(ROOT,b,HEAD)
            self.assertEqual(a.read_bytes(),b.read_bytes())
            self.assertEqual(ma,mb)
            with zipfile.ZipFile(a) as z:
                names=z.namelist()
                self.assertEqual(len(names),3)
                self.assertTrue(all(not any(n.endswith('/'+f) for f in FILES) for n in names))
                php=z.read(ZIPROOT+'/fv-ex2-sealed-preview.php')
                self.assertIn(b'FV_EX2_PACKED_ASSETS',php)
                self.assertNotIn(b'wp_ajax_nopriv_',php)
                self.assertIn(b'check_ajax_referer',php)
                path=Path(d)/'plugin.php';path.write_bytes(php)
                syntax=subprocess.run(['php','-l',str(path)],capture_output=True,text=True)
                self.assertEqual(syntax.returncode,0,syntax.stdout+syntax.stderr)
                self.assertEqual(ma['asset_sha256']['index.html'],hashlib.sha256((ROOT/'index.html').read_bytes()).hexdigest())

    def test_abort_on_missing_js(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'root';target.mkdir()
            for f in FILES:
                if f!='reading-trail.js': (target/f).write_bytes((ROOT/f).read_bytes())
            with self.assertRaisesRegex(ValueError,'missing source file'):
                build(target,Path(d)/'bad.zip',HEAD)

    def test_aborts_on_bogus_commit(self):
        with self.assertRaisesRegex(ValueError,'exact 40-hex'):
            build(ROOT,Path(tempfile.gettempdir())/'bad.zip','main')

    def test_runtime_auth_and_private_ajax_content(self):
        with tempfile.TemporaryDirectory() as d:
            output=Path(d)/'a.zip';build(ROOT,output,HEAD)
            with zipfile.ZipFile(output) as z:
                php=Path(d)/'plugin.php';php.write_bytes(z.read(ZIPROOT+'/fv-ex2-sealed-preview.php'))
            stub=r'''<?php
            define('ABSPATH','/');define('FV_EX2_ALLOW_PREVIEW',true);
            $mode=$argv[1];$E=($mode==='production'?'production':'staging');$LOG=($mode!=='guest');$CAP=($mode!=='noneditor');
            function wp_get_environment_type(){return $GLOBALS['E'];}
            function is_user_logged_in(){return $GLOBALS['LOG'];}
            function current_user_can($a){return $GLOBALS['CAP'];}
            function add_shortcode($n,$f){}function add_action($n,$f){}
            function add_query_arg($q,$u){return $u.'?action='.$q['action'].'&_wpnonce='.$q['_wpnonce'];}
            function admin_url($p){return 'https://private-test.invalid/wp-admin/'.$p;}
            function wp_create_nonce($v){return 'static-test-nonce';}
            function esc_url($v){return htmlspecialchars($v,ENT_QUOTES);}
            function check_ajax_referer($v){}
            function nocache_headers(){}
            function status_header($n){exit(77);}
            require '__PLUGIN__';
            if ($mode==='production'||$mode==='guest'||$mode==='noneditor') {
                if (fv_ex2_sealed_shortcode([])!=='')exit(41);
                if (fv_ex2_sealed_authorized())exit(42);
                echo 'DENIED';exit;
            }
            if (strpos(fv_ex2_sealed_shortcode([]),'sandbox="allow-scripts allow-popups"')===false)exit(43);
            fv_ex2_sealed_render();
            '''.replace('__PLUGIN__',str(php).replace('\\','\\\\').replace("'","\\'"))
            file=Path(d)/'test.php';file.write_text(stub)
            for mode in ('production','guest','noneditor'):
                run=subprocess.run(['php',str(file),mode],capture_output=True,text=True)
                self.assertEqual(run.returncode,0,mode+' '+run.stderr)
                self.assertEqual(run.stdout,'DENIED')
            run=subprocess.run(['php',str(file),'editor'],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stdout[-200:]+run.stderr)
            self.assertIn('data-fv-home-flagship',run.stdout)
            self.assertEqual(run.stdout.count('data-ex2-style='),6)
            self.assertEqual(run.stdout.count('data-ex2-script='),4)
            self.assertNotIn('src="./',run.stdout)
            self.assertNotIn('href="./',run.stdout)

if __name__=='__main__':unittest.main()
