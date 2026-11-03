"""Adversarial source-only tests. No network, CMS credentials, or page mutation."""
import unittest
from audit_published_homepage import audit_page, reproduced_nypl_map, unpack_page

GOOD = '<!-- wp:html --><section class="fv-hf"><div class="fv-hf__opening"></div><div class="fv-hf__case"></div></section><!-- /wp:html -->'
MARGINS = '<span class="fv-margin-strip__item">item</span>' * 72
FOCUS = '<a href="https://finalvestige.com/focus/">Focus</a><a href="/focus/">Focus</a>'
SOURCE = MARGINS + '<!-- wp:jetpack/subscriptions {"subscribePlaceholder":"Email"} /-->' + FOCUS + GOOD


def page(content=SOURCE, modified="2026-11-02T17:48:13"):
    return {"data": {"id": 6, "status": "publish",
                     "modified": modified, "content": content}}


class LiveDriftTest(unittest.TestCase):
    def test_baseline_guards_never_authorize_release(self):
        result = audit_page(page(), GOOD)
        self.assertTrue(all(result["guards"].values()))
        self.assertEqual(result["release_decision"], "HOLD")

    def test_live_image_detected_but_catalog_link_allowed(self):
        src = "https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg?fit=1024"
        self.assertTrue(reproduced_nypl_map('<img src="' + src + '">'))
        self.assertFalse(reproduced_nypl_map('<a href="https://digitalcollections.nypl.org/items/any">NYPL original catalog</a>'))

    def test_srcset_percent_encoding_cannot_bypass(self):
        self.assertTrue(reproduced_nypl_map('<source srcset="https://x.test/edit-017-v02-nypl-5003296-original%2Ejpg 1024w">'))

    def test_css_background_image_cannot_bypass(self):
        self.assertTrue(reproduced_nypl_map('<style>.x{background-image:url(https://a.test/edit-017-v02-nypl-5003296-original.jpg)}</style>'))

    def test_missing_margins_and_subscription_fail(self):
        result = audit_page(page(content=SOURCE.replace(MARGINS, "").replace("jetpack/subscriptions", "jetpack/other")), GOOD)
        self.assertFalse(result["guards"]["margins_72_present"])
        self.assertFalse(result["guards"]["jetpack_subscription_present"])

    def test_changed_candidate_fails_content_parity(self):
        result = audit_page(page(), GOOD.replace("fv-hf__case", "fv-hf__other"))
        self.assertFalse(result["guards"]["live_exact_candidate"])

    def test_unexpected_revision_time_holds(self):
        result = audit_page(page(), GOOD, expected_modified="2026-10-30T12:00:00")
        self.assertFalse(result["guards"]["expected_modified"])

    def test_wrong_page_or_unpublished_revision_fails(self):
        with self.assertRaisesRegex(ValueError, "unexpected"):
            unpack_page({"id": 7, "status": "publish", "content": SOURCE})
        with self.assertRaisesRegex(ValueError, "unexpected"):
            unpack_page({"id": 6, "status": "draft", "content": SOURCE})

    def test_rendered_only_export_refused(self):
        with self.assertRaisesRegex(ValueError, "raw WordPress"):
            unpack_page({"id": 6, "status": "publish", "content": {"rendered": "hey"}})

    def test_candidate_map_reproduction_rejected(self):
        candidate = GOOD.replace("</section>", '<img src="https://example.org/edit-017-v02-nypl-5003296-original.jpg"></section>')
        self.assertFalse(audit_page(page(), candidate)["guards"]["candidate_rights_safe"])

    def test_missing_fieldbook_link_rejected(self):
        self.assertFalse(audit_page(page(content=SOURCE.replace(FOCUS, "")), GOOD)["guards"]["fieldbook_links_preserved"])


if __name__ == "__main__":
    unittest.main()
