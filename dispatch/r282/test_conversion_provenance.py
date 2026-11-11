import unittest
from conversion_provenance import inspect, check_campaign_url

S = {"total": 3, "confirmed": 3, "unconfirmed": 2, "email_followers": 0, "wpcom_followers": 3}


def e(kind, ref, source, **kw):
    return dict(kind=kind, ref=ref, source=source, verified=True, **kw)


class ProvenanceTests(unittest.TestCase):
    def test_ambiguous_platform_totals_remain_unknown(self):
        r = inspect([], S)
        self.assertIsNone(r["provider_eligible_audience"])
        self.assertIsNone(r["net_revenue_per_1000_qualified_sessions"])
        self.assertEqual(r["provider_diagnostic"]["unconfirmed"], 2)

    def test_provider_verified_preverified_account_without_click(self):
        ev = e("confirmed_signup", "hashed_001", "jetpack_provider", provider_eligible=True, consent_recorded=True)
        self.assertEqual(inspect([ev], S)["verified_confirmed_leads_in_supplied_events"], 1)

    def test_no_consent_or_no_eligibility_is_not_lead(self):
        for field in ["consent_recorded", "provider_eligible"]:
            x = e("confirmed_signup", "hashed_001", "jetpack_provider", provider_eligible=True, consent_recorded=True)
            x[field] = False
            self.assertEqual(inspect([x], S)["verified_confirmed_leads_in_supplied_events"], 0)

    def test_unverified_and_wrong_source_not_lead(self):
        x = e("confirmed_signup", "hashed_001", "first_party_server", consent_recorded=True, provider_eligible=True)
        self.assertEqual(inspect([x], S)["verified_confirmed_leads_in_supplied_events"], 0)
        x["source"] = "jetpack_provider"
        x["verified"] = False
        self.assertEqual(inspect([x], S)["verified_confirmed_leads_in_supplied_events"], 0)

    def test_duplicate_signups_not_double_counted(self):
        x = e("confirmed_signup", "hashed_001", "jetpack_provider", consent_recorded=True, provider_eligible=True)
        self.assertEqual(inspect([x, x], S)["verified_confirmed_leads_in_supplied_events"], 1)

    def test_clicks_do_not_create_orders(self):
        x = e("cta_click", "evt_click_123", "first_party_server")
        r = inspect([x], S)
        self.assertEqual(r["verified_first_party_orders_in_supplied_events"], 0)
        self.assertEqual(r["affiliate_net_commission_in_supplied_events"], "0")

    def test_settlement_net_and_dedup(self):
        x = e("affiliate_settlement", "settlement_abc", "merchant_statement", order_ref="order_01", commission="18.50", fees="1.20", refunds="3.00")
        y = e("affiliate_settlement", "settlement_xyz", "merchant_statement", order_ref="order_01", commission="18.50", fees="1.20", refunds="3.00")
        r = inspect([x, y], S)
        self.assertEqual(r["affiliate_net_commission_in_supplied_events"], "14.30")
        self.assertEqual(r["independently_reported_affiliate_settlements_in_supplied_events"], 1)

    def test_unrefunded_commission_cannot_be_negative(self):
        x = e("affiliate_settlement", "settlement_abc", "merchant_statement", order_ref="order_01", commission="4", fees="1", refunds="7")
        with self.assertRaises(ValueError): inspect([x], S)

    def test_negative_nan_or_missing_amounts_rejected(self):
        for amount in ["-2", "NaN", "Infinity", None]:
            x = e("affiliate_settlement", "settlement_abc", "merchant_statement", order_ref="order_01", commission=amount, fees="0", refunds="0")
            with self.assertRaises(ValueError): inspect([x], S)

    def test_pii_and_link_query_exfiltration_rejected(self):
        x = e("landing_visit", "landing_evt_1", "first_party_server", landing_url="https://finalvestige.com/focus/?utm_source=youtube&utm_campaign=test&email=user%40mail.com")
        with self.assertRaises(ValueError): inspect([x], S)
        x.pop("landing_url")
        x["email"] = "somebody"
        with self.assertRaises(ValueError): inspect([x], S)

    def test_campaign_url_validation(self):
        self.assertEqual(check_campaign_url("https://finalvestige.com/focus/?utm_source=youtube&utm_campaign=perception_01&asset_id=grok_342")["asset_id"], "grok_342")
        for url in ["http://finalvestige.com/focus/", "https://finalvestige.com.evil.org/focus/", "https://finalvestige.com/focus/?utm_source=a&utm_source=b", "https://finalvestige.com/focus/?asset_id=abc", "https://finalvestige.com/focus/?utm_source=foo%40bar", "https://finalvestige.com/focus/#secret"]:
            with self.subTest(url=url), self.assertRaises(ValueError): check_campaign_url(url)

    def test_raw_strings_in_refs_disallowed(self):
        x = e("cta_click", "alice@example.com", "first_party_server")
        with self.assertRaises(ValueError): inspect([x], S)

    def test_never_approves_campaign(self):
        self.assertFalse(inspect([], S)["is_campaign_release_approved"])
        self.assertFalse(inspect([], S)["is_live_measurement"])


if __name__ == "__main__": unittest.main()
