"""Dispatch R41: privacy, provenance and no-fake-results adversarial tests.

All supplied event values are synthetic. No traffic measurement, subscriber
records, email, WordPress, merchant, analytics or network action is performed.
"""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "r41-measurement-truth" / "measurement_gate.py"
SPEC = importlib.util.spec_from_file_location("r41_measurement_gate", PATH)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def fake(channel="jetpack", metrics=None):
    return {"edition": 1, "channel": channel,
            "observed_utc": "2026-11-01T12:00:00Z",
            "evidence_ref": "synthetic:test_only",
            "metrics": {"reported_sent": 30, "reported_delivered": 28}
                       if metrics is None else metrics,
            "synthetic": True}


class MeasurementTruthTests(unittest.TestCase):
    def test_exact_original_six_still_on_hold(self):
        r = gate.report()
        self.assertEqual(len(r["issues"]), 6)
        self.assertTrue(r["all_six_held"])
        self.assertFalse(r["founder_final_send_approval"])
        self.assertEqual([x["edition"] for x in r["issues"]], list(range(1, 7)))

    def test_founder_four_two_not_replaced(self):
        r = gate.report()
        self.assertEqual(r["founder_mix"], {"editorial": 4, "commercial": 2})
        self.assertEqual([x["kind"] for x in r["issues"]].count("editorial"), 4)
        self.assertEqual([x["edition"] for x in r["issues"]
                          if x["release"] == "HOLD_UNSENT_AND_MERCHANT"], [3, 5])

    def test_no_fabricated_sales_clicks_or_performance(self):
        r = gate.report()
        self.assertEqual(r["observed_edition_metrics"], "NONE_VERIFIED")
        self.assertFalse(r["attribution"]["tracking_deployed"])
        self.assertTrue(all(x["orders"] == "UNKNOWN_NOT_ZERO" for x in r["issues"]))
        self.assertTrue(all(x["rates"] == "NOT_COMPUTED" for x in r["issues"]))

    def test_empty_recent_sends_not_all_time_zero(self):
        s = gate.report()["platform_reality"]
        self.assertEqual(s["recent_send_entries"], 0)
        self.assertEqual(s["lifetime_sends"], "UNKNOWN_NOT_ZERO")
        self.assertEqual(s["unique_consent_eligible"], "UNKNOWN")
        self.assertEqual(s["subscriber_counts"], "NONADDITIVE_2_2_2")

    def test_native_email_click_is_not_website_click(self):
        r = gate.report()
        self.assertTrue(r["attribution"]["email_read_more_distinct_from_onsite_cta"])
        self.assertTrue(r["attribution"]["outbound_click_does_not_prove_sale"])
        self.assertTrue(r["attribution"]["opens_can_be_prefetched"])

    def test_synthetic_structure_pass_never_live_proof(self):
        self.assertEqual(gate.validate_synthetic_aggregate(fake())["result"],
                         "STRUCTURE_ONLY_SYNTHETIC_NOT_PLATFORM_PROOF")

    def test_false_live_label_rejected(self):
        p = fake()
        p["synthetic"] = False
        with self.assertRaises(gate.EvidenceError):
            gate.validate_synthetic_aggregate(p)

    def test_extra_fields_including_personal_identifiers_rejected(self):
        keys = ("email", "recipient", "subscriber_id", "customer_id",
                "ip_address", "click_id", "visitor_id", "session_id",
                "access_token", "person_id", "user_agent")
        for key in keys:
            p = fake()
            p[key] = "secret"
            with self.subTest(key=key), self.assertRaises(gate.EvidenceError):
                gate.validate_synthetic_aggregate(p)

    def test_embedded_email_address_rejected(self):
        p = fake()
        p["evidence_ref"] = "sensitive@example.com"
        with self.assertRaises(gate.EvidenceError):
            gate.validate_synthetic_aggregate(p)

    def test_tokenized_url_rejected(self):
        p = fake()
        p["evidence_ref"] = "https://some.test/?token=SECRET"
        with self.assertRaises(gate.EvidenceError):
            gate.validate_synthetic_aggregate(p)

    def test_wrong_channel_metric_mapping_rejected(self):
        for channel, name in (("jetpack", "confirmed_orders"),
                              ("site_analytics", "reported_sent"),
                              ("merchant", "email_readmore_clicks")):
            with self.subTest(channel=channel):
                with self.assertRaises(gate.EvidenceError):
                    gate.validate_synthetic_aggregate(fake(channel, {name: 1}))

    def test_fabricated_ab_test_metric_rejected(self):
        with self.assertRaises(gate.EvidenceError):
            gate.validate_synthetic_aggregate(fake(metrics={"conversion_lift": 42}))

    def test_negative_fraction_boolean_counts_rejected(self):
        for value in (-1, .3, True):
            with self.subTest(value=value):
                with self.assertRaises(gate.EvidenceError):
                    gate.validate_synthetic_aggregate(fake(metrics={"reported_sent": value}))

    def test_impossible_deliveries_and_clicks_rejected(self):
        for metrics in ({"reported_sent": 4, "reported_delivered": 5},
                        {"reported_delivered": 0, "email_readmore_clicks": 1}):
            with self.subTest(metrics=metrics):
                with self.assertRaises(gate.EvidenceError):
                    gate.validate_synthetic_aggregate(fake(metrics=metrics))

    def test_unknown_channel_and_edition_rejected(self):
        p = fake()
        p["channel"] = "magic_source"
        with self.assertRaises(gate.EvidenceError):
            gate.validate_synthetic_aggregate(p)
        p = fake()
        p["edition"] = 7
        with self.assertRaises(gate.EvidenceError):
            gate.validate_synthetic_aggregate(p)

    def test_opaque_provenance_and_timezone_required(self):
        p = fake()
        p["evidence_ref"] = "github_174"
        with self.assertRaises(gate.EvidenceError):
            gate.validate_synthetic_aggregate(p)
        p = fake()
        p["observed_utc"] = "2026-11-01T12:00:00"
        with self.assertRaises(gate.EvidenceError):
            gate.validate_synthetic_aggregate(p)

    def test_no_percentage_on_two_subscribers(self):
        r = gate.cautious_ratio(1, 2)
        self.assertEqual(r["state"], "SUPPRESSED_SMALL_DENOMINATOR")
        self.assertIsNone(r["rate"])

    def test_no_percentage_on_missing_or_impossible_denominator(self):
        for a, b in ((0, None), (1, 0), (2, 1), (-1, 12)):
            with self.subTest(pair=(a, b)):
                self.assertEqual(gate.cautious_ratio(a, b)["state"], "UNAVAILABLE")

    def test_large_synthetic_ratio_only_illustration(self):
        result = gate.cautious_ratio(30, 100)
        self.assertEqual(result, {"state": "ILLUSTRATIVE_NOT_OBSERVED", "rate": .3})

    def test_canonical_mutations_fail_closed(self):
        base = gate._read(ROOT / "manifest.json")
        for name in ("activate_merchant", "send", "change_mix", "change_editorial_target"):
            changed = copy.deepcopy(base)
            if name == "activate_merchant":
                changed["issues"][2]["merchant_affiliate_url"] = "https://merchant.invalid/offer"
            elif name == "send":
                changed["issues"][0]["publish_state"] = "publish"
            elif name == "change_mix":
                changed["issues"][2]["kind"] = "editorial"
            else:
                changed["issues"][0]["editorial_cta"] = "https://merchant.invalid/"
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "manifest.json"
                p.write_text(json.dumps(changed), encoding="utf-8")
                with self.subTest(name=name), self.assertRaises(gate.EvidenceError):
                    gate.canonical(manifest_path=p)

    def test_observation_mutations_fail_closed(self):
        base = gate._read(gate.EVIDENCE)
        for name in ("fake_lifetime", "fake_consent", "enabled_send", "fake_postal",
                     "changed_count", "new_send"):
            v = copy.deepcopy(base)
            if name == "fake_lifetime":
                v["lifetime_sends"] = 0
            elif name == "fake_consent":
                v["unique_consent_eligible"] = 2
            elif name == "enabled_send":
                v["newsletter"]["auto_new_post_emails"] = True
            elif name == "fake_postal":
                v["release_evidence"]["postal_footer_received"] = True
            elif name == "changed_count":
                v["newsletter"]["diagnostic_counters"]["total"] = 4
            else:
                v["newsletter"]["recent_sends"] = [{"status":"sent"}]
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "snapshot.json"
                p.write_text(json.dumps(v), encoding="utf-8")
                with self.subTest(name=name), self.assertRaises(gate.EvidenceError):
                    gate.canonical(evidence_path=p)

    def test_snapshots_cannot_contain_email_address(self):
        v = gate._read(gate.EVIDENCE)
        v["subscriber_email"] = "redacted@example.com"
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "snapshot.json"
            p.write_text(json.dumps(v), encoding="utf-8")
            with self.assertRaises(gate.EvidenceError):
                gate.canonical(evidence_path=p)


if __name__ == "__main__":
    unittest.main()
