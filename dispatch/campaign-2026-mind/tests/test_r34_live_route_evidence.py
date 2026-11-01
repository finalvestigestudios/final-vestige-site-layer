"""Independent R34 mutation tests: source proof and newsletter remain HOLD."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "r34-live-cta-evidence" / "audit_live_route_evidence.py"
spec = importlib.util.spec_from_file_location("fv_dispatch_r34", FILE)
audit_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_mod)

class LiveRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        cls.e = json.loads((FILE.parent / "LIVE_ROUTE_EVIDENCE.json").read_text(encoding="utf-8"))

    def reject(self, fn, in_manifest=False):
        m, e = copy.deepcopy(self.m), copy.deepcopy(self.e)
        fn(m if in_manifest else e)
        with self.assertRaises(audit_mod.EvidenceError):
            audit_mod.audit(m, e)

    def test_baseline_four_editorial_routes_and_two_holds(self):
        out = audit_mod.audit(self.m, self.e)
        self.assertEqual(out["editorial_ctas_published_on_snapshot"], 4)
        self.assertEqual(out["commercial_ctas_blocked"], 2)
        self.assertEqual(out["release"], "HOLD_UNSENT")
        self.assertFalse(out["real_jetpack_email_received"])

    def test_no_double_counted_audience(self):
        self.assertEqual(audit_mod.audit(self.m, self.e)["eligible_audience_verified"], False)

    def test_manifest_six_issue_mix(self):
        self.reject(lambda m: m["issues"][2].update(kind="editorial"), True)

    def test_manifest_active_affiliate(self):
        self.reject(lambda m: m["issues"][2].update(merchant_affiliate_url="https://example.invalid/buy"), True)

    def test_manifest_commercial_destination(self):
        self.reject(lambda m: m["issues"][2].update(editorial_cta="https://finalvestige.com/mind/zen12-guide/"), True)

    def test_manifest_prepublication_guard(self):
        self.reject(lambda m: m["issues"][0].update(publish_state="publish"), True)

    def test_missing_editorial_record(self):
        self.reject(lambda e: e["routes"].pop(0))

    def test_duplicate_record(self):
        self.reject(lambda e: e["routes"][1].update(number=1))

    def test_wrong_editorial_target(self):
        self.reject(lambda e: e["routes"][0].update(url="https://finalvestige.com/other/"))

    def test_lookalike_domain_rejected(self):
        self.reject(lambda e: e["routes"][0].update(url="https://evilfinalvestige.com/the-missing-caption/"))

    def test_no_id_rejected(self):
        self.reject(lambda e: e["routes"][0].update(wp_id=None))

    def test_claim_draft_is_published_rejected(self):
        self.reject(lambda e: e["routes"][0].update(status="draft"))

    def test_forged_published_commercial_guide_rejected(self):
        self.reject(lambda e: e["routes"][2].update(
            status="publish", wp_id=100, wp_type="page",
            url="https://finalvestige.com/mind/zen12-guide/"))

    def test_commercial_email_permission_not_verified(self):
        self.reject(lambda e: e["routes"][2].update(partner_email_permission_verified=True))

    def test_commercial_guide_not_live(self):
        self.assertIsNone(self.e["routes"][4]["url"])

    def test_counters_cannot_be_added(self):
        self.reject(lambda e: e["subscriber_counts_nonadditive"].update(total=4))

    def test_false_eligible_count_rejected(self):
        self.reject(lambda e: e.update(eligible_unique_recipients=2))

    def test_false_welcome_receipt_rejected(self):
        self.reject(lambda e: e["newsletter"].update(welcome_received_verified=True))

    def test_auto_email_must_remain_off(self):
        self.reject(lambda e: e["newsletter"].update(new_post_automatic_email=True))

    def test_all_holds_must_remain(self):
        self.reject(lambda e: e.update(release="READY"))

    def test_snapshot_not_live_claim(self):
        self.reject(lambda e: e.update(snapshot_not_live_requery=False))

    def test_timestamp_manipulation(self):
        self.reject(lambda e: e.update(as_of_utc="2027-01-01T00:00:00Z"))

    def test_email_data_privacy(self):
        self.reject(lambda e: e.update(recipient_email="example@example.invalid"))

    def test_unsubscribe_token_privacy(self):
        self.reject(lambda e: e.update(unsubscribe_token="secret"))

    def test_other_private_token_privacy(self):
        self.reject(lambda e: e.update(affiliate_earning_url="https://example.invalid/secret"))

if __name__ == "__main__":
    unittest.main()
