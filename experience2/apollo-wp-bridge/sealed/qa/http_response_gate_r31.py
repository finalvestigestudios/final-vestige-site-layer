#!/usr/bin/env python3
"""R31: real-PHP-HTTP response custody for source-pinned, private Apollo staging.

Not real WordPress auth, a browser-enforced CSP, or a production release test.
"""
import argparse
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from zipfile import ZipFile

ZIP_SHA='d29ee02d629ae50716058b8ffa6cb3d9bac76a9cd72d9e3387504e2d22dab14f'
PHP_SHA='ea465fcb6518ae2ba6bfaf8c6cd66dae354de4887e402ab4f0a27d02d28c8168'
ROOT='fv-ex2-apollo-private-review/'
STUB='''<?php
// Tests the actual sealed plugin with mocked WordPress permissions/nonces.
define('ABSPATH',__DIR__);
define('FV_EX2_APOLLO_STAGING_ALLOW', !isset($_GET['optout']));
function wp_get_environment_type(){return isset($_GET['production'])?'production':'staging';}
function is_user_logged_in(){return !isset($_GET['guest']);}
function current_user_can($c){return $c==='edit_pages'&&!isset($_GET['denycap']);}
function wp_create_nonce($a){return 'LOCALTEST';}
function check_ajax_referer($a,$k,$stop){return ($_REQUEST[$k]??'')==='LOCALTEST'?1:false;}
function admin_url($p){return 'https://private-staging.invalid/wp-admin/'.$p;}
function add_query_arg($a,$u){return $u.'?'.http_build_query($a);}
function esc_url($v){return htmlspecialchars($v,ENT_QUOTES,'UTF-8');}
function add_shortcode($a,$b){} function add_action($a,$b){}
function nocache_headers(){header('Cache-Control: no-store, private');}
function status_header($c){http_response_code($c);}
require __DIR__.'/fv-ex2-apollo-sealed.php'; fv_ex2_apollo_sealed_page();
'''
def sha(b): return sha256(b).hexdigest()

class Custody(HTMLParser):
    def __init__(self):
        super().__init__(); self.records=0;self.rights=0;self.catalog=0;self.geo=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        self.records+=int('data-concordance-record' in a)
        self.rights+=int(a.get('data-media-hold')=='true')
        self.catalog+=int(a.get('data-crosswalk-review')=='hold')
        self.geo+=int('data-lat' in a or 'data-lon' in a)

def verify_zip(path):
    raw=path.read_bytes()
    if sha(raw)!=ZIP_SHA: raise ValueError('R29 archive SHA mismatch')
    with ZipFile(path) as z:
        names={ROOT+n for n in ('INSTALLATION_HOLD.txt','SEALED_SOURCE_MANIFEST.json','fv-ex2-apollo-sealed.php')}
        if set(z.namelist())!=names: raise ValueError('R29 archive file list mismatch')
        for i in z.infolist():
            if i.is_dir() or '..' in Path(i.filename).parts or (i.external_attr>>16)&0o170000==0o120000:
                raise ValueError('unsafe archive file')
        php=z.read(ROOT+'fv-ex2-apollo-sealed.php')
    if sha(php)!=PHP_SHA or re.search(rb"add_action\s*\(\s*['\"]wp_ajax_nopriv_",php):
        raise ValueError('PHP source identity or private-access requirement failed')
    return php

def fetch(url):
    try:
        with urlopen(url,timeout=8) as r: return r.status,dict(r.headers),r.read()
    except HTTPError as e: return e.code,dict(e.headers),e.read()

