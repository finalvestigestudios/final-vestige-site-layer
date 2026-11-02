"""Prevent origin prefix confusion and production avatar-setting regressions."""
import unittest
from wordpress_r68 import blueprint, is_strict_loopback_request

class R72LoopbackSafety(unittest.TestCase):
    def test_only_literal_http_loopback_port_9438(self):
        self.assertTrue(is_strict_loopback_request('http://127.0.0.1:9438/wp-content/script.js'))
        self.assertTrue(is_strict_loopback_request('http://127.0.0.1:9438/?pagename=fv-apollo-review-private'))
    def test_host_prefix_confusion_refused(self):
        for host in ('http://127.0.0.1:9438.evil.example/', 'http://127.0.0.1.evil.example:9438/', 'http://127.0.0.11:9438/'):
            with self.subTest(host=host):
                self.assertFalse(is_strict_loopback_request(host))
    def test_remote_and_scheme_substitutions_refused(self):
        for address in ('https://127.0.0.1:9438/', 'http://localhost:9438/', 'http://[::1]:9438/', 'http://finalvestige.com:9438/', '//127.0.0.1:9438/', 'javascript:alert(1)'):
            with self.subTest(address=address):
                self.assertFalse(is_strict_loopback_request(address))
    def test_bad_ports_and_embedded_credentials_refused(self):
        for address in ('http://127.0.0.1:443/', 'http://admin:password@127.0.0.1:9438/', 'http://127.0.0.1:port/', None, ''):
            with self.subTest(address=address):
                self.assertFalse(is_strict_loopback_request(address))
    def test_gravatar_disable_applies_only_after_localhost_guard(self):
        code=blueprint()['steps'][-1]['code']
        self.assertIn("NONLOCAL_WORDPRESS_REFUSED",code)
        self.assertIn("update_option('show_avatars', 0)",code)
        self.assertLess(code.index("NONLOCAL_WORDPRESS_REFUSED"),code.index("update_option('show_avatars', 0)"))
        self.assertIn("'private'",code)
        self.assertNotIn('finalvestige.com',code)
    def test_no_approval_or_license_markers(self):
        code=blueprint()['steps'][-1]['code'].lower()
        self.assertNotIn('rights_cleared',code)
        self.assertNotIn('allow_remote',code)
        self.assertNotIn('publish',code)
if __name__=='__main__':unittest.main()
