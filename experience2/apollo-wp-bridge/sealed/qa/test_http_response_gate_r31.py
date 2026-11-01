#!/usr/bin/env python3
"""R31 adversarial contract tests; no WordPress, network, or paid dependencies."""
import unittest
from pathlib import Path
import tempfile
from http_response_gate_r31 import audit, verify_zip

NONCE='A'*24
BASE_CSP=("default-src 'none'; script-src 'nonce-"+NONCE+"'; style-src 'nonce-"+NONCE+
          "'; img-src 'none'; connect-src 'none'; form-action 'none'; frame-ancestors 'self'")
HEADERS={'Content-Security-Policy':BASE_CSP,'X-Robots-Tag':'noindex, nofollow, noarchive',
         'Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff',
         'X-FV-EX2-Apollo-Source-Head':'74375657f2cdaac0710f94c6de6c24534ee06858',
         'Cache-Control':'no-store, private'}

def fixture():
    body=('<!doctype html><html><head><style nonce="'+NONCE+'"></style></head><body>'+
          '<section data-concordance-record></section>'*6+
          '<div data-media-hold="true"></div>'*6+
          '<div data-crosswalk-review="hold"></div>'+
          '<script nonce="'+NONCE+'"></script></body></html>')
    return (body+(' '*150000)).encode('utf8')

class HTTPGateMutations(unittest.TestCase):
    def test_valid_custody(self):
        r=audit(200,HEADERS,fixture())
        self.assertEqual(r['bytes'],len(fixture()))
    def test_no_error_response_may_pass(self):
        for code in (403,404,500):
            with self.subTest(code=code),self.assertRaises(AssertionError): audit(code,HEADERS,fixture())
    def test_header_absence_rejected(self):
        for key in HEADERS:
            with self.subTest(key=key),self.assertRaises(AssertionError):
                audit(200,{k:v for k,v in HEADERS.items() if k!=key},fixture())
    def test_bad_nonce_binding_rejected(self):
        with self.assertRaises(AssertionError): audit(200,HEADERS,fixture().replace(NONCE.encode(),b'B'*24))
    def test_permissive_csp_rejected(self):
        with self.assertRaises(AssertionError):
            audit(200,{**HEADERS,'Content-Security-Policy':BASE_CSP+"; script-src-elem 'unsafe-inline'"},fixture())
    def test_fabricated_geo_rejected(self):
        with self.assertRaises(AssertionError):
            audit(200,HEADERS,fixture().replace(b'</body>',b'<i data-lat="40.0"></i></body>'))
    def test_missing_nasa_review_rejected(self):
        with self.assertRaises(AssertionError):
            audit(200,HEADERS,fixture().replace(b'data-media-hold="true"',b'data-media-hold="false"',1))
    def test_untrusted_archive_refused(self):
        with tempfile.TemporaryDirectory() as t:
            bad=Path(t)/'untrusted.zip';bad.write_bytes(b'not-a-zip')
            with self.assertRaises(ValueError):verify_zip(bad)

if __name__=='__main__':unittest.main()
