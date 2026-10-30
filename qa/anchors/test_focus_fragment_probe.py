"""Offline tests for the non-mutating fragment audit."""
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parent))
from focus_fragment_probe import FragmentParser, FirstPartyRedirect, audit, main


class FragmentTests(unittest.TestCase):
    def test_valid_multiple_ctas(self):
        html = '<div id="subscribe-blog"></div><a href="#subscribe-blog" data-fv-location="after_why">Get</a><a href="#subscribe-blog">Get</a>'
        value = audit(html)
        self.assertEqual(value["verdict"], "PASS_SOURCE")
        self.assertEqual(value["cta_count"], 2)
        self.assertTrue(value["target_in_html"])

    def test_missing_target_is_review_not_broken_claim(self):
        value = audit('<a href="#subscribe-blog">Get</a>')
        self.assertEqual(value["verdict"], "REVIEW_RENDERED_ANCHOR")
        self.assertFalse(value["browser_verified"])
        self.assertFalse(value["form_submit_tested"])

    def test_no_cta_is_review(self):
        self.assertEqual(audit('<p>Hi</p>')["verdict"], "REVIEW_NO_FRAGMENT_CTAS")

    def test_named_anchor_supported(self):
        self.assertEqual(audit('<a name="subscribe-blog"></a><a href="#subscribe-blog">Go</a>')["verdict"], "PASS_SOURCE")

    def test_quoted_href_comparison(self):
        self.assertEqual(audit('<a href="#subscribe-blog-other">Go</a>')["cta_count"], 0)

    def test_script_text_does_not_count_as_id(self):
        value = audit('<script>let fake = "id=subscribe-blog";</script><a href="#subscribe-blog">Go</a>')
        self.assertEqual(value["verdict"], "REVIEW_RENDERED_ANCHOR")

    def test_html_entities_and_case(self):
        value = audit('<DIV id="subscribe-blog"></DIV><A href="#subscribe-blog">Go</A>')
        self.assertEqual(value["verdict"], "PASS_SOURCE")

    def test_redirect_blocks_external_host(self):
        with self.assertRaises(ValueError):
            FirstPartyRedirect().redirect_request(None, None, 302, "", {}, "https://example.net/focus/")

    def test_redirect_blocks_http(self):
        with self.assertRaises(ValueError):
            FirstPartyRedirect().redirect_request(None, None, 302, "", {}, "http://finalvestige.com/focus/")

    def test_redirect_blocks_excessive_hops(self):
        h = FirstPartyRedirect()
        h.hops = 3
        with self.assertRaises(ValueError):
            h.redirect_request(None, None, 302, "", {}, "https://finalvestige.com/focus/")

    def test_file_mode_missing_target_exit2(self):
        with tempfile.TemporaryDirectory() as directory:
            f = Path(directory) / "fixture.html"
            f.write_text('<a href="#subscribe-blog">Get</a>', encoding="utf-8")
            with patch("sys.stdout", new_callable=io.StringIO) as out:
                code = main(["--html-file", str(f)])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(out.getvalue())["verdict"], "REVIEW_RENDERED_ANCHOR")

    def test_file_mode_valid_exit0(self):
        with tempfile.TemporaryDirectory() as directory:
            f = Path(directory) / "fixture.html"
            f.write_text('<span id="subscribe-blog"></span><a href="#subscribe-blog">Get</a>', encoding="utf-8")
            with patch("sys.stdout", new_callable=io.StringIO) as out:
                code = main(["--html-file", str(f)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out.getvalue())["verdict"], "PASS_SOURCE")

    def test_network_failure_is_inconclusive(self):
        with patch("focus_fragment_probe.fetch", side_effect=URLError("dns unavailable")):
            with patch("sys.stdout", new_callable=io.StringIO) as out:
                code = main([])
            self.assertEqual(code, 2)
            self.assertIn("INCONCLUSIVE_FETCH", out.getvalue())


if __name__ == "__main__":
    unittest.main()
