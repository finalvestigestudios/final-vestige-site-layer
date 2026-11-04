"""Hermetic regression tests: all markup is synthetic, no merchant/network traffic."""
import unittest
from audit import audit_html, audit_campaign_utm, commercial_outcome_status

AFF = "https://www.awin1.com/cread.php?awinmid=125352&amp;awinaffid=3055117"
DOC = '<p class="fv-affiliate-note">Affiliate link; we may earn a commission.</p>'

class AuditTests(unittest.TestCase):
    def test_affiliate_before_disclosure_flagged(self):
        r = audit_html(f'<a href="{AFF}" rel="sponsored">Compass image</a>' + DOC)
        self.assertEqual(r["affiliate_ctas_before_first_inline_disclosure"], 1)

    def test_affiliate_after_disclosure_not_flagged(self):
        r = audit_html(DOC + f'<a href="{AFF}" rel="sponsored">Compass</a>')
        self.assertEqual(r["affiliate_ctas_before_first_inline_disclosure"], 0)

    def test_two_links_before_note(self):
        r = audit_html(f'<a href="{AFF}" rel="sponsored">Image</a><a href="{AFF}" rel="sponsored">Text</a>' + DOC)
        self.assertEqual(r["affiliate_ctas_before_first_inline_disclosure"], 2)

    def test_missing_disclosure_remains_flagged(self):
        self.assertEqual(audit_html(f'<a href="{AFF}" rel="sponsored">Product</a>')["affiliate_ctas_before_first_inline_disclosure"], 1)

    def test_sponsored_rel(self):
        r = audit_html(f'<a href="{AFF}">Product</a>')
        self.assertEqual(r["affiliate_ctas_missing_sponsored_rel"], 1)

    def test_payhip_and_focus_separate(self):
        r = audit_html('<a href="https://payhip.com/b/ABCD">Buy</a><a href="/focus/">Free</a>')
        self.assertEqual((r["payhip_cta_count"],r["focus_link_count"]),(1,1))

    def test_native_subscriber_node_not_css_text(self):
        r = audit_html('<style>.wp-block-jetpack-subscriptions{display:block}</style><div class="wp-block-jetpack-subscriptions"></div>')
        self.assertEqual(r["native_subscription_block_nodes"], 1)

    def test_no_merchant_no_claim(self):
        r = audit_html(DOC)
        self.assertFalse(r["merchant_checkout_tested"])
        self.assertIsNone(r["realized_net_revenue"])

    def test_valid_utm_contract_not_attributed(self):
        r = audit_campaign_utm('https://finalvestige.com/collection/?utm_source=youtube&utm_medium=organic_social&utm_campaign=nav_pilot_2026_11&utm_content=ytshort_001')
        self.assertTrue(r["valid"])
        self.assertFalse(r["attribution_verified"])

    def test_missing_asset_id_rejected(self):
        r = audit_campaign_utm('https://finalvestige.com/collection/?utm_source=tiktok&utm_medium=organic_social&utm_campaign=nav_pilot_2026_11')
        self.assertFalse(r["valid"])

    def test_no_email_tracking(self):
        r = audit_campaign_utm('https://finalvestige.com/?utm_source=tiktok&utm_medium=organic_social&utm_campaign=x&utm_content=x&email=test@example.com')
        self.assertIn('PII_query_key_present',r['issues'])

    def test_duplicate_utm_rejected(self):
        r = audit_campaign_utm('https://finalvestige.com/?utm_source=tiktok&utm_source=youtube&utm_medium=organic_social&utm_campaign=x&utm_content=x')
        self.assertFalse(r['valid'])

    def test_wrong_host_rejected(self):
        r = audit_campaign_utm('https://example.com/?utm_source=tiktok&utm_medium=organic_social&utm_campaign=x&utm_content=x')
        self.assertFalse(r['valid'])

    def test_click_does_not_make_sale(self):
        r = commercial_outcome_status(external_clicks=100,leads=5)
        self.assertEqual(r['status'],'NOT_OBSERVABLE')
        self.assertIsNone(r['paid_orders'])

    def test_reported_outcomes_remain_source_reported(self):
        r = commercial_outcome_status(external_clicks=0,leads=0,verified_paid_orders=1,verified_net_revenue=12.34)
        self.assertEqual(r['status'],'SOURCE_REPORTED_ONLY')

    def test_negative_paid_orders_rejected(self):
        with self.assertRaises(ValueError):
            commercial_outcome_status(external_clicks=0,leads=0,verified_paid_orders=-1,verified_net_revenue=0)

if __name__ == '__main__':
    unittest.main()
