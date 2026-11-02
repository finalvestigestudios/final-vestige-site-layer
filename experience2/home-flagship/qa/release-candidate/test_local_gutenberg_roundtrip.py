"""Hostile offline tests for exact, isolated WordPress Gutenberg round-trip."""
import unittest
from verify_local_gutenberg_roundtrip import (
    guard_origin, six_block_probe, check_saved_raw, sha256,
)

class LocalPostSaveAdmission(unittest.TestCase):
    def setUp(self):
        self.candidate = '<!-- wp:html -->\n<div data-fv-home-flagship><style>x{a:b}</style><script>1</script></div>\n<!-- /wp:html -->'
        self.content, self.protected = six_block_probe(self.candidate)

    def test_exact_raw_roundtrip_accepts(self):
        check_saved_raw(self.content, self.candidate, self.protected)
        self.assertEqual(len(sha256(self.content)), 64)

    def test_inline_script_strip_detected(self):
        with self.assertRaisesRegex(ValueError, 'SAVE_CHANGED_BYTES'):
            check_saved_raw(self.content.replace('<script>1</script>', ''), self.candidate, self.protected)

    def test_gutenberg_comment_rewrite_detected(self):
        with self.assertRaisesRegex(ValueError, 'SAVE_CHANGED_BYTES'):
            check_saved_raw(self.content.replace('<!-- wp:html -->', '<!-- wp:html /-->', 1),
                            self.candidate, self.protected)

    def test_protected_focus_link_loss_detected(self):
        with self.assertRaisesRegex(ValueError, 'SAVE_CHANGED_BYTES'):
            check_saved_raw(self.content.replace('href="/focus/"', 'href="/gone/"'),
                            self.candidate, self.protected)

    def test_unexpected_editor_normalization_detected(self):
        with self.assertRaisesRegex(ValueError, 'SAVE_CHANGED_BYTES'):
            check_saved_raw(self.content.replace('\n', '\r\n'), self.candidate, self.protected)

    def test_allows_only_exact_local_admin_origin(self):
        guard_origin('http://127.0.0.1:9400/wp-admin/post-new.php?post_type=page')
        for url in ('https://finalvestige.com/wp-admin/',
                    'http://localhost:9400/wp-admin/',
                    'http://127.0.0.1:9401/wp-admin/',
                    'http://127.0.0.1:9400.evil.test/wp-admin/',
                    'http://127.0.0.1:9400/wp-json/',
                    'http://admin:password@127.0.0.1:9400/wp-admin/'):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, 'LOCAL_WORDPRESS'):
                guard_origin(url)

if __name__ == '__main__':
    unittest.main()
