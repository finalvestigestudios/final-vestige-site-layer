"""Local PHP HTTP test of exact HTML SHA-256 header, using synthetic payload only.

No production CMS access, actual WordPress, source rights, or browser certification.
"""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.request

BASE=Path(__file__).resolve().parent
PRIVATE=BASE.parent/'integration/private-preview'
spec=importlib.util.spec_from_file_location('builder',PRIVATE/'build_private_preview.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
PORT='18941'
URL='http://127.0.0.1:'+PORT+'/'
AUTH='?action=fv_ex2_private_render&_wpnonce=TEST_NONCE&mock_optin=yes&mock_env=staging&mock_login=yes&mock_edit=yes'

class ComposerHeaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='fv-stage-header-')
        cls.path=Path(cls.tmp.name)
        cls.index=("<!doctype html><html><head>"+
            ''.join(f'<link rel="stylesheet" href="./{n}">' for n in
                     ('flagship.css','chronicle.css','chronicle-lens.css','inquiry.css','observer-lab.css','reading-trail.css'))+
            ''.join(f'<script src="./{n}" defer></script>' for n in
                     ('flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js'))+
            '</head><body><!-- DO NOT DEPLOY AS THE WORDPRESS HOME PAGE -->'+
            '<div data-fv-home-flagship>DESIGN STUDY · NOT LIVE</div></body></html>')
        names=('flagship.css','chronicle.css','chronicle-lens.css','inquiry.css','observer-lab.css','reading-trail.css',
               'flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js')
        files={'index.html':cls.index.encode(),**{name:b'/* synthetic fixture */' for name in names}}
        (cls.path/'fv-ex2-private-payload.php').write_bytes(builder.php_payload(files))
        (cls.path/'fv-ex2-private-preview.php').write_bytes((PRIVATE/'fv-ex2-private-preview.php').read_bytes())
        env=dict(os.environ,FV_EX2_MOCK_PLUGIN_ROOT=str(cls.path))
        cls.proc=subprocess.Popen(['php','-S','127.0.0.1:'+PORT,'-t',str(PRIVATE/'mock'),str(PRIVATE/'mock/router.php')],
                                  stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env)
        for _ in range(80):
            try:cls.get(URL);break
            except Exception:time.sleep(.1)
        else:raise RuntimeError('PHP fixture server unavailable')

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate();cls.proc.wait(timeout=4);cls.tmp.cleanup()

    @staticmethod
    def get(url):
        try:
            with urllib.request.urlopen(url,timeout=4) as r:return r.status,r.read(),dict(r.headers)
        except urllib.error.HTTPError as e:return e.code,e.read(),dict(e.headers)

    def test_headers_match_exact_original_html(self):
        status,body,headers=self.get(URL+AUTH)
        self.assertEqual(status,200)
        self.assertEqual(headers.get('X-FV-EX2-Index-SHA256'),hashlib.sha256(self.index.encode()).hexdigest())
        self.assertIn(b'DESIGN STUDY',body)
        self.assertIn('no-store',headers.get('Cache-Control',''))

    def test_unauthorized_has_no_source_attestation_header(self):
        status,body,headers=self.get(URL+AUTH.replace('mock_env=staging','mock_env=production'))
        self.assertEqual(status,403)
        self.assertNotIn('X-FV-EX2-Index-SHA256',headers)
        self.assertEqual(body,b'')

    def test_tampered_payload_has_no_attestation_header(self):
        p=self.path/'fv-ex2-private-payload.php';original=p.read_bytes()
        p.write_bytes(original.replace(b"'index.html' => '",b"'index.html' => 'A",1))
        try:
            status,body,headers=self.get(URL+AUTH)
            self.assertEqual(status,503)
            self.assertEqual(body,b'')
            self.assertNotIn('X-FV-EX2-Index-SHA256',headers)
        finally:p.write_bytes(original)

if __name__=='__main__':unittest.main()
