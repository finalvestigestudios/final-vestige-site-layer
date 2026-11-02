import unittest

from focus_anchor_guard import audit


class FocusNoJSAnchorTests(unittest.TestCase):
    def test_static_named_anchor_resolves(self):
        r = audit('<a href="#subscribe-blog">Get book</a><span id="subscribe-blog"></span>')
        self.assertEqual(r['missing_static_targets'], {})

    def test_missing_anchor_is_nonblocking_source_review(self):
        r = audit('<a href="#subscribe-blog">Get book</a>')
        self.assertEqual(r['missing_static_targets'], {'subscribe-blog': 1})
        self.assertFalse(r['production_defect_confirmed'])

    def test_javascript_generated_anchor_is_not_static_evidence(self):
        r = audit('<a href="#subscribe-blog">Get book</a><script>anchor.id="subscribe-blog";</script>')
        self.assertEqual(r['missing_static_targets'], {'subscribe-blog': 1})

    def test_gutenberg_comment_cannot_supply_target(self):
        r = audit('<!-- <span id="subscribe-blog"></span> --><a href="#subscribe-blog">Book</a>')
        self.assertTrue(r['requires_anonymous_no_js_browser_verification'])

    def test_multiple_links_to_one_target_counted(self):
        r = audit('<a href="#subscribe-blog">1</a><a href="#subscribe-blog">2</a>')
        self.assertEqual(r['missing_static_targets'], {'subscribe-blog': 2})

    def test_other_present_target_works(self):
        r = audit('<a href="#faq">FAQ</a><h2 id="faq">Answer</h2>')
        self.assertEqual(r['missing_static_targets'], {})

    def test_native_jetpack_is_not_misclassified_as_static_anchor(self):
        r = audit('<!-- wp:jetpack/subscriptions /--><a href="#subscribe-blog">Join</a>')
        self.assertEqual(r['native_jetpack_block_count'], 1)
        self.assertEqual(r['missing_static_targets'], {'subscribe-blog': 1})

    def test_external_and_empty_hash_are_ignored(self):
        r = audit('<a href="#">Ignore</a><a href="https://other.test/#faq">Offsite</a>')
        self.assertEqual(r['fragment_links'], 0)

    def test_url_encoded_fragment(self):
        r = audit('<a href="#start%20here">go</a><div id="start here"></div>')
        self.assertEqual(r['missing_static_targets'], {})

    def test_requires_real_source(self):
        with self.assertRaises(ValueError):
            audit('  ')


if __name__ == '__main__':
    unittest.main()
