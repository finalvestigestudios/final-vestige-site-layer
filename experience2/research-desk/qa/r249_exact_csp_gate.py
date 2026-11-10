#!/usr/bin/env python3
"""R249 exact-source PHP/CSP link smoke gate. Full checkout required.
Tests pinned NASA/JS/CSS files and three simulated WP render phases.
This does NOT claim actual WordPress, HTTP CSP, axe, or field performance.
"""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from shutil import copy2

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'templates/ledger.html': '403d128c57b9bc82dac7c619651689070edef86c',
    'assets/source-ledger.css': 'db531213e6f8dbaa44fba2885eefdd016dab93e3',
    'assets/source-ledger.js': '32e757cc4dc8708397ff65ac21e89dd319781d78',
}
PLUGIN = 'final-vestige-ex2-research-desk.php'
SHIM = r'''<?php
define('ABSPATH', '/qa/');
function plugin_dir_path($f){return dirname($f).'/';}
function plugins_url($p,$f){return 'https://example.test/assets/'.basename($p);}
function esc_url($u){return htmlspecialchars($u,ENT_QUOTES,'UTF-8');}
function add_action($a,$b,$c){} function add_shortcode($a,$b){}
function wp_enqueue_style($a,$b,$c,$d){}
function wp_enqueue_script($a,$b,$c,$d,$e){}
function wp_style_is($a,$b){return $_SERVER['argv'][1]==='printed';}
function did_action($a){return $_SERVER['argv'][1]==='before'?0:1;}
function is_singular(){return true;} function has_shortcode($a,$b){return true;}
function get_post(){return (object)['post_content'=>'[fv_ex2_research_desk]'];}
require __DIR__.'/final-vestige-ex2-research-desk.php';
echo json_encode(array(fv_ex2_rd_shortcode(),fv_ex2_rd_shortcode()),JSON_THROW_ON_ERROR);
'''
def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def php(root,phase):
    p=subprocess.run(['php',str(root/'shim.php'),phase],text=True,
                     capture_output=True,check=True)
    return json.loads(p.stdout)

def main():
    source=(ROOT/PLUGIN).read_bytes()
    assert b'<link rel="stylesheet"' in source
    assert b'<style id="fv-ex2-research-desk-late-style"' not in source
    for path,sha in PINS.items():
        assert git_blob((ROOT/path).read_bytes()) == sha, 'source drift: '+path
        assert sha.encode() in source, 'pin absent: '+path
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);copy2(ROOT/PLUGIN,root/PLUGIN)
        for path in PINS:
            f=root/path;f.parent.mkdir(parents=True,exist_ok=True)
            copy2(ROOT/path,f)
        (root/'shim.php').write_text(SHIM)
        lint=subprocess.run(['php','-l',str(root/PLUGIN)],capture_output=True)
        assert lint.returncode==0,lint.stderr
        for phase,count in [('before',0),('after',1),('printed',0)]:
            one,two=php(root,phase)
            assert one.count('id="fv-ex2-research-desk-late-style"')==count,phase
            assert 'fv-ex2-research-desk-late-style' not in two,phase
            assert one.count('data-fvx-record')==6,phase
            assert two.count('data-fvx-record')==6,phase
            assert '<style id="fv-ex2-research-desk-late-style"' not in one,phase
            if count:
                assert 'href="https://example.test/assets/source-ledger.css"' in one
        css=root/'assets/source-ledger.css';css.write_bytes(css.read_bytes()+b'\nTAMPER')
        one,two=php(root,'after')
        assert 'fv-ex2-research-desk-late-style' not in one
        html=root/'templates/ledger.html';html.write_bytes(html.read_bytes()+b'\nTAMPER')
        one,two=php(root,'after')
        assert 'Research source viewer unavailable' in one
        assert 'data-fvx-record' not in one
    print(json.dumps({'result':'PASS','mode':'EXACT_ORIGINAL_NASA_SOURCE',
       'staging_only':True,'installed_wordpress':False,
       'csp_http_transport_tested':False,'axe_core':False}))
if __name__=='__main__':main()
