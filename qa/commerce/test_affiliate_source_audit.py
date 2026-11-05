"""Fully offline regression tests for source-only Awin view/click distinction."""
import unittest
from affiliate_source_audit import _url_kind, audit_page, audit_snapshot


def page(html, description=""):
    return {"id": 99, "slug": "test-guide", "status": "publish", "content": html, "meta": {"advanced_seo_description": description}}


class AffiliateSourceTest(unittest.TestCase):
    def test_awin_cread_is_click_url_not_view(self):
        self.assertEqual(_url_kind("https://www.awin1.com/cread.php?s=1&r=2"), "awin_click_url")

    def test_awin_cshow_is_view_url_not_click(self):
        self.assertEqual(_url_kind("https://www.awin1.com/cshow.php?s=1&r=2"), "awin_creative_view_url")

    def test_host_must_match_exactly(self):
        self.assertEqual(_url_kind("https://www.awin1.com.evil.invalid/cshow.php"), "external_other")

    def test_relative_url_is_first_party(self):
        self.assertEqual(_url_kind("/focus/"), "site_or_relative")

    def test_supported_awclick_is_click(self):
        self.assertEqual(_url_kind("https://awin1.com/awclick.php?mid=1"), "awin_click_url")

    def test_full_good_banner_classified_separately(self):
        src = '<a href="https://www.awin1.com/cread.php?s=1&amp;r=2" rel="sponsored noopener noreferrer"><img alt="Advertiser banner" loading="lazy" src="https://www.awin1.com/cshow.php?s=1&amp;r=2"></a>'
        a = audit_page(page(src, "Guide"))
        self.assertEqual((a["awin_click_link_count"], a["awin_creative_view_image_count"]), (1, 1))
        self.assertEqual(a["sponsored_attribute_failures"], 0)
        self.assertEqual(a["view_image_missing_alt_count"], 0)
        self.assertIn("third_party_image_request_on_render_review_consent_and_network", a["review_flags"])

    def test_missing_rel_is_flagged(self):
        a = audit_page(page('<a href="https://www.awin1.com/cread.php?s=1">Buy</a>'))
        self.assertEqual(a["sponsored_attribute_failures"], 1)

    def test_external_direct_link_is_not_affiliate_click(self):
        a = audit_page(page('<a href="https://merchant.example/products">Info</a>'))
        self.assertEqual(a["awin_click_link_count"], 0)
        self.assertEqual(a["external_non_awin_link_count"], 1)

    def test_missing_alt_flagged(self):
        a = audit_page(page('<img src="https://awin1.com/cshow.php?s=1">'))
        self.assertEqual(a["view_image_missing_alt_count"], 1)

    def test_empty_description_flagged_not_assumed_no_rendered_meta(self):
        a = audit_page(page(""))
        self.assertFalse(a["dedicated_seo_description_present"])
        self.assertIn("dedicated_seo_description_empty", a["review_flags"])

    def test_content_as_raw(self):
        a = audit_page({"content": {"raw": '<img src="https://awin1.com/cshow.php?s=1">'}})
        self.assertEqual(a["awin_creative_view_image_count"], 1)

    def test_snapshot_schema_fail_closed(self):
        with self.assertRaises(ValueError):
            audit_snapshot({"posts": []})

    def test_snapshot_network_free_contract(self):
        a = audit_snapshot({"pages": [page('<a href="/focus/">Focus</a>')]})
        self.assertEqual(a["network_requests_performed"], 0)
        self.assertEqual(len(a["pages"]), 1)


if __name__ == "__main__":
    unittest.main()
