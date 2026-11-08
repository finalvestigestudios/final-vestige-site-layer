"""R121 unsent canon fingerprint guards. Native Python unittest in a repo checkout."""
import json
import pathlib
import subprocess
import unittest

DIR = pathlib.Path(__file__).resolve().parents[1]
REPO = DIR.parents[2]

class TestCanonicalAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=json.loads((DIR/"audit.json").read_text(encoding="utf-8"))
        cls.rows=cls.audit["rows"]
        cls.manifest=json.loads((DIR.parent/"manifest.json").read_text(encoding="utf-8"))

    def test_six_with_four_editorial_two_commercial(self):
        self.assertEqual([r["issue"] for r in self.rows],list(range(1,7)))
        self.assertEqual(sum(r["kind"]=="editorial" for r in self.rows),4)
        self.assertEqual(sum(r["kind"]=="commercial-review-pending" for r in self.rows),2)

    def test_all_changed_not_authorized(self):
        self.assertTrue(all(r["source_changed"] and r["original_blob"] != r["stacked_blob"] for r in self.rows))
        self.assertEqual(self.audit["status"],"ALL_HOLD_UNSENT")
        self.assertFalse(self.audit["affiliate_authorized"])

    def test_revision_matches_manifest(self):
        for r,m in zip(self.rows,self.manifest["issues"]):
            self.assertEqual(m["subject"],r["stacked_subject"])
            self.assertEqual(m["preheader"],r["stacked_preheader"])
            self.assertIsNone(m["merchant_affiliate_url"])

    def test_inherited_source_sha(self):
        for r in self.rows:
            path=REPO/r["path"]
            self.assertTrue(path.exists(),str(path))
            sha=subprocess.check_output(["git","hash-object",str(path)],text=True).strip()
            self.assertEqual(r["stacked_blob"],sha)

    def test_no_invented_conversions(self):
        self.assertIsNone(self.audit["paid_orders"])
        self.assertIsNone(self.audit["realized_net_revenue"])
        self.assertIsNone(self.audit["authenticated_wp_snapshot"]["reachable"])

    def test_source_specific_findings(self):
        self.assertIn("17.1 seconds",self.rows[3]["editorial_finding"])
        self.assertIn("official product-specific citation",self.rows[4]["editorial_finding"])
        self.assertIn("/focus/",self.rows[5]["editorial_finding"])

if __name__=="__main__":unittest.main()
