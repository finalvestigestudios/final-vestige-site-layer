#!/usr/bin/env python3
"""Exact-source Apollo PHP HTTP security checks through a localhost WordPress stub.

IMPORTANT: real HTTP headers/status/export bytes, NOT genuine WordPress, browser
CSP enforcement, native screen-reader QA, axe-core, or field Core Web Vitals.
No network access, public assets, WordPress writes, or paid services.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import zipfile

HERE=Path(__file__).resolve().parent
SEALED=HERE.parent
sys.path.insert(0,str(SEALED))
from build_sealed import build, ROOT

def fetch(base, route, mode=None):
    hdr={'Cookie':f'fv_test_mode={mode}'} if mode else {}
    try:
        with urlopen(Request(base+route,headers=hdr),timeout=8) as r:
            return r.status,dict(r.headers),r.read()
    except HTTPError as e:
        return e.code,dict(e.headers),e.read()

def ajax(base, action, mode='editor', nonce='http-stub-fixed-nonce', **extra):
    query=urlencode(dict(action=action,_wpnonce=nonce,**extra))
    return fetch(base,'/wp-admin/admin-ajax.php?'+query,mode)

class ApolloSealedHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='fv-apollo-http-')
        root=Path(cls.tmp.name)
        cls.zip=root/'sealed.zip'
        cls.manifest=build(cls.zip)
        with zipfile.ZipFile(cls.zip) as z:
            cls.plugin=root/'sealed.php'
            cls.plugin.write_bytes(z.read(ROOT+'/fv-ex2-apollo-sealed.php'))
        cls.zip2=root/'sealed2.zip'
        build(cls.zip2)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0))
            port=sock.getsockname()[1]
        cls.base=f'http://127.0.0.1:{port}'
        cls.proc=subprocess.Popen(['php','-S',f'127.0.0.1:{port}',str(HERE/'http_router_entry.php')],
            cwd=HERE,env=dict(os.environ,FV_TEST_APOLLO_PLUGIN=str(cls.plugin)),
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(80):
            if cls.proc.poll() is not None:raise RuntimeError('PHP HTTP server exited')
            try:
                if fetch(cls.base,'/health')[0]==200:break
            except (URLError,TimeoutError):
                time.sleep(0.05)
        else:raise RuntimeError('PHP HTTP server not ready')

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:cls.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:cls.proc.kill()
        cls.tmp.cleanup()

    def test_01_deterministic_build(self):
        self.assertEqual(self.zip.read_bytes(),self.zip2.read_bytes())
        self.assertTrue(self.manifest['source_match_all_12_blob_pins'])
        self.assertEqual(self.manifest['plugin_sha256'],hashlib.sha256(self.plugin.read_bytes()).hexdigest())

    def test_02_editor_shortcode_safe_full_page_alternative(self):
        code,headers,body=fetch(self.base,'/review','editor')
        self.assertEqual(code,200)
        self.assertEqual(body.count(b'fv_ex2_apollo_sealed_page'),2)
        self.assertIn(b'Open the private full-page evidence review',body)
        self.assertIn(b'rel="noopener noreferrer"',body)
        self.assertIn(b'allow-popups-to-escape-sandbox',body)
        self.assertNotIn(b'allow-same-origin',body)
        self.assertNotIn(b'allow-top-navigation',body)
        self.assertIn(b'referrerpolicy="no-referrer"',body)

    def test_03_non_editor_and_production_deny(self):
        for mode in ('guest','reader','production','off'):
            with self.subTest(mode=mode):
                code,h,body=fetch(self.base,'/review',mode)
                self.assertEqual(code,200)
                self.assertNotIn(b'<iframe',body)
                for act in ('fv_ex2_apollo_sealed_page','fv_ex2_apollo_sealed_download'):
                    code,h,body=ajax(self.base,act,mode,file='evidence-export.csv')
                    self.assertEqual((code,body),(403,b''))

    def test_04_bad_nonce_denied(self):
        for act in ('fv_ex2_apollo_sealed_page','fv_ex2_apollo_sealed_download'):
            code,h,body=ajax(self.base,act,nonce='wrong',file='evidence-export.csv')
            self.assertEqual((code,body),(403,b''))

    def test_05_real_php_http_csp_headers(self):
        code,h,body=ajax(self.base,'fv_ex2_apollo_sealed_page')
        h={k.lower():v for k,v in h.items()}
        self.assertEqual(code,200)
        self.assertEqual(h.get('x-content-type-options'),'nosniff')
        self.assertIn('noindex',h.get('x-robots-tag',''))
        self.assertEqual(h.get('referrer-policy'),'no-referrer')
        self.assertIn("frame-ancestors 'self'",h.get('content-security-policy',''))
        self.assertIn("img-src 'none'",h.get('content-security-policy',''))
        self.assertIn("connect-src 'none'",h.get('content-security-policy',''))
        self.assertNotIn("'unsafe-inline'",h.get('content-security-policy',''))
        self.assertEqual(body.count(b'id="fv-ex2-wayfinder"'),1)
        self.assertEqual(body.count(b'class="fv-ex2-wayfinder__list"'),1)
        self.assertEqual(h.get('x-fv-ex2-apollo-wayfinder-sha256'),self.manifest['outputs_sha256']['wayfinder.html'])
        self.assertEqual(h.get('x-fv-ex2-apollo-touch-targets-sha256'),self.manifest['outputs_sha256']['touch-targets.css'])
        self.assertEqual(h.get('x-fv-ex2-apollo-print-ledger-sha256'),self.manifest['outputs_sha256']['print-source-transcript.html'])
        self.assertEqual(h.get('x-fv-ex2-apollo-print-css-sha256'),self.manifest['outputs_sha256']['print-source-transcript.css'])
        self.assertEqual(body.count(b'data-r25-print-record='),6)
        self.assertNotIn(b'admin-ajax.php',body.split(b'id="fv-ex2-print-transcript"')[1].split(b'</section>')[0])
        self.assertIn(b'id="atlas"',body)
        self.assertIn(b'id="source-concordance"',body)
        self.assertEqual(body.count(b'data-concordance-record='), 6)
        self.assertEqual(h.get('x-fv-ex2-apollo-concordance-sha256'),self.manifest['outputs_sha256']['source-concordance.html'])
        self.assertIn(b'id="documentary-trails"',body)
        self.assertNotIn(b'{{FV_EX2_ASSET_BASE}}',body)
        self.assertEqual(body.count(b'fv_ex2_apollo_sealed_download'),14)
        self.assertEqual(body.count(b'data-admission-record='),6)
        self.assertEqual(body.count(b'data-media-review='),6)
        self.assertEqual(body.count(b'data-media-hold="true"'),6)
        self.assertEqual(h.get('x-fv-ex2-apollo-media-rights-sha256'),self.manifest['outputs_sha256']['media-rights.html'])
        self.assertEqual(h.get('x-fv-ex2-apollo-media-rights-index-sha256'),self.manifest['outputs_sha256']['media-rights.json'])
        self.assertEqual(h.get('x-fv-ex2-apollo-atlas-sha256'),self.manifest['outputs_sha256']['atlas-admission.html'])
        self.assertEqual(h.get('x-fv-ex2-apollo-atlas-index-sha256'),self.manifest['outputs_sha256']['atlas-admission.json'])
        self.assertEqual(h.get('x-fv-ex2-apollo-context-sha256'),self.manifest['outputs_sha256']['source-context.json'])
        import re
        nonces=re.findall(rb'<(?:script|style) nonce="([^"]+)"',body)
        self.assertEqual(len(nonces),2)
        self.assertEqual(nonces[0],nonces[1])
        self.assertIn(b"'nonce-"+nonces[0]+b"'",h['content-security-policy'].encode())

    def test_06_exact_exports_and_path_allowlist(self):
        for name in ('evidence-export.csv','evidence-export.json','response-export.csv','response-export.json','source-context.json','atlas-admission.json','media-rights.json'):
            with self.subTest(name=name):
                code,h,body=ajax(self.base,'fv_ex2_apollo_sealed_download',file=name)
                self.assertEqual(code,200)
                self.assertEqual(body,(SEALED.parent/'generated'/name).read_bytes() if name not in ('source-context.json','atlas-admission.json','media-rights.json')
                                 else (__import__('source_concordance').build_context_index().encode('utf-8') if name == 'source-context.json' else __import__('atlas_admission').build_atlas_admission()[2].encode('utf-8') if name == 'atlas-admission.json' else __import__('media_rights_ledger').build_media_rights()[2].encode('utf-8')))
                self.assertEqual(len(body),int(h['Content-Length']))
                self.assertIn('attachment;',h['Content-Disposition'])
        for bad in ('../fragment.html','apollo.js','response-export.json/..',''):
            code,h,body=ajax(self.base,'fv_ex2_apollo_sealed_download',file=bad)
            self.assertEqual((code,body),(404,b''))

    def test_07_no_direct_static_exposure(self):
        for path in ('/fv-ex2-apollo-sealed.php','/fragment.html','/apollo.js','/apollo.css','/generated/evidence-export.csv'):
            code,h,body=fetch(self.base,path,'editor')
            self.assertEqual((code,body),(404,b''))

    def test_08_no_public_ajax_route(self):
        code,h,body=fetch(self.base,'/wp-admin/admin-ajax.php?action=wp_ajax_nopriv_fv_ex2_apollo_sealed_page','editor')
        self.assertEqual((code,body),(404,b''))

# Compatibility alias: staging-admission reuses this fixture directly.
ApolloHttp = ApolloSealedHTTP

if __name__=='__main__':
    unittest.main()
