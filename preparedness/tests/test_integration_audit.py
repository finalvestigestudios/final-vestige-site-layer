"""Structural checks for the read-only integration audit CLI."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_integration  # noqa: E402


class IntegrationReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit_integration.make_report()

    def test_run_produces_deterministic_json(self):
        once = json.dumps(self.report, sort_keys=True)
        twice = json.dumps(audit_integration.make_report(), sort_keys=True)
        self.assertEqual(once, twice)

    def test_exact_slate_35_articles_one_tool(self):
        slate = self.report["slate"]
        self.assertEqual(slate["actual_articles"], 35)
        self.assertEqual(slate["expected_articles"], 35)
        self.assertEqual(slate["tools"], 6)

    def test_drafts_never_become_published_from_a_report(self):
        self.assertEqual(self.report["publication"], "HOLD")
        self.assertEqual(self.report["slate"]["drafts_including_tools"], 41)
        self.assertFalse(self.report["wordpress_published_by_this_tool"])

    def test_source_depth_and_review_status_visible(self):
        src = self.report["sources"]
        self.assertEqual(src["raw_rows"], 244)
        self.assertEqual(src["verified_by_machine"], 229)
        self.assertEqual(src["human_link_checked_rows"], 0)
        self.assertEqual(src["shared_url_groups"], 32)
        self.assertEqual(src["pending_groups"], 32)

    def test_never_reports_human_qa_proven(self):
        self.assertFalse(self.report["external_human_qa_proven"])
        self.assertFalse(self.report["release_ready_by_static_checks"])

    def test_urls_from_pending_shared_sources_remain_auditable(self):
        d = {a["slug"]: a for a in self.report["articles"]}
        self.assertGreater(d["pioneer-travel-rations"]["pending_shared_source_count"], 0)
        self.assertGreater(d["pioneer-supply-chains-failed"]["pending_shared_source_count"], 0)
        self.assertNotEqual(
            next(s["origin"] for s in d["pioneer-travel-rations"]["sources"]
                 if s["id"] == "loc-pioneer-diaries"),
            next(s["origin"] for s in d["pioneer-supply-chains-failed"]["sources"]
                 if s["id"] == "loc-pioneer-diaries"),
        )


if __name__ == "__main__":
    unittest.main()