def audit(status,headers,body):
    csp=headers.get('Content-Security-Policy','')
    if status!=200 or len(body)<150000 or not body.startswith(b'<!doctype html>'):
        raise AssertionError('complete private HTTP response not received')
    for k,v in [('X-Robots-Tag','noindex, nofollow, noarchive'),('Referrer-Policy','no-referrer'),
                ('X-Content-Type-Options','nosniff'),('X-FV-EX2-Apollo-Source-Head','74375657f2cdaac0710f94c6de6c24534ee06858')]:
        if headers.get(k)!=v: raise AssertionError(f'bad HTTP header: {k}')
    if 'no-store' not in headers.get('Cache-Control',''): raise AssertionError('private no-store absent')
    for d in ("default-src 'none'","img-src 'none'","connect-src 'none'", "form-action 'none'", "frame-ancestors 'self'"):
        if d not in csp: raise AssertionError('missing CSP directive: '+d)
    if "'unsafe-inline'" in csp: raise AssertionError('permissive CSP')
    css=re.findall(rb'<style nonce="([^"]+)"',body); js=re.findall(rb'<script nonce="([^"]+)"',body)
    if len(css)!=1 or len(js)!=1 or css!=js: raise AssertionError('style/script nonce mismatch')
    nonce=css[0].decode('ascii')
    for d in ("script-src 'nonce-"+nonce+"'", "style-src 'nonce-"+nonce+"'"):
        if d not in csp: raise AssertionError('HTTP header nonce differs from HTML')
    document=Custody();document.feed(body.decode('utf-8'))
    if (document.records,document.rights,document.catalog,document.geo)!=(6,6,1,0):
        raise AssertionError('NASA custody or Atlas admission changed')
    normalized=body.replace(nonce.encode(),b'Z'*len(nonce))
    return {'http':200,'bytes':len(body),'normalized_html_sha256':sha(normalized),
            'normalized_csp':csp.replace(nonce,'Z'*len(nonce)), 'nonce':nonce}

def run(path):
    source=verify_zip(path)
    with tempfile.TemporaryDirectory(prefix='fv-apollo-r31-') as folder:
        root=Path(folder);(root/'fv-ex2-apollo-sealed.php').write_bytes(source)
        (root/'index.php').write_text(STUB)
        with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
        srv=subprocess.Popen(['php','-S',f'127.0.0.1:{port}','-t',str(root)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        base=f'http://127.0.0.1:{port}/index.php'
        try:
            for _ in range(50):
                try: fetch(base+'?_wpnonce=LOCALTEST');break
                except URLError:time.sleep(.1)
            good=audit(*fetch(base+'?_wpnonce=LOCALTEST'));other=audit(*fetch(base+'?_wpnonce=LOCALTEST'))
            if good['nonce']==other['nonce'] or good['normalized_html_sha256']!=other['normalized_html_sha256']:
                raise AssertionError('nonce not fresh or normalized response unstable')
            good.pop('nonce')
            denied=[]
            for suffix,label in [('', 'missing-nonce'),('?_wpnonce=NO','bad-nonce'),
                                 ('?_wpnonce=LOCALTEST&guest=1','guest'),('?_wpnonce=LOCALTEST&denycap=1','no-editor'),
                                 ('?_wpnonce=LOCALTEST&production=1','production'),('?_wpnonce=LOCALTEST&optout=1','optout'),
                                 ('?_wpnonce='+('x'*129),'overlong-nonce')]:
                code,_,data=fetch(base+suffix)
                if code!=403 or data:raise AssertionError(f'{label} leaked data: {code}/{len(data)}')
                denied.append(label)
            direct=fetch(f'http://127.0.0.1:{port}/fv-ex2-apollo-sealed.php')
            if direct[2]:raise AssertionError('direct plugin source exposed')
            return {'result':'PASS_LOCAL_HTTP_RELEASE_HOLD','source_zip_sha256':ZIP_SHA,'sealed_php_sha256':PHP_SHA,
                    'allowed':good,'fresh_csp_nonce':True,'empty_403_denials':denied,
                    'direct_php_status':direct[0],'direct_php_bytes':len(direct[2]),
                    'limits':'Mock WordPress auth. Real PHP HTTP headers only; browser CSP, axe, real WordPress and hosted CWV NOT tested.'}
        finally:
            srv.terminate()
            try:srv.communicate(timeout=5)
            except subprocess.TimeoutExpired:srv.kill();srv.communicate()

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--r29-zip',required=True,type=Path);a.add_argument('--out',required=True,type=Path)
    args=a.parse_args(); receipt=run(args.r29_zip)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('R31: local PHP HTTP PASS; seven empty 403 denials, rotating CSP nonces; release HOLD')
