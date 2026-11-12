"""R327 Preparedness source-to-paid-offer evidence contract, synthetic negative controls."""
import copy
import unittest
from preparedness.tools import r327_conversion_source_gate_hold as gate
from preparedness.tools import r323_full_slate_identity_crosswalk_hold as crosswalk

def fixture():
    c = gate.blank()
    rows = []
    slugs = [("family-communication-plan", "articles", 15, "start-here")]
    slugs += [(f"article-{i}", "articles", i + 50, "start-here") for i in range(34)]
    slugs += [("reunification-plan", "tools", 102, "field-tools"),
              ("family-reunification-card", "tools", 104, "field-tools")]
    slugs += [(f"tool-{i}", "tools", 200 + i, "field-tools") for i in range(4)]
    for slug, kind, num, section in slugs:
        rows.append({"slug": slug, "type": kind, "number": num, "publication": "draft",
                     "canonical": f"https://finalvestige.com/preparedness/{section}/{slug}/",
                     "body_git_blob": "a" * 40, "metadata_git_blob": "b" * 40})
    c["free"]["guide_url"] = rows[0]["canonical"]
    audit = {"schema": crosswalk.SCHEMA, "state": "DRAFT_HARD_HOLD", "errors": [],
             "entries": rows, "release": crosswalk.RELEASE.copy(), "source_conflicts_held": 15}
    return c, audit

class R327TruthGate(unittest.TestCase):
    def test_review_only_contract(self):
        c, a = fixture()
        r = gate.inspect(c, a)
        self.assertEqual(r["state"], "DRAFT_HARD_HOLD", r)
        self.assertEqual(r["entries_checked"], 41)
        self.assertEqual(r["conflicts_held"], 15)
        self.assertIsNone(r["net_revenue_per_1000_qualified_sessions"])
        self.assertFalse(any(r["release"].values()))

    def test_matching_youtube_asset_still_not_verified(self):
        c, a = fixture()
        c["social"].update(platform="youtube_shorts", asset_id="iUlaEBT8dSU",
                           published_url="https://www.youtube.com/shorts/iUlaEBT8dSU",
                           utm_campaign="prep-reunification-iUlaEBT8dSU")
        r = gate.inspect(c, a)
        self.assertEqual(r["state"], "DRAFT_HARD_HOLD")
        self.assertEqual(r["asset"], "EXTERNAL_VERIFICATION_REQUIRED")

    def test_missing_full_repository_fails_closed(self):
        c, a = fixture()
        for altered in (None, {}, {"entries": []}, {"state": "PASS", "entries": a["entries"]}):
            with self.subTest(altered=altered):
                self.assertEqual(gate.inspect(c, altered)["state"], "INVALID_HARD_HOLD")

    def test_no_http_or_retired_freebie(self):
        for url in ("http://finalvestige.com/preparedness/",
                    "https://finalvestige.com/preparedness/water-guide/",
                    "https://finalvestige.com:443/preparedness/",
                    "https://evil.test/preparedness/",
                    "https://finalvestige.com/preparedness/?buy=1",
                    "https://finalvestige.com/preparedness/#purchase",
                    "https://finalvestige.com/preparedness/%2e%2e/",
                    "https://finalvestige.com/preparedness//tool/",
                    "//finalvestige.com/preparedness/"):
            with self.subTest(url=url):
                self.assertFalse(gate.first_party(url))

def add_negative_case(name, group, field, bad):
    def check(self):
        c, a = fixture()
        c[group][field] = bad
        r = gate.inspect(c, a)
        self.assertEqual(r["state"], "INVALID_HARD_HOLD", (name, r))
        self.assertFalse(any(r["release"].values()))
        self.assertIsNone(r["net_revenue_per_1000_qualified_sessions"])
    setattr(R327TruthGate, "test_negative_" + name, check)

cases = []
for field in gate.HOLD:
    cases.extend([(f"release_{field}_true", "release", field, True),
                  (f"release_{field}_zero", "release", field, 0)])
for field in ("rights_approved", "merchant_approved", "delivery_approved",
              "refunds_approved", "founder_approved"):
    cases.append((f"paid_{field}", "paid", field, True))
cases.extend([("paid_sku", "paid", "sku", "prep-bundle-001"),
              ("paid_checkout", "paid", "checkout_url", "https://payhip.com/b/test"),
              ("tool_wrong_slug", "tool", "slug", "reunification-plan"),
              ("tool_wrong_number", "tool", "number", 102),
              ("tool_bool_number", "tool", "number", True),
              ("tool_public_link", "tool", "cta_url", "https://finalvestige.com/preparedness/"),
              ("tool_privacy", "tool", "privacy_approved", True),
              ("tool_emergency", "tool", "emergency_advice_approved", True),
              ("tool_print", "tool", "print_approved", True),
              ("free_retired", "free", "url", "https://finalvestige.com/preparedness/water-guide/"),
              ("free_wrong_guide", "free", "guide_slug", "reunification-plan"),
              ("free_unverified_source_claim", "free", "source_safety_approved", True),
              ("free_missing_guide_url", "free", "guide_url", None),
              ("social_unverified_claim", "social", "externally_verified", True),
              ("social_short_id", "social", "asset_id", "bad"),
              ("social_unmatched_url", "social", "published_url", "https://www.youtube.com/shorts/UNKNOWN"),
              ("social_unmatched_utm", "social", "utm_campaign", "another_campaign"),
              ("social_false_platform", "social", "platform", "tiktok"),
              ("metrics_wrong_cohorts", "metrics", "cohorts", [30]),
              ("metrics_wrong_steps", "metrics", "steps", ["views", "sales"])])
for f in ("qualified_sessions", "paid_orders", "gross", "fees", "refunds", "realized_net"):
    cases += [(f"metric_{f}_nonzero", "metrics", f, 1),
              (f"metric_{f}_zero", "metrics", f, 0)]
for name, group, field, bad in cases:
    add_negative_case(name, group, field, bad)

class R327CrosswalkTampering(unittest.TestCase):
    def test_41_entries_required(self):
        c, a = fixture()
        a["entries"].pop()
        self.assertEqual(gate.inspect(c, a)["state"], "INVALID_HARD_HOLD")

    def test_tool_identity_cannot_be_swapped(self):
        c, a = fixture()
        next(x for x in a["entries"] if x["slug"] == "family-reunification-card")["number"] = 102
        self.assertIn("TOOL_102_104_IDENTITY_COLLISION", gate.inspect(c, a)["errors"])

    def test_released_article_cannot_be_accepted(self):
        c, a = fixture()
        a["entries"][0]["publication"] = "publish"
        self.assertIn("SOURCE_IDENTITY_OR_ROUTE_DRIFT", gate.inspect(c, a)["errors"])

    def test_duplicated_canonical_refused(self):
        c, a = fixture()
        a["entries"][2]["canonical"] = a["entries"][1]["canonical"]
        self.assertIn("SOURCE_IDENTITY_OR_ROUTE_DRIFT", gate.inspect(c, a)["errors"])

    def test_wrong_source_blob_refused(self):
        c, a = fixture()
        a["entries"][5]["body_git_blob"] = "bogus"
        self.assertIn("SOURCE_IDENTITY_OR_ROUTE_DRIFT", gate.inspect(c, a)["errors"])

    def test_forged_crosswalk_approval_refused(self):
        c, a = fixture()
        a["release"]["independent_qd_pass"] = 0
        self.assertIn("NATIVE_CROSSWALK_REQUIRED", gate.inspect(c, a)["errors"])

if __name__ == "__main__":
    unittest.main()
