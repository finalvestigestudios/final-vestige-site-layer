"""No-network regression tests for candidate internal link errors."""
import unittest

from canonical_crosslinks import inspect, normalized_path

CANON = "https://finalvestige.com/2026/08/16/the-morning-san-francisco-lost-its-water/"
OTHER = "https://finalvestige.com/2026/08/16/the-cisterns-beneath-san-francisco/"


def snapshot(href, published=None, retired=None):
    return {
        "published": published or [
            {"url": CANON, "kind": "post"},
            {"url": OTHER, "kind": "post"},
            {"url": "https://finalvestige.com/focus/", "kind": "page"},
        ],
        "sources": [{"url": OTHER, "html": f'<p><a href="{href}">Read the source</a></p>'}],
        "retired_or_draft_urls": retired or [],
    }


class CanonicalCrosslinksTests(unittest.TestCase):
    def test_actual_short_slug_is_candidate_not_claimed_404(self):
        a = inspect(snapshot("/the-morning-san-francisco-lost-its-water/"))
        self.assertEqual(a[0]["code"], "NONCANONICAL_POST_LINK_CANDIDATE")
        self.assertEqual(a[0]["suggested_canonical"], "/2026/08/16/the-morning-san-francisco-lost-its-water/")
        self.assertFalse(a[0]["http_status_verified"])

    def test_current_canonical_passes(self):
        self.assertEqual(inspect(snapshot(CANON)), [])

    def test_known_root_page_passes(self):
        self.assertEqual(inspect(snapshot("/focus/")), [])

    def test_external_and_mailto_ignored(self):
        self.assertEqual(inspect(snapshot("https://example.com/the-morning-san-francisco-lost-its-water/")), [])
        self.assertEqual(inspect(snapshot("mailto:test@example.com")), [])

    def test_first_party_www_and_query_are_normalized(self):
        self.assertEqual(inspect(snapshot("https://www.finalvestige.com/2026/08/16/the-morning-san-francisco-lost-its-water/?x=1")), [])

    def test_draft_candidate(self):
        a = inspect(snapshot("/72-hours-without-the-tap/", retired=["https://finalvestige.com/72-hours-without-the-tap/"]))
        self.assertEqual(a[0]["code"], "DRAFT_DESTINATION_CANDIDATE")
        self.assertIsNone(a[0]["suggested_canonical"])

    def test_dynamic_plugin_and_media_routes_are_excluded(self):
        for path in ("/portal/space/general-history/home", "/wp-content/uploads/file.pdf", "/wp-json/wp/v2/posts"):
            self.assertEqual(inspect(snapshot(path)), [])

    def test_fragments_and_tel_links_ignored(self):
        self.assertEqual(inspect(snapshot("#faq-phone")), [])
        self.assertEqual(inspect(snapshot("tel:+11234567890")), [])

    def test_ambiguous_slug_does_not_guess_target(self):
        duplicate = "https://finalvestige.com/2025/02/01/the-morning-san-francisco-lost-its-water/"
        s = snapshot("/the-morning-san-francisco-lost-its-water/")
        s["published"].append({"url": duplicate, "kind": "post"})
        self.assertEqual(inspect(s), [])

    def test_sanitized_no_network_data(self):
        s = snapshot("/the-morning-san-francisco-lost-its-water/")
        before = str(s)
        inspect(s)
        self.assertEqual(str(s), before)

    def test_normalizer_rejects_non_http_schemes(self):
        self.assertIsNone(normalized_path("javascript:alert(1)"))
        self.assertIsNone(normalized_path("//another-site.com/a"))


if __name__ == "__main__":
    unittest.main()
