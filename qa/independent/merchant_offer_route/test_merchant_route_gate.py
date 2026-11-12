"""Synthetic, offline failure modes for offer/redirect eligibility evidence."""
import unittest
from copy import deepcopy
from datetime import date
from merchant_route_gate import assess


TODAY = date(2026, 11, 12)
BASE = {
    "observed_on": "2026-11-12",
    "affiliate_url": "https://www.awin1.com/cread.php?test=offline",
    "resolved_url": "https://shop.minimuseum.com/pages/mini-museum-fourth-edition-mm4",
    "expected_merchant_host": "shop.minimuseum.com",
    "featured_offer": {"name": "Fourth Edition Large", "availability": "sold_out"},
    "landing_type": "specific_edition",
    "cta_copy": "SEE THE CURRENT COLLECTION",
}


class MerchantRouteTests(unittest.TestCase):
    def sample(self, **values):
        x = deepcopy(BASE)
        x.update(values)
        return x

    def test_current_sold_out_edition_holds(self):
        self.assertEqual(assess(BASE, TODAY)["status"], "HOLD_OFFER_MATCH")

    def test_in_stock_offer_only_passes_route_not_purchase(self):
        x = self.sample(featured_offer={"name": "Example", "availability": "in_stock"})
        r = assess(x, TODAY)
        self.assertEqual(r["status"], "PASS_ROUTE_ONLY")
        self.assertIn("No checkout", r["reasons"][1])

    def test_unknown_stock_holds(self):
        x = self.sample(featured_offer={"name": "Example", "availability": "unknown"})
        self.assertEqual(assess(x, TODAY)["status"], "HOLD_OFFER_MATCH")

    def test_untrusted_redirect_holds(self):
        self.assertEqual(assess(self.sample(resolved_url="https://example.org/other"), TODAY)["status"], "HOLD_ROUTE_OR_EVIDENCE")

    def test_non_https_redirect_holds(self):
        self.assertEqual(assess(self.sample(resolved_url="http://shop.minimuseum.com/"), TODAY)["status"], "HOLD_ROUTE_OR_EVIDENCE")

    def test_untracked_link_holds(self):
        self.assertEqual(assess(self.sample(affiliate_url="https://shop.minimuseum.com/"), TODAY)["status"], "HOLD_ROUTE_OR_EVIDENCE")

    def test_stale_inventory_holds(self):
        x = self.sample(observed_on="2026-11-01")
        self.assertEqual(assess(x, TODAY)["status"], "HOLD_ROUTE_OR_EVIDENCE")

    def test_future_inventory_holds(self):
        x = self.sample(observed_on="2026-11-13")
        self.assertEqual(assess(x, TODAY)["status"], "HOLD_ROUTE_OR_EVIDENCE")

    def test_missing_required_field_fails_closed(self):
        x = self.sample()
        del x["featured_offer"]
        self.assertEqual(assess(x, TODAY)["status"], "HOLD_EVIDENCE_INVALID")

    def test_invalid_availability_fails_closed(self):
        x = self.sample(featured_offer={"availability": "maybe"})
        self.assertEqual(assess(x, TODAY)["status"], "HOLD_ROUTE_OR_EVIDENCE")

    def test_no_copy_fails_closed(self):
        self.assertEqual(assess(self.sample(cta_copy=""), TODAY)["status"], "HOLD_ROUTE_OR_EVIDENCE")

    def test_catalog_stock_may_pass_only_route(self):
        x = self.sample(landing_type="catalog", featured_offer={"name": "Current items", "availability": "in_stock"})
        self.assertEqual(assess(x, TODAY)["status"], "PASS_ROUTE_ONLY")


if __name__ == "__main__":
    unittest.main()
