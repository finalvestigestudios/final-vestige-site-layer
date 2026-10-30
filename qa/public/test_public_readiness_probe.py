"""Offline tests; fake HTTP responses; never access public network."""
import io
import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import patch

from public_readiness_probe import FirstPartyRedirects, first_party, inspect_legacy, probe, ROUTES, PDF


class FakeResponse:
    def __init__(self, data, mime, url, code=200):
        self.file = io.BytesIO(data)
        self.headers = {"Content-Type": mime}
        self.url = url
        self.code = code
    def __enter__(self): return self
    def __exit__(self, *args): return None
    def geturl(self): return self.url
    def getcode(self): return self.code
    def read(self, n=-1): return self.file.read(n)


class FakeOpener:
    def __init__(self, response=None, error=None):
        self.response, self.error = response, error
    def open(self, request, timeout):
        assert request.get_method() == "GET"
        assert timeout <= 10
        if self.error: raise self.error
        return self.response


def fake_html(url, text=b"Final Vestige Focus Fieldbook The Dispatch"):
    return FakeResponse(b"<!doctype html><html><body>" + text + b"</body></html>", "text/html; charset=utf-8", url)


def fake_pdf(url, size=599946):
    return FakeResponse(b"%PDF-1.7" + b"X" * (size - 14) + b"%%EOF\n", "application/pdf", url)


class PublicProbeTests(unittest.TestCase):
    def test_first_party_valid(self): self.assertTrue(first_party("https://finalvestige.com/focus/"))
    def test_www_valid(self): self.assertTrue(first_party("https://www.finalvestige.com/"))
    def test_no_insecure_http(self): self.assertFalse(first_party("http://finalvestige.com/"))
    def test_no_external_host(self): self.assertFalse(first_party("https://finalvestige.com.evil.test/"))
    def test_no_userinfo(self): self.assertFalse(first_party("https://user:pass@finalvestige.com/"))
    def test_html_success(self):
        url = "https://finalvestige.com/focus/"
        r = probe("focus", "/focus/", "html", b"focus fieldbook", FakeOpener(fake_html(url)))
        self.assertEqual(r["outcome"], "PASS")
    def test_html_missing_copy(self):
        r = probe("focus", "/focus/", "html", b"focus fieldbook", FakeOpener(fake_html("https://finalvestige.com/focus/", b"404 in a branded page")))
        self.assertEqual(r["outcome"], "FAIL")
    def test_html_wrong_type(self):
        r = probe("focus", "/focus/", "html", b"focus fieldbook", FakeOpener(FakeResponse(b"%PDF-", "application/pdf", "https://finalvestige.com/focus/")))
        self.assertEqual(r["outcome"], "FAIL")
    def test_pdf_valid(self):
        url = "https://finalvestige.com" + PDF
        r = probe("pdf", PDF, "pdf", opener=FakeOpener(fake_pdf(url)))
        self.assertEqual(r["outcome"], "PASS")
    def test_pdf_wrong_length(self):
        url = "https://finalvestige.com" + PDF
        r = probe("pdf", PDF, "pdf", opener=FakeOpener(fake_pdf(url, size=599945)))
        self.assertEqual(r["outcome"], "FAIL")
    def test_pdf_wrong_signature(self):
        url = "https://finalvestige.com" + PDF
        r = probe("pdf", PDF, "pdf", opener=FakeOpener(FakeResponse(b"not a PDF", "application/pdf", url)))
        self.assertEqual(r["outcome"], "FAIL")
    def test_pdf_truncated(self):
        url = "https://finalvestige.com" + PDF
        r = probe("pdf", PDF, "pdf", opener=FakeOpener(FakeResponse(b"%PDF-1.7", "application/pdf", url)))
        self.assertEqual(r["outcome"], "FAIL")
    def test_host_leaving(self):
        r = probe("focus", "/focus/", "html", opener=FakeOpener(fake_html("https://external.test/")))
        self.assertEqual(r["outcome"], "INCONCLUSIVE")
    def test_dns_error_is_not_site_fail(self):
        r = probe("focus", "/focus/", "html", opener=FakeOpener(error=URLError("DNS unavailable")))
        self.assertEqual(r["outcome"], "INCONCLUSIVE")
    def test_redirect_guard_rejects_external(self):
        handler = FirstPartyRedirects()
        with self.assertRaises(URLError):
            handler.redirect_request(None, None, 302, "moved", {}, "https://external.test")
    def test_legacy_redirect_classifies_without_following(self):
        url = "https://finalvestige.com/72-hours-without-the-tap/"
        e = HTTPError(url, 301, "moved", {"Location": "/research-sources/"}, None)
        r = inspect_legacy("legacy", "/72-hours-without-the-tap/", FakeOpener(error=e))
        self.assertEqual(r["outcome"], "OBSERVED")
        self.assertEqual(r["status"], 301)
        self.assertEqual(r["redirect_location"], "https://finalvestige.com/research-sources/")
    def test_legacy_gone_classification(self):
        url = "https://finalvestige.com/72-hours-without-the-tap/"
        r = inspect_legacy("legacy", "/72-hours-without-the-tap/", FakeOpener(error=HTTPError(url, 410, "gone", {}, None)))
        self.assertEqual(r["outcome"], "OBSERVED")
        self.assertEqual(r["status"], 410)
    def test_core_routes_exactly_four(self): self.assertEqual(len(ROUTES), 4)


if __name__ == "__main__": unittest.main()
