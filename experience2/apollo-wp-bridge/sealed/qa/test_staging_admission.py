"""Read-only staging-admission contract; actual PHP socket, synthetic WordPress only."""
from __future__ import annotations
import hashlib
from pathlib import Path
import os
import tempfile
import unittest
from staging_admission import (AdmissionError, admit, no_redirect_fetch,
                               read_cookie_file, require_safe_origin)
import test_http


class TestStagingAdmission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_http.ApolloHttp.setUpClass()
    @classmethod
    def tearDownClass(cls):
        test_http.ApolloHttp.tearDownClass()

    def test_provenance_and_exact_five_exports_over_real_php_http(self):
        r = admit(test_http.ApolloHttp.base, '/review', 'fv_test_mode=editor', allow_stub=True)
        self.assertEqual(r['status'], 'PASS_HTTP_INTEGRITY_ONLY')
        self.assertEqual(r['anonymous_private_page'], 403)
        self.assertEqual(len(r['exports_sha256']), 5)
        self.assertFalse(r['wordpress_integrated'])
        self.assertEqual(r['axe'], 'NOT_TESTED')
        self.assertEqual(len(r['fragment_sha256']), 64)

    def test_no_production_or_public_host_or_cleartext_remote(self):
        for u in ('https://finalvestige.com', 'https://www.finalvestige.com',
                  'https://staging.finalvestige.com', 'http://preview.example.org',
                  'http://127.0.0.1:8080', 'https://preview.example.org/?x=1',
                  'https://user:secret@preview.example.org',
                  'https://preview.example.org/wordpress'):
            with self.subTest(origin=u), self.assertRaises(AdmissionError):
                require_safe_origin(u)
        self.assertEqual(require_safe_origin('https://preview.example.org'), 'https://preview.example.org')

    def test_role_denials(self):
        for role in ('guest','reader','production','off'):
            with self.subTest(role=role), self.assertRaises(AdmissionError):
                admit(test_http.ApolloHttp.base, '/review', 'fv_test_mode='+role, allow_stub=True)

    def test_remote_browser_policy_is_not_certified(self):
        r = admit(test_http.ApolloHttp.base, '/review', 'fv_test_mode=editor', allow_stub=True)
        self.assertEqual(r['browser_csp_enforcement'], 'NOT_TESTED')
        self.assertIn('does NOT establish Playwright', r['limitations'])

    def test_header_downgrade_and_digest_mutation_fail_closed(self):
        def bad_header(url, cookie=''):
            status, h, data = no_redirect_fetch(url, cookie)
            if h.get('x-fv-ex2-apollo-fragment-sha256'):
                h['x-fv-ex2-apollo-fragment-sha256'] = '0'*64
            return status, h, data
        with self.assertRaisesRegex(AdmissionError, 'provenance hash'):
            admit(test_http.ApolloHttp.base, '/review', 'fv_test_mode=editor', allow_stub=True, fetch=bad_header)

        def bad_csp(url, cookie=''):
            status, h, data = no_redirect_fetch(url, cookie)
            if 'content-security-policy' in h:
                h['content-security-policy'] = h['content-security-policy'].replace("frame-ancestors 'self'", '')
            return status, h, data
        with self.assertRaisesRegex(AdmissionError, 'CSP term'):
            admit(test_http.ApolloHttp.base, '/review', 'fv_test_mode=editor', allow_stub=True, fetch=bad_csp)

    def test_concordance_provenance_header_mutation_denied(self):
        def bad_concordance(url, cookie=''):
            status, h, data = no_redirect_fetch(url, cookie)
            if 'x-fv-ex2-apollo-concordance-sha256' in h:
                h['x-fv-ex2-apollo-concordance-sha256'] = '0'*64
            return status, h, data
        with self.assertRaisesRegex(AdmissionError, 'concordance provenance hash'):
            admit(test_http.ApolloHttp.base, '/review', 'fv_test_mode=editor',
                  allow_stub=True, fetch=bad_concordance)

    def test_context_index_header_mutation_denied(self):
        def bad_context_header(url, cookie=''):
            status, h, data = no_redirect_fetch(url, cookie)
            if 'x-fv-ex2-apollo-context-sha256' in h:
                h['x-fv-ex2-apollo-context-sha256'] = '0'*64
            return status, h, data
        with self.assertRaisesRegex(AdmissionError, 'source context index hash mismatch'):
            admit(test_http.ApolloHttp.base, '/review', 'fv_test_mode=editor',
                  allow_stub=True, fetch=bad_context_header)

    def test_context_index_response_tampering_denied(self):
        def bad_context_export(url, cookie=''):
            status, h, data = no_redirect_fetch(url, cookie)
            if cookie and 'file=source-context.json' in url:
                data = data.replace(b'"geographic_coordinates_assigned": 0',
                                    b'"geographic_coordinates_assigned": 1')
                self.assertNotEqual(data, no_redirect_fetch(url, cookie)[2])
            return status, h, data
        with self.assertRaisesRegex(AdmissionError, 'Export integrity'):
            admit(test_http.ApolloHttp.base, '/review', 'fv_test_mode=editor',
                  allow_stub=True, fetch=bad_context_export)

    def test_export_tampering_not_accepted(self):
        def bad_export(url, cookie=''):
            status, h, data = no_redirect_fetch(url, cookie)
            if cookie and 'file=evidence-export.csv' in url:
                data = data + b'FAKE'
            return status, h, data
        with self.assertRaisesRegex(AdmissionError, 'Export integrity'):
            admit(test_http.ApolloHttp.base, '/review', 'fv_test_mode=editor', allow_stub=True, fetch=bad_export)

    def test_review_path_restrictions(self):
        for path in ('//evil', 'http://evil/', '/review?nonce=secret', '/review#frag', 'review'):
            with self.subTest(path=path), self.assertRaises(AdmissionError):
                admit(test_http.ApolloHttp.base, path, 'fv_test_mode=editor', allow_stub=True)

    def test_private_cookie_file_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'cookie'
            p.write_text('wordpress_logged_in_test=secret\n', encoding='utf-8')
            p.chmod(0o600)
            self.assertEqual(read_cookie_file(p), 'wordpress_logged_in_test=secret')
            p.chmod(0o644)
            with self.assertRaises(AdmissionError): read_cookie_file(p)
            p.chmod(0o600)
            p.write_text('a=b\nEvil: injected', encoding='utf-8')
            with self.assertRaises(AdmissionError): read_cookie_file(p)


if __name__ == '__main__': unittest.main()
