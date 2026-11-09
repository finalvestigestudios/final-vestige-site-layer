#!/usr/bin/env python3
"""R243 Research Desk shortcode lifecycle security/ID tests. No WordPress install claimed."""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from bs4 import BeautifulSoup

SHIM = r'''<?php
define('ABSPATH','/fake/');$GLOBALS['queued']=[];
function wp_enqueue_style($h,$u,$d,$v){$GLOBALS['queued'][]=$h;}
function wp_enqueue_script($h,$u,$d,$v,$f){$GLOBALS['queued'][]=$h;}
function wp_style_is($h,$s){return $_SERVER['argv'][1]==='early';}
function plugins_url($p,$f){return '/staging/'.$p;}
function plugin_dir_path($f){return dirname($f).'/';}
function add_action($a,$f,$p){} function add_shortcode($n,$f){}
function is_singular(){return true;} function get_post(){return (object)['post_content'=>'[fv_ex2_research_desk]'];}
function has_shortcode($c,$n){return strpos($c,'['.$n.']')!==false;}
function esc_url($u){return htmlspecialchars($u,ENT_QUOTES,'UTF-8');}
require __DIR__.'/final-vestige-ex2-research-desk.php';
if($_SERVER['argv'][1]==='early')fv_ex2_rd_assets();
echo json_encode(['first'=>fv_ex2_rd_shortcode(),'second'=>fv_ex2_rd_shortcode(),'queued'=>$GLOBALS['queued']],JSON_THROW_ON_ERROR);
'''

def synthetic(root):
    (root/'templates').mkdir();(root/'assets').mkdir()
    cards=''.join(f'<article id="fv-ex2-ledger-apollo1-record-{i}" data-fvx-record><h2>Record {i}</h2><details><summary>Evidence</summary><p>Sample only</p></details></article>' for i in range(6))
    (root/'templates/ledger.html').write_text('<section data-fvx-ledger aria-labelledby="fv-ex2-ledger-apollo1-title"><h1 id="fv-ex2-ledger-apollo1-title">Sample</h1><label for="fv-ex2-ledger-apollo1-search">Search</label><input id="fv-ex2-ledger-apollo1-search" aria-controls="fv-ex2-ledger-apollo1-grid"><div id="fv-ex2-ledger-apollo1-grid">'+cards+'</div></section>')
    (root/'assets/source-ledger.css').write_text('[data-fvx-ledger]{background:#111;color:white}')

def invoke(root, mode):
    p=subprocess.run(['php',str(root/'shim.php'),mode],capture_output=True,text=True)
    assert p.returncode==0, p.stderr
    return json.loads(p.stdout)

def check(payload, mode):
    first,second=payload['first'],payload['second']
    assert len(BeautifulSoup(first,'html.parser').select('[data-fvx-record]'))==6
    assert len(BeautifulSoup(second,'html.parser').select('[data-fvx-record]'))==6
    assert first.count('<style')==(1 if mode=='late' else 0)
    assert second.count('<style')==0
    soup=BeautifulSoup(first+second,'html.parser')
    ids=[e['id'] for e in soup.select('[id]')]
    assert len(ids)==len(set(ids)), 'duplicate IDs from repeated shortcode'
    for attr in ('for','aria-controls','aria-labelledby'):
        for e in soup.select('['+attr+']'):
            assert all(ref in ids for ref in e[attr].split()),attr
    assert 'instance-2-' in second and 'instance-2-' not in first
    assert payload['queued'].count('fv-ex2-research-desk')>=2

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--fixture',action='store_true');a=p.parse_args()
    with tempfile.TemporaryDirectory(prefix='apollo-r243-') as t:
        root=Path(t);shutil.copy2(a.source/'final-vestige-ex2-research-desk.php',root/'final-vestige-ex2-research-desk.php')
        if a.fixture:synthetic(root)
        else:
            shutil.copytree(a.source/'templates',root/'templates');shutil.copytree(a.source/'assets',root/'assets')
        (root/'shim.php').write_text(SHIM)
        for mode in ('early','late'):check(invoke(root,mode),mode)
        original=(root/'assets/source-ledger.css').read_text()
        (root/'assets/source-ledger.css').write_text('</style><script>alert(1)</script>')
        assert '<style' not in invoke(root,'late')['first'],'untrusted CSS escaped its element'
        (root/'assets/source-ledger.css').write_text(original)
        f=root/'templates/ledger.html';v=f.read_text();f.unlink()
        assert 'Read the original Apollo 1 investigation' in invoke(root,'late')['first']
        f.write_text(v)
    print(json.dumps({'status':'PASS','cases':['early','late','two instances','aria references','CSS injection rejected','missing template fallback'],'fixture':a.fixture,'installed_WP':False}))
if __name__=='__main__':main()
