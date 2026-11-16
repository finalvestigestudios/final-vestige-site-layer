import unittest
from copy import deepcopy
from revenue_proof import reduce_proofs


def example():
    return {"window_days": 7, "as_of": "2026-11-16", "refunds_complete": True, "fees_complete": True,
            "source_sessions": [{"date": "2026-11-15", "asset_id": "grok_asset_001", "utm_campaign": "mind_pilot_2026_11", "qualified_human_sessions": 80, "source": {"kind": "analytics_audited_aggregate", "proof_ref": "audit-001"}}],
            "paid_transactions": [{"date": "2026-11-15", "order_ref": "merchant-001", "asset_id": "grok_asset_001", "utm_campaign": "mind_pilot_2026_11", "currency": "USD", "paid_commission_cents": 2000, "refund_cents": 300, "fee_cents": 200, "source": {"kind": "merchant_paid_settlement", "proof_ref": "settlement-001"}}]}


class RevenueProofTests(unittest.TestCase):
    def test_empty_evidence_is_not_zero(self):
        p = example(); p["source_sessions"] = []; p["paid_transactions"] = []
        r = reduce_proofs(p); self.assertEqual(r["commercial_kpi_status"], "NOT_COMPUTABLE"); self.assertIsNone(r["net_usd"])

    def test_paid_with_independent_sessions(self):
        r = reduce_proofs(example()); self.assertEqual(r["net_usd"], "15"); self.assertEqual(r["net_usd_per_1000_qualified_sessions"], "187.50")

    def test_no_orders_not_zero(self):
        p = example(); p["paid_transactions"] = []; self.assertEqual(reduce_proofs(p)["commercial_kpi_status"], "NOT_COMPUTABLE")

    def test_no_sessions_not_computable(self):
        p = example(); p["source_sessions"] = []; self.assertEqual(reduce_proofs(p)["commercial_kpi_status"], "NOT_COMPUTABLE")

    def test_missing_refunds_not_computable(self):
        p = example(); p["refunds_complete"] = False; self.assertIsNone(reduce_proofs(p)["net_usd"])

    def test_missing_fees_not_computable(self):
        p = example(); p["fees_complete"] = False; self.assertIsNone(reduce_proofs(p)["net_usd"])

    def test_wrong_campaign_not_computable(self):
        p = example(); p["paid_transactions"][0]["utm_campaign"] = "other"; self.assertIsNone(reduce_proofs(p)["net_usd"])

    def test_wrong_asset_not_computable(self):
        p = example(); p["paid_transactions"][0]["asset_id"] = "not-the-source"; self.assertIsNone(reduce_proofs(p)["net_usd"])

    def test_duplicate_orders_rejected(self):
        p = example(); p["paid_transactions"].append(deepcopy(p["paid_transactions"][0])); self.assertRaises(ValueError, reduce_proofs, p)

    def test_duplicate_sessions_rejected(self):
        p = example(); p["source_sessions"].append(deepcopy(p["source_sessions"][0])); self.assertRaises(ValueError, reduce_proofs, p)

    def test_email_address_rejected(self):
        p = example(); p["paid_transactions"][0]["order_ref"] = "person@example.com"; self.assertRaises(ValueError, reduce_proofs, p)

    def test_token_leak_rejected(self):
        p = example(); p["source_sessions"][0]["asset_id"] = "subscriber_id=12"; self.assertRaises(ValueError, reduce_proofs, p)

    def test_pageview_not_authorized(self):
        p = example(); p["source_sessions"][0]["source"]["kind"] = "pageview"; self.assertRaises(ValueError, reduce_proofs, p)

    def test_click_not_sale(self):
        p = example(); p["paid_transactions"][0]["source"]["kind"] = "affiliate_click"; self.assertRaises(ValueError, reduce_proofs, p)

    def test_pending_settlement_not_sale(self):
        p = example(); p["paid_transactions"][0]["source"]["kind"] = "merchant_pending"; self.assertRaises(ValueError, reduce_proofs, p)

    def test_currency_mismatch_rejected(self):
        p = example(); p["paid_transactions"][0]["currency"] = "GBP"; self.assertRaises(ValueError, reduce_proofs, p)

    def test_refund_above_paid_rejected(self):
        p = example(); p["paid_transactions"][0]["refund_cents"] = 5000; self.assertRaises(ValueError, reduce_proofs, p)

    def test_negative_amount_rejected(self):
        p = example(); p["paid_transactions"][0]["fee_cents"] = -20; self.assertRaises(ValueError, reduce_proofs, p)

    def test_floats_rejected(self):
        p = example(); p["paid_transactions"][0]["paid_commission_cents"] = 20.5; self.assertRaises(ValueError, reduce_proofs, p)

    def test_dates_out_of_window_rejected(self):
        p = example(); p["paid_transactions"][0]["date"] = "2026-11-01"; self.assertRaises(ValueError, reduce_proofs, p)

    def test_future_dates_rejected(self):
        p = example(); p["source_sessions"][0]["date"] = "2026-11-17"; self.assertRaises(ValueError, reduce_proofs, p)

    def test_unknown_schema_rejected(self):
        p = example(); p["source_sessions"][0]["email"] = "abc"; self.assertRaises(ValueError, reduce_proofs, p)

    def test_30day_window_supported(self):
        p = example(); p["window_days"] = 30; self.assertEqual(reduce_proofs(p)["commercial_kpi_status"], "EVIDENCE_BOUND")

    def test_campaign_never_released(self):
        self.assertEqual(reduce_proofs(example())["release"], "HOLD_UNSENT")


if __name__ == "__main__": unittest.main()
