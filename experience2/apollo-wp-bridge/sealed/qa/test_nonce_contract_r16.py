"""R16: WordPress nonce API parity through actual PHP HTTP responses.

This is NOT installed WordPress: its shim deliberately models WP core's
check_ajax_referer $stop behavior, _ajax_nonce lookup precedence, and valid
nonce ages 1/2 so tests detect accidental reversion to default output "-1".
"""
from __future__ import annotations
from urllib.parse import urlencode
import unittest
import test_http


class TestRealHTTPNonceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_http.ApolloHttp.setUpClass()
        cls.base = test_http.ApolloHttp.base

    @classmethod
    def tearDownClass(cls):
        test_http.ApolloHttp.tearDownClass()

    def request(self, action, token='http-stub-fixed-nonce', *, extra=None, mode='editor'):
        args={'action':action, 'file':'source-context.json'}
        if token is not None:
            args['_wpnonce']=token
        if extra:
            args.update(extra)
        code,headers,data=test_http.fetch(self.base,
             '/wp-admin/admin-ajax.php?'+urlencode(args),mode)
        return code,{k.lower():v for k,v in headers.items()},data

    def test_01_valid_current_nonce_allows_both_routes(self):
        for action in ('fv_ex2_apollo_sealed_page','fv_ex2_apollo_sealed_download'):
            with self.subTest(action=action):
                code,h,data=self.request(action)
                self.assertEqual(code,200)
                self.assertTrue(data)

    def test_02_valid_12_to_24h_wordpress_nonce_still_accepted(self):
        for action in ('fv_ex2_apollo_sealed_page','fv_ex2_apollo_sealed_download'):
            with self.subTest(action=action):
                code,h,data=self.request(action,'http-stub-old-nonce')
                self.assertEqual(code,200)
                self.assertTrue(data)

    def test_03_missing_or_blank_nonce_denied_empty_and_uncached(self):
        for token in (None, ''):
            for action in ('fv_ex2_apollo_sealed_page','fv_ex2_apollo_sealed_download'):
                with self.subTest(token=token,action=action):
                    code,h,data=self.request(action,token)
                    self.assertEqual((code,data),(403,b''))
                    self.assertIn('no-store',h.get('cache-control',''))

    def test_04_structured_array_nonce_denied_without_php_fatal(self):
        for action in ('fv_ex2_apollo_sealed_page','fv_ex2_apollo_sealed_download'):
            with self.subTest(action=action):
                code,h,data=self.request(action,None,extra={'_wpnonce[]':'http-stub-fixed-nonce'})
                self.assertEqual((code,data),(403,b''))

    def test_05_oversized_nonce_denied_without_reflection(self):
        code,h,data=self.request('fv_ex2_apollo_sealed_page','x'*1025)
        self.assertEqual((code,data),(403,b''))
        self.assertIn('no-store',h.get('cache-control',''))

    def test_06_explicit_wpnonce_cannot_be_shadowed_by_ajax_nonce(self):
        code,h,data=self.request('fv_ex2_apollo_sealed_page',
                                 extra={'_ajax_nonce':'wrong-shadow'})
        self.assertEqual(code,200)
        self.assertIn(b'id="source-concordance"',data)

    def test_07_wrong_wpnonce_not_rescued_by_valid_ajax_nonce(self):
        code,h,data=self.request('fv_ex2_apollo_sealed_page','wrong',
                                 extra={'_ajax_nonce':'http-stub-fixed-nonce'})
        self.assertEqual((code,data),(403,b''))

    def test_08_valid_nonce_cannot_elevate_unauthorized_editor_role(self):
        for mode in ('guest','reader','production','off'):
            with self.subTest(mode=mode):
                code,h,data=self.request('fv_ex2_apollo_sealed_page','http-stub-old-nonce',mode=mode)
                self.assertEqual((code,data),(403,b''))
                self.assertIn('no-store',h.get('cache-control',''))

    def test_09_nonce_failure_never_returns_wordpress_default_minus_one(self):
        for token in ('bad','',None):
            with self.subTest(token=token):
                code,h,data=self.request('fv_ex2_apollo_sealed_download',token)
                self.assertEqual((code,data),(403,b''))
                self.assertNotEqual(data,b'-1')

    def test_10_valid_nonce_export_preserves_source_custody_hash(self):
        code,h,data=self.request('fv_ex2_apollo_sealed_download','http-stub-old-nonce')
        self.assertEqual(code,200)
        self.assertEqual(h.get('x-fv-ex2-apollo-asset-sha256'),
                         __import__('hashlib').sha256(data).hexdigest())
        self.assertIn('no-store',h.get('cache-control',''))

if __name__=='__main__': unittest.main()
