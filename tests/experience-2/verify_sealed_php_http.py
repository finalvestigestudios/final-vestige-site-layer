#!/usr/bin/env python3
"""Fail-closed real HTTP test of sealed EX2 plugin PHP response and denial headers.

Runs unchanged generated PHP under isolated WordPress-function STUBS on a local
PHP 127.0.0.1 HTTP server. Never installs WordPress, accesses production,
uses real credentials, or changes a CMS. It verifies real PHP-emitted HTTP
status and headers but NOT a real WordPress session, hosted behavior, browser
CSP enforcement, image transfers, WCAG, or conversion.

python tests/experience-2/verify_sealed_php_http.py \
  --plugin generated-plugin.php --manifest STAGING_MANIFEST.json --out receipt.json
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROUTER = r'''<?php
// Local-only test doubles. NOT WordPress. No real user/session data.
define('ABSPATH','/fv-http-test-only/');
define('FV_EX2_ALLOW_PREVIEW',getenv('FV_HTTP_ALLOW')==='1');
function wp_get_environment_type(){return getenv('FV_HTTP_ENV')?:'production';}
function is_user_logged_in(){return in_array(($_COOKIE['fv_test_role']??''),['editor','reader'],true);}
function current_user_can($cap){return $cap==='edit_pages' && ($_COOKIE['fv_test_role']??'')==='editor';}
function check_ajax_referer($action){
  if($action!=='fv_ex2_sealed_render'||($_GET['_wpnonce']??'')!=='local-test-nonce'){
      http_response_code(403);exit('denied');
  }
}
function wp_create_nonce($action){return 'local-test-nonce';}
function add_shortcode($name,$callback){}
function add_action($name,$callback){}
function status_header($code){http_response_code($code);}
function nocache_headers(){header('Cache-Control: no-cache, must-revalidate');}
function admin_url($s){return 'http://127.0.0.1:'.getenv('FV_HTTP_PORT').'/wp-admin/'.$s;}
function add_query_arg($args,$url){return $url.'?'.http_build_query($args);}
function esc_url($s){return htmlspecialchars($s,ENT_QUOTES,'UTF-8');}
require __DIR__.'/fv-ex2-sealed-preview.php';
$path=parse_url($_SERVER['REQUEST_URI'],PHP_URL_PATH);
if($path==='/review'){echo fv_ex2_sealed_shortcode();exit;}
if($path==='/wp-admin/admin-ajax.php'){
 if(($_GET['action']??'')!=='fv_ex2_sealed_render'){http_response_code(404);exit;}
 fv_ex2_sealed_render();exit;
}
http_response_code(404);exit;
''';

def request(url,role=''):
    req=Request(url,headers={'Cookie':'fv_test_role='+role} if role else {})
    try:
        with urlopen(req,timeout=7) as resp:
            return resp.status,{k.lower():v for k,v in resp.headers.items()},resp.read()
    except HTTPError as e:
        return e.code,{k.lower():v for k,v in e.headers.items()},e.read()

def run(plugin,manifest_path,out):
    plugin_bytes=plugin.read_bytes();manifest=json.loads(manifest_path.read_text())
    sha=hashlib.sha256(plugin_bytes).hexdigest()
    assert sha==manifest['plugin_sha256'],'Generated plugin differs from declared manifest'
    assert manifest['status']=='PRIVATE_STAGING_ONLY_NO_PRODUCTION_INSTALL'
    assert re.fullmatch('[0-9a-f]{40}',manifest['expected_commit'])
    assert manifest['browser_visible_asset_paths']==[]
    assert b'wp_ajax_nopriv_' not in plugin_bytes
    required=('fv_ex2_sealed_authorized','fv_ex2_sealed_render','FV_EX2_PACKED_ASSETS','FV_EX2_ASSET_SHA256')
    assert all(s.encode() in plugin_bytes for s in required)
    out.parent.mkdir(parents=True,exist_ok=True)
    receipts=[]
    with tempfile.TemporaryDirectory(prefix='fv-ex2-php-http-') as td:
        root=Path(td)
        (root/'fv-ex2-sealed-preview.php').write_bytes(plugin_bytes)
        (root/'index.php').write_text(ROUTER)
        def server(environment,allow):
            with socket.socket() as sock:
                sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
            env={**os.environ,'FV_HTTP_ENV':environment,'FV_HTTP_ALLOW':'1' if allow else '0','FV_HTTP_PORT':str(port)}
            proc=subprocess.Popen(['php','-S',f'127.0.0.1:{port}','-t',str(root),str(root/'index.php')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            base=f'http://127.0.0.1:{port}'
            for _ in range(70):
                try:
                    request(base+'/review');return proc,base
                except Exception:time.sleep(.07)
            proc.terminate();raise RuntimeError('PHP localhost HTTP transport unavailable')
        def test(name,url,role,code,need=(),forbid=()):
            status,headers,body=request(url,role)
            assert status==code,(name,status,code)
            for text in need:assert text.encode() in body,(name,'missing expected text',text)
            for text in forbid:assert text.encode() not in body,(name,'unwanted text',text)
            receipts.append({'test':name,'environment':environment,'preview_enabled':allow,'role':role or 'anonymous','status':status,'response_bytes':len(body),'pass':True})
            return headers,body
        def stop(proc):
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()

        for environment,allow in [('production',True),('staging',False),('staging',True),('development',True),('local',True),('unexpected',True)]:
            proc,base=server(environment,allow)
            try:
                ajax=base+'/wp-admin/admin-ajax.php?action=fv_ex2_sealed_render&_wpnonce=local-test-nonce'
                if not allow or environment not in ('staging','development','local'):
                    test(f'denied_{environment}_{"on" if allow else "off"}',ajax,'editor',403,forbid=('data-fv-home-flagship',))
                    test(f'empty_shortcode_{environment}_{"on" if allow else "off"}',base+'/review','editor',200,forbid=('PRIVATE STAGING STUDY',))
                    continue
                if environment=='staging':
                    test('anonymous_denied',ajax,'',403,forbid=('data-fv-home-flagship',))
                    test('reader_denied',ajax,'reader',403,forbid=('data-fv-home-flagship',))
                    test('nonce_missing',ajax.split('&_wpnonce=')[0],'editor',403)
                    test('nonce_wrong',ajax.replace('local-test-nonce','fake'),'editor',403)
                    test('anonymous_shortcode_empty',base+'/review','',200,forbid=('PRIVATE STAGING STUDY',))
                    test('reader_shortcode_empty',base+'/review','reader',200,forbid=('PRIVATE STAGING STUDY',))
                    test('direct_html_404',base+'/wp-content/plugins/fv-ex2/index.html','',404)
                    test('direct_css_404',base+'/wp-content/plugins/fv-ex2/flagship.css','',404)
                    test('direct_js_404',base+'/wp-content/plugins/fv-ex2/flagship.js','',404)
                    test('direct_php_unhandled_404',base+'/wp-content/plugins/fv-ex2/fv-ex2-sealed-preview.php','',404)
                _,short=test(f'editor_shortcode_{environment}',base+'/review','editor',200,need=('PRIVATE STAGING STUDY','<iframe','fv_ex2_sealed_render'))
                assert '&amp;_wpnonce=local-test-nonce' in short.decode(), 'Shortcode must contain a nonce for authorized reviewer'
                headers,body=test(f'editor_render_{environment}',ajax,'editor',200,need=('data-fv-home-flagship','fv-hf-mind-title','https://finalvestige.com/focus/','data-ex2-style=','data-ex2-script='))
                assert headers['x-robots-tag']=='noindex, nofollow, noarchive'
                assert headers['referrer-policy']=='no-referrer'
                assert headers['x-content-type-options']=='nosniff'
                assert 'no-cache' in headers['cache-control']
                assert headers['content-type'].startswith('text/html')
                csp=headers['content-security-policy']
                assert "default-src 'none'" in csp and "frame-ancestors 'self'" in csp
                nonce_match=re.search(r"script-src 'nonce-([^']+)'",csp)
                assert nonce_match and len(nonce_match.group(1))>=20
                assert f'nonce="{nonce_match.group(1)}"'.encode() in body
                assert body.count(b'data-ex2-script=')==4 and body.count(b'data-ex2-style=')==6
                assert b'src="./' not in body and b'href="./' not in body
                if environment=='staging':
                    _,headers2,body2=request(ajax,'editor')
                    nonce2=re.search(r"script-src 'nonce-([^']+)'",headers2['content-security-policy']).group(1)
                    assert nonce_match.group(1)!=nonce2, 'CSP nonces must be fresh per response'
                    receipts.append({'test':'fresh_script_nonce_across_http_responses','environment':'staging','preview_enabled':True,'role':'editor','status':200,'pass':True})
            finally:stop(proc)
    receipt={'result':'PASS','test_count':len(receipts),'checks':receipts,'plugin_sha256':sha,
             'expected_commit_from_manifest':manifest['expected_commit'],
             'scope':'Actual PHP HTTP status/headers on localhost against stubbed WordPress functions; NOT WordPress integration or real WordPress cookies/nonce',
             'browser_navigation':'BLOCKED_BY_ADMINISTRATOR in current lab; no browser HTTP claim',
             'release':'HOLD','actual_cms_writes':0,
             'outstanding':['Real isolated WordPress/Assembler host','Browser HTTP CSP enforcement and authenticated cookie handling','Axe/WCAG 2.2 AA','Safari/no-JS on real WordPress','Actual archival image network transfers and rights','Lighthouse/CWV','Jetpack confirmed signup','Independent CI/QD','Founder visual/release approval']}
    out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'result':'PASS','checks':len(receipts),'plugin_sha256':sha,'scope':receipt['scope']}))
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--plugin',type=Path,required=True)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    run(args.plugin,args.manifest,args.out)
